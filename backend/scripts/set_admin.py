#!/usr/bin/env python3
"""
Script to set admin status for users by email pattern.

Usage:
    python -m backend.scripts.set_admin "@tuta"
    python -m backend.scripts.set_admin "user@example.com"
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import or_
from backend.db.session import SessionLocal
from backend.models.user import User


def set_admin_by_email_pattern(email_pattern: str, is_admin: bool = True) -> int:
    """
    Set admin status for users matching email pattern.
    
    Args:
        email_pattern: Email pattern to match (e.g., "@tuta" or "user@example.com")
        is_admin: Whether to set admin status (default: True)
    
    Returns:
        Number of users updated
    """
    db = SessionLocal()
    try:
        # If pattern contains @, search for emails containing it
        if "@" in email_pattern and email_pattern != "user@example.com":
            # Pattern search (e.g., "@tuta" will match "@tuta.io", "@tuta.com", etc.)
            users = db.query(User).filter(
                User.email.like(f"%{email_pattern}%")
            ).all()
        else:
            # Exact email match
            users = db.query(User).filter(User.email == email_pattern).all()
        
        if not users:
            print(f"No users found matching pattern: {email_pattern}")
            return 0
        
        # Update admin status
        updated_count = 0
        for user in users:
            user.is_admin = is_admin
            updated_count += 1
            print(f"✓ Set is_admin={is_admin} for user: {user.email} (ID: {user.id})")
        
        db.commit()
        print(f"\n✓ Successfully updated {updated_count} user(s)")
        return updated_count
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error updating users: {e}")
        raise
    finally:
        db.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m backend.scripts.set_admin <email_pattern> [is_admin]")
        print("Examples:")
        print('  python -m backend.scripts.set_admin "@tuta"')
        print('  python -m backend.scripts.set_admin "user@tuta.io"')
        print('  python -m backend.scripts.set_admin "user@example.com" false')
        sys.exit(1)
    
    email_pattern = sys.argv[1]
    is_admin = True
    
    if len(sys.argv) >= 3:
        is_admin = sys.argv[2].lower() in ("true", "1", "yes", "y")
    
    print(f"Setting admin status for users matching: {email_pattern}")
    print(f"is_admin = {is_admin}\n")
    
    count = set_admin_by_email_pattern(email_pattern, is_admin)
    sys.exit(0 if count > 0 else 1)


if __name__ == "__main__":
    main()

