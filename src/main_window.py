"""
Main window for Automation Studio.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import logging

# Encoding setup
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# Import components
from src.theme import ModernTheme
from src.studio_layout import StudioLayout
from src.action_schema import EnhancedAction
from src.screenshot_manager import ScreenshotManager
from src.visual_canvas import VisualCanvas, ActionAnnotation
from src.action_card import ActionCard
from src.variable_manager import VariableManagerDialog
from src.template_manager import TemplateManager
from src.comment_manager import CommentManager
from src.ui_factory import create_menu, create_toolbar
from src.action_handlers import ActionHandlers
from src.workflow_manager import WorkflowManager
from src.playback_manager import PlaybackManager
from src.recording_manager import RecordingManager
from src.workflow_actions import WorkflowActions

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
    """Main Automation Studio application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Automation Studio")
        self.root.geometry("1200x700")

        # Apply modern theme
        ModernTheme.configure_style()
        self.root.configure(bg=ModernTheme.BACKGROUND)

        # Initialize state
        self.actions = []  # List of EnhancedAction objects
        self.selected_action_indices = []
        self.selected_action_index = None  # Index of the last selected action (for single selection)
        self.action_cards = []  # List of ActionCard widgets
        self.batch_data = []
        self.batch_columns = []
        self.is_dirty = False
        self.current_filepath = None

        # Initialize managers
        self.screenshot_manager = ScreenshotManager()
        self.template_manager = TemplateManager(self)
        self.comment_manager = CommentManager(self)
        self.action_handlers = ActionHandlers(self)
        self.workflow_manager = WorkflowManager(self)
        self.playback_manager = PlaybackManager(self)
        self.recording_manager = RecordingManager(self)
        self.workflow_actions = WorkflowActions(self)

        # Create studio layout first
        self.studio_callbacks = {
            'add_step': self.action_handlers.show_add_step_menu,
        }
        self.studio = StudioLayout(self.root, callbacks=self.studio_callbacks)

        # Initialize visual canvas with callbacks
        self.visual_canvas = VisualCanvas(
            self.studio.canvas_panel.canvas,
            on_annotation_click=self.workflow_actions.select_action,
            on_annotation_double_click=self._edit_action_from_canvas,
            on_zoom_change=self._update_zoom_label
        )

        # Create menu and toolbar
        create_menu(self)
        create_toolbar(self)

        # Connect zoom buttons
        self._connect_canvas_controls()

        # Set minimum window size
        self.root.minsize(1200, 700)

        # Welcome message
        self.update_status("Welcome to Automation Studio! Click '+ Add Step' to begin.")

        logging.info("Automation Studio initialized")

    def _connect_canvas_controls(self):
        """Connect canvas zoom controls to visual canvas"""
        for child in self.studio.canvas_panel.winfo_children():
            if isinstance(child, ttk.Frame):
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

    def _refresh_workflow(self):
        """Refresh workflow panel with current actions"""
        self.studio.workflow_panel.clear_actions()
        self.action_cards.clear()

        for i, action in enumerate(self.actions):
            comment_text = None
            if self.comment_manager.core_manager.has_comment(i):
                comment_text = self.comment_manager.core_manager.get_comment(i).text

            card = ActionCard(
                self.studio.workflow_panel.actions_frame,
                action, i,
                on_select=lambda index, event: self.workflow_actions.select_action(index, event),
                on_toggle=self.workflow_actions.toggle_action,
                on_delete=self.workflow_actions.delete_action,
                on_duplicate=self.workflow_actions.duplicate_action,
                on_reorder=self.workflow_actions.reorder_action,
                on_enable_selected=self.workflow_actions.enable_selected,
                on_disable_selected=self.workflow_actions.disable_selected,
                comment=comment_text
            )
            card.pack(fill=tk.X, pady=5)
            self.action_cards.append(card)

            self.studio.workflow_panel.bind_mousewheel_to_widget(card)

        self.studio.workflow_panel.update_counter(len(self.actions))

    def _on_property_change(self, index: int, property_name: str, value):
        """Handle property change from properties panel"""
        if 0 <= index < len(self.actions):
            action = self.actions[index]

            if property_name == 'enabled':
                action.enabled = value
                if index < len(self.action_cards):
                    self.action_cards[index].update_enabled_state(value)
            else:
                action.params[property_name] = value

            if property_name in ['x', 'y'] and action.has_visual_data():
                if 'x' in action.visual.capture_region:
                    action.visual.capture_region['x'] = action.params.get('x', 0)
                if 'y' in action.visual.capture_region:
                    action.visual.capture_region['y'] = action.params.get('y', 0)

                self.visual_canvas.clear_annotations()
                for i, act in enumerate(self.actions):
                    if act.has_visual_data():
                        self._add_canvas_annotation(act, i)

            if property_name == 'description':
                self._refresh_workflow()

            self.update_status(f"Updated {property_name} for action #{index + 1}")
            self.is_dirty = True

    def _recapture_position(self, index: int):
        """Recapture position for an action"""
        if 0 <= index < len(self.actions):
            from src.capture_overlay import CaptureOverlay, CaptureMode

            # Show overlay and capture position
            def on_capture_complete(result):
                if result.get('success'):
                    self._on_position_captured(index, result)

            overlay = CaptureOverlay(self.root, mode=CaptureMode.POINT, callback=on_capture_complete)
            overlay.show()

    def _on_position_captured(self, index: int, region: dict):
        """Handle newly captured position"""
        if 0 <= index < len(self.actions):
            action = self.actions[index]

            # Update action coordinates
            x, y = region['x'], region['y']

            # CRITICAL: Directly update on the action in the list
            self.actions[index].params['x'] = x
            self.actions[index].params['y'] = y

            # If the action has a description that was likely based on coordinates,
            # clear it so that get_summary() will show the new coordinates
            if self.actions[index].description and ('at (' in self.actions[index].description or 'Click at' in self.actions[index].description or 'Set value at' in self.actions[index].description):
                self.actions[index].description = ''

            logging.info(f"Position updated: action #{index + 1} -> ({x}, {y})")
            logging.info(f"Action params (direct from list): x={self.actions[index].params.get('x')}, y={self.actions[index].params.get('y')}")
            logging.info(f"Action ID: {id(action)} vs List ID: {id(self.actions[index])}")
            logging.info(f"Params ID: {id(action.params)} vs List Params ID: {id(self.actions[index].params)}")

            # Update visual capture region if it exists
            if action.has_visual_data() and action.visual.capture_region:
                action.visual.capture_region['x'] = x
                action.visual.capture_region['y'] = y

            # Save the current selection state before refresh
            previously_selected = self.selected_action_indices.copy()

            # Refresh workflow panel to show updated coordinates
            self._refresh_workflow()

            logging.info(f"Action summary from list AFTER refresh: {self.actions[index].get_summary()}")
            logging.info(f"Action summary from variable AFTER refresh: {action.get_summary()}")

            # After refresh, restore the selection state
            self.selected_action_indices = previously_selected
            
            # Update single selection index
            if len(self.selected_action_indices) == 1:
                self.selected_action_index = self.selected_action_indices[0]
            elif len(self.selected_action_indices) == 0:
                self.selected_action_index = None
            else:
                # When multiple are selected, keep the last selected as the single index
                self.selected_action_index = self.selected_action_indices[-1]
            
            # Update UI selection state
            for i, card in enumerate(self.action_cards):
                if i in self.selected_action_indices:
                    card.select()
                else:
                    card.deselect()

            # Refresh visual canvas
            self.visual_canvas.clear_annotations()
            for i, act in enumerate(self.actions):
                if act.has_visual_data():
                    self._add_canvas_annotation(act, i)

            # Refresh property panel
            if index in self.selected_action_indices:
                # Get the updated action after the list has been refreshed
                updated_action = self.actions[index] if index < len(self.actions) else action
                self.studio.properties_panel.show_action_properties(
                    updated_action,
                    on_change=lambda prop, val: self._on_property_change(index, prop, val),
                    batch_columns=self.batch_columns,
                    on_recapture=lambda: self._recapture_position(index)
                )

            self.update_status(f"Updated position for action #{index + 1} to ({x}, {y})")
            self.is_dirty = True

    def _edit_action_from_canvas(self, index: int):
        """Edit action by double-clicking canvas annotation"""
        if 0 <= index < len(self.actions):
            action = self.actions[index]
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

            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def open_variable_manager(self):
        """Open the variable manager dialog."""
        def on_save(data, columns):
            self.batch_data = data
            self.batch_columns = columns
            self.update_status(f"Saved {len(data)} batch rows.")

        dialog = VariableManagerDialog(self.root, self.batch_data, self.batch_columns, on_save=on_save)
        dialog.wait_window()

    def show_about(self):
        """Show about dialog"""
        about = """                    Automation Studio ✨

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

        Keyboard Shortcuts:
        • Ctrl+Up/Down - Move selected action
        • Up/Down - Select action
        • Delete - Delete selected action
        • Ctrl+D - Duplicate selected action
        • Ctrl+M - Add comment to action
        • F5 - Play workflow

        Built with Python & Tkinter"""

        messagebox.showinfo("About", about)

    def quit_app(self):
        """Quit application"""
        if messagebox.askyesno("Quit", "Quit Automation Studio?"):
            logging.info("Automation Studio closing")
            self.root.quit()

    # Delegate methods to managers
    def load_workflow(self):
        self.workflow_manager.load_workflow()

    def save_workflow(self):
        self.workflow_manager.save_workflow()

    def export_classic(self):
        self.workflow_manager.export_classic()

    def play_workflow(self):
        self.playback_manager.play_workflow()

    def start_recording(self):
        self.recording_manager.start_recording()

    def stop_recording(self):
        self.recording_manager.stop_recording()

    def pause_recording(self):
        self.recording_manager.pause_recording()

    def resume_recording(self):
        self.recording_manager.resume_recording()

    def insert_template(self):
        self.template_manager.insert_template()

    def save_as_template(self):
        self.template_manager.save_as_template()

    def browse_templates(self):
        self.template_manager.browse_templates()

    def add_comment_to_selected(self):
        self.comment_manager.add_comment_to_selected()

    def select_action(self, index):
        self.workflow_actions.select_action(index)

    def toggle_action(self, index):
        self.workflow_actions.toggle_action(index)

    def delete_action(self, index):
        self.workflow_actions.delete_action(index)

    def delete_selected(self):
        self.workflow_actions.delete_selected()

    def duplicate_action(self, index):
        self.workflow_actions.duplicate_action(index)

    def duplicate_selected(self): 
        self.workflow_actions.duplicate_selected()

    def reorder_action(self, from_index, to_index):
        self.workflow_actions.reorder_action(from_index, to_index)

    def _navigate_up(self):
        self.workflow_actions._navigate_up()

    def _navigate_down(self):
        self.workflow_actions._navigate_down()

    def _move_action_up(self):
        self.workflow_actions._move_action_up()

    def _move_action_down(self):
        self.workflow_actions._move_action_down()
