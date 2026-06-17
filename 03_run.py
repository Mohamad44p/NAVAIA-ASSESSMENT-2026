"""Phase 4 — run a task through the workforce and capture the result.

Creates a task (topic = ``NAVAIA_TOPIC`` or the demo topic), waits for the
pipeline to finish, prints the assembled package, and saves it to
``output/last_run.md`` as evidence.

    python 03_run.py
"""

from __future__ import annotations

import os
from pathlib import Path

from navaia_forge import NavaiaForgeError

import config
import content_studio as cs


def main() -> int:
    state = config.load_state()
    wf_id = state.get("workforce_id")
    if not wf_id:
        print("No workforce_id in state. Run 02_build_workforce.py first.")
        return 1

    client = config.local_client()
    topic = os.environ.get("NAVAIA_TOPIC", cs.DEMO_TOPIC)

    print(f"[..] creating task: {topic}")
    task = client.tasks.create(workforce_id=wf_id, title=topic)
    print(f"[ok] task {task.id} created (status={task.status}); waiting (up to 30 min)...")

    try:
        final = client.tasks.wait_for_completion(task.id, poll_interval=10.0, timeout=1800.0)
    except NavaiaForgeError as exc:
        print(f"[fail] {exc}")
        return 1

    print(f"[ok] final status: {final.status}")
    if final.error:
        print(f"[warn] error field: {final.error}")

    result = final.result or ""
    print("\n" + "=" * 72 + "\nRESULT\n" + "=" * 72)
    print(result if result else "(no result text on the task; check task logs / agent outputs)")

    out = config.ROOT / "output" / "last_run.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        f"# Content Studio — Task Result\n\n"
        f"- **Topic:** {topic}\n"
        f"- **Task ID:** {final.id}\n"
        f"- **Status:** {final.status}\n\n"
        f"---\n\n{result}\n",
        encoding="utf-8",
    )
    print(f"\n[ok] saved result to {out}")

    config.save_state(last_task_id=task.id, last_task_status=final.status)
    return 0 if final.status == "done" else 2


if __name__ == "__main__":
    raise SystemExit(main())
