"""Phase 4 — run the Content Studio pipeline and capture the result.

Drives the 5-agent pipeline over the chat surface (see pipeline.py — the backend
image ships chat-over-OpenRouter but not the task-runtime CLIs) and saves the
assembled content package to ``output/last_run.md`` as evidence.

    python 03_run.py
"""

from __future__ import annotations

import os
import sys

from navaia_forge import NavaiaForgeError

import config
import content_studio as cs
from pipeline import run_pipeline

# Windows consoles default to cp1252 and choke on emoji/unicode the models emit;
# emit UTF-8 (replacing anything unencodable) so console output never crashes.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def main() -> int:
    state = config.load_state()
    wf_id = state.get("workforce_id")
    agent_ids = state.get("agent_ids") or {}
    if not wf_id or not agent_ids:
        print("Missing workforce / agent ids in state. Run 02_build_workforce.py first.")
        return 1

    client = config.local_client()
    try:
        client.health()
    except NavaiaForgeError as exc:
        print(f"[fail] backend not reachable: {exc}")
        return 1

    topic = os.environ.get("NAVAIA_TOPIC", cs.DEMO_TOPIC)
    print(f"[..] running Content Studio pipeline on:\n     {topic}\n")

    out = run_pipeline(client, wf_id, agent_ids, topic)

    # Save the artifact FIRST so a console-encoding hiccup can never lose it.
    path = config.ROOT / "output" / "last_run.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(out["package"], encoding="utf-8")

    print("\n[ok] pipeline complete — stage output sizes (chars):")
    for k in ("dossier", "brief", "article", "social", "qa"):
        print(f"     {k:9}: {len(out[k])}")
    print(f"[ok] full content package ({len(out['package'])} chars) saved to {path}")

    config.save_state(
        last_topic=topic,
        last_pipeline_conversations=out["conversation_ids"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
