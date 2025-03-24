"""
Main application window and navigation for the Sign Business application.
"""
import tkinter as tk
from tkinter import ttk
from db.connection import DatabaseConnection
from .sign_views import SignViews

class SignBusinessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Business Management")
        self.root.geometry("1200x700")
        self.root.configure(padx=10, pady=10)
        
        # Database connection
        self.db_connection = DatabaseConnection.get_instance()
        
        # Main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create navigation panel
        self.create_navigation_panel()
        
        # Create main content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Initialize sign view manager
        self.sign_views = SignViews(self.content_frame, self)
        
        # Initialize with signs view
        self.show_signs()
    
    def create_navigation_panel(self):
        """Create the navigation panel with buttons"""
        nav_frame = ttk.Frame(self.main_frame, width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        ttk.Label(nav_frame, text="Navegacion", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Navigation buttons
        ttk.Button(nav_frame, text="Ver carteles", command=self.show_signs, width=20).pack(pady=5)
        ttk.Button(nav_frame, text="Agregar nuevo cartel", command=self.add_new_sign, width=20).pack(pady=5)
        ttk.Separator(nav_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(nav_frame, text="Salir", command=self.root.destroy, width=20).pack(pady=5)
    
    def clear_content_frame(self):
        """Clear all widgets from the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_signs(self):
        """Display list of all signs"""
        self.clear_content_frame()
        self.sign_views.show_signs_list()
    
    def add_new_sign(self):
        """Add a new sign to the database"""
        self.clear_content_frame()
        self.sign_views.show_add_sign_form()
    
    def close_application(self):
        """Close the application and database connection"""
        if self.db_connection:
            self.db_connection.close()
        self.root.destroy()