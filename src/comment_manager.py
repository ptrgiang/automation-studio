"""
Comment manager for handling action comments.
"""
from tkinter import messagebox
from src.workflow_comments import CommentDialog, CommentManager as CoreCommentManager

class CommentManager:
    def __init__(self, app):
        self.app = app
        self.core_manager = CoreCommentManager()

    def add_comment_to_selected(self):
        """Add comment to selected action"""
        if self.app.selected_action_index is None:
            messagebox.showinfo("No Selection", "Please select an action first")
            return

        existing_comment = None
        if self.core_manager.has_comment(self.app.selected_action_index):
            existing_comment = self.core_manager.get_comment(self.app.selected_action_index).text

        def on_save(comment_text):
            self.core_manager.add_comment(self.app.selected_action_index, comment_text)
            self.app._refresh_workflow()
            self.app.update_status(f"Added comment to action #{self.app.selected_action_index + 1}")

        dialog = CommentDialog(self.app.root, existing_comment, on_save=on_save)
        dialog.show()
