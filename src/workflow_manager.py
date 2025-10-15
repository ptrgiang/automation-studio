"""
Workflow manager for loading, saving, and exporting workflows.
"""
from tkinter import filedialog, messagebox
import json
from datetime import datetime
from src.action_schema import EnhancedAction, ActionSchemaManager

class WorkflowManager:
    def __init__(self, app):
        self.app = app

    def load_workflow(self):
        """Load workflow from file"""
        filepath = filedialog.askopenfilename(
            title="Open Workflow",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                actions_data = data.get('actions', [])
                self.app.actions = [EnhancedAction.from_dict(a) for a in actions_data]
                self.app.batch_columns = data.get('batch_columns', [])
                self.app.batch_data = data.get('batch_data', [])
                # For backward compatibility with old format
                if not self.app.batch_data and 'batch_variables' in data:
                    self.app.batch_columns = ['variable']
                    self.app.batch_data = [{'variable': var} for var in data['batch_variables']]

                self.app._refresh_workflow()

                # Load comments if present
                if 'comments' in data:
                    self.app.comment_manager.core_manager.from_dict(data['comments'])

                # Load first screenshot if available
                for action in self.app.actions:
                    if action.has_visual_data() and action.visual.screenshot_path:
                        try:
                            from PIL import Image
                            screenshot = Image.open(action.visual.screenshot_path)
                            self.app.visual_canvas.load_screenshot(screenshot)

                            # Add all annotations
                            for i, act in enumerate(self.app.actions):
                                if act.has_visual_data():
                                    self.app._add_canvas_annotation(act, i)
                            break
                        except:
                            pass

                self.app.update_status(f"Loaded {len(self.app.actions)} actions")
                messagebox.showinfo("Success", f"Loaded {len(self.app.actions)} actions")
                self.app.current_filepath = filepath
                self.app.is_dirty = False

            except Exception as e:
                self.app.update_status(f"Error loading: {str(e)}")
                messagebox.showerror("Error", f"Failed to load:\n{str(e)}")

    def save_workflow(self):
        """Save workflow to file, using current path if available."""
        if not self.app.actions:
            messagebox.showwarning("No Actions", "No actions to save")
            return

        filepath = self.app.current_filepath
        if not filepath:
            filepath = filedialog.asksaveasfilename(
                title="Save Workflow",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )

        if filepath:
            try:
                data = {
                    'version': '2.1',
                    'created': datetime.now().isoformat(),
                    'total_actions': len(self.app.actions),
                    'actions': [a.to_dict() for a in self.app.actions],
                    'comments': self.app.comment_manager.core_manager.to_dict(),
                    'batch_columns': self.app.batch_columns,
                    'batch_data': self.app.batch_data
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                self.app.current_filepath = filepath
                self.app.is_dirty = False
                self.app.update_status(f"Saved {len(self.app.actions)} actions to {filepath}")
                messagebox.showinfo("Success", "Workflow saved")

            except Exception as e:
                self.app.update_status(f"Error saving: {str(e)}")
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")

    def export_classic(self):
        """Export to classic format"""
        if not self.app.actions:
            messagebox.showwarning("No Actions", "No actions to export")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export to Classic Format",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if filepath:
            try:
                classic_actions = ActionSchemaManager.export_simulation(
                    self.app.actions, include_visual=False
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
                self.app.update_status(f"Error exporting: {str(e)}")
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def new_workflow(self):
        """Creates a new, empty workflow."""
        if self.app.is_dirty:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them before creating a new workflow?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                self.save_workflow()

        self.app.actions.clear()
        self.app.action_cards.clear()
        self.app.visual_canvas.clear_annotations()
        self.app.visual_canvas.load_screenshot(None)
        self.app.comment_manager.core_manager.comments.clear()
        self.app._refresh_workflow()
        self.app.update_status("New workflow created")
        self.app.is_dirty = False
        self.app.current_filepath = None
