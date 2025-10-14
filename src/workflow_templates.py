"""
Workflow Templates System
Pre-built templates for common automation tasks
"""
import json
from typing import List, Dict, Any
from pathlib import Path
from src.action_schema import EnhancedAction


class WorkflowTemplate:
    """Represents a workflow template"""

    def __init__(self, name: str, description: str, category: str, actions: List[Dict[str, Any]]):
        self.name = name
        self.description = description
        self.category = category
        self.actions = actions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'actions': self.actions
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WorkflowTemplate':
        """Create from dictionary"""
        return WorkflowTemplate(
            name=data['name'],
            description=data['description'],
            category=data['category'],
            actions=data['actions']
        )

    def create_actions(self) -> List[EnhancedAction]:
        """Create EnhancedAction objects from template"""
        return [EnhancedAction.from_dict(action_data) for action_data in self.actions]


class TemplateManager:
    """Manages workflow templates"""

    # Built-in templates
    BUILTIN_TEMPLATES = {
        'form_fill': WorkflowTemplate(
            name='Form Filling',
            description='Template for filling out web forms with multiple fields',
            category='Web Automation',
            actions=[
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 0, 'description': 'Click first field'},
                    'enabled': True
                },
                {
                    'type': 'type',
                    'params': {'text': '{VALUE1}', 'description': 'Enter first value'},
                    'enabled': True
                },
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 50, 'description': 'Click second field'},
                    'enabled': True
                },
                {
                    'type': 'type',
                    'params': {'text': '{VALUE2}', 'description': 'Enter second value'},
                    'enabled': True
                },
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 100, 'description': 'Click submit'},
                    'enabled': True
                }
            ]
        ),
        'login': WorkflowTemplate(
            name='Login Sequence',
            description='Standard login flow with username and password',
            category='Authentication',
            actions=[
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 0, 'description': 'Click username field'},
                    'enabled': True
                },
                {
                    'type': 'type',
                    'params': {'text': '{USERNAME}', 'description': 'Enter username'},
                    'enabled': True
                },
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 50, 'description': 'Click password field'},
                    'enabled': True
                },
                {
                    'type': 'type',
                    'params': {'text': '{PASSWORD}', 'description': 'Enter password'},
                    'enabled': True
                },
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 100, 'description': 'Click login button'},
                    'enabled': True
                },
                {
                    'type': 'wait',
                    'params': {'wait_type': 'duration', 'duration': 2.0, 'description': 'Wait for login'},
                    'enabled': True
                }
            ]
        ),
        'data_entry': WorkflowTemplate(
            name='Repetitive Data Entry',
            description='Template for entering data in multiple fields repeatedly',
            category='Data Entry',
            actions=[
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 0, 'description': 'Click field 1'},
                    'enabled': True
                },
                {
                    'type': 'set_value',
                    'params': {'x': 0, 'y': 0, 'value': '{DATA}', 'method': 'ctrl_a', 'description': 'Enter data'},
                    'enabled': True
                },
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 50, 'description': 'Click next button'},
                    'enabled': True
                },
                {
                    'type': 'wait',
                    'params': {'wait_type': 'duration', 'duration': 0.5, 'description': 'Wait'},
                    'enabled': True
                }
            ]
        ),
        'scroll_and_click': WorkflowTemplate(
            name='Scroll and Click Pattern',
            description='Scroll down and click elements in sequence',
            category='Navigation',
            actions=[
                {
                    'type': 'scroll',
                    'params': {'scroll_type': 'amount', 'amount': -300, 'description': 'Scroll down'},
                    'enabled': True
                },
                {
                    'type': 'wait',
                    'params': {'wait_type': 'duration', 'duration': 0.5, 'description': 'Wait for load'},
                    'enabled': True
                },
                {
                    'type': 'click',
                    'params': {'x': 0, 'y': 0, 'description': 'Click element'},
                    'enabled': True
                }
            ]
        ),
        'wait_and_verify': WorkflowTemplate(
            name='Wait and Verify',
            description='Wait for element to appear before continuing',
            category='Verification',
            actions=[
                {
                    'type': 'wait',
                    'params': {'wait_type': 'duration', 'duration': 2.0, 'description': 'Wait for page'},
                    'enabled': True
                },
                {
                    'type': 'find_image',
                    'params': {
                        'image_name': 'target_element',
                        'confidence': 0.8,
                        'description': 'Verify element exists'
                    },
                    'enabled': True
                }
            ]
        )
    }

    def __init__(self, custom_templates_path: str = 'templates'):
        """
        Initialize template manager

        Args:
            custom_templates_path: Path to custom templates directory
        """
        self.custom_templates_path = Path(custom_templates_path)
        self.custom_templates_path.mkdir(exist_ok=True)
        self.custom_templates: Dict[str, WorkflowTemplate] = {}
        self._load_custom_templates()

    def _load_custom_templates(self):
        """Load custom templates from disk"""
        for template_file in self.custom_templates_path.glob('*.json'):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = WorkflowTemplate.from_dict(data)
                    self.custom_templates[template_file.stem] = template
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

    def get_all_templates(self) -> Dict[str, WorkflowTemplate]:
        """Get all templates (built-in + custom)"""
        return {**self.BUILTIN_TEMPLATES, **self.custom_templates}

    def get_template(self, template_id: str) -> WorkflowTemplate:
        """Get specific template by ID"""
        all_templates = self.get_all_templates()
        return all_templates.get(template_id)

    def get_categories(self) -> List[str]:
        """Get all template categories"""
        categories = set()
        for template in self.get_all_templates().values():
            categories.add(template.category)
        return sorted(list(categories))

    def get_templates_by_category(self, category: str) -> List[WorkflowTemplate]:
        """Get templates in specific category"""
        return [t for t in self.get_all_templates().values() if t.category == category]

    def save_custom_template(self, template_id: str, template: WorkflowTemplate):
        """Save custom template to disk"""
        template_file = self.custom_templates_path / f"{template_id}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2)
        self.custom_templates[template_id] = template

    def delete_custom_template(self, template_id: str):
        """Delete custom template"""
        if template_id in self.custom_templates:
            template_file = self.custom_templates_path / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
            del self.custom_templates[template_id]

    def create_template_from_workflow(self, name: str, description: str,
                                      category: str, actions: List[EnhancedAction]) -> WorkflowTemplate:
        """Create template from existing workflow"""
        action_dicts = [action.to_dict() for action in actions]
        return WorkflowTemplate(name, description, category, action_dicts)


# Test code
if __name__ == "__main__":
    manager = TemplateManager()

    print("Available Templates:")
    print("=" * 50)

    for template_id, template in manager.get_all_templates().items():
        print(f"\nID: {template_id}")
        print(f"Name: {template.name}")
        print(f"Category: {template.category}")
        print(f"Description: {template.description}")
        print(f"Actions: {len(template.actions)}")

    print("\n\nCategories:")
    for category in manager.get_categories():
        print(f"  - {category}")
