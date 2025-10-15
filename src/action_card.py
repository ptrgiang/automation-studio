"""
Action Card Widgets for Workflow Panel
Beautiful, draggable cards representing automation actions
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict
from PIL import Image, ImageTk
from src.theme import ModernTheme, Icons
from src.action_schema import EnhancedAction


class ActionCard(ttk.Frame):
    """Visual card representing an action in the workflow"""

    def __init__(self, parent, action: EnhancedAction, index: int,
                 on_select: Optional[Callable] = None,
                 on_toggle: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 on_duplicate: Optional[Callable] = None,
                 on_reorder: Optional[Callable] = None,
                 on_enable_selected: Optional[Callable] = None,
                 on_disable_selected: Optional[Callable] = None,
                 comment: Optional[str] = None):
        super().__init__(parent, style='Card.TFrame')
        self.action = action
        self.index = index
        self.on_select = on_select
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self.on_duplicate = on_duplicate
        self.on_reorder = on_reorder
        self.on_enable_selected = on_enable_selected
        self.on_disable_selected = on_disable_selected
        self.comment = comment

        self.is_selected = False

        self._create_card()
        self._bind_events()
        
        # Apply initial enabled/disabled styling based on action state
        self.update_enabled_state(self.action.enabled)

    def _create_card(self):
        # Main container
        main = ttk.Frame(self, style='Card.TFrame')
        main.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Selection indicator (left border)
        self.selection_indicator = tk.Frame(main, width=3, bg=ModernTheme.BACKGROUND)
        self.selection_indicator.pack(side=tk.LEFT, fill=tk.Y)

        # Left side - Icon
        left_frame = ttk.Frame(main, style='Card.TFrame', width=50)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        icon_label = ttk.Label(left_frame, text=self.action.ui.icon, font=('Segoe UI Emoji', 18), style='Card.TLabel')
        icon_label.pack(expand=True)

        # Right side - Info
        right_frame = ttk.Frame(main, style='Card.TFrame')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, ModernTheme.PADDING_MD))

        # Action type and description
        info_frame = ttk.Frame(right_frame, style='Card.TFrame')
        info_frame.pack(fill=tk.X, pady=(ModernTheme.PADDING_MD, 0))

        self.type_label = ttk.Label(info_frame, text=self.action.type.upper(), font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold'), style='Card.TLabel')
        self.type_label.pack(anchor=tk.W)

        summary = self.action.get_summary()
        self.desc_label = ttk.Label(info_frame, text=summary, style='Card.TLabel', wraplength=200)
        self.desc_label.pack(anchor=tk.W)

        # Comment
        if self.comment:
            comment_label = ttk.Label(right_frame, text=f"💬 {self.comment}", style='Secondary.TLabel', wraplength=200)
            comment_label.pack(anchor=tk.W, pady=(ModernTheme.PADDING_SM, 0))

    def _bind_events(self):
        def bind_recursive(widget):
            widget.bind('<Button-1>', self._on_click)
            widget.bind('<Button-3>', self._on_right_click)

            for child in widget.winfo_children():
                bind_recursive(child)

        bind_recursive(self)

    def _on_click(self, event):
        if self.on_select:
            self.on_select(self.index, event)

    def _on_right_click(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Duplicate", command=self._duplicate)
        menu.add_separator()
        menu.add_command(label="Enable Selected", command=self._enable_selected)
        menu.add_command(label="Disable Selected", command=self._disable_selected)
        menu.add_separator()
        menu.add_command(label="Delete", command=self._delete, foreground=ModernTheme.DESTRUCTIVE)
        menu.tk_popup(event.x_root, event.y_root)

    def _delete(self):
        if self.on_delete:
            self.on_delete(self.index)

    def _duplicate(self):
        if self.on_duplicate:
            self.on_duplicate(self.index)

    def _enable_selected(self):
        if self.on_enable_selected:
            self.on_enable_selected()

    def _disable_selected(self):
        if self.on_disable_selected:
            self.on_disable_selected()

    def select(self):
        self.is_selected = True
        self.selection_indicator.configure(bg=ModernTheme.PRIMARY)

    def deselect(self):
        self.is_selected = False
        self.selection_indicator.configure(bg=ModernTheme.BACKGROUND)

    def update_enabled_state(self, enabled: bool):
        self.action.enabled = enabled
        if not enabled:
            # Apply disabled styling to the main frame and all child widgets
            self.configure(style='Disabled.Card.TFrame')
            self.type_label.configure(style='Disabled.Card.TLabel')
            self.desc_label.configure(style='Disabled.Card.TLabel')
            # Apply to all child widgets recursively
            self._apply_disabled_style_recursive(self, 'Disabled.Card.TLabel')
        else:
            # Apply normal styling to the main frame and all child widgets  
            self.configure(style='Card.TFrame')
            self.type_label.configure(style='Card.TLabel')
            self.desc_label.configure(style='Card.TLabel')
            # Apply to all child widgets recursively
            self._apply_disabled_style_recursive(self, 'Card.TLabel')
    
    def _apply_disabled_style_recursive(self, widget, style_name):
        """Apply style recursively to all child widgets that support styling"""
        for child in widget.winfo_children():
            if isinstance(child, (ttk.Label, ttk.Button)):
                child.configure(style=style_name)
            # Recursively apply to grandchildren
            self._apply_disabled_style_recursive(child, style_name)



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
