"""
Action Card Widgets for Workflow Panel
Beautiful, draggable cards representing automation actions
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict
from PIL import Image, ImageTk
from src.theme import ModernTheme
from src.action_schema import EnhancedAction, UIMetadata


class ToolTip:
    """Simple tooltip for widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffdd", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 9))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ActionCard(ttk.Frame):
    """Visual card representing an action in the workflow"""

    def __init__(self, parent, action: EnhancedAction, index: int,
                 on_select: Optional[Callable] = None,
                 on_toggle: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 on_duplicate: Optional[Callable] = None,
                 on_reorder: Optional[Callable] = None,
                 comment: Optional[str] = None):
        """
        Initialize action card

        Args:
            parent: Parent widget
            action: EnhancedAction object
            index: Action index
            on_select: Callback when card is selected
            on_toggle: Callback to toggle enabled state
            on_delete: Callback to delete action
            on_duplicate: Callback to duplicate action
            on_reorder: Callback for drag-and-drop reorder(from_index, to_index)
            comment: Optional comment text to display
        """
        super().__init__(parent, style='Card.TFrame')
        self.action = action
        self.index = index
        self.on_select = on_select
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self.on_duplicate = on_duplicate
        self.on_reorder = on_reorder
        self.comment = comment

        self.is_selected = False
        self.is_hovered = False

        # Drag-and-drop state
        self.is_dragging = False
        self.drag_start_y = 0
        self.original_y = 0

        # Configure card
        self.configure(height=80)
        self.pack_propagate(False)

        # Create card UI
        self._create_card()

        # Bind events
        self._bind_events()

    def _create_card(self):
        """Create card UI elements"""
        # Main container
        main = tk.Frame(self, bg=self.action.ui.color, height=80)
        main.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        main.pack_propagate(False)

        # Left side - Info only (no icons)
        left_frame = tk.Frame(main, bg=self.action.ui.color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Number label
        self.number_label = tk.Label(left_frame,
                                     text=f"#{self.index + 1}",
                                     font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                                     bg=self.action.ui.color,
                                     fg='white',
                                     width=3)
        self.number_label.pack(side=tk.LEFT, padx=(0, 10))

        # Info
        info_frame = tk.Frame(left_frame, bg=self.action.ui.color)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Action type badge
        self.type_label = tk.Label(info_frame,
                                   text=self.action.type.upper(),
                                   font=(ModernTheme.FONT_FAMILY, 9, 'bold'),
                                   bg='white',
                                   fg=self.action.ui.color,
                                   padx=6, pady=2)
        self.type_label.pack(anchor=tk.W)

        # Description
        summary = self.action.get_summary()
        self.desc_label = tk.Label(info_frame,
                                   text=summary,
                                   font=(ModernTheme.FONT_FAMILY, 10),
                                   bg=self.action.ui.color,
                                   fg='white',
                                   anchor=tk.W,
                                   justify=tk.LEFT,
                                   wraplength=180)
        self.desc_label.pack(anchor=tk.W, pady=(4, 0))

        # Comment indicator (if comment exists)
        if self.comment:
            comment_frame = tk.Frame(info_frame, bg='#ffeb3b', height=20)
            comment_frame.pack(anchor=tk.W, pady=(4, 0), fill=tk.X)

            icon = tk.Label(comment_frame, text="💬",
                          font=('Arial', 10),
                          bg='#ffeb3b', fg='#000000')
            icon.pack(side=tk.LEFT, padx=(2, 2))

            preview = self.comment[:25] + "..." if len(self.comment) > 25 else self.comment
            comment_label = tk.Label(comment_frame, text=preview,
                                   font=(ModernTheme.FONT_FAMILY, 8),
                                   bg='#ffeb3b', fg='#000000',
                                   anchor=tk.W)
            comment_label.pack(side=tk.LEFT, padx=(0, 2))

            # Add tooltip for full comment
            ToolTip(comment_frame, self.comment)

        # Right side - Thumbnail and controls
        right_frame = tk.Frame(main, bg=self.action.ui.color, width=70)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        right_frame.pack_propagate(False)

        # Thumbnail (if available)
        if self.action.has_visual_data() and self.action.visual.thumbnail_path:
            self._load_thumbnail(right_frame)
        else:
            # Placeholder
            placeholder = tk.Label(right_frame,
                                  text="No\nPreview",
                                  font=(ModernTheme.FONT_FAMILY, 8),
                                  bg='#404040',
                                  fg='white',
                                  justify=tk.CENTER)
            placeholder.pack(fill=tk.BOTH, expand=True)

        # Enabled/disabled indicator
        status_color = '#00FF00' if self.action.enabled else '#FF0000'
        self.status_indicator = tk.Frame(main, bg=status_color, width=4)
        self.status_indicator.pack(side=tk.LEFT, fill=tk.Y)

        # Hover menu (initially hidden)
        self.hover_menu = None

        # Add tooltip with action details
        tooltip_text = f"{self.action.type.upper()}\n{summary}"
        if self.action.params:
            param_str = ", ".join([f"{k}={v}" for k, v in list(self.action.params.items())[:3]])
            if len(param_str) > 60:
                param_str = param_str[:60] + "..."
            tooltip_text += f"\n{param_str}"
        ToolTip(self, tooltip_text)

    def _load_thumbnail(self, parent):
        """Load and display thumbnail"""
        try:
            img = Image.open(self.action.visual.thumbnail_path)
            img.thumbnail((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            thumb_label = tk.Label(parent, image=photo, bg='black')
            thumb_label.image = photo  # Keep reference
            thumb_label.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            # Fallback to placeholder
            placeholder = tk.Label(parent, text="📷", font=('Arial', 20),
                                  bg='#404040', fg='white')
            placeholder.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self):
        """Bind mouse events"""
        # Bind to all child widgets for consistent behavior
        def bind_recursive(widget):
            widget.bind('<Button-1>', self._on_click)
            # DISABLED: Drag-and-drop causes issues with scrollable frames
            # widget.bind('<ButtonPress-1>', self._on_drag_start)
            # widget.bind('<B1-Motion>', self._on_drag_motion)
            # widget.bind('<ButtonRelease-1>', self._on_drag_release)
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
            widget.bind('<Button-3>', self._on_right_click)

            for child in widget.winfo_children():
                bind_recursive(child)

        bind_recursive(self)

    def _on_drag_start(self, event):
        """Start drag operation"""
        self.drag_start_y = event.y_root
        self.original_y = self.winfo_y()

    def _on_drag_motion(self, event):
        """Handle drag motion"""
        # Only start dragging if moved more than 5 pixels
        if not self.is_dragging and abs(event.y_root - self.drag_start_y) > 5:
            self.is_dragging = True
            self.configure(cursor='fleur')
            # Add visual feedback - slightly transparent
            self.configure(style='Dragging.Card.TFrame')

        if self.is_dragging:
            # Calculate new position
            delta_y = event.y_root - self.drag_start_y
            new_y = self.original_y + delta_y

            # Move the card
            self.place(y=new_y)

            # Determine target index based on position
            parent_height = self.master.winfo_height()
            card_height = 90  # Card height + padding
            target_index = max(0, min(int(new_y / card_height),
                                     len(self.master.winfo_children()) - 1))

            # Visual indicator could be added here

    def _on_drag_release(self, event):
        """Complete drag operation"""
        if self.is_dragging:
            # Calculate target position
            delta_y = event.y_root - self.drag_start_y
            card_height = 90  # Card height + padding

            # Determine how many positions moved
            positions_moved = round(delta_y / card_height)
            target_index = max(0, min(self.index + positions_moved,
                                     len(self.master.winfo_children()) - 1))

            # Call reorder callback if index changed
            if target_index != self.index and self.on_reorder:
                self.on_reorder(self.index, target_index)

            # Reset drag state
            self.is_dragging = False
            self.configure(cursor='')
            self.configure(style='Card.TFrame')

        # Reset position (parent will repack)
        self.place_forget()

    def _on_click(self, event):
        """Handle left click"""
        # Only trigger click if not dragging
        if not self.is_dragging and self.on_select:
            self.on_select(self.index)

    def _on_right_click(self, event):
        """Handle right click - show context menu"""
        menu = tk.Menu(self, tearoff=0)

        menu.add_command(label="✏️  Edit", command=lambda: self._edit())
        menu.add_command(label="📋  Duplicate", command=lambda: self._duplicate())
        menu.add_separator()

        toggle_text = "❌  Disable" if self.action.enabled else "✓  Enable"
        menu.add_command(label=toggle_text, command=lambda: self._toggle())

        menu.add_separator()
        menu.add_command(label="🗑️  Delete", command=lambda: self._delete())

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_enter(self, event):
        """Handle mouse enter"""
        self.is_hovered = True
        self.configure(relief=tk.RAISED)

    def _on_leave(self, event):
        """Handle mouse leave"""
        self.is_hovered = False
        if not self.is_selected:
            self.configure(relief=tk.FLAT)

    def _edit(self):
        """Edit action"""
        if self.on_select:
            self.on_select(self.index)

    def _toggle(self):
        """Toggle enabled state"""
        if self.on_toggle:
            self.on_toggle(self.index)

    def _delete(self):
        """Delete action"""
        if self.on_delete:
            self.on_delete(self.index)

    def _duplicate(self):
        """Duplicate action"""
        if self.on_duplicate:
            self.on_duplicate(self.index)

    def select(self):
        """Mark card as selected"""
        self.is_selected = True
        self.configure(relief=tk.RAISED, borderwidth=3)
        # Add pulse animation
        self._pulse_animation()

    def deselect(self):
        """Mark card as not selected"""
        self.is_selected = False
        self.configure(relief=tk.FLAT, borderwidth=1)

    def _pulse_animation(self, count=0):
        """Subtle pulse animation on selection"""
        if count >= 2:  # Pulse twice
            return

        # Brighten
        def brighten():
            self.configure(style='Selected.Card.TFrame')
            self.after(100, darken)

        def darken():
            self.configure(style='Card.TFrame' if not self.is_selected else 'Selected.Card.TFrame')
            if count < 1:
                self.after(100, lambda: self._pulse_animation(count + 1))

        brighten()

    def update_index(self, new_index: int):
        """Update card index"""
        self.index = new_index
        self.number_label.config(text=f"#{new_index + 1}")

    def update_enabled_state(self, enabled: bool):
        """Update visual enabled state"""
        self.action.enabled = enabled
        status_color = '#00FF00' if enabled else '#FF0000'
        self.status_indicator.config(bg=status_color)

        # Also update opacity/style
        if not enabled:
            # Make card slightly transparent when disabled
            self.configure(style='Disabled.Card.TFrame')
        else:
            self.configure(style='Card.TFrame')


# Test code
if __name__ == "__main__":
    from src.theme import ModernTheme
    from src.action_schema import EnhancedAction

    root = tk.Tk()
    root.title("Action Card Test")
    root.geometry("350x600")

    ModernTheme.configure_style()
    root.configure(bg=ModernTheme.BACKGROUND)

    # Create container
    container = tk.Frame(root, bg=ModernTheme.BACKGROUND)
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create test actions
    actions = [
        EnhancedAction('click', x=100, y=200, description='Click login button'),
        EnhancedAction('type', text='username@example.com', description='Enter email'),
        EnhancedAction('set_value', value='password123', description='Enter password'),
        EnhancedAction('wait', wait_type='duration', duration=2.0, description=''),
        EnhancedAction('find_image', image_name='submit_button', description=''),
    ]

    # Callbacks
    def on_select(index):
        print(f"Selected action {index}")
        # Deselect all
        for card in cards:
            card.deselect()
        # Select clicked
        cards[index].select()

    def on_toggle(index):
        action = actions[index]
        action.enabled = not action.enabled
        cards[index].update_enabled_state(action.enabled)
        print(f"Toggled action {index}: enabled={action.enabled}")

    def on_delete(index):
        print(f"Delete action {index}")

    def on_duplicate(index):
        print(f"Duplicate action {index}")

    # Create cards
    cards = []
    for i, action in enumerate(actions):
        card = ActionCard(container, action, i,
                         on_select=on_select,
                         on_toggle=on_toggle,
                         on_delete=on_delete,
                         on_duplicate=on_duplicate)
        card.pack(fill=tk.X, pady=5)
        cards.append(card)

    root.mainloop()
