"""
Payload-crafter node — realizes AttackIntent into a concrete victim-facing prompt.

Conditioned on:
- AttackIntent (from planner)
- Victim MAS shape (agent roles, channel topology) — known statically from the
  YAML config, passed in at construction
- Past turns in the session, for continuity (Crescendo policies need
  conversational coherence across turns)

This node is intentionally a different LLM call from the planner, with a
different prompt template. Conceptually: planner = strategist, crafter =
ghostwriter.

TODO: prompt template, victim-MAS-shape extraction helper.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from typing import Any

from bili.aegis.probe.schema import AttackIntent, ProbeSession


class PayloadCrafterNode:  # pylint: disable=too-few-public-methods
    """LangGraph node implementation."""

    def __init__(
        self,
        model_config: dict[str, Any],
        victim_mas_shape: dict[str, Any],
    ) -> None:
        self.model_config = model_config
        self.victim_mas_shape = victim_mas_shape

    def __call__(self, intent: AttackIntent, session: ProbeSession) -> str:
        """Returns the concrete payload string to send to the victim MAS."""
        # TODO: implement
        raise NotImplementedError
