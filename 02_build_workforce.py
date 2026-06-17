"""Phase 3 — build the Content Studio workforce: 5 agents + 4 pipeline edges.

Creates the workforce, every agent in ``content_studio.AGENTS``, and an edge
between each consecutive pair in ``content_studio.PIPELINE``. IDs are saved to
``.forge_state.json``.

    python 02_build_workforce.py
"""

from __future__ import annotations

from navaia_forge import NavaiaForgeError

import config
import content_studio as cs


def main() -> int:
    if not config.local_api_key():
        print("No local API key found. Run 01_register.py first.")
        return 1

    client = config.local_client()

    try:
        client.health()
    except NavaiaForgeError as exc:
        print(f"[fail] backend not reachable: {exc}")
        return 1

    # 1. Workforce.
    wf = client.workforces.create(
        name=cs.WORKFORCE_NAME,
        description=cs.WORKFORCE_DESCRIPTION,
        runtime_mode=cs.RUNTIME_MODE,
    )
    print(f"[ok] workforce '{wf.name}' ({wf.id}) runtime={wf.runtime_mode}")

    # 2. Agents.
    name_to_id: dict[str, str] = {}
    for spec in cs.AGENTS:
        agent = client.agents.create(
            workforce_id=wf.id,
            name=spec["name"],
            role=spec["role"],
            instructions=spec["instructions"],
            model_provider=cs.MODEL_PROVIDER,
            model_name=spec["model_name"],
            position_x=spec["position_x"],
            position_y=spec["position_y"],
        )
        name_to_id[spec["name"]] = agent.id
        print(f"   + {agent.name:<11} role={agent.role:<10} "
              f"model={agent.model_provider}/{agent.model_name} -> {agent.id}")

    # 3. Edges along the linear pipeline.
    edge_ids: list[str] = []
    for src, dst in zip(cs.PIPELINE, cs.PIPELINE[1:]):
        edge = client.workforces.edges.create(
            workforce_id=wf.id,
            source_agent_id=name_to_id[src],
            target_agent_id=name_to_id[dst],
            label=f"{src} -> {dst}",
        )
        edge_ids.append(edge.id)
        print(f"   ~ edge {src} -> {dst}")

    config.save_state(workforce_id=wf.id, agent_ids=name_to_id, edge_ids=edge_ids)
    print(f"[ok] saved workforce + {len(name_to_id)} agents + {len(edge_ids)} edges to state.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
