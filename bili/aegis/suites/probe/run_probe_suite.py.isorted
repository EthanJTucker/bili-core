"""
Entry point for the PROBE suite.

Matches the existing AEGIS runner CLI shape:

    python bili/aegis/suites/probe/run_probe_suite.py --stub
    python bili/aegis/suites/probe/run_probe_suite.py \\
        --baseline-results bili/aegis/suites/baseline/results

Probe-specific flags:
    --policies pair crescendo tap          (default: all three)
    --objectives pr_misinfo_001 ...        (default: all in library)
    --configs path/to/mas.yaml ...         (default: CONFIG_PATHS in _helpers.py)
    --seeds 0 1 2                          (default: [0])
    --budget-turns 12                      (per-session turn cap)
    --budget-tokens 200000                 (per-session token cap)
    --budget-cost-usd 5.0                  (per-session cost cap)
    --smoke                                (1/10 scale for CI sanity check)

Output:
    bili/aegis/suites/probe/results/{mas_id}/{session_id}.json   (sidecar)
    bili/aegis/suites/probe/results/probe_results_matrix.csv     (matrix)

See RFC § 12 for acceptance criteria.

Implementation status: scaffold. The argparse skeleton is real; the session
loop body is TODO.
"""

# pylint: disable=fixme  # TODOs are intentional scaffold markers; will be removed as features land

from __future__ import annotations

import argparse
import sys


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_probe_suite",
        description="AEGIS-PROBE: autonomous adaptive red-teaming suite.",
    )
    p.add_argument(
        "--stub",
        action="store_true",
        help="Skip all LLM calls; useful for framework wiring tests.",
    )
    p.add_argument(
        "--policies",
        nargs="+",
        default=["pair", "crescendo", "tap"],
        help="Policies to run (default: all three).",
    )
    p.add_argument(
        "--objectives",
        nargs="+",
        default=None,
        help="Objective IDs (default: full library).",
    )
    p.add_argument(
        "--configs",
        nargs="+",
        default=None,
        help="MAS YAML paths (default: CONFIG_PATHS from _helpers).",
    )
    p.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=[0],
        help="RNG seeds; one session per seed.",
    )
    p.add_argument("--budget-turns", type=int, default=12)
    p.add_argument("--budget-tokens", type=int, default=200_000)
    p.add_argument("--budget-cost-usd", type=float, default=5.0)
    p.add_argument(
        "--baseline-results",
        type=str,
        default=None,
        help="Path to baseline results dir (required for Tier 3).",
    )
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Run at 1/10 scale (first objective only, single seed).",
    )
    p.add_argument("--results-dir", type=str, default="bili/aegis/suites/probe/results")
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point for the PROBE suite runner. See module docstring."""
    args = _build_argparser().parse_args(argv)
    _ = args  # pylint: disable=unused-variable  # consumed by TODO loop body

    # TODO: implement the suite loop:
    #
    # 1. Resolve config paths (default to CONFIG_PATHS from _helpers).
    # 2. Load PROBE_OBJECTIVE_LIBRARY; filter by args.objectives.
    # 3. For each (objective, mas_config, policy, seed):
    #      session = ProbeSession(...)
    #      session.budget = BudgetState(
    #          max_turns=args.budget_turns,
    #          max_tokens_total=args.budget_tokens,
    #          max_cost_usd=args.budget_cost_usd,
    #      )
    #      attacker = AttackerMAS(policy, attacker_cfg, judge_cfg)
    #      attacker.initialize()
    #      victim = MASExecutor.from_yaml(mas_config)
    #      victim.initialize()
    #      session = attacker.run_session(session, victim)
    #      _write_sidecar(session, args.results_dir)
    #      _append_csv_row(session, args.results_dir)
    # 4. Print summary block matching existing AEGIS runner format.
    # 5. Return 0 on success, non-zero on framework error.

    raise NotImplementedError("PROBE runner scaffold; see TODO inline.")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
