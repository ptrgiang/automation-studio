"""
Action Recorder - Real-time action recording system
Captures user interactions (mouse, keyboard) and converts them to actions
"""
import threading
import time
import logging
from typing import Optional, Callable, List, Dict, Any
from enum import Enum
from pynput import mouse, keyboard
import pyautogui
from PIL import ImageGrab
from src.action_schema import EnhancedAction
from src.screenshot_manager import ScreenshotManager


class RecordingState(Enum):
    """Recording states"""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"


class RecordedEvent:
    """Represents a recorded user event"""

    def __init__(self, event_type: str, **kwargs):
        self.event_type = event_type  # 'click', 'type', 'scroll', 'key'
        self.timestamp = time.time()
        self.data = kwargs

    def __repr__(self):
        return f"RecordedEvent({self.event_type}, {self.data})"


class ActionRecorder:
    """Records user actions in real-time"""

    def __init__(self, screenshot_manager: ScreenshotManager,
                 on_action_recorded: Optional[Callable] = None,
                 on_state_change: Optional[Callable] = None):
        """
        Initialize action recorder

        Args:
            screenshot_manager: Manager for capturing screenshots
            on_action_recorded: Callback when action is recorded (action)
            on_state_change: Callback when recording state changes (state)
        """
        self.screenshot_manager = screenshot_manager
        self.on_action_recorded = on_action_recorded
        self.on_state_change = on_state_change

        # Recording state
        self.state = RecordingState.IDLE
        self.recorded_events: List[RecordedEvent] = []
        self.actions: List[EnhancedAction] = []

        # Event listeners
        self.mouse_listener = None
        self.keyboard_listener = None

        # Recording settings
        self.capture_screenshots = True
        self.merge_similar_actions = True
        self.min_action_interval = 0.5  # Minimum time between actions (seconds)

        # Tracking
        self.last_action_time = 0
        self.last_mouse_pos = (0, 0)
        self.typing_buffer = ""
        self.typing_timeout = 1.0  # Time to wait before flushing typing buffer
        self.last_type_time = 0

        # Control keys
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False

        # Typing timer
        self.typing_timer = None

        logging.info("ActionRecorder initialized")

    def start_recording(self):
        """Start recording user actions"""
        if self.state != RecordingState.IDLE:
            logging.warning("Already recording or paused")
            return

        self.state = RecordingState.RECORDING
        self.recorded_events.clear()
        self.actions.clear()
        self.typing_buffer = ""
        self.last_action_time = time.time()

        # Start listeners
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()

        self._trigger_state_change(RecordingState.RECORDING)
        logging.info("Recording started")

    def pause_recording(self):
        """Pause recording"""
        if self.state != RecordingState.RECORDING:
            return

        self.state = RecordingState.PAUSED
        self._flush_typing_buffer()
        self._trigger_state_change(RecordingState.PAUSED)
        logging.info("Recording paused")

    def resume_recording(self):
        """Resume recording"""
        if self.state != RecordingState.PAUSED:
            return

        self.state = RecordingState.RECORDING
        self.last_action_time = time.time()
        self._trigger_state_change(RecordingState.RECORDING)
        logging.info("Recording resumed")

    def stop_recording(self) -> List[EnhancedAction]:
        """Stop recording and return recorded actions"""
        if self.state == RecordingState.IDLE:
            return []

        self.state = RecordingState.STOPPED

        # Flush any remaining typing
        self._flush_typing_buffer()

        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        # Cancel typing timer
        if self.typing_timer:
            self.typing_timer.cancel()
            self.typing_timer = None

        self._trigger_state_change(RecordingState.STOPPED)

        # Process and optimize actions
        if self.merge_similar_actions:
            self._optimize_actions()

        self.state = RecordingState.IDLE
        logging.info(f"Recording stopped. Recorded {len(self.actions)} actions")

        return self.actions.copy()

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click event"""
        if self.state != RecordingState.RECORDING:
            return

        # Only record button press (not release)
        if not pressed:
            return

        # Only record left clicks
        if button != mouse.Button.left:
            return

        # Check minimum interval
        current_time = time.time()
        if current_time - self.last_action_time < self.min_action_interval:
            return

        # Flush any pending typing
        self._flush_typing_buffer()

        # Record click event
        event = RecordedEvent('click', x=x, y=y, button=str(button))
        self.recorded_events.append(event)

        # Create action
        self._create_click_action(x, y)

        self.last_action_time = current_time
        self.last_mouse_pos = (x, y)

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll event"""
        if self.state != RecordingState.RECORDING:
            return

        # Check minimum interval
        current_time = time.time()
        if current_time - self.last_action_time < self.min_action_interval:
            return

        # Flush any pending typing
        self._flush_typing_buffer()

        # Calculate scroll amount (negative dy means scroll down)
        scroll_amount = int(dy * -100)  # Scale for better UX

        # Record scroll event
        event = RecordedEvent('scroll', x=x, y=y, dx=dx, dy=dy, amount=scroll_amount)
        self.recorded_events.append(event)

        # Create action
        self._create_scroll_action(scroll_amount)

        self.last_action_time = current_time

    def _on_key_press(self, key):
        """Handle key press event"""
        if self.state != RecordingState.RECORDING:
            return

        try:
            # Track modifier keys
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
                return
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.shift_pressed = True
                return
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = True
                return

            # Ignore other special keys for typing
            if hasattr(key, 'char') and key.char:
                # Regular character
                self.typing_buffer += key.char
                self.last_type_time = time.time()

                # Reset typing timer
                if self.typing_timer:
                    self.typing_timer.cancel()

                self.typing_timer = threading.Timer(
                    self.typing_timeout,
                    self._flush_typing_buffer
                )
                self.typing_timer.start()

            elif key == keyboard.Key.space:
                self.typing_buffer += ' '
                self.last_type_time = time.time()

            elif key == keyboard.Key.enter:
                # Flush typing and record enter as separate action
                self._flush_typing_buffer()
                # Could record Enter key press if needed

            elif key == keyboard.Key.backspace:
                if self.typing_buffer:
                    self.typing_buffer = self.typing_buffer[:-1]
                    self.last_type_time = time.time()

        except AttributeError:
            # Special key without char attribute
            pass

    def _on_key_release(self, key):
        """Handle key release event"""
        # Track modifier keys
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            self.shift_pressed = False
        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = False

    def _flush_typing_buffer(self):
        """Flush typing buffer and create type action"""
        if not self.typing_buffer.strip():
            self.typing_buffer = ""
            return

        # Create type action
        text = self.typing_buffer
        self.typing_buffer = ""

        # Cancel timer if exists
        if self.typing_timer:
            self.typing_timer.cancel()
            self.typing_timer = None

        self._create_type_action(text)

    def _create_click_action(self, x: int, y: int):
        """Create click action with screenshot"""
        action = EnhancedAction('click', x=x, y=y,
                               description=f"Click at ({x}, {y})")

        # Capture screenshot if enabled
        if self.capture_screenshots:
            try:
                # Capture point with context
                full_path, region_path, region_dict = \
                    self.screenshot_manager.capture_point_with_context(x, y, context_size=100)

                # Create thumbnail
                thumb_path = self.screenshot_manager.create_thumbnail(region_path)

                # Add visual metadata
                action.visual.screenshot_path = full_path
                action.visual.capture_region = region_dict
                action.visual.thumbnail_path = thumb_path
                action.visual.screen_resolution = self.screenshot_manager.get_screen_resolution()

            except Exception as e:
                logging.warning(f"Failed to capture screenshot for click: {e}")

        action.ui.order = len(self.actions)
        self.actions.append(action)

        # Trigger callback
        if self.on_action_recorded:
            self.on_action_recorded(action)

        logging.info(f"Recorded click action at ({x}, {y})")

    def _create_type_action(self, text: str):
        """Create type action"""
        action = EnhancedAction('type', text=text,
                               description=f"Type: {text[:30]}{'...' if len(text) > 30 else ''}")

        action.ui.order = len(self.actions)
        self.actions.append(action)

        # Trigger callback
        if self.on_action_recorded:
            self.on_action_recorded(action)

        logging.info(f"Recorded type action: {text[:50]}")

    def _create_scroll_action(self, amount: int):
        """Create scroll action"""
        action = EnhancedAction('scroll', scroll_type='amount', amount=amount,
                               description=f"Scroll {amount}")

        action.ui.order = len(self.actions)
        self.actions.append(action)

        # Trigger callback
        if self.on_action_recorded:
            self.on_action_recorded(action)

        logging.info(f"Recorded scroll action: {amount}")

    def _optimize_actions(self):
        """Optimize recorded actions by merging similar ones"""
        if len(self.actions) < 2:
            return

        optimized = []
        i = 0

        while i < len(self.actions):
            current = self.actions[i]

            # Check if next action can be merged
            if i + 1 < len(self.actions):
                next_action = self.actions[i + 1]

                # Merge consecutive type actions
                if current.type == 'type' and next_action.type == 'type':
                    merged_text = current.params.get('text', '') + next_action.params.get('text', '')
                    current.params['text'] = merged_text
                    current.params['description'] = f"Type: {merged_text[:30]}{'...' if len(merged_text) > 30 else ''}"
                    i += 1  # Skip next action

                # Merge consecutive scrolls in same direction
                elif current.type == 'scroll' and next_action.type == 'scroll':
                    if current.params.get('scroll_type') == 'amount' and \
                       next_action.params.get('scroll_type') == 'amount':
                        total_amount = current.params.get('amount', 0) + next_action.params.get('amount', 0)
                        current.params['amount'] = total_amount
                        current.params['description'] = f"Scroll {total_amount}"
                        i += 1  # Skip next action

            optimized.append(current)
            i += 1

        # Update action orders
        for idx, action in enumerate(optimized):
            action.ui.order = idx

        self.actions = optimized
        logging.info(f"Optimized actions: {len(self.actions)} actions remaining")

    def _trigger_state_change(self, new_state: RecordingState):
        """Trigger state change callback"""
        if self.on_state_change:
            self.on_state_change(new_state)

    def get_state(self) -> RecordingState:
        """Get current recording state"""
        return self.state

    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.state == RecordingState.RECORDING

    def is_paused(self) -> bool:
        """Check if paused"""
        return self.state == RecordingState.PAUSED

    def get_recorded_count(self) -> int:
        """Get number of recorded actions"""
        return len(self.actions)


# Test code
if __name__ == "__main__":
    from src.screenshot_manager import ScreenshotManager

    print("Action Recorder Test")
    print("====================")
    print("Recording will start in 3 seconds...")
    print("Perform some actions (clicks, typing, scrolling)")
    print("Recording will stop after 10 seconds")
    print()

    screenshot_mgr = ScreenshotManager()

    def on_action(action):
        print(f"✓ Recorded: {action.type} - {action.get_summary()}")

    def on_state(state):
        print(f"State changed: {state.value}")

    recorder = ActionRecorder(screenshot_mgr, on_action_recorded=on_action, on_state_change=on_state)

    time.sleep(3)
    recorder.start_recording()

    time.sleep(10)

    actions = recorder.stop_recording()

    print()
    print(f"Recording complete! Captured {len(actions)} actions:")
    for i, action in enumerate(actions):
        print(f"  {i+1}. {action.type}: {action.get_summary()}")
