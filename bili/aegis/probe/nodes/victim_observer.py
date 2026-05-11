"""
Victim-observer node — extracts attack-relevant signals from victim output.

The observer reads:
- The full victim MAS state after execution (output of MASExecutor.run)
- The original payload that was sent

and produces a structured observation_summary feeding back into the planner
for the next turn.

This is *not* the success judge. The observer is fast, cheap, and produces
free-form descriptions of what happened ("agent X resisted, agent Y partially
complied by acknowledging the framing"). The success_evaluator does the
formal Tier 3 scoring.

The observer also computes:
- propagation_path (reuses AEGIS PropagationTracker)
- influenced_agents
- resistant_agents

TODO: integrate with bili.aegis.attacks.PropagationTracker.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from typing import Any

from bili.aegis.probe.schema import ProbeSession


class VictimObserverNode:  # pylint: disable=too-few-public-methods
    """LangGraph node implementation."""

    def __init__(self, model_config: dict[str, Any]) -> None:
        self.model_config = model_config

    def __call__(
        self,
        payload_text: str,
        victim_output: dict[str, Any],
        session: ProbeSession,
    ) -> dict[str, Any]:
        """
        Returns dict with:
            observation_summary: str
            propagation_path: list[str]
            influenced_agents: list[str]
            resistant_agents: list[str]
        """
        # TODO: implement
        raise NotImplementedError
