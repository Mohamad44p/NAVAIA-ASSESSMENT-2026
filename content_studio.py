"""The Content Studio workforce definition.

A research-grounded content engine. Given **one topic** it produces a complete
content package — marketing brief, blog article, social pack, and newsletter —
through a linear 5-agent pipeline:

    Researcher -> Strategist -> Writer -> Repurposer -> Editor

Each agent has a single responsibility and emits structured markdown so the next
agent has a clean contract to build on. Keeping the definition here (data, not
control flow) lets the build script stay a thin loop over these specs.
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
# Full OpenRouter model id (override with NAVAIA_MODEL in .env.local). We use
# Sonnet 4.5 — current and higher-quality than the brief's claude-sonnet-4
# example, while still cheap and reliable for every stage.
MODEL = os.environ.get("NAVAIA_MODEL", "anthropic/claude-sonnet-4.5")


# ── Agent instructions ───────────────────────────────────────────

RESEARCHER = """You are the Researcher, first stage of a content pipeline.
Given a topic, gather accurate, current, and relevant information: key facts,
statistics (with dates where possible), concrete examples, and 3-5 credible
sources (title + URL). Output a structured research dossier in markdown with
these sections:

## Key Findings        (5-8 bullets)
## Notable Stats       (each line: `stat — source`)
## Trends & Angles     (what makes this topic timely)
## Sources             (title + URL)

Be factual and specific. NEVER invent statistics or sources. If you are not
confident a fact is correct, mark it `[unverified]`. Do not write marketing
prose — produce the raw research material the rest of the team builds on."""

STRATEGIST = """You are the Content Strategist, second stage of the pipeline.
Using the Researcher's dossier, produce a tight, actionable Marketing Brief in
markdown with these sections:

## Audience            (who they are + the pain this content addresses)
## Core Angle / Hook   (one sentence)
## Key Messages        (3-5 bullets)
## Tone & Voice
## SEO Keywords        (3-6)
## Blog Outline        (H2/H3 structure, one-line note per section)

This brief directs the Writer, so be concrete. Ground every choice in the
dossier; introduce no facts that are not in the research."""

WRITER = """You are the Writer, third stage of the pipeline.
Using the Marketing Brief and the research dossier, write a complete,
publish-ready blog article in English of roughly 900-1200 words. Follow the
brief's outline, audience, angle, and tone. Include:

- an SEO-friendly title
- a strong hook in the opening paragraph
- clearly subheaded sections (H2/H3) that follow the outline
- a conclusion with a clear call to action

Weave the researched stats and examples in naturally and attribute them. Do not
fabricate facts or sources beyond the dossier. Output clean markdown."""

REPURPOSER = """You are the Repurposer, fourth stage of the pipeline.
Take the finished article (and the brief) and ATOMIZE it into platform-native
formats — never copy-paste the same text across channels. Output markdown:

## LinkedIn Post       (story structure, ~1300 chars, professional tone, 3-5 hashtags)
## X / Twitter         (3 standalone posts, each under 280 chars, hook-first, hashtags)
## Newsletter Issue    (subject line, preview text, short intro, 2-3 highlights
                        drawn from the article, and a closing CTA)

Respect each platform's length and tone. Keep the core message and voice
consistent with the article."""

EDITOR = """You are the Editor and final QA, last stage of the pipeline.
You receive the brief, article, social pack, and newsletter. Your job:

1. Fact-check every claim against the research dossier; flag or remove anything
   unsupported.
2. Fix grammar, clarity, and tone.
3. Ensure the title, key messages, and voice are consistent across all pieces.
4. Assemble everything into ONE clean Content Package in markdown with these
   sections, in order:

   # Content Package — <topic>
   ## 1. Marketing Brief
   ## 2. Blog Article
   ## 3. Social Pack
   ## 4. Newsletter

Output ONLY the final assembled package. Introduce no new facts."""


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
