import shutil
from pathlib import Path

import pytest

from backend.tools import git_tools


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    monkeypatch.delenv("CBA_GIT_ALLOWED_HOSTS", raising=False)
    monkeypatch.delenv("CBA_GIT_ALLOWED_ORGS", raising=False)
    monkeypatch.delenv("CBA_GIT_CLONE_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("CBA_GIT_CLONE_SIZE_MB", raising=False)


def test_clone_repository_success(monkeypatch):
    monkeypatch.setenv("CBA_GIT_ALLOWED_HOSTS", "github.com")
    monkeypatch.setenv("CBA_GIT_ALLOWED_ORGS", "user")

    def fake_run(cmd, check, timeout, cwd, env):
        target = Path(cmd[-1])
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text("ok")
        assert env["GIT_TERMINAL_PROMPT"] == "0"
        return object()

    monkeypatch.setattr(git_tools.subprocess, "run", fake_run)

    repo_path = Path(git_tools.clone_repository("https://github.com/user/repo"))
    assert repo_path.exists()
    shutil.rmtree(repo_path.parent)


def test_clone_repository_rejects_disallowed_host(monkeypatch):
    monkeypatch.setenv("CBA_GIT_ALLOWED_HOSTS", "github.com")
    monkeypatch.setenv("CBA_GIT_ALLOWED_ORGS", "user")

    with pytest.raises(ValueError):
        git_tools.clone_repository("https://gitlab.com/user/repo")


def test_clone_repository_rejects_disallowed_org(monkeypatch):
    monkeypatch.setenv("CBA_GIT_ALLOWED_HOSTS", "github.com")
    monkeypatch.setenv("CBA_GIT_ALLOWED_ORGS", "trusted")

    with pytest.raises(ValueError):
        git_tools.clone_repository("https://github.com/user/repo")


def test_clone_repository_rejects_large_clone(monkeypatch):
    monkeypatch.setenv("CBA_GIT_ALLOWED_HOSTS", "github.com")
    monkeypatch.setenv("CBA_GIT_ALLOWED_ORGS", "user")
    monkeypatch.setenv("CBA_GIT_CLONE_SIZE_MB", "1")

    def fake_run(cmd, check, timeout, cwd, env):
        target = Path(cmd[-1])
        target.mkdir(parents=True, exist_ok=True)
        big_file = target / "blob.bin"
        big_file.write_bytes(b"1" * (2 * 1024 * 1024))
        return object()

    monkeypatch.setattr(git_tools.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError):
        git_tools.clone_repository("https://github.com/user/repo")
