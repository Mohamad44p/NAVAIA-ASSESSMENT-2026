"""Phase 5 — sync the workforce to the Fareegi cloud and publish it.

Pushes the local workforce (with its completed task + conversations) to
``fareegi.navaia.sa``, then lists it on the marketplace. Requires
``NAVAIA_CLOUD_API_KEY`` in ``.env.local``.

    python 04_sync_publish.py
"""

from __future__ import annotations

from navaia_forge import NavaiaForgeError, SyncConflictError

import config
import content_studio as cs


def main() -> int:
    state = config.load_state()
    wf_id = state.get("workforce_id")
    if not wf_id:
        print("No workforce_id in state. Run 02_build_workforce.py first.")
        return 1

    local = config.local_client()
    cloud = config.cloud_client()

    # 1. Sync local -> cloud (include the completed task as proof of work).
    print("[..] pushing workforce to cloud (fareegi.navaia.sa)...")
    try:
        result = local.sync.push(
            wf_id, remote=cloud, include_tasks=True, include_conversations=True
        )
    except SyncConflictError:
        print("[info] remote was modified since last sync; forcing local version...")
        result = local.sync.push(
            wf_id, remote=cloud, include_tasks=True, include_conversations=True, force=True
        )

    print(f"[ok] synced: action={result.action} cloud_id={result.workforce_id}")
    print(f"     agents={result.agents} edges={result.edges} tasks={result.tasks_imported}")
    config.save_state(cloud_workforce_id=result.workforce_id, sync_action=result.action)

    # 2. Publish to the marketplace.
    pub = cs.PUBLISH
    print(f"[..] publishing (category={pub['category']}, price_cents={pub['price_cents']})...")
    try:
        published = cloud.workforces.publish(
            result.workforce_id,
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
