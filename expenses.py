import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_connection
from utils import COLORS, FONTS, create_button, create_entry, create_label, safe_execute

CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Education", "Entertainment", "Medical", "Other"]

class ExpenseManager:
    def __init__(self, parent_frame, user_id, update_dashboard_callback):
        self.frame = parent_frame
        self.user_id = user_id
        self.update_dashboard = update_dashboard_callback
        
        self.setup_ui()
        self.load_expense_data()

    def setup_ui(self):
        """Setup the UI for Expense Management."""
        # Top section for Add Expense form
        form_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        form_frame.pack(fill="x", pady=10, padx=20)

        # Form fields
        create_label(form_frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_amount = create_entry(form_frame, width=15)
        self.ent_amount.grid(row=0, column=1, padx=5, pady=5)

        create_label(form_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.cb_category = ttk.Combobox(form_frame, textvariable=self.category_var, values=CATEGORIES, state="readonly", width=13)
        self.cb_category.grid(row=0, column=3, padx=5, pady=5)

        create_label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_date = create_entry(form_frame, width=15)
        self.ent_date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.ent_date.grid(row=1, column=1, padx=5, pady=5)

        create_label(form_frame, text="Description:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.ent_desc = create_entry(form_frame, width=15)
        self.ent_desc.grid(row=1, column=3, padx=5, pady=5)

        btn_add = create_button(form_frame, text="Add Expense", command=self.add_expense, bg_color=COLORS["secondary"], width=15)
        btn_add.grid(row=0, column=4, rowspan=2, padx=20, pady=5)

        # Table for displaying expense records
        table_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Amount", "Category", "Date", "Description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure Treeview styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLORS["entry_bg"], foreground=COLORS["fg"], fieldbackground=COLORS["entry_bg"], rowheight=25)
        style.map("Treeview", background=[("selected", COLORS["primary"])])
        style.configure("Treeview.Heading", background=COLORS["primary"], foreground=COLORS["fg"], font=FONTS["small"])

        self.tree.heading("ID", text="ID")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Amount", width=100, anchor="e")
        self.tree.column("Category", width=120)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Description", width=250)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bottom section for Delete button
        action_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        action_frame.pack(fill="x", pady=10, padx=20)
        
        btn_delete = create_button(action_frame, text="Delete Selected", command=self.delete_expense, bg_color=COLORS["error"], width=15)
        btn_delete.pack(side="right")

    @safe_execute
    def add_expense(self):
        """Add new expense record."""
        amount_str = self.ent_amount.get().strip()
        category = self.category_var.get()
        date = self.ent_date.get().strip()
        desc = self.ent_desc.get().strip()

        if not amount_str or not category or not date:
            messagebox.showwarning("Input Error", "Amount, Category, and Date are required")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a positive number")
            return

        # Simple date validation
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Input Error", "Date must be in YYYY-MM-DD format")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.user_id, amount, category, date, desc))
        conn.commit()
        conn.close()

        # Check budget warning
        self.check_budget()

        # Clear inputs
        self.ent_amount.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.ent_date.delete(0, tk.END)
        self.ent_date.insert(0, datetime.today().strftime('%Y-%m-%d'))

        messagebox.showinfo("Success", "Expense added successfully")
        self.load_expense_data()
        self.update_dashboard()

    @safe_execute
    def load_expense_data(self):
        """Load expense data into the Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, category, date, description FROM expenses WHERE user_id=? ORDER BY date DESC", (self.user_id,))
        records = cursor.fetchall()
        conn.close()

        for record in records:
            self.tree.insert("", tk.END, values=(record['id'], f"₹{record['amount']:.2f}", record['category'], record['date'], record['description']))

    @safe_execute
    def delete_expense(self):
        """Delete selected expense record."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record to delete")
            return

        record_id = self.tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense record?"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (record_id, self.user_id))
            conn.commit()
            conn.close()

            self.load_expense_data()
            self.update_dashboard()
            messagebox.showinfo("Success", "Expense deleted successfully")

    def check_budget(self):
        """Check if expenses exceed the set budget for the current month."""
        conn = get_connection()
        cursor = conn.cursor()
        
        current_month = datetime.today().strftime('%Y-%m')
        
        # Get budget for current month
        cursor.execute("SELECT budget_amount FROM budgets WHERE user_id=? AND month=?", (self.user_id, current_month))
        budget_row = cursor.fetchone()
        
        if budget_row:
            budget = budget_row['budget_amount']
            
            # Get total expenses for current month
            cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id=? AND date LIKE ?", (self.user_id, f"{current_month}%"))
            expense_row = cursor.fetchone()
            total_expense = expense_row['total'] or 0
            
            if total_expense > budget:
                messagebox.showwarning("Budget Warning", f"Warning: Your expenses (₹{total_expense:.2f}) have exceeded your monthly budget (₹{budget:.2f})!")
                
        conn.close()
