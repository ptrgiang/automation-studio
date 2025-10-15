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
        ttk.Button(header_frame, text=f"{Icons.DELETE} Delete Selected", command=self._delete_selected_columns).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(header_frame, text=f"{Icons.PLUS} Add Column", command=self._add_column).pack(side=tk.RIGHT, padx=(0, 5))

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

        for col_index, col_name in enumerate(self.columns):
            col_frame = ttk.Frame(self.panels_frame, padding=5)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create a frame for the header with column name and delete checkbox
            header_frame = ttk.Frame(col_frame)
            header_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Create a delete checkbox for this column
            delete_var = tk.BooleanVar()
            delete_checkbox = ttk.Checkbutton(header_frame, variable=delete_var)
            delete_checkbox.pack(side=tk.LEFT)
            
            # Store the delete variable for later access
            if not hasattr(self, 'delete_vars'):
                self.delete_vars = {}
            self.delete_vars[col_name] = delete_var
            
            # Make column name editable with an entry field
            col_entry = ttk.Entry(header_frame, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD, 'bold'))
            col_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            col_entry.insert(0, col_name)
            
            # Store the entry widget for later access
            if not hasattr(self, 'col_entries'):
                self.col_entries = {}
            self.col_entries[col_name] = col_entry
            
            # Add event to update the column name when changed
            col_entry.bind('<FocusOut>', lambda e, cn=col_name, entry=col_entry: self._update_column_name(cn, entry))
            
            # Create a frame for the text widget and scrollbars
            text_frame = ttk.Frame(col_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create text widget and scrollbars
            text_widget = tk.Text(text_frame, width=20, font=(ModernTheme.FONT_FAMILY, 10),
                                  bg=ModernTheme.CARD, fg=ModernTheme.CARD_FOREGROUND,
                                  wrap=tk.NONE, borderwidth=1, relief=tk.SOLID)
            
            # Create scrollbars
            v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            
            text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack text widget first, then scrollbars
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            values = [str(row.get(col_name, '')) for row in self.data]
            text_widget.insert('1.0', '\n'.join(values))
            
            # Configure scrollbars
            text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # To implement conditional scrollbar visibility, we'll use a more reliable approach
            def check_and_show_scrollbars(event=None):
                # Update idletasks to make sure dimensions are calculated
                text_widget.update_idletasks()
                
                # Temporarily set scrollbars to see if they're needed
                # Check vertical scrollbar - if content is larger than widget
                try:
                    # Check if scrollbar is needed by comparing content height to widget height
                    text_widget.update_idletasks()
                    # Check if we need vertical scrollbar by seeing if we can scroll
                    top, bottom = text_widget.yview()
                    if top != 0 or bottom != 1.0:  # There's more content than visible
                        if v_scrollbar.winfo_ismapped() == 0:
                            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    else:
                        if v_scrollbar.winfo_ismapped() == 1:
                            v_scrollbar.pack_forget()
                except tk.TclError:
                    pass  # Ignore errors and keep scrollbar visible
                
                try:
                    # Check if we need horizontal scrollbar
                    left, right = text_widget.xview()
                    if left != 0 or right != 1.0:  # There's wider content than visible
                        if h_scrollbar.winfo_ismapped() == 0:
                            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                    else:
                        if h_scrollbar.winfo_ismapped() == 1:
                            h_scrollbar.pack_forget()
                except tk.TclError:
                    pass  # Ignore errors and keep scrollbar visible

            # Bind events to check scrollbar visibility
            text_widget.bind('<KeyRelease>', check_and_show_scrollbars)
            text_widget.bind('<MouseWheel>', check_and_show_scrollbars)
            text_widget.bind('<Button-4>', check_and_show_scrollbars)  # Linux
            text_widget.bind('<Button-5>', check_and_show_scrollbars)  # Linux
            text_widget.bind('<Configure>', check_and_show_scrollbars)
            
            # Initial check after widget is rendered
            self.after(100, check_and_show_scrollbars)
            
            self.text_widgets[col_name] = text_widget

    def _update_column_name(self, old_name, entry_widget):
        """Update the column name when user edits it."""
        new_name = entry_widget.get().strip()
        if new_name and new_name != old_name and new_name not in self.columns:
            # Update the column name
            index = self.columns.index(old_name)
            self.columns[index] = new_name
            
            # Update data to use new column name
            for row in self.data:
                if old_name in row:
                    value = row.pop(old_name)
                    row[new_name] = value
                    
            # Update the column entries mapping
            self.col_entries[new_name] = self.col_entries.pop(old_name)
            self.delete_vars[new_name] = self.delete_vars.pop(old_name)
            self.text_widgets[new_name] = self.text_widgets.pop(old_name)
        elif new_name in self.columns and new_name != old_name:
            # Column name already exists, revert to original
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, old_name)
            messagebox.showerror("Error", f"Column name '{new_name}' already exists.", parent=self)

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

    def _delete_selected_columns(self):
        """Delete columns that are marked for deletion."""
        if not hasattr(self, 'delete_vars'):
            return
            
        columns_to_delete = []
        for col_name, delete_var in self.delete_vars.items():
            if delete_var.get():  # If checkbox is checked
                columns_to_delete.append(col_name)
        
        if not columns_to_delete:
            messagebox.showinfo("No Selection", "No columns selected for deletion.", parent=self)
            return
            
        if messagebox.askyesno("Delete Columns", f"Delete {len(columns_to_delete)} selected columns? This cannot be undone.", parent=self):
            # Remove the selected columns from self.columns
            for col_name in columns_to_delete:
                if col_name in self.columns:
                    self.columns.remove(col_name)
                    # Remove from other tracking dictionaries
                    if col_name in self.text_widgets:
                        del self.text_widgets[col_name]
                    if col_name in self.col_entries:
                        del self.col_entries[col_name]
                    if col_name in self.delete_vars:
                        del self.delete_vars[col_name]
                    
                    # Remove the column from all rows
                    for row in self.data:
                        if col_name in row:
                            del row[col_name]
            
            # Repopulate the panels
            self._populate_panels()

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
        """Parse data from panels, delete checked columns, save, and close the dialog."""
        self._parse_panels_to_data()
        
        # Remove columns that were marked for deletion
        if hasattr(self, 'delete_vars'):
            columns_to_delete = []
            for col_name, delete_var in self.delete_vars.items():
                if delete_var.get():  # If checkbox is checked
                    columns_to_delete.append(col_name)
            
            # Remove the selected columns
            for col_name in columns_to_delete:
                if col_name in self.columns:
                    self.columns.remove(col_name)
                    # Remove from other tracking dictionaries
                    if col_name in self.text_widgets:
                        del self.text_widgets[col_name]
                    if col_name in self.col_entries:
                        del self.col_entries[col_name]
                    if col_name in self.delete_vars:
                        del self.delete_vars[col_name]
                    
                    # Remove the column from all rows
                    for row in self.data:
                        if col_name in row:
                            del row[col_name]
        
        self.on_save(self.data, self.columns)
        self.destroy()
