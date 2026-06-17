# Write-up — Content Studio

**What it does.** Content Studio is a 5-agent NavaiaForge workforce that turns a
single topic into a complete, research-grounded content package: a marketing
brief, a publish-ready blog article, a social pack (LinkedIn + X), and a
newsletter issue. One research pass feeds every downstream format.

**Why this shape.** It mirrors a real editorial workflow as a linear pipeline —
**Researcher → Strategist → Writer → Repurposer → Editor** — where each agent
has exactly one responsibility and hands structured markdown to the next. I
chose a focused linear graph over a flashier fan-out because the brief rewards a
workforce that *clearly works* over an ambitious one that half-runs, and because
single-responsibility agents are easy to reason about, debug, and judge. Two
deliberate quality choices: the Researcher must cite sources and mark anything
uncertain `[unverified]`, and the Editor fact-checks every claim back against the
research dossier — so the output stays grounded rather than hallucinated.

**Tech choices.** `runtime_mode="navaia_code"` (the OpenRouter-backed runtime)
with every agent on `anthropic/claude-sonnet-4`. I started with one strong model
everywhere for reliability; the design notes a follow-up option to drop the
mechanical stages (Researcher, Repurposer) to a cheaper model to trim cost.

**How I used AI.** I built this with Claude Code: it read the actual installed
SDK source to get the API exactly right, scaffolded the phase scripts, and helped
shape the agent instructions. The content-engine concept (research → write →
*atomize* into per-channel formats) is adapted from a social-media automation app
I had previously explored, restructured here as a NavaiaForge multi-agent
workforce. The design decisions, structure, and final editing are my own.

<!-- Fill in after the live run / publish: -->
<!-- - Marketplace listing: https://fareegi.navaia.sa/... -->
<!-- - Example output: output/last_run.md -->
