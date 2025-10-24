"""
Input validation utilities.

TODO: Implementation steps:
1. Implement validate_github_url()
2. Implement validate_depth_tier()
3. Implement validate_email()
4. Implement validate_password_strength()
5. Add custom Pydantic validators
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse


def validate_github_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate GitHub repository URL and extract owner/repo.

    Args:
        url: GitHub repository URL

    Returns:
        Tuple of (is_valid, owner, repo_name)

    TODO:
    1. Parse URL
    2. Check if domain is github.com
    3. Extract owner and repo name from path
    4. Return validation result
    """
    # TODO: Implement
    # Example patterns:
    # https://github.com/owner/repo
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git
    pass


def validate_depth_tier(tier: str) -> bool:
    """
    Validate depth tier value.

    TODO:
    - Check if tier is one of: survey, standard, comprehensive
    """
    valid_tiers = ["survey", "standard", "comprehensive"]
    return tier.lower() in valid_tiers


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Returns:
        Tuple of (is_valid, error_message)

    TODO:
    - Check minimum length (8 chars)
    - Check for uppercase letter
    - Check for lowercase letter
    - Check for number
    - Check for special character
    - Return validation result with helpful message
    """
    # TODO: Implement
    pass


def validate_email_format(email: str) -> bool:
    """
    Validate email format.

    TODO:
    - Use regex to validate email format
    - Return True/False
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None
