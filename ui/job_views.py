"""
Job-related views and operations for the Sign Business application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import db.queries as queries

class JobViews:
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
    
    def add_job(self, component_id, parent_window, sign_id):
        """Add a new job to a component"""
        # Create dialog window
        dialog = tk.Toplevel(parent_window)
        dialog.title("Add New Job")
        dialog.geometry("400x250")
        dialog.configure(padx=20, pady=20)
        
        # Form fields
        ttk.Label(dialog, text="Job Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Unit Cost:").grid(row=1, column=0, sticky=tk.W, pady=5)
        cost_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=cost_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Quantity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=quantity_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(dialog, text="(Leave empty if not applicable)").grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # Save button
        def save_job():
            name = name_var.get().strip()
            cost_str = cost_var.get().strip()
            quantity_str = quantity_var.get().strip()
            
            if not name or not cost_str:
                messagebox.showwarning("Validation Error", "Job name and unit cost are required.")
                return
            
            try:
                cost = float(cost_str)
                quantity = float(quantity_str) if quantity_str else None
                
                job_id = queries.create_job(component_id, name, cost, quantity)
                
                if job_id is not None:
                    messagebox.showinfo("Success", "Job added successfully!")
                    dialog.destroy()
                    
                    # Get the detail view function from parent to refresh
                    self._refresh_detail_view(sign_id, parent_window)
                
            except ValueError:
                messagebox.showwarning("Validation Error", "Cost and quantity must be valid numbers.")
        
        ttk.Button(dialog, text="Save Job", command=save_job).grid(row=3, column=0, pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=3, column=1, pady=20)
    
    def edit_job(self, tree, parent_window, sign_id):
        """Edit the selected job"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a job to edit.")
            return
        
        job_name = tree.item(selected_item[0], "values")[0]
        unit_cost = tree.item(selected_item[0], "values")[1].replace("$", "")
        quantity = tree.item(selected_item[0], "values")[2]
        
        # Get job ID from database
        job = queries.get_job_by_details(job_name, float(unit_cost))
        
        if not job:
            messagebox.showerror("Error", "Job not found in database.")
            return
            
        job_id = job['JobID']
        
        # Create dialog window
        dialog = tk.Toplevel(parent_window)
        dialog.title("Edit Job")
        dialog.geometry("400x250")
        dialog.configure(padx=20, pady=20)
        
        # Form fields
        ttk.Label(dialog, text="Job Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=job_name)
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Unit Cost:").grid(row=1, column=0, sticky=tk.W, pady=5)
        cost_var = tk.StringVar(value=unit_cost)
        ttk.Entry(dialog, textvariable=cost_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(dialog, text="Quantity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.StringVar(value="" if quantity == "-" else quantity)
        ttk.Entry(dialog, textvariable=quantity_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(dialog, text="(Leave empty if not applicable)").grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # Save button
        def save_changes():
            name = name_var.get().strip()
            cost_str = cost_var.get().strip()
            quantity_str = quantity_var.get().strip()
            
            if not name or not cost_str:
                messagebox.showwarning("Validation Error", "Job name and unit cost are required.")
                return
            
            try:
                cost = float(cost_str)
                quantity = float(quantity_str) if quantity_str else None
                
                success = queries.update_job(job_id, name, cost, quantity)
                
                if success is not None:
                    messagebox.showinfo("Success", "Job updated successfully!")
                    dialog.destroy()
                    
                    # Refresh the detail view
                    self._refresh_detail_view(sign_id, parent_window)
                
            except ValueError:
                messagebox.showwarning("Validation Error", "Cost and quantity must be valid numbers.")
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).grid(row=3, column=0, pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=3, column=1, pady=20)
    
    def delete_job(self, tree, parent_window, sign_id):
        """Delete the selected job"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a job to delete.")
            return
        
        job_name = tree.item(selected_item[0], "values")[0]
        unit_cost = tree.item(selected_item[0], "values")[1].replace("$", "")
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                      f"Are you sure you want to delete the job:\n\n{job_name}\n\nThis action cannot be undone!")
        if not confirm:
            return
        
        # Get job ID from database
        job = queries.get_job_by_details(job_name, float(unit_cost))
        
        if not job:
            messagebox.showerror("Error", "Job not found in database.")
            return
            
        job_id = job['JobID']
        
        success = queries.delete_job(job_id)
        
        if success is not None:
            messagebox.showinfo("Success", "Job deleted successfully!")
            
            # Refresh the detail view
            self._refresh_detail_view(sign_id, parent_window)
    
    def _refresh_detail_view(self, sign_id, parent_window):
        """Refresh the detail view after changes"""
        parent_window.destroy()
        
        # Create a new detail window
        from ui.sign_views import SignViews
        sign_views = SignViews(self.parent_frame, self.app)
        sign_views._show_sign_detail_window(sign_id)