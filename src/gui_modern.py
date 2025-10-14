"""
Modern professional GUI components for Amazon Simulator
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Callable, Optional
from src.theme import ModernTheme, Icons


class ModernGUIBuilder:
    """Builds modern professional GUI components"""

    @staticmethod
    def create_toolbar(parent, callbacks: Dict[str, Callable]) -> ttk.Frame:
        """
        Create modern toolbar with common actions

        Args:
            parent: Parent widget
            callbacks: Dictionary of button callbacks

        Returns:
            Toolbar frame widget
        """
        toolbar = ttk.Frame(parent, style='Card.TFrame', padding="5")

        # File operations
        ttk.Button(toolbar, text=f"{Icons.FOLDER} Open",
                  command=callbacks.get('load'),
                  style='Outline.TButton').pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text=f"{Icons.SAVE} Save",
                  command=callbacks.get('save'),
                  style='Outline.TButton').pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Playback
        ttk.Button(toolbar, text=f"{Icons.PLAY} Play",
                  command=callbacks.get('play_single'),
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text=f"{Icons.PLAY} Batch",
                  command=callbacks.get('play_batch'),
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Help
        ttk.Button(toolbar, text=f"{Icons.INFO} Help",
                  command=callbacks.get('help'),
                  style='Outline.TButton').pack(side=tk.RIGHT, padx=2)

        return toolbar

    @staticmethod
    def create_recording_panel(parent, callbacks: Dict[str, Callable]) -> ttk.Frame:
        """
        Create modern recording panel with categorized actions

        Args:
            parent: Parent widget
            callbacks: Dictionary of button callbacks

        Returns:
            Recording panel frame
        """
        panel = ttk.LabelFrame(parent, text="Recording Actions", padding="15")
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.columnconfigure(2, weight=1)

        # Row 0 - Mouse actions
        ttk.Label(panel, text="Mouse Actions",
                 style='Heading.TLabel').grid(row=0, column=0, columnspan=3,
                                             sticky=tk.W, pady=(0, 5))

        ttk.Button(panel, text=f"{Icons.CLICK} Click",
                  command=callbacks.get('click'),
                  style='Primary.TButton').grid(
            row=1, column=0, padx=3, pady=3, sticky=(tk.W, tk.E))

        ttk.Button(panel, text=f"{Icons.MOUSE} Move Mouse",
                  command=callbacks.get('move_mouse'),
                  style='Primary.TButton').grid(
            row=1, column=1, padx=3, pady=3, sticky=(tk.W, tk.E))

        ttk.Button(panel, text=f"{Icons.SCROLL} Scroll",
                  command=callbacks.get('scroll'),
                  style='Primary.TButton').grid(
            row=1, column=2, padx=3, pady=3, sticky=(tk.W, tk.E))

        # Row 2 - Keyboard actions
        ttk.Label(panel, text="Keyboard Actions",
                 style='Heading.TLabel').grid(row=2, column=0, columnspan=3,
                                             sticky=tk.W, pady=(10, 5))

        ttk.Button(panel, text=f"{Icons.KEYBOARD} Type",
                  command=callbacks.get('type'),
                  style='Primary.TButton').grid(
            row=3, column=0, padx=3, pady=3, sticky=(tk.W, tk.E))

        ttk.Button(panel, text=f"{Icons.EDIT} Set Value",
                  command=callbacks.get('set_value'),
                  style='Primary.TButton').grid(
            row=3, column=1, padx=3, pady=3, sticky=(tk.W, tk.E))

        ttk.Button(panel, text=f"{Icons.DELETE} Delete",
                  command=callbacks.get('delete'),
                  style='Primary.TButton').grid(
            row=3, column=2, padx=3, pady=3, sticky=(tk.W, tk.E))

        # Row 4 - Advanced actions
        ttk.Label(panel, text="Advanced Actions",
                 style='Heading.TLabel').grid(row=4, column=0, columnspan=3,
                                             sticky=tk.W, pady=(10, 5))

        ttk.Button(panel, text=f"{Icons.IMAGE} Find Image",
                  command=callbacks.get('find_image'),
                  style='Primary.TButton').grid(
            row=5, column=0, padx=3, pady=3, sticky=(tk.W, tk.E))

        ttk.Button(panel, text=f"{Icons.TIME} Wait",
                  command=callbacks.get('wait'),
                  style='Primary.TButton').grid(
            row=5, column=1, padx=3, pady=3, sticky=(tk.W, tk.E))

        return panel

    @staticmethod
    def create_actions_treeview(parent, callbacks: Dict[str, Callable]) -> tuple:
        """
        Create professional actions list with treeview

        Args:
            parent: Parent widget
            callbacks: Dictionary of button callbacks

        Returns:
            Tuple of (frame, treeview_widget)
        """
        frame = ttk.LabelFrame(parent, text="Action Sequence", padding="15")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Create treeview
        columns = ('status', 'type', 'details', 'description')
        tree = ttk.Treeview(frame, columns=columns, show='headings',
                           selectmode='extended', height=12)

        # Configure columns
        tree.heading('status', text='')
        tree.heading('type', text='Action')
        tree.heading('details', text='Details')
        tree.heading('description', text='Description')

        tree.column('status', width=40, anchor=tk.CENTER)
        tree.column('type', width=100, anchor=tk.W)
        tree.column('details', width=200, anchor=tk.W)
        tree.column('description', width=150, anchor=tk.W)

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Button panel
        btn_panel = ttk.Frame(frame)
        btn_panel.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))

        ttk.Button(btn_panel, text=f"{Icons.PLUS} Insert",
                  command=callbacks.get('insert'),
                  style='Outline.TButton').pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_panel, text=f"{Icons.DELETE} Delete",
                  command=callbacks.get('delete_step'),
                  style='Outline.TButton').pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_panel, text=f"{Icons.CHECKMARK} Toggle",
                  command=callbacks.get('toggle'),
                  style='Outline.TButton').pack(side=tk.LEFT, padx=2)

        # Stats label
        stats_label = ttk.Label(btn_panel, text="0 actions",
                               style='Status.TLabel')
        stats_label.pack(side=tk.RIGHT, padx=5)

        return frame, tree, stats_label

    @staticmethod
    def create_status_bar(parent) -> tuple:
        """
        Create modern status bar with progress

        Args:
            parent: Parent widget

        Returns:
            Tuple of (frame, status_label, progress_bar)
        """
        status_frame = ttk.Frame(parent, style='Card.TFrame', padding="5")

        # Status label
        status_label = ttk.Label(status_frame,
                                text="Ready",
                                style='Status.TLabel')
        status_label.pack(side=tk.LEFT, padx=5)

        # Progress bar (initially hidden)
        progress = ttk.Progressbar(status_frame, mode='indeterminate',
                                  length=200)

        return status_frame, status_label, progress

    @staticmethod
    def populate_treeview(tree: ttk.Treeview, actions: List[Dict[str, Any]],
                         stats_label: Optional[ttk.Label] = None):
        """
        Populate treeview with actions

        Args:
            tree: Treeview widget
            actions: List of action dictionaries
            stats_label: Optional label to update with stats
        """
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Add actions
        for i, action in enumerate(actions, 1):
            enabled = action.get('enabled', True)
            status = Icons.CHECK if enabled else Icons.CROSS
            action_type = action['type'].upper()
            desc = action.get('description', '')

            # Format details based on action type
            details = ModernGUIBuilder._format_action_details(action)

            # Add to tree with tag for styling
            tag = 'enabled' if enabled else 'disabled'
            tree.insert('', tk.END, iid=str(i-1),
                       values=(status, action_type, details, desc),
                       tags=(tag,))

        # Configure tags
        tree.tag_configure('enabled', foreground=ModernTheme.TEXT)
        tree.tag_configure('disabled', foreground=ModernTheme.TEXT_LIGHT)

        # Update stats
        if stats_label:
            enabled_count = sum(1 for a in actions if a.get('enabled', True))
            stats_label.config(text=f"{len(actions)} actions ({enabled_count} enabled)")

    @staticmethod
    def _format_action_details(action: Dict[str, Any]) -> str:
        """Format action details for display"""
        action_type = action['type']

        if action_type == 'click':
            if action.get('use_current_position'):
                return "at current position"
            return f"at ({action['x']}, {action['y']})"

        elif action_type == 'type':
            text = action.get('text', '')
            return f'"{text[:40]}..."' if len(text) > 40 else f'"{text}"'

        elif action_type == 'set_value':
            value = action.get('value', '')
            loc = "current pos" if action.get('use_current_position') else f"({action.get('x')}, {action.get('y')})"
            return f'{loc} = "{value[:30]}"'

        elif action_type == 'scroll':
            scroll_type = action.get('scroll_type', 'amount')
            if scroll_type == 'amount':
                return f"{action.get('amount')} pixels"
            return f"to {scroll_type}"

        elif action_type == 'wait':
            wait_type = action.get('wait_type', 'duration')
            if wait_type == 'duration':
                return f"{action.get('duration')}s"
            return f"for image: {action.get('image_name')}"

        elif action_type == 'find_image':
            click = " + click" if action.get('click_after') else ""
            return f"{action.get('image_name')}{click}"

        elif action_type == 'move_mouse':
            return f"{action.get('direction')} {action.get('distance')}px"

        elif action_type == 'delete':
            return f"method: {action.get('method')}"

        return ""


class ModernDialog:
    """Professional dialog windows"""

    @staticmethod
    def create_input_dialog(parent, title: str, fields: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Create modern input dialog with multiple fields

        Args:
            parent: Parent window
            title: Dialog title
            fields: List of field definitions [{'name': 'field1', 'label': 'Label:', 'type': 'text', 'default': ''}]

        Returns:
            Dictionary of field values or None if cancelled
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.grab_set()

        # Configure dialog
        dialog.configure(bg=ModernTheme.BACKGROUND)

        # Center dialog
        dialog.geometry("500x400")
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = {'cancelled': True}
        entries = {}

        # Content frame
        content = ttk.Frame(dialog, padding="20", style='Card.TFrame')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        ttk.Label(content, text=title, style='Title.TLabel').pack(anchor=tk.W, pady=(0, 15))

        # Fields
        for field in fields:
            field_frame = ttk.Frame(content)
            field_frame.pack(fill=tk.X, pady=5)

            ttk.Label(field_frame, text=field.get('label', ''),
                     style='TLabel').pack(anchor=tk.W, pady=(0, 3))

            field_type = field.get('type', 'text')

            if field_type == 'text':
                entry = ttk.Entry(field_frame, width=50)
                entry.insert(0, field.get('default', ''))
                entry.pack(fill=tk.X)
                entries[field['name']] = entry

            elif field_type == 'number':
                entry = ttk.Entry(field_frame, width=20)
                entry.insert(0, str(field.get('default', '')))
                entry.pack(anchor=tk.W)
                entries[field['name']] = entry

            elif field_type == 'choice':
                var = tk.StringVar(value=field.get('default', ''))
                choices = field.get('choices', [])
                for choice in choices:
                    ttk.Radiobutton(field_frame, text=choice, variable=var,
                                   value=choice).pack(anchor=tk.W, padx=10)
                entries[field['name']] = var

            elif field_type == 'checkbox':
                var = tk.BooleanVar(value=field.get('default', False))
                ttk.Checkbutton(field_frame, text=field.get('text', ''),
                               variable=var).pack(anchor=tk.W)
                entries[field['name']] = var

        # Button frame
        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=(20, 0))

        def on_ok():
            # Collect values
            result['cancelled'] = False
            for name, widget in entries.items():
                if isinstance(widget, tk.StringVar) or isinstance(widget, tk.BooleanVar):
                    result[name] = widget.get()
                else:
                    result[name] = widget.get()
            dialog.destroy()

        def on_cancel():
            result['cancelled'] = True
            dialog.destroy()

        ttk.Button(btn_frame, text=f"{Icons.CHECK} OK",
                  command=on_ok,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text=f"{Icons.CLOSE} Cancel",
                  command=on_cancel,
                  style='Outline.TButton').pack(side=tk.LEFT, padx=5)

        # Bind Enter key
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        # Wait for dialog
        dialog.wait_window()

        return None if result.get('cancelled') else result

    @staticmethod
    def show_about(parent):
        """Show about dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title("About Amazon Simulator")
        dialog.transient(parent)
        dialog.grab_set()
        dialog.geometry("450x350")
        dialog.configure(bg=ModernTheme.BACKGROUND)
        dialog.resizable(False, False)

        # Center
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (225)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (175)
        dialog.geometry(f"+{x}+{y}")

        content = ttk.Frame(dialog, padding="30", style='Card.TFrame')
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # App name
        ttk.Label(content, text="Amazon Simulator",
                 style='Title.TLabel').pack(pady=(0, 5))

        # Version
        ttk.Label(content, text="Version 2.0 - Professional Edition",
                 foreground=ModernTheme.TEXT_SECONDARY).pack()

        # Description
        desc = ("Automate your Amazon seller operations with powerful\n"
                "recording and playback capabilities.\n\n"
                "Record once, replay unlimited times.")
        ttk.Label(content, text=desc,
                 justify=tk.CENTER,
                 foreground=ModernTheme.TEXT_SECONDARY).pack(pady=20)

        # Features
        features_text = (
            "✓ Record mouse and keyboard actions\n"
            "✓ Image recognition support\n"
            "✓ Batch processing with SKUs\n"
            "✓ Professional UI/UX\n"
            "✓ Modular architecture"
        )
        ttk.Label(content, text=features_text,
                 justify=tk.LEFT).pack(pady=10)

        # Close button
        ttk.Button(content, text="Close",
                  command=dialog.destroy,
                  style='Primary.TButton').pack(pady=(20, 0))
