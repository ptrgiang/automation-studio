"""
Simulation execution engine
"""
import pyautogui
import time
import logging
import copy
from typing import List, Dict, Any, Optional, Callable


class SimulationExecutor:
    """Executes simulation actions"""

    def __init__(self, stop_callback: Optional[Callable] = None,
                 pause_callback: Optional[Callable] = None,
                 status_callback: Optional[Callable] = None,
                 progress_callback: Optional[Callable] = None):
        """
        Initialize executor

        Args:
            stop_callback: Callback that returns True if simulation should stop
            pause_callback: Callback that returns True if simulation should pause
            status_callback: Callback to update status messages
            progress_callback: Callback to update progress (step_num, total, action_type, details)
        """
        self.stop_callback = stop_callback
        self.pause_callback = pause_callback
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        pyautogui.FAILSAFE = True

    def should_stop(self) -> bool:
        """Check if simulation should stop"""
        return self.stop_callback() if self.stop_callback else False

    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.pause_callback() if self.pause_callback else False

    def handle_pause(self):
        """Handle pause state - wait until unpaused or stopped"""
        while self.is_paused() and not self.should_stop():
            time.sleep(0.1)  # Check every 100ms

    def update_status(self, message: str):
        """Update status message"""
        if self.status_callback:
            self.status_callback(message)
        # Don't log here - let the callback handler do it to avoid duplicate logs

    def execute_action(self, action: Dict[str, Any], row_data: Dict[str, Any] = None):
        """
        Execute a single action

        Args:
            action: Action dictionary
            row_data: A dictionary representing a row of data for substitution.
        """
        if row_data is None:
            row_data = {}
        action_type = action['type']

        if action_type == 'click':
            self._execute_click(action)
        elif action_type == 'delete':
            self._execute_delete(action)
        elif action_type == 'type':
            self._execute_type(action, row_data)
        elif action_type == 'key_press':
            self._execute_key_press(action)
        elif action_type == 'set_value':
            self._execute_set_value(action, row_data)
        elif action_type == 'scroll':
            self._execute_scroll(action)
        elif action_type == 'wait':
            self._execute_wait(action)
        elif action_type == 'find_image':
            self._execute_find_image(action)
        elif action_type == 'move_mouse':
            self._execute_move_mouse(action)

        # Wait after action
        time.sleep(action.get('wait_after', 0.5))

    def _execute_click(self, action: Dict[str, Any]):
        """Execute click action"""
        if action.get('use_current_position'):
            pyautogui.click()
        else:
            pyautogui.click(action['x'], action['y'])

    def _execute_delete(self, action: Dict[str, Any]):
        """Execute delete action"""
        method = action.get('method', 'ctrl_a')

        if method == 'ctrl_a':
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
        elif method == 'backspace':
            for _ in range(50):
                pyautogui.press('backspace')
                time.sleep(0.01)
        elif method == 'triple_click':
            pyautogui.click(clicks=3)
            time.sleep(0.2)
            pyautogui.press('delete')

    def _replace_placeholders(self, text: str, row_data: Dict[str, Any]) -> str:
        """Replace placeholders in a string with data from a row."""
        import re
        
        def replace_match(match):
            column_name = match.group(1)
            return str(row_data.get(column_name, match.group(0)))

        return re.sub(r'{batch:(\w+)}', replace_match, text)

    def _execute_type(self, action: Dict[str, Any], row_data: Dict[str, Any]):
        """Execute type action"""
        text = self._replace_placeholders(action['text'], row_data)
        interval = action.get('interval', 0.1)
        pyautogui.write(text, interval=interval)

    def _execute_key_press(self, action: Dict[str, Any]):
        """Execute key press action"""
        key = action.get('key', 'enter')
        pyautogui.press(key)
        logging.info(f"Pressed key: {key}")

    def _execute_set_value(self, action: Dict[str, Any], row_data: Dict[str, Any]):
        """Execute set_value action (click + delete + type)"""
        # Click
        if action.get('use_current_position', False):
            pyautogui.click()
            time.sleep(0.3)
        else:
            pyautogui.click(action['x'], action['y'])
            time.sleep(0.3)

        # Delete existing value
        method = action.get('method', 'ctrl_a')
        if method == 'ctrl_a':
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
        elif method == 'triple_click':
            pyautogui.click(clicks=3)
            time.sleep(0.2)
            pyautogui.press('delete')

        time.sleep(0.3)

        # Type new value
        value = self._replace_placeholders(action['value'], row_data)
        pyautogui.write(value, interval=0.1)

    def _execute_scroll(self, action: Dict[str, Any]):
        """Execute scroll action"""
        scroll_type = action.get('scroll_type', 'amount')

        if scroll_type == 'amount':
            pyautogui.scroll(action['amount'])
        elif scroll_type == 'top':
            for _ in range(10):
                pyautogui.press('home')
                time.sleep(0.1)
        elif scroll_type == 'bottom':
            for _ in range(10):
                pyautogui.press('end')
                time.sleep(0.1)

    def _execute_wait(self, action: Dict[str, Any]):
        """Execute wait action"""
        wait_type = action.get('wait_type', 'duration')

        if wait_type == 'image':
            self._wait_for_image(action)
        else:
            time.sleep(action.get('duration', 1.0))

    def _wait_for_image(self, action: Dict[str, Any]):
        """Wait for image to appear on screen"""
        image_path = action['image_path']
        timeout = action.get('timeout', 30)
        check_interval = action.get('check_interval', 0.5)
        confidence = action.get('confidence', 0.8)

        elapsed = 0
        found = False

        while elapsed < timeout:
            if self.should_stop():
                break

            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    found = True
                    logging.info(f"Wait: Image '{action.get('image_name')}' found after {elapsed}s")
                    break
            except:
                pass

            time.sleep(check_interval)
            elapsed += check_interval

        if not found and not self.should_stop():
            logging.warning(f"Wait: Image '{action.get('image_name')}' not found after {timeout}s timeout")

    def _execute_find_image(self, action: Dict[str, Any]):
        """Execute find_image action"""
        image_path = action['image_path']
        confidence = action.get('confidence', 0.8)
        click_after = action.get('click_after', False)

        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.moveTo(center.x, center.y)
                logging.info(f"Found image at ({center.x}, {center.y})")

                if click_after:
                    time.sleep(0.3)
                    pyautogui.click()
                    logging.info(f"Clicked at ({center.x}, {center.y})")
            else:
                logging.warning(f"Image not found: {image_path}")
        except Exception as e:
            logging.error(f"Error finding image: {str(e)}")

    def _execute_move_mouse(self, action: Dict[str, Any]):
        """Execute move_mouse action"""
        current_pos = pyautogui.position()
        direction = action['direction']
        distance = action['distance']

        if direction == 'up':
            pyautogui.moveTo(current_pos.x, current_pos.y - distance)
        elif direction == 'down':
            pyautogui.moveTo(current_pos.x, current_pos.y + distance)
        elif direction == 'left':
            pyautogui.moveTo(current_pos.x - distance, current_pos.y)
        elif direction == 'right':
            pyautogui.moveTo(current_pos.x + distance, current_pos.y)

    def _get_action_details(self, action: Dict[str, Any], row_data: Dict[str, Any] = None) -> str:
        """Get formatted details string for an action"""
        if row_data is None:
            row_data = {}
        action_type = action['type']

        if action_type == 'click':
            if action.get('use_current_position'):
                return "at current position"
            return f"at ({action.get('x')}, {action.get('y')})"

        elif action_type == 'type':
            text = self._replace_placeholders(action.get('text', ''), row_data)
            return f'"{text[:40]}"'

        elif action_type == 'key_press':
            key = action.get('key', 'enter')
            return f"{key.upper()}"

        elif action_type == 'set_value':
            value = self._replace_placeholders(action.get('value', ''), row_data)
            return f'= "{value[:30]}"'

        elif action_type == 'scroll':
            scroll_type = action.get('scroll_type', 'amount')
            if scroll_type == 'amount':
                return f"{action.get('amount')} pixels"
            return f"to {scroll_type}"

        elif action_type == 'wait':
            wait_type = action.get('wait_type', 'duration')
            if wait_type == 'duration':
                return f"{action.get('duration')}s"
            return f"for {action.get('image_name')}"

        elif action_type == 'find_image':
            return f"{action.get('image_name')}"

        elif action_type == 'move_mouse':
            return f"{action.get('direction')} {action.get('distance')}px"

        elif action_type == 'delete':
            return f"({action.get('method')})"

        return ""

    def execute_simulation(self, actions: List[Dict[str, Any]], row_data: Dict[str, Any] = None) -> bool:
        """
        Execute complete simulation

        Args:
            actions: List of action dictionaries
            row_data: A dictionary representing a row of data for substitution.

        Returns:
            True if completed successfully, False if stopped
        """
        if row_data is None:
            row_data = {}
        try:
            logging.info(f"Executor received {len(actions)} actions to execute")
            self.update_status(f"Playing simulation... (Press S to stop, P to pause)")

            for i, action in enumerate(actions, 1):
                logging.info(f"Processing action {i}/{len(actions)}: {action['type']}")

                # Check for pause
                if self.is_paused():
                    self.handle_pause()

                # Check for stop
                if self.should_stop():
                    self.update_status(f"⏹ Simulation stopped at step {i}/{len(actions)}")
                    return False

                # Skip disabled steps
                if not action.get('enabled', True):
                    self.update_status(f"[{i}/{len(actions)}] SKIPPED (disabled): {action['type'].upper()}")
                    logging.info(f"Skipped disabled action {i}")
                    continue

                self.update_status(f"[{i}/{len(actions)}] {action['type'].upper()}: {action.get('description', '')}")

                # Update progress callback if provided
                if self.progress_callback:
                    current_action_details = self._get_action_details(action, row_data)
                    next_action_details = ""
                    if i < len(actions):
                        next_action_details = self._get_action_details(actions[i], row_data)
                    
                    self.progress_callback(
                        f"Step {i}/{len(actions)}: {action['type'].upper()} {current_action_details}",
                        f"Next: {actions[i]['type'].upper()} {next_action_details}" if i < len(actions) else "Finish"
                    )

                logging.info(f"Executing action {i}: {action['type']}")
                self.execute_action(action, row_data)
                logging.info(f"Completed action {i}")

            self.update_status(f"✓ Completed")
            return True

        except Exception as e:
            self.update_status(f"✗ Error: {str(e)}")
            logging.error(f"Simulation error: {str(e)}")
            return False

    def execute_batch(self, actions: List[Dict[str, Any]], data: List[Dict[str, Any]],
                     delay_between: float = 2.0) -> Dict[str, int]:
        """
        Execute simulation for multiple items.

        Args:
            actions: List of action dictionaries
            data: List of dictionaries, where each dictionary represents a row of data.
            delay_between: Delay between executions

        Returns:
            Dictionary with success_count and total_count
        """
        success_count = 0

        for i, row_data in enumerate(data, 1):
            if self.should_stop():
                self.update_status(f"⏹ Batch stopped at item {i}/{len(data)}")
                return {"success_count": success_count, "total_count": i - 1}

            self.update_status(f"Batch [{i}/{len(data)}]")

            if self.execute_simulation(copy.deepcopy(actions), row_data):
                success_count += 1

            if self.should_stop():
                return {"success_count": success_count, "total_count": i}

            if i < len(data):
                time.sleep(delay_between)

        self.update_status(f"✓ Batch complete: {success_count}/{len(data)} successful")
        return {"success_count": success_count, "total_count": len(data)}
