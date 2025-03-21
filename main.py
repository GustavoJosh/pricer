"""
Main entry point for the Sign Business Management application.
"""
import tkinter as tk
from ui.app import SignBusinessApp

def main():
    """Initialize and run the application"""
    root = tk.Tk()
    app = SignBusinessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_application)  # Handle window close
    root.mainloop()

if __name__ == "__main__":
    main()