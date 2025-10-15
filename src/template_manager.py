"""
Template manager for handling workflow templates.
"""
from tkinter import messagebox, Toplevel, Label, Frame, Listbox, Button, END
from src.theme import ModernTheme, Icons
from src.workflow_templates import TemplateManager as CoreTemplateManager

class TemplateManager:
    def __init__(self, app):
        self.app = app
        self.core_manager = CoreTemplateManager()

    def insert_template(self):
        """Insert template workflow"""
        templates = self.core_manager.get_all_templates()
        if not templates:
            messagebox.showinfo("No Templates", "No templates available")
            return

        dialog = Toplevel(self.app.root)
        dialog.title("Insert Template")
        dialog.geometry("500x400")
        dialog.transient(self.app.root)
        dialog.grab_set()

        header = Label(dialog, text="📋 Select Template",
                         font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                         bg=ModernTheme.PRIMARY, fg='white', pady=15)
        header.pack(fill='x')

        list_frame = Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
        list_frame.pack(fill='both', expand=True)

        listbox = Listbox(list_frame, font=(ModernTheme.FONT_FAMILY, 10),
                            height=10, bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT)
        listbox.pack(fill='both', expand=True)

        template_ids = list(templates.keys())
        for template_id in template_ids:
            template = templates[template_id]
            listbox.insert(END, f"{template.name} ({template.category})")

        desc_label = Label(list_frame, text="",
                             font=(ModernTheme.FONT_FAMILY, 9),
                             bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT_SECONDARY,
                             justify='left', wraplength=450)
        desc_label.pack(pady=(10, 0))

        def on_select(event):
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                template = templates[template_ids[idx]]
                desc_label.config(text=template.description)

        listbox.bind('<<ListboxSelect>>', on_select)

        button_frame = Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=15)
        button_frame.pack(fill='x')

        def insert():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                template = templates[template_ids[idx]]
                actions = template.create_actions()

                for action in actions:
                    action.ui.order = len(self.app.actions)
                    self.app.actions.append(action)

                self.app._refresh_workflow()
                self.app.update_status(f"Inserted template: {template.name}")
                dialog.destroy()

        Button(button_frame, text="Insert", command=insert).pack(side='right', padx=(5, 0))
        Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='right')

    def save_as_template(self):
        """Save current workflow as template"""
        if not self.app.actions:
            messagebox.showwarning("No Actions", "No actions to save as template")
            return

        from src.gui_modern import ModernDialog

        result = ModernDialog.create_input_dialog(self.app.root, "Save as Template", [
            {'name': 'name', 'label': 'Template Name:', 'type': 'text', 'default': ''},
            {'name': 'category', 'label': 'Category:', 'type': 'text', 'default': 'Custom'},
            {'name': 'description', 'label': 'Description:', 'type': 'text', 'default': ''}
        ])

        if result and result['name']:
            template = self.core_manager.create_template_from_workflow(
                name=result['name'],
                description=result['description'] or 'Custom workflow template',
                category=result['category'] or 'Custom',
                actions=self.app.actions
            )

            template_id = result['name'].lower().replace(' ', '_')
            self.core_manager.save_custom_template(template_id, template)

            messagebox.showinfo("Success", f"Template '{result['name']}' saved!")

    def browse_templates(self):
        """Browse available templates"""
        templates = self.core_manager.get_all_templates()

        dialog = Toplevel(self.app.root)
        dialog.title("Template Browser")
        dialog.geometry("600x500")
        dialog.transient(self.app.root)

        header = Label(dialog, text="📚 Template Browser",
                         font=(ModernTheme.FONT_FAMILY, 14, 'bold'),
                         bg=ModernTheme.PRIMARY, fg='white', pady=15)
        header.pack(fill='x')

        content = Frame(dialog, bg=ModernTheme.BACKGROUND, padx=20, pady=20)
        content.pack(fill='both', expand=True)

        categories = self.core_manager.get_categories()
        for category in categories:
            cat_label = Label(content, text=category,
                                font=(ModernTheme.FONT_FAMILY, 12, 'bold'),
                                bg=ModernTheme.BACKGROUND, fg=ModernTheme.TEXT)
            cat_label.pack(anchor='w', pady=(10, 5))

            cat_templates = self.core_manager.get_templates_by_category(category)
            for template in cat_templates:
                template_frame = Frame(content, bg=ModernTheme.SURFACE,
                                         relief='solid', borderwidth=1)
                template_frame.pack(fill='x', pady=2)

                Label(template_frame, text=template.name,
                        font=(ModernTheme.FONT_FAMILY, 10, 'bold'),
                        bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT).pack(anchor='w', padx=10, pady=(5, 0))

                Label(template_frame, text=template.description,
                        font=(ModernTheme.FONT_FAMILY, 9),
                        bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_SECONDARY,
                        wraplength=550, justify='left').pack(anchor='w', padx=10, pady=(2, 5))

        Button(content, text="Close", command=dialog.destroy).pack(pady=(20, 0))
