"""
Main entry point for Automation Studio.
"""
import tkinter as tk
from src.main_window import AutomationStudio

def main():
    """Main entry point"""
    root = tk.Tk()
    app = AutomationStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
