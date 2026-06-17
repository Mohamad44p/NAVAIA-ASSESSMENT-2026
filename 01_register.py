"""Phase 2 — register an account on the local backend and mint an API key.

Idempotent: if the email is already registered it falls back to login. The
resulting long-lived key (``nf_...``) is saved to ``.forge_state.json`` for the
later phase scripts.

    python 01_register.py
"""

from __future__ import annotations

import os

from navaia_forge import NavaiaForgeClient, NavaiaForgeError

import config


def main() -> int:
    name = os.environ.get("NAVAIA_NAME", "NavaiaForge Builder")
    email = os.environ.get("NAVAIA_EMAIL")
    password = os.environ.get("NAVAIA_PASSWORD")
    if not email or not password:
        print("Set NAVAIA_EMAIL and NAVAIA_PASSWORD in .env.local first "
              "(copy from .env.local.example).")
        return 1

    base = config.local_base_url()
    anon = NavaiaForgeClient(base_url=base, api_key="", timeout=60.0)

    # 1. Backend reachable?
    try:
        health = anon.health()
        print(f"[ok] backend healthy at {base}: {health}")
    except NavaiaForgeError as exc:
        print(f"[fail] backend not reachable at {base}: {exc}")
        print("       Did you run: docker compose -f docker-compose.dist.yml up -d ?")
        return 1

    # 2. Register, or log in if the account already exists.
    try:
        pair = anon.auth.register(name=name, email=email, password=password)
        print(f"[ok] registered new account: {email}")
    except NavaiaForgeError as exc:
        print(f"[info] register returned {exc.status_code}; trying login instead...")
        pair = anon.auth.login(email=email, password=password)
        print(f"[ok] logged in as: {email}")

    # 3. Mint a long-lived API key (shown once).
    authed = NavaiaForgeClient(base_url=base, api_key=pair.access_token, timeout=60.0)
    key = authed.auth.create_key("content-studio")
    config.save_state(local_api_key=key.api_key, account_email=email)
    print(f"[ok] created API key {key.api_key[:10]}... (saved to .forge_state.json)")

    # 4. Sanity-check the key.
    check = config.local_client().auth.validate()
    print(f"[ok] key valid={check.valid} user={check.user_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
