"""
Automation Studio Layout Manager
Implements the three-panel layout: Workflow | Canvas | Properties
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
from src.theme import ModernTheme, Icons


class ResizablePane(ttk.Frame):
    """A pane with a draggable resize handle"""

    def __init__(self, parent, side: str = 'left', min_width: int = 200,
                 max_width: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.side = side
        self.min_width = min_width
        self.max_width = max_width
        self.current_width = min_width

        self.is_resizing = False
        self.resize_start_x = 0
        self.resize_start_width = 0

        self.configure(width=self.current_width)
        self.pack_propagate(False)

    def add_resize_handle(self):
        handle = tk.Frame(self, width=4, cursor='sb_h_double_arrow',
                            bg=ModernTheme.BORDER)
        if self.side == 'left':
            handle.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            handle.pack(side=tk.LEFT, fill=tk.Y)

        handle.bind('<Button-1>', self._start_resize)
        handle.bind('<B1-Motion>', self._do_resize)
        handle.bind('<ButtonRelease-1>', self._stop_resize)

        return handle

    def _start_resize(self, event):
        self.is_resizing = True
        self.resize_start_x = event.x_root
        self.resize_start_width = self.current_width

    def _do_resize(self, event):
        if not self.is_resizing:
            return

        delta = event.x_root - self.resize_start_x

        if self.side == 'left':
            new_width = self.resize_start_width + delta
        else:
            new_width = self.resize_start_width - delta

        new_width = max(self.min_width, new_width)
        if self.max_width:
            new_width = min(self.max_width, new_width)

        self.current_width = new_width
        self.configure(width=self.current_width)

    def _stop_resize(self, event):
        self.is_resizing = False


class WorkflowPanel(ResizablePane):
    def __init__(self, parent, callbacks: Optional[Dict[str, Callable]] = None):
        super().__init__(parent, side='left', min_width=300, max_width=600)
        self.callbacks = callbacks or {}

        self.configure(style='TFrame')

        self._create_header()
        self._create_action_container()
        self._create_footer()
        self.add_resize_handle()

    def _create_header(self):
        header = ttk.Frame(self, style='TFrame', height=60)
        header.pack(fill=tk.X, padx=ModernTheme.PADDING_LG, pady=(ModernTheme.PADDING_LG, 0))
        header.pack_propagate(False)

        title_label = ttk.Label(header, text="Workflow", font=(ModernTheme.FONT_FAMILY, 16, 'bold'))
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        self.counter_label = ttk.Label(header, text="0 steps", style='Secondary.TLabel')
        self.counter_label.pack(side=tk.RIGHT, anchor=tk.E)

    def _create_action_container(self):
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_MD)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(container)
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas = tk.Canvas(container, bg=ModernTheme.BACKGROUND, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)

        self.actions_frame = ttk.Frame(self.canvas, style='TFrame')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.actions_frame, anchor=tk.NW)

        self.actions_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.actions_frame.bind('<MouseWheel>', self._on_mousewheel)

    def _check_scrollbar(self):
        """Show/hide scrollbar based on content height"""
        if self.actions_frame.winfo_height() > self.canvas.winfo_height():
            self.scrollbar.grid()
            self.scrollbar_visible = True
        else:
            self.scrollbar.grid_remove()
            self.scrollbar_visible = False

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self._check_scrollbar()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._check_scrollbar()

    def _on_mousewheel(self, event):
        """Only scroll if scrollbar is visible"""
        if hasattr(self, 'scrollbar_visible') and self.scrollbar_visible:
            delta = -1 * (event.delta // 120)
            self.canvas.yview_scroll(delta, 'units')

    def _create_footer(self):
        footer = ttk.Frame(self, style='TFrame', height=60)
        footer.pack(fill=tk.X, padx=ModernTheme.PADDING_LG, pady=(0, ModernTheme.PADDING_LG))
        footer.pack_propagate(False)

        add_btn = ttk.Button(footer, text="+ Add Step", style='Primary.TButton', command=self._on_add_step)
        add_btn.pack(fill=tk.BOTH, expand=True)

    def _on_add_step(self):
        if 'add_step' in self.callbacks:
            self.callbacks['add_step']()

    def update_counter(self, count: int):
        self.counter_label.config(text=f"{count} step{'s' if count != 1 else ''}")

    def clear_actions(self):
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        self.update_counter(0)

    def bind_mousewheel_to_widget(self, widget):
        widget.bind('<MouseWheel>', self._on_mousewheel)
        for child in widget.winfo_children():
            self.bind_mousewheel_to_widget(child)


class CanvasPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='TFrame')

        self._create_header()
        self._create_canvas()
        self._create_toolbar()

    def _create_header(self):
        header = ttk.Frame(self, style='TFrame', height=60)
        header.pack(fill=tk.X, padx=ModernTheme.PADDING_LG, pady=(ModernTheme.PADDING_LG, 0))
        header.pack_propagate(False)

        title_label = ttk.Label(header, text="Visual Canvas", font=(ModernTheme.FONT_FAMILY, 16, 'bold'))
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        self.info_label = ttk.Label(header, text="No screenshot", style='Secondary.TLabel')
        self.info_label.pack(side=tk.RIGHT, anchor=tk.E)

    def _create_canvas(self):
        canvas_container = ttk.Frame(self, style='TFrame')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_MD)
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        self.h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas = tk.Canvas(canvas_container, bg=ModernTheme.MUTED, highlightthickness=0,
                               xscrollcommand=self._on_xscroll, yscrollcommand=self._on_yscroll)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.h_scrollbar.configure(command=self.canvas.xview)
        self.v_scrollbar.configure(command=self.canvas.yview)

        self.h_scrollbar_visible = False
        self.v_scrollbar_visible = False
        self._check_scrollbars()

        self.placeholder_text = self.canvas.create_text(0, 0, text="📸 No screenshot loaded",
                                                       font=(ModernTheme.FONT_FAMILY, 14),
                                                       fill=ModernTheme.MUTED_FOREGROUND)
        self.canvas.bind('<Configure>', self._center_placeholder)

    def _on_xscroll(self, first, last):
        """Handle horizontal scrollbar updates and show/hide"""
        self.h_scrollbar.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.h_scrollbar.grid_remove()
            self.h_scrollbar_visible = False
        else:
            self.h_scrollbar.grid()
            self.h_scrollbar_visible = True

    def _on_yscroll(self, first, last):
        """Handle vertical scrollbar updates and show/hide"""
        self.v_scrollbar.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.v_scrollbar.grid_remove()
            self.v_scrollbar_visible = False
        else:
            self.v_scrollbar.grid()
            self.v_scrollbar_visible = True

    def _check_scrollbars(self):
        """Initial check for scrollbars visibility"""
        self.h_scrollbar.grid_remove()
        self.v_scrollbar.grid_remove()
        self.h_scrollbar_visible = False
        self.v_scrollbar_visible = False

    def _center_placeholder(self, event=None):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.placeholder_text, width // 2, height // 2)

    def _create_toolbar(self):
        toolbar = ttk.Frame(self, style='TFrame', height=50)
        toolbar.pack(fill=tk.X, padx=ModernTheme.PADDING_LG, pady=(0, ModernTheme.PADDING_LG))
        toolbar.pack_propagate(False)

        zoom_out_btn = ttk.Button(toolbar, text="-", width=3, style='Outline.TButton')
        zoom_out_btn.pack(side=tk.LEFT, padx=2)

        self.zoom_label = ttk.Label(toolbar, text="100%", style='Secondary.TLabel', width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=ModernTheme.PADDING_MD)

        zoom_in_btn = ttk.Button(toolbar, text="+", width=3, style='Outline.TButton')
        zoom_in_btn.pack(side=tk.LEFT, padx=2)

        zoom_fit_btn = ttk.Button(toolbar, text="Fit", style='Outline.TButton')
        zoom_fit_btn.pack(side=tk.LEFT, padx=(ModernTheme.PADDING_MD, 0))


class PropertiesPanel(ResizablePane):
    def __init__(self, parent):
        super().__init__(parent, side='right', min_width=300, max_width=500)
        self.configure(style='TFrame')

        self._create_header()
        self._create_content_area()
        self.add_resize_handle()
        self._show_placeholder()

    def _create_header(self):
        header = ttk.Frame(self, style='TFrame', height=60)
        header.pack(fill=tk.X, padx=ModernTheme.PADDING_LG, pady=(ModernTheme.PADDING_LG, 0))
        header.pack_propagate(False)

        self.title_label = ttk.Label(header, text="Properties", font=(ModernTheme.FONT_FAMILY, 16, 'bold'))
        self.title_label.pack(side=tk.LEFT, anchor=tk.W)

    def _create_content_area(self):
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_MD)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(container)
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas = tk.Canvas(container, bg=ModernTheme.BACKGROUND, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)

        self.content_frame = ttk.Frame(self.canvas, style='TFrame')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW)

        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.content_frame.bind('<MouseWheel>', self._on_mousewheel)

    def _check_scrollbar(self):
        """Show/hide scrollbar based on content height"""
        if self.content_frame.winfo_height() > self.canvas.winfo_height():
            self.scrollbar.grid()
            self.scrollbar_visible = True
        else:
            self.scrollbar.grid_remove()
            self.scrollbar_visible = False

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self._check_scrollbar()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._check_scrollbar()

    def _on_mousewheel(self, event):
        """Only scroll if scrollbar is visible"""
        if hasattr(self, 'scrollbar_visible') and self.scrollbar_visible:
            delta = -1 * (event.delta // 120)
            self.canvas.yview_scroll(delta, 'units')

    def _show_placeholder(self):
        self.clear_content()
        placeholder = ttk.Label(self.content_frame, text="Select an action to see its properties",
                               style='Secondary.TLabel', justify=tk.CENTER)
        placeholder.pack(expand=True, pady=100)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_action_properties(self, action, on_change=None, batch_columns=None, on_recapture=None):
        from src.property_editor import ActionPropertyPanel
        self.clear_content()
        self.title_label.config(text=f"Properties: {action.type.upper()}")
        ActionPropertyPanel(self.content_frame, action, on_change=on_change,
                          batch_columns=batch_columns, on_recapture=on_recapture)


class StudioLayout(ttk.Frame):
    def __init__(self, parent, callbacks: Optional[Dict[str, Callable]] = None):
        super().__init__(parent)
        self.callbacks = callbacks or {}

        self.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_LG)

        self.workflow_panel = WorkflowPanel(self, callbacks=callbacks)
        self.workflow_panel.pack(side=tk.LEFT, fill=tk.BOTH)

        self.properties_panel = PropertiesPanel(self)
        self.properties_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.canvas_panel = CanvasPanel(self)
        self.canvas_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_MD)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Automation Studio Layout Test")
    root.geometry("1400x800")

    ModernTheme.configure_style()
    root.configure(bg=ModernTheme.BACKGROUND)

    def on_add_step():
        print("Add step clicked")

    callbacks = {
        'add_step': on_add_step
    }

    studio = StudioLayout(root, callbacks=callbacks)
    studio.workflow_panel.update_counter(5)
    studio.canvas_panel.info_label.config(text="1920 × 1080")

    root.mainloop()
