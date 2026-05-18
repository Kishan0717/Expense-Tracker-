import tkinter as tk
from database import init_db
from auth import AuthApp
from dashboard import DashboardApp
from utils import COLORS

class MainApplication:
    def __init__(self):
        # Initialize Database
        init_db()
        
        self.root = tk.Tk()
        self.root.title("Expense Tracker")
        self.root.configure(bg=COLORS["bg"])
        
        self.show_auth()

    def show_auth(self):
        """Show the Login/Registration Screen."""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.auth_app = AuthApp(self.root, self.on_login_success)

    def on_login_success(self, user_id, user_name):
        """Callback when user logs in successfully."""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.dashboard_app = DashboardApp(self.root, user_id, user_name, self.show_auth)

    def run(self):
        """Start the Tkinter event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
