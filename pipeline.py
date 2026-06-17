"""Client-side orchestration of the Content Studio pipeline over the chat API.

Why client-side: the published backend image does not bundle the task-execution
runtime CLIs (`genexa` / `claude` / `claw`), so server-side multi-agent *task*
runs can't execute. The backend DOES generate chat replies directly against
OpenRouter, using each conversation's bound agent's own instructions + model.
So we run the documented pipeline

    Researcher -> Strategist -> Writer -> Repurposer -> Editor

by feeding each stage's output into the next agent's conversation. Real agents,
real Sonnet 4.5, real output. A compact "house style" block (audience, voice,
banned words) from the BRAND config is injected into every stage so the same
workforce can be retargeted to any brand. The final package is assembled
deterministically, which also keeps every LLM call under the backend's 60s
chat timeout.
"""

from __future__ import annotations

from typing import Any, Callable

from navaia_forge import NavaiaForgeClient

# Reply prefixes the backend returns when generation fails / isn't configured.
_FALLBACKS = ("Sorry — I couldn't generate", "I can't reach the language model")


def house_style(brand: dict[str, Any]) -> str:
    """A compact style header prepended to every stage's input."""
    banned = ", ".join(brand.get("banned_words", []))
    return (
        "House style (apply at every stage):\n"
        f"- Target audience: {brand['audience']}\n"
        f"- Voice: {brand['voice']}\n"
        f"- Avoid these words/phrases: {banned}\n"
        "---\n"
    )


def _ask(
    client: NavaiaForgeClient,
    workforce_id: str,
    agent_id: str,
    user_input: str,
    title: str,
    *,
    retries: int = 1,
) -> tuple[str, str]:
    """Open a fresh conversation bound to ``agent_id``, send one message, return its reply."""
    reply = ""
    convo_id = ""
    for _ in range(retries + 1):
        convo = client.conversations.create(workforce_id, title=title, agent_id=agent_id)
        convo_id = convo.id
        client.conversations.send_message(convo.id, user_input)
        reply = ""
        for m in client.conversations.messages(convo.id):
            if m.role == "assistant" and m.content:
                reply = m.content
        if reply and not any(reply.startswith(f) for f in _FALLBACKS):
            break
    return reply, convo_id


def _split_social_newsletter(repurposed: str) -> tuple[str, str]:
    """Split the Repurposer output into (social pack, newsletter) on the newsletter header."""
    for marker in ("## Newsletter Issue", "## Newsletter", "Newsletter Issue"):
        idx = repurposed.find(marker)
        if idx != -1:
            return repurposed[:idx].rstrip(), repurposed[idx:].strip()
    return repurposed, ""  # no newsletter header found — keep it all as the social pack


def run_pipeline(
    client: NavaiaForgeClient,
    workforce_id: str,
    agent_ids: dict[str, str],
    topic: str,
    brand: dict[str, Any],
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Run the five stages in order and return every stage output + assembled package."""
    style = house_style(brand)
    words = brand.get("article_words", 800)
    convo_ids: dict[str, str] = {}

    log("[1/5] Researcher  - gathering research...")
    dossier, convo_ids["Researcher"] = _ask(
        client, workforce_id, agent_ids["Researcher"],
        f"{style}Topic: {topic}\n\nProduce the research dossier for this topic.",
        "Stage 1 - Research",
    )
    log(f"      dossier: {len(dossier)} chars")

    log("[2/5] Strategist  - building the marketing brief...")
    brief, convo_ids["Strategist"] = _ask(
        client, workforce_id, agent_ids["Strategist"],
        f"{style}Topic: {topic}\n\nResearch dossier:\n\n{dossier}\n\nProduce the marketing brief.",
        "Stage 2 - Strategy",
    )
    log(f"      brief: {len(brief)} chars")

    log(f"[3/5] Writer      - drafting the article (~{words} words)...")
    article, convo_ids["Writer"] = _ask(
        client, workforce_id, agent_ids["Writer"],
        f"{style}Topic: {topic}\n\nMarketing brief:\n\n{brief}\n\nResearch dossier:\n\n{dossier}\n\n"
        f"Write the blog article now. Target about {words} words so it stays focused.",
        "Stage 3 - Writing",
    )
    log(f"      article: {len(article)} chars")

    log("[4/5] Repurposer  - atomizing into social + newsletter...")
    repurposed, convo_ids["Repurposer"] = _ask(
        client, workforce_id, agent_ids["Repurposer"],
        f"{style}Marketing brief:\n\n{brief}\n\nBlog article:\n\n{article}\n\n"
        "Atomize into the social pack and newsletter issue.",
        "Stage 4 - Repurpose",
    )
    social, newsletter = _split_social_newsletter(repurposed)
    log(f"      social: {len(social)} chars | newsletter: {len(newsletter)} chars")

    log("[5/5] Editor      - QA / fact-check against the research...")
    qa, convo_ids["Editor"] = _ask(
        client, workforce_id, agent_ids["Editor"],
        f"{style}Topic: {topic}\n\nResearch dossier:\n\n{dossier}\n\nArticle:\n\n{article}\n\n"
        f"Social + newsletter:\n\n{repurposed}\n\nRun your QA pass.",
        "Stage 5 - Editor QA",
    )
    log(f"      QA note: {len(qa)} chars")

    package = (
        f"# Content Package - {topic}\n\n"
        f"## Editor QA & Sign-off\n\n{qa}\n\n"
        f"## 1. Marketing Brief\n\n{brief}\n\n"
        f"## 2. Blog Article\n\n{article}\n\n"
        f"## 3. Social Pack\n\n{social}\n\n"
        f"## 4. Newsletter\n\n{newsletter}\n\n"
        "---\n\n"
        f"<details>\n<summary>Research dossier (source material)</summary>\n\n{dossier}\n\n</details>\n"
    )

    return {
        "topic": topic,
        "dossier": dossier,
        "brief": brief,
        "article": article,
        "social": social,
        "newsletter": newsletter,
        "qa": qa,
        "package": package,
        "conversation_ids": convo_ids,
    }
