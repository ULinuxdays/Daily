"""Deduplicate, rank, and summarize newsletter content."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from urllib.parse import urlparse

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import DigestSections, Item


def _fingerprint(item: Item) -> str:
    host = urlparse(item.url).netloc.lower().replace("www.", "")
    title = re.sub(r"[^a-z0-9 ]", "", item.title.lower())
    words = " ".join(title.split()[:8])
    return f"{host}:{words}"


def dedupe(items: list[Item]) -> list[Item]:
    seen: dict[str, Item] = {}
    for item in items:
        key = _fingerprint(item)
        current = seen.get(key)
        if not current or item.score > current.score or len(item.summary) > len(current.summary):
            seen[key] = item
    return list(seen.values())


def _heuristic_score(item: Item) -> float:
    score = item.score
    title = item.title.lower()
    for keyword, weight in {
        "breakthrough": 8,
        "record": 6,
        "grid": 5,
        "storage": 5,
        "policy": 4,
        "tariff": 4,
        "market": 3,
        "solar": 3,
        "wind": 3,
        "battery": 4,
        "acquisition": 7,
        "deal": 6,
        "financing": 7,
        "funding": 6,
        "investment": 7,
        "joint venture": 7,
        "project finance": 8,
        "raises": 5,
        "stake": 5,
        "ai act": 8,
        "regulation": 7,
        "governance": 7,
        "safety": 7,
        "alignment": 7,
        "benchmark": 5,
        "frontier": 5,
        "ethics": 5,
        "compute": 5,
        "chip": 5,
        "valuation": 6,
    }.items():
        if keyword in title:
            score += weight
    if item.published_at:
        score += 3
    if item.section_hint == "academic_spotlight":
        score += 5
    return score


def _clean_text(text: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", "", text).split())


def _trim_summary(text: str, max_words: int = 130) -> str:
    words = _clean_text(text).split()
    if not words:
        return ""
    trimmed = " ".join(words[:max_words])
    return trimmed + ("..." if len(words) > max_words else "")


def _ai_detail_context(item: Item) -> str:
    if item.section_hint == "governance":
        return (
            "Read this through three lenses: what obligation or incentive changes, who has to comply, and when the "
            "change becomes real rather than symbolic. The important details are scope, exemptions, reporting duties, "
            "auditability, enforcement authority, procurement effects, and whether the rule reaches frontier model "
            "developers, deployers, cloud providers, or downstream users."
        )
    if item.section_hint == "technical_development":
        return (
            "The useful technical question is what capability or efficiency changed and whether the evidence is strong. "
            "Look for the evaluation setup, baseline comparisons, data contamination risks, compute cost, reproducibility, "
            "failure modes, and whether the result improves real tasks or only moves a benchmark."
        )
    if item.section_hint == "ai_ethics":
        return (
            "The ethical weight depends on the affected group, the power imbalance, and whether the proposed remedy is "
            "operational. Watch for consent, fairness, attribution, labor impact, privacy, epistemic trust, and whether "
            "the argument changes product design, deployment review, or institutional accountability."
        )
    if item.section_hint == "xrisk_management":
        return (
            "For existential-risk management, separate vocabulary from control. The key question is whether this creates "
            "measurable risk reduction: stronger evaluations, deployment thresholds, incident reporting, model security, "
            "misuse monitoring, interpretability, or independent review that can constrain frontier deployment."
        )
    if item.section_hint == "business":
        return (
            "The business signal is where durable advantage may be forming: compute supply, distribution, data access, "
            "enterprise contracts, chip capacity, cloud partnerships, pricing power, or acquisition strategy. Watch whether "
            "capital spending converts into revenue and whether infrastructure bottlenecks change the competitive map."
        )
    return ""


def _fallback_summary(item: Item) -> str:
    is_ai_section = item.section_hint in {"governance", "technical_development", "ai_ethics", "xrisk_management", "business"}
    summary = _trim_summary(item.summary, max_words=220 if is_ai_section else 130)
    watch = _watch_context(item)
    if summary:
        extra = _ai_detail_context(item)
        if extra:
            return f"{summary}\n\nWhy it matters: {watch}\n\nWhat to examine: {extra}"
        return f"{summary}\n\nWhy it matters: {watch}"

    if item.section_hint == "business_deals":
        return (
            "This item was selected because it points to capital moving in the energy sector: financing, M&A, project "
            "development, PPAs, or strategic investment. The important business question is not just who announced the "
            "deal, but what it says about investor appetite, cost of capital, regional growth, technology risk, and "
            "which parts of the energy value chain are attracting money."
        )
    if item.section_hint == "academic_spotlight":
        return (
            "This paper was selected because its title, source, and metadata point to relevance for energy systems, "
            "grid operations, storage, or energy-sector analytics. Read it as a research signal rather than a confirmed "
            "market development: the practical value depends on the method, assumptions, and whether the findings hold "
            "outside the study setting."
        )
    if item.section_hint == "data_markets":
        return (
            "This item was selected as a market or data signal for the energy sector. The main thing to watch is whether "
            "the reported movement changes expectations for power prices, fuel supply, demand, grid reliability, or "
            "investment timing over the next few days."
        )
    if item.section_hint == "policy_pulse":
        return (
            "This policy item matters because government decisions can change project economics, permitting timelines, "
            "supply-chain choices, or compliance requirements. The next useful question is whether the action is final, "
            "open for comment, or still dependent on implementation details."
        )
    if item.section_hint == "governance":
        return (
            "This governance item was selected because it points to a government, regulator, standards body, or legal "
            "process changing how AI systems may be built, deployed, audited, or restricted. The practical question is "
            "whether the action is binding, voluntary, still in consultation, or likely to shape procurement and "
            "compliance expectations before formal enforcement arrives."
        )
    if item.section_hint == "technical_development":
        return (
            "This technical item was selected as a research or engineering signal in AI. Read it for the concrete method, "
            "benchmark, model behavior, or systems result, but keep the usual caveat: a paper, demo, or benchmark result "
            "is not the same as reliable deployment under real-world cost, latency, security, and evaluation constraints."
        )
    if item.section_hint == "ai_ethics":
        return (
            "This ethics item matters because it raises questions about who is affected by AI systems, which values are "
            "being optimized, and what harms may be hidden by narrow performance metrics. The useful follow-up is whether "
            "the discussion leads to enforceable practice, clearer evaluation, or just another abstract statement of principles."
        )
    if item.section_hint == "xrisk_management":
        return (
            "This existential-risk item was selected because it concerns frontier-model safety, alignment, catastrophic-risk "
            "evaluation, misuse prevention, or governance of capabilities that could scale beyond ordinary product risk. "
            "Watch whether the work creates measurable safety controls, independent verification, or stronger deployment thresholds."
        )
    if item.section_hint == "business":
        return (
            "This business item was selected because it shows money, infrastructure, customers, or market power moving in AI. "
            "The key signal is whether the announcement changes who controls compute, talent, distribution, model access, "
            "or enterprise adoption, and whether the economics are supported by revenue rather than just valuation momentum."
        )
    return (
        "This story was selected for its relevance to energy-sector strategy, infrastructure, markets, or technology. "
        "The source should be read for exact figures and quotes, but the core signal is that it may affect how energy "
        "companies, policymakers, or investors think about near-term risks and opportunities."
    )


def _watch_context(item: Item) -> str:
    title = item.title.lower()
    if item.section_hint == "business_deals":
        return (
            "The business signal is where capital is flowing, which counterparties are taking risk, and whether the "
            "transaction makes a project, technology, or market expansion more executable. Watch deal size, financing "
            "terms, offtake quality, permitting status, geography, and whether this is a single announcement or part of "
            "a broader investment cycle."
        )
    if item.section_hint == "academic_spotlight":
        return (
            "Treat this as a research signal. The useful questions are whether the assumptions match real grid, market, "
            "or asset conditions; whether the method improves on current planning or operations practice; and whether "
            "the result has been validated outside the paper's dataset or model environment."
        )
    if item.section_hint == "data_markets":
        return (
            "Market and data items matter when they change expectations for prices, supply, demand, reliability, or "
            "capital allocation. Watch whether the signal persists across the next few reporting cycles or gets revised "
            "away as new demand, weather, inventory, or generation data comes in."
        )
    if item.section_hint == "policy_pulse":
        return (
            "Policy changes can move project economics even before steel is in the ground. The practical impact depends "
            "on implementation timing, eligibility rules, legal challenges, and whether developers or utilities can "
            "convert the change into faster approvals, lower costs, or clearer compliance obligations."
        )
    if item.section_hint == "governance":
        return (
            "Governance items matter when they change incentives before or after deployment: reporting duties, audit trails, "
            "liability, procurement rules, safety standards, export controls, or enforcement risk. Watch the implementation "
            "details, exemptions, and whether companies adapt behavior or only change public language."
        )
    if item.section_hint == "technical_development":
        return (
            "Technical advances matter when they survive contact with real evaluation: robustness, cost, latency, data quality, "
            "security, and reproducibility. Watch whether independent labs can verify the result and whether the capability "
            "meaningfully changes what users or developers can do."
        )
    if item.section_hint == "ai_ethics":
        return (
            "Ethics work matters when it clarifies a real tradeoff: fairness, autonomy, consent, labor displacement, privacy, "
            "power concentration, epistemic trust, or human agency. Watch whether it affects product design, regulation, "
            "institutional review, or procurement standards."
        )
    if item.section_hint == "xrisk_management":
        return (
            "Existential-risk management matters only if it produces usable controls: evals with teeth, deployment gates, "
            "secure model handling, incident reporting, monitoring, or governance that can keep pace with capability gains. "
            "Watch for independent assessment rather than self-certification."
        )
    if item.section_hint == "business":
        return (
            "AI business stories matter when they reveal durable advantages: compute supply, distribution, proprietary data, "
            "enterprise contracts, chips, cloud capacity, pricing power, or acquisition strategy. Watch whether spending turns "
            "into revenue and whether infrastructure constraints reshape competition."
        )
    if any(word in title for word in ("grid", "transmission", "interconnection", "reliability")):
        return (
            "Grid stories are usually about bottlenecks, reliability margins, or who pays for infrastructure. Watch for "
            "whether this leads to actual capacity additions, faster interconnection, changed market rules, or just "
            "another planning signal without near-term execution."
        )
    if any(word in title for word in ("battery", "storage", "solar", "wind", "renewable")):
        return (
            "Clean power and storage stories matter most when they affect deployment pace, project economics, supply "
            "chains, or grid integration. Watch costs, permitting, interconnection queues, and whether announced capacity "
            "turns into operating assets."
        )
    if any(word in title for word in ("acquisition", "deal", "financing", "funding", "investment", "joint venture", "ppa", "stake")):
        return (
            "Business-side energy news matters because capital allocation often reveals what companies believe will scale. "
            "Watch who is providing capital, whether there is contracted revenue or merchant exposure, and whether the "
            "deal changes competitive positioning in a region or technology category."
        )
    if any(word in title for word in ("oil", "gas", "lng", "fuel", "power price", "prices")):
        return (
            "Fuel and power-market stories can feed directly into inflation, utility costs, industrial margins, and "
            "dispatch decisions. Watch whether the move is weather-driven, supply-driven, policy-driven, or a short-lived "
            "trading response."
        )
    return (
        "The practical importance is whether this changes decisions for utilities, developers, policymakers, investors, "
        "or large energy buyers. Watch for follow-through: funding, permits, contracts, rule changes, operating data, or "
        "credible evidence that the headline is becoming an executable shift."
    )


def _fallback_curate(items: list[Item], profile: NewsletterProfile) -> DigestSections:
    buckets: dict[str, list[Item]] = defaultdict(list)
    for item in dedupe(items):
        section = item.section_hint if item.section_hint in profile.section_limits else next(iter(profile.sections))
        item.score = _heuristic_score(item)
        item.summary = _fallback_summary(item)
        buckets[section].append(item)

    sections: DigestSections = {}
    for section, limit in profile.section_limits.items():
        sections[section] = sorted(buckets.get(section, []), key=lambda row: row.score, reverse=True)[:limit]
    return sections


def _serialize_for_prompt(items: list[Item]) -> list[dict[str, object]]:
    return [
        {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "summary": item.summary[:1200],
            "section_hint": item.section_hint,
            "authors": item.authors[:6],
            "score": item.score,
            "published_at": item.published_at.isoformat() if item.published_at else None,
        }
        for item in items
    ]


def _prompt_requirements(profile: NewsletterProfile) -> str:
    if profile.key == "ai":
        return """
- Select items for exactly these five sections: governance, technical_development, ai_ethics, xrisk_management, business.
- Governance: major policy, legislation, standards, regulators, courts, procurement rules, and government action regulating or steering AI.
- Technical Development: scientific and engineering advances, new models, methods, benchmarks, systems, and capabilities.
- Developments in AI Ethics: philosophical, moral, social, fairness, rights, labor, consent, bias, agency, and responsible-AI debates.
- Existential Risk Analysis & Management: frontier safety, alignment, catastrophic-risk evaluation, misuse prevention, deployment gates, and risk-reduction work.
- Business: investment, funding, revenue, enterprise adoption, chips, compute, cloud deals, acquisitions, partnerships, and market strategy.
- Rank by daily importance, credibility, novelty, and practical consequence.
- Select enough items to make the report genuinely useful: up to 5 governance items, 5 technical-development items, 4 ethics items, 4 existential-risk items, and 5 business items when credible source material exists.
- Make each summary a detailed mini-brief of 180-260 words.
- Each mini-brief must cover: what happened; the actors involved; the concrete mechanism, rule, method, argument, or transaction; why it matters; who is affected; what to watch next; and the uncertainty, limitation, or counterargument.
- For research papers, explain the method and evaluation in plain English, then separate benchmark evidence from field-proven usefulness.
- For governance, distinguish proposed rules, final rules, guidance, litigation, standards, procurement pressure, and actual enforcement.
- For ethics and existential risk, make the moral or safety tradeoff explicit instead of gesturing at "concerns."
- For business, explain the strategic rationale, capital/compute implications, and what would prove whether the move is durable.
- Avoid hype and generic significance language.
- Return only JSON with keys: governance, technical_development, ai_ethics, xrisk_management, business.
""".strip()
    return """
- Select 3-4 top stories, 3-4 business deals/investment items, 3-4 academic papers, 2-3 data/market items, and 1-2 policy items.
- Academic Spotlight should remain substantial, but the digest must also highlight the business side globally: financings, acquisitions, PPAs, project finance, joint ventures, offtake agreements, strategic investments, and capital allocation trends.
- Deduplicate overlapping coverage.
- Rank by impact, recency, credibility, and usefulness to an energy-sector reader.
- Make the email self-contained. The reader should understand the item without opening the link.
- Rewrite each summary as a compact mini-brief of 100-160 words.
- Each mini-brief must explain: what happened or what the paper claims; why it matters for energy systems, markets, policy, or investment; what to watch next; and any uncertainty or limitation.
- For business deals, explain the transaction type, counterparties, geography, technology or asset class, business rationale, what it signals about capital flows, and what terms or milestones matter next. If deal value or terms are not available, say that clearly.
- For academic papers, explain the method or research question in plain English, the practical implication, and why it is not yet the same as field-proven deployment.
- Avoid hype, vague language, and generic phrases like "significant development" unless you explain the specific significance.
- Return only JSON with keys: top_stories, business_deals, academic_spotlight, data_markets, policy_pulse.
""".strip()


def curate_with_claude(
    items: list[Item],
    anthropic_api_key: str | None,
    profile: NewsletterProfile | None = None,
) -> DigestSections:
    profile = profile or get_profile()
    if not anthropic_api_key:
        return _fallback_curate(items, profile)

    try:
        from anthropic import Anthropic
    except ImportError:
        return _fallback_curate(items, profile)

    unique = dedupe(items)
    prompt = f"""
You curate {profile.name}, a daily newsletter.

Requirements:
- Deduplicate overlapping coverage.
{_prompt_requirements(profile)}
- Each item must include: title, url, source, summary, authors.

Candidate items:
{json.dumps(_serialize_for_prompt(unique[:120]), ensure_ascii=False)}
""".strip()

    try:
        client = Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=10000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text")
        start = raw.find("{")
        end = raw.rfind("}")
        data = json.loads(raw[start : end + 1])
    except Exception as exc:  # noqa: BLE001 - keep the daily job alive.
        print(f"curation warning: {exc}")
        return _fallback_curate(unique, profile)

    by_url = {item.url: item for item in unique}
    sections: DigestSections = {}
    for section, limit in profile.section_limits.items():
        selected: list[Item] = []
        for row in data.get(section, [])[:limit]:
            base = by_url.get(row.get("url"))
            if base:
                base.summary = row.get("summary") or base.summary
                base.title = row.get("title") or base.title
                base.source = row.get("source") or base.source
                base.authors = row.get("authors") or base.authors
                selected.append(base)
        sections[section] = selected
    return sections
