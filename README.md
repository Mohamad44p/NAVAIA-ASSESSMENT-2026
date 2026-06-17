# Content Studio — a NavaiaForge Workforce

A research-grounded **content engine** built on the NavaiaForge SDK. Give it one
topic and a 5-agent pipeline returns a complete content package:

> **Researcher → Strategist → Writer → Repurposer → Editor**

| Agent | Job | Produces |
|-------|-----|----------|
| **Researcher** | Find accurate facts, stats, sources | research dossier |
| **Strategist** | Audience, angle, key messages, outline | marketing brief |
| **Writer** | Write the article from brief + research | blog article (~900 words) |
| **Repurposer** | Atomize the article into channels | LinkedIn + 3× X posts + newsletter |
| **Editor** | Fact-check vs. research, QA sign-off | verified, assembled package |

Built for the NavaiaForge SDK assessment (AI Engineer Intern track). A real
example run is committed at [`output/last_run.md`](output/last_run.md). Design
spec: [`docs/superpowers/specs/2026-06-17-content-studio-workforce-design.md`](docs/superpowers/specs/2026-06-17-content-studio-workforce-design.md).

---

## Prerequisites

- Docker 24+ with Compose v2
- Python ≥ 3.10
- An [OpenRouter API key](https://openrouter.ai/keys) with credits

## Setup

```bash
pip install -r requirements.txt

cp .env.example .env              # backend config — add OPENROUTER_API_KEY + secrets
cp .env.local.example .env.local  # SDK config — add account email/password
```

Generate the secrets `.env` needs:

```bash
python -c "import secrets; print(secrets.token_hex(32))"                       # SECRET_KEY, WEAVIATE_API_KEY
python -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"  # GITHUB_TOKEN_ENC_KEY
```

## Run it (phase by phase)

```bash
# Phase 1 — start the backend.
#   On amd64 hosts the backend image is arm64-only, so include the emulation override:
docker compose -f docker-compose.dist.yml -f docker-compose.override.yml up -d
#   (on arm64 hosts the override is a no-op; you can omit it)

#   Apply the database schema (one-shot; the image does not auto-migrate on Postgres):
docker exec -w /app navaia-forge-api alembic upgrade head

#   Verify:
curl http://localhost:8001/health        # {"status":"healthy","version":"0.1.0"}

# Phase 2 — register + mint a local API key (saved to .forge_state.json)
python 01_register.py

# Phase 3 — create the workforce (5 agents + 4 edges)
python 02_build_workforce.py

# Phase 4 — run the pipeline and save the content package to output/last_run.md
python 03_run.py

# Phase 5 — sync to the cloud and publish to the marketplace
#   (add NAVAIA_CLOUD_API_KEY from fareegi.navaia.sa to .env.local first)
python 04_sync_publish.py
```

## Project layout

```
config.py             shared client construction + run-state (.forge_state.json)
content_studio.py     the workforce definition: agents, instructions, edges, listing
pipeline.py           client-side orchestration of the 5-agent pipeline (see note below)
01_register.py        Phase 2 — account + API key
02_build_workforce.py Phase 3 — workforce, agents, edges
03_run.py             Phase 4 — run the pipeline, save the result
04_sync_publish.py    Phase 5 — sync to cloud + publish
output/last_run.md    a real generated content package (evidence)
docs/                 design spec
```

---

## Notes from getting it running

The brief is a *reference, not a spec*, and the published `latest` backend image
differs from it in a few ways. What I found and how I handled it:

1. **Execution runtime.** `runtime_mode="navaia_code"` (from the brief) isn't a
   branch in this image — it falls through to `claude_max`, which shells out to a
   `claude` CLI that isn't installed. In fact **none** of the task-execution
   runtime CLIs (`genexa` / `claude` / `claw`) or the OpenHands SDK are bundled,
   so server-side multi-agent *task* runs can't execute on this image.
   **However**, the backend generates **chat** replies directly against OpenRouter
   (`conversations/llm.py`), using each conversation's bound agent's own
   instructions + model. So Phase 4 orchestrates the documented pipeline over the
   chat surface (`pipeline.py`): each stage is one conversation with that agent,
   fed the previous stage's output. Real agents, real Sonnet 4.5, real output —
   and the brief explicitly supports "chat with your agents."
2. **Database schema.** On Postgres the image deliberately skips `create_all`; you
   must run `alembic upgrade head` once (above).
3. **Startup guards.** In production mode the API refuses to boot unless
   `ALLOWED_ORIGINS` includes a non-localhost origin, and it requires a
   `GITHUB_TOKEN_ENC_KEY` (Fernet). Both are in `.env.example`.
4. **Architecture.** The backend image is published for `linux/arm64` only;
   `docker-compose.override.yml` runs it under emulation on amd64.
5. **API-key auth.** `/auth/keys` authenticates via `Authorization: Bearer <jwt>`,
   not `X-API-Key` — `01_register.py` sends the token accordingly.

## Configuration notes

- **Models** — every agent uses `anthropic/claude-sonnet-4.5` via OpenRouter
  (current, higher quality than the brief's `claude-sonnet-4` example, equally
  well-supported). Override globally with `NAVAIA_MODEL` in `.env.local`.
- **Secrets** — `.env`, `.env.local`, and `.forge_state.json` are git-ignored.
