"""Phase 5 — sync the workforce to the Fareegi cloud and publish it.

Pushes the local workforce to ``fareegi.navaia.sa`` then lists it on the
marketplace. Requires ``NAVAIA_CLOUD_API_KEY`` in ``.env.local``.

Note on the push: the SDK's ``sync.push`` round-trips the export through a
pydantic model (dropping nulls / applying defaults), which re-serializes the
JSON and breaks the bundle's ``content_hash`` (the cloud rejects it with 422).
So we stream the *raw* export JSON straight from the local export endpoint to
the cloud import endpoint, preserving the exact bytes the hash was computed over.

    python 04_sync_publish.py
"""

from __future__ import annotations

from typing import Any

from navaia_forge import NavaiaForgeClient, NavaiaForgeError

import config
import content_studio as cs


def _raw_push(
    local: NavaiaForgeClient,
    cloud: NavaiaForgeClient,
    workforce_id: str,
    *,
    force: bool = False,
) -> Any:
    """Raw export -> import, bypassing the SDK model round-trip (preserves content_hash)."""
    raw = local.http.get(
        f"/sync/export/{workforce_id}",
        params={"include_tasks": False, "include_conversations": False},
    )
    resp = cloud.http.request_raw(
        "POST", "/sync/import", json_body=raw, params={"force": force}
    )
    if resp.status_code == 409:  # remote changed since last sync — take local
        print("[info] remote modified since last sync; forcing local version...")
        resp = cloud.http.request_raw(
            "POST", "/sync/import", json_body=raw, params={"force": True}
        )
    return cloud.http.parse_response(resp)


def main() -> int:
    state = config.load_state()
    wf_id = state.get("workforce_id")
    if not wf_id:
        print("No workforce_id in state. Run 02_build_workforce.py first.")
        return 1

    local = config.local_client()
    cloud = config.cloud_client()

    # 1. Sync local -> cloud.
    print("[..] pushing workforce to cloud (fareegi.navaia.sa)...")
    try:
        result = _raw_push(local, cloud, wf_id)
    except NavaiaForgeError as exc:
        print(f"[fail] sync failed: {exc}")
        return 1

    cloud_wf_id = result["workforce_id"]
    print(f"[ok] synced: action={result.get('action', '?')} cloud_id={cloud_wf_id}")
    config.save_state(cloud_workforce_id=cloud_wf_id, sync_action=result.get("action"))

    # 2. Publish to the marketplace (skip if it's already listed — the sync above
    #    already updated the cloud agents/edges in place).
    try:
        existing = cloud.workforces.get(cloud_wf_id)
    except NavaiaForgeError:
        existing = None
    if existing is not None and existing.is_public:
        print(f"[ok] already published (moderation_status={existing.moderation_status}); "
              "sync refreshed the listing's agents in place.")
        config.save_state(published=True, moderation_status=existing.moderation_status)
        return 0

    pub = cs.PUBLISH
    print(f"[..] publishing (category={pub['category']}, price_cents={pub['price_cents']})...")
    try:
        published = cloud.workforces.publish(
            cloud_wf_id,
            tagline=pub["tagline"],
            category=pub["category"],
            price_cents=pub["price_cents"],
            currency=pub["currency"],
        )
    except NavaiaForgeError as exc:
        print(f"[fail] publish failed: {exc}")
        return 1

    print(f"[ok] published: is_public={published.is_public} "
          f"moderation_status={published.moderation_status}")
    print("     After the Navaia team approves it, the card appears at "
          "https://fareegi.navaia.sa")
    config.save_state(published=True, moderation_status=published.moderation_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
