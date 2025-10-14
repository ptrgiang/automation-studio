"""
GUI for managing multi-column batch data using column-based text panels.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import io
from src.theme import ModernTheme, Icons

class VariableManagerDialog(tk.Toplevel):
    """Dialog for managing a table of batch variables via column panels."""

    def __init__(self, parent, data: list, columns: list, on_save: callable):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Manage Batch Data")
        self.geometry("800x600")
        self.configure(bg=ModernTheme.BACKGROUND)

        self.data = [dict(row) for row in data]
        self.columns = list(columns)
        self.on_save = on_save

        if not self.columns:
            self.columns = ['column1']

        self.text_widgets = {}
        self._create_widgets()
        self._populate_panels()

    def _create_widgets(self):
        """Create all UI components."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="Batch Data", style='Title.TLabel').pack(side=tk.LEFT)

        # Column management buttons
        ttk.Button(header_frame, text=f"{Icons.PLUS} Add Column", command=self._add_column).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(header_frame, text=f"{Icons.DELETE} Delete Last Column", command=self._delete_column).pack(side=tk.RIGHT)

        # Panels Frame
        self.panels_frame = ttk.Frame(main_frame)
        self.panels_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # File and Save/Cancel buttons
        footer = ttk.Frame(main_frame)
        footer.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(footer, text=f"{Icons.FOLDER} Import CSV...", command=self._import_csv).pack(side=tk.LEFT)
        ttk.Button(footer, text=f"{Icons.SAVE} Export CSV...", command=self._export_csv).pack(side=tk.LEFT, padx=10)

        self.save_btn = ttk.Button(footer, text=f"{Icons.SAVE} Save and Close", command=self._save_and_close, style='Primary.TButton')
        self.save_btn.pack(side=tk.RIGHT)
        self.cancel_btn = ttk.Button(footer, text="Cancel", command=self.destroy)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def _populate_panels(self):
        """Create and fill the text panels for each column."""
        for widget in self.panels_frame.winfo_children():
            widget.destroy()
        self.text_widgets.clear()

        for col_name in self.columns:
            col_frame = ttk.Frame(self.panels_frame, padding=5)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            ttk.Label(col_frame, text=col_name, style='Heading.TLabel').pack(anchor=tk.W)
            
            text_widget = tk.Text(col_frame, width=20, font=(ModernTheme.FONT_FAMILY, 10),
                                  bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT,
                                  wrap=tk.NONE, borderwidth=1, relief=tk.SOLID)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            values = [str(row.get(col_name, '')) for row in self.data]
            text_widget.insert('1.0', '\n'.join(values))
            
            self.text_widgets[col_name] = text_widget

    def _add_column(self):
        """Add a new column."""
        from tkinter.simpledialog import askstring
        new_col_name = askstring("New Column", "Enter column name:", parent=self)
        if new_col_name and new_col_name not in self.columns:
            self.columns.append(new_col_name)
            self._populate_panels()
        elif new_col_name:
            messagebox.showerror("Error", "Column name already exists.", parent=self)

    def _delete_column(self):
        """Delete the last column."""
        if len(self.columns) > 1:
            if messagebox.askyesno("Delete Column", f"Delete last column '{self.columns[-1]}' التقليد؟", parent=self):
                self.columns.pop()
                self._populate_panels()
        else:
            messagebox.showwarning("Cannot Delete", "Cannot delete the last column.", parent=self)

    def _import_csv(self):
        """Load variables from a CSV file."""
        filepath = filedialog.askopenfilename(
            title="Import CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                new_data = [dict(zip(header, row)) for row in reader]

            if new_data:
                self.columns = header
                self.data = new_data
                self._populate_panels()
                messagebox.showinfo("Success", f"Loaded {len(new_data)} rows from CSV.", parent=self)
            else:
                messagebox.showwarning("Empty File", "The selected CSV file is empty or invalid.", parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV:\n{e}", parent=self)

    def _export_csv(self):
        """Export data to a CSV file."""
        self._parse_panels_to_data() # Ensure data is up-to-date
        if not self.data:
            messagebox.showwarning("No Data", "There is no data to export.", parent=self)
            return

        filepath = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.columns)
                writer.writeheader()
                writer.writerows(self.data)
            messagebox.showinfo("Success", "Data exported to CSV successfully.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{e}", parent=self)

    def _parse_panels_to_data(self):
        """Parse the text from panels and update self.data."""
        panel_data = {}
        max_rows = 0
        for col_name, text_widget in self.text_widgets.items():
            lines = text_widget.get('1.0', tk.END).strip().split('\n')
            panel_data[col_name] = lines
            if len(lines) > max_rows:
                max_rows = len(lines)

        new_data = []
        for i in range(max_rows):
            row = {}
            for col_name in self.columns:
                if i < len(panel_data[col_name]):
                    row[col_name] = panel_data[col_name][i]
                else:
                    row[col_name] = ""
            new_data.append(row)
        
        self.data = new_data

    def _save_and_close(self):
        """Parse data from panels, save, and close the dialog."""
        self._parse_panels_to_data()
        self.on_save(self.data, self.columns)
        self.destroy()
