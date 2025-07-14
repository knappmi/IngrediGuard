import sqlite3
import os
import hashlib
import secrets
import time
from kivy.logger import Logger

class UserDatabase:
    """
    A class to manage the user database using SQLite.
    It provides methods to add, delete, and retrieve users,
    as well as authenticate users and manage permissions.
    """

    def __init__(self, db_path="app_data/users.db"):
        """
        Initializes the database connection and creates the users table if it
        doesn't exist.
        """
        self.manager = None  # Add manager attribute to prevent crashes
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_table()
        self.ensure_default_admin()

    def create_table(self):
        """Creates the users table if it doesn't already exist."""
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        is_admin BOOLEAN NOT NULL DEFAULT 0,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at INTEGER NOT NULL,
                        last_login INTEGER
                    )
                """)
        except sqlite3.Error as e:
            Logger.error(f"Database error in create_table: {e}")

    def ensure_default_admin(self):
        """Ensures that a default admin user exists in the database."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
                if cursor.fetchone()[0] == 0:
                    Logger.info("Creating default admin user")
                    # Create a default admin user
                    self.add_user("admin", "admin123", is_admin=True)
        except sqlite3.Error as e:
            Logger.error(f"Database error in ensure_default_admin: {e}")

    def hash_password(self, password, salt=None):
        """Hashes a password with a salt using PBKDF2."""
        if salt is None:
            salt = secrets.token_hex(16)  # Generate a random salt
        
        # Use PBKDF2 with 100,000 iterations (adjust as needed)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return salt, key.hex()

    def add_user(self, username, password, is_admin=False):
        """Adds a new user to the database."""
        try:
            # Check if username already exists
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                if cursor.fetchone()[0] > 0:
                    Logger.warning(f"Username {username} already exists")
                    return False, "Username already exists"
                
                # Hash the password
                salt, password_hash = self.hash_password(password)
                
                # Add the user
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt, is_admin, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, password_hash, salt, is_admin, True, int(time.time()))
                )
                Logger.info(f"Added new user: {username}, admin: {is_admin}")
                return True, "User added successfully"
        except sqlite3.Error as e:
            Logger.error(f"Database error in add_user: {e}")
            return False, f"Database error: {e}"

    def authenticate_user(self, username, password):
        """Authenticates a user with the given username and password."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, password_hash, salt, is_admin, is_active FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                
                if not user:
                    Logger.warning(f"Authentication failed: User {username} not found")
                    return False, "Invalid username or password", None
                
                user_id, stored_hash, salt, is_admin, is_active = user
                
                if not is_active:
                    Logger.warning(f"Authentication failed: User {username} is inactive")
                    return False, "Account is disabled", None
                
                # Verify password
                _, calculated_hash = self.hash_password(password, salt)
                
                if calculated_hash == stored_hash:
                    # Update last login time
                    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (int(time.time()), user_id))
                    Logger.info(f"User {username} authenticated successfully")
                    return True, "Authentication successful", {"id": user_id, "username": username, "is_admin": is_admin}
                else:
                    Logger.warning(f"Authentication failed: Invalid password for {username}")
                    return False, "Invalid username or password", None
        except sqlite3.Error as e:
            Logger.error(f"Database error in authenticate_user: {e}")
            return False, f"Database error: {e}", None

    def get_users(self):
        """Retrieves all users from the database."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, username, is_admin, is_active, created_at, last_login FROM users")
                rows = cursor.fetchall()
                # Convert list of tuples to list of dictionaries
                users_list = [{
                    'id': r[0], 
                    'username': r[1], 
                    'is_admin': bool(r[2]), 
                    'is_active': bool(r[3]),
                    'created_at': r[4],
                    'last_login': r[5]
                } for r in rows]
                return users_list
        except sqlite3.Error as e:
            Logger.error(f"Database error in get_users: {e}")
            return []

    def toggle_user_status(self, user_id, is_active):
        """Enable or disable a user."""
        try:
            with self.conn:
                # Check if this is the last admin
                if not is_active:  # Only check when disabling
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
                    user = cursor.fetchone()
                    if user and user[0]:  # This is an admin
                        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1 AND is_active = 1")
                        active_admins = cursor.fetchone()[0]
                        if active_admins <= 1:
                            return False, "Cannot disable the last active admin"
                
                self.conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
                status = "enabled" if is_active else "disabled"
                Logger.info(f"User ID {user_id} {status}")
                return True, f"User {status} successfully"
        except sqlite3.Error as e:
            Logger.error(f"Database error in toggle_user_status: {e}")
            return False, f"Database error: {e}"

    def toggle_user_admin(self, user_id, is_admin):
        """Make a user an admin or remove admin privileges."""
        try:
            with self.conn:
                self.conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (is_admin, user_id))
                status = "granted" if is_admin else "revoked"
                Logger.info(f"Admin privileges {status} for User ID {user_id}")
                return True, f"Admin privileges {status} successfully"
        except sqlite3.Error as e:
            Logger.error(f"Database error in toggle_user_admin: {e}")
            return False, f"Database error: {e}"

    def change_password(self, user_id, new_password):
        """Changes a user's password."""
        try:
            with self.conn:
                # Hash the new password
                salt, password_hash = self.hash_password(new_password)
                
                self.conn.execute(
                    "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                    (password_hash, salt, user_id)
                )
                Logger.info(f"Password changed for User ID {user_id}")
                return True, "Password changed successfully"
        except sqlite3.Error as e:
            Logger.error(f"Database error in change_password: {e}")
            return False, f"Database error: {e}"

    def reset_database(self):
        """Resets the user database by removing all users and recreating the default admin."""
        try:
            with self.conn:
                self.conn.execute("DROP TABLE IF EXISTS users")
                self.create_table()
                self.ensure_default_admin()
                Logger.warning("User database has been reset")
                return True, "Database reset successfully"
        except sqlite3.Error as e:
            Logger.error(f"Database error in reset_database: {e}")
            return False, f"Database error: {e}"

    def close(self):
        """Closes the database connection."""
        self.conn.close()
