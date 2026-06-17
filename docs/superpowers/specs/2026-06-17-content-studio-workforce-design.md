# Content Studio — NavaiaForge Workforce Design

**Date:** 2026-06-17
**Author:** (candidate) — AI Engineer Intern assessment, NavaiaForge SDK track
**Status:** Approved design (pending spec review)

---

## 1. Problem & goal

Build a **multi-agent workforce** with the NavaiaForge SDK that solves a real
content-operations problem: turning a single topic into a complete, research-grounded
**content package**.

Give the workforce **one topic**, and it returns:

1. A **marketing brief** (audience, angle, key messages, outline)
2. A **publish-ready blog article** (~900–1200 words, English)
3. A **social pack** (1 LinkedIn post + 3 X/Twitter posts)
4. A **newsletter issue** (subject, intro, highlights, CTA)

All four are built from **one research pass** — the real "research once, repurpose many"
content-ops pattern. This is the deliverable that makes the workforce "not a toy."

### Success criteria (mapped to the rubric)
- **Gets it running (15%)** — backend up (`/health` OK), SDK installed, keys created.
- **Workforce design (25%)** — 5 agents with single, clear responsibilities and a sensible
  linear edge graph.
- **Functionality (25%)** — one task run produces a genuinely useful, consistent package.
- **SDK & code quality (15%)** — clean SDK usage, sensible model + instructions per agent.
- **Shipped (10%)** — synced to `fareegi.navaia.sa` and published (free) with tagline + category.
- **Communication (10%)** — short, honest write-up incl. how AI was used.

---

## 2. Scope

### In scope
- 5-agent linear workforce created entirely via the SDK.
- One verification task run (the demo topic below), result printed.
- Sync to cloud + publish to marketplace (free, `category="Content"`).
- A short write-up (`WRITEUP.md`).

### Out of scope (YAGNI)
- No custom UI — the assessment is SDK + backend only.
- No real web-browsing tools (agents reason from model knowledge; sources are model-provided
  and explicitly flagged `[unverified]` when not certain — see anti-hallucination rules).
- No multi-language output (English only, per decision).
- No fan-out/parallel graph — linear pipeline only.

---

## 3. Architecture — linear pipeline, 5 agents

```
Researcher → Strategist → Writer → Repurposer → Editor
```

Four edges, each `source → target`, defining strict handoff order. Each agent has exactly
one job and consumes the previous agent's output.

| # | Agent | role | Consumes | Produces |
|---|-------|------|----------|----------|
| 1 | Researcher  | `research`   | the topic              | research dossier |
| 2 | Strategist  | `strategy`   | dossier                | marketing brief |
| 3 | Writer      | `writer`     | brief + dossier        | blog article |
| 4 | Repurposer  | `repurpose`  | article + brief        | social pack + newsletter |
| 5 | Editor      | `editor`     | all of the above + dossier | final assembled package |

### Design provenance
Adapted from concepts in two prior projects on this machine:
- **`aisoical` / "Lemon AI"** (AI social-media platform) — the **Atomize** concept (one input →
  platform-native variants) shapes the **Repurposer**; its AI-writing-assistant behaviors shape
  the **Writer**.
- **`billix_agent_main`** — its anti-hallucination prompt section and FAST/PREMIUM model-tiering
  shape the **Researcher**/**Editor** fact-checking discipline and the optional model tiering below.

---

## 4. Agent instructions (the core of the build)

> These are the `instructions` strings passed to `agents.create(...)`. They are intentionally
> concrete: each agent outputs structured markdown so the next agent has a clean contract.

### 4.1 Researcher (`role="research"`)
> You are the Researcher. Given a topic, gather accurate, current, relevant information: key
> facts, statistics (with dates where possible), concrete examples, and 3–5 credible sources
> (title + URL). Output a structured research dossier in markdown with these sections:
> `## Key Findings` (bullets), `## Notable Stats` (`stat — source`), `## Trends & Angles`,
> `## Sources`. Be factual and specific. **Never invent statistics or sources.** If you are not
> confident a fact is correct, mark it `[unverified]`. Do not write marketing prose — produce
> raw research material the rest of the team builds on.

### 4.2 Strategist (`role="strategy"`)
> You are the Content Strategist. Using the research dossier, produce a Marketing Brief in
> markdown with: `## Audience` (who + their pain), `## Core Angle / Hook` (one sentence),
> `## Key Messages` (3–5 bullets), `## Tone & Voice`, `## SEO Keywords` (3–6), and
> `## Blog Outline` (H2/H3 structure, one-line note per section). Keep it tight and actionable —
> this brief directs the Writer. Ground every choice in the research; introduce no facts that
> are not in the dossier.

### 4.3 Writer (`role="writer"`)
> You are the Writer. Using the Marketing Brief and research dossier, write a complete,
> publish-ready blog article in English (~900–1200 words). Follow the brief's outline, audience,
> angle, and tone. Include an SEO-friendly title, a strong hook intro, clearly subheaded sections
> (H2/H3), and a conclusion with a call to action. Weave in the researched stats/examples
> naturally and attribute them. Do not fabricate facts or sources beyond the dossier. Output
> clean markdown.

### 4.4 Repurposer (`role="repurpose"`)
> You are the Repurposer. Take the finished article and brief and **atomize** them into
> platform-native formats — never copy-paste the same text. Produce in markdown:
> `## LinkedIn Post` (story structure, ~1300 chars, professional tone, 3–5 hashtags),
> `## X / Twitter` (3 standalone posts, each < 280 chars, hook-first, relevant hashtags),
> `## Newsletter Issue` (subject line, preview text, short intro, 2–3 highlights drawn from the
> article, closing CTA). Respect each platform's length and tone. Keep the core message and
> voice consistent with the article.

### 4.5 Editor (`role="editor"`)
> You are the Editor and final QA. You receive the brief, article, social pack, and newsletter.
> (1) Fact-check every claim against the research dossier; flag or remove anything unsupported.
> (2) Fix grammar, clarity, and tone. (3) Ensure the title, key messages, and voice are
> consistent across all pieces. (4) Assemble everything into one clean Content Package in
> markdown with sections: `# Content Package — <topic>`, `## 1. Marketing Brief`,
> `## 2. Blog Article`, `## 3. Social Pack`, `## 4. Newsletter`. Output only the final assembled
> package. Introduce no new facts.

---

## 5. Models

**Start uniform:** every agent uses the full OpenRouter model ID `anthropic/claude-sonnet-4`
(the brief's own example — reliable, strong writing). Exact ID to be verified against the live
OpenRouter model list at build time.

**Optional cost tiering** (borrowed from `billix` FAST/PREMIUM pools) — only if we want to trim
OpenRouter spend after a clean first run:
- Researcher, Repurposer → a faster/cheaper model.
- Strategist, Writer, Editor → keep the premium model (quality-critical).

Decision: ship uniform first for reliability; tiering is a follow-up, not a blocker.

---

## 6. Verification (Phase 4)

Run one task:

- **Demo topic:** *"How AI customer-support agents are changing the game for small businesses."*
  (Useful, easy to judge, and quietly on-brand for Navaia's market. Swappable.)
- Create task → `wait_for_completion` → print `status` + `result` (the assembled package).
- Optionally also exercise `conversations` to show chat works (the brief accepts either).

Pass condition: status completed and the result contains all four labeled sections with
coherent, on-topic content.

---

## 7. Ship (Phase 5)

- `local.sync.push(workforce_id, remote=cloud)` → capture cloud workforce ID.
- `cloud.workforces.publish(cloud_id, tagline=..., category="Content", price_cents=0, currency="SAR")`.
- Free (`price_cents=0`) → installable immediately, so the listing is verifiably live.
- Tagline (draft): *"Turn one topic into a full content package — brief, article, social posts, and newsletter, all from a single research pass."*

---

## 8. Code structure

Small, clean Python project (no framework beyond the SDK):

```
NAVAIA-ASSESSMENT-2026/
├── .env                     # backend env (Docker); not committed
├── docker-compose.dist.yml  # backend (downloaded in Phase 1)
├── config.py                # shared NavaiaForgeClient construction + key loading
├── 01_register.py           # register account + create long-lived API key (Phase 2)
├── 02_build_workforce.py    # create workforce + 5 agents + 4 edges (Phase 3)
├── 03_run.py                # run demo task, wait, print result (Phase 4)
├── 04_sync_publish.py       # sync to cloud + publish (Phase 5)
├── WRITEUP.md               # required short write-up (what / why / how AI used)
└── docs/superpowers/specs/  # this design + later the implementation plan
```

Keys/IDs (`nf_local_...`, `nf_cloud_...`, workforce id) flow between scripts via a local,
git-ignored file (e.g. `.secrets.json` or `.env.local`) written by `01`/`02` and read by later
scripts — no hardcoded secrets.

---

## 9. Known unknowns (resolve during implementation)

1. **Exact SDK signatures** — the brief shows examples; verify against the installed
   `navaia-forge` package (method names, kwargs, return shapes) before writing the scripts.
2. **Graph execution semantics** — confirm how the backend runs the task across edges (sequential
   handoff vs. other) on the first real run; adjust agent contracts if needed.
3. **Live OpenRouter model IDs** — confirm `anthropic/claude-sonnet-4` (or current equivalent)
   is available before the run.
4. **Prerequisites (gating)** — Docker 24+ running, Python ≥ 3.10, and an OpenRouter key with
   credits must be ready before Phase 1.

---

## 10. Write-up angle (Communication, 10%)

`WRITEUP.md` covers, in a few honest lines:
- **What:** a 5-agent Content Studio that turns a topic into a complete content package.
- **Why this shape:** linear pipeline mirrors a real editorial workflow; single-responsibility
  agents keep it reliable (per the brief's "focused beats ambitious" tip).
- **How AI was used:** built and iterated with Claude Code; adapted the content-engine concept
  from a prior social-media automation project (Lemon AI), restructured as a NavaiaForge workforce.
