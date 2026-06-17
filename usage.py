"""Rough token + cost estimate for a pipeline run.

The chat surface doesn't return exact token usage to the SDK, so we approximate
from text length (~4 chars/token) and OpenRouter's published per-token pricing.
Clearly an estimate — for exact spend, see the OpenRouter dashboard.
"""

from __future__ import annotations

from typing import Any

import httpx

_CHARS_PER_TOKEN = 4
_MODELS_URL = "https://openrouter.ai/api/v1/models"


def _pricing(model: str) -> dict[str, float] | None:
    """Return {prompt, completion} USD-per-token for the model, or None on failure."""
    try:
        data = httpx.get(_MODELS_URL, timeout=10).json()
    except Exception:
        return None
    for m in data.get("data", []):
        if m.get("id") == model:
            p = m.get("pricing", {})
            try:
                return {"prompt": float(p.get("prompt", 0)), "completion": float(p.get("completion", 0))}
            except (TypeError, ValueError):
                return None
    return None


def estimate(out: dict[str, Any], model: str) -> dict[str, Any]:
    """Estimate tokens + cost from the pipeline's stage outputs."""
    stages = ("dossier", "brief", "article", "social", "newsletter", "qa")
    out_chars = sum(len(out.get(s, "")) for s in stages)
    out_tokens = out_chars // _CHARS_PER_TOKEN
    # Each stage re-sends prior outputs as input, so input grows roughly cumulatively;
    # ~2x total output is a reasonable rough multiplier across the 5 stages.
    in_tokens = out_tokens * 2

    price = _pricing(model)
    usd = None
    if price:
        usd = in_tokens * price["prompt"] + out_tokens * price["completion"]
    return {"in_tokens": in_tokens, "out_tokens": out_tokens, "usd": usd}


def format_report(est: dict[str, Any], model: str) -> str:
    cost = f"~${est['usd']:.4f}" if est.get("usd") is not None else "(pricing unavailable)"
    return (
        f"usage (rough estimate, {model}): "
        f"~{est['in_tokens']:,} input + ~{est['out_tokens']:,} output tokens, {cost}"
    )
