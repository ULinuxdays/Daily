"""Deterministic sample content for preview and test sends."""

from __future__ import annotations

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import Item


def sample_items(profile: NewsletterProfile | None = None) -> list[Item]:
    profile = profile or get_profile()
    if profile.key == "ai":
        return [
            Item(
                title="Regulators publish updated frontier AI reporting guidance",
                url="https://www.nist.gov/artificial-intelligence",
                source="Sample Governance",
                summary=(
                    "A government standards body updated guidance for reporting, evaluating, and documenting frontier AI systems. "
                    "The practical impact depends on whether agencies and large buyers turn the guidance into procurement and compliance requirements."
                ),
                section_hint="governance",
            ),
            Item(
                title="New agent benchmark tests long-horizon tool use under realistic failures",
                url="https://arxiv.org/list/cs.AI/recent",
                source="Sample Research",
                summary=(
                    "Researchers introduced a benchmark that measures whether AI agents can recover from missing data, tool errors, and ambiguous instructions. "
                    "The result is useful because many current evaluations overstate agent reliability by testing short, clean tasks."
                ),
                section_hint="technical_development",
                authors=["A. Researcher", "B. Evaluator"],
                score=20,
            ),
            Item(
                title="New paper argues consent is under-specified in AI training-data practice",
                url="https://thegradient.pub/",
                source="Sample Ethics",
                summary=(
                    "The essay argues that current data collection norms blur consent, attribution, and downstream economic harm. "
                    "The moral question is whether opt-out mechanisms and licensing deals actually respect agency or simply legalize extraction after the fact."
                ),
                section_hint="ai_ethics",
            ),
            Item(
                title="Safety lab proposes deployment gates for high-capability autonomous systems",
                url="https://www.anthropic.com/news",
                source="Sample Safety",
                summary=(
                    "A safety group proposed evaluation thresholds before releasing autonomous systems with stronger cyber, persuasion, or scientific capabilities. "
                    "The important test is whether the thresholds are independently audited and strong enough to delay launches when risk evidence is bad."
                ),
                section_hint="xrisk_management",
            ),
            Item(
                title="AI infrastructure startup raises funding for inference data centers",
                url="https://venturebeat.com/category/ai/",
                source="Sample Business",
                summary=(
                    "An AI infrastructure company raised capital to expand inference-focused data centers. "
                    "The deal points to a market shift from training-only compute demand toward serving costs, latency, and enterprise reliability."
                ),
                section_hint="business",
                score=25,
            ),
        ]

    return [
        Item(
            title="Grid operators expand battery dispatch as evening peaks rise",
            url="https://www.energy.gov/oe/grid-deployment-office",
            source="Sample News",
            summary=(
                "Battery fleets are being dispatched for longer windows as solar-heavy regions "
                "manage sharper evening ramps. Operators are watching market rules and "
                "interconnection queues as the next constraints."
            ),
            section_hint="top_stories",
        ),
        Item(
            title="Global developer secures project financing for battery storage portfolio",
            url="https://www.energy-storage.news/",
            source="Sample Deals",
            summary=(
                "A storage developer closed financing for a multi-market battery portfolio backed by contracted "
                "revenues and merchant upside. The transaction points to continued investor appetite for grid-scale "
                "flexibility assets, but execution still depends on interconnection timing, equipment delivery, and "
                "regional power-market volatility."
            ),
            section_hint="business_deals",
            score=25,
        ),
        Item(
            title="New model improves co-optimization of storage and transmission planning",
            url="https://arxiv.org/list/eess.SY/recent",
            source="Sample Journal",
            summary=(
                "The paper proposes a planning model that jointly values transmission upgrades "
                "and storage siting under renewable uncertainty. The results show lower "
                "curtailment and better resilience during high-load periods."
            ),
            section_hint="academic_spotlight",
            authors=["A. Researcher", "B. Analyst"],
            score=20,
        ),
        Item(
            title="Power forwards move higher after heat outlook shifts",
            url="https://www.eia.gov/todayinenergy/",
            source="Sample Markets",
            summary=(
                "Forward electricity prices rose after updated weather models pointed to "
                "stronger cooling demand. Gas prices remained the key marginal-cost driver "
                "in several regions."
            ),
            section_hint="data_markets",
        ),
        Item(
            title="Regulators open consultation on transmission permitting reform",
            url="https://www.energy.gov/gdo/transmission-siting-and-economic-development-grants-program",
            source="Sample Policy",
            summary=(
                "The consultation focuses on timelines, cost allocation, and regional planning "
                "requirements. Developers say faster permitting remains central to connecting "
                "renewable generation."
            ),
            section_hint="policy_pulse",
        ),
    ]
