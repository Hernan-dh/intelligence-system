"""Install a local pre-commit hook that runs the public-source verifier."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    hooks_path = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--git-path", "hooks"],
        check=False, capture_output=True, text=True,
    )
    if hooks_path.returncode:
        print("Initialize this directory as a Git repository before installing hooks.", file=sys.stderr)
        return 1
    hook = (ROOT / hooks_path.stdout.strip()).resolve()
    hook.mkdir(parents=True, exist_ok=True)
    target = hook / "pre-commit"
    target.write_text(f"#!{sys.executable}\nimport subprocess, sys\nsys.exit(subprocess.call([{sys.executable!r}, 'scripts/verify.py']))\n", encoding="utf-8")
    print(f"Installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
