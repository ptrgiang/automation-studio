"""
Modern theme and styling for Amazon Simulator
"""
import tkinter as tk
from tkinter import ttk
from src.theme_shadcn import ShadcnTheme

class ModernTheme(ShadcnTheme):
    """Modern professional theme for UI components"""

    @staticmethod
    def configure_style():
        """Configure ttk styles for a modern look"""
        style = ttk.Style()
        style.theme_use('clam')

        # General widget styling
        style.configure('.',
                        background=ModernTheme.BACKGROUND,
                        foreground=ModernTheme.FOREGROUND,
                        font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD),
                        borderwidth=0,
                        focuscolor=ModernTheme.RING)

        # Frame and LabelFrame
        style.configure('TFrame', background=ModernTheme.BACKGROUND)
        style.configure('TLabelFrame', background=ModernTheme.BACKGROUND, borderwidth=1, relief="solid")
        style.configure('TLabelFrame.Label', foreground=ModernTheme.MUTED_FOREGROUND, background=ModernTheme.BACKGROUND)

        # Button
        style.configure('TButton', padding=ModernTheme.PADDING_MD, borderwidth=1, relief="solid")
        style.map('TButton', background=[('active', ModernTheme.MUTED)])

        # Primary Button
        style.configure('Primary.TButton', background=ModernTheme.PRIMARY, foreground=ModernTheme.PRIMARY_FOREGROUND)
        style.map('Primary.TButton', background=[('active', ModernTheme.PRIMARY)])

        # Destructive Button
        style.configure('Destructive.TButton', background=ModernTheme.DESTRUCTIVE, foreground="#ffffff")
        style.map('Destructive.TButton', background=[('active', ModernTheme.DESTRUCTIVE)])

        # Outline Button
        style.configure('Outline.TButton', background=ModernTheme.BACKGROUND, foreground=ModernTheme.FOREGROUND)
        style.map('Outline.TButton', background=[('active', ModernTheme.MUTED)])

        # Treeview
        style.configure('Treeview', rowheight=25, fieldbackground=ModernTheme.BACKGROUND, borderwidth=0)
        style.configure('Treeview.Heading', font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD, 'bold'))
        style.map('Treeview', background=[('selected', ModernTheme.MUTED)])

        # Scrollbars
        style.configure('Vertical.TScrollbar', background=ModernTheme.BACKGROUND, troughcolor=ModernTheme.MUTED)
        style.configure('Horizontal.TScrollbar', background=ModernTheme.BACKGROUND, troughcolor=ModernTheme.MUTED)

        # Card Styles (clean, no borders)
        style.configure('Card.TFrame', background=ModernTheme.CARD, borderwidth=0, relief='flat')
        style.configure('Card.TLabel', background=ModernTheme.CARD, foreground=ModernTheme.CARD_FOREGROUND)

        # Disabled Card Style - Properly muted for better appearance
        style.configure('Disabled.Card.TFrame', background='#f1f5f9', borderwidth=0, relief='flat')  # MUTED background
        style.configure('Disabled.Card.TLabel', background='#f1f5f9', foreground='#a1a1aa')  # Zinc 400 - more muted gray

class Icons:
    """Modern icon set"""
    FOLDER = "📁"
    SAVE = "💾"
    PLAY = "▶️"
    PLUS = "+"
    DELETE = "🗑️"
    COPY = "📋"
    COMMENT = "💬"
    VARIABLE = "x"
    INFO = "ℹ️"
    CHECK = "✔️"
    CROSS = "❌"
    KEYBOARD = "⌨️"
    MOUSE = "🖱️"
    SCROLL = "↕️"
    EDIT = "✏️"
    TIME = "⏱️"
    IMAGE = "🖼️"
