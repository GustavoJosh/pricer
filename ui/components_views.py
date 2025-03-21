"""
Component-related views and operations for the Sign Business application.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import db.queries as queries
from .job_views import JobViews

class ComponentViews:
    def __init__(self, parent_frame, app):
        self.parent_frame = parent_frame
        self.app = app
        self.job_views = JobViews(parent_frame, app)
    
    def add_component(self, sign_id, parent_window, refresh_callback):
        """Add a new component to a sign"""
        component_name = simpledialog.askstring("New Component", "Enter component name:", parent=parent_window)
        
        if not component_name or not component_name.strip():
            return
        
        component_id = queries.create_component(sign_id, component_name.strip())
        
        if component_id is not None:
            messagebox.showinfo("Success", "Component added successfully!")
            refresh_callback(sign_id, parent_window)
    
    def add_component_tab(self, notebook, component, sign_id, parent_window):
        """Add a tab for a component to the notebook"""
        # Create a tab for the component
        component_tab = ttk.Frame(notebook)
        notebook.add(component_tab, text=f"{component['ComponentName']} (${component['Subtotal']:.2f})")
        
        # Get jobs for this component
        jobs = queries.get_jobs_by_component_id(component['ComponentID'])
        
        # Create a treeview for jobs
        job_columns = ("Job Name", "Unit Cost", "Quantity", "Amount")
        job_tree = ttk.Treeview(component_tab, columns=job_columns, show="headings", height=10)
        
        for col in job_columns:
            job_tree.heading(col, text=col)
            job_tree.column(col, width=150)
        
        job_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add scrollbar
        job_scrollbar = ttk.Scrollbar(component_tab, orient="vertical", command=job_tree.yview)
        job_tree.configure(yscrollcommand=job_scrollbar.set)
        job_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate job data
        if jobs:
            for job in jobs:
                quantity = job['Quantity'] if job['Quantity'] is not None else "-"
                amount = f"${job['Amount']:.2f}" if job['Amount'] is not None else "-"
                
                job_tree.insert("", tk.END, values=(
                    job['JobName'],
                    f"${job['UnitCost']:.2f}", 
                    quantity,
                    amount
                ))
        
        # Button frame for component actions
        component_buttons = ttk.Frame(component_tab)
        component_buttons.pack(pady=10)
        
        ttk.Button(component_buttons, text="Add Job", 
                  command=lambda c_id=component['ComponentID']: 
                  self.job_views.add_job(c_id, parent_window, sign_id)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(component_buttons, text="Edit Selected Job", 
                  command=lambda tree=job_tree, c_id=component['ComponentID']: 
                  self.job_views.edit_job(tree, parent_window, sign_id)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(component_buttons, text="Delete Selected Job", 
                  command=lambda tree=job_tree, c_id=component['ComponentID']: 
                  self.job_views.delete_job(tree, parent_window, sign_id)).pack(side=tk.LEFT, padx=5)