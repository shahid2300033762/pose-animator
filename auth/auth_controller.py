import os
import json
import uuid
import datetime
from auth.models import User, DB_PATH, check_password_hash

class AuthController:
    def __init__(self):
        self.db_path = DB_PATH
        self.current_user = None
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the users database file exists"""
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self):
        """Load users from the database file"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self, users):
        """Save users to the database file"""
        with open(self.db_path, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register(self, username, email, password):
        """Register a new user"""
        users = self._load_users()
        
        # Check if username already exists
        for user_data in users.values():
            if user_data['username'].lower() == username.lower():
                return False, "Username already exists"
            if user_data.get('email', '').lower() == email.lower():
                return False, "Email already exists"
        
        # Create new user
        user_id = str(uuid.uuid4())  # Better ID generation
        created_at = datetime.datetime.now().isoformat()
        new_user = User(username=username, email=email, password=password, user_id=user_id, created_at=created_at)
        
        # Save to database
        users[user_id] = new_user.to_dict()
        self._save_users(users)
        
        return True, new_user
    
    def login(self, username, password):
        """Login a user with username and password"""
        users = self._load_users()
        
        # Find user by username
        for user_id, user_data in users.items():
            if user_data['username'].lower() == username.lower():
                # Check password
                if check_password_hash(user_data['password_hash'], password):
                    # Create user object
                    user = User.from_dict(user_data)
                    self.current_user = user
                    return True, user
                else:
                    return False, None
        
        return False, None
    
    def create_guest_session(self, guest_username):
        """Create a guest user session"""
        # Create a temporary guest user
        user_id = str(uuid.uuid4())
        created_at = datetime.datetime.now().isoformat()
        
        guest_user = User(
            user_id=user_id,
            username=guest_username,
            email=f"{guest_username}@guest.local",
            password=str(uuid.uuid4()),  # Random password
            created_at=created_at,
            is_guest=True
        )
        
        # Save guest user
        users = self._load_users()
        
        # Check if we already have too many guest accounts (optional cleanup)
        guest_users = {uid: data for uid, data in users.items() 
                      if data.get('is_guest', False)}
        if len(guest_users) > 10:  # Limit number of stored guest accounts
            # Remove oldest guest accounts
            users = {uid: data for uid, data in users.items() 
                    if not data.get('is_guest', False)}
        
        # Add the new guest user
        users[user_id] = guest_user.to_dict()
        self._save_users(users)
        
        # Set as current user
        self.current_user = guest_user
        
        return True, guest_user
    
    def get_current_user(self):
        """Get the currently logged in user"""
        return self.current_user
    
    def logout(self):
        """Logout the current user"""
        self.current_user = None
        return True