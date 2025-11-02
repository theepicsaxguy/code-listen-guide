"""CLI script to PROMOTE an existing user to admin.

Usage:
    python -m backend.scripts.create_admin --email user@example.com

Behavior:
- Normalizes email to lowercase
- Looks up existing user; if not found exits with error
- Sets `is_admin=True` if not already admin
- Idempotent: if already admin, reports and exits successfully

Exit codes:
- 0 success (promoted or already admin)
- 1 validation / input error (bad email)
- 2 user not found
- 3 unexpected error
"""
from __future__ import annotations
import sys
import argparse
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.user import User
from backend.utils.validators import validate_email_format

def promote_admin(email: str, db: Session) -> User:
    """Promote existing user to admin or exit if not found."""
    normalized_email = email.strip().lower()
    if not validate_email_format(normalized_email):
        print("ERROR: Invalid email format", file=sys.stderr)
        sys.exit(1)
    stmt = select(User).where(func.lower(User.email) == normalized_email)
    user = db.scalars(stmt).first()
    if not user:
        print("ERROR: User not found", file=sys.stderr)
        sys.exit(2)
    if user.is_admin:
        print(f"User {normalized_email} already admin. Nothing to do.")
        return user
    user.is_admin = True
    db.commit()
    db.refresh(user)
    print(f"Promoted user {normalized_email} to admin (id={user.id}).")
    return user

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Promote existing user to admin")
    parser.add_argument("--email", required=True, help="User email address to promote")

    args = parser.parse_args(argv)

    try:
        db = SessionLocal()
    except Exception as e:
        print(f"ERROR: Could not create DB session: {e}", file=sys.stderr)
        return 3

    try:
        promote_admin(email=args.email, db=db)
        return 0
    except SystemExit as se:
        return se.code
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 3
    finally:
        db.close()

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
