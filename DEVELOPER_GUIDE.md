# Developer Guide: Automation Studio v2

This guide provides instructions for developers looking to extend and customize the Automation Studio application.

## Project Structure

The project is organized into the following key modules in the `src/` directory:

- `automation_studio.py`: Main application entry point.
- `studio_layout.py`: Defines the main UI structure and panels.
- `action_card.py`: The UI component for displaying a single action in the workflow list.
- `visual_canvas.py`: The central canvas for displaying screenshots and action annotations.
- `property_editor.py`: The panel on the right for editing the properties of a selected action.
- `action_schema.py`: Contains the data models (`EnhancedAction`) for all supported actions.
- `screenshot_manager.py`: Handles capturing, saving, and loading screenshots.
- `capture_overlay.py`: The full-screen overlay used for capturing screen regions or points.
- `action_recorder.py`: The core logic for recording user interactions (mouse, keyboard).
- `executor.py`: The engine responsible for playing back the recorded actions in a workflow.
- `theme.py`: Contains all UI styling, colors, fonts, and icons.
- `workflow_templates.py`: Manages the creation, saving, and loading of workflow templates.
- `workflow_comments.py`: Manages comments associated with actions in a workflow.

## Adding a New Custom Action

Follow these steps to add a new action type to the application.

### 1. Define the Action in `action_schema.py`

First, you need to define the parameters for your new action. Add a new `dataclass` for your action's parameters in `action_schema.py`. 

For example, to add a "Highlight" action:

```python
# In src/action_schema.py

@dataclass
class HighlightParams:
    x: int
    y: int
    width: int
    height: int
    duration: float = 1.0
    color: str = "red"
```

Then, update the `ActionParams` union type to include your new params class:

```python
# In src/action_schema.py

ActionParams = Union[ClickParams, TypeParams, ..., HighlightParams]
```

### 2. Add the Action to the `EnhancedAction` Class

In the `EnhancedAction` class, add your new action type to the `type` literal and map it to the new `dataclass`.

### 3. Implement the Executor Logic in `executor.py`

In the `SimulationExecutor` class, add a new method to handle the execution of your action. The method should be named `_execute_<action_type>`. 

```python
# In src/executor.py

class SimulationExecutor:
    # ... existing methods

    def _execute_highlight(self, params: HighlightParams):
        self.status_callback(f"Highlighting region at ({params.x}, {params.y})")
        # Your implementation using pyautogui or other libraries
        # For example, draw a rectangle on the screen
        pyautogui.screenshot(region=(params.x, params.y, params.width, params.height))
        # ... (this is a simplified example)
```

### 4. Add the Action to the UI in `automation_studio.py`

In the `show_add_step_menu` method, add a new menu item for your action. If it requires screen capture, use `add_action_with_capture`. If not, use one of the other helper methods.

```python
# In automation_studio.py

def show_add_step_menu(self):
    # ...
    menu.add_command(label="Highlight Region", command=lambda: self.add_action_with_capture('highlight'))
    # ...
```

### 5. Customize the Action Card (Optional)

If your action needs a unique appearance on its action card, you can modify the `ActionCard` class in `src/action_card.py` to customize its display based on the action type.

## UI Customization

To change the application's theme (colors, fonts, etc.), edit the `ModernTheme` class in `src/theme.py`. All UI components reference this class for their styling.

```python
# In src/theme.py

class ModernTheme:
    PRIMARY = "#2563eb"  # Change to your desired primary color
    BACKGROUND = "#f0f2f5"
    # ... and so on
```

## Running Tests

(Placeholder for testing information - no test suite is currently set up).

To ensure the quality of the application, you should create tests for any new functionality you add. The `unittest` or `pytest` frameworks are recommended.

Create a `tests/` directory and add your test files there. For example, `tests/test_executor.py` could contain tests for the action execution logic.
