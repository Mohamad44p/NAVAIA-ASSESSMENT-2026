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

**Tech choices & a real-world adaptation.** Every agent runs
`anthropic/claude-sonnet-4.5` via OpenRouter (one strong model everywhere for
reliability). The honest wrinkle: the published `latest` backend image doesn't
bundle any of the task-execution runtime CLIs (`genexa`/`claude`/`claw`), so
server-side multi-agent *task* runs can't execute on it. But the backend does
serve **chat** replies directly against OpenRouter using each conversation's
bound agent's own instructions. So I orchestrate the documented pipeline
client-side over the chat API (`pipeline.py`): each stage is one conversation
with that agent, fed the previous stage's output, the Editor does a focused
fact-check pass, and the package is assembled deterministically — which also
keeps every call under the backend's 60s chat timeout. The brief explicitly
supports "chat with your agents," and this is the kind of pragmatic adaptation
the real work calls for. (Full findings in the README.)

**How I used AI.** I built this with Claude Code: it read the actual installed
SDK source to get the API exactly right, scaffolded the phase scripts, and helped
shape the agent instructions. The content-engine concept (research → write →
*atomize* into per-channel formats) is adapted from a social-media automation app
I had previously explored, restructured here as a NavaiaForge multi-agent
workforce. The design decisions, structure, and final editing are my own.

<!-- Fill in after the live run / publish: -->
<!-- - Marketplace listing: https://fareegi.navaia.sa/... -->
<!-- - Example output: output/last_run.md -->
