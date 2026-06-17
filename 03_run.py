"""Phase 4 — run the Content Studio pipeline and capture the result.

Drives the 5-agent pipeline over the chat surface (see pipeline.py) and saves the
content package plus each stage as its own artifact under ``output/``, then prints
a rough usage/cost estimate.

    python 03_run.py
"""

from __future__ import annotations

import os
import sys

from navaia_forge import NavaiaForgeError

import config
import content_studio as cs
import usage
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

    out = run_pipeline(client, wf_id, agent_ids, topic, cs.BRAND)

    # Save the combined package + each stage as its own artifact.
    out_dir = config.ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    artifacts = {
        "last_run.md": out["package"],
        "dossier.md": out["dossier"],
        "brief.md": out["brief"],
        "article.md": out["article"],
        "social.md": out["social"],
        "newsletter.md": out["newsletter"],
    }
    for name, text in artifacts.items():
        (out_dir / name).write_text(text or "", encoding="utf-8")

    print("\n[ok] pipeline complete — stage output sizes (chars):")
    for k in ("dossier", "brief", "article", "social", "newsletter", "qa"):
        print(f"     {k:10}: {len(out[k])}")
    print(f"[ok] artifacts written to {out_dir}\\  (last_run.md + per-stage files)")
    print("[..] " + usage.format_report(usage.estimate(out, cs.MODEL), cs.MODEL))

    config.save_state(last_topic=topic, last_pipeline_conversations=out["conversation_ids"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
