"""
Sign-related views and operations for the Sign Business application.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import db.queries as queries
from .components_views import ComponentViews
from utils.print_invoice import PrintInvoice

class SignViews:
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.component_views = ComponentViews(parent_frame, app)
        self.current_windows = {}  # Track open windows by sign_id
    
    def show_signs_list(self):
        """Display list of all signs"""
        # Header
        ttk.Label(self.parent_frame, text="Lista de carteles", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create treeview
        columns = ("ID", "Cartel", "Cliente", "Creado", "Estado", "Costo Total")
        tree = ttk.Treeview(self.parent_frame, columns=columns, show="headings", height=20)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            if col == "Sign Name" or col == "Customer":
                tree.column(col, width=200)
            elif col == "Creation Date":
                tree.column(col, width=150)
            else:
                tree.column(col, width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate data
        signs = queries.get_all_signs()
        if signs:
            for sign in signs:
                # Format date and cost for display
                date_formatted = sign['CreationDate'].strftime("%Y-%m-%d %H:%M")
                cost_formatted = f"${sign['TotalCost']:.2f}"
                
                tree.insert("", tk.END, values=(
                    sign['SignID'], 
                    sign['SignName'], 
                    sign['CustomerInfo'], 
                    date_formatted, 
                    sign['Status'], 
                    cost_formatted
                ))
        
        # Button frame
        button_frame = ttk.Frame(self.parent_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Ver detalles del cartel", 
                  command=lambda: self._view_sign_details(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar detalles del cartel", 
                  command=lambda: self._edit_sign(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar cartel", 
                  command=lambda: self._delete_sign(tree)).pack(side=tk.LEFT, padx=5)
    
    def show_add_sign_form(self):
        """Show form to add a new sign"""
        # Header
        ttk.Label(self.parent_frame, text="ADD NEW SIGN", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = ttk.Frame(self.parent_frame)
        form_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # Form fields
        ttk.Label(form_frame, text="Sign Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Customer:").grid(row=1, column=0, sticky=tk.W, pady=5)
        customer_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=customer_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=description_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value="Pending")
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, values=["Pending", "In Progress", "Completed"])
        status_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Components section
        ttk.Label(form_frame, text="Initial Components:", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Initialize list to store component entries
        component_entries = []
        component_frame = ttk.Frame(form_frame)
        component_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Function to add component entry
        def add_component_entry():
            entry_var = tk.StringVar()
            entry = ttk.Entry(component_frame, textvariable=entry_var, width=30)
            entry.pack(pady=2)
            component_entries.append(entry_var)
        
        # Add three component entries by default
        for _ in range(3):
            add_component_entry()
        
        ttk.Button(form_frame, text="Add Another Component", 
                  command=add_component_entry).grid(row=6, column=0, columnspan=2, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.parent_frame)
        buttons_frame.pack(pady=20)
        
        # Save button
        def save_sign():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation Error", "Sign name is required.")
                return
            
            # Create sign
            sign_id = queries.create_sign(
                name, 
                description_var.get(), 
                customer_var.get(), 
                status_var.get()
            )
            
            if sign_id:
                # Insert components
                for component_var in component_entries:
                    component_name = component_var.get().strip()
                    if component_name:
                        queries.create_component(sign_id, component_name)
                
                messagebox.showinfo("Success", "Sign created successfully!")
                self.app.show_signs()  # Refresh sign list
            else:
                messagebox.showerror("Error", "Failed to create sign.")
        
        ttk.Button(buttons_frame, text="Save Sign", command=save_sign).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.app.show_signs).pack(side=tk.LEFT, padx=5)
    
    def _view_sign_details(self, tree):
        """View details of the selected sign"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a sign to view.")
            return
        
        sign_id = tree.item(selected_item[0], "values")[0]
        
        # Check if window is already open
        if sign_id in self.current_windows and self.current_windows[sign_id].winfo_exists():
            # If window exists, bring it to front
            self.current_windows[sign_id].lift()
            self.current_windows[sign_id].focus_set()
            # Refresh the content
            self._refresh_detail_view(sign_id, self.current_windows[sign_id])
        else:
            # Create new window
            self._show_sign_detail_window(sign_id)    
    
    def _edit_sign(self, tree):
        """Edit the selected sign"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a sign to edit.")
            return
        
        sign_id = tree.item(selected_item[0], "values")[0]
        sign = queries.get_sign_by_id(sign_id)
        
        if not sign:
            messagebox.showerror("Error", "Sign not found.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Sign")
        dialog.geometry("500x300")
        dialog.configure(padx=20, pady=20)
        
        # Make dialog modal
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Form fields
        ttk.Label(dialog, text="Sign Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=sign['SignName'])
        ttk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Customer:").grid(row=1, column=0, sticky=tk.W, pady=5)
        customer_var = tk.StringVar(value=sign['CustomerInfo'] or "")
        ttk.Entry(dialog, textvariable=customer_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        description_var = tk.StringVar(value=sign['Description'] or "")
        ttk.Entry(dialog, textvariable=description_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value=sign['Status'])
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=["Pending", "In Progress", "Completed"])
        status_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Save button
        def save_changes():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation Error", "Sign name is required.")
                return
            
            success = queries.update_sign(
                sign_id, 
                name, 
                description_var.get(), 
                customer_var.get(), 
                status_var.get()
            )
            
            if success is not None:  # None indicates error
                messagebox.showinfo("Success", "Sign updated successfully!")
                dialog.destroy()
                self.app.show_signs()  # Refresh sign list
                
                # Update detail window if open
                if sign_id in self.current_windows and self.current_windows[sign_id].winfo_exists():
                    self._refresh_detail_view(sign_id, self.current_windows[sign_id])
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).grid(row=4, column=0, pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=4, column=1, pady=20)
        
        # Wait for dialog to close
        self.app.root.wait_window(dialog)
    
    def _delete_sign(self, tree):
        """Delete the selected sign"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a sign to delete.")
            return
        
        sign_id = tree.item(selected_item[0], "values")[0]
        sign_name = tree.item(selected_item[0], "values")[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                      f"Are you sure you want to delete the sign:\n\n{sign_name}\n\nThis action cannot be undone!")
        if not confirm:
            return
        
        success = queries.delete_sign(sign_id)
        if success is not None:  # None indicates error
            messagebox.showinfo("Success", "Sign deleted successfully!")
            
            # Close detail window if open
            if sign_id in self.current_windows and self.current_windows[sign_id].winfo_exists():
                self.current_windows[sign_id].destroy()
                
            self.app.show_signs()  # Refresh sign list
    
    def _refresh_detail_view(self, sign_id, detail_window):
        """Refresh the detail view after changes"""
        # For a complete refresh, destroy and recreate window
        if detail_window and detail_window.winfo_exists():
            detail_window.destroy()
        self._show_sign_detail_window(sign_id)
        
        # For a partial refresh (alternative approach):
        # self._update_sign_details(sign_id, detail_window)
    
    def _update_sign_details(self, sign_id, detail_window):
        """Update only parts of the detail window that need updating"""
        # This is a placeholder for a more sophisticated update mechanism
        # Instead of destroying and recreating the entire window
        # Implementation would require storing references to UI elements
        pass

    # Modify the _show_sign_detail_window method in sign_views.py to add a refresh button:

    def _show_sign_detail_window(self, sign_id):
        """Show the detail window for a sign"""
        # Create a new window for sign details
        detail_window = tk.Toplevel(self.app.root)
        detail_window.title("Sign Details")
        detail_window.geometry("900x700")
        detail_window.configure(padx=20, pady=20)
        
        # Get sign details
        sign = queries.get_sign_by_id(sign_id)
        
        if not sign:
            messagebox.showerror("Error", "Sign not found.")
            detail_window.destroy()
            return
        
        # Sign information section
        info_frame = ttk.LabelFrame(detail_window, text="Sign Information")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Name: {sign['SignName']}", font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text=f"Customer: {sign['CustomerInfo']}", font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text=f"Status: {sign['Status']}", font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text=f"Creation Date: {sign['CreationDate']}", font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text=f"Description: {sign['Description'] or 'N/A'}", font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text=f"Total Cost: ${sign['TotalCost']:.2f}", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        # Action buttons for sign
        action_frame = ttk.Frame(info_frame)
        action_frame.pack(anchor=tk.W, pady=10)
        
        # Print invoice button
        def print_invoice():
            printer = PrintInvoice(sign_id)
            printer.print_invoice()
        
        # Refresh button - Add this new button
        def refresh_view():
            self._refresh_detail_view(sign_id, detail_window)
            
        ttk.Button(action_frame, text="Print Invoice", command=print_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh View", command=refresh_view).pack(side=tk.LEFT, padx=5)
        
        # Components section
        components = queries.get_components_by_sign_id(sign_id)
        
        components_frame = ttk.LabelFrame(detail_window, text="Components")
        components_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        if components:
            # Create a notebook (tabbed interface) for components
            notebook = ttk.Notebook(components_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=10)
            
            for component in components:
                self.component_views.add_component_tab(notebook, component, sign_id, detail_window)
        else:
            ttk.Label(components_frame, text="No components found.").pack(pady=20)
        
        # Add component button
        ttk.Button(components_frame, text="Add New Component", 
                command=lambda: self.component_views.add_component(sign_id, detail_window, self._refresh_detail_view)).pack(pady=10)
        
        # Close button
        ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)
        
        return detail_window