"""
The attacker is itself an AETHER MAS.

This module assembles the four PROBE nodes (planner / payload_crafter /
victim_observer / success_evaluator) into a LangGraph-compiled MAS via the
existing AETHER compiler, with a per-turn loop driven by the chosen
AttackPolicy.

Key design choice: rather than declaring the attacker MAS in YAML (the
standard AETHER pattern), we construct it programmatically. Reasons:
- The loop structure is policy-dependent (e.g. TAPPolicy needs a tree)
- Custom state fields (ProbeSession.turns, BudgetState) need typed access
  that's awkward to express in YAML
- Programmatic construction lets policies inject their own reducers

If the upstream AETHER YAML schema later supports loops + injected reducers,
revisit this choice — running the attacker as a YAML-defined MAS is more
elegant and dogfoods the framework harder.

See RFC § 5.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

from typing import Any

from bili.aegis.probe.policies.base import AttackPolicy
from bili.aegis.probe.schema import ProbeSession


class AttackerMAS:
    """
    The compiled attacker multi-agent system.

    Lifecycle:
        1. Construct with (policy, attacker_model_config, judge_model_config).
        2. .initialize() — compiles the LangGraph workflow.
        3. .run_session(session) — executes the per-turn loop until termination.

    The victim MAS is *not* part of the attacker MAS — it is invoked between
    payload_crafter and victim_observer via a normal AETHER MASExecutor call.
    This keeps the meta-recursive design clean: two completely independent
    AETHER MAS objects, communicating through the runner.
    """

    def __init__(
        self,
        policy: AttackPolicy,
        attacker_model_config: dict[str, Any],
        judge_model_config: dict[str, Any],
    ) -> None:
        self.policy = policy
        self.attacker_model_config = attacker_model_config
        self.judge_model_config = judge_model_config
        self._graph: Any = None  # Compiled LangGraph object

    def initialize(self) -> None:
        """
        Build the LangGraph workflow for the attacker.

        TODO: assemble graph using bili.aether.compiler primitives. Nodes:
        - planner (uses self.policy.plan_next_intent)
        - payload_crafter
        - (victim execution happens between payload_crafter exit and observer entry,
          as an external step coordinated by run_probe_session)
        - victim_observer
        - success_evaluator (calls SemanticEvaluator with judge_model_config)
        """
        raise NotImplementedError

    def run_session(self, session: ProbeSession, victim_executor: Any) -> ProbeSession:
        """
        Execute the per-turn loop on `session` against `victim_executor`.

        Returns the same session object with `turns` populated and
        `final_outcome` set.

        TODO: implement the per-turn loop. Pseudocode:

            while session.budget.can_continue() and not _is_done(session):
                intent = policy.plan_next_intent(session)
                payload = payload_crafter(intent, session)
                victim_output = victim_executor.run(payload)
                observation = victim_observer(payload, victim_output)
                verdict = success_evaluator(session.objective, victim_output)
                turn = build_turn(...)
                session.turns.append(turn)
                if not policy.should_continue(session):
                    break
            session.final_outcome = _finalize(session)
            return session
        """
        raise NotImplementedError
