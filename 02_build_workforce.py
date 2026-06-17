"""Phase 3 — build (or update) the Content Studio workforce: 5 agents + 4 edges.

Idempotent: re-running reuses the saved workforce, updates existing agents in
place (so edited instructions/models are pushed without duplicating), and creates
only missing edges. IDs are saved to ``.forge_state.json``.

    python 02_build_workforce.py
"""

from __future__ import annotations

from navaia_forge import NavaiaForgeError

import config
import content_studio as cs


def _get_or_create_workforce(client):
    state = config.load_state()
    wf_id = state.get("workforce_id")
    if wf_id:
        try:
            wf = client.workforces.get(wf_id)
            client.workforces.update(
                wf.id, name=cs.WORKFORCE_NAME, description=cs.WORKFORCE_DESCRIPTION,
                runtime_mode=cs.RUNTIME_MODE,
            )
            print(f"[ok] reusing workforce '{cs.WORKFORCE_NAME}' ({wf.id})")
            return wf.id
        except NavaiaForgeError:
            print("[info] saved workforce_id not found; creating a fresh workforce")
    wf = client.workforces.create(
        name=cs.WORKFORCE_NAME, description=cs.WORKFORCE_DESCRIPTION, runtime_mode=cs.RUNTIME_MODE,
    )
    print(f"[ok] created workforce '{wf.name}' ({wf.id})")
    return wf.id


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

    wf_id = _get_or_create_workforce(client)

    # Agents — update in place when they already exist, else create.
    existing = {a.name: a.id for a in client.agents.list(wf_id)}
    name_to_id: dict[str, str] = {}
    for spec in cs.AGENTS:
        fields = dict(
            role=spec["role"], instructions=spec["instructions"],
            model_provider=cs.MODEL_PROVIDER, model_name=spec["model_name"],
            position_x=spec["position_x"], position_y=spec["position_y"],
        )
        if spec["name"] in existing:
            agent = client.agents.update(existing[spec["name"]], **fields)
            verb = "updated"
        else:
            agent = client.agents.create(wf_id, name=spec["name"], **fields)
            verb = "created"
        name_to_id[spec["name"]] = agent.id
        print(f"   {verb:8} {agent.name:<11} role={agent.role:<10} model={agent.model_name}")

    # Edges — create only the consecutive pairs that don't already exist.
    have = {(e.source_agent_id, e.target_agent_id) for e in client.workforces.edges.list(wf_id)}
    edge_ids: list[str] = []
    for src, dst in zip(cs.PIPELINE, cs.PIPELINE[1:]):
        pair = (name_to_id[src], name_to_id[dst])
        if pair in have:
            print(f"   edge exists {src} -> {dst}")
            continue
        edge = client.workforces.edges.create(
            workforce_id=wf_id, source_agent_id=pair[0], target_agent_id=pair[1],
            label=f"{src} -> {dst}",
        )
        edge_ids.append(edge.id)
        print(f"   edge created {src} -> {dst}")

    config.save_state(workforce_id=wf_id, agent_ids=name_to_id)
    print(f"[ok] workforce ready — {len(name_to_id)} agents, "
          f"{len(have) + len(edge_ids)} edges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
