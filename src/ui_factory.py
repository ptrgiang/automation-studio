"""
UI Factory for creating menu and toolbar
"""
import tkinter as tk
from tkinter import ttk
from src.theme import Icons

def create_menu(app):
    """Create menu bar"""
    menubar = tk.Menu(app.root)
    app.root.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label=f"{Icons.PLUS} New Workflow...",
                            command=app.workflow_manager.new_workflow, accelerator="Ctrl+N")
    file_menu.add_command(label=f"{Icons.FOLDER} Open Workflow...",
                            command=app.load_workflow, accelerator="Ctrl+O")
    file_menu.add_command(label=f"{Icons.SAVE} Save Workflow...",
                            command=app.save_workflow, accelerator="Ctrl+S")
    file_menu.add_separator()
    file_menu.add_command(label=f"{Icons.SAVE} Export to Classic Format...",
                            command=app.export_classic)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.quit_app, accelerator="Ctrl+Q")

    # Edit menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Delete Selected", command=app.delete_selected,
                            accelerator="Del")
    edit_menu.add_command(label="Duplicate Selected", command=app.duplicate_selected,
                            accelerator="Ctrl+D")
    edit_menu.add_separator()
    edit_menu.add_command(label="💬 Add Comment", command=app.add_comment_to_selected,
                            accelerator="Ctrl+M")
    edit_menu.add_separator()
    edit_menu.add_command(label="Manage Batch Variables...", command=app.open_variable_manager)

    # View menu
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Zoom In", command=app.visual_canvas.zoom_in,
                            accelerator="+")
    view_menu.add_command(label="Zoom Out", command=app.visual_canvas.zoom_out,
                            accelerator="-")
    view_menu.add_command(label="Fit to Window", command=app.visual_canvas.zoom_fit,
                            accelerator="0")

    # Templates menu
    templates_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Templates", menu=templates_menu)
    templates_menu.add_command(label="📋 Insert Template...", command=app.insert_template)
    templates_menu.add_command(label="💾 Save as Template...", command=app.save_as_template)
    templates_menu.add_separator()
    templates_menu.add_command(label="📚 Browse Templates", command=app.browse_templates)

    # Playback menu
    playback_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Playback", menu=playback_menu)
    playback_menu.add_command(label=f"{Icons.PLAY} Play Workflow",
                                command=app.play_workflow, accelerator="F5")

    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label=f"{Icons.INFO} About", command=app.show_about)

    # Bind keyboard shortcuts
    app.root.bind('<Control-n>', lambda e: app.workflow_manager.new_workflow())
    app.root.bind('<Control-s>', lambda e: app.save_workflow())
    app.root.bind('<Control-o>', lambda e: app.load_workflow())
    app.root.bind('<Control-d>', lambda e: app.duplicate_selected())
    app.root.bind('<Control-m>', lambda e: app.add_comment_to_selected())
    app.root.bind('<Delete>', lambda e: app.delete_selected())
    app.root.bind('<F5>', lambda e: app.play_workflow())

    # Navigation shortcuts
    app.root.bind('<Up>', lambda e: app._navigate_up())
    app.root.bind('<Down>', lambda e: app._navigate_down())
    app.root.bind('<Control-Up>', lambda e: app._move_action_up())
    app.root.bind('<Control-Down>', lambda e: app._move_action_down())

def create_toolbar(app):
    """Create main toolbar"""
    toolbar = ttk.Frame(app.root, style='Toolbar.TFrame', height=50)
    toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))
    toolbar.pack_propagate(False)

    # File operations
    ttk.Button(toolbar, text=f"{Icons.FOLDER} Open",
                command=app.load_workflow).pack(side=tk.LEFT, padx=2)
    ttk.Button(toolbar, text=f"{Icons.SAVE} Save",
                command=app.save_workflow).pack(side=tk.LEFT, padx=2)

    ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

    # Record button
    app.record_btn = ttk.Button(toolbar, text="🔴 Record",
                                    command=app.start_recording,
                                    style='Danger.TButton')
    app.record_btn.pack(side=tk.LEFT, padx=2)

    ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

    # Playback controls
    ttk.Button(toolbar, text=f"{Icons.PLAY} Play",
                command=app.play_workflow,
                style='Success.TButton').pack(side=tk.LEFT, padx=2)

    # Status
    app.status_label = ttk.Label(toolbar, text="Ready",
                                    style='Secondary.TLabel')
    app.status_label.pack(side=tk.RIGHT, padx=10)
