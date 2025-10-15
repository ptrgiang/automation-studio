"""
Enhanced Action Schema for Automation Studio
Supports both classic and visual automation modes with backward compatibility
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json


class VisualMetadata:
    """Visual metadata for an action"""

    def __init__(self, screenshot_path: Optional[str] = None,
                 capture_region: Optional[Dict[str, int]] = None,
                 thumbnail_path: Optional[str] = None,
                 screen_resolution: Optional[Dict[str, int]] = None):
        self.screenshot_path = screenshot_path
        self.capture_region = capture_region or {}
        self.thumbnail_path = thumbnail_path
        self.screen_resolution = screen_resolution or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'screenshot_path': self.screenshot_path,
            'capture_region': self.capture_region,
            'thumbnail_path': self.thumbnail_path,
            'screen_resolution': self.screen_resolution
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualMetadata':
        """Create from dictionary"""
        return cls(
            screenshot_path=data.get('screenshot_path'),
            capture_region=data.get('capture_region', {}),
            thumbnail_path=data.get('thumbnail_path'),
            screen_resolution=data.get('screen_resolution', {})
        )


class UIMetadata:
    """UI presentation metadata for an action"""

    # Color scheme for different action types
    ACTION_COLORS = {
        'click': '#4A90E2',       # Blue
        'type': '#50C878',        # Green
        'key_press': '#2ECC71',   # Bright Green
        'set_value': '#50C878',   # Green
        'wait': '#FFA500',        # Orange
        'find_image': '#9B59B6',  # Purple
        'scroll': '#34495E',      # Gray
        'delete': '#E74C3C',      # Red
        'move_mouse': '#3498DB'   # Light Blue
    }

    # Icons for different action types
    ACTION_ICONS = {
        'click': '🖱️',
        'type': '📝',
        'key_press': '⌨️',
        'set_value': '✏️',
        'wait': '⏸️',
        'find_image': '🖼️',
        'scroll': '📜',
        'delete': '🗑️',
        'move_mouse': '↔️'
    }

    def __init__(self, color: Optional[str] = None,
                 order: int = 0,
                 collapsed: bool = False,
                 icon: Optional[str] = None):
        self.color = color
        self.order = order
        self.collapsed = collapsed
        self.icon = icon

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'color': self.color,
            'order': self.order,
            'collapsed': self.collapsed,
            'icon': self.icon
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIMetadata':
        """Create from dictionary"""
        return cls(
            color=data.get('color'),
            order=data.get('order', 0),
            collapsed=data.get('collapsed', False),
            icon=data.get('icon')
        )

    @classmethod
    def get_color_for_action(cls, action_type: str) -> str:
        """Get default color for action type"""
        return cls.ACTION_COLORS.get(action_type, '#95A5A6')

    @classmethod
    def get_icon_for_action(cls, action_type: str) -> str:
        """Get default icon for action type"""
        return cls.ACTION_ICONS.get(action_type, '⚙️')


class EnhancedAction:
    """Enhanced action model with visual and UI metadata"""

    def __init__(self, action_type: str, **kwargs):
        """
        Initialize enhanced action

        Args:
            action_type: Type of action (click, type, wait, etc.)
            **kwargs: Action-specific parameters and metadata
        """
        self.type = action_type
        self.description = kwargs.get('description', '')
        self.enabled = kwargs.get('enabled', True)
        self.wait_after = kwargs.get('wait_after', 0.5)

        # Store action-specific parameters
        self.params = {k: v for k, v in kwargs.items()
                      if k not in ['description', 'enabled', 'wait_after', 'visual', 'ui']}

        # Visual metadata
        visual_data = kwargs.get('visual', {})
        if isinstance(visual_data, dict):
            self.visual = VisualMetadata.from_dict(visual_data)
        else:
            self.visual = visual_data or VisualMetadata()

        # UI metadata
        ui_data = kwargs.get('ui', {})
        if isinstance(ui_data, dict):
            self.ui = UIMetadata.from_dict(ui_data)
        else:
            self.ui = ui_data or UIMetadata()

        # Set default color and icon if not provided
        if not self.ui.color:
            self.ui.color = UIMetadata.get_color_for_action(action_type)
        if not self.ui.icon:
            self.ui.icon = UIMetadata.get_icon_for_action(action_type)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            'type': self.type,
            'description': self.description,
            'enabled': self.enabled,
            'wait_after': self.wait_after,
            **self.params
        }

        # Add visual metadata if it exists
        if self.visual.screenshot_path or self.visual.capture_region:
            result['visual'] = self.visual.to_dict()

        # Add UI metadata
        result['ui'] = self.ui.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedAction':
        """Create from dictionary (backward compatible with classic actions)"""
        return cls(data['type'], **data)

    def has_visual_data(self) -> bool:
        """Check if action has visual metadata"""
        return bool(self.visual.screenshot_path or self.visual.capture_region)

    def get_summary(self) -> str:
        """Get human-readable summary of action"""
        if self.description:
            return self.description

        # Generate smart summary based on action type
        if self.type == 'click':
            if self.params.get('use_current_position'):
                return "Click at current position"
            return f"Click at ({self.params.get('x')}, {self.params.get('y')})"

        elif self.type == 'type':
            text = self.params.get('text', '')
            return f"Type: {text[:40]}{'...' if len(text) > 40 else ''}"

        elif self.type == 'key_press':
            key = self.params.get('key', 'enter')
            return f"Press {key.upper()}"

        elif self.type == 'set_value':
            value = self.params.get('value', '')
            x = self.params.get('x')
            y = self.params.get('y')
            if x is not None and y is not None:
                return f"Set value at ({x}, {y})"
            return f"Set value: {value[:30]}{'...' if len(value) > 30 else ''}"

        elif self.type == 'wait':
            wait_type = self.params.get('wait_type', 'duration')
            if wait_type == 'duration':
                return f"Wait {self.params.get('duration', 1.0)}s"
            return f"Wait for {self.params.get('image_name', 'image')}"

        elif self.type == 'find_image':
            return f"Find image: {self.params.get('image_name', 'unknown')}"

        elif self.type == 'scroll':
            scroll_type = self.params.get('scroll_type', 'amount')
            if scroll_type == 'amount':
                return f"Scroll {self.params.get('amount', 0)} pixels"
            return f"Scroll to {scroll_type}"

        elif self.type == 'delete':
            return f"Delete field ({self.params.get('method', 'ctrl_a')})"

        elif self.type == 'move_mouse':
            return f"Move mouse {self.params.get('direction', '')} {self.params.get('distance', 0)}px"

        return self.type.upper()


class ActionSchemaManager:
    """Manager for handling action schema conversions and migrations"""

    @staticmethod
    def classic_to_enhanced(classic_action: Dict[str, Any]) -> EnhancedAction:
        """Convert classic action format to enhanced format"""
        return EnhancedAction.from_dict(classic_action)

    @staticmethod
    def enhanced_to_classic(enhanced_action: EnhancedAction) -> Dict[str, Any]:
        """Convert enhanced action to classic format (removes visual/ui metadata)"""
        data = enhanced_action.to_dict()
        # Remove enhanced fields for backward compatibility
        data.pop('visual', None)
        data.pop('ui', None)
        return data

    @staticmethod
    def migrate_simulation(actions: list) -> list:
        """Migrate a list of classic actions to enhanced format"""
        enhanced_actions = []
        for i, action in enumerate(actions):
            enhanced = ActionSchemaManager.classic_to_enhanced(action)
            enhanced.ui.order = i  # Set explicit order
            enhanced_actions.append(enhanced)
        return enhanced_actions

    @staticmethod
    def export_simulation(enhanced_actions: list, include_visual: bool = True) -> list:
        """Export enhanced actions to dictionary format"""
        result = []
        for action in enhanced_actions:
            if isinstance(action, EnhancedAction):
                data = action.to_dict()
                if not include_visual:
                    data.pop('visual', None)
                    data.pop('ui', None)
                result.append(data)
            else:
                # Already a dict
                result.append(action)
        return result

    @staticmethod
    def is_enhanced_format(action: Dict[str, Any]) -> bool:
        """Check if action uses enhanced format"""
        return 'visual' in action or 'ui' in action


# Example usage and testing
if __name__ == "__main__":
    # Create a classic action
    classic = {
        'type': 'click',
        'x': 100,
        'y': 200,
        'description': 'Click login button',
        'wait_after': 1.0,
        'enabled': True
    }

    # Convert to enhanced
    enhanced = EnhancedAction.from_dict(classic)
    print("Enhanced action:")
    print(json.dumps(enhanced.to_dict(), indent=2))

    # Add visual metadata
    enhanced.visual.screenshot_path = "screenshots/action_001.png"
    enhanced.visual.capture_region = {'x': 90, 'y': 190, 'width': 120, 'height': 40}

    print("\nWith visual metadata:")
    print(json.dumps(enhanced.to_dict(), indent=2))

    print("\nSummary:", enhanced.get_summary())
    print("Color:", enhanced.ui.color)
    print("Icon:", enhanced.ui.icon)
