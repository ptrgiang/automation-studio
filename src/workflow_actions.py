"""
Handles actions related to the workflow panel.
"""
from tkinter import messagebox

class WorkflowActions:
    def __init__(self, app):
        self.app = app

    def select_action(self, index: int, event=None):
        """Select an action, with support for multi-selection."""
        # Multi-selection logic
        if event and (event.state & 0x0004):  # Control key pressed
            if index in self.app.selected_action_indices:
                self.app.selected_action_indices.remove(index)
            else:
                self.app.selected_action_indices.append(index)
        elif event and (event.state & 0x0001):  # Shift key pressed
            if self.app.selected_action_indices:
                last_selected = self.app.selected_action_indices[-1]
                start = min(last_selected, index)
                end = max(last_selected, index)
                self.app.selected_action_indices = list(range(start, end + 1))
            else:
                self.app.selected_action_indices = [index]
        else:
            self.app.selected_action_indices = [index]

        # Update UI
        for i, card in enumerate(self.app.action_cards):
            if i in self.app.selected_action_indices:
                card.select()
            else:
                card.deselect()

        # Update single selection index (for operations that work on single actions)
        if len(self.app.selected_action_indices) == 1:
            self.app.selected_action_index = self.app.selected_action_indices[0]
        elif len(self.app.selected_action_indices) == 0:
            self.app.selected_action_index = None
        else:
            # When multiple are selected, keep the last selected as the single index
            self.app.selected_action_index = self.app.selected_action_indices[-1]

        # Update property panel for the last selected action
        if self.app.selected_action_indices:
            last_selected_index = self.app.selected_action_indices[-1]
            if 0 <= last_selected_index < len(self.app.actions):
                action = self.app.actions[last_selected_index]
                self.app.studio.properties_panel.show_action_properties(
                    action,
                    on_change=lambda prop, val: self.app._on_property_change(last_selected_index, prop, val),
                    batch_columns=self.app.batch_columns,
                    on_recapture=lambda: self.app._recapture_position(last_selected_index)
                )

    def delete_selected(self):
        """Delete all selected actions."""
        if not self.app.selected_action_indices:
            return

        if messagebox.askyesno("Delete Actions", f"Delete {len(self.app.selected_action_indices)} selected actions?"):
            # Sort indices in reverse order to avoid index shifting issues
            for index in sorted(self.app.selected_action_indices, reverse=True):
                self.app.visual_canvas.remove_annotation(index)
                self.app.actions.pop(index)
                self.app.comment_manager.core_manager.shift_indices_after_delete(index)
            
            self.app.selected_action_indices.clear()
            self.app._refresh_workflow()
            self.app.update_status(f"Deleted selected actions")
            self.app.is_dirty = True

    def duplicate_action(self, index: int):
        """Duplicate an action"""
        if 0 <= index < len(self.app.actions):
            import copy
            action_copy = copy.deepcopy(self.app.actions[index])
            action_copy.ui.order = len(self.app.actions)
            self.app.actions.insert(index + 1, action_copy)
            self.app._refresh_workflow()
            self.app.update_status(f"Duplicated action #{index + 1}")
            self.app.is_dirty = True

    def duplicate_selected(self):
        """Duplicate selected action"""
        if self.app.selected_action_index is not None:
            self.duplicate_action(self.app.selected_action_index)

    def reorder_action(self, from_index: int, to_index: int):
        """Reorder action by drag-and-drop"""
        if from_index == to_index:
            return

        if 0 <= from_index < len(self.app.actions) and 0 <= to_index < len(self.app.actions):
            action = self.app.actions.pop(from_index)
            self.app.actions.insert(to_index, action)

            if from_index < to_index:
                for i in range(from_index + 1, to_index + 1):
                    if self.app.comment_manager.core_manager.has_comment(i):
                        comment = self.app.comment_manager.core_manager.comments.pop(i)
                        comment.action_index = i - 1
                        self.app.comment_manager.core_manager.comments[i - 1] = comment
                if self.app.comment_manager.core_manager.has_comment(from_index):
                    comment = self.app.comment_manager.core_manager.comments.pop(from_index)
                    comment.action_index = to_index
                    self.app.comment_manager.core_manager.comments[to_index] = comment
            else:
                for i in range(from_index - 1, to_index - 1, -1):
                    if self.app.comment_manager.core_manager.has_comment(i):
                        comment = self.app.comment_manager.core_manager.comments.pop(i)
                        comment.action_index = i + 1
                        self.app.comment_manager.core_manager.comments[i + 1] = comment
                if self.app.comment_manager.core_manager.has_comment(from_index):
                    comment = self.app.comment_manager.core_manager.comments.pop(from_index)
                    comment.action_index = to_index
                    self.app.comment_manager.core_manager.comments[to_index] = comment

            self.app._refresh_workflow()

            self.app.visual_canvas.clear_annotations()
            for i, act in enumerate(self.app.actions):
                if act.has_visual_data():
                    self.app._add_canvas_annotation(act, i)

            self.select_action(to_index)

            self.app.update_status(f"Moved action from #{from_index + 1} to #{to_index + 1}")
            self.app.is_dirty = True

    def _navigate_up(self):
        """Navigate to previous action"""
        if self.app.selected_action_index is None:
            if self.app.actions:
                self.select_action(0)
        elif self.app.selected_action_index > 0:
            self.select_action(self.app.selected_action_index - 1)

    def _navigate_down(self):
        """Navigate to next action"""
        if self.app.selected_action_index is None:
            if self.app.actions:
                self.select_action(0)
        elif self.app.selected_action_index < len(self.app.actions) - 1:
            self.select_action(self.app.selected_action_index + 1)

    def _move_action_up(self):
        """Move selected action up in list"""
        if self.app.selected_action_index is not None and self.app.selected_action_index > 0:
            self.reorder_action(self.app.selected_action_index, self.app.selected_action_index - 1)

    def _move_action_down(self):
        """Move selected action down in list"""
        if self.app.selected_action_index is not None and self.app.selected_action_index < len(self.app.actions) - 1:
            self.reorder_action(self.app.selected_action_index, self.app.selected_action_index + 1)

    def enable_selected(self):
        """Enable all selected actions."""
        if not self.app.selected_action_indices:
            return
        for index in self.app.selected_action_indices:
            if 0 <= index < len(self.app.actions):
                self.app.actions[index].enabled = True
        self.app._refresh_workflow()

    def disable_selected(self):
        """Disable all selected actions."""
        if not self.app.selected_action_indices:
            return
        for index in self.app.selected_action_indices:
            if 0 <= index < len(self.app.actions):
                self.app.actions[index].enabled = False
        self.app._refresh_workflow()

    def toggle_action(self, index: int):
        """Toggle enabled/disabled state of a single action."""
        if 0 <= index < len(self.app.actions):
            self.app.actions[index].enabled = not self.app.actions[index].enabled
            self.app._refresh_workflow()
            self.app.update_status(f"Toggled action #{index + 1}")
            self.app.is_dirty = True

    def delete_action(self, index: int):
        """Delete a single action."""
        if 0 <= index < len(self.app.actions):
            if messagebox.askyesno("Delete Action", f"Delete action #{index + 1}?"):
                self.app.visual_canvas.remove_annotation(index)
                self.app.actions.pop(index)
                self.app.comment_manager.core_manager.shift_indices_after_delete(index)
                self.app.selected_action_indices.clear()
                self.app._refresh_workflow()
                self.app.update_status(f"Deleted action #{index + 1}")
                self.app.is_dirty = True
