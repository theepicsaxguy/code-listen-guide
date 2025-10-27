"""GitHub API helper with optional App or token authentication."""

from __future__ import annotations

import logging
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

import os
import requests
from jose import jwt

logger = logging.getLogger(__name__)


@dataclass
class GitHubCredentials:
    """Authentication inputs for GitHub API access."""

    app_id: Optional[str]
    private_key: Optional[str]
    installation_id: Optional[str]
    personal_access_token: Optional[str]

    @property
    def has_app_credentials(self) -> bool:
        return all(
            value
            for value in (self.app_id, self.private_key, self.installation_id)
        )

    @property
    def has_personal_token(self) -> bool:
        return bool(self.personal_access_token)

    @property
    def has_any_credentials(self) -> bool:
        return self.has_app_credentials or self.has_personal_token

    @classmethod
    def from_environment(cls) -> "GitHubCredentials":
        private_key = os.getenv("GITHUB_PRIVATE_KEY")
        if private_key:
            private_key = private_key.replace("\\n", "\n")
        return cls(
            app_id=os.getenv("GITHUB_APP_ID"),
            private_key=private_key,
            installation_id=os.getenv("GITHUB_INSTALLATION_ID"),
            personal_access_token=os.getenv("GITHUB_PAT"),
        )


class GitHubService:
    """Fetch repository metadata and files from GitHub."""

    def __init__(
        self,
        credentials: Optional[GitHubCredentials] = None,
        session: Optional[requests.Session] = None,
        request_timeout_seconds: float = 10.0,
    ) -> None:
        self._credentials = credentials or GitHubCredentials.from_environment()
        self._session = session or requests.Session()
        self._timeout = request_timeout_seconds
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        if not self._credentials.has_any_credentials:
            logger.warning(
                "Proceeding without GitHub credentials; rate limit is limited to 60 requests per hour."
            )

    def get_default_branch(self, owner: str, repository: str) -> Optional[str]:
        """Return the default branch name for a repository."""

        response = self._request("GET", f"/repos/{owner}/{repository}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return data.get("default_branch")

    def list_repository_files(
        self,
        owner: str,
        repository: str,
        branch: Optional[str] = None,
    ) -> list[str]:
        """Return a filtered list of file paths for a repository."""

        branch_candidates: Iterable[str]
        if branch:
            branch_candidates = (branch,)
        else:
            default_branch = self.get_default_branch(owner, repository)
            if default_branch:
                branch_candidates = (default_branch,)
            else:
                branch_candidates = ("main", "master")
        for candidate in branch_candidates:
            paths = self._fetch_tree(owner, repository, candidate)
            if paths is not None:
                return paths
        raise ValueError("Unable to fetch repository tree; verify that the repository is public and the branch exists.")

    def get_readme(self, owner: str, repository: str) -> str:
        """Return the README contents for a repository."""

        response = self._request("GET", f"/repos/{owner}/{repository}/readme")
        if response.status_code == 404:
            raise ValueError("Repository not found.")
        response.raise_for_status()
        download_url = response.json().get("download_url")
        if not download_url:
            raise RuntimeError("README metadata did not include a download URL.")
        raw_response = self._session.get(download_url, timeout=self._timeout)
        raw_response.raise_for_status()
        return raw_response.text

    def get_file_contents(self, owner: str, repository: str, path: str) -> str:
        """Return decoded file contents for a repository path."""

        response = self._request(
            "GET", f"/repos/{owner}/{repository}/contents/{path}"
        )
        if response.status_code == 404:
            raise ValueError("File not found in the repository.")
        response.raise_for_status()
        payload = response.json()
        encoded = payload.get("content")
        if not encoded:
            raise RuntimeError("GitHub response did not include file content.")
        normalized = encoded.replace("\n", "")
        return b64decode(normalized).decode("utf-8")

    def _fetch_tree(
        self, owner: str, repository: str, branch: str
    ) -> Optional[list[str]]:
        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/git/trees/{branch}",
            params={"recursive": "1"},
        )
        if response.status_code != 200:
            return None
        data = response.json()
        tree = data.get("tree")
        if not isinstance(tree, list):
            return []
        return [
            entry["path"]
            for entry in tree
            if entry.get("type") == "blob"
            and self._include_path(entry.get("path", ""))
        ]

    def _include_path(self, path: str) -> bool:
        excluded_fragments = (
            "node_modules/",
            "vendor/",
            "venv/",
            ".min.",
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".class",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".ico",
            ".svg",
            ".ttf",
            ".woff",
            ".webp",
            "__pycache__/",
            ".cache/",
            ".tmp/",
            "yarn.lock",
            "poetry.lock",
            ".log",
            ".vscode/",
            ".idea/",
        )
        lower_path = path.lower()
        return all(fragment not in lower_path for fragment in excluded_fragments)

    def _request(self, method: str, path: str, **kwargs: object) -> requests.Response:
        url = f"https://api.github.com{path}"
        headers = kwargs.pop("headers", {})
        base_headers = {
            "Accept": "application/vnd.github+json",
            **self._authorization_headers(),
        }
        merged_headers = {**base_headers, **headers}
        response = self._session.request(
            method,
            url,
            headers=merged_headers,
            timeout=self._timeout,
            **kwargs,
        )
        return response

    def _authorization_headers(self) -> dict[str, str]:
        if self._credentials.has_personal_token:
            token = self._credentials.personal_access_token or ""
            return {"Authorization": f"token {token}"}
        if self._credentials.has_app_credentials:
            token = self._installation_token()
            return {
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        return {}

    def _installation_token(self) -> str:
        if self._access_token and self._token_expires_at:
            if datetime.now(timezone.utc) < self._token_expires_at:
                return self._access_token
        jwt_token = self._build_jwt()
        url = (
            "https://api.github.com/app/installations/"
            f"{self._credentials.installation_id}/access_tokens"
        )
        response = self._session.post(
            url,
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("token")
        if not token:
            raise RuntimeError("GitHub response did not include an access token.")
        self._access_token = token
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=55)
        return token

    def _build_jwt(self) -> str:
        if not self._credentials.has_app_credentials:
            raise RuntimeError("GitHub App credentials are required for JWT generation.")
        now = datetime.now(timezone.utc)
        payload = {
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
            "iss": self._credentials.app_id,
        }
        private_key = self._credentials.private_key or ""
        return jwt.encode(payload, private_key, algorithm="RS256")
