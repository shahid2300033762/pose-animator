import os
import json
import hashlib
import base64
from datetime import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'auth', 'users.json')

# Simple password hashing functions
def generate_password_hash(password):
    """Generate a simple hash for a password"""
    salt = "pose_animator_salt"  # In production, use a random salt per user
    hash_obj = hashlib.sha256((password + salt).encode())
    return base64.b64encode(hash_obj.digest()).decode()

def check_password_hash(stored_hash, password):
    """Check if the provided password matches the stored hash"""
    return stored_hash == generate_password_hash(password)

class User:
    def __init__(self, username, email, password=None, user_id=None, created_at=None, is_guest=False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = created_at or datetime.now().isoformat()
        self.is_guest = is_guest
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """Set a new password for the user"""
        self.password_hash = generate_password_hash(password)
    
    def to_dict(self):
        """Convert user object to dictionary for JSON storage"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'is_guest': self.is_guest
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a user object from dictionary data"""
        user = cls(
            username=data['username'],
            email=data['email'],
            user_id=data['user_id'],
            created_at=data['created_at'],
            is_guest=data.get('is_guest', False)
        )
        user.password_hash = data['password_hash']
        return user


class UserManager:
    def __init__(self):
        self.users = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, 'r') as f:
                    data = json.load(f)
                    for user_id, user_data in data.items():
                        self.users[user_id] = User.from_dict(user_data)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is empty or corrupted, start with empty users dict
                self.users = {}
        else:
            # Create empty users file
            with open(DB_PATH, 'w') as f:
                json.dump({}, f)
    
    def _save_users(self):
        """Save users to JSON file"""
        users_dict = {user_id: user.to_dict() for user_id, user in self.users.items()}
        with open(DB_PATH, 'w') as f:
            json.dump(users_dict, f, indent=2)
    
    def create_user(self, username, email, password):
        """Create a new user"""
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username:
                return False, "Username already exists"
            if user.email == email:
                return False, "Email already exists"
        
        # Generate a unique user ID
        user_id = str(len(self.users) + 1)
        
        # Create and save the new user
        new_user = User(username, email, password, user_id)
        self.users[user_id] = new_user
        self._save_users()
        
        return True, user_id
    
    def authenticate(self, username, password):
        """Authenticate a user by username and password"""
        for user in self.users.values():
            if user.username == username and user.check_password(password):
                return True, user.user_id
        return False, "Invalid username or password"
    
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        return self.users.get(user_id)