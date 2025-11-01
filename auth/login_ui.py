import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.auth_controller import AuthController

class LoginUI:
    def __init__(self, on_login_success=None):
        self.auth_controller = AuthController()
        self.on_login_success = on_login_success
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Pose Animator - Login")
        self.root.withdraw()  # Hide window during setup
        
        # Colors and Fonts - matching final_app.py style
        self.colors = {
            'background': '#0E0F1A',
            'primary': '#00C2FF', 
            'accent': '#8A2BE2',
            'success': '#00FFB2', 
            'error': '#FF4D4D',
            'text': '#FFFFFF', 
            'panel_bg': '#161827',
            'dark_bg': '#0A0B14'
        }
        self.fonts = {
            'header': ('Poppins', 24, 'bold'), 
            'body': ('Inter', 12),
            'button': ('Montserrat', 12, 'bold'), 
            'label': ('Inter', 10, 'bold')
        }
        
        # Setup splash screen
        self._setup_splash()
        
        # Setup main login window after splash
        self.root.after(1500, self._setup_login_window)
        
    def _setup_splash(self):
        """Create a splash screen while loading"""
        self.splash = tk.Toplevel(self.root)
        self.splash.overrideredirect(True)
        self.splash.geometry("400x250")
        self._center_window(self.splash)
        
        # Make sure the splash screen is visible
        self.splash.attributes('-topmost', True)
        
        splash_canvas = tk.Canvas(self.splash, bg=self.colors['background'], highlightthickness=0)
        splash_canvas.pack(fill='both', expand=True)
        
        try:
            # Logo and loading text
            splash_canvas.create_text(200, 100, text="🅿️🅰️", font=('Poppins', 60, 'bold'), fill=self.colors['primary'])
            splash_canvas.create_text(200, 160, text="Pose Animator", font=('Poppins', 20, 'bold'), fill=self.colors['text'])
            self.loading_label = tk.Label(splash_canvas, text="Loading...", font=('Inter', 12), 
                                         fg=self.colors['text'], bg=self.colors['background'])
            self.loading_label.place(x=160, y=200)
            
            # Print to console for debugging
            print("Splash screen created successfully")
        except tk.TclError:
            # Fallback if fonts are not available
            self.loading_label = tk.Label(splash_canvas, text="Loading...", font=('Arial', 12), 
                                         fg=self.colors['text'], bg=self.colors['background'])
            self.loading_label.place(x=160, y=200)
            print("Splash screen created with fallback fonts")
    
    def _center_window(self, window):
        """Center a window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_login_window(self):
        """Setup the main login window"""
        # Close splash screen
        self.splash.destroy()
        
        # Configure main window
        self.root.configure(bg=self.colors['background'])
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self._center_window(self.root)
        
        # Make sure the main window is visible
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        
        # Show window
        self.root.deiconify()
        
        print("Main login window created and displayed")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['background'])
        header_frame.pack(fill='x', pady=(0, 30))
        
        tk.Label(header_frame, text="Pose Animator", font=self.fonts['header'], 
                fg=self.colors['primary'], bg=self.colors['background']).pack()
        tk.Label(header_frame, text="Sign In", font=self.fonts['body'], 
                fg=self.colors['text'], bg=self.colors['background']).pack(pady=(5, 0))
        
        # Login form
        form_frame = tk.Frame(main_frame, bg=self.colors['panel_bg'], padx=30, pady=30)
        form_frame.pack(fill='x', ipady=10)
        
        # Username
        tk.Label(form_frame, text="Username", font=self.fonts['label'], 
                fg=self.colors['text'], bg=self.colors['panel_bg']).pack(anchor='w', pady=(0, 5))
        self.username_entry = tk.Entry(form_frame, font=self.fonts['body'], bg=self.colors['dark_bg'], 
                                      fg=self.colors['text'], insertbackground=self.colors['text'])
        self.username_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # Password
        tk.Label(form_frame, text="Password", font=self.fonts['label'], 
                fg=self.colors['text'], bg=self.colors['panel_bg']).pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(form_frame, font=self.fonts['body'], bg=self.colors['dark_bg'], 
                                      fg=self.colors['text'], insertbackground=self.colors['text'], show="•")
        self.password_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # Login button
        self.login_button = tk.Button(form_frame, text="Sign In", font=self.fonts['button'], 
                                     bg=self.colors['primary'], fg=self.colors['background'], 
                                     relief='flat', command=self._handle_login)
        self.login_button.pack(fill='x', ipady=10, pady=(10, 0))
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready to login", font=self.fonts['label'], 
                                  fg=self.colors['text'], bg=self.colors['primary'], anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self._handle_login())
        
        # Focus username entry
        self.username_entry.focus_set()
    
    def _handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Update status
        self.status_bar.config(text="Logging in...", bg=self.colors['accent'])
        self.root.update_idletasks()
        
        # Attempt login
        success, user = self.auth_controller.login(username, password)
        
        if success:
            self.status_bar.config(text=f"Welcome, {user.username}!", bg=self.colors['success'])
            self.root.update_idletasks()
            self.root.after(1000, self._login_success)
        else:
            self.status_bar.config(text="Login failed. Please try again.", bg=self.colors['error'])
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def _login_success(self):
        """Handle successful login"""
        if self.on_login_success:
            self.root.destroy()
            self.on_login_success()
    
    def run(self):
        """Run the login UI"""
        self.root.mainloop()

if __name__ == "__main__":
    # For testing the login UI independently
    login_ui = LoginUI(on_login_success=lambda: print("Login successful!"))
    login_ui.run()