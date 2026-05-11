"""
PAIRPolicy — linear single-thread refinement.

Implements the core loop from Chao et al. 2023 ("Jailbreaking Black Box Large
Language Models in Twenty Queries"):

    state = []
    while not done:
        intent = planner_LLM(objective, state)
        payload = realize(intent)
        response = victim(payload)
        verdict = judge(objective, response)
        state.append((payload, response, verdict))

The planner LLM is asked to "diagnose why the previous attempt failed and
propose a more effective next attempt" — the prompt is what makes this PAIR
rather than random retry.

Default budget: 8 turns. Self-abandons if 3 consecutive turns produce
TurnVerdict.NO_PROGRESS with no propagation signal.

TODO: planner prompt template adapted from Chao et al. § 3.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from bili.aegis.probe.policies.base import AttackPolicy
from bili.aegis.probe.schema import AttackIntent, ProbeSession


class PAIRPolicy(AttackPolicy):
    """Linear single-thread refinement policy (Chao et al. 2023).

    See ``bili/aegis/docs/probe-rfc.md`` section 6.1 for design rationale.
    """

    DEFAULT_MAX_TURNS = 8
    SELF_ABANDON_AFTER_N_NO_PROGRESS = 3

    def name(self) -> str:
        return "pair"

    def plan_next_intent(self, session: ProbeSession) -> AttackIntent:
        # TODO: build planner prompt from session.objective + session.turns,
        # call attacker LLM, parse AttackIntent
        raise NotImplementedError

    def should_continue(self, session: ProbeSession) -> bool:
        # TODO: check trailing N turns for NO_PROGRESS streak; return False
        # if attacker should self-abandon
        raise NotImplementedError
