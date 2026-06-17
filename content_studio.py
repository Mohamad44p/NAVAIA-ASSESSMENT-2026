"""The Content Studio workforce definition.

A research-grounded content engine. Given **one topic** it produces a complete
content package — marketing brief, blog article, social pack, and newsletter —
through a linear 5-agent pipeline:

    Researcher -> Strategist -> Writer -> Repurposer -> Editor

Each agent has a single responsibility and emits structured markdown so the next
agent has a clean contract. The agent instructions enforce an anti-fabrication
discipline end-to-end (the Researcher won't invent precise stats/URLs; the Editor
flags anything unverifiable), which is what keeps the output trustworthy.
"""

from __future__ import annotations

import os

WORKFORCE_NAME = "Content Studio"
WORKFORCE_DESCRIPTION = (
    "A research-grounded content engine: turns one topic into a complete content "
    "package — marketing brief, blog article, social pack, and newsletter — from a "
    "single research pass."
)

# OpenRouter-backed runtime (the alternative, "claude_max", needs Claude Code on
# the backend host). The brief mandates the OpenRouter key, so we use navaia_code.
RUNTIME_MODE = "navaia_code"

MODEL_PROVIDER = "openrouter"
# Full OpenRouter model id (override with NAVAIA_MODEL in .env.local). Sonnet 4.5
# is current and higher-quality than the brief's claude-sonnet-4 example.
MODEL = os.environ.get("NAVAIA_MODEL", "anthropic/claude-sonnet-4.5")


# ── Brand / house style (override via env to retarget the same workforce) ──────

BRAND = {
    "audience": os.environ.get(
        "NAVAIA_AUDIENCE", "small business owners and operators (10-500 employees)"
    ),
    "voice": os.environ.get(
        "NAVAIA_VOICE",
        "pragmatic, peer-to-peer, evidence-based; plain English, no hype, no jargon",
    ),
    "banned_words": [
        "revolutionary", "game-changer", "game changer", "synergy", "unlock",
        "leverage", "delve", "elevate", "supercharge", "seamless", "cutting-edge",
    ],
    "article_words": int(os.environ.get("NAVAIA_ARTICLE_WORDS", "800")),
}


# ── Agent instructions ───────────────────────────────────────────

RESEARCHER = """You are the Researcher, first stage of a content pipeline.

Given a topic, assemble an accurate, useful research dossier in markdown:

## Key Findings     5-8 substantive, widely-accepted points
## Notable Figures  only quantitative claims you are genuinely confident are
                    accurate; phrase uncertain magnitudes qualitatively
                    ("a large majority", "roughly a third") and tag them [estimate]
## Trends & Angles  why this topic is timely
## Source Types     the KINDS of sources that support these points
                    (e.g. "vendor case studies", "industry analyst reports")

Integrity rules (these matter most):
- Do NOT fabricate precise statistics, dates, company names, or source URLs.
- If you can't recall an exact figure, give its qualitative shape and tag it
  [estimate] — never invent a specific number to sound authoritative.
- Do NOT invent citations or links. Name a specific source only if you are
  confident it exists and says what you claim; otherwise list source *types*.

Accurate-but-general beats specific-but-fabricated. No marketing prose."""

STRATEGIST = """You are the Content Strategist, second stage.

Using the Researcher's dossier, produce a tight, actionable Marketing Brief in
markdown:

## Audience          who they are + the pain this content addresses
## Core Angle / Hook one sentence
## Key Messages      3-5 bullets
## Tone & Voice
## SEO Keywords      3-6
## Blog Outline      H2/H3 structure, one-line note per section

Ground every point in the dossier; introduce no new facts. Preserve any
[estimate] tag on figures you carry over."""

WRITER = """You are the Writer, third stage.

Using the Marketing Brief and the dossier, write a complete, publish-ready blog
article in English. Follow the brief's outline, audience, angle, and tone.
Include an SEO-friendly title, a strong hook, clear H2/H3 sections, and a
conclusion with a call to action.

Rules:
- Use only facts present in the dossier; add no new statistics or sources.
- Present anything tagged [estimate] qualitatively, never as a hard number.
- Write naturally; avoid hype and cliche. Output clean markdown.
(The target length is given in the request.)"""

REPURPOSER = """You are the Repurposer, fourth stage.

Take the finished article and brief and ATOMIZE them into platform-native
formats — never copy-paste the same text. Output markdown:

## LinkedIn Post    story structure, ~1300 chars, professional tone, 3-5 hashtags
## X / Twitter      3 standalone posts, each under 280 chars, hook-first, hashtags
## Newsletter Issue subject line, preview text, short intro, 2-3 highlights drawn
                    from the article, and a closing CTA

Respect each platform's length and tone. Keep the core message and voice
consistent with the article. Do not introduce facts not in the article."""

EDITOR = """You are the Editor and final QA, last stage.

Review the pieces against the research dossier. Output ONLY:

1) Claims check — list the main factual claims; mark each Verified (clearly
   supported by the dossier) or Flagged. Flag and recommend softening or removing:
   any precise statistic, date, or named source that isn't clearly supported, and
   anything the dossier tagged [estimate] that a piece states as a hard fact.
2) Consistency — one line on title / voice consistency across the pieces.
3) Sign-off — 2-3 sentences.

Be strict: prefer flagging an unverifiable specific over letting it through. Do
NOT reproduce the brief, article, social posts, or newsletter text."""


# ── Agents (laid out left-to-right for a clean graph in the UI) ──

AGENTS: list[dict] = [
    {"name": "Researcher", "role": "research", "instructions": RESEARCHER},
    {"name": "Strategist", "role": "strategy", "instructions": STRATEGIST},
    {"name": "Writer", "role": "writer", "instructions": WRITER},
    {"name": "Repurposer", "role": "repurpose", "instructions": REPURPOSER},
    {"name": "Editor", "role": "editor", "instructions": EDITOR},
]

for _i, _spec in enumerate(AGENTS):
    _spec.setdefault("model_name", MODEL)
    _spec.setdefault("position_x", float(_i * 280))
    _spec.setdefault("position_y", 0.0)

# Linear handoff order — edges are created between consecutive agents.
PIPELINE: list[str] = [a["name"] for a in AGENTS]


# ── Demo task (Phase 4) ──────────────────────────────────────────

DEMO_TOPIC = "How AI customer-support agents are changing the game for small businesses"


# ── Marketplace listing (Phase 5) ────────────────────────────────

PUBLISH = {
    "tagline": (
        "Turn one topic into a full content package — brief, article, social posts, "
        "and newsletter, all from a single research pass."
    ),
    "category": "content",
    "price_cents": 0,  # free → installable immediately
    "currency": "SAR",
}
