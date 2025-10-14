"""
Recording Overlay - Visual feedback during recording
Shows recording status, action count, and controls
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from src.theme import ModernTheme, Icons


class RecordingOverlay:
    """Floating overlay showing recording status"""

    def __init__(self, parent, on_pause: Optional[Callable] = None,
                 on_resume: Optional[Callable] = None,
                 on_stop: Optional[Callable] = None):
        """
        Initialize recording overlay

        Args:
            parent: Parent window
            on_pause: Callback when pause is clicked
            on_resume: Callback when resume is clicked
            on_stop: Callback when stop is clicked
        """
        self.parent = parent
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_stop = on_stop

        # Create overlay window
        self.window = tk.Toplevel(parent)
        self.window.title("Recording")
        self.window.geometry("320x140")

        # Window properties
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(False)  # Keep title bar for dragging
        self.window.resizable(False, False)

        # Position at top-right of screen
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"+{screen_width - 340}+20")

        # State
        self.is_paused = False
        self.action_count = 0

        # Create UI
        self._create_ui()

        # Make window stay on top
        self.window.lift()
        self.window.focus_force()

    def _create_ui(self):
        """Create overlay UI"""
        # Main container
        container = tk.Frame(self.window, bg='#2d2d2d', padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Header with recording indicator
        header = tk.Frame(container, bg='#2d2d2d')
        header.pack(fill=tk.X, pady=(0, 10))

        # Recording dot (animated)
        self.recording_dot = tk.Label(header, text="●", font=('Arial', 20),
                                     fg='#ff4444', bg='#2d2d2d')
        self.recording_dot.pack(side=tk.LEFT, padx=(0, 10))

        # Status label
        self.status_label = tk.Label(header, text="RECORDING",
                                     font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                                     fg='white', bg='#2d2d2d')
        self.status_label.pack(side=tk.LEFT)

        # Action counter
        counter_frame = tk.Frame(container, bg='#3d3d3d', padx=10, pady=8)
        counter_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(counter_frame, text="Actions Recorded:",
                font=(ModernTheme.FONT_FAMILY, 9),
                fg='#cccccc', bg='#3d3d3d').pack(side=tk.LEFT)

        self.count_label = tk.Label(counter_frame, text="0",
                                    font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                                    fg='#4CAF50', bg='#3d3d3d')
        self.count_label.pack(side=tk.RIGHT)

        # Control buttons
        controls = tk.Frame(container, bg='#2d2d2d')
        controls.pack(fill=tk.X)

        # Pause/Resume button
        self.pause_btn = tk.Button(controls, text="⏸ Pause",
                                   font=(ModernTheme.FONT_FAMILY, 10),
                                   bg='#555555', fg='white',
                                   activebackground='#666666',
                                   relief=tk.FLAT, padx=15, pady=8,
                                   cursor='hand2',
                                   command=self._on_pause_resume_click)
        self.pause_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Stop button
        stop_btn = tk.Button(controls, text="⏹ Stop",
                            font=(ModernTheme.FONT_FAMILY, 10),
                            bg='#d32f2f', fg='white',
                            activebackground='#b71c1c',
                            relief=tk.FLAT, padx=15, pady=8,
                            cursor='hand2',
                            command=self._on_stop_click)
        stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Hotkey hint
        hint = tk.Label(container, text="Hotkeys: P = Pause/Resume, S = Stop",
                       font=(ModernTheme.FONT_FAMILY, 8),
                       fg='#888888', bg='#2d2d2d')
        hint.pack(pady=(10, 0))

        # Start animation
        self._animate_recording_dot()

    def _animate_recording_dot(self):
        """Animate recording dot"""
        if not self.window.winfo_exists():
            return

        if not self.is_paused:
            current_fg = self.recording_dot.cget('fg')
            new_fg = '#ff4444' if current_fg == '#ff8888' else '#ff8888'
            self.recording_dot.config(fg=new_fg)

        self.window.after(500, self._animate_recording_dot)

    def _on_pause_resume_click(self):
        """Handle pause/resume button click"""
        if self.is_paused:
            if self.on_resume:
                self.on_resume()
        else:
            if self.on_pause:
                self.on_pause()

    def _on_stop_click(self):
        """Handle stop button click"""
        if self.on_stop:
            self.on_stop()

    def set_paused(self, paused: bool):
        """Set paused state"""
        self.is_paused = paused

        if paused:
            self.status_label.config(text="PAUSED")
            self.recording_dot.config(fg='#ffaa00')
            self.pause_btn.config(text="▶ Resume", bg='#4CAF50')
        else:
            self.status_label.config(text="RECORDING")
            self.recording_dot.config(fg='#ff4444')
            self.pause_btn.config(text="⏸ Pause", bg='#555555')

    def update_count(self, count: int):
        """Update action count"""
        self.action_count = count
        self.count_label.config(text=str(count))

        # Flash the counter
        self.count_label.config(fg='#8BC34A')
        self.window.after(200, lambda: self.count_label.config(fg='#4CAF50'))

    def show(self):
        """Show overlay"""
        self.window.deiconify()
        self.window.lift()
        self.window.attributes('-topmost', True)

    def hide(self):
        """Hide overlay"""
        self.window.withdraw()

    def destroy(self):
        """Destroy overlay"""
        if self.window.winfo_exists():
            self.window.destroy()


class RecordingControlPanel:
    """Control panel for recording in main window"""

    def __init__(self, parent, on_start: Optional[Callable] = None,
                 on_pause: Optional[Callable] = None,
                 on_stop: Optional[Callable] = None):
        """
        Initialize recording control panel

        Args:
            parent: Parent widget
            on_start: Callback when start recording is clicked
            on_pause: Callback when pause is clicked
            on_stop: Callback when stop is clicked
        """
        self.parent = parent
        self.on_start = on_start
        self.on_pause = on_pause
        self.on_stop = on_stop

        # Create frame
        self.frame = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        self.is_recording = False

        self._create_ui()

    def _create_ui(self):
        """Create control panel UI"""
        # Title
        title = tk.Label(self.frame, text="Recording Controls",
                        font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                        bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT)
        title.pack(pady=(0, 10))

        # Info
        info = tk.Label(self.frame,
                       text="Record your actions automatically\nClicks, typing, and scrolling will be captured",
                       font=(ModernTheme.FONT_FAMILY, 9),
                       bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT_SECONDARY,
                       justify=tk.LEFT)
        info.pack(pady=(0, 15))

        # Start button
        self.start_btn = tk.Button(self.frame, text="🔴 Start Recording",
                                   font=(ModernTheme.FONT_FAMILY, 11, 'bold'),
                                   bg='#d32f2f', fg='white',
                                   activebackground='#b71c1c',
                                   relief=tk.FLAT, padx=20, pady=12,
                                   cursor='hand2',
                                   command=self._on_start_click)
        self.start_btn.pack(fill=tk.X)

        # Recording status (hidden initially)
        self.status_frame = tk.Frame(self.frame, bg='#2d2d2d', padx=15, pady=15)

        status_label = tk.Label(self.status_frame, text="● Recording in progress...",
                               font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                               bg='#2d2d2d', fg='#ff4444')
        status_label.pack(pady=(0, 10))

        self.action_count_label = tk.Label(self.status_frame, text="0 actions recorded",
                                           font=(ModernTheme.FONT_FAMILY, 9),
                                           bg='#2d2d2d', fg='#cccccc')
        self.action_count_label.pack(pady=(0, 10))

        # Pause button
        self.pause_btn = tk.Button(self.status_frame, text="⏸ Pause",
                                   font=(ModernTheme.FONT_FAMILY, 10),
                                   bg='#555555', fg='white',
                                   relief=tk.FLAT, padx=15, pady=8,
                                   cursor='hand2',
                                   command=self._on_pause_click)
        self.pause_btn.pack(fill=tk.X, pady=(0, 5))

        # Stop button
        stop_btn = tk.Button(self.status_frame, text="⏹ Stop Recording",
                            font=(ModernTheme.FONT_FAMILY, 10),
                            bg='#d32f2f', fg='white',
                            relief=tk.FLAT, padx=15, pady=8,
                            cursor='hand2',
                            command=self._on_stop_click)
        stop_btn.pack(fill=tk.X)

    def _on_start_click(self):
        """Handle start button click"""
        if self.on_start:
            self.on_start()

    def _on_pause_click(self):
        """Handle pause button click"""
        if self.on_pause:
            self.on_pause()

    def _on_stop_click(self):
        """Handle stop button click"""
        if self.on_stop:
            self.on_stop()

    def show_recording(self):
        """Show recording state"""
        self.is_recording = True
        self.start_btn.pack_forget()
        self.status_frame.pack(fill=tk.X, pady=(10, 0))

    def show_idle(self):
        """Show idle state"""
        self.is_recording = False
        self.status_frame.pack_forget()
        self.start_btn.pack(fill=tk.X)

    def update_count(self, count: int):
        """Update action count"""
        self.action_count_label.config(text=f"{count} action{'s' if count != 1 else ''} recorded")

    def set_paused(self, paused: bool):
        """Set paused state"""
        if paused:
            self.pause_btn.config(text="▶ Resume", bg='#4CAF50')
        else:
            self.pause_btn.config(text="⏸ Pause", bg='#555555')

    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)

    def destroy(self):
        """Destroy the frame"""
        self.frame.destroy()


# Test code
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Recording Overlay Test")
    root.geometry("400x300")
    root.configure(bg=ModernTheme.BACKGROUND)

    def on_pause():
        print("Pause clicked")
        overlay.set_paused(True)

    def on_resume():
        print("Resume clicked")
        overlay.set_paused(False)

    def on_stop():
        print("Stop clicked")
        overlay.destroy()

    # Test overlay
    overlay = RecordingOverlay(root, on_pause=on_pause, on_resume=on_resume, on_stop=on_stop)
    overlay.show()

    # Simulate action count updates
    count = 0

    def update_count():
        global count
        count += 1
        overlay.update_count(count)
        root.after(1000, update_count)

    root.after(1000, update_count)

    root.mainloop()
