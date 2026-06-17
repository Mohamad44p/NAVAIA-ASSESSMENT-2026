"""Convenience runner — Phases 2-4 in sequence (register if needed, build, run).

Phase 1 (backend) and Phase 5 (publish — outward-facing) are intentionally left
out; run those deliberately. Registration is skipped when a key already exists.

    python run_all.py
"""

from __future__ import annotations

import subprocess
import sys

import config


def main() -> int:
    scripts: list[str] = []
    if not config.local_api_key():
        scripts.append("01_register.py")
    scripts += ["02_build_workforce.py", "03_run.py"]

    for script in scripts:
        print(f"\n{'=' * 60}\n  {script}\n{'=' * 60}")
        result = subprocess.run([sys.executable, script], cwd=str(config.ROOT))
        if result.returncode != 0:
            print(f"[fail] {script} exited {result.returncode} — stopping.")
            return result.returncode
    print("\n[ok] build + run complete. Publish with: python 04_sync_publish.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
