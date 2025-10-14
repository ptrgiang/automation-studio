"""
Transparent execution popup for live playback feedback
"""
import tkinter as tk
from tkinter import ttk
from src.theme import ModernTheme, Icons


class ExecutionPopup:
    """Transparent popup window showing execution progress"""

    def __init__(self, parent):
        self.parent = parent
        self.popup = None
        self.current_step_label = None
        self.progress_label = None
        self.history_frame = None
        self.history_labels = []
        self.max_history = 5

    def show(self):
        """Show the execution popup"""
        if self.popup:
            return

        # Create top-level window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Execution Progress")

        # Make it stay on top
        self.popup.attributes('-topmost', True)

        # Make it semi-transparent (0.0 to 1.0)
        self.popup.attributes('-alpha', 0.95)

        # Remove window decorations for cleaner look
        self.popup.overrideredirect(True)

        # Set size and position (middle-right of screen)
        width = 400
        height = 300
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = screen_width - width - 50  # 50px from right edge
        y = (screen_height - height) // 2  # Centered vertically

        self.popup.geometry(f"{width}x{height}+{x}+{y}")

        # Main container with rounded corners effect
        main_frame = tk.Frame(self.popup, bg=ModernTheme.SURFACE,
                             highlightbackground=ModernTheme.PRIMARY,
                             highlightthickness=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Header
        header = tk.Frame(main_frame, bg=ModernTheme.PRIMARY, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_label = tk.Label(header, text="⚡ Execution in Progress",
                              font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                              bg=ModernTheme.PRIMARY,
                              fg='white')
        title_label.pack(side=tk.LEFT, padx=15, pady=8)

        # Close button
        close_btn = tk.Label(header, text="✕", font=(ModernTheme.FONT_FAMILY, 14),
                            bg=ModernTheme.PRIMARY, fg='white',
                            cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind('<Button-1>', lambda e: self.hide())

        # Content area
        content = tk.Frame(main_frame, bg=ModernTheme.SURFACE)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Progress indicator
        self.progress_label = tk.Label(content,
                                      text="Step 0 / 0",
                                      font=(ModernTheme.FONT_FAMILY, 10),
                                      bg=ModernTheme.SURFACE,
                                      fg=ModernTheme.TEXT_SECONDARY)
        self.progress_label.pack(anchor=tk.W, pady=(0, 10))

        # Current step (large, prominent)
        self.current_step_label = tk.Label(content,
                                          text="Starting...",
                                          font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                                          bg=ModernTheme.SURFACE,
                                          fg=ModernTheme.PRIMARY,
                                          wraplength=350,
                                          justify=tk.LEFT)
        self.current_step_label.pack(anchor=tk.W, pady=10)

        # Separator
        sep = tk.Frame(content, height=1, bg=ModernTheme.BORDER)
        sep.pack(fill=tk.X, pady=10)

        # Recent history label
        history_header = tk.Label(content,
                                 text="Recent Steps:",
                                 font=(ModernTheme.FONT_FAMILY, 9, 'bold'),
                                 bg=ModernTheme.SURFACE,
                                 fg=ModernTheme.TEXT_SECONDARY)
        history_header.pack(anchor=tk.W, pady=(0, 5))

        # History frame for recent steps
        self.history_frame = tk.Frame(content, bg=ModernTheme.SURFACE)
        self.history_frame.pack(fill=tk.BOTH, expand=True)

        # Controls at bottom
        controls = tk.Frame(main_frame, bg=ModernTheme.SURFACE)
        controls.pack(fill=tk.X, padx=15, pady=(0, 15))

        controls_text = "Press P to Pause/Resume  •  Press S to Stop"
        controls_label = tk.Label(controls,
                                 text=controls_text,
                                 font=(ModernTheme.FONT_FAMILY, 9),
                                 bg=ModernTheme.SURFACE,
                                 fg=ModernTheme.TEXT_LIGHT)
        controls_label.pack()

        # Make window draggable
        self._make_draggable(header)

    def hide(self):
        """Hide the execution popup"""
        if self.popup:
            self.popup.destroy()
            self.popup = None
            self.history_labels = []

    def update_step(self, current: int, total: int, action_type: str, details: str = ""):
        """Update the current step being executed"""
        if not self.popup:
            return

        # Update progress
        self.progress_label.config(text=f"Step {current} / {total}")

        # Update current step with animation effect
        step_text = f"{action_type.upper()}: {details}" if details else action_type.upper()
        self.current_step_label.config(text=step_text)

        # Add to history (with fade effect simulation)
        self._add_to_history(f"✓ Step {current}: {action_type}")

        # Flash animation
        self.popup.update()

    def _add_to_history(self, text: str):
        """Add a step to the history list"""
        # Create new history label
        label = tk.Label(self.history_frame,
                        text=text,
                        font=(ModernTheme.FONT_FAMILY, 9),
                        bg=ModernTheme.SURFACE,
                        fg=ModernTheme.TEXT_LIGHT,
                        anchor=tk.W)
        label.pack(fill=tk.X, pady=2)

        # Add to list
        self.history_labels.append(label)

        # Keep only last N items
        if len(self.history_labels) > self.max_history:
            old_label = self.history_labels.pop(0)
            old_label.destroy()

    def set_status(self, status: str):
        """Set a status message"""
        if not self.popup:
            return
        self.current_step_label.config(text=status)

    def _make_draggable(self, widget):
        """Make the popup window draggable"""
        widget._drag_data = {"x": 0, "y": 0}

        def on_press(event):
            widget._drag_data["x"] = event.x
            widget._drag_data["y"] = event.y

        def on_drag(event):
            deltax = event.x - widget._drag_data["x"]
            deltay = event.y - widget._drag_data["y"]
            x = self.popup.winfo_x() + deltax
            y = self.popup.winfo_y() + deltay
            self.popup.geometry(f"+{x}+{y}")

        widget.bind("<Button-1>", on_press)
        widget.bind("<B1-Motion>", on_drag)
