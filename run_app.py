import os
import sys
import importlib.util
import tkinter as tk
from tkinter import messagebox, simpledialog
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the auth controller
from auth.auth_controller import AuthController

class SimpleLoginUI:
    def __init__(self, on_login_success):
        self.auth_controller = AuthController()
        self.on_login_success = on_login_success
        self.is_login_mode = True
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Pose Animator - Login")
        self.root.geometry("400x600")
        self.root.configure(bg="#0E0F1A")
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Ensure the login window is visible and focused on launch
        try:
            self.root.deiconify()
            self.root.state('normal')
            self.root.lift()
            self.root.focus_force()
            self.root.attributes('-topmost', True)
            self.root.after(800, lambda: self.root.attributes('-topmost', False))
        except Exception:
            pass
        
        # Header
        tk.Label(self.root, text="Pose Animator", font=("Arial", 24, "bold"), 
                fg="#00C2FF", bg="#0E0F1A").pack(pady=(40, 10))
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#161827", padx=30, pady=30)
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Mode selector
        self.mode_frame = tk.Frame(self.main_frame, bg="#161827")
        self.mode_frame.pack(fill="x", pady=(0, 20))
        
        self.login_mode_btn = tk.Button(self.mode_frame, text="Login", font=("Arial", 12, "bold"),
                                      bg="#00C2FF", fg="#0E0F1A", relief="flat",
                                      command=self._switch_to_login)
        self.login_mode_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.register_mode_btn = tk.Button(self.mode_frame, text="Sign Up", font=("Arial", 12, "bold"),
                                         bg="#9966FF", fg="#0E0F1A", relief="flat",
                                         command=self._switch_to_register)
        self.register_mode_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Form fields
        # Username
        tk.Label(self.main_frame, text="Username", font=("Arial", 10, "bold"), 
                fg="white", bg="#161827").pack(anchor="w", pady=(0, 5))
        self.username_entry = tk.Entry(self.main_frame, font=("Arial", 12), bg="#0A0B14", 
                                      fg="white", insertbackground="white")
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Email (initially hidden for login mode)
        self.email_label = tk.Label(self.main_frame, text="Email", font=("Arial", 10, "bold"), 
                                  fg="white", bg="#161827")
        self.email_entry = tk.Entry(self.main_frame, font=("Arial", 12), bg="#0A0B14", 
                                   fg="white", insertbackground="white")
        
        # Password
        tk.Label(self.main_frame, text="Password", font=("Arial", 10, "bold"), 
                fg="white", bg="#161827").pack(anchor="w", pady=(0, 5))
        self.password_entry = tk.Entry(self.main_frame, font=("Arial", 12), bg="#0A0B14", 
                                      fg="white", insertbackground="white", show="•")
        self.password_entry.pack(fill="x", ipady=8, pady=(0, 20))
        
        # Action buttons
        self.action_frame = tk.Frame(self.main_frame, bg="#161827")
        self.action_frame.pack(fill="x", pady=(10, 0))
        
        # Submit button (login/register)
        self.submit_button = tk.Button(self.action_frame, text="Login", font=("Arial", 12, "bold"), 
                                     bg="#00C2FF", fg="#0E0F1A", relief="flat",
                                     command=self._handle_submit)
        self.submit_button.pack(fill="x", ipady=8, pady=(0, 10))
        
        # Guest button
        self.guest_button = tk.Button(self.action_frame, text="Continue as Guest", font=("Arial", 12, "bold"), 
                                    bg="#FF9900", fg="#0E0F1A", relief="flat",
                                    command=self._handle_guest)
        self.guest_button.pack(fill="x", ipady=8)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready to login", font=("Arial", 10), 
                                  fg="white", bg="#00C2FF", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        
        # Set default user
        self.username_entry.insert(0, "admin")
        self.password_entry.insert(0, "password123")
        
        # Initialize in login mode
        self._switch_to_login()
    
    def _switch_to_login(self):
        self.is_login_mode = True
        self.login_mode_btn.config(bg="#00C2FF")
        self.register_mode_btn.config(bg="#666666")
        self.submit_button.config(text="Login", bg="#00C2FF")
        
        # Hide email field
        self.email_label.pack_forget()
        self.email_entry.pack_forget()
        
        self.status_bar.config(text="Ready to login", bg="#00C2FF")
    
    def _switch_to_register(self):
        self.is_login_mode = False
        self.login_mode_btn.config(bg="#666666")
        self.register_mode_btn.config(bg="#9966FF")
        self.submit_button.config(text="Sign Up", bg="#9966FF")
        
        # Show email field
        self.email_label.pack(anchor="w", pady=(0, 5), after=self.username_entry)
        self.email_entry.pack(fill="x", ipady=8, pady=(0, 15), after=self.email_label)
        
        self.status_bar.config(text="Ready to create account", bg="#9966FF")
    
    def _handle_submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if self.is_login_mode:
            self._handle_login(username, password)
        else:
            email = self.email_entry.get().strip()
            self._handle_register(username, email, password)
    
    def _handle_login(self, username, password):
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        self.status_bar.config(text="Logging in...", bg="#8A2BE2")
        self.root.update_idletasks()
        
        success, user = self.auth_controller.login(username, password)
        
        if success:
            self.status_bar.config(text=f"Welcome, {user.username}!", bg="#00FFB2")
            self.root.update_idletasks()
            self.root.after(1000, self._login_success)
        else:
            self.status_bar.config(text="Login failed", bg="#FF4D4D")
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def _handle_register(self, username, email, password):
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        self.status_bar.config(text="Creating account...", bg="#8A2BE2")
        self.root.update_idletasks()
        
        success, result = self.auth_controller.register(username, email, password)
        
        if success:
            self.status_bar.config(text="Account created successfully!", bg="#00FFB2")
            messagebox.showinfo("Success", "Account created successfully! You can now log in.")
            self._switch_to_login()
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
            self.password_entry.delete(0, tk.END)
        else:
            self.status_bar.config(text="Registration failed", bg="#FF4D4D")
            messagebox.showerror("Registration Failed", result)
    
    def _handle_guest(self):
        self.status_bar.config(text="Creating guest session...", bg="#FF9900")
        self.root.update_idletasks()
        
        import uuid
        guest_id = str(uuid.uuid4())[:8]
        guest_username = f"guest_{guest_id}"
        
        success, user = self.auth_controller.create_guest_session(guest_username)
        
        if success:
            self.status_bar.config(text=f"Welcome, Guest User!", bg="#00FFB2")
            self.root.update_idletasks()
            self.root.after(1000, self._login_success)
        else:
            self.status_bar.config(text="Failed to create guest session", bg="#FF4D4D")
            messagebox.showerror("Error", "Failed to create guest session")
    
    def _login_success(self):
        if self.on_login_success:
            self.root.destroy()
            self.on_login_success()
    
    def run(self):
        self.root.mainloop()

def load_final_app():
    """Dynamically load and run the final_app.py"""
    try:
        # Path to final_app.py - corrected path to include pose_animator-master subdirectory
        final_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     'pose_animator-master', 'final_app.py')
        
        # Load the module
        spec = importlib.util.spec_from_file_location("final_app", final_app_path)
        final_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(final_app)
        
        # Run the application
        app = final_app.ModernPoseAnimatorGUI()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load the Pose Animator application: {str(e)}")
        print(f"Error loading application: {str(e)}")

def ensure_default_user_exists():
    """Ensure at least one default user exists in the system"""
    auth_controller = AuthController()
    users = auth_controller._load_users()
    
    if not users:
        # Create a default admin user if no users exist
        auth_controller.register(
            username="admin",
            email="admin@example.com",
            password="password123"
        )
        print("Created default admin user (username: admin, password: password123)")

def main():
    """Main entry point for the application with login → app → back to login flow"""
    print("Starting Pose Animator with Login...")

    # Ensure we have at least one user in the system
    ensure_default_user_exists()

    while True:
        # Track whether login succeeded
        login_success = {"flag": False}

        def on_login_success():
            login_success["flag"] = True

        # Show login UI
        login_ui = SimpleLoginUI(on_login_success=on_login_success)
        login_ui.run()

        # If user closed login window without logging in, exit
        if not login_success["flag"]:
            print("Login cancelled. Exiting.")
            break

        # Launch the final application; when it closes, loop back to login
        load_final_app()

        # After app closes, clear session and return to login
        try:
            AuthController().logout()
        except Exception:
            pass

if __name__ == "__main__":
    main()