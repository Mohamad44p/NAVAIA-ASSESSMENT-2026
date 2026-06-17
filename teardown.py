"""Stop the local backend stack.

    python teardown.py            # stop containers (keeps data volumes)
    python teardown.py --volumes  # also remove pgdata/weaviate/redis volumes
"""

from __future__ import annotations

import subprocess
import sys

import config

COMPOSE = ["docker", "compose", "-f", "docker-compose.dist.yml", "-f", "docker-compose.override.yml"]


def main() -> int:
    cmd = COMPOSE + ["down"]
    if "--volumes" in sys.argv or "-v" in sys.argv:
        cmd.append("--volumes")
        print("[..] bringing the stack down AND removing data volumes...")
    else:
        print("[..] bringing the stack down (data volumes preserved)...")
    return subprocess.run(cmd, cwd=str(config.ROOT)).returncode


if __name__ == "__main__":
    raise SystemExit(main())
