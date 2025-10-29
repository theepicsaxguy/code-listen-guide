#!/usr/bin/env python3
"""Test script for the parse repository endpoint."""

import json
import requests
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

BASE_URL = "http://localhost:8000"


def get_auth_token():
    """Get authentication token."""
    # Try to login with test credentials
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!",
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)

    if response.status_code == 200:
        return response.json()["access_token"]

    # If login fails, try to register
    print("Login failed, attempting to register test user...")
    register_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)

    if response.status_code == 201:
        print("Registration successful, logging in...")
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        if login_response.status_code == 200:
            return login_response.json()["access_token"]

    raise Exception(f"Authentication failed: {response.text}")


def test_parse_endpoint(token: str, repo_url: str):
    """Test the parse repository endpoint."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "repo_url": repo_url,
        "git_ref": "main",
        "use_chonkie": True,
        "max_file_size_kb": 100,  # Small limit for testing
    }

    print(f"\n{'='*80}")
    print(f"Testing Parse Endpoint")
    print(f"{'='*80}")
    print(f"Repository: {repo_url}")
    print(f"Sending request to: {BASE_URL}/api/v1/parse/repository")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"\nWaiting for response (this may take 10-30 seconds)...\n")

    response = requests.post(
        f"{BASE_URL}/api/v1/parse/repository",
        headers=headers,
        json=payload,
        timeout=120,  # 2 minute timeout
    )

    print(f"Status Code: {response.status_code}")
    print(f"\n{'='*80}")

    if response.status_code == 200:
        result = response.json()
        print("✓ SUCCESS - Repository parsed successfully!")
        print(f"\n{'='*80}")
        print("SUMMARY:")
        print(f"{'='*80}")
        print(f"Analysis Mode: {result['analysis_mode']}")
        print(f"Commit SHA: {result.get('commit_sha', 'N/A')}")
        print(f"Execution Time: {result['execution_time_seconds']}s")
        print(f"\nRepository Summary:")
        summary = result['summary']
        print(f"  - Total Files: {summary['total_files']}")
        print(f"  - Total Size: {summary['total_size_bytes']:,} bytes")
        print(f"  - Languages: {', '.join(summary['languages']) or 'None detected'}")
        print(f"  - Frameworks: {', '.join(summary['frameworks']) or 'None detected'}")
        print(f"  - Patterns: {', '.join(summary['patterns']) or 'None detected'}")
        print(f"  - Entry Points: {', '.join(summary['entry_points']) or 'None detected'}")
        print(f"  - Parse Success Rate: {summary['parse_success_rate']}%")

        if summary['warnings']:
            print(f"\nWarnings:")
            for warning in summary['warnings']:
                print(f"  - {warning}")

        print(f"\n{'='*80}")
        print("PARSED FILES:")
        print(f"{'='*80}")

        modules = result['modules']
        for i, (path, file_data) in enumerate(list(modules.items())[:5], 1):
            print(f"\n{i}. {path}")
            print(f"   Language: {file_data['language'] or 'Unknown'}")
            print(f"   Size: {file_data['metadata']['size_bytes']} bytes")
            print(f"   Tags: {', '.join(file_data['metadata']['tags']) or 'None'}")
            if file_data['metadata']['summary']:
                print(f"   Summary: {file_data['metadata']['summary']}")
            print(f"   Content Preview: {file_data['content'][:200]}...")

        if len(modules) > 5:
            print(f"\n... and {len(modules) - 5} more files")

        print(f"\n{'='*80}")
        print(f"Full response saved to: parse_result.json")
        print(f"{'='*80}\n")

        # Save full response
        with open("parse_result.json", "w") as f:
            json.dump(result, f, indent=2)

        return True
    else:
        print(f"✗ FAILED - Error parsing repository")
        print(f"\nError Response:")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
        except:
            print(response.text)
        return False


def main():
    """Main test function."""
    # Use a small public repository for testing
    test_repos = [
        "https://github.com/microsoft/agent-framework/tree/main/workflow-samples",  # Small, well-structured Python project
    ]

    try:
        print("Authenticating...")
        token = get_auth_token()
        print("✓ Authentication successful\n")

        for repo_url in test_repos:
            success = test_parse_endpoint(token, repo_url)
            if not success:
                print("\nTest failed!")
                sys.exit(1)

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
