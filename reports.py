import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import get_connection
from utils import COLORS, FONTS, create_button, create_label, safe_execute

class ReportManager:
    def __init__(self, parent_frame, user_id):
        self.frame = parent_frame
        self.user_id = user_id
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI for Reports."""
        # Top Action Bar
        action_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        action_frame.pack(fill="x", pady=10, padx=20)

        create_button(action_frame, text="Generate Monthly Chart", command=self.show_monthly_bar_chart).pack(side="left", padx=5)
        create_button(action_frame, text="Generate Category Pie Chart", command=self.show_category_pie_chart).pack(side="left", padx=5)
        create_button(action_frame, text="Export to CSV", command=self.export_csv, bg_color=COLORS["secondary"]).pack(side="right", padx=5)
        create_button(action_frame, text="Export to TXT", command=self.export_txt, bg_color=COLORS["secondary"]).pack(side="right", padx=5)

        # Chart Display Area
        self.chart_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Show default chart
        self.show_category_pie_chart()

    def clear_chart_frame(self):
        """Clear existing charts from the frame."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    @safe_execute
    def show_category_pie_chart(self):
        """Generate and display a pie chart for category-wise expenses."""
        self.clear_chart_frame()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY category", (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            create_label(self.chart_frame, text="No expense data available for chart.", font=FONTS["header"]).pack(pady=50)
            return

        categories = [row['category'] for row in data]
        amounts = [row['total'] for row in data]

        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])
        
        # Plot pie chart
        wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, 
                                          textprops={'color': COLORS["fg"]})
        
        ax.set_title("Expenses by Category", color=COLORS["fg"], fontsize=14, fontweight="bold")
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    @safe_execute
    def show_monthly_bar_chart(self):
        """Generate and display a bar chart for monthly expenses."""
        self.clear_chart_frame()
        
        conn = get_connection()
        cursor = conn.cursor()
        # Extract YYYY-MM
        cursor.execute("SELECT substr(date, 1, 7) as month, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY month ORDER BY month", (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            create_label(self.chart_frame, text="No expense data available for chart.", font=FONTS["header"]).pack(pady=50)
            return

        months = [row['month'] for row in data]
        amounts = [row['total'] for row in data]

        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])
        
        # Plot bar chart
        bars = ax.bar(months, amounts, color=COLORS["accent"])
        
        ax.set_title("Monthly Expenses", color=COLORS["fg"], fontsize=14, fontweight="bold")
        ax.set_xlabel("Month", color=COLORS["fg"])
        ax.set_ylabel("Amount (₹)", color=COLORS["fg"])
        ax.tick_params(colors=COLORS["fg"])
        
        # Add values on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, f'₹{yval:.0f}', ha='center', va='bottom', color=COLORS["fg"])
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    @safe_execute
    def export_csv(self):
        """Export all income and expense data to CSV."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        # Get Income
        cursor.execute("SELECT 'Income' as type, amount, source as category, date, description FROM income WHERE user_id=? ORDER BY date DESC", (self.user_id,))
        income_data = cursor.fetchall()
        
        # Get Expenses
        cursor.execute("SELECT 'Expense' as type, amount, category, date, description FROM expenses WHERE user_id=? ORDER BY date DESC", (self.user_id,))
        expense_data = cursor.fetchall()
        
        conn.close()

        all_data = income_data + expense_data
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Amount", "Category/Source", "Date", "Description"])
            for row in all_data:
                writer.writerow([row['type'], row['amount'], row['category'], row['date'], row['description']])
                
        messagebox.showinfo("Success", "Data exported to CSV successfully.")

    @safe_execute
    def export_txt(self):
        """Export a summary report to TXT."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        # Total Income
        cursor.execute("SELECT SUM(amount) as total FROM income WHERE user_id=?", (self.user_id,))
        total_in = cursor.fetchone()['total'] or 0
        
        # Total Expenses
        cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id=?", (self.user_id,))
        total_out = cursor.fetchone()['total'] or 0
        
        # Category Breakdown
        cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY category", (self.user_id,))
        category_data = cursor.fetchall()
        
        conn.close()

        balance = total_in - total_out

        with open(file_path, mode='w', encoding='utf-8') as file:
            file.write("="*40 + "\n")
            file.write("PERSONAL EXPENSE TRACKER REPORT\n")
            file.write("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            file.write("="*40 + "\n\n")
            
            file.write("--- FINANCIAL SUMMARY ---\n")
            file.write(f"Total Income:  ₹{total_in:.2f}\n")
            file.write(f"Total Expense: ₹{total_out:.2f}\n")
            file.write(f"Current Balance: ₹{balance:.2f}\n\n")
            
            file.write("--- EXPENSE BY CATEGORY ---\n")
            for row in category_data:
                file.write(f"{row['category']}: ₹{row['total']:.2f}\n")
                
            file.write("\n" + "="*40 + "\n")
                
        messagebox.showinfo("Success", "Report exported to TXT successfully.")
