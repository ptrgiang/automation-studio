"""
Property Editor Widgets for Properties Panel
Context-aware property editing with validation
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any, List
from src.theme import ModernTheme, Icons
from src.action_schema import EnhancedAction


class PropertyEditor(ttk.Frame):
    """Base class for property editors"""

    def __init__(self, parent, label: str, on_change: Optional[Callable] = None):
        super().__init__(parent, style='TFrame')
        self.label = label
        self.on_change = on_change

        self.pack(fill=tk.X, pady=ModernTheme.PADDING_MD)

        if label:
            label_widget = ttk.Label(self, text=label, style='TLabel', font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD, 'bold'))
            label_widget.pack(anchor=tk.W, pady=(0, ModernTheme.PADDING_SM))

    def _trigger_change(self, value: Any):
        if self.on_change:
            self.on_change(value)


class TextPropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, value: str, on_change: Optional[Callable] = None):
        super().__init__(parent, label, on_change)
        self.entry = ttk.Entry(self, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD))
        self.entry.pack(fill=tk.X)
        self.entry.insert(0, str(value) if value else "")
        self.entry.bind('<KeyRelease>', lambda e: self._trigger_change(self.entry.get()))


class HybridTextPropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, value: str, batch_columns: List[str], on_change: Optional[Callable] = None):
        super().__init__(parent, label, on_change)
        self.batch_columns = batch_columns

        editor_frame = ttk.Frame(self)
        editor_frame.pack(fill=tk.X)

        self.entry = ttk.Entry(editor_frame, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.insert(0, str(value) if value else "")
        self.entry.bind('<KeyRelease>', lambda e: self._trigger_change(self.entry.get()))

        if self.batch_columns:
            self.combobox = ttk.Combobox(editor_frame, values=self.batch_columns, state='readonly', width=15)
            self.combobox.pack(side=tk.LEFT, padx=(ModernTheme.PADDING_SM, 0))
            self.combobox.set("Insert Column...")
            self.combobox.bind('<<ComboboxSelected>>', self._on_column_select)

    def _on_column_select(self, event):
        selected_column = self.combobox.get()
        if selected_column:
            placeholder = f"{{batch:{selected_column}}}"
            self.entry.delete(0, tk.END)
            self.entry.insert(0, placeholder)
            self._trigger_change(placeholder)


class NumberPropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, value: float, on_change: Optional[Callable] = None, min_val: Optional[float] = None, max_val: Optional[float] = None):
        super().__init__(parent, label, on_change)
        self.spinbox = ttk.Spinbox(self, from_=min_val if min_val is not None else -999999, to=max_val if max_val is not None else 999999, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD))
        self.spinbox.pack(fill=tk.X)
        self.spinbox.set(str(value) if value is not None else "0")
        self.spinbox.bind('<KeyRelease>', self._on_change)
        self.spinbox.bind('<<Increment>>', self._on_change)
        self.spinbox.bind('<<Decrement>>', self._on_change)

    def _on_change(self, event=None):
        try:
            val = float(self.spinbox.get())
            self._trigger_change(val)
        except ValueError:
            pass


class ChoicePropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, value: str, choices: List[str], on_change: Optional[Callable] = None):
        super().__init__(parent, label, on_change)
        self.choices = choices
        self.combobox = ttk.Combobox(self, values=choices, state='readonly', font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD))
        self.combobox.pack(fill=tk.X)
        if value in choices:
            self.combobox.set(value)
        elif choices:
            self.combobox.set(choices[0])
        self.combobox.bind('<<ComboboxSelected>>', lambda e: self._trigger_change(self.combobox.get()))


class BooleanPropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, value: bool, on_change: Optional[Callable] = None):
        super().__init__(parent, "", on_change)
        self.var = tk.BooleanVar(value=value)
        self.checkbox = ttk.Checkbutton(self, text=label, variable=self.var, command=self._on_toggle, style='TCheckbutton')
        self.checkbox.pack(anchor=tk.W)

    def _on_toggle(self):
        self._trigger_change(self.var.get())


class CoordinatePropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, x: int, y: int, on_change: Optional[Callable] = None):
        super().__init__(parent, label, on_change)
        coord_frame = ttk.Frame(self, style='TFrame')
        coord_frame.pack(fill=tk.X)

        x_frame = ttk.Frame(coord_frame, style='TFrame')
        x_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, ModernTheme.PADDING_SM))
        ttk.Label(x_frame, text="X:", style='Secondary.TLabel').pack(side=tk.LEFT)
        self.x_entry = ttk.Entry(x_frame, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD), width=8)
        self.x_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.x_entry.insert(0, str(x))
        self.x_entry.bind('<KeyRelease>', self._on_change)

        y_frame = ttk.Frame(coord_frame, style='TFrame')
        y_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(y_frame, text="Y:", style='Secondary.TLabel').pack(side=tk.LEFT)
        self.y_entry = ttk.Entry(y_frame, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD), width=8)
        self.y_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.y_entry.insert(0, str(y))
        self.y_entry.bind('<KeyRelease>', self._on_change)

    def _on_change(self, event=None):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            self._trigger_change((x, y))
        except ValueError:
            pass


class CoordinateDisplayEditor(PropertyEditor):
    """Read-only coordinate display with recapture button"""
    def __init__(self, parent, label: str, x: int, y: int, on_recapture: Optional[Callable] = None):
        super().__init__(parent, label, None)
        self.on_recapture = on_recapture

        # Display frame
        display_frame = ttk.Frame(self, style='TFrame')
        display_frame.pack(fill=tk.X)

        # Coordinates display (read-only)
        info_frame = ttk.Frame(display_frame, style='TFrame')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.coord_label = ttk.Label(info_frame, text=f"X: {x}, Y: {y}",
                                     style='TLabel',
                                     font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD))
        self.coord_label.pack(anchor=tk.W)

        # Recapture button
        recapture_btn = ttk.Button(display_frame, text="📍 Recapture",
                                   style='Outline.TButton',
                                   command=self._on_recapture_click)
        recapture_btn.pack(side=tk.RIGHT, padx=(ModernTheme.PADDING_SM, 0))

    def _on_recapture_click(self):
        if self.on_recapture:
            self.on_recapture()

    def update_coordinates(self, x: int, y: int):
        """Update displayed coordinates"""
        self.coord_label.config(text=f"X: {x}, Y: {y}")


class MultilineTextPropertyEditor(PropertyEditor):
    def __init__(self, parent, label: str, value: str, on_change: Optional[Callable] = None, height: int = 4):
        super().__init__(parent, label, on_change)
        self.text = tk.Text(self, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD), height=height, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, highlightthickness=1, highlightcolor=ModernTheme.RING)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert('1.0', str(value) if value else "")
        self.text.bind('<KeyRelease>', lambda e: self._trigger_change(self.text.get('1.0', 'end-1c')))


class ActionPropertyPanel(ttk.Frame):
    def __init__(self, parent, action: EnhancedAction, on_change: Optional[Callable] = None,
                 batch_columns: List[str] = None, on_recapture: Optional[Callable] = None):
        super().__init__(parent, style='TFrame')
        self.pack(fill=tk.BOTH, expand=True)
        self.action = action
        self.on_change = on_change
        self.on_recapture = on_recapture
        self.batch_columns = batch_columns if batch_columns is not None else []

        self._create_common_properties()
        self._create_type_specific_properties()

    def _create_common_properties(self):
        BooleanPropertyEditor(self, "Enabled", self.action.enabled, on_change=lambda v: self._on_property_change('enabled', v))
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=ModernTheme.PADDING_MD)
        MultilineTextPropertyEditor(self, "Description", self.action.params.get('description', ''), on_change=lambda v: self._on_property_change('description', v), height=3)
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=ModernTheme.PADDING_MD)

    def _create_type_specific_properties(self):
        action_type = self.action.type
        params = self.action.params

        if action_type == 'click':
            CoordinateDisplayEditor(self, "Position", params.get('x', 0), params.get('y', 0),
                                  on_recapture=lambda: self._on_recapture_position())

        if action_type == 'move_mouse':
            CoordinatePropertyEditor(self, "Position", params.get('x', 0), params.get('y', 0), on_change=lambda v: self._on_coords_change(v))

        if action_type == 'type':
            HybridTextPropertyEditor(self, "Text to Type", params.get('text', ''), self.batch_columns, on_change=lambda v: self._on_property_change('text', v))

        if action_type == 'set_value':
            CoordinateDisplayEditor(self, "Position", params.get('x', 0), params.get('y', 0),
                                  on_recapture=lambda: self._on_recapture_position())
            HybridTextPropertyEditor(self, "Value", params.get('value', ''), self.batch_columns, on_change=lambda v: self._on_property_change('value', v))
            ChoicePropertyEditor(self, "Clear Method", params.get('method', 'ctrl_a'), ['ctrl_a', 'backspace', 'triple_click'], on_change=lambda v: self._on_property_change('method', v))

        if action_type == 'wait':
            wait_type = params.get('wait_type', 'duration')
            ChoicePropertyEditor(self, "Wait Type", wait_type, ['duration', 'image'], on_change=lambda v: self._on_property_change('wait_type', v))
            if wait_type == 'duration':
                NumberPropertyEditor(self, "Duration (s)", params.get('duration', 1.0), on_change=lambda v: self._on_property_change('duration', v), min_val=0.1, max_val=300.0)

        if action_type == 'scroll':
            scroll_type = params.get('scroll_type', 'amount')
            ChoicePropertyEditor(self, "Scroll Type", scroll_type, ['amount', 'top', 'bottom'], on_change=lambda v: self._on_property_change('scroll_type', v))
            if scroll_type == 'amount':
                NumberPropertyEditor(self, "Amount", params.get('amount', -300), on_change=lambda v: self._on_property_change('amount', int(v)), min_val=-5000, max_val=5000)

        if action_type == 'find_image':
            TextPropertyEditor(self, "Image Name", params.get('image_name', ''), on_change=lambda v: self._on_property_change('image_name', v))
            NumberPropertyEditor(self, "Confidence", params.get('confidence', 0.8), on_change=lambda v: self._on_property_change('confidence', v), min_val=0.1, max_val=1.0)

        if action_type == 'delete':
            ChoicePropertyEditor(self, "Delete Method", params.get('method', 'ctrl_a'), ['ctrl_a', 'backspace', 'triple_click'], on_change=lambda v: self._on_property_change('method', v))

    def _on_coords_change(self, coords: tuple):
        x, y = coords
        self._on_property_change('x', x)
        self._on_property_change('y', y)

    def _on_recapture_position(self):
        """Trigger position recapture callback"""
        if self.on_recapture:
            self.on_recapture()

    def _on_property_change(self, property_name: str, value: Any):
        if self.on_change:
            self.on_change(property_name, value)


# Test code
if __name__ == "__main__":
    from src.action_schema import EnhancedAction

    root = tk.Tk()
    root.title("Property Editor Test")
    root.geometry("400x700")
    root.configure(bg=ModernTheme.BACKGROUND)

    from src.theme import ModernTheme
    ModernTheme.configure_style()

    # Create container
    container = ttk.Frame(root, style='Panel.TFrame')
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Test action
    action = EnhancedAction('set_value', x=100, y=200, value='test', method='ctrl_a',
                           description='Test set value action')

    # Callback
    def on_change(prop, val):
        print(f"Property '{prop}' changed to: {val}")

    # Create property panel
    panel = ActionPropertyPanel(container, action, on_change=on_change)

    root.mainloop()
