"""
Modern theme and styling for Amazon Simulator
"""
import tkinter as tk
from tkinter import ttk


class ModernTheme:
    """Modern color scheme and styling"""

    # Color palette - Coffee/Beige theme based on provided CSS
    PRIMARY = "#644a40"          # Coffee brown
    PRIMARY_DARK = "#503a32"     # Darker coffee brown
    PRIMARY_LIGHT = "#7a5e54"    # Lighter coffee brown

    SECONDARY = "#ffdfb5"        # Light beige
    SECONDARY_DARK = "#e8c9a0"   # Darker beige
    SECONDARY_LIGHT = "#ffe6c4"  # Lighter beige

    SUCCESS = "#644a40"          # Coffee brown (same as primary)
    WARNING = "#e8e8e8"          # Light gray
    ERROR = "#e54d2e"            # Red
    INFO = "#644a40"             # Coffee brown

    BACKGROUND = "#f9f9f9"       # Light background
    SURFACE = "#fcfcfc"          # Light white surface
    SURFACE_DARK = "#f7f7f7"     # Slightly darker surface

    TEXT = "#202020"             # Dark gray text
    TEXT_SECONDARY = "#646464"   # Medium gray text
    TEXT_LIGHT = "#b4b4b4"       # Light gray text

    BORDER = "#d8d8d8"           # Light border
    BORDER_DARK = "#c0c0c0"      # Darker border
    
    # Additional colors
    PRIMARY_FG = "#ffffff"       # White text on primary
    SECONDARY_FG = "#582d1d"     # Dark brown text on secondary
    ERROR_FG = "#ffffff"         # White text on error

    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 16
    FONT_SIZE_HEADING = 14

    @staticmethod
    def configure_style():
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()

        # Use 'clam' theme as base for better customization
        style.theme_use('clam')

        # Configure TFrame
        style.configure('TFrame',
                       background=ModernTheme.BACKGROUND)

        style.configure('Card.TFrame',
                       background=ModernTheme.SURFACE,
                       relief='flat',
                       borderwidth=1)

        style.configure('Dragging.Card.TFrame',
                       background=ModernTheme.SURFACE,
                       relief='raised',
                       borderwidth=2)

        style.configure('Selected.Card.TFrame',
                       background='#fffef8',  # Slightly brighter
                       relief='raised',
                       borderwidth=3)

        # Configure TLabel
        style.configure('TLabel',
                       background=ModernTheme.BACKGROUND,
                       foreground=ModernTheme.TEXT,
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL))

        style.configure('Title.TLabel',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_TITLE, 'bold'),
                       foreground=ModernTheme.PRIMARY)

        style.configure('Heading.TLabel',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_HEADING, 'bold'),
                       foreground=ModernTheme.TEXT)

        style.configure('Status.TLabel',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL),
                       foreground=ModernTheme.TEXT_SECONDARY,
                       background=ModernTheme.SURFACE_DARK)

        style.configure('Success.TLabel',
                       foreground=ModernTheme.SUCCESS)

        style.configure('Error.TLabel',
                       foreground=ModernTheme.ERROR)

        # Configure TButton (default style)
        style.configure('TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
                       background=ModernTheme.PRIMARY,
                       foreground='white',
                       borderwidth=0,
                       relief='flat',
                       padding=(12, 6))

        style.map('TButton',
                 background=[('active', ModernTheme.PRIMARY_LIGHT),
                           ('!active', ModernTheme.PRIMARY)],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])

        # Primary button (explicit style)
        style.configure('Primary.TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
                       background=ModernTheme.PRIMARY,
                       foreground='white',
                       borderwidth=0,
                       padding=(12, 6))

        style.map('Primary.TButton',
                 background=[('active', ModernTheme.PRIMARY_LIGHT),
                           ('!active', ModernTheme.PRIMARY)],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])

        # Secondary button
        style.configure('Secondary.TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
                       background=ModernTheme.SECONDARY,
                       foreground=ModernTheme.SECONDARY_FG,
                       borderwidth=0,
                       padding=(12, 6))

        style.map('Secondary.TButton',
                 background=[('active', ModernTheme.SECONDARY_DARK),
                           ('!active', ModernTheme.SECONDARY)],
                 foreground=[('active', ModernTheme.SECONDARY_FG),
                           ('!active', ModernTheme.SECONDARY_FG)])

        # Success button
        style.configure('Success.TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
                       background=ModernTheme.SUCCESS,
                       foreground='white',
                       borderwidth=0,
                       padding=(12, 6))

        style.map('Success.TButton',
                 background=[('active', ModernTheme.PRIMARY_DARK),
                           ('!active', ModernTheme.SUCCESS)],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])

        # Danger button
        style.configure('Danger.TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
                       background='#d32f2f',
                       foreground='white',
                       borderwidth=0,
                       padding=(12, 6))

        style.map('Danger.TButton',
                 background=[('active', '#b71c1c'),
                           ('!active', '#d32f2f')],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])

        # Outline button (white background with colored text and border)
        style.configure('Outline.TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
                       background=ModernTheme.SURFACE,
                       foreground=ModernTheme.PRIMARY,
                       borderwidth=2,
                       bordercolor=ModernTheme.PRIMARY,
                       relief='solid',
                       padding=(12, 6),
                       lightcolor=ModernTheme.PRIMARY,
                       darkcolor=ModernTheme.PRIMARY)

        style.map('Outline.TButton',
                 background=[('active', ModernTheme.SURFACE_DARK),
                           ('!active', ModernTheme.SURFACE)],
                 foreground=[('active', ModernTheme.PRIMARY_DARK),
                           ('!active', ModernTheme.PRIMARY)],
                 bordercolor=[('active', ModernTheme.PRIMARY_DARK),
                            ('!active', ModernTheme.PRIMARY)])

        # Small button
        style.configure('Small.TButton',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL),
                       background=ModernTheme.PRIMARY,
                       foreground='white',
                       borderwidth=0,
                       padding=(8, 4))

        style.map('Small.TButton',
                 background=[('active', ModernTheme.PRIMARY_LIGHT),
                           ('!active', ModernTheme.PRIMARY)],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])

        # Configure TLabelFrame
        style.configure('TLabelframe',
                       background=ModernTheme.SURFACE,
                       borderwidth=1,
                       relief='solid')

        style.configure('TLabelframe.Label',
                       background=ModernTheme.SURFACE,
                       foreground=ModernTheme.TEXT,
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL, 'bold'))

        # Configure Treeview
        style.configure('Treeview',
                       background=ModernTheme.SURFACE,
                       foreground=ModernTheme.TEXT,
                       fieldbackground=ModernTheme.SURFACE,
                       borderwidth=1,
                       relief='flat',
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL))

        style.configure('Treeview.Heading',
                       background=ModernTheme.WARNING,
                       foreground=ModernTheme.TEXT,
                       borderwidth=0,
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL, 'bold'))

        style.map('Treeview',
                 background=[('selected', ModernTheme.SECONDARY)],
                 foreground=[('selected', ModernTheme.SECONDARY_DARK)])

        # Configure Entry
        style.configure('TEntry',
                       fieldbackground=ModernTheme.SURFACE,
                       foreground=ModernTheme.TEXT,
                       borderwidth=1,
                       relief='solid')

        # Configure Checkbutton
        style.configure('TCheckbutton',
                       background=ModernTheme.BACKGROUND,
                       foreground=ModernTheme.TEXT)

        # Configure Progressbar
        style.configure('TProgressbar',
                       background=ModernTheme.PRIMARY,
                       troughcolor=ModernTheme.WARNING,
                       borderwidth=0,
                       thickness=20)

        # Configure Notebook
        style.configure('TNotebook',
                       background=ModernTheme.BACKGROUND,
                       borderwidth=0)

        style.configure('TNotebook.Tab',
                       background=ModernTheme.SURFACE_DARK,
                       foreground=ModernTheme.TEXT,
                       padding=(12, 6),
                       font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL))

        style.map('TNotebook.Tab',
                 background=[('selected', ModernTheme.SURFACE)],
                 foreground=[('selected', ModernTheme.PRIMARY)])

        return style


class Icons:
    """Unicode icons for various UI elements"""

    # General
    CLOSE = "✕"
    CHECK = "✓"
    CHECKMARK = "✓"
    CROSS = "✗"
    PLUS = "+"
    MINUS = "−"
    ELLIPSIS = "⋯"

    # Actions
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    RECORD = "⏺"
    SETTINGS = "⚙"

    # Navigation
    UP = "▲"
    DOWN = "▼"
    LEFT = "◀"
    RIGHT = "▶"

    # Files
    FOLDER = "📁"
    FILE = "📄"
    SAVE = "💾"
    DOWNLOAD = "⬇"
    UPLOAD = "⬆"

    # Status
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"

    # Tools
    EDIT = "✎"
    DELETE = "🗑"
    COPY = "📋"
    SEARCH = "🔍"

    # Actions types
    CLICK = "🖱"
    KEYBOARD = "⌨"
    IMAGE = "🖼"
    TIME = "⏱"
    MOUSE = "🖱"
    SCROLL = "📜"
