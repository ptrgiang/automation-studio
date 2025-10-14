"""
Property Editor Widgets for Properties Panel
Context-aware property editing with validation
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any, List
from src.theme import ModernTheme
from src.action_schema import EnhancedAction


class PropertyEditor:
    """Base class for property editors"""

    def __init__(self, parent, label: str, value: Any, on_change: Optional[Callable] = None):
        """
        Initialize property editor

        Args:
            parent: Parent widget
            label: Property label
            value: Current value
            on_change: Callback when value changes (value)
        """
        self.parent = parent
        self.label = label
        self.value = value
        self.on_change = on_change

        # Create container
        self.frame = ttk.Frame(parent, style='Panel.TFrame')
        self.frame.pack(fill=tk.X, pady=5)

        # Create label
        label_widget = ttk.Label(self.frame, text=label,
                                style='TLabel',
                                font=(ModernTheme.FONT_FAMILY, 10, 'bold'))
        label_widget.pack(anchor=tk.W, pady=(0, 2))

    def get_value(self) -> Any:
        """Get current value"""
        return self.value

    def set_value(self, value: Any):
        """Set value programmatically"""
        self.value = value

    def _trigger_change(self, value: Any):
        """Trigger change callback"""
        self.value = value
        if self.on_change:
            self.on_change(value)


class TextPropertyEditor(PropertyEditor):
    """Text input property editor"""

    def __init__(self, parent, label: str, value: str, on_change: Optional[Callable] = None,
                 placeholder: str = ""):
        super().__init__(parent, label, value, on_change)

        # Create entry
        self.entry = ttk.Entry(self.frame, font=(ModernTheme.FONT_FAMILY, 10))
        self.entry.pack(fill=tk.X, pady=(0, 2))
        self.entry.insert(0, str(value) if value else "")

        # Bind change event
        self.entry.bind('<KeyRelease>', lambda e: self._trigger_change(self.entry.get()))

    def get_value(self) -> str:
        return self.entry.get()

    def set_value(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(value) if value else "")
        self.value = value


class NumberPropertyEditor(PropertyEditor):
    """Numeric input property editor with validation"""

    def __init__(self, parent, label: str, value: float, on_change: Optional[Callable] = None,
                 min_val: Optional[float] = None, max_val: Optional[float] = None):
        super().__init__(parent, label, value, on_change)

        self.min_val = min_val
        self.max_val = max_val

        # Create spinbox
        self.spinbox = ttk.Spinbox(self.frame,
                                   from_=min_val if min_val is not None else -999999,
                                   to=max_val if max_val is not None else 999999,
                                   font=(ModernTheme.FONT_FAMILY, 10))
        self.spinbox.pack(fill=tk.X, pady=(0, 2))
        self.spinbox.set(str(value) if value is not None else "0")

        # Bind change event
        self.spinbox.bind('<KeyRelease>', self._on_change)
        self.spinbox.bind('<<Increment>>', self._on_change)
        self.spinbox.bind('<<Decrement>>', self._on_change)

    def _on_change(self, event=None):
        try:
            val = float(self.spinbox.get())
            # Apply constraints
            if self.min_val is not None:
                val = max(self.min_val, val)
            if self.max_val is not None:
                val = min(self.max_val, val)
            self._trigger_change(val)
        except ValueError:
            pass  # Invalid input, ignore

    def get_value(self) -> float:
        try:
            return float(self.spinbox.get())
        except ValueError:
            return 0.0

    def set_value(self, value: float):
        self.spinbox.set(str(value))
        self.value = value


class ChoicePropertyEditor(PropertyEditor):
    """Choice/dropdown property editor"""

    def __init__(self, parent, label: str, value: str, choices: List[str],
                 on_change: Optional[Callable] = None):
        super().__init__(parent, label, value, on_change)

        self.choices = choices

        # Create combobox
        self.combobox = ttk.Combobox(self.frame, values=choices, state='readonly',
                                     font=(ModernTheme.FONT_FAMILY, 10))
        self.combobox.pack(fill=tk.X, pady=(0, 2))

        if value in choices:
            self.combobox.set(value)
        elif choices:
            self.combobox.set(choices[0])

        # Bind change event
        self.combobox.bind('<<ComboboxSelected>>', lambda e: self._trigger_change(self.combobox.get()))

    def get_value(self) -> str:
        return self.combobox.get()

    def set_value(self, value: str):
        if value in self.choices:
            self.combobox.set(value)
            self.value = value


class BooleanPropertyEditor(PropertyEditor):
    """Boolean checkbox property editor"""

    def __init__(self, parent, label: str, value: bool, on_change: Optional[Callable] = None):
        # Don't call super().__init__ for boolean, we'll create custom layout
        self.parent = parent
        self.label = label
        self.value = value
        self.on_change = on_change

        # Create container
        self.frame = ttk.Frame(parent, style='Panel.TFrame')
        self.frame.pack(fill=tk.X, pady=5)

        # Create checkbox with label
        self.var = tk.BooleanVar(value=value)
        self.checkbox = ttk.Checkbutton(self.frame, text=label, variable=self.var,
                                       command=self._on_toggle,
                                       style='TCheckbutton')
        self.checkbox.pack(anchor=tk.W)

    def _on_toggle(self):
        self._trigger_change(self.var.get())

    def get_value(self) -> bool:
        return self.var.get()

    def set_value(self, value: bool):
        self.var.set(value)
        self.value = value


class CoordinatePropertyEditor(PropertyEditor):
    """Coordinate (x, y) property editor"""

    def __init__(self, parent, label: str, x: int, y: int, on_change: Optional[Callable] = None):
        super().__init__(parent, label, (x, y), on_change)

        # Create coordinate inputs
        coord_frame = ttk.Frame(self.frame, style='Panel.TFrame')
        coord_frame.pack(fill=tk.X, pady=(0, 2))

        # X coordinate
        x_frame = ttk.Frame(coord_frame, style='Panel.TFrame')
        x_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Label(x_frame, text="X:", style='Secondary.TLabel',
                 font=(ModernTheme.FONT_FAMILY, 9)).pack(side=tk.LEFT, padx=(0, 2))

        self.x_entry = ttk.Entry(x_frame, font=(ModernTheme.FONT_FAMILY, 10), width=10)
        self.x_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.x_entry.insert(0, str(x))
        self.x_entry.bind('<KeyRelease>', self._on_change)

        # Y coordinate
        y_frame = ttk.Frame(coord_frame, style='Panel.TFrame')
        y_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(y_frame, text="Y:", style='Secondary.TLabel',
                 font=(ModernTheme.FONT_FAMILY, 9)).pack(side=tk.LEFT, padx=(0, 2))

        self.y_entry = ttk.Entry(y_frame, font=(ModernTheme.FONT_FAMILY, 10), width=10)
        self.y_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.y_entry.insert(0, str(y))
        self.y_entry.bind('<KeyRelease>', self._on_change)

    def _on_change(self, event=None):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            self._trigger_change((x, y))
        except ValueError:
            pass  # Invalid input, ignore

    def get_value(self) -> tuple:
        try:
            return (int(self.x_entry.get()), int(self.y_entry.get()))
        except ValueError:
            return (0, 0)

    def set_value(self, value: tuple):
        x, y = value
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))
        self.value = value


class MultilineTextPropertyEditor(PropertyEditor):
    """Multiline text property editor"""

    def __init__(self, parent, label: str, value: str, on_change: Optional[Callable] = None,
                 height: int = 4):
        super().__init__(parent, label, value, on_change)

        # Create text widget
        self.text = tk.Text(self.frame, font=(ModernTheme.FONT_FAMILY, 10),
                           height=height, wrap=tk.WORD,
                           bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT,
                           relief=tk.SOLID, borderwidth=1)
        self.text.pack(fill=tk.BOTH, pady=(0, 2))
        self.text.insert('1.0', str(value) if value else "")

        # Bind change event
        self.text.bind('<KeyRelease>', lambda e: self._trigger_change(self.text.get('1.0', 'end-1c')))

    def get_value(self) -> str:
        return self.text.get('1.0', 'end-1c')

    def set_value(self, value: str):
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', str(value) if value else "")
        self.value = value


class ActionPropertyPanel:
    """Complete property panel for an action"""

    def __init__(self, parent, action: EnhancedAction, on_change: Optional[Callable] = None):
        """
        Initialize action property panel

        Args:
            parent: Parent widget
            action: EnhancedAction object
            on_change: Callback when any property changes (property_name, value)
        """
        self.parent = parent
        self.action = action
        self.on_change = on_change
        self.editors = {}

        # Create property editors based on action type
        self._create_common_properties()
        self._create_type_specific_properties()

    def _create_common_properties(self):
        """Create common properties for all actions"""
        # Enabled checkbox
        enabled_editor = BooleanPropertyEditor(
            self.parent, "Enabled", self.action.enabled,
            on_change=lambda v: self._on_property_change('enabled', v)
        )
        self.editors['enabled'] = enabled_editor

        # Add separator
        separator = ttk.Separator(self.parent, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=10)

        # Description
        desc_editor = MultilineTextPropertyEditor(
            self.parent, "Description",
            self.action.params.get('description', ''),
            on_change=lambda v: self._on_property_change('description', v),
            height=3
        )
        self.editors['description'] = desc_editor

        # Add separator
        separator = ttk.Separator(self.parent, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=10)

    def _create_type_specific_properties(self):
        """Create properties specific to action type"""
        action_type = self.action.type
        params = self.action.params

        if action_type in ['click', 'move_mouse']:
            # Coordinates
            x = params.get('x', 0)
            y = params.get('y', 0)
            coord_editor = CoordinatePropertyEditor(
                self.parent, "Position", x, y,
                on_change=lambda v: self._on_coords_change(v)
            )
            self.editors['coordinates'] = coord_editor

        if action_type == 'type':
            # Text to type
            text_editor = MultilineTextPropertyEditor(
                self.parent, "Text to Type",
                params.get('text', ''),
                on_change=lambda v: self._on_property_change('text', v),
                height=4
            )
            self.editors['text'] = text_editor

        if action_type == 'set_value':
            # Value and coordinates
            x = params.get('x', 0)
            y = params.get('y', 0)
            coord_editor = CoordinatePropertyEditor(
                self.parent, "Position", x, y,
                on_change=lambda v: self._on_coords_change(v)
            )
            self.editors['coordinates'] = coord_editor

            value_editor = TextPropertyEditor(
                self.parent, "Value",
                params.get('value', ''),
                on_change=lambda v: self._on_property_change('value', v)
            )
            self.editors['value'] = value_editor

            # Clear method
            method_editor = ChoicePropertyEditor(
                self.parent, "Clear Method",
                params.get('method', 'ctrl_a'),
                ['ctrl_a', 'backspace', 'triple_click'],
                on_change=lambda v: self._on_property_change('method', v)
            )
            self.editors['method'] = method_editor

        if action_type == 'wait':
            # Wait type and duration
            wait_type = params.get('wait_type', 'duration')
            wait_type_editor = ChoicePropertyEditor(
                self.parent, "Wait Type", wait_type,
                ['duration', 'image'],
                on_change=lambda v: self._on_property_change('wait_type', v)
            )
            self.editors['wait_type'] = wait_type_editor

            if wait_type == 'duration':
                duration_editor = NumberPropertyEditor(
                    self.parent, "Duration (seconds)",
                    params.get('duration', 1.0),
                    on_change=lambda v: self._on_property_change('duration', v),
                    min_val=0.1, max_val=300.0
                )
                self.editors['duration'] = duration_editor

        if action_type == 'scroll':
            # Scroll type and amount
            scroll_type = params.get('scroll_type', 'amount')
            scroll_type_editor = ChoicePropertyEditor(
                self.parent, "Scroll Type", scroll_type,
                ['amount', 'top', 'bottom'],
                on_change=lambda v: self._on_property_change('scroll_type', v)
            )
            self.editors['scroll_type'] = scroll_type_editor

            if scroll_type == 'amount':
                amount_editor = NumberPropertyEditor(
                    self.parent, "Amount (negative = down)",
                    params.get('amount', -300),
                    on_change=lambda v: self._on_property_change('amount', int(v)),
                    min_val=-5000, max_val=5000
                )
                self.editors['amount'] = amount_editor

        if action_type == 'find_image':
            # Image name and confidence
            image_name_editor = TextPropertyEditor(
                self.parent, "Image Name",
                params.get('image_name', ''),
                on_change=lambda v: self._on_property_change('image_name', v)
            )
            self.editors['image_name'] = image_name_editor

            confidence_editor = NumberPropertyEditor(
                self.parent, "Confidence (0.0 - 1.0)",
                params.get('confidence', 0.8),
                on_change=lambda v: self._on_property_change('confidence', v),
                min_val=0.1, max_val=1.0
            )
            self.editors['confidence'] = confidence_editor

        if action_type == 'delete':
            # Delete method
            method_editor = ChoicePropertyEditor(
                self.parent, "Delete Method",
                params.get('method', 'ctrl_a'),
                ['ctrl_a', 'backspace', 'triple_click'],
                on_change=lambda v: self._on_property_change('method', v)
            )
            self.editors['method'] = method_editor

    def _on_coords_change(self, coords: tuple):
        """Handle coordinate change"""
        x, y = coords
        self._on_property_change('x', x)
        self._on_property_change('y', y)

    def _on_property_change(self, property_name: str, value: Any):
        """Handle property change"""
        # Update action
        if property_name == 'enabled':
            self.action.enabled = value
        else:
            self.action.params[property_name] = value

        # Trigger callback
        if self.on_change:
            self.on_change(property_name, value)

    def get_all_values(self) -> Dict[str, Any]:
        """Get all current property values"""
        values = {}
        for name, editor in self.editors.items():
            values[name] = editor.get_value()
        return values


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
