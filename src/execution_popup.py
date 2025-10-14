"""
Transparent, click-through popup window to display execution status.
"""
import tkinter as tk
from tkinter import ttk
from src.theme import ModernTheme

class ExecutionPopup(tk.Toplevel):
    """A small, transparent, always-on-top window for execution status."""

    def __init__(self, parent):
        super().__init__(parent)

        self.overrideredirect(True)  # Frameless window
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.8) # Slightly less transparent

        # A specific color that will be made transparent
        self.transparent_color = '#abcdef'
        self.attributes("-transparentcolor", self.transparent_color)

        self.geometry("+%d+%d" % (self.winfo_screenwidth() - 350, self.winfo_screenheight() - 180))

        self.configure(bg=self.transparent_color)

        self._create_widgets()

    def _create_widgets(self):
        """Create the labels for the popup."""
        # Use a Frame with a background color that is NOT the transparent color
        container = tk.Frame(self, bg='black', bd=1, relief='solid')
        container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.current_step_label = ttk.Label(container, text="Current: ", background='black', foreground='white', font=(ModernTheme.FONT_FAMILY, 11, 'bold'))
        self.current_step_label.pack(anchor=tk.W, padx=15, pady=(10, 5))

        self.next_step_label = ttk.Label(container, text="Next: ", background='black', foreground='#dddddd', font=(ModernTheme.FONT_FAMILY, 9))
        self.next_step_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

        note_label = ttk.Label(container, text="Press P to pause/resume, S to stop", background='black', foreground='#aaaaaa', font=(ModernTheme.FONT_FAMILY, 8, 'italic'))
        note_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

    def update_progress(self, current_step: str, next_step: str):
        """Update the text on the labels."""
        self.current_step_label.config(text=f"Current: {current_step}")
        self.next_step_label.config(text=f"Next: {next_step}")

    def show(self):
        """Show the popup."""
        self.deiconify()

    def hide(self):
        """Hide the popup."""
        self.withdraw()
