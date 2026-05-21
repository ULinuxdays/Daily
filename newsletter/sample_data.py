"""Deterministic sample content for preview and test sends."""

from __future__ import annotations

from newsletter.models import Item


def sample_items() -> list[Item]:
    return [
        Item(
            title="Grid operators expand battery dispatch as evening peaks rise",
            url="https://example.com/grid-battery-dispatch",
            source="Sample News",
            summary=(
                "Battery fleets are being dispatched for longer windows as solar-heavy regions "
                "manage sharper evening ramps. Operators are watching market rules and "
                "interconnection queues as the next constraints."
            ),
            section_hint="top_stories",
        ),
        Item(
            title="New model improves co-optimization of storage and transmission planning",
            url="https://example.com/storage-transmission-paper",
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
            url="https://example.com/power-forwards",
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
            url="https://example.com/permitting-reform",
            source="Sample Policy",
            summary=(
                "The consultation focuses on timelines, cost allocation, and regional planning "
                "requirements. Developers say faster permitting remains central to connecting "
                "renewable generation."
            ),
            section_hint="policy_pulse",
        ),
    ]
