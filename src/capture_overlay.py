"""
Screen Capture Overlay
Full-screen transparent overlay for visual target selection
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Callable, Dict, Any
import pyautogui
from PIL import Image, ImageTk, ImageDraw
import logging


class CaptureMode:
    """Capture mode constants"""
    POINT = "point"  # Click to capture a point
    REGION = "region"  # Drag to capture a region


class CaptureOverlay:
    """Full-screen overlay for capturing screen regions visually"""

    def __init__(self, parent, mode: str = CaptureMode.POINT,
                 callback: Optional[Callable] = None):
        """
        Initialize capture overlay

        Args:
            parent: Parent window
            mode: Capture mode (POINT or REGION)
            callback: Callback function(result_dict) called on capture
        """
        self.parent = parent
        self.mode = mode
        self.callback = callback

        # Capture state
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.is_selecting = False

        # Screenshot
        self.screenshot = None
        self.screenshot_image = None

        # UI elements
        self.overlay = None
        self.canvas = None
        self.selection_rect = None
        self.crosshair_h = None
        self.crosshair_v = None
        self.help_text = None

        # Result
        self.result = None

    def show(self):
        """Show the capture overlay"""
        # Capture screenshot first
        self._capture_screenshot()

        # Create overlay window
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.3)  # Semi-transparent
        self.overlay.configure(bg='black')

        # Disable window decorations
        self.overlay.overrideredirect(True)

        # Get screen size
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()

        # Create canvas
        self.canvas = tk.Canvas(self.overlay,
                               width=screen_width,
                               height=screen_height,
                               bg='black',
                               highlightthickness=0,
                               cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Display screenshot
        self.canvas.create_image(0, 0, image=self.screenshot_image, anchor=tk.NW)

        # Create help text
        if self.mode == CaptureMode.POINT:
            help_msg = "Click on the target location • ESC to cancel"
        else:
            help_msg = "Click and drag to select region • ESC to cancel"

        self.help_text = self.canvas.create_text(
            screen_width // 2, 30,
            text=help_msg,
            font=('Arial', 16, 'bold'),
            fill='white',
            tags='help'
        )

        # Create crosshair lines (initially hidden)
        self.crosshair_h = self.canvas.create_line(
            0, 0, screen_width, 0,
            fill='#00FF00', width=1, dash=(5, 5), tags='crosshair'
        )
        self.crosshair_v = self.canvas.create_line(
            0, 0, 0, screen_height,
            fill='#00FF00', width=1, dash=(5, 5), tags='crosshair'
        )

        # Create selection rectangle (initially hidden)
        self.selection_rect = self.canvas.create_rectangle(
            0, 0, 0, 0,
            outline='#00FF00', width=2, tags='selection'
        )

        # Bind events
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.overlay.bind('<Escape>', self._on_cancel)

        # Focus overlay
        self.overlay.focus_force()
        self.overlay.grab_set()

        logging.info(f"Capture overlay shown in {self.mode} mode")

    def _capture_screenshot(self):
        """Capture current screen"""
        self.screenshot = pyautogui.screenshot()

        # Convert to PhotoImage for display
        self.screenshot_image = ImageTk.PhotoImage(self.screenshot)

    def _on_mouse_move(self, event):
        """Handle mouse movement"""
        # Update crosshair position
        self.canvas.coords(self.crosshair_h, 0, event.y,
                          self.canvas.winfo_width(), event.y)
        self.canvas.coords(self.crosshair_v, event.x, 0,
                          event.x, self.canvas.winfo_height())

        # Update current position
        self.current_x = event.x
        self.current_y = event.y

        # If dragging in region mode, update selection rectangle
        if self.is_selecting and self.mode == CaptureMode.REGION:
            self._update_selection_rect()

    def _on_mouse_down(self, event):
        """Handle mouse button press"""
        self.start_x = event.x
        self.start_y = event.y
        self.is_selecting = True

        if self.mode == CaptureMode.POINT:
            # In point mode, immediate capture on click
            self._capture_point()
        else:
            # In region mode, start selection
            self.canvas.itemconfig(self.selection_rect, state='normal')

    def _on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.mode == CaptureMode.REGION and self.is_selecting:
            self.current_x = event.x
            self.current_y = event.y
            self._update_selection_rect()

    def _on_mouse_up(self, event):
        """Handle mouse button release"""
        if self.mode == CaptureMode.REGION and self.is_selecting:
            self.current_x = event.x
            self.current_y = event.y
            self._capture_region()

        self.is_selecting = False

    def _update_selection_rect(self):
        """Update selection rectangle coordinates"""
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)

        self.canvas.coords(self.selection_rect, x1, y1, x2, y2)

        # Show dimensions
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # Update help text to show dimensions
        self.canvas.itemconfig(
            self.help_text,
            text=f"Region: {width} × {height} pixels • Release to capture • ESC to cancel"
        )

    def _capture_point(self):
        """Capture a point with context"""
        logging.info(f"Captured point: ({self.start_x}, {self.start_y})")

        # Create result
        self.result = {
            'mode': CaptureMode.POINT,
            'x': self.start_x,
            'y': self.start_y,
            'screenshot': self.screenshot,
            'success': True
        }

        # Close overlay and call callback
        self._finish_capture()

    def _capture_region(self):
        """Capture a rectangular region"""
        # Calculate region bounds
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # Minimum region size
        if width < 10 or height < 10:
            logging.warning("Region too small, treating as point capture")
            self._capture_point()
            return

        logging.info(f"Captured region: ({x1}, {y1}) {width}×{height}")

        # Create result
        self.result = {
            'mode': CaptureMode.REGION,
            'x': x1,
            'y': y1,
            'width': width,
            'height': height,
            'screenshot': self.screenshot,
            'success': True
        }

        # Close overlay and call callback
        self._finish_capture()

    def _finish_capture(self):
        """Finish capture and cleanup"""
        # Hide overlay
        self.overlay.grab_release()
        self.overlay.destroy()

        # Call callback with result
        if self.callback and self.result:
            self.callback(self.result)

    def _on_cancel(self, event=None):
        """Cancel capture"""
        logging.info("Capture cancelled")

        self.result = {
            'success': False,
            'cancelled': True
        }

        self.overlay.grab_release()
        self.overlay.destroy()

        if self.callback:
            self.callback(self.result)


class CaptureConfirmDialog:
    """Dialog to confirm captured region with preview"""

    def __init__(self, parent, capture_result: Dict[str, Any],
                 on_confirm: Callable, on_recapture: Callable, on_cancel: Callable):
        """
        Initialize confirmation dialog

        Args:
            parent: Parent window
            capture_result: Result from CaptureOverlay
            on_confirm: Callback when user confirms
            on_recapture: Callback when user wants to recapture
            on_cancel: Callback when user cancels
        """
        self.parent = parent
        self.capture_result = capture_result
        self.on_confirm = on_confirm
        self.on_recapture = on_recapture
        self.on_cancel = on_cancel

        self.dialog = None
        self.preview_label = None

    def show(self):
        """Show confirmation dialog"""
        from src.theme import ModernTheme

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Confirm Capture")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.configure(bg=ModernTheme.BACKGROUND)
        self.dialog.resizable(False, False)

        # Make modal
        self.dialog.grab_set()

        # Main container
        container = ttk.Frame(self.dialog, padding=20, style='Card.TFrame')
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(container, text="Confirm Screen Capture",
                         style='Title.TLabel',
                         font=(ModernTheme.FONT_FAMILY, 14, 'bold'))
        title.pack(pady=(0, 10))

        # Info
        mode = self.capture_result.get('mode', CaptureMode.POINT)
        if mode == CaptureMode.POINT:
            x = self.capture_result['x']
            y = self.capture_result['y']
            info_text = f"Captured point at ({x}, {y})"
        else:
            x = self.capture_result['x']
            y = self.capture_result['y']
            w = self.capture_result['width']
            h = self.capture_result['height']
            info_text = f"Captured region at ({x}, {y})\nSize: {w} × {h} pixels"

        info_label = ttk.Label(container, text=info_text,
                              style='Secondary.TLabel',
                              justify=tk.CENTER)
        info_label.pack(pady=(0, 15))

        # Preview frame
        preview_frame = ttk.Frame(container, style='Card.TFrame')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Generate preview image
        self._create_preview(preview_frame)

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="✓ Confirm",
                  command=self._handle_confirm,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        ttk.Button(button_frame, text="📸 Recapture",
                  command=self._handle_recapture,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        ttk.Button(button_frame, text="✕ Cancel",
                  command=self._handle_cancel,
                  style='Outline.TButton').pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Bind escape key
        self.dialog.bind('<Escape>', lambda e: self._handle_cancel())
        self.dialog.bind('<Return>', lambda e: self._handle_confirm())

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_preview(self, parent):
        """Create preview of captured region"""
        screenshot = self.capture_result['screenshot']
        mode = self.capture_result.get('mode', CaptureMode.POINT)

        if mode == CaptureMode.POINT:
            # Show point with context (100x100 region around point)
            x = self.capture_result['x']
            y = self.capture_result['y']

            # Calculate region bounds
            context_size = 100
            x1 = max(0, x - context_size // 2)
            y1 = max(0, y - context_size // 2)
            x2 = min(screenshot.width, x1 + context_size)
            y2 = min(screenshot.height, y1 + context_size)

            # Crop region
            preview = screenshot.crop((x1, y1, x2, y2))

            # Draw crosshair at the captured point
            draw = ImageDraw.Draw(preview)
            local_x = x - x1
            local_y = y - y1
            size = 10

            # Draw crosshair
            draw.line([(local_x - size, local_y), (local_x + size, local_y)],
                     fill='red', width=2)
            draw.line([(local_x, local_y - size), (local_x, local_y + size)],
                     fill='red', width=2)
            # Draw circle
            draw.ellipse([(local_x - 5, local_y - 5), (local_x + 5, local_y + 5)],
                        outline='red', width=2)

        else:
            # Show captured region
            x = self.capture_result['x']
            y = self.capture_result['y']
            w = self.capture_result['width']
            h = self.capture_result['height']

            # Crop region
            preview = screenshot.crop((x, y, x + w, y + h))

            # Draw border
            draw = ImageDraw.Draw(preview)
            draw.rectangle([(0, 0), (w - 1, h - 1)], outline='red', width=3)

        # Resize to fit preview area (max 400x200)
        preview.thumbnail((400, 200), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        preview_image = ImageTk.PhotoImage(preview)

        # Display in label
        self.preview_label = tk.Label(parent, image=preview_image, bg='black')
        self.preview_label.image = preview_image  # Keep reference
        self.preview_label.pack(expand=True)

    def _handle_confirm(self):
        """Handle confirm button"""
        self.dialog.grab_release()
        self.dialog.destroy()
        self.on_confirm(self.capture_result)

    def _handle_recapture(self):
        """Handle recapture button"""
        self.dialog.grab_release()
        self.dialog.destroy()
        self.on_recapture()

    def _handle_cancel(self):
        """Handle cancel button"""
        self.dialog.grab_release()
        self.dialog.destroy()
        self.on_cancel()


# Test code
if __name__ == "__main__":
    def on_capture(result):
        if result.get('success'):
            print(f"Captured: {result}")
        else:
            print("Capture cancelled")
        root.quit()

    root = tk.Tk()
    root.withdraw()

    # Test point capture
    overlay = CaptureOverlay(root, mode=CaptureMode.POINT, callback=on_capture)
    overlay.show()

    root.mainloop()
