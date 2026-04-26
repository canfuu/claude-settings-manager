"""
Claude Settings Manager - Main Entry Point
"""
import tkinter as tk
from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Create and show main window
    app = MainWindow(root)

    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
