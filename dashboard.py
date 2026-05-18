import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from database import get_connection
from utils import COLORS, FONTS, center_window, create_button, create_label, safe_execute
from income import IncomeManager
from expenses import ExpenseManager
from reports import ReportManager

class DashboardApp:
    def __init__(self, root, user_id, user_name, on_logout):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name
        self.on_logout = on_logout
        
        self.root.title("Expense Tracker - Dashboard")
        center_window(self.root, 900, 700)
        self.root.configure(bg=COLORS["bg"])
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the main dashboard layout."""
        # Header Frame
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        lbl_welcome = tk.Label(header, text=f"Welcome, {self.user_name}!", font=FONTS["header"], bg=COLORS["primary"], fg=COLORS["fg"])
        lbl_welcome.pack(side="left", padx=20, pady=15)
        
        btn_logout = create_button(header, text="Logout", command=self.logout, bg_color=COLORS["error"], width=10)
        btn_logout.pack(side="right", padx=20, pady=15)
        
        # Setup Notebook (Tabs)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=COLORS["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', background=COLORS["entry_bg"], foreground=COLORS["fg"], padding=[20, 5], font=FONTS["normal"])
        style.map('TNotebook.Tab', background=[("selected", COLORS["accent"])], foreground=[("selected", COLORS["btn_fg"])])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Tabs
        self.tab_overview = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.tab_income = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.tab_expenses = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.tab_reports = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.tab_settings = tk.Frame(self.notebook, bg=COLORS["bg"])
        
        self.notebook.add(self.tab_overview, text="Overview")
        self.notebook.add(self.tab_income, text="Income")
        self.notebook.add(self.tab_expenses, text="Expenses")
        self.notebook.add(self.tab_reports, text="Reports")
        self.notebook.add(self.tab_settings, text="Settings")
        
        # Initialize Managers
        self.setup_overview()
        self.income_manager = IncomeManager(self.tab_income, self.user_id, self.update_overview)
        self.expense_manager = ExpenseManager(self.tab_expenses, self.user_id, self.update_overview)
        self.report_manager = ReportManager(self.tab_reports, self.user_id)
        self.setup_settings()
        
        # When tab changes, update overview and reports just in case
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        """Handle tab change events to refresh data."""
        current_tab = self.notebook.index("current")
        if current_tab == 0:  # Overview
            self.update_overview()
        elif current_tab == 3:  # Reports
            self.report_manager.show_category_pie_chart()

    def setup_overview(self):
        """Setup the Overview Tab UI."""
        # Summary Cards Frame
        self.summary_frame = tk.Frame(self.tab_overview, bg=COLORS["bg"])
        self.summary_frame.pack(fill="x", pady=20, padx=20)
        
        self.lbl_total_income = self.create_summary_card(self.summary_frame, "Total Income", "₹0.00", 0, COLORS["secondary"])
        self.lbl_total_expense = self.create_summary_card(self.summary_frame, "Total Expense", "₹0.00", 1, COLORS["error"])
        self.lbl_balance = self.create_summary_card(self.summary_frame, "Current Balance", "₹0.00", 2, COLORS["accent"])
        
        # Budget info
        self.budget_frame = tk.Frame(self.tab_overview, bg=COLORS["bg"])
        self.budget_frame.pack(fill="x", pady=10, padx=20)
        self.lbl_budget = create_label(self.budget_frame, text="Monthly Budget: Not Set", font=FONTS["header"])
        self.lbl_budget.pack(side="left")
        
        create_button(self.budget_frame, text="Set Budget", command=self.set_budget, bg_color=COLORS["primary"], fg_color=COLORS["fg"]).pack(side="right")
        
        # Recent Transactions
        trans_lbl = create_label(self.tab_overview, text="Recent Transactions (Last 5)", font=FONTS["header"], fg=COLORS["secondary"])
        trans_lbl.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.tree_recent = ttk.Treeview(self.tab_overview, columns=("Type", "Amount", "Date", "Desc"), show="headings", height=5)
        self.tree_recent.heading("Type", text="Type")
        self.tree_recent.heading("Amount", text="Amount")
        self.tree_recent.heading("Date", text="Date")
        self.tree_recent.heading("Desc", text="Description")
        
        self.tree_recent.column("Type", width=100)
        self.tree_recent.column("Amount", width=100)
        self.tree_recent.column("Date", width=100)
        self.tree_recent.column("Desc", width=400)
        
        self.tree_recent.pack(fill="x", padx=20)
        
        self.update_overview()

    def create_summary_card(self, parent, title, value, col, color):
        """Helper to create a summary card."""
        card = tk.Frame(parent, bg=COLORS["entry_bg"], bd=2, relief="groove")
        card.grid(row=0, column=col, padx=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=title, font=FONTS["normal"], bg=COLORS["entry_bg"], fg=COLORS["fg"]).pack(pady=(10, 5))
        lbl_val = tk.Label(card, text=value, font=FONTS["title"], bg=COLORS["entry_bg"], fg=color)
        lbl_val.pack(pady=(0, 10))
        return lbl_val

    @safe_execute
    def update_overview(self):
        """Update dashboard overview statistics."""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get Totals
        cursor.execute("SELECT SUM(amount) as total FROM income WHERE user_id=?", (self.user_id,))
        total_in = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id=?", (self.user_id,))
        total_out = cursor.fetchone()['total'] or 0
        
        balance = total_in - total_out
        
        self.lbl_total_income.config(text=f"₹{total_in:.2f}")
        self.lbl_total_expense.config(text=f"₹{total_out:.2f}")
        self.lbl_balance.config(text=f"₹{balance:.2f}")
        
        # Color balance based on value
        if balance < 0:
            self.lbl_balance.config(fg=COLORS["error"])
        else:
            self.lbl_balance.config(fg=COLORS["accent"])
            
        # Get Budget
        current_month = datetime.today().strftime('%Y-%m')
        cursor.execute("SELECT budget_amount FROM budgets WHERE user_id=? AND month=?", (self.user_id, current_month))
        budget_row = cursor.fetchone()
        
        if budget_row:
            self.lbl_budget.config(text=f"Monthly Budget: ₹{budget_row['budget_amount']:.2f}")
        else:
            self.lbl_budget.config(text="Monthly Budget: Not Set")
            
        # Update Recent Transactions
        for item in self.tree_recent.get_children():
            self.tree_recent.delete(item)
            
        cursor.execute('''
            SELECT 'Income' as type, amount, date, description FROM income WHERE user_id=?
            UNION
            SELECT 'Expense' as type, amount, date, description FROM expenses WHERE user_id=?
            ORDER BY date DESC LIMIT 5
        ''', (self.user_id, self.user_id))
        recent = cursor.fetchall()
        
        for r in recent:
            self.tree_recent.insert("", tk.END, values=(r['type'], f"₹{r['amount']:.2f}", r['date'], r['description']))
            
        conn.close()

    @safe_execute
    def set_budget(self):
        """Prompt user to set a budget for the current month."""
        budget_str = simpledialog.askstring("Set Budget", "Enter budget amount for this month (₹):", parent=self.root)
        if budget_str:
            try:
                budget_amt = float(budget_str)
                if budget_amt < 0:
                    raise ValueError
                    
                current_month = datetime.today().strftime('%Y-%m')
                conn = get_connection()
                cursor = conn.cursor()
                
                # Check if budget exists
                cursor.execute("SELECT id FROM budgets WHERE user_id=? AND month=?", (self.user_id, current_month))
                if cursor.fetchone():
                    cursor.execute("UPDATE budgets SET budget_amount=? WHERE user_id=? AND month=?", (budget_amt, self.user_id, current_month))
                else:
                    cursor.execute("INSERT INTO budgets (user_id, month, budget_amount) VALUES (?, ?, ?)", (self.user_id, current_month, budget_amt))
                    
                conn.commit()
                conn.close()
                self.update_overview()
                messagebox.showinfo("Success", "Budget updated successfully")
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number.")

    def setup_settings(self):
        """Setup the Settings Tab."""
        lbl_title = create_label(self.tab_settings, text="Settings", font=FONTS["title"], fg=COLORS["secondary"])
        lbl_title.pack(pady=20)
        
        # User details
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, username, email FROM users WHERE id=?", (self.user_id,))
        user = cursor.fetchone()
        conn.close()
        
        info_frame = tk.Frame(self.tab_settings, bg=COLORS["entry_bg"], bd=1, relief="solid")
        info_frame.pack(pady=20, padx=50, fill="x")
        
        create_label(info_frame, text=f"Name: {user['full_name']}").pack(anchor="w", padx=20, pady=5)
        create_label(info_frame, text=f"Username: {user['username']}").pack(anchor="w", padx=20, pady=5)
        create_label(info_frame, text=f"Email: {user['email']}").pack(anchor="w", padx=20, pady=5)
        
        btn_del_acc = create_button(self.tab_settings, text="Delete Account Data", command=self.delete_account, bg_color=COLORS["error"])
        btn_del_acc.pack(pady=20)

    @safe_execute
    def delete_account(self):
        """Clear all user data."""
        if messagebox.askyesno("WARNING", "Are you sure you want to delete ALL your data? This action cannot be undone."):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM income WHERE user_id=?", (self.user_id,))
            cursor.execute("DELETE FROM expenses WHERE user_id=?", (self.user_id,))
            cursor.execute("DELETE FROM budgets WHERE user_id=?", (self.user_id,))
            # Optionally delete user: cursor.execute("DELETE FROM users WHERE id=?", (self.user_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "All your transactions have been deleted.")
            self.update_overview()
            self.income_manager.load_income_data()
            self.expense_manager.load_expense_data()

    def logout(self):
        """Logout user and return to login screen."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.on_logout()
