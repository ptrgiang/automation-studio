"""
Visual Canvas for displaying screenshots with action annotations
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict, Any, Tuple
from PIL import Image, ImageTk, ImageDraw
import logging
from src.theme import ModernTheme


class ActionAnnotation:
    """Visual annotation for an action on the canvas"""

    def __init__(self, action_index: int, action_type: str,
                 x: int, y: int, width: Optional[int] = None,
                 height: Optional[int] = None, color: str = ModernTheme.PRIMARY):
        self.action_index = action_index
        self.action_type = action_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.items = []

    def is_point(self) -> bool:
        return self.width is None or self.height is None


class VisualCanvas(ttk.Frame):
    """Canvas for displaying screenshots with action annotations"""

    def __init__(self, canvas_widget: tk.Canvas, on_annotation_click=None, on_annotation_double_click=None, on_zoom_change=None):
        super().__init__(canvas_widget)
        self.canvas = canvas_widget
        self.screenshot = None
        self.screenshot_photo = None
        self.screenshot_item = None
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.annotations: List[ActionAnnotation] = []
        self.selected_annotation = None
        self.on_annotation_click = on_annotation_click
        self.on_annotation_double_click = on_annotation_double_click
        self.on_zoom_change = on_zoom_change
        self._bind_events()

    def _bind_events(self):
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Button-4>', self._on_mouse_wheel)
        self.canvas.bind('<Button-5>', self._on_mouse_wheel)
        self.canvas.bind('<Button-2>', self._on_pan_start)
        self.canvas.bind('<B2-Motion>', self._on_pan_drag)
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Double-Button-1>', self._on_double_click)

    def load_screenshot(self, screenshot: Image.Image, clear_annotations: bool = True):
        if not screenshot:
            self.screenshot = None
            if self.screenshot_item:
                self.canvas.delete(self.screenshot_item)
            self.clear_annotations()
            self.zoom_level = 1.0
            self.pan_x = 0
            self.pan_y = 0
            logging.info("Screenshot cleared")
            self._update_display() # Clear canvas
            return

        self.screenshot = screenshot
        if self.screenshot_item:
            self.canvas.delete(self.screenshot_item)
        if clear_annotations:
            self.clear_annotations()
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._update_display()
        logging.info(f"Loaded screenshot: {screenshot.size}")

    def _update_display(self):
        if not self.screenshot:
            self.canvas.delete("all")
            return

        zoomed_width = int(self.screenshot.width * self.zoom_level)
        zoomed_height = int(self.screenshot.height * self.zoom_level)

        display_image = self.screenshot.resize((zoomed_width, zoomed_height), Image.Resampling.LANCZOS) if self.zoom_level != 1.0 else self.screenshot
        self.screenshot_photo = ImageTk.PhotoImage(display_image)

        if self.screenshot_item:
            self.canvas.delete(self.screenshot_item)

        self.screenshot_item = self.canvas.create_image(self.pan_x, self.pan_y, image=self.screenshot_photo, anchor=tk.NW, tags='screenshot')
        self.canvas.configure(scrollregion=(self.pan_x, self.pan_y, self.pan_x + zoomed_width, self.pan_y + zoomed_height))
        self._redraw_annotations()

        if self.on_zoom_change:
            self.on_zoom_change(self.get_zoom_percentage())

    def add_annotation(self, annotation: ActionAnnotation):
        self.annotations.append(annotation)
        self._draw_annotation(annotation)

    def remove_annotation(self, action_index: int):
        annotation_to_remove = None
        for ann in self.annotations:
            if ann.action_index == action_index:
                annotation_to_remove = ann
                for item_id in ann.items:
                    self.canvas.delete(item_id)
                break
        if annotation_to_remove:
            self.annotations.remove(annotation_to_remove)
            for ann in self.annotations:
                if ann.action_index > action_index:
                    ann.action_index -= 1
            self._redraw_annotations()

    def clear_annotations(self):
        for annotation in self.annotations:
            for item_id in annotation.items:
                self.canvas.delete(item_id)
        self.annotations.clear()
        self.selected_annotation = None

    def select_annotation(self, action_index: int):
        self.selected_annotation = action_index
        self._redraw_annotations()

    def _draw_annotation(self, annotation: ActionAnnotation):
        for item_id in annotation.items:
            self.canvas.delete(item_id)
        annotation.items.clear()

        x = int(annotation.x * self.zoom_level) + self.pan_x
        y = int(annotation.y * self.zoom_level) + self.pan_y

        is_selected = (self.selected_annotation == annotation.action_index)
        line_width = 2 if is_selected else 1
        color = ModernTheme.RING if is_selected else annotation.color

        if annotation.is_point():
            size = int(12 * self.zoom_level)
            h_line = self.canvas.create_line(x - size, y, x + size, y, fill=color, width=line_width, tags='annotation')
            v_line = self.canvas.create_line(x, y - size, x, y + size, fill=color, width=line_width, tags='annotation')
            annotation.items.extend([h_line, v_line])
        else:
            width = int(annotation.width * self.zoom_level)
            height = int(annotation.height * self.zoom_level)
            rect = self.canvas.create_rectangle(x, y, x + width, y + height, outline=color, width=line_width, tags='annotation')
            annotation.items.append(rect)

        label_bg = self.canvas.create_rectangle(x, y - 20, x + 30, y, fill=color, outline='', tags='annotation')
        label_text = self.canvas.create_text(x + 15, y - 10, text=f"#{annotation.action_index + 1}", font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold'), fill=ModernTheme.POPOVER_FOREGROUND, tags='annotation')
        annotation.items.extend([label_bg, label_text])
        self.canvas.tag_raise('annotation')

    def _redraw_annotations(self):
        for annotation in self.annotations:
            self._draw_annotation(annotation)

    def zoom_in(self):
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self._update_display()

    def zoom_out(self):
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self._update_display()

    def zoom_fit(self):
        if not self.screenshot:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        zoom_x = canvas_width / self.screenshot.width
        zoom_y = canvas_height / self.screenshot.height
        self.zoom_level = min(zoom_x, zoom_y) * 0.95
        self.pan_x = 0
        self.pan_y = 0
        self._update_display()

    def get_zoom_percentage(self) -> int:
        return int(self.zoom_level * 100)

    def _on_mouse_wheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_level = max(0.1, min(self.zoom_level * factor, 5.0))
        self._update_display()

    def _on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_annotation = None
        for annotation in self.annotations:
            ann_x = int(annotation.x * self.zoom_level) + self.pan_x
            ann_y = int(annotation.y * self.zoom_level) + self.pan_y
            if annotation.is_point():
                if abs(x - ann_x) < 20 and abs(y - ann_y) < 20:
                    clicked_annotation = annotation
                    break
            else:
                ann_width = int(annotation.width * self.zoom_level)
                ann_height = int(annotation.height * self.zoom_level)
                if ann_x <= x <= ann_x + ann_width and ann_y <= y <= ann_y + ann_height:
                    clicked_annotation = annotation
                    break
        if clicked_annotation and self.on_annotation_click:
            self.on_annotation_click(clicked_annotation.action_index)

    def _on_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for annotation in self.annotations:
            ann_x = int(annotation.x * self.zoom_level) + self.pan_x
            ann_y = int(annotation.y * self.zoom_level) + self.pan_y
            if annotation.is_point():
                if abs(x - ann_x) < 20 and abs(y - ann_y) < 20:
                    if self.on_annotation_double_click:
                        self.on_annotation_double_click(annotation.action_index)
                    return
            else:
                ann_width = int(annotation.width * self.zoom_level)
                ann_height = int(annotation.height * self.zoom_level)
                if ann_x <= x <= ann_x + ann_width and ann_y <= y <= ann_y + ann_height:
                    if self.on_annotation_double_click:
                        self.on_annotation_double_click(annotation.action_index)
                    return

    def has_screenshot(self) -> bool:
        return self.screenshot is not None


# Test code
if __name__ == "__main__":
    from src.theme import ModernTheme
    import pyautogui

    root = tk.Tk()
    root.title("Visual Canvas Test")
    root.geometry("900x700")

    ModernTheme.configure_style()
    root.configure(bg=ModernTheme.BACKGROUND)

    # Create canvas
    canvas_widget = tk.Canvas(root, bg=ModernTheme.CARD)
    canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create visual canvas
    visual_canvas = VisualCanvas(canvas_widget)

    # Capture and load screenshot
    screenshot = pyautogui.screenshot()
    visual_canvas.load_screenshot(screenshot)

    # Add some test annotations
    visual_canvas.add_annotation(ActionAnnotation(
        0, 'click', 100, 100, color='#4A90E2'
    ))
    visual_canvas.add_annotation(ActionAnnotation(
        1, 'set_value', 300, 200, 150, 30, color='#50C878'
    ))
    visual_canvas.add_annotation(ActionAnnotation(
        2, 'find_image', 500, 400, 80, 60, color='#9B59B6'
    ))

    # Zoom controls
    controls = ttk.Frame(root)
    controls.pack(fill=tk.X, padx=10, pady=5)

    ttk.Button(controls, text="Zoom In", command=visual_canvas.zoom_in).pack(side=tk.LEFT, padx=2)
    ttk.Button(controls, text="Zoom Out", command=visual_canvas.zoom_out).pack(side=tk.LEFT, padx=2)
    ttk.Button(controls, text="Fit", command=visual_canvas.zoom_fit).pack(side=tk.LEFT, padx=2)
    ttk.Button(controls, text="Reset", command=visual_canvas.zoom_reset).pack(side=tk.LEFT, padx=2)

    root.mainloop()
