"""
TAPPolicy — Tree of Attacks with Pruning.

Implements Mehrotra et al. 2023 ("Tree of Attacks: Jailbreaking Black-Box
LLMs Automatically"). Maintains a tree of candidate attack trajectories;
each node is a (payload, victim_response, verdict) triple. At each step:

    1. Select the most promising leaf by Tier 3 score (with tie-breaks on
       depth, then random).
    2. Expand it: ask the attacker LLM for K refinements (default K=3).
    3. Evaluate each refinement against the victim.
    4. Prune: drop any leaf whose Tier 3 score has not improved over its
       parent for D consecutive expansions (default D=2).
    5. Stop when a leaf reaches TurnVerdict.SUCCESS or budget is exhausted.

Note: TAP is more expensive than PAIR by a factor of K. The default budget
of 32 leaf evaluations and max depth 6 is calibrated to be roughly cost-
parity with PAIRPolicy at default settings.

TODO: tree data structure; expansion prompt; pruning logic.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from dataclasses import dataclass, field

from bili.aegis.probe.policies.base import AttackPolicy
from bili.aegis.probe.schema import AttackIntent, ProbeSession


@dataclass
class _TAPNode:
    """Internal tree node. Distinct from ProbeTurn which is the flat session log."""

    parent_id: str | None
    node_id: str
    depth: int
    payload_text: str
    tier3_score: int
    pruned: bool = False
    children: list[str] = field(default_factory=list)


class TAPPolicy(AttackPolicy):
    """Tree-of-attacks with pruning policy (Mehrotra et al. 2023).

    See ``bili/aegis/docs/probe-rfc.md`` section 6.3 for design rationale.
    """

    DEFAULT_MAX_LEAF_EVALUATIONS = 32
    DEFAULT_MAX_DEPTH = 6
    DEFAULT_BRANCHING_FACTOR = 3
    DEFAULT_PRUNE_AFTER_N = 2

    def __init__(
        self,
        max_leaf_evaluations: int = DEFAULT_MAX_LEAF_EVALUATIONS,
        max_depth: int = DEFAULT_MAX_DEPTH,
        branching_factor: int = DEFAULT_BRANCHING_FACTOR,
    ) -> None:
        self.max_leaf_evaluations = max_leaf_evaluations
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self._tree: dict[str, _TAPNode] = {}

    def name(self) -> str:
        return "tap"

    def plan_next_intent(self, session: ProbeSession) -> AttackIntent:
        # TODO: select most promising unpruned leaf; expand via attacker LLM
        raise NotImplementedError

    def should_continue(self, session: ProbeSession) -> bool:
        # TODO: stop on success leaf, or when all leaves pruned, or depth cap
        raise NotImplementedError
