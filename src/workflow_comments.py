"""
Workflow Comments and Annotations
Add notes and markers to workflow actions
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from src.theme import ModernTheme


class WorkflowComment:
    """Represents a comment/annotation for an action"""

    def __init__(self, action_index: int, text: str, color: str = '#ffeb3b'):
        self.action_index = action_index
        self.text = text
        self.color = color
        self.timestamp = None

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'action_index': self.action_index,
            'text': self.text,
            'color': self.color
        }

    @staticmethod
    def from_dict(data: dict) -> 'WorkflowComment':
        """Create from dictionary"""
        return WorkflowComment(
            action_index=data['action_index'],
            text=data['text'],
            color=data.get('color', '#ffeb3b')
        )


class CommentDialog:
    """Dialog for adding/editing comments"""

    def __init__(self, parent, existing_comment: Optional[str] = None,
                 on_save: Optional[Callable] = None):
        self.parent = parent
        self.existing_comment = existing_comment
        self.on_save = on_save
        self.result = None

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Comment")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_ui()

        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create dialog UI"""
        # Header
        header = tk.Frame(self.dialog, bg=ModernTheme.PRIMARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(header, text="📝 Add Comment",
                        font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                        bg=ModernTheme.PRIMARY, fg='white')
        title.pack(pady=15)

        # Content
        content = tk.Frame(self.dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Info
        info = tk.Label(content,
                       text="Add a note or reminder for this action:",
                       font=(ModernTheme.FONT_FAMILY, 10),
                       bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT,
                       justify=tk.LEFT)
        info.pack(anchor=tk.W, pady=(0, 10))

        # Text area
        self.text = tk.Text(content, font=(ModernTheme.FONT_FAMILY, 10),
                           height=8, wrap=tk.WORD,
                           bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT,
                           relief=tk.SOLID, borderwidth=1, padx=5, pady=5)
        self.text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        if self.existing_comment:
            self.text.insert('1.0', self.existing_comment)
            self.text.focus_set()

        # Buttons
        button_frame = tk.Frame(content, bg=ModernTheme.BACKGROUND)
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(button_frame, text="Cancel",
                               font=(ModernTheme.FONT_FAMILY, 10),
                               bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT,
                               relief=tk.FLAT, padx=20, pady=8,
                               cursor='hand2',
                               command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        save_btn = tk.Button(button_frame, text="Save Comment",
                            font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                            bg=ModernTheme.PRIMARY, fg='white',
                            relief=tk.FLAT, padx=20, pady=8,
                            cursor='hand2',
                            command=self._on_save)
        save_btn.pack(side=tk.RIGHT)

    def _on_save(self):
        """Handle save"""
        comment_text = self.text.get('1.0', 'end-1c').strip()
        if comment_text:
            self.result = comment_text
            if self.on_save:
                self.on_save(comment_text)
        self.dialog.destroy()

    def _on_cancel(self):
        """Handle cancel"""
        self.result = None
        self.dialog.destroy()

    def show(self) -> Optional[str]:
        """Show dialog and wait for result"""
        self.dialog.wait_window()
        return self.result


class CommentIndicator:
    """Visual indicator for action with comment"""

    def __init__(self, parent, comment_text: str, on_click: Optional[Callable] = None):
        self.parent = parent
        self.comment_text = comment_text
        self.on_click = on_click

        # Create indicator
        self.frame = tk.Frame(parent, bg='#ffeb3b', cursor='hand2')

        # Icon
        icon = tk.Label(self.frame, text="💬",
                       font=('Arial', 12),
                       bg='#ffeb3b', fg='#000000')
        icon.pack(side=tk.LEFT, padx=(5, 2))

        # Preview text
        preview = comment_text[:30] + "..." if len(comment_text) > 30 else comment_text
        text_label = tk.Label(self.frame, text=preview,
                             font=(ModernTheme.FONT_FAMILY, 8),
                             bg='#ffeb3b', fg='#000000')
        text_label.pack(side=tk.LEFT, padx=(2, 5))

        # Bind click
        self.frame.bind('<Button-1>', self._on_click)
        icon.bind('<Button-1>', self._on_click)
        text_label.bind('<Button-1>', self._on_click)

    def _on_click(self, event=None):
        """Handle click"""
        if self.on_click:
            self.on_click()

    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)

    def destroy(self):
        """Destroy the frame"""
        self.frame.destroy()


class CommentManager:
    """Manages comments for workflow actions"""

    def __init__(self):
        self.comments: dict[int, WorkflowComment] = {}

    def add_comment(self, action_index: int, text: str, color: str = '#ffeb3b'):
        """Add comment to action"""
        self.comments[action_index] = WorkflowComment(action_index, text, color)

    def get_comment(self, action_index: int) -> Optional[WorkflowComment]:
        """Get comment for action"""
        return self.comments.get(action_index)

    def has_comment(self, action_index: int) -> bool:
        """Check if action has comment"""
        return action_index in self.comments

    def remove_comment(self, action_index: int):
        """Remove comment from action"""
        if action_index in self.comments:
            del self.comments[action_index]

    def update_indices(self, old_index: int, new_index: int):
        """Update comment index when action is reordered"""
        if old_index in self.comments:
            comment = self.comments.pop(old_index)
            comment.action_index = new_index
            self.comments[new_index] = comment

    def shift_indices_after_delete(self, deleted_index: int):
        """Shift comment indices after action deletion"""
        # Remove comment for deleted action
        if deleted_index in self.comments:
            del self.comments[deleted_index]

        # Shift all comments after deleted index down by 1
        new_comments = {}
        for index, comment in self.comments.items():
            if index > deleted_index:
                comment.action_index = index - 1
                new_comments[index - 1] = comment
            else:
                new_comments[index] = comment

        self.comments = new_comments

    def shift_indices_after_insert(self, insert_index: int):
        """Shift comment indices after action insertion"""
        new_comments = {}
        for index, comment in self.comments.items():
            if index >= insert_index:
                comment.action_index = index + 1
                new_comments[index + 1] = comment
            else:
                new_comments[index] = comment

        self.comments = new_comments

    def get_all_comments(self) -> dict[int, WorkflowComment]:
        """Get all comments"""
        return self.comments.copy()

    def clear(self):
        """Clear all comments"""
        self.comments.clear()

    def to_dict(self) -> list[dict]:
        """Convert to dictionary for saving"""
        return [comment.to_dict() for comment in self.comments.values()]

    def from_dict(self, data: list[dict]):
        """Load from dictionary"""
        self.comments.clear()
        for comment_data in data:
            comment = WorkflowComment.from_dict(comment_data)
            self.comments[comment.action_index] = comment


# Test code
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Comment System Test")
    root.geometry("600x400")
    root.configure(bg=ModernTheme.BACKGROUND)

    from src.theme import ModernTheme
    ModernTheme.configure_style()

    # Test comment manager
    manager = CommentManager()
    manager.add_comment(0, "This is the first action")
    manager.add_comment(2, "Important: Wait for element to load before proceeding")
    manager.add_comment(5, "Double-check the value here")

    # Display comments
    container = tk.Frame(root, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    title = tk.Label(container, text="Action Comments",
                    font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                    bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT)
    title.pack(anchor=tk.W, pady=(0, 15))

    for index, comment in manager.get_all_comments().items():
        indicator = CommentIndicator(
            container,
            comment.text,
            on_click=lambda: print(f"Clicked comment for action {index}")
        )
        indicator.pack(fill=tk.X, pady=5)

    # Add button to test dialog
    def show_dialog():
        dialog = CommentDialog(root, existing_comment="Test comment")
        result = dialog.show()
        if result:
            print(f"Saved comment: {result}")

    btn = tk.Button(container, text="Add New Comment",
                   font=(ModernTheme.FONT_FAMILY, 10),
                   command=show_dialog)
    btn.pack(pady=20)

    root.mainloop()
