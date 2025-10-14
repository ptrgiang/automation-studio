"""
Automation Studio Layout Manager
Implements the three-panel layout: Workflow | Canvas | Properties
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
from src.theme import ModernTheme


class ResizablePane(ttk.Frame):
    """A pane with a draggable resize handle"""

    def __init__(self, parent, side: str = 'left', min_width: int = 200,
                 max_width: Optional[int] = None, **kwargs):
        """
        Initialize resizable pane

        Args:
            parent: Parent widget
            side: Which side the pane is on ('left' or 'right')
            min_width: Minimum width in pixels
            max_width: Maximum width in pixels (None for no limit)
        """
        super().__init__(parent, **kwargs)
        self.side = side
        self.min_width = min_width
        self.max_width = max_width
        self.current_width = min_width

        self.is_resizing = False
        self.resize_start_x = 0
        self.resize_start_width = 0

        # Configure pane
        self.configure(width=self.current_width)
        self.pack_propagate(False)

    def add_resize_handle(self):
        """Add a resize handle to the pane"""
        if self.side == 'left':
            # Handle on the right edge
            handle = tk.Frame(self, width=4, cursor='sb_h_double_arrow',
                            bg=ModernTheme.BORDER)
            handle.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            # Handle on the left edge
            handle = tk.Frame(self, width=4, cursor='sb_h_double_arrow',
                            bg=ModernTheme.BORDER)
            handle.pack(side=tk.LEFT, fill=tk.Y)

        # Bind resize events
        handle.bind('<Button-1>', self._start_resize)
        handle.bind('<B1-Motion>', self._do_resize)
        handle.bind('<ButtonRelease-1>', self._stop_resize)

        return handle

    def _start_resize(self, event):
        """Start resize operation"""
        self.is_resizing = True
        self.resize_start_x = event.x_root
        self.resize_start_width = self.current_width

    def _do_resize(self, event):
        """Handle resize drag"""
        if not self.is_resizing:
            return

        delta = event.x_root - self.resize_start_x

        if self.side == 'left':
            new_width = self.resize_start_width + delta
        else:
            new_width = self.resize_start_width - delta

        # Apply constraints
        new_width = max(self.min_width, new_width)
        if self.max_width:
            new_width = min(self.max_width, new_width)

        self.current_width = new_width
        self.configure(width=self.current_width)

    def _stop_resize(self, event):
        """Stop resize operation"""
        self.is_resizing = False


class WorkflowPanel(ResizablePane):
    """Left panel showing workflow/action sequence"""

    def __init__(self, parent, callbacks: Optional[Dict[str, Callable]] = None):
        """
        Initialize workflow panel

        Args:
            parent: Parent widget
            callbacks: Dictionary of callback functions
        """
        super().__init__(parent, side='left', min_width=280, max_width=500)
        self.callbacks = callbacks or {}

        self.configure(style='Panel.TFrame')

        # Create header
        self._create_header()

        # Create action list container
        self._create_action_container()

        # Create footer
        self._create_footer()

        # Add resize handle
        self.add_resize_handle()

    def _create_header(self):
        """Create panel header"""
        header = ttk.Frame(self, style='Header.TFrame', height=50)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        header.pack_propagate(False)

        # Title
        title_label = ttk.Label(header, text="Workflow",
                               style='Title.TLabel',
                               font=(ModernTheme.FONT_FAMILY, 14, 'bold'))
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        # Action counter
        self.counter_label = ttk.Label(header, text="0 steps",
                                      style='Secondary.TLabel',
                                      font=(ModernTheme.FONT_FAMILY, 10))
        self.counter_label.pack(side=tk.RIGHT, anchor=tk.E)

    def _create_action_container(self):
        """Create scrollable container for action cards"""
        container = ttk.Frame(self, style='Panel.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for scrolling
        self.canvas = tk.Canvas(container, bg=ModernTheme.BACKGROUND,
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.canvas.yview)

        # Frame inside canvas for action cards
        self.actions_frame = ttk.Frame(self.canvas, style='Panel.TFrame')
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.actions_frame, anchor=tk.NW
        )

        # Bind resize event
        self.actions_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Bind mouse wheel for scrolling to canvas
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', self._on_mousewheel)  # Linux scroll up
        self.canvas.bind('<Button-5>', self._on_mousewheel)  # Linux scroll down

        # Also bind to actions_frame so scrolling works over action cards
        self.actions_frame.bind('<MouseWheel>', self._on_mousewheel)
        self.actions_frame.bind('<Button-4>', self._on_mousewheel)
        self.actions_frame.bind('<Button-5>', self._on_mousewheel)

    def _on_frame_configure(self, event=None):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        """Update frame width when canvas resizes"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Windows and MacOS
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

    def _create_footer(self):
        """Create panel footer with add button"""
        footer = ttk.Frame(self, style='Panel.TFrame', height=60)
        footer.pack(fill=tk.X, padx=10, pady=(0, 10))
        footer.pack_propagate(False)

        # Add step button
        add_btn = ttk.Button(footer, text="+ Add Step",
                            style='Primary.TButton',
                            command=self._on_add_step)
        add_btn.pack(fill=tk.X, pady=10)

    def _on_add_step(self):
        """Handle add step button click"""
        if 'add_step' in self.callbacks:
            self.callbacks['add_step']()

    def update_counter(self, count: int):
        """Update action counter"""
        self.counter_label.config(text=f"{count} step{'s' if count != 1 else ''}")

    def clear_actions(self):
        """Clear all action cards"""
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        self.update_counter(0)

    def bind_mousewheel_to_widget(self, widget):
        """Recursively bind mouse wheel to widget and all its children"""
        widget.bind('<MouseWheel>', self._on_mousewheel)
        widget.bind('<Button-4>', self._on_mousewheel)
        widget.bind('<Button-5>', self._on_mousewheel)

        # Bind to all children recursively
        for child in widget.winfo_children():
            self.bind_mousewheel_to_widget(child)


class CanvasPanel(ttk.Frame):
    """Center panel showing visual canvas with screenshots"""

    def __init__(self, parent):
        """Initialize canvas panel"""
        super().__init__(parent, style='Canvas.TFrame')

        # Create header
        self._create_header()

        # Create canvas area
        self._create_canvas()

        # Create toolbar
        self._create_toolbar()

    def _create_header(self):
        """Create panel header"""
        header = ttk.Frame(self, style='Header.TFrame', height=50)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        header.pack_propagate(False)

        # Title
        title_label = ttk.Label(header, text="Visual Canvas",
                               style='Title.TLabel',
                               font=(ModernTheme.FONT_FAMILY, 14, 'bold'))
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        # Info label
        self.info_label = ttk.Label(header, text="No screenshot",
                                   style='Secondary.TLabel',
                                   font=(ModernTheme.FONT_FAMILY, 10))
        self.info_label.pack(side=tk.RIGHT, anchor=tk.E)

    def _create_canvas(self):
        """Create canvas area"""
        canvas_container = ttk.Frame(self, style='Canvas.TFrame')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas with scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(canvas_container,
                               bg=ModernTheme.SURFACE,
                               highlightthickness=1,
                               highlightbackground=ModernTheme.BORDER,
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        h_scrollbar.configure(command=self.canvas.xview)
        v_scrollbar.configure(command=self.canvas.yview)

        # Placeholder text
        self.placeholder_text = self.canvas.create_text(
            0, 0, text="📸 No screenshot loaded\n\nSelect an action or capture a new screenshot",
            font=(ModernTheme.FONT_FAMILY, 12),
            fill=ModernTheme.TEXT_LIGHT,
            justify=tk.CENTER
        )

        # Center placeholder
        self.canvas.bind('<Configure>', self._center_placeholder)

    def _center_placeholder(self, event=None):
        """Center the placeholder text"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.placeholder_text, width // 2, height // 2)

    def _create_toolbar(self):
        """Create canvas toolbar"""
        toolbar = ttk.Frame(self, style='Toolbar.TFrame', height=40)
        toolbar.pack(fill=tk.X, padx=10, pady=(0, 10))
        toolbar.pack_propagate(False)

        # Zoom controls
        ttk.Label(toolbar, text="Zoom:",
                 style='Secondary.TLabel').pack(side=tk.LEFT, padx=(0, 5))

        zoom_out_btn = ttk.Button(toolbar, text="-", width=3,
                                  style='Outline.TButton')
        zoom_out_btn.pack(side=tk.LEFT, padx=2)

        self.zoom_label = ttk.Label(toolbar, text="100%",
                                    style='Secondary.TLabel', width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)

        zoom_in_btn = ttk.Button(toolbar, text="+", width=3,
                                style='Outline.TButton')
        zoom_in_btn.pack(side=tk.LEFT, padx=2)

        zoom_fit_btn = ttk.Button(toolbar, text="Fit",
                                  style='Outline.TButton')
        zoom_fit_btn.pack(side=tk.LEFT, padx=(10, 2))

        # Capture button
        capture_btn = ttk.Button(toolbar, text="📸 Capture Screen",
                                style='Primary.TButton')
        capture_btn.pack(side=tk.RIGHT, padx=2)


class PropertiesPanel(ResizablePane):
    """Right panel showing properties of selected action"""

    def __init__(self, parent):
        """Initialize properties panel"""
        super().__init__(parent, side='right', min_width=280, max_width=400)
        self.configure(style='Panel.TFrame')

        # Create header
        self._create_header()

        # Create scrollable content area
        self._create_content_area()

        # Add resize handle
        self.add_resize_handle()

        # Show placeholder
        self._show_placeholder()

    def _create_header(self):
        """Create panel header"""
        header = ttk.Frame(self, style='Header.TFrame', height=50)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        header.pack_propagate(False)

        # Title
        self.title_label = ttk.Label(header, text="Properties",
                                     style='Title.TLabel',
                                     font=(ModernTheme.FONT_FAMILY, 14, 'bold'))
        self.title_label.pack(side=tk.LEFT, anchor=tk.W)

    def _create_content_area(self):
        """Create scrollable content area"""
        container = ttk.Frame(self, style='Panel.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for scrolling
        self.canvas = tk.Canvas(container, bg=ModernTheme.BACKGROUND,
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.canvas.yview)

        # Frame inside canvas for properties
        self.content_frame = ttk.Frame(self.canvas, style='Panel.TFrame')
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.content_frame, anchor=tk.NW
        )

        # Bind resize event
        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_frame_configure(self, event=None):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        """Update frame width when canvas resizes"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _show_placeholder(self):
        """Show placeholder when no action is selected"""
        self.clear_content()

        placeholder = ttk.Label(self.content_frame,
                               text="⚙️\n\nNo action selected\n\nSelect an action from the workflow\nto view its properties",
                               style='Secondary.TLabel',
                               font=(ModernTheme.FONT_FAMILY, 11),
                               justify=tk.CENTER)
        placeholder.pack(expand=True, pady=50)

    def clear_content(self):
        """Clear all content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_action_properties(self, action, on_change=None):
        """Show properties for an action"""
        from src.property_editor import ActionPropertyPanel

        self.clear_content()

        # Update title
        self.title_label.config(text=f"Properties: {action.type.upper()}")

        # Action info header
        info_frame = ttk.Frame(self.content_frame, style='Panel.TFrame')
        info_frame.pack(fill=tk.X, pady=(10, 15))

        # Action type badge
        badge_frame = ttk.Frame(info_frame, style='Panel.TFrame')
        badge_frame.pack(anchor=tk.W)

        badge = tk.Label(badge_frame,
                        text=action.ui.icon + " " + action.type.upper(),
                        font=(ModernTheme.FONT_FAMILY, 11, 'bold'),
                        bg=action.ui.color,
                        fg='white',
                        padx=10, pady=5)
        badge.pack()

        # Create property panel
        ActionPropertyPanel(self.content_frame, action, on_change=on_change)


class StudioLayout(ttk.Frame):
    """Main studio layout with three panels"""

    def __init__(self, parent, callbacks: Optional[Dict[str, Callable]] = None):
        """
        Initialize studio layout

        Args:
            parent: Parent widget
            callbacks: Dictionary of callback functions
        """
        super().__init__(parent)
        self.callbacks = callbacks or {}

        # Configure main frame
        self.pack(fill=tk.BOTH, expand=True)

        # Create the three panels
        self.workflow_panel = WorkflowPanel(self, callbacks=callbacks)
        self.workflow_panel.pack(side=tk.LEFT, fill=tk.BOTH)

        self.canvas_panel = CanvasPanel(self)
        self.canvas_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.properties_panel = PropertiesPanel(self)
        self.properties_panel.pack(side=tk.RIGHT, fill=tk.BOTH)


# Test/demo code
if __name__ == "__main__":
    # Create test window
    root = tk.Tk()
    root.title("Automation Studio Layout Test")
    root.geometry("1400x800")

    # Apply theme
    from src.theme import ModernTheme
    ModernTheme.configure_style()
    root.configure(bg=ModernTheme.BACKGROUND)

    # Define callbacks
    def on_add_step():
        print("Add step clicked")

    callbacks = {
        'add_step': on_add_step
    }

    # Create studio layout
    studio = StudioLayout(root, callbacks=callbacks)

    # Update counter for testing
    studio.workflow_panel.update_counter(5)
    studio.canvas_panel.info_label.config(text="1920 × 1080")

    root.mainloop()
