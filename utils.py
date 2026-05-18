import tkinter as tk
from tkinter import messagebox
from functools import wraps

# UI Configuration settings
COLORS = {
    "bg": "#121212",          # Dark background
    "fg": "#FFFFFF",          # White text
    "accent": "#BB86FC",      # Purple accent
    "primary": "#3700B3",     # Darker purple
    "secondary": "#03DAC6",   # Teal secondary
    "error": "#CF6679",       # Red error
    "entry_bg": "#1E1E1E",    # Slightly lighter background for entry
    "btn_fg": "#000000",      # Black text on buttons
}

FONTS = {
    "title": ("Arial", 24, "bold"),
    "header": ("Arial", 16, "bold"),
    "normal": ("Arial", 12),
    "small": ("Arial", 10),
}

def center_window(window, width, height):
    """Centers a tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_button(parent, text, command, bg_color=COLORS["accent"], fg_color=COLORS["btn_fg"], font=FONTS["normal"], width=20):
    """Creates a standardized styled button."""
    btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg=fg_color, font=font, 
                    activebackground=COLORS["primary"], activeforeground=COLORS["fg"], 
                    relief="flat", cursor="hand2", width=width)
    return btn

def create_entry(parent, font=FONTS["normal"], show=None, width=30):
    """Creates a standardized styled entry field."""
    entry = tk.Entry(parent, font=font, bg=COLORS["entry_bg"], fg=COLORS["fg"], 
                     insertbackground=COLORS["fg"], show=show, relief="flat", width=width)
    return entry

def create_label(parent, text, font=FONTS["normal"], fg=COLORS["fg"]):
    """Creates a standardized styled label."""
    label = tk.Label(parent, text=text, font=font, bg=COLORS["bg"], fg=fg)
    return label

def safe_execute(func):
    """Decorator to handle exceptions globally in GUI callbacks."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            print(f"Error in {func.__name__}: {e}")
    return wrapper
