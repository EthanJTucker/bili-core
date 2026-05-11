"""
Budget enforcement for PROBE sessions.

Multi-turn adaptive attackers are the most cost-intensive thing AEGIS contains.
Budget enforcement is non-optional: a session that would exceed any limit is
force-terminated with `ProbeOutcomeReason.BUDGET_EXCEEDED`.

See RFC § 9.1.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BudgetState:  # pylint: disable=too-many-instance-attributes
    """
    Tracks all four budget axes for a session.

    Limits with value None are unbounded for that axis. At least one axis
    must be bounded; constructor enforces this.

    Cost is computed lazily from token counts using a pluggable price table
    so that price changes do not require code changes — see RFC § 9.1.
    """

    max_turns: int | None = 12
    max_tokens_total: int | None = 200_000
    max_wall_clock_seconds: float | None = 300.0
    max_cost_usd: float | None = 5.00

    # Running totals (updated by the runner)
    turns_used: int = 0
    tokens_used: int = 0
    wall_clock_seconds_used: float = 0.0
    estimated_cost_usd: float = 0.0

    # Token-to-cost lookup; populated from a price config file
    price_table: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # TODO: enforce at least one bounded axis
        pass

    def remaining_turns(self) -> float:
        """Returns inf if max_turns is None."""
        # TODO: implement
        raise NotImplementedError

    def can_continue(self) -> bool:
        """True iff no budget axis is exceeded."""
        # TODO: implement
        raise NotImplementedError

    def record_turn(
        self,
        turn_tokens: int,
        turn_seconds: float,
        turn_cost_usd: float,
    ) -> None:
        """Increment running totals after a turn completes."""
        # TODO: implement
        raise NotImplementedError
