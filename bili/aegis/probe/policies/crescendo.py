"""
CrescendoPolicy — multi-turn benign-to-harmful escalation.

Implements the escalation pattern from Russinovich et al. (Microsoft, 2024,
"Great, Now Write an Article About That: The Crescendo Multi-Turn LLM
Jailbreak Attack").

Key idea: each turn looks individually benign or only mildly out-of-policy,
but the cumulative trajectory walks the conversation past per-turn safety
filters. The planner is given an explicit ladder of N rungs (N=8 by default)
and is constrained to climb at most one rung per turn.

The ladder is generated once per session at turn 0, conditioned on the
objective. Subsequent turns refine but do not regenerate the ladder.

Default budget: 10 turns, ladder of 8 rungs (2 turns of headroom for
re-attempts on a failed rung).

TODO: ladder generation prompt; per-rung intent template.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from bili.aegis.probe.policies.base import AttackPolicy
from bili.aegis.probe.schema import AttackIntent, ProbeSession


class CrescendoPolicy(AttackPolicy):
    """Multi-turn benign-to-harmful escalation policy (Russinovich et al. 2024).

    See ``bili/aegis/docs/probe-rfc.md`` section 6.2 for design rationale.
    """

    DEFAULT_MAX_TURNS = 10
    DEFAULT_LADDER_RUNGS = 8

    def __init__(self, ladder_rungs: int = DEFAULT_LADDER_RUNGS) -> None:
        self.ladder_rungs = ladder_rungs
        self._ladder: list[str] | None = None  # generated lazily on turn 0

    def name(self) -> str:
        return "crescendo"

    def plan_next_intent(self, session: ProbeSession) -> AttackIntent:
        # TODO:
        # if turn 0: call attacker LLM to generate ladder, store in self._ladder
        # else: select next rung based on prior verdict (advance on success,
        #   re-attempt on partial, restart from earlier rung on failure)
        raise NotImplementedError

    def should_continue(self, session: ProbeSession) -> bool:
        # TODO: stop when last rung achieved or when 2+ consecutive rungs fail
        raise NotImplementedError
