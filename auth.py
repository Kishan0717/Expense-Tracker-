import tkinter as tk
from tkinter import messagebox
import hashlib
from database import get_connection
from utils import COLORS, FONTS, center_window, create_button, create_entry, create_label, safe_execute

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

class AuthApp:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Expense Tracker - Login")
        self.root.configure(bg=COLORS["bg"])
        center_window(self.root, 400, 500)
        
        self.show_login()

    def clear_frame(self):
        """Destroy all widgets in the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        """Render the Login Screen."""
        self.clear_frame()
        self.root.title("Expense Tracker - Login")
        
        frame = tk.Frame(self.root, bg=COLORS["bg"])
        frame.pack(expand=True)

        lbl_title = create_label(frame, text="Welcome Back", font=FONTS["title"], fg=COLORS["accent"])
        lbl_title.pack(pady=(0, 30))

        # Username
        lbl_user = create_label(frame, text="Username")
        lbl_user.pack(anchor="w")
        self.ent_user = create_entry(frame)
        self.ent_user.pack(pady=(0, 15))

        # Password
        lbl_pass = create_label(frame, text="Password")
        lbl_pass.pack(anchor="w")
        
        pass_frame = tk.Frame(frame, bg=COLORS["bg"])
        pass_frame.pack(fill="x", pady=(0, 20))
        
        self.ent_pass = create_entry(pass_frame, show="*")
        self.ent_pass.pack(side="left", fill="x", expand=True)
        
        self.show_pass_var = tk.BooleanVar()
        chk_show = tk.Checkbutton(pass_frame, text="Show", variable=self.show_pass_var, 
                                  command=self.toggle_password, bg=COLORS["bg"], fg=COLORS["fg"], 
                                  selectcolor=COLORS["entry_bg"], activebackground=COLORS["bg"],
                                  activeforeground=COLORS["fg"])
        chk_show.pack(side="right", padx=(5, 0))

        # Buttons
        btn_login = create_button(frame, text="Login", command=self.login)
        btn_login.pack(pady=10)

        lbl_register = create_label(frame, text="Don't have an account?", font=FONTS["small"])
        lbl_register.pack(pady=(20, 5))
        
        btn_go_register = create_button(frame, text="Register", command=self.show_register, 
                                        bg_color=COLORS["secondary"])
        btn_go_register.pack()

    def toggle_password(self):
        """Toggle password visibility for login and registration."""
        if hasattr(self, 'ent_pass'):
            if self.show_pass_var.get():
                self.ent_pass.config(show="")
            else:
                self.ent_pass.config(show="*")
        
        if hasattr(self, 'ent_reg_pass'):
            if self.show_pass_var.get():
                self.ent_reg_pass.config(show="")
                self.ent_reg_confirm.config(show="")
            else:
                self.ent_reg_pass.config(show="*")
                self.ent_reg_confirm.config(show="*")

    def show_register(self):
        """Render the Registration Screen."""
        self.clear_frame()
        self.root.title("Expense Tracker - Register")
        
        # Make the window slightly larger for registration
        center_window(self.root, 400, 600)
        
        frame = tk.Frame(self.root, bg=COLORS["bg"])
        frame.pack(expand=True)

        lbl_title = create_label(frame, text="Create Account", font=FONTS["title"], fg=COLORS["secondary"])
        lbl_title.pack(pady=(0, 20))

        # Full Name
        lbl_name = create_label(frame, text="Full Name")
        lbl_name.pack(anchor="w")
        self.ent_reg_name = create_entry(frame)
        self.ent_reg_name.pack(pady=(0, 10))

        # Username
        lbl_user = create_label(frame, text="Username")
        lbl_user.pack(anchor="w")
        self.ent_reg_user = create_entry(frame)
        self.ent_reg_user.pack(pady=(0, 10))

        # Email
        lbl_email = create_label(frame, text="Email")
        lbl_email.pack(anchor="w")
        self.ent_reg_email = create_entry(frame)
        self.ent_reg_email.pack(pady=(0, 10))

        # Password
        lbl_pass = create_label(frame, text="Password")
        lbl_pass.pack(anchor="w")
        self.ent_reg_pass = create_entry(frame, show="*")
        self.ent_reg_pass.pack(pady=(0, 10))

        # Confirm Password
        lbl_confirm = create_label(frame, text="Confirm Password")
        lbl_confirm.pack(anchor="w")
        self.ent_reg_confirm = create_entry(frame, show="*")
        self.ent_reg_confirm.pack(pady=(0, 10))
        
        self.show_pass_var = tk.BooleanVar()
        chk_show = tk.Checkbutton(frame, text="Show Passwords", variable=self.show_pass_var, 
                                  command=self.toggle_password, bg=COLORS["bg"], fg=COLORS["fg"], 
                                  selectcolor=COLORS["entry_bg"], activebackground=COLORS["bg"],
                                  activeforeground=COLORS["fg"])
        chk_show.pack(anchor="w", pady=(0, 10))

        # Buttons
        btn_register = create_button(frame, text="Register", command=self.register, bg_color=COLORS["secondary"])
        btn_register.pack(pady=10)

        btn_back = create_button(frame, text="Back to Login", command=self.show_login, bg_color=COLORS["entry_bg"], fg_color=COLORS["fg"])
        btn_back.pack()

    @safe_execute
    def login(self):
        """Process login attempt."""
        username = self.ent_user.get().strip()
        password = self.ent_pass.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return

        hashed_pw = hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Success", f"Welcome back, {user['full_name']}!")
            # Call the success callback, passing user info
            self.on_success(user['id'], user['full_name'])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    @safe_execute
    def register(self):
        """Process registration attempt."""
        name = self.ent_reg_name.get().strip()
        username = self.ent_reg_user.get().strip()
        email = self.ent_reg_email.get().strip()
        password = self.ent_reg_pass.get()
        confirm = self.ent_reg_confirm.get()

        if not all([name, username, email, password, confirm]):
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return

        if password != confirm:
            messagebox.showwarning("Input Error", "Passwords do not match")
            return

        if len(password) < 6:
            messagebox.showwarning("Input Error", "Password must be at least 6 characters")
            return

        hashed_pw = hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (full_name, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (name, username, email, hashed_pw))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_login()
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                messagebox.showerror("Error", "Username already exists")
            elif "email" in str(e).lower():
                messagebox.showerror("Error", "Email already exists")
            else:
                messagebox.showerror("Error", "Registration failed. Try again.")
        finally:
            conn.close()
