# Content Studio — a NavaiaForge Workforce

A research-grounded **content engine** built on the NavaiaForge SDK. Give it one
topic and a 5-agent pipeline returns a complete content package:

> **Researcher → Strategist → Writer → Repurposer → Editor**

| Agent | Job | Produces |
|-------|-----|----------|
| **Researcher** | Find accurate facts, stats, sources | research dossier |
| **Strategist** | Audience, angle, key messages, outline | marketing brief |
| **Writer** | Write the article from brief + research | blog article (~900–1200 words) |
| **Repurposer** | Atomize the article into channels | LinkedIn + 3× X posts + newsletter |
| **Editor** | Fact-check vs. research, polish, assemble | final content package |

Built for the NavaiaForge SDK assessment (AI Engineer Intern track). Design spec:
[`docs/superpowers/specs/2026-06-17-content-studio-workforce-design.md`](docs/superpowers/specs/2026-06-17-content-studio-workforce-design.md).

---

## Prerequisites

- Docker 24+ with Compose v2
- Python ≥ 3.10
- An [OpenRouter API key](https://openrouter.ai/keys) with credits

## Setup

```bash
pip install -r requirements.txt

cp .env.example .env            # backend config — add your OPENROUTER_API_KEY
cp .env.local.example .env.local  # SDK config — add your account email/password
```

Generate the random secrets for `.env` (Windows-friendly):

```bash
python -c "import secrets; print(secrets.token_hex(32))"   # SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"   # WEAVIATE_API_KEY
```

## Run it (phase by phase)

```bash
# Phase 1 — start the backend, then verify health
docker compose -f docker-compose.dist.yml up -d
curl http://localhost:8001/health

# Phase 2 — register + mint a local API key  (saved to .forge_state.json)
python 01_register.py

# Phase 3 — create the workforce (5 agents + 4 edges)
python 02_build_workforce.py

# Phase 4 — run a task and capture the result  (output/last_run.md)
python 03_run.py

# Phase 5 — sync to the cloud and publish to the marketplace
#   (add NAVAIA_CLOUD_API_KEY from fareegi.navaia.sa to .env.local first)
python 04_sync_publish.py
```

## Project layout

```
config.py             shared client construction + run-state (.forge_state.json)
content_studio.py     the workforce definition: agents, instructions, edges, listing
01_register.py        Phase 2 — account + API key
02_build_workforce.py Phase 3 — workforce, agents, edges
03_run.py             Phase 4 — run a task, save the result
04_sync_publish.py    Phase 5 — sync to cloud + publish
output/               generated task results (committed as evidence)
docs/                 design spec
```

## Configuration notes

- **`runtime_mode="navaia_code"`** — the OpenRouter-backed runtime (the SDK
  default `claude_max` would require Claude Code on the backend host).
- **Models** — every agent uses `anthropic/claude-sonnet-4` via OpenRouter.
  Override globally with `NAVAIA_MODEL` in `.env.local`.
- **Secrets** — `.env`, `.env.local`, and `.forge_state.json` are git-ignored.
