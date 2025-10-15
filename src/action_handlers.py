"""
Action handlers for creating and adding new actions to the workflow.
"""
import tkinter as tk
from tkinter import messagebox
from src.action_schema import EnhancedAction
from src.capture_overlay import CaptureOverlay, CaptureMode, CaptureConfirmDialog
from src.gui_modern import ModernDialog

class ActionHandlers:
    def __init__(self, app):
        self.app = app

    def show_add_step_menu(self):
        """Show menu to add a new step"""
        menu = tk.Menu(self.app.root, tearoff=0)

        # Visual actions (require capture)
        menu.add_command(label="Click at specific position", command=lambda: self.add_action_with_capture('click'))
        menu.add_command(label="Click at current position", command=lambda: self.add_click_current_pos_action())
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
            menu.tk_popup(self.app.root.winfo_pointerx(), self.app.root.winfo_pointery())
        finally:
            menu.grab_release()

    def add_action_with_capture(self, action_type: str):
        """Add action that requires screen capture"""
        self.app.update_status(f"Prepare to capture target for {action_type}...")

        # Minimize window before capture
        self.app.root.iconify()

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
                self.app.root.deiconify()
                self.app.root.lift()
                self.app.root.focus_force()

                if not result.get('success'):
                    self.app.update_status("Capture cancelled")
                    return

                # Show confirmation dialog
                def on_confirm(capture_data):
                    self._create_action_from_capture(action_type, capture_data)

                def on_recapture():
                    # Retry capture
                    self.add_action_with_capture(action_type)

                def on_cancel():
                    self.app.update_status("Action cancelled")

                confirm_dialog = CaptureConfirmDialog(
                    self.app.root, result,
                    on_confirm=on_confirm,
                    on_recapture=on_recapture,
                    on_cancel=on_cancel
                )
                confirm_dialog.show()

            overlay = CaptureOverlay(self.app.root, mode=mode, callback=on_capture_complete)
            overlay.show()

        # Delay to allow window to minimize
        self.app.root.after(300, start_capture)

    def _create_action_from_capture(self, action_type: str, capture_data):
        """Create action from capture data"""
        x = capture_data['x']
        y = capture_data['y']
        screenshot = capture_data['screenshot']
        mode = capture_data['mode']

        # Save screenshot and create thumbnail
        if mode == CaptureMode.POINT:
            full_path, region_path, region_dict = self.app.screenshot_manager.capture_point_with_context(
                x, y, context_size=100
            )
        else:
            full_path = self.app.screenshot_manager._generate_filename()
            full_filepath = self.app.screenshot_manager.screenshots_dir / full_path
            screenshot.save(str(full_filepath), 'PNG')

            region_dict = {
                'x': x,
                'y': y,
                'width': capture_data['width'],
                'height': capture_data['height']
            }

            # Extract region
            region = screenshot.crop((x, y, x + region_dict['width'], y + region_dict['height']))
            region_filename = self.app.screenshot_manager._generate_filename("region")
            region_path = str(self.app.screenshot_manager.regions_dir / region_filename)
            region.save(region_path, 'PNG')
            full_path = str(full_filepath)

        # Create thumbnail
        thumb_path = self.app.screenshot_manager.create_thumbnail(region_path)

        # Create action with visual metadata
        action_params = {
            'x': x,
            'y': y,
            'description': f"{action_type.title()} at ({x}, {y})",
        }

        # Get additional parameters for set_value
        if action_type == 'set_value':
            result = ModernDialog.create_input_dialog(self.app.root, "Set Value", [
                {'name': 'value', 'label': 'Value to set:', 'type': 'text', 'default': ''},
                {'name': 'method', 'label': 'Clear method:', 'type': 'choice',
                 'choices': ['ctrl_a', 'backspace', 'triple_click'], 'default': 'ctrl_a'}
            ])

            if result:
                action_params['value'] = result['value']
                action_params['method'] = result['method']
            else:
                # User cancelled - don't create action
                self.app.update_status("Action cancelled")
                return

        if action_type == 'find_image':
            action_params['image_path'] = region_path
            action_params['image_name'] = f"image_{len(self.app.actions)}"
            action_params['confidence'] = 0.8

        if action_type == 'wait_for_image':
            action_params['wait_type'] = 'image'
            action_params['image_path'] = region_path
            action_params['image_name'] = f"image_{len(self.app.actions)}"
            action_params['confidence'] = 0.8
            action_params['timeout'] = 30
            action_type = 'wait'

        action = EnhancedAction(action_type, **action_params)
        action.ui.order = len(self.app.actions)

        # Add visual metadata
        action.visual.screenshot_path = full_path
        action.visual.capture_region = region_dict
        action.visual.thumbnail_path = thumb_path
        action.visual.screen_resolution = self.app.screenshot_manager.get_screen_resolution()

        # Add action
        self.app.actions.append(action)
        self.app._refresh_workflow()

        # Load screenshot on canvas if first action
        if len(self.app.actions) == 1:
            self.app.visual_canvas.load_screenshot(screenshot)

        # Add annotation to canvas
        self.app._add_canvas_annotation(action, len(self.app.actions) - 1)

        self.app.update_status(f"Added {action_type} action with visual capture")
        self.app.is_dirty = True

    def add_text_action(self, action_type: str):
        """Add type action"""
        result = ModernDialog.create_input_dialog(self.app.root, "Type Text", [
            {'name': 'text', 'label': 'Text to type:', 'type': 'text', 'default': ''},
            {'name': 'description', 'label': 'Description:', 'type': 'text', 'default': ''}
        ])

        if result and result['text']:
            action = EnhancedAction(action_type,
                                   text=result['text'],
                                   description=result['description'] or f"Type: {result['text'][:30]}")
            action.ui.order = len(self.app.actions)
            self.app.actions.append(action)
            self.app._refresh_workflow()
            self.app.update_status(f"Added {action_type} action")
            self.app.is_dirty = True

    def add_key_press_action(self):
        """Add key press action (Enter, Tab, Escape, etc)"""
        # Create custom dialog with dropdown instead of radio buttons
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Press Key")
        dialog.geometry("400x250")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=ModernTheme.BACKGROUND)

        # Center dialog
        dialog.update_idletasks()
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 200
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 125
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
            action.ui.order = len(self.app.actions)
            self.app.actions.append(action)
            self.app._refresh_workflow()
            self.app.update_status(f"Added key press action: {key}")
            self.app.is_dirty = True

    def add_wait_action(self):
        """Add wait action with choice of duration or image"""
        result = ModernDialog.create_input_dialog(self.app.root, "Wait Action", [
            {'name': 'wait_type', 'label': 'Wait for:', 'type': 'choice',
             'choices': ['Duration', 'Image'], 'default': 'Duration'}
        ])

        if not result:
            return

        wait_type = result['wait_type'].lower()

        if wait_type == 'duration':
            duration_result = ModernDialog.create_input_dialog(self.app.root, "Wait for Duration", [
                {'name': 'duration', 'label': 'Duration (seconds):', 'type': 'number', 'default': '1.0'}
            ])
            if duration_result:
                try:
                    duration = float(duration_result['duration'])
                    action = EnhancedAction('wait',
                                           wait_type='duration',
                                           duration=duration,
                                           description=f"Wait {duration}s")
                    action.ui.order = len(self.app.actions)
                    self.app.actions.append(action)
                    self.app._refresh_workflow()
                    self.app.update_status("Added wait action")
                    self.app.is_dirty = True
                except ValueError:
                    messagebox.showerror("Error", "Invalid duration")
        
        elif wait_type == 'image':
            self.add_action_with_capture('wait_for_image')

    def add_scroll_action(self):
        """Add scroll action"""
        result = ModernDialog.create_input_dialog(self.app.root, "Scroll", [
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
                action.ui.order = len(self.app.actions)
                self.app.actions.append(action)
                self.app._refresh_workflow()
                self.app.update_status("Added scroll action")
                self.app.is_dirty = True
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")

    def add_simple_action(self, action_type: str):
        """Add simple action without parameters"""
        action = EnhancedAction(action_type, method='ctrl_a',
                               description=f"{action_type.title()} field")
        action.ui.order = len(self.app.actions)
        self.app.actions.append(action)
        self.app.update_status(f"Added {action_type} action")
        self.app.is_dirty = True

    def add_click_current_pos_action(self):
        """Add a click action that uses the current mouse position at execution time."""
        action = EnhancedAction(
            'click',
            use_current_position=True,
            description="Click at current mouse position"
        )
        action.ui.order = len(self.app.actions)
        self.app.actions.append(action)
        self.app._refresh_workflow()
        self.app.update_status("Added 'Click at current position' action")
        self.app.is_dirty = True
