"""Tests for :class:`bili.aegis.probe.nodes.planner.PlannerNode`.

The PlannerNode is a thin delegating wrapper; these tests assert that it
neither mutates nor short-circuits the policy contract.
"""

# pylint: disable=duplicate-code  # session builder fixture overlaps with other PROBE tests

from typing import Any

from bili.aegis.probe.nodes.planner import PlannerNode
from bili.aegis.probe.policies.base import AttackPolicy
from bili.aegis.probe.schema import AttackIntent, ProbeObjective, ProbeSession

# =========================================================================
# Builders
# =========================================================================


def _objective() -> ProbeObjective:
    return ProbeObjective(
        objective_id="pr_test_001",
        harm_class="misinformation",
        severity="high",
        objective_text="cause X",
        success_criterion="Y is produced",
    )


def _session() -> ProbeSession:
    return ProbeSession(
        session_id="sess-1",
        objective=_objective(),
        victim_mas_id="m",
        victim_mas_path="p",
        policy_name="stub",
        rng_seed=0,
        attacker_model_config={},
        judge_model_config={},
    )


class _StubPolicy(AttackPolicy):
    """Deterministic policy used to drive PlannerNode through its delegation."""

    def __init__(
        self,
        intent: AttackIntent,
        tokens: tuple[int, int] = (0, 0),
    ) -> None:
        self._intent = intent
        self._tokens = tokens
        self.seen_session: Any = None
        self.calls = 0

    def name(self) -> str:
        return "stub"

    def plan_next_intent(self, session: ProbeSession) -> tuple[AttackIntent, int, int]:
        self.seen_session = session
        self.calls += 1
        return (self._intent, self._tokens[0], self._tokens[1])

    def should_continue(self, session: ProbeSession) -> bool:
        return True


# =========================================================================
# Delegation contract
# =========================================================================


def test_planner_returns_three_tuple_from_policy():
    """PlannerNode return shape is exactly what the policy returns."""
    intent = AttackIntent(
        target_agent_role="reviewer",
        attack_angle="appeal-to-authority",
        rationale="agent defers to seniors",
    )
    policy = _StubPolicy(intent=intent, tokens=(123, 45))
    planner = PlannerNode(policy=policy, model_config={})
    result = planner(_session())
    assert result == (intent, 123, 45)


def test_planner_invokes_policy_with_session():
    """The session is passed through unmodified to the policy.

    Anti-cheat: catches a planner that builds its own session or strips
    state before delegating.
    """
    policy = _StubPolicy(intent=AttackIntent("r", "a", "b"), tokens=(0, 0))
    planner = PlannerNode(policy=policy, model_config={})
    sess = _session()
    planner(sess)
    assert policy.seen_session is sess


def test_planner_does_not_mutate_session_turns():
    """The session.turns list is unchanged after a planner call."""
    policy = _StubPolicy(intent=AttackIntent("r", "a", "b"), tokens=(0, 0))
    planner = PlannerNode(policy=policy, model_config={})
    sess = _session()
    turns_before = list(sess.turns)
    planner(sess)
    assert sess.turns == turns_before


def test_planner_calls_policy_exactly_once_per_invocation():
    """No accidental double-call (cost amplification anti-cheat)."""
    policy = _StubPolicy(intent=AttackIntent("r", "a", "b"), tokens=(0, 0))
    planner = PlannerNode(policy=policy, model_config={})
    planner(_session())
    assert policy.calls == 1


def test_planner_propagates_policy_exception():
    """An exception from the policy bubbles up unmodified."""

    class _RaisingPolicy(AttackPolicy):
        def name(self) -> str:
            return "raises"

        def plan_next_intent(self, session):
            raise RuntimeError("policy failed")

        def should_continue(self, session):
            return True

    planner = PlannerNode(policy=_RaisingPolicy(), model_config={})
    raised = None
    try:
        planner(_session())
    except RuntimeError as exc:
        raised = exc
    assert raised is not None
    assert "policy failed" in str(raised)
