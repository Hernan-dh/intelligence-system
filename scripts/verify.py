"""Verify that the project is safe and reproducible to publish."""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md", ".env.example", ".gitignore", ".dockerignore", "requirements.txt",
    "AGENTS.md", "docs/ARCHITECTURE.md", "docs/OPERATIONS.md", "docs/decisions/README.md",
)
PRIVATE_NAMES = {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
PRIVATE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
IGNORED_PARTS = {".venv", "venv", "__pycache__", ".pytest_cache", ".pytest-tmp", "data"}
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yml", ".yaml", ".json", ".sh", ".ps1", ".txt"}
SECRET_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"\b(?:gsk_|github_pat_|sk-or-v1)[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def project_python() -> str:
    """Use this project's environment even when another virtualenv is active."""
    executable = ROOT / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    return str(executable) if executable.is_file() else sys.executable


def public_files() -> list[Path]:
    return [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in PRIVATE_NAMES
        and not path.name.startswith(".env.")
        and not set(path.relative_to(ROOT).parts) & IGNORED_PARTS
    ]


def main() -> int:
    errors: list[str] = []
    files = public_files()
    print("[check] required files and source hygiene")
    for item in REQUIRED_FILES:
        if not (ROOT / item).is_file():
            errors.append(f"Missing required file: {item}")
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".env" not in ignored:
        errors.append(".env is not ignored")
    for path in files:
        relative = path.relative_to(ROOT)
        if path.name in PRIVATE_NAMES or (path.name.startswith(".env.") and path.name != ".env.example"):
            errors.append(f"Private file would be published: {relative}")
        if path.suffix.lower() in PRIVATE_SUFFIXES:
            errors.append(f"Private key file would be published: {relative}")
        if path.stat().st_size > 5 * 1024 * 1024:
            errors.append(f"File exceeds 5 MiB: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 1024 * 1024:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"Text file is not UTF-8: {relative}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                errors.append(f"Potential secret in {relative}")
                break

    print("[check] Python syntax")
    for path in files:
        if path.suffix != ".py":
            continue
        try:
            with tokenize.open(path) as source:
                ast.parse(source.read(), filename=str(path))
        except (SyntaxError, UnicodeError) as error:
            errors.append(f"Invalid Python in {path.relative_to(ROOT)}: {error}")

    print("[check] tests")
    # The checkout may have been moved from another Windows account, leaving
    # its old pytest cache or the user's shared TEMP directory inaccessible.
    # A fresh, ignored directory beneath this writable project avoids both.
    test_temp = tempfile.mkdtemp(prefix=".verify-", dir=ROOT)
    environment = {**os.environ, "TMP": test_temp, "TEMP": test_temp, "TMPDIR": test_temp}
    result = subprocess.run(
        [project_python(), "-m", "pytest", "-q", f"--basetemp={test_temp}"],
        cwd=ROOT, env=environment, check=False,
    )
    if result.returncode:
        errors.append("pytest failed")
    if errors:
        print("\nVerification failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("\nVerification completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
