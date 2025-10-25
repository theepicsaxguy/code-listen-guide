import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Tuple
from urllib.parse import urlparse

import ipaddress


def clone_repository(url: str) -> str:
    host, _ = _validate_repository_url(url)
    sandbox = Path(tempfile.mkdtemp(prefix="cba_repo_"))
    destination = sandbox / "repo"
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    cleanup_required = True
    try:
        destination_parent = destination.parent
        destination_parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--single-branch",
                url,
                str(destination),
            ],
            check=True,
            timeout=_clone_timeout_seconds(),
            cwd=str(destination_parent),
            env=env,
        )
        _enforce_size_limit(destination, _clone_size_limit_bytes())
        cleanup_required = False
        return str(destination)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"Timed out cloning repository from {host} after {_clone_timeout_seconds()}s"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to clone repository: {exc}") from exc
    finally:
        if cleanup_required:
            shutil.rmtree(sandbox, ignore_errors=True)


def list_repository_files(path: str) -> List[str]:
    root = Path(path)
    results: List[str] = []
    for entry in root.rglob("*"):
        if entry.is_file() and ".git" not in entry.parts:
            results.append(str(entry.relative_to(root)))
    return results


def _validate_repository_url(url: str) -> Tuple[str, str]:
    if not url:
        raise ValueError("Repository URL is required")
    if url.startswith("git@"):
        host, owner = _parse_ssh_url(url)
    else:
        host, owner = _parse_https_url(url)
    if _is_local_address(host):
        raise ValueError("Local and private network hosts are not allowed")
    allowed_hosts = _allowed_git_hosts()
    if host not in allowed_hosts:
        raise ValueError(f"Git host '{host}' is not in the allow list")
    allowed_orgs = _allowed_git_organizations()
    if owner not in allowed_orgs:
        raise ValueError(f"Git organization '{owner}' is not in the allow list")
    return host, owner


def _parse_https_url(url: str) -> Tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        raise ValueError("Only HTTPS Git URLs are supported")
    host = (parsed.hostname or "").lower()
    path = parsed.path.strip("/")
    parts = [segment for segment in path.split("/") if segment]
    if len(parts) < 2:
        raise ValueError("Git URL must include organization and repository")
    if any(part == ".." for part in parts):
        raise ValueError("Path traversal is not allowed in Git URLs")
    owner = parts[0].lower()
    return host, owner


def _parse_ssh_url(url: str) -> Tuple[str, str]:
    try:
        prefix, path = url.split(":", 1)
        _, host = prefix.split("@", 1)
    except ValueError as exc:
        raise ValueError("Invalid SSH Git URL format") from exc
    clean_path = path.strip("/").replace(".git", "")
    parts = [segment for segment in clean_path.split("/") if segment]
    if len(parts) < 2:
        raise ValueError("Git URL must include organization and repository")
    if any(part == ".." for part in parts):
        raise ValueError("Path traversal is not allowed in Git URLs")
    owner = parts[0].lower()
    return host.lower(), owner


def _allowed_git_hosts() -> Tuple[str, ...]:
    return _read_env_csv("CBA_GIT_ALLOWED_HOSTS", ("github.com",))


def _allowed_git_organizations() -> Tuple[str, ...]:
    return _read_env_csv("CBA_GIT_ALLOWED_ORGS", ("codebase-audiobooks", "user"))


def _clone_timeout_seconds() -> int:
    return _read_env_int("CBA_GIT_CLONE_TIMEOUT_SECONDS", 60)


def _clone_size_limit_bytes() -> int:
    limit_mb = _read_env_int("CBA_GIT_CLONE_SIZE_MB", 500)
    return limit_mb * 1024 * 1024


def _read_env_csv(name: str, fallback: Tuple[str, ...]) -> Tuple[str, ...]:
    raw = os.getenv(name)
    if raw is None:
        return tuple(item.lower() for item in fallback)
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not values:
        return tuple(item.lower() for item in fallback)
    return tuple(values)


def _read_env_int(name: str, fallback: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def _is_local_address(host: str) -> bool:
    if host in {"localhost", ""}:
        return True
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return False


def _enforce_size_limit(path: Path, limit_bytes: int) -> None:
    if limit_bytes <= 0:
        return
    total_size = _directory_size(path)
    if total_size > limit_bytes:
        raise ValueError("Repository exceeds configured size limit")


def _directory_size(path: Path) -> int:
    total = 0
    for entry in _iter_files(path):
        total += entry.stat().st_size
    return total


def _iter_files(path: Path) -> Iterable[Path]:
    for entry in path.rglob("*"):
        if entry.is_file():
            yield entry
