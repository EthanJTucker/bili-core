"""
Planner node — strategy decisions only, no payload realization.

The planner reads:
- current ProbeSession (objective, full turn history)
- the active AttackPolicy

and produces an AttackIntent (target_agent_role, attack_angle, rationale,
optional rung_index).

The intent is intentionally abstract: "exploit the supervisor's tendency to
defer to subordinates" rather than "send the string 'You are now DAN'." The
payload_crafter realizes intents into concrete prompts.

This split is what lets us swap policies without rewriting prompt-engineering.
See RFC § 6.

TODO: prompt template for the planner LLM, with explicit format-locked output
parsing for AttackIntent fields.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from typing import Any

from bili.aegis.probe.policies.base import AttackPolicy
from bili.aegis.probe.schema import AttackIntent, ProbeSession


class PlannerNode:  # pylint: disable=too-few-public-methods
    """LangGraph node implementation. Stateless — state lives in ProbeSession."""

    def __init__(self, policy: AttackPolicy, model_config: dict[str, Any]) -> None:
        self.policy = policy
        self.model_config = model_config

    def __call__(self, session: ProbeSession) -> AttackIntent:
        """Produce the next AttackIntent for the session."""
        # TODO: delegate to self.policy.plan_next_intent which internally calls
        # an LLM with a policy-specific prompt template
        raise NotImplementedError
