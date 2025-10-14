"""
Visual Canvas for displaying screenshots with action annotations
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict, Any, Tuple
from PIL import Image, ImageTk, ImageDraw
import logging


class ActionAnnotation:
    """Visual annotation for an action on the canvas"""

    def __init__(self, action_index: int, action_type: str,
                 x: int, y: int, width: Optional[int] = None,
                 height: Optional[int] = None, color: str = '#00FF00'):
        """
        Initialize action annotation

        Args:
            action_index: Index of the action
            action_type: Type of action
            x, y: Position
            width, height: Size (for regions)
            color: Annotation color
        """
        self.action_index = action_index
        self.action_type = action_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        # Canvas item IDs
        self.items = []

    def is_point(self) -> bool:
        """Check if annotation is a point (vs region)"""
        return self.width is None or self.height is None


class VisualCanvas:
    """Canvas for displaying screenshots with action annotations"""

    def __init__(self, canvas_widget: tk.Canvas, on_annotation_click=None, on_annotation_double_click=None, on_zoom_change=None):
        """
        Initialize visual canvas

        Args:
            canvas_widget: The tk.Canvas widget to use
            on_annotation_click: Callback when annotation is clicked (index)
            on_annotation_double_click: Callback when annotation is double-clicked (index)
            on_zoom_change: Callback when zoom level changes (percentage)
        """
        self.canvas = canvas_widget
        self.screenshot = None  # PIL Image
        self.screenshot_photo = None  # PhotoImage for display
        self.screenshot_item = None  # Canvas image item ID

        # Zoom and pan state
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

        # Annotations
        self.annotations: List[ActionAnnotation] = []
        self.selected_annotation = None

        # Callbacks
        self.on_annotation_click = on_annotation_click
        self.on_annotation_double_click = on_annotation_double_click
        self.on_zoom_change = on_zoom_change

        # Bind events
        self._bind_events()

    def _bind_events(self):
        """Bind canvas events"""
        # Mouse wheel for zoom
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Button-4>', self._on_mouse_wheel)  # Linux scroll up
        self.canvas.bind('<Button-5>', self._on_mouse_wheel)  # Linux scroll down

        # Middle button drag for pan
        self.canvas.bind('<Button-2>', self._on_pan_start)
        self.canvas.bind('<B2-Motion>', self._on_pan_drag)

        # Click to select annotation
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Double-Button-1>', self._on_double_click)

    def load_screenshot(self, screenshot: Image.Image, clear_annotations: bool = True):
        """
        Load a screenshot onto the canvas

        Args:
            screenshot: PIL Image
            clear_annotations: Whether to clear existing annotations
        """
        self.screenshot = screenshot

        # Clear existing content
        if self.screenshot_item:
            self.canvas.delete(self.screenshot_item)

        if clear_annotations:
            self.clear_annotations()

        # Reset zoom and pan
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

        # Create PhotoImage and display
        self._update_display()

        logging.info(f"Loaded screenshot: {screenshot.size}")

    def _update_display(self):
        """Update canvas display with current zoom/pan"""
        if not self.screenshot:
            return

        # Apply zoom
        zoomed_width = int(self.screenshot.width * self.zoom_level)
        zoomed_height = int(self.screenshot.height * self.zoom_level)

        if self.zoom_level != 1.0:
            display_image = self.screenshot.resize(
                (zoomed_width, zoomed_height),
                Image.Resampling.LANCZOS
            )
        else:
            display_image = self.screenshot

        # Convert to PhotoImage
        self.screenshot_photo = ImageTk.PhotoImage(display_image)

        # Display on canvas
        if self.screenshot_item:
            self.canvas.delete(self.screenshot_item)

        self.screenshot_item = self.canvas.create_image(
            self.pan_x, self.pan_y,
            image=self.screenshot_photo,
            anchor=tk.NW,
            tags='screenshot'
        )

        # Update scroll region
        self.canvas.configure(scrollregion=(
            self.pan_x, self.pan_y,
            self.pan_x + zoomed_width,
            self.pan_y + zoomed_height
        ))

        # Redraw annotations
        self._redraw_annotations()

        # Notify zoom change
        if self.on_zoom_change:
            self.on_zoom_change(self.get_zoom_percentage())

    def add_annotation(self, annotation: ActionAnnotation):
        """Add an action annotation to the canvas"""
        self.annotations.append(annotation)
        self._draw_annotation(annotation)

    def remove_annotation(self, action_index: int):
        """Remove annotation for specific action"""
        self.annotations = [a for a in self.annotations
                           if a.action_index != action_index]
        self._redraw_annotations()

    def clear_annotations(self):
        """Clear all annotations"""
        for annotation in self.annotations:
            for item_id in annotation.items:
                self.canvas.delete(item_id)

        self.annotations.clear()
        self.selected_annotation = None

    def select_annotation(self, action_index: int):
        """Highlight annotation for selected action"""
        self.selected_annotation = action_index
        self._redraw_annotations()

    def _draw_annotation(self, annotation: ActionAnnotation):
        """Draw a single annotation"""
        # Clear existing items for this annotation
        for item_id in annotation.items:
            self.canvas.delete(item_id)
        annotation.items.clear()

        # Calculate zoomed and panned coordinates
        x = int(annotation.x * self.zoom_level) + self.pan_x
        y = int(annotation.y * self.zoom_level) + self.pan_y

        # Determine if this annotation is selected
        is_selected = (self.selected_annotation == annotation.action_index)
        line_width = 3 if is_selected else 2
        color = '#FFFF00' if is_selected else annotation.color  # Yellow when selected

        if annotation.is_point():
            # Draw crosshair and circle for point
            size = int(15 * self.zoom_level)

            # Crosshair
            h_line = self.canvas.create_line(
                x - size, y, x + size, y,
                fill=color, width=line_width, tags='annotation'
            )
            v_line = self.canvas.create_line(
                x, y - size, x, y + size,
                fill=color, width=line_width, tags='annotation'
            )

            # Circle
            circle_size = int(8 * self.zoom_level)
            circle = self.canvas.create_oval(
                x - circle_size, y - circle_size,
                x + circle_size, y + circle_size,
                outline=color, width=line_width, tags='annotation'
            )

            annotation.items = [h_line, v_line, circle]

        else:
            # Draw rectangle for region
            width = int(annotation.width * self.zoom_level)
            height = int(annotation.height * self.zoom_level)

            rect = self.canvas.create_rectangle(
                x, y, x + width, y + height,
                outline=color, width=line_width, tags='annotation'
            )

            annotation.items = [rect]

        # Add label with action number
        label_bg = self.canvas.create_rectangle(
            x - 2, y - 20, x + 30, y - 2,
            fill=color, outline='', tags='annotation'
        )
        label_text = self.canvas.create_text(
            x + 14, y - 11,
            text=f"#{annotation.action_index + 1}",
            font=('Arial', 10, 'bold'),
            fill='black', tags='annotation'
        )

        annotation.items.extend([label_bg, label_text])

        # Bring annotations to front
        self.canvas.tag_raise('annotation')

    def _redraw_annotations(self):
        """Redraw all annotations"""
        for annotation in self.annotations:
            self._draw_annotation(annotation)

    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self._update_display()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self._update_display()

    def zoom_fit(self):
        """Zoom to fit canvas"""
        if not self.screenshot:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate zoom to fit
        zoom_x = canvas_width / self.screenshot.width
        zoom_y = canvas_height / self.screenshot.height

        self.zoom_level = min(zoom_x, zoom_y) * 0.95  # 95% to add padding
        self.pan_x = 0
        self.pan_y = 0

        self._update_display()

    def zoom_reset(self):
        """Reset zoom to 100%"""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._update_display()

    def get_zoom_percentage(self) -> int:
        """Get current zoom as percentage"""
        return int(self.zoom_level * 100)

    def _on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        # Get mouse position
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Determine zoom direction
        if event.num == 5 or event.delta < 0:
            # Zoom out
            factor = 0.9
        else:
            # Zoom in
            factor = 1.1

        # Apply zoom
        old_zoom = self.zoom_level
        self.zoom_level = max(0.1, min(self.zoom_level * factor, 5.0))

        # Adjust pan to zoom around mouse position
        zoom_change = self.zoom_level / old_zoom
        self.pan_x = x - (x - self.pan_x) * zoom_change
        self.pan_y = y - (y - self.pan_y) * zoom_change

        self._update_display()

    def _on_pan_start(self, event):
        """Start panning"""
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_drag(self, event):
        """Pan canvas"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_click(self, event):
        """Handle click on canvas"""
        # Check if clicked on an annotation
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        clicked_annotation = None

        for annotation in self.annotations:
            # Calculate annotation bounds with zoom
            ann_x = int(annotation.x * self.zoom_level) + self.pan_x
            ann_y = int(annotation.y * self.zoom_level) + self.pan_y

            if annotation.is_point():
                # Check if clicked near point
                distance = ((x - ann_x) ** 2 + (y - ann_y) ** 2) ** 0.5
                if distance < 20:
                    clicked_annotation = annotation
                    break
            else:
                # Check if clicked inside region
                ann_width = int(annotation.width * self.zoom_level)
                ann_height = int(annotation.height * self.zoom_level)

                if (ann_x <= x <= ann_x + ann_width and
                    ann_y <= y <= ann_y + ann_height):
                    clicked_annotation = annotation
                    break

        if clicked_annotation:
            self.select_annotation(clicked_annotation.action_index)
            # Trigger callback
            if self.on_annotation_click:
                self.on_annotation_click(clicked_annotation.action_index)

    def _on_double_click(self, event):
        """Handle double-click on canvas"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Find clicked annotation
        for annotation in self.annotations:
            ann_x = int(annotation.x * self.zoom_level) + self.pan_x
            ann_y = int(annotation.y * self.zoom_level) + self.pan_y

            if annotation.is_point():
                distance = ((x - ann_x) ** 2 + (y - ann_y) ** 2) ** 0.5
                if distance < 20:
                    if self.on_annotation_double_click:
                        self.on_annotation_double_click(annotation.action_index)
                    return
            else:
                ann_width = int(annotation.width * self.zoom_level)
                ann_height = int(annotation.height * self.zoom_level)

                if (ann_x <= x <= ann_x + ann_width and
                    ann_y <= y <= ann_y + ann_height):
                    if self.on_annotation_double_click:
                        self.on_annotation_double_click(annotation.action_index)
                    return

    def has_screenshot(self) -> bool:
        """Check if canvas has a screenshot loaded"""
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
    canvas_widget = tk.Canvas(root, bg=ModernTheme.SURFACE)
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
