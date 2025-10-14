"""
Action recording functionality
"""
import pyautogui
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from PIL import ImageGrab
from pathlib import Path


class ActionRecorder:
    """Records user actions into simulation steps"""

    def __init__(self, actions: List[Dict[str, Any]], images_dir: str = "images"):
        """
        Initialize recorder

        Args:
            actions: Reference to actions list to append to
            images_dir: Directory to save captured images
        """
        self.actions = actions
        self.images_dir = Path(images_dir)
        self.images_dir.mkdir(exist_ok=True)

    def record_click(self, description: str = "", wait_after: float = 1.0,
                    use_current: bool = False) -> Dict[str, Any]:
        """
        Record a click action

        Args:
            description: Action description
            wait_after: Wait time after action
            use_current: Use current mouse position instead of waiting for click

        Returns:
            Created action dictionary
        """
        if use_current:
            x, y = pyautogui.position()
        else:
            logging.info("Move mouse to position and click...")
            time.sleep(2)
            x, y = pyautogui.position()

        action = {
            "type": "click",
            "x": x,
            "y": y,
            "description": description,
            "wait_after": wait_after,
            "use_current_position": use_current
        }

        self.actions.append(action)
        return action

    def record_delete(self, method: str = "ctrl_a", description: str = "",
                     wait_after: float = 0.5) -> Dict[str, Any]:
        """Record a delete action"""
        action = {
            "type": "delete",
            "method": method,
            "description": description,
            "wait_after": wait_after,
            "enabled": True
        }

        self.actions.append(action)
        return action

    def record_type(self, text: str, interval: float = 0.1,
                   description: str = "", wait_after: float = 0.5) -> Dict[str, Any]:
        """Record a type action"""
        action = {
            "type": "type",
            "text": text,
            "interval": interval,
            "description": description,
            "wait_after": wait_after,
            "enabled": True
        }

        self.actions.append(action)
        return action

    def record_set_value(self, value: str, x: Optional[int] = None,
                        y: Optional[int] = None, method: str = "ctrl_a",
                        use_current: bool = False, description: str = "",
                        wait_after: float = 0.5) -> Dict[str, Any]:
        """Record a set_value action (click + delete + type)"""
        action = {
            "type": "set_value",
            "x": x,
            "y": y,
            "value": value,
            "method": method,
            "description": description,
            "wait_after": wait_after,
            "use_current_position": use_current,
            "enabled": True
        }

        self.actions.append(action)
        return action

    def record_scroll(self, scroll_type: str = "amount", amount: Optional[int] = None,
                     description: str = "", wait_after: float = 1.0) -> Dict[str, Any]:
        """Record a scroll action"""
        action = {
            "type": "scroll",
            "scroll_type": scroll_type,
            "amount": amount,
            "description": description,
            "wait_after": wait_after,
            "enabled": True
        }

        self.actions.append(action)
        return action

    def record_wait(self, wait_type: str = "duration", duration: float = 1.0,
                   image_name: Optional[str] = None, image_path: Optional[str] = None,
                   timeout: float = 30.0, check_interval: float = 0.5,
                   confidence: float = 0.8, description: str = "") -> Dict[str, Any]:
        """Record a wait action"""
        action = {
            "type": "wait",
            "wait_type": wait_type,
            "description": description
        }

        if wait_type == "image":
            action.update({
                "image_name": image_name,
                "image_path": image_path,
                "timeout": timeout,
                "check_interval": check_interval,
                "confidence": confidence
            })
        else:
            action["duration"] = duration

        self.actions.append(action)
        return action

    def record_find_image(self, image_name: str, image_path: str,
                         confidence: float = 0.9, click_after: bool = False,
                         description: str = "", wait_after: float = 1.0) -> Dict[str, Any]:
        """Record a find_image action"""
        action = {
            "type": "find_image",
            "image_name": image_name,
            "image_path": image_path,
            "description": description,
            "confidence": confidence,
            "click_after": click_after,
            "wait_after": wait_after,
            "enabled": True
        }

        self.actions.append(action)
        return action

    def record_move_mouse(self, direction: str, distance: int,
                         description: str = "", wait_after: float = 0.5) -> Dict[str, Any]:
        """Record a move_mouse action"""
        action = {
            "type": "move_mouse",
            "direction": direction,
            "distance": distance,
            "description": description,
            "wait_after": wait_after,
            "enabled": True
        }

        self.actions.append(action)
        return action

    def capture_screen_region(self, delay: float = 2.0) -> Optional[str]:
        """
        Capture a screen region for image recognition

        Args:
            delay: Time to wait before capture

        Returns:
            Path to saved image or None if cancelled
        """
        logging.info(f"Move mouse to target area. Capturing in {delay}s...")
        time.sleep(delay)

        # Get mouse position
        x, y = pyautogui.position()

        # Capture region around cursor (100x100 box)
        region = (x - 50, y - 50, x + 50, y + 50)

        try:
            screenshot = ImageGrab.grab(bbox=region)

            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            filepath = self.images_dir / filename

            screenshot.save(str(filepath))
            logging.info(f"Saved capture to {filepath}")

            return str(filepath)

        except Exception as e:
            logging.error(f"Error capturing screen: {str(e)}")
            return None

    def insert_action(self, action: Dict[str, Any], position: int):
        """Insert action at specific position"""
        if 0 <= position <= len(self.actions):
            self.actions.insert(position, action)
        else:
            self.actions.append(action)

    def delete_action(self, index: int) -> bool:
        """Delete action at index"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
            return True
        return False

    def toggle_action(self, index: int) -> bool:
        """Toggle action enabled state"""
        if 0 <= index < len(self.actions):
            self.actions[index]['enabled'] = not self.actions[index].get('enabled', True)
            return True
        return False

    def undo_last(self) -> bool:
        """Remove last recorded action"""
        if self.actions:
            self.actions.pop()
            return True
        return False

    def clear_all(self):
        """Clear all recorded actions"""
        self.actions.clear()
