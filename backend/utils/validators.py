"""
Input validation utilities.

Provides validation functions for:
- GitHub repository URLs
- Depth tiers (survey, standard, comprehensive)
- Email addresses
- Password strength requirements
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse


def validate_github_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate GitHub repository URL and extract owner/repo.

    Supports patterns:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git

    Args:
        url: GitHub repository URL

    Returns:
        Tuple of (is_valid, owner, repo_name)
    """
    # Handle git@ SSH format
    if url.startswith("git@github.com:"):
        # git@github.com:owner/repo.git
        path = url.replace("git@github.com:", "").replace(".git", "")
        parts = path.split("/")
        if len(parts) == 2:
            return (True, parts[0], parts[1])
        return (False, None, None)

    # Handle HTTPS format
    try:
        parsed = urlparse(url)
        if parsed.netloc not in ["github.com", "www.github.com"]:
            return (False, None, None)

        # Path should be /owner/repo or /owner/repo.git
        path = parsed.path.strip("/").replace(".git", "")
        parts = path.split("/")

        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1]
            return (True, owner, repo)

        return (False, None, None)
    except Exception:
        return (False, None, None)


def validate_depth_tier(tier: str) -> bool:
    """
    Validate depth tier value.

    Args:
        tier: Depth tier string to validate

    Returns:
        True if tier is valid (survey, standard, or comprehensive)
    """
    valid_tiers = ["survey", "standard", "comprehensive"]
    return tier.lower() in valid_tiers


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Requirements:
    - Minimum 8 characters
    - Maximum 72 bytes (bcrypt limit)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    Args:
        password: Password string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return (False, "Password must be at least 8 characters long")

    # Bcrypt silently truncates passwords at 72 bytes
    # Check byte length to ensure the full password is hashed
    if len(password.encode('utf-8')) > 72:
        return (False, "Password must be 72 bytes or less")

    if not re.search(r"[A-Z]", password):
        return (False, "Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        return (False, "Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        return (False, "Password must contain at least one number")

    return (True, None)


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None
