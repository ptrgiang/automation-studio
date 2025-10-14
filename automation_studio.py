"""
Automation Studio
Visual Automation Tool with Full Capture Integration
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import io
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Encoding setup
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# Import Phase 1 & 2 components
from src.theme import ModernTheme, Icons
from src.studio_layout import StudioLayout, WorkflowPanel
from src.action_schema import EnhancedAction, ActionSchemaManager
from src.screenshot_manager import ScreenshotManager
from src.capture_overlay import CaptureOverlay, CaptureMode, CaptureConfirmDialog
from src.visual_canvas import VisualCanvas, ActionAnnotation
from src.action_card import ActionCard
from src.variable_manager import VariableManagerDialog
from src.execution_popup import ExecutionPopup
from pynput import keyboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_studio.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class AutomationStudio:
    """Main Automation Studio application with Phase 2 integration"""

    def __init__(self, root):
        self.root = root
        self.root.title("Automation Studio - Visual Automation")
        self.root.geometry("1200x700")

        # Apply modern theme
        ModernTheme.configure_style()
        self.root.configure(bg=ModernTheme.BACKGROUND)

        # Initialize state
        self.actions = []  # List of EnhancedAction objects
        self.selected_action_index = None
        self.action_cards = []  # List of ActionCard widgets
        self.batch_data = []
        self.batch_columns = []

        # Initialize managers
        self.screenshot_manager = ScreenshotManager()

        # Recording system
        self.action_recorder = None
        self.recording_overlay = None
        self.is_recording = False

        # Phase 6 systems
        from src.workflow_templates import TemplateManager
        from src.workflow_comments import CommentManager
        self.template_manager = TemplateManager()
        self.comment_manager = CommentManager()

        # Create studio layout first
        self.studio_callbacks = {
            'add_step': self.show_add_step_menu,
        }
        self.studio = StudioLayout(self.root, callbacks=self.studio_callbacks)

        # Initialize visual canvas with callbacks
        self.visual_canvas = VisualCanvas(
            self.studio.canvas_panel.canvas,
            on_annotation_click=self.select_action,
            on_annotation_double_click=self._edit_action_from_canvas,
            on_zoom_change=self._update_zoom_label
        )

        # Create menu and toolbar (after visual_canvas exists)
        self._create_menu()
        self._create_toolbar()

        # Connect zoom buttons
        self._connect_canvas_controls()

        # Set minimum window size
        self.root.minsize(1200, 700)

        # Welcome message
        self.update_status("Welcome to Automation Studio! Click '+ Add Step' to begin.")

        logging.info("Automation Studio initialized with full features")

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label=f"{Icons.FOLDER} Open Workflow...",
                             command=self.load_workflow, accelerator="Ctrl+O")
        file_menu.add_command(label=f"{Icons.SAVE} Save Workflow...",
                             command=self.save_workflow, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label=f"{Icons.SAVE} Export to Classic Format...",
                             command=self.export_classic)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected,
                             accelerator="Del")
        edit_menu.add_command(label="Duplicate Selected", command=self.duplicate_selected,
                             accelerator="Ctrl+D")
        edit_menu.add_separator()
        edit_menu.add_command(label="💬 Add Comment", command=self.add_comment_to_selected,
                             accelerator="Ctrl+M")
        edit_menu.add_separator()
        edit_menu.add_command(label="Manage Batch Variables...", command=self.open_variable_manager)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.visual_canvas.zoom_in,
                             accelerator="+")
        view_menu.add_command(label="Zoom Out", command=self.visual_canvas.zoom_out,
                             accelerator="-")
        view_menu.add_command(label="Fit to Window", command=self.visual_canvas.zoom_fit,
                             accelerator="0")

        # Templates menu
        templates_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Templates", menu=templates_menu)
        templates_menu.add_command(label="📋 Insert Template...", command=self.insert_template)
        templates_menu.add_command(label="💾 Save as Template...", command=self.save_as_template)
        templates_menu.add_separator()
        templates_menu.add_command(label="📚 Browse Templates", command=self.browse_templates)

        # Playback menu
        playback_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Playback", menu=playback_menu)
        playback_menu.add_command(label=f"{Icons.PLAY} Play Workflow",
                                 command=self.play_workflow, accelerator="F5")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label=f"{Icons.INFO} About", command=self.show_about)

        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_workflow())
        self.root.bind('<Control-o>', lambda e: self.load_workflow())
        self.root.bind('<Control-d>', lambda e: self.duplicate_selected())
        self.root.bind('<Control-m>', lambda e: self.add_comment_to_selected())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<F5>', lambda e: self.play_workflow())

        # Navigation shortcuts
        self.root.bind('<Up>', lambda e: self._navigate_up())
        self.root.bind('<Down>', lambda e: self._navigate_down())
        self.root.bind('<Control-Up>', lambda e: self._move_action_up())
        self.root.bind('<Control-Down>', lambda e: self._move_action_down())

    def _create_toolbar(self):
        """Create main toolbar"""
        toolbar = ttk.Frame(self.root, style='Toolbar.TFrame', height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))
        toolbar.pack_propagate(False)

        # File operations
        ttk.Button(toolbar, text=f"{Icons.FOLDER} Open",
                  command=self.load_workflow).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=f"{Icons.SAVE} Save",
                  command=self.save_workflow).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Record button
        self.record_btn = ttk.Button(toolbar, text="🔴 Record",
                                     command=self.start_recording,
                                     style='Danger.TButton')
        self.record_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Playback controls
        ttk.Button(toolbar, text=f"{Icons.PLAY} Play",
                  command=self.play_workflow,
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)

        # Status
        self.status_label = ttk.Label(toolbar, text="Ready",
                                     style='Secondary.TLabel')
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def open_variable_manager(self):
        """Open the variable manager dialog."""
        def on_save(data, columns):
            self.batch_data = data
            self.batch_columns = columns
            self.update_status(f"Saved {len(data)} batch rows.")

        dialog = VariableManagerDialog(self.root, self.batch_data, self.batch_columns, on_save=on_save)
        dialog.wait_window()

    def _connect_canvas_controls(self):
        """Connect canvas zoom controls to visual canvas"""
        # Find and configure zoom buttons in canvas panel
        toolbar = None
        for child in self.studio.canvas_panel.winfo_children():
            if isinstance(child, ttk.Frame):
                # Check if it's the toolbar
                for btn in child.winfo_children():
                    if isinstance(btn, ttk.Button):
                        text = btn.cget('text')
                        if text == '-':
                            btn.configure(command=self.visual_canvas.zoom_out)
                        elif text == '+':
                            btn.configure(command=self.visual_canvas.zoom_in)
                        elif text == 'Fit':
                            btn.configure(command=self.visual_canvas.zoom_fit)

    def update_status(self, message: str):
        """Update status message"""
        self.status_label.config(text=message)
        self.studio.canvas_panel.info_label.config(text=message)
        logging.info(message)

    def _update_zoom_label(self, zoom_percentage: int):
        """Update zoom label with current percentage"""
        self.studio.canvas_panel.zoom_label.config(text=f"{zoom_percentage}%")

    def show_add_step_menu(self):
        """Show menu to add a new step"""
        menu = tk.Menu(self.root, tearoff=0)

        # Visual actions (require capture)
        menu.add_command(label="Click", command=lambda: self.add_action_with_capture('click'))
        menu.add_command(label="Set Value (Click & Type)",
                        command=lambda: self.add_action_with_capture('set_value'))
        menu.add_command(label="Find Image",
                        command=lambda: self.add_action_with_capture('find_image'))
        menu.add_separator()

        # Non-visual actions
        menu.add_command(label="Type Text", command=lambda: self.add_text_action('type'))
        menu.add_command(label="Press Key (Enter, Tab, etc)", command=lambda: self.add_key_press_action())
        menu.add_command(label="Wait", command=lambda: self.add_wait_action())
        menu.add_command(label="Scroll", command=lambda: self.add_scroll_action())
        menu.add_command(label="Delete/Clear", command=lambda: self.add_simple_action('delete'))

        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def add_action_with_capture(self, action_type: str):
        """Add action that requires screen capture"""
        self.update_status(f"Prepare to capture target for {action_type}...")

        # Minimize window before capture
        self.root.iconify()

        # Wait a moment for window to minimize
        def start_capture():
            # Determine capture mode
            if action_type in ['click']:
                mode = CaptureMode.POINT
            else:
                mode = CaptureMode.REGION

            # Show capture overlay
            def on_capture_complete(result):
                # Restore window
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()

                if not result.get('success'):
                    self.update_status("Capture cancelled")
                    return

                # Show confirmation dialog
                def on_confirm(capture_data):
                    self._create_action_from_capture(action_type, capture_data)

                def on_recapture():
                    # Retry capture
                    self.add_action_with_capture(action_type)

                def on_cancel():
                    self.update_status("Action cancelled")

                confirm_dialog = CaptureConfirmDialog(
                    self.root, result,
                    on_confirm=on_confirm,
                    on_recapture=on_recapture,
                    on_cancel=on_cancel
                )
                confirm_dialog.show()

            overlay = CaptureOverlay(self.root, mode=mode, callback=on_capture_complete)
            overlay.show()

        # Delay to allow window to minimize
        self.root.after(300, start_capture)

    def _create_action_from_capture(self, action_type: str, capture_data: Dict):
        """Create action from capture data"""
        x = capture_data['x']
        y = capture_data['y']
        screenshot = capture_data['screenshot']
        mode = capture_data['mode']

        # Save screenshot and create thumbnail
        if mode == CaptureMode.POINT:
            full_path, region_path, region_dict = self.screenshot_manager.capture_point_with_context(
                x, y, context_size=100
            )
        else:
            full_path = self.screenshot_manager._generate_filename()
            full_filepath = self.screenshot_manager.screenshots_dir / full_path
            screenshot.save(str(full_filepath), 'PNG')

            region_dict = {
                'x': x,
                'y': y,
                'width': capture_data['width'],
                'height': capture_data['height']
            }

            # Extract region
            region = screenshot.crop((x, y, x + region_dict['width'], y + region_dict['height']))
            region_filename = self.screenshot_manager._generate_filename("region")
            region_path = str(self.screenshot_manager.regions_dir / region_filename)
            region.save(region_path, 'PNG')
            full_path = str(full_filepath)

        # Create thumbnail
        thumb_path = self.screenshot_manager.create_thumbnail(region_path)

        # Create action with visual metadata
        action_params = {
            'x': x,
            'y': y,
            'description': f"{action_type.title()} at ({x}, {y})",
        }

        # Get additional parameters for set_value
        if action_type == 'set_value':
            from src.gui_modern import ModernDialog
            result = ModernDialog.create_input_dialog(self.root, "Set Value", [
                {'name': 'value', 'label': 'Value to set:', 'type': 'text', 'default': ''},
                {'name': 'method', 'label': 'Clear method:', 'type': 'choice',
                 'choices': ['ctrl_a', 'backspace', 'triple_click'], 'default': 'ctrl_a'}
            ])

            if result:
                action_params['value'] = result['value']
                action_params['method'] = result['method']
            else:
                # User cancelled - don't create action
                self.update_status("Action cancelled")
                return

        if action_type == 'find_image':
            action_params['image_path'] = region_path
            action_params['image_name'] = f"image_{len(self.actions)}"
            action_params['confidence'] = 0.8

        action = EnhancedAction(action_type, **action_params)
        action.ui.order = len(self.actions)

        # Add visual metadata
        action.visual.screenshot_path = full_path
        action.visual.capture_region = region_dict
        action.visual.thumbnail_path = thumb_path
        action.visual.screen_resolution = self.screenshot_manager.get_screen_resolution()

        # Add action
        self.actions.append(action)
        self._refresh_workflow()

        # Load screenshot on canvas if first action
        if len(self.actions) == 1:
            self.visual_canvas.load_screenshot(screenshot)

        # Add annotation to canvas
        self._add_canvas_annotation(action, len(self.actions) - 1)

        self.update_status(f"Added {action_type} action with visual capture")
        logging.info(f"Created {action_type} action with visual data")

    def _add_canvas_annotation(self, action: EnhancedAction, index: int):
        """Add annotation to canvas for action"""
        if not action.visual.capture_region:
            return

        region = action.visual.capture_region
        x = region.get('x', action.params.get('x', 0))
        y = region.get('y', action.params.get('y', 0))
        width = region.get('width')
        height = region.get('height')

        annotation = ActionAnnotation(
            index, action.type, x, y, width, height,
            color=action.ui.color
        )

        self.visual_canvas.add_annotation(annotation)

    def add_text_action(self, action_type: str):
        """Add type action"""
        from src.gui_modern import ModernDialog

        result = ModernDialog.create_input_dialog(self.root, "Type Text", [
            {'name': 'text', 'label': 'Text to type:', 'type': 'text', 'default': ''},
            {'name': 'description', 'label': 'Description:', 'type': 'text', 'default': ''}
        ])

        if result and result['text']:
            action = EnhancedAction(action_type,
                                   text=result['text'],
                                   description=result['description'] or f"Type: {result['text'][:30]}")
            action.ui.order = len(self.actions)
            self.actions.append(action)
            self._refresh_workflow()
            self.update_status(f"Added {action_type} action")

    def add_key_press_action(self):
        """Add key press action (Enter, Tab, Escape, etc)"""
        # Create custom dialog with dropdown instead of radio buttons
        dialog = tk.Toplevel(self.root)
        dialog.title("Press Key")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=ModernTheme.BACKGROUND)

        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")

        result = {'cancelled': True}

        # Content
        content = tk.Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(content, text="Press Key",
                font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT).pack(anchor=tk.W, pady=(0, 15))

        # Key selection
        tk.Label(content, text="Key to press:",
                font=(ModernTheme.FONT_FAMILY, 10),
                bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT).pack(anchor=tk.W, pady=(0, 5))

        key_var = tk.StringVar(value='enter')
        key_choices = ['enter', 'tab', 'escape', 'space', 'backspace', 'delete',
                      'up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown',
                      'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']

        key_combo = ttk.Combobox(content, textvariable=key_var, values=key_choices,
                                state='readonly', width=30)
        key_combo.pack(fill=tk.X, pady=(0, 15))

        # Description
        tk.Label(content, text="Description (optional):",
                font=(ModernTheme.FONT_FAMILY, 10),
                bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT).pack(anchor=tk.W, pady=(0, 5))

        desc_entry = ttk.Entry(content, width=30)
        desc_entry.pack(fill=tk.X, pady=(0, 20))

        # Buttons
        btn_frame = tk.Frame(content, bg=ModernTheme.BACKGROUND)
        btn_frame.pack()

        def on_ok():
            result['cancelled'] = False
            result['key'] = key_var.get()
            result['description'] = desc_entry.get()
            dialog.destroy()

        def on_cancel():
            result['cancelled'] = True
            dialog.destroy()

        ttk.Button(btn_frame, text=f"{Icons.CHECK} OK",
                  command=on_ok, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=f"{Icons.CLOSE} Cancel",
                  command=on_cancel, style='Outline.TButton').pack(side=tk.LEFT, padx=5)

        # Bind keys
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        # Wait for dialog
        dialog.wait_window()

        # Process result
        if not result.get('cancelled'):
            key = result['key']
            action = EnhancedAction('key_press',
                                   key=key,
                                   description=result['description'] or f"Press {key.upper()}")
            action.ui.order = len(self.actions)
            self.actions.append(action)
            self._refresh_workflow()
            self.update_status(f"Added key press action: {key}")
            logging.info(f"Added key_press action to workflow: {action.get_summary()}")

    def add_wait_action(self):
        """Add wait action"""
        from src.gui_modern import ModernDialog

        result = ModernDialog.create_input_dialog(self.root, "Wait", [
            {'name': 'duration', 'label': 'Duration (seconds):', 'type': 'number', 'default': '1.0'}
        ])

        if result:
            try:
                duration = float(result['duration'])
                action = EnhancedAction('wait',
                                       wait_type='duration',
                                       duration=duration,
                                       description=f"Wait {duration}s")
                action.ui.order = len(self.actions)
                self.actions.append(action)
                self._refresh_workflow()
                self.update_status("Added wait action")
            except ValueError:
                messagebox.showerror("Error", "Invalid duration")

    def add_scroll_action(self):
        """Add scroll action"""
        from src.gui_modern import ModernDialog

        result = ModernDialog.create_input_dialog(self.root, "Scroll", [
            {'name': 'scroll_type', 'label': 'Scroll type:', 'type': 'choice',
             'choices': ['amount', 'top', 'bottom'], 'default': 'amount'},
            {'name': 'amount', 'label': 'Amount (negative=down):', 'type': 'number', 'default': '-300'}
        ])

        if result:
            try:
                amount = int(result['amount']) if result['scroll_type'] == 'amount' else None
                action = EnhancedAction('scroll',
                                       scroll_type=result['scroll_type'],
                                       amount=amount,
                                       description=f"Scroll {result['scroll_type']}")
                action.ui.order = len(self.actions)
                self.actions.append(action)
                self._refresh_workflow()
                self.update_status("Added scroll action")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")

    def add_simple_action(self, action_type: str):
        """Add simple action without parameters"""
        action = EnhancedAction(action_type, method='ctrl_a',
                               description=f"{action_type.title()} field")
        action.ui.order = len(self.actions)
        self.actions.append(action)
        self._refresh_workflow()
        self.update_status(f"Added {action_type} action")

    def _refresh_workflow(self):
        """Refresh workflow panel with current actions"""
        # Clear existing cards
        self.studio.workflow_panel.clear_actions()
        self.action_cards.clear()

        # Create cards for each action
        for i, action in enumerate(self.actions):
            # Get comment if exists
            comment_text = None
            if self.comment_manager.has_comment(i):
                comment_text = self.comment_manager.get_comment(i).text

            card = ActionCard(
                self.studio.workflow_panel.actions_frame,
                action, i,
                on_select=self.select_action,
                on_toggle=self.toggle_action,
                on_delete=self.delete_action,
                on_duplicate=self.duplicate_action,
                on_reorder=self.reorder_action,
                comment=comment_text
            )
            card.pack(fill=tk.X, pady=5)
            self.action_cards.append(card)

            # Bind mouse wheel to card and all its children
            self.studio.workflow_panel.bind_mousewheel_to_widget(card)

        # Update counter
        self.studio.workflow_panel.update_counter(len(self.actions))

    def select_action(self, index: int):
        """Select an action"""
        self.selected_action_index = index

        # Deselect all cards
        for card in self.action_cards:
            card.deselect()

        # Select clicked card
        if 0 <= index < len(self.action_cards):
            self.action_cards[index].select()

        # Highlight on canvas
        self.visual_canvas.select_annotation(index)

        # Show properties in properties panel
        if 0 <= index < len(self.actions):
            action = self.actions[index]
            self.studio.properties_panel.show_action_properties(
                action,
                on_change=lambda prop, val: self._on_property_change(index, prop, val),
                batch_columns=self.batch_columns
            )

        logging.info(f"Selected action {index}")

    def _on_property_change(self, index: int, property_name: str, value):
        """Handle property change from properties panel"""
        if 0 <= index < len(self.actions):
            action = self.actions[index]

            # Update the action
            if property_name == 'enabled':
                action.enabled = value
                # Update card visual state
                if index < len(self.action_cards):
                    self.action_cards[index].update_enabled_state(value)
            else:
                # Update parameter
                action.params[property_name] = value

            # If coordinates changed, update canvas annotation
            if property_name in ['x', 'y'] and action.has_visual_data():
                # Update capture region
                if 'x' in action.visual.capture_region:
                    action.visual.capture_region['x'] = action.params.get('x', 0)
                if 'y' in action.visual.capture_region:
                    action.visual.capture_region['y'] = action.params.get('y', 0)

                # Redraw canvas annotations
                self.visual_canvas.clear_annotations()
                for i, act in enumerate(self.actions):
                    if act.has_visual_data():
                        self._add_canvas_annotation(act, i)

            # Refresh card description if description changed
            if property_name == 'description':
                self._refresh_workflow()

            self.update_status(f"Updated {property_name} for action #{index + 1}")
            logging.info(f"Property '{property_name}' changed to '{value}' for action {index}")

    def toggle_action(self, index: int):
        """Toggle action enabled state"""
        if 0 <= index < len(self.actions):
            action = self.actions[index]
            action.enabled = not action.enabled
            self.action_cards[index].update_enabled_state(action.enabled)
            logging.info(f"Toggled action {index}: enabled={action.enabled}")

    def delete_action(self, index: int):
        """Delete an action"""
        if messagebox.askyesno("Delete Action",
                              f"Delete action #{index + 1}?"):
            self.actions.pop(index)
            self.visual_canvas.remove_annotation(index)
            # Update comment indices after deletion
            self.comment_manager.shift_indices_after_delete(index)
            self._refresh_workflow()
            self.update_status(f"Deleted action #{index + 1}")

    def delete_selected(self):
        """Delete selected action"""
        if self.selected_action_index is not None:
            self.delete_action(self.selected_action_index)
            self.selected_action_index = None

    def duplicate_action(self, index: int):
        """Duplicate an action"""
        if 0 <= index < len(self.actions):
            import copy
            action_copy = copy.deepcopy(self.actions[index])
            action_copy.ui.order = len(self.actions)
            self.actions.insert(index + 1, action_copy)
            self._refresh_workflow()
            self.update_status(f"Duplicated action #{index + 1}")

    def duplicate_selected(self):
        """Duplicate selected action"""
        if self.selected_action_index is not None:
            self.duplicate_action(self.selected_action_index)

    def reorder_action(self, from_index: int, to_index: int):
        """Reorder action by drag-and-drop"""
        if from_index == to_index:
            return

        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            # Move action in list
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)

            # Update comment indices
            # When dragging from position A to position B, we need to:
            # 1. Move comment at A to B
            # 2. Shift all comments between A and B
            if from_index < to_index:
                # Moving down: shift comments between from+1 and to down by 1
                for i in range(from_index + 1, to_index + 1):
                    if self.comment_manager.has_comment(i):
                        comment = self.comment_manager.comments.pop(i)
                        comment.action_index = i - 1
                        self.comment_manager.comments[i - 1] = comment
                # Move original comment
                if self.comment_manager.has_comment(from_index):
                    comment = self.comment_manager.comments.pop(from_index)
                    comment.action_index = to_index
                    self.comment_manager.comments[to_index] = comment
            else:
                # Moving up: shift comments between to and from-1 up by 1
                for i in range(from_index - 1, to_index - 1, -1):
                    if self.comment_manager.has_comment(i):
                        comment = self.comment_manager.comments.pop(i)
                        comment.action_index = i + 1
                        self.comment_manager.comments[i + 1] = comment
                # Move original comment
                if self.comment_manager.has_comment(from_index):
                    comment = self.comment_manager.comments.pop(from_index)
                    comment.action_index = to_index
                    self.comment_manager.comments[to_index] = comment

            # Refresh UI
            self._refresh_workflow()

            # Redraw all canvas annotations
            self.visual_canvas.clear_annotations()
            for i, act in enumerate(self.actions):
                if act.has_visual_data():
                    self._add_canvas_annotation(act, i)

            # Select moved action at new position
            self.select_action(to_index)

            self.update_status(f"Moved action from #{from_index + 1} to #{to_index + 1}")
            logging.info(f"Reordered action: {from_index} → {to_index}")

    def _navigate_up(self):
        """Navigate to previous action"""
        if self.selected_action_index is None:
            if self.actions:
                self.select_action(0)
        elif self.selected_action_index > 0:
            self.select_action(self.selected_action_index - 1)

    def _navigate_down(self):
        """Navigate to next action"""
        if self.selected_action_index is None:
            if self.actions:
                self.select_action(0)
        elif self.selected_action_index < len(self.actions) - 1:
            self.select_action(self.selected_action_index + 1)

    def _move_action_up(self):
        """Move selected action up in list"""
        if self.selected_action_index is not None and self.selected_action_index > 0:
            self.reorder_action(self.selected_action_index, self.selected_action_index - 1)

    def _move_action_down(self):
        """Move selected action down in list"""
        if self.selected_action_index is not None and self.selected_action_index < len(self.actions) - 1:
            self.reorder_action(self.selected_action_index, self.selected_action_index + 1)

    def _edit_action_from_canvas(self, index: int):
        """Edit action by double-clicking canvas annotation"""
        if 0 <= index < len(self.actions):
            action = self.actions[index]
            # Show action details in a dialog
            from src.gui_modern import ModernDialog
            import json

            details = {
                'type': action.type,
                'enabled': action.enabled,
                'params': action.params,
                'description': action.get_summary()
            }

            detail_text = json.dumps(details, indent=2)

            dialog = tk.Toplevel(self.root)
            dialog.title(f"Action #{index + 1} Details")
            dialog.geometry("500x400")

            text_widget = tk.Text(dialog, font=('Consolas', 10), wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert('1.0', detail_text)
            text_widget.configure(state='disabled')

            ttk.Button(dialog, text="Close",
                      command=dialog.destroy).pack(pady=10)

    def load_workflow(self):
        """Load workflow from file"""
        filepath = filedialog.askopenfilename(
            title="Open Workflow",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                import json
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                actions_data = data.get('actions', [])
                self.actions = [EnhancedAction.from_dict(a) for a in actions_data]
                self.batch_columns = data.get('batch_columns', [])
                self.batch_data = data.get('batch_data', [])
                # For backward compatibility with old format
                if not self.batch_data and 'batch_variables' in data:
                    self.batch_columns = ['variable']
                    self.batch_data = [{'variable': var} for var in data['batch_variables']]

                self._refresh_workflow()

                # Load comments if present
                if 'comments' in data:
                    self.comment_manager.from_dict(data['comments'])

                # Load first screenshot if available
                for action in self.actions:
                    if action.has_visual_data() and action.visual.screenshot_path:
                        try:
                            from PIL import Image
                            screenshot = Image.open(action.visual.screenshot_path)
                            self.visual_canvas.load_screenshot(screenshot)

                            # Add all annotations
                            for i, act in enumerate(self.actions):
                                if act.has_visual_data():
                                    self._add_canvas_annotation(act, i)
                            break
                        except:
                            pass

                self.update_status(f"Loaded {len(self.actions)} actions")
                messagebox.showinfo("Success", f"Loaded {len(self.actions)} actions")

            except Exception as e:
                logging.error(f"Error loading: {str(e)}")
                messagebox.showerror("Error", f"Failed to load:\n{str(e)}")

    def save_workflow(self):
        """Save workflow to file"""
        if not self.actions:
            messagebox.showwarning("No Actions", "No actions to save")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Workflow",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if filepath:
            try:
                import json
                data = {
                    'version': '2.1',
                    'created': datetime.now().isoformat(),
                    'total_actions': len(self.actions),
                    'actions': [a.to_dict() for a in self.actions],
                    'comments': self.comment_manager.to_dict(),
                    'batch_columns': self.batch_columns,
                    'batch_data': self.batch_data
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                self.update_status(f"Saved {len(self.actions)} actions")
                messagebox.showinfo("Success", "Workflow saved")

            except Exception as e:
                logging.error(f"Error saving: {str(e)}")
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")

    def export_classic(self):
        """Export to classic format"""
        if not self.actions:
            messagebox.showwarning("No Actions", "No actions to export")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export to Classic Format",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if filepath:
            try:
                import json
                classic_actions = ActionSchemaManager.export_simulation(
                    self.actions, include_visual=False
                )

                data = {
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'total_actions': len(classic_actions),
                    'actions': classic_actions
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                messagebox.showinfo("Success", f"Exported {len(classic_actions)} actions")

            except Exception as e:
                logging.error(f"Error exporting: {str(e)}")
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def play_workflow(self):
        """Play workflow with a transparent popup for status."""
        from src.executor import SimulationExecutor
        if not self.actions:
            messagebox.showwarning("No Actions", "No actions to play.")
            return

        is_batch = any('{batch:' in str(action.params.get('text', '')) or '{batch:' in str(action.params.get('value', '')) for action in self.actions)

        if is_batch and not self.batch_data:
            messagebox.showwarning("No Batch Data", "Workflow requires batch data. Please add data via 'Edit > Manage Variables'.")
            return

        # --- Setup for execution ---
        self.root.withdraw()
        popup = ExecutionPopup(self.root)
        popup.show()

        stop_execution = False
        pause_execution = False

        def on_press(key):
            nonlocal stop_execution, pause_execution
            try:
                if key.char == 's':
                    stop_execution = True
                elif key.char == 'p':
                    pause_execution = not pause_execution
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        def stop_callback():
            return stop_execution

        def pause_callback():
            return pause_execution

        def progress_callback(current_step, next_step):
            self.root.after(0, popup.update_progress, current_step, next_step)

        executor = SimulationExecutor(
            stop_callback=stop_callback,
            pause_callback=pause_callback,
            status_callback=lambda msg: self.root.after(0, self.update_status, msg),
            progress_callback=progress_callback
        )

        def execution_target():
            try:
                classic_actions = ActionSchemaManager.export_simulation(self.actions, include_visual=False)
                if is_batch:
                    executor.execute_batch(classic_actions, self.batch_data)
                else:
                    executor.execute_simulation(classic_actions)
            finally:
                listener.stop()
                self.root.after(0, popup.destroy)
                self.root.after(0, self.root.deiconify)

        import threading
        thread = threading.Thread(target=execution_target)
        thread.daemon = True
        thread.start()

    def start_recording(self):
        """Start recording mode"""
        if self.is_recording:
            return

        from src.action_recorder import ActionRecorder, RecordingState
        from src.recording_overlay import RecordingOverlay

        # Ask for confirmation
        if not messagebox.askyesno("Start Recording",
                                   "Start recording your actions?\n\n" +
                                   "All clicks, typing, and scrolling will be captured.\n" +
                                   "Press 'Stop' in the overlay when done."):
            return

        # Minimize main window
        self.root.iconify()

        # Create recorder
        self.action_recorder = ActionRecorder(
            self.screenshot_manager,
            on_action_recorded=self._on_action_recorded,
            on_state_change=self._on_recording_state_change
        )

        # Create overlay
        self.recording_overlay = RecordingOverlay(
            self.root,
            on_pause=self.pause_recording,
            on_resume=self.resume_recording,
            on_stop=self.stop_recording
        )
        self.recording_overlay.show()

        # Start recording after short delay
        self.root.after(1000, self._begin_recording)

        self.is_recording = True
        self.record_btn.config(state='disabled')
        self.update_status("Recording started...")
        logging.info("Recording mode started")

    def _begin_recording(self):
        """Begin actual recording (after delay)"""
        if self.action_recorder:
            self.action_recorder.start_recording()

    def pause_recording(self):
        """Pause recording"""
        if self.action_recorder and self.action_recorder.is_recording():
            self.action_recorder.pause_recording()
            if self.recording_overlay:
                self.recording_overlay.set_paused(True)
            logging.info("Recording paused")

    def resume_recording(self):
        """Resume recording"""
        if self.action_recorder and self.action_recorder.is_paused():
            self.action_recorder.resume_recording()
            if self.recording_overlay:
                self.recording_overlay.set_paused(False)
            logging.info("Recording resumed")

    def stop_recording(self):
        """Stop recording and process captured actions"""
        if not self.is_recording or not self.action_recorder:
            return

        # Stop recording
        recorded_actions = self.action_recorder.stop_recording()

        # Destroy overlay
        if self.recording_overlay:
            self.recording_overlay.destroy()
            self.recording_overlay = None

        # Restore main window
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        # Add recorded actions to workflow
        if recorded_actions:
            for action in recorded_actions:
                self.actions.append(action)

            self._refresh_workflow()

            # Load first screenshot if this is the first set of actions
            if len(recorded_actions) > 0 and recorded_actions[0].has_visual_data():
                if not self.visual_canvas.has_screenshot():
                    from PIL import Image
                    try:
                        screenshot = Image.open(recorded_actions[0].visual.screenshot_path)
                        self.visual_canvas.load_screenshot(screenshot)
                    except:
                        pass

            # Add all annotations
            for i, action in enumerate(self.actions):
                if action.has_visual_data():
                    self._add_canvas_annotation(action, i)

            messagebox.showinfo("Recording Complete",
                              f"Recorded {len(recorded_actions)} action{'s' if len(recorded_actions) != 1 else ''}!\n\n" +
                              "Actions have been added to your workflow.")

            self.update_status(f"Recording complete: {len(recorded_actions)} actions added")
        else:
            messagebox.showinfo("Recording Complete", "No actions were recorded.")
            self.update_status("Recording stopped (no actions)")

        # Cleanup
        self.is_recording = False
        self.action_recorder = None
        self.record_btn.config(state='normal')

        logging.info(f"Recording stopped. Added {len(recorded_actions)} actions")

    def _on_action_recorded(self, action):
        """Callback when action is recorded"""
        if self.recording_overlay:
            count = self.action_recorder.get_recorded_count()
            self.recording_overlay.update_count(count)
        logging.info(f"Action recorded: {action.type} - {action.get_summary()}")

    def _on_recording_state_change(self, state):
        """Callback when recording state changes"""
        from src.action_recorder import RecordingState
        logging.info(f"Recording state changed to: {state.value}")

    def insert_template(self):
        """Insert template workflow"""
        from src.gui_modern import ModernDialog

        # Get all templates
        templates = self.template_manager.get_all_templates()
        if not templates:
            messagebox.showinfo("No Templates", "No templates available")
            return

        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Insert Template")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        header = tk.Label(dialog, text="📋 Select Template",
                         font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                         bg=ModernTheme.PRIMARY, fg='white', pady=15)
        header.pack(fill=tk.X)

        # List
        list_frame = tk.Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
        list_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(list_frame, font=(ModernTheme.FONT_FAMILY, 10),
                            height=10, bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT)
        listbox.pack(fill=tk.BOTH, expand=True)

        template_ids = list(templates.keys())
        for template_id in template_ids:
            template = templates[template_id]
            listbox.insert(tk.END, f"{template.name} ({template.category})")

        # Description label
        desc_label = tk.Label(list_frame, text="",
                             font=(ModernTheme.FONT_FAMILY, 9),
                             bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT_SECONDARY,
                             justify=tk.LEFT, wraplength=450)
        desc_label.pack(pady=(10, 0))

        def on_select(event):
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                template = templates[template_ids[idx]]
                desc_label.config(text=template.description)

        listbox.bind('<<ListboxSelect>>', on_select)

        # Buttons
        button_frame = tk.Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=15)
        button_frame.pack(fill=tk.X)

        def insert():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                template = templates[template_ids[idx]]
                actions = template.create_actions()

                # Add to workflow
                for action in actions:
                    action.ui.order = len(self.actions)
                    self.actions.append(action)

                self._refresh_workflow()
                self.update_status(f"Inserted template: {template.name}")
                dialog.destroy()

        ttk.Button(button_frame, text="Insert", command=insert,
                  style='Primary.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def save_as_template(self):
        """Save current workflow as template"""
        if not self.actions:
            messagebox.showwarning("No Actions", "No actions to save as template")
            return

        from src.gui_modern import ModernDialog

        result = ModernDialog.create_input_dialog(self.root, "Save as Template", [
            {'name': 'name', 'label': 'Template Name:', 'type': 'text', 'default': ''},
            {'name': 'category', 'label': 'Category:', 'type': 'text', 'default': 'Custom'},
            {'name': 'description', 'label': 'Description:', 'type': 'text', 'default': ''}
        ])

        if result and result['name']:
            template = self.template_manager.create_template_from_workflow(
                name=result['name'],
                description=result['description'] or 'Custom workflow template',
                category=result['category'] or 'Custom',
                actions=self.actions
            )

            template_id = result['name'].lower().replace(' ', '_')
            self.template_manager.save_custom_template(template_id, template)

            messagebox.showinfo("Success", f"Template '{result['name']}' saved!")
            logging.info(f"Saved template: {result['name']}")

    def browse_templates(self):
        """Browse available templates"""
        templates = self.template_manager.get_all_templates()

        dialog = tk.Toplevel(self.root)
        dialog.title("Template Browser")
        dialog.geometry("600x500")
        dialog.transient(self.root)

        # Header
        header = tk.Label(dialog, text="📚 Template Browser",
                         font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                         bg=ModernTheme.PRIMARY, fg='white', pady=15)
        header.pack(fill=tk.X)

        # Content
        content = tk.Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Categories
        categories = self.template_manager.get_categories()
        for category in categories:
            cat_label = tk.Label(content, text=category,
                                font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                                bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT)
            cat_label.pack(anchor=tk.W, pady=(10, 5))

            cat_templates = self.template_manager.get_templates_by_category(category)
            for template in cat_templates:
                template_frame = tk.Frame(content, bg=ModernTheme.SURFACE,
                                         relief=tk.SOLID, borderwidth=1)
                template_frame.pack(fill=tk.X, pady=2)

                tk.Label(template_frame, text=template.name,
                        font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                        bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT).pack(anchor=tk.W, padx=10, pady=(5, 0))

                tk.Label(template_frame, text=template.description,
                        font=(ModernTheme.FONT_FAMILY, 9),
                        bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_SECONDARY,
                        wraplength=550, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(2, 5))

        ttk.Button(content, text="Close", command=dialog.destroy).pack(pady=(20, 0))

    def add_comment_to_selected(self):
        """Add comment to selected action"""
        if self.selected_action_index is None:
            messagebox.showinfo("No Selection", "Please select an action first")
            return

        from src.workflow_comments import CommentDialog

        existing_comment = None
        if self.comment_manager.has_comment(self.selected_action_index):
            existing_comment = self.comment_manager.get_comment(self.selected_action_index).text

        def on_save(comment_text):
            self.comment_manager.add_comment(self.selected_action_index, comment_text)
            self._refresh_workflow()
            self.update_status(f"Added comment to action #{self.selected_action_index + 1}")
            logging.info(f"Added comment to action {self.selected_action_index}")

        dialog = CommentDialog(self.root, existing_comment, on_save=on_save)
        dialog.show()

    def show_about(self):
        """Show about dialog"""
        about = """Automation Studio - COMPLETE ✨

Visual automation tool with:
✓ Screen capture overlay
✓ Visual canvas with annotations
✓ Beautiful action cards
✓ Keyboard workflow reordering (Ctrl+Up/Down)
✓ Smooth animations & transitions
✓ Keyboard navigation (Up/Down arrows)
✓ Context-aware properties panel
✓ Real-time property editing
✓ Recording mode 🎬
✓ Workflow templates 📋
✓ Action comments 💬
✓ Press Key action (Enter, Tab, etc)
✓ Full backward compatibility

Phase 6 Features - Advanced:
• 📋 Pre-built workflow templates
• 💾 Save custom templates
• 📚 Template browser
• 💬 Action comments/notes
• 🎯 Smart action optimization
• ⚡ Performance enhancements
• 🛡️ Error handling improvements
• 📤 Export/Import workflows

Keyboard Shortcuts:
• Ctrl+Up/Down - Move selected action
• Up/Down - Select action
• Delete - Delete selected action
• Ctrl+D - Duplicate selected action
• Ctrl+M - Add comment to action
• F5 - Play workflow

All Phases Complete! 🎉

Built with Python & Tkinter"""

        messagebox.showinfo("About", about)

    def quit_app(self):
        """Quit application"""
        if messagebox.askyesno("Quit", "Quit Automation Studio?"):
            logging.info("Automation Studio closing")
            self.root.quit()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AutomationStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
