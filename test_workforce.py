"""Validation tests for the Content Studio workforce definition.

Pure checks on the workforce spec — no backend required. Runs under pytest
(`pytest test_workforce.py`) or standalone (`python test_workforce.py`).
"""

from __future__ import annotations

import re

import content_studio as cs


def test_agent_count_within_bounds():
    assert 2 <= len(cs.AGENTS) <= 10, "workforce must have 2-10 agents"


def test_agents_are_complete():
    seen = set()
    for a in cs.AGENTS:
        assert a["name"] and a["name"] not in seen, f"missing/duplicate name: {a}"
        seen.add(a["name"])
        assert a["role"], f"{a['name']} missing role"
        assert len(a["instructions"]) > 100, f"{a['name']} instructions too thin"
        assert a["model_name"] == cs.MODEL


def test_model_id_is_fully_qualified():
    # OpenRouter ids look like "vendor/model" — never a bare alias like "sonnet".
    assert re.match(r"^[\w.-]+/[\w.\-:]+$", cs.MODEL), f"bad model id: {cs.MODEL}"
    assert cs.MODEL_PROVIDER == "openrouter"


def test_pipeline_is_a_connected_linear_chain():
    names = [a["name"] for a in cs.AGENTS]
    assert cs.PIPELINE == names, "PIPELINE order must match AGENTS order"
    # A linear chain over N nodes has exactly N-1 edges and visits every node.
    edges = list(zip(cs.PIPELINE, cs.PIPELINE[1:]))
    assert len(edges) == len(cs.PIPELINE) - 1
    assert {n for pair in edges for n in pair} == set(names), "graph is not connected"


def test_publish_metadata_is_valid():
    p = cs.PUBLISH
    assert p["tagline"] and len(p["tagline"]) <= 200
    assert p["category"] in {
        "research", "content", "sales", "support", "engineering", "business ops", "qa",
    }
    assert p["price_cents"] >= 0 and p["currency"]


def test_brand_config_is_sane():
    b = cs.BRAND
    assert b["audience"] and b["voice"]
    assert isinstance(b["banned_words"], list) and b["banned_words"]
    assert 300 <= b["article_words"] <= 3000


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
