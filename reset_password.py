#!/usr/bin/env python3
"""
SPEED MOI - Password Reset Utility
Run this script from the terminal to reset the password for an admin user.

Usage:
  python reset_password.py
"""

import sys
import getpass
from werkzeug.security import generate_password_hash
import database

def main():
    print("=" * 50)
    print("          SPEED MOI - PASSWORD RESET")
    print("=" * 50)

    database.init_db()

    username = input("Enter username to reset [admin]: ").strip()
    if not username:
        username = "admin"

    user = database.get_user_by_username(username)
    if not user:
        print(f"\n[ERROR] User '{username}' was not found in the database.")
        print("Please check the username and try again.")
        sys.exit(1)

    print(f"User '{username}' found.")
    while True:
        password = getpass.getpass("Enter new password (at least 6 characters): ")
        if len(password) < 6:
            print("Password must be at least 6 characters long. Please try again.")
            continue
        confirm = getpass.getpass("Confirm new password: ")
        if password != confirm:
            print("Passwords do not match. Please try again.")
            continue
        break

    new_hash = generate_password_hash(password)
    success = database.update_user_password(username, new_hash)

    if success:
        print("\n[SUCCESS] Password has been reset successfully!")
        print(f"You can now log in as '{username}' with your new password.")
    else:
        print("\n[ERROR] Failed to update password. Please try again.")

if __name__ == "__main__":
    main()
