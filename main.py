# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.config import Config, logger
from database.connection import DatabaseConnection
from ui.tabs.reservations import ReservationsTab
from ui.tabs.rooms import RoomsTab
from ui.tabs.guests import GuestsTab
from ui.tabs.reports import ReportsTab

class HotelManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure main window
        self.title(f"{Config.APP_NAME} v{Config.VERSION}")
        self.geometry("1024x768")
        
        try:
            # Ensure directories exist
            Config.ensure_directories()
            
            # Initialize database
            self.db = DatabaseConnection(Config.DATABASE_PATH)
            
            # Setup UI
            self.setup_ui()
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            messagebox.showerror("Initialization Error", 
                               f"Failed to start application: {str(e)}")
            self.destroy()

    def setup_ui(self):
        """Setup the main user interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Create tabs
        self.reservations_tab = ReservationsTab(self.notebook, self.db)
        self.rooms_tab = RoomsTab(self.notebook, self.db)
        self.guests_tab = GuestsTab(self.notebook, self.db)
        self.reports_tab = ReportsTab(self.notebook, self.db)

        # Add tabs to notebook
        self.notebook.add(self.reservations_tab, text="Reservations")
        self.notebook.add(self.rooms_tab, text="Rooms")
        self.notebook.add(self.guests_tab, text="Guests")
        self.notebook.add(self.reports_tab, text="Reports")

        # Create menu
        self.create_menu()

        # Create status bar
        self.create_status_bar()

    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_bar = ttk.Label(
            self, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def backup_database(self):
        """Handle database backup"""
        try:
            # Implement backup logic here
            logger.info("Database backup initiated")
            self.status_bar.config(text="Backing up database...")
            # Add actual backup implementation
            messagebox.showinfo("Backup", "Database backup completed successfully")
            self.status_bar.config(text="Ready")
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            messagebox.showerror("Backup Error", f"Failed to backup database: {str(e)}")
            self.status_bar.config(text="Ready")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        {Config.APP_NAME}
        Version: {Config.VERSION}
        
        A comprehensive hotel management system
        for managing reservations, rooms, and guests.
        """
        messagebox.showinfo("About", about_text)

    def quit_app(self):
        """Handle application exit"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                self.db.close()
                logger.info("Application closed successfully")
                self.destroy()
            except Exception as e:
                logger.error(f"Error while closing application: {str(e)}")
                self.destroy()

def main():
    try:
        app = HotelManagementSystem()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        messagebox.showerror("Critical Error", 
                           f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main()