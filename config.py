"""Shared configuration, client construction, and run-state for Content Studio.

Loads key/value config from ``.env`` and ``.env.local`` with no extra
dependencies, builds the local + cloud SDK clients, and persists run state
(local API key, workforce id, agent ids) to a git-ignored ``.forge_state.json``
so each phase script can run independently.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from navaia_forge import NavaiaForgeClient

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / ".forge_state.json"

CLOUD_BASE_URL = "https://fareegi.navaia.sa"


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a minimal ``KEY=VALUE`` env file (ignores blanks and ``#`` comments)."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            values[key] = val
    return values


def load_env() -> None:
    """Load ``.env`` then ``.env.local`` into ``os.environ`` (never overwriting real env vars)."""
    for name in (".env", ".env.local"):
        for key, val in _parse_env_file(ROOT / name).items():
            os.environ.setdefault(key, val)


load_env()


def local_base_url() -> str:
    """Resolve the local backend URL (honours ``NAVAIA_LOCAL_URL`` / ``API_PORT``)."""
    explicit = os.environ.get("NAVAIA_LOCAL_URL")
    if explicit:
        return explicit.rstrip("/")
    port = os.environ.get("API_PORT", "8001")
    return f"http://localhost:{port}"


# ── Run-state persistence ────────────────────────────────────────


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(**updates: Any) -> dict[str, Any]:
    """Merge ``updates`` (skipping ``None``) into the state file and return it."""
    state = load_state()
    state.update({k: v for k, v in updates.items() if v is not None})
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


# ── Clients ──────────────────────────────────────────────────────


def local_api_key() -> str:
    return os.environ.get("NAVAIA_LOCAL_API_KEY") or load_state().get("local_api_key", "")


def local_client(api_key: str | None = None) -> NavaiaForgeClient:
    """Client pointed at the local backend; uses the saved API key by default."""
    return NavaiaForgeClient(
        base_url=local_base_url(),
        api_key=api_key if api_key is not None else local_api_key(),
        timeout=120.0,
    )


def cloud_client() -> NavaiaForgeClient:
    """Client pointed at the Fareegi cloud; requires ``NAVAIA_CLOUD_API_KEY``."""
    key = os.environ.get("NAVAIA_CLOUD_API_KEY", "")
    if not key or key.startswith("nf_cloud_..."):
        raise SystemExit(
            "Missing NAVAIA_CLOUD_API_KEY.\n"
            "Create a cloud account + key at https://fareegi.navaia.sa "
            "(Settings > Manage API keys) and add it to .env.local."
        )
    return NavaiaForgeClient(base_url=CLOUD_BASE_URL, api_key=key, timeout=120.0)
