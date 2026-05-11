"""
AEGIS-PROBE: Persistent Reasoning Open-ended Black-box Evaluator.

An autonomous adversarial agent suite for AEGIS that conducts multi-round,
adaptive red-teaming against AETHER multi-agent victim systems.

See: docs/probe-design.md and the RFC.

Public surface:
- ProbeSession, ProbeTurn, ProbeOutcome, ProbeObjective (schema.py)
- AttackPolicy ABC and reference implementations (policies/)
- BudgetState (budget.py)
- run_probe_session() top-level entry point used by the suite runner

Implementation status: scaffold only. See TODO markers in each module.
"""

from bili.aegis.probe.budget import BudgetState
from bili.aegis.probe.schema import (
    AttackIntent,
    ProbeObjective,
    ProbeOutcome,
    ProbeSession,
    ProbeTurn,
)

__all__ = [
    "ProbeSession",
    "ProbeTurn",
    "ProbeOutcome",
    "ProbeObjective",
    "AttackIntent",
    "BudgetState",
]
