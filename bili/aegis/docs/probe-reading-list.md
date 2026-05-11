# AEGIS-PROBE — Reading list and 3-week plan

## Reading list

Tiered by what you need to extract. Aim to spend ~2 days on the reading
before writing implementation code; you do not need to read everything
end-to-end.

### Tier 1 — Read carefully, take notes

These four define the policy designs you are implementing. Extract the prompt
templates, success-rate tables, and ablation choices from each.

1. **PAIR — Chao et al., 2023.** *Jailbreaking Black Box Large Language
   Models in Twenty Queries.* arXiv:2310.08419. Key extraction targets: §3
   (algorithm), §4.1 (attacker prompt template), Table 2 (ASR results).
   Maps directly to `policies/pair.py`.

2. **TAP — Mehrotra et al., 2023.** *Tree of Attacks: Jailbreaking Black-Box
   LLMs Automatically.* arXiv:2312.02119. Key extraction targets: §3.2
   (tree expansion + pruning), §3.3 (judge model design choices), Algorithm 1.
   Maps to `policies/tap.py`.

3. **Crescendo — Russinovich et al., Microsoft, 2024.** *Great, Now Write an
   Article About That: The Crescendo Multi-Turn LLM Jailbreak Attack.*
   arXiv:2404.01833. Key extraction targets: §3.2 (the "ladder" mechanic),
   §4 (results across model families), the prompt examples in the appendix.
   Maps to `policies/crescendo.py`.

4. **GOAT — Pavlova et al., Meta, 2024.** *Automated Red Teaming with GOAT:
   the Generative Offensive Agent Tester.* arXiv:2410.01606. Key extraction
   targets: the meta-cognition prompt structure (planning/observation/payload
   separation), the multi-turn evaluation methodology. Closest published
   precedent to PROBE's overall architecture.

### Tier 2 — Skim, internalize the framing

Useful background; you do not need to implement anything from these directly.

5. **HouYi — Liu et al., 2023.** *Prompt Injection Attack against
   LLM-integrated Applications.* arXiv:2306.05499. Useful for the
   "framework / separator / payload" decomposition (§3.2). Informs how
   `payload_crafter` could potentially be templated.

6. **AutoDAN — Zhu et al., 2023.** *AutoDAN: Generating Stealthy Jailbreak
   Prompts on Aligned Large Language Models.* arXiv:2310.04451. Genetic-
   algorithm based; you are not implementing this in v0.1, but it is the
   canonical "search over a payload feature space" paper and worth knowing
   for the future-policy slot in your ABC.

7. **AdvBench — Zou et al., 2023.** *Universal and Transferable Adversarial
   Attacks on Aligned Language Models.* arXiv:2307.15043. Defines the
   harmful-behaviors dataset most subsequent work uses. Useful for objective
   library curation.

8. **HarmBench — Mazeika et al., 2024.** *HarmBench: A Standardized
   Evaluation Framework for Automated Red Teaming and Robust Refusal.*
   arXiv:2402.04249. The likely source for your PROBE objective library
   harm taxonomy. Read §3 (taxonomy) and §4 (evaluation methodology).

9. **JailbreakBench — Chao et al., 2024.** *JailbreakBench: An Open
   Robustness Benchmark for Jailbreaking Large Language Models.*
   arXiv:2404.01318. The reproducibility infrastructure paper for this
   space. Their judge methodology (§4.2) is worth comparing to AEGIS's.

### Tier 3 — Multi-agent attacks (sparse but growing)

This area is much less mature than single-agent attacks. Read for context;
the gap PROBE addresses lives here.

10. **Lee & Tiwari, 2024.** *Prompt Infection: LLM-to-LLM Prompt Injection
    within Multi-Agent Systems.* arXiv:2410.07283. One of the earliest
    multi-agent prompt-injection papers. Their threat model is close to
    AEGIS's existing prompt-injection suite — useful for understanding
    where PROBE goes beyond it.

11. **Khan et al., 2024.** *Debating with More Persuasive LLMs Leads to
    More Truthful Answers.* arXiv:2402.06782. Not adversarial framing per
    se, but multi-agent debate dynamics are exactly what `pr_consensus_break_001`
    is testing. Useful inspiration for objective design.

12. **Zhang et al., 2024.** *PsySafe: A Comprehensive Framework for
    Psychological-based Attack, Defense, and Evaluation of Multi-agent System
    Safety.* arXiv:2401.11880. Closest published thing to a multi-agent
    adversarial benchmark. Read for what they did and didn't measure;
    PROBE's TTC metric is something they don't have.

### Tier 4 — Skim only if curious

13. *Many-shot Jailbreaking* (Anil et al., Anthropic, 2024). Single-prompt
    long-context attack; orthogonal to PROBE but interesting.
14. *PoisonedRAG* (Zou et al., 2024). RAG-specific; tangential unless your
    victim configs use RAG-heavy IRIS pipelines.
15. *SneakyPrompt* (Yang et al., 2023). Image-generation specific; out of
    scope but cited frequently.

### Framework / engineering reading

- **bili-core source you should actually read before week 2:**
  - `bili/aegis/attacks/propagation_tracker.py` — your observer reuses it
  - `bili/aegis/evaluator/semantic_evaluator.py` — your success_evaluator
    reuses it; understand the cross-provider judge constraint logic
  - `bili/aegis/evaluator/evaluator_config.py` — judge prompt templates;
    you are adding `PROBE_JUDGE_PROMPT` here
  - `bili/aegis/suites/injection/run_injection_suite.py` — the cleanest
    existing runner to mirror
  - `bili/aegis/suites/_helpers.py` — `CONFIG_PATHS` constant you'll consume
  - `bili/aether/runtime/mas_executor.py` — how you invoke the victim
  - `bili/aether/compiler/` — what AETHER expects when you build the
    attacker MAS programmatically

- **LangGraph documentation** — specifically the conditional-edges and
  loop primitives. You'll need these for the per-turn loop in `attacker_mas.py`.
  https://langchain-ai.github.io/langgraph/

---

## 3-week milestone plan

Each milestone has explicit exit criteria. Treat the criteria as binary:
either they're met or the milestone isn't done.

### Week 1 — Reading, RFC sign-off, scaffolding

**Days 1–2: Reading.**
- Tier 1 papers fully read, notes captured
- Tier 2 papers skimmed
- Tier 3 papers read for context only
- bili-core source files in the engineering list read end-to-end

**Day 3: RFC review.**
- Re-read the RFC against your notes. Update anything you now disagree
  with based on the literature reading.
- Send the RFC to the MSU Denver maintainer for a courtesy review,
  even though you have permission to fork. Goal: catch design issues
  before code, and create a paper trail of upstream alignment.

**Days 4–5: Drop the scaffolding into your fork.**
- Fork `msu-denver/bili-core`. Branch: `aegis-probe`.
- Drop the `bili/aegis/probe/` and `bili/aegis/suites/probe/` directories
  into the fork.
- Wire imports, run `pytest bili/aegis/suites/probe/test_probe_structural.py
  -v` — should skip all tests (no results yet) but framework should not
  error.
- Run `python bili/aegis/suites/probe/run_probe_suite.py --stub` — should
  hit `NotImplementedError` cleanly, not import-error.

**Exit criteria:**
- [ ] RFC sent and reviewed
- [ ] Fork created, scaffolding committed
- [ ] Imports clean, structural pytest passes (or skips)
- [ ] First commit with a clear message tying back to the RFC

### Week 2 — Core implementation

The order matters. Build bottom-up so each layer can be tested in isolation.

**Day 1: BudgetState + ProbeSession serialization.**
- Implement `BudgetState.can_continue`, `record_turn`, cost computation.
- Implement `ProbeSession.to_csv_row` and `to_sidecar_json`.
- Unit tests for both.

**Day 2: SuccessEvaluatorNode.**
- Write the PROBE judge prompt template and rubric.
- Implement the cross-provider constraint check.
- Add `PROBE_JUDGE_PROMPT` and `PROBE_SCORE_DESCRIPTIONS` to
  `evaluator_config.py` (this is your one upstream-shaped change).
- Unit test against fixture victim outputs.

**Day 3: VictimObserverNode.**
- Implement using existing `PropagationTracker`.
- Unit test against fixture victim outputs.

**Day 4: PayloadCrafterNode + PlannerNode.**
- Prompt templates for both.
- The planner's behavior is policy-dependent, so its `__call__` is thin —
  most logic lives in the policies.

**Day 5: PAIRPolicy end-to-end.**
- Implement `plan_next_intent` and `should_continue`.
- Wire `AttackerMAS.run_session` for the linear policy case.
- Run one real-LLM session against `simple_chain.yaml` with a single
  PAIR objective.
- Manually inspect the sidecar JSON. The session should look like a
  recognizable multi-turn attack trajectory.

**Exit criteria:**
- [ ] All four node `__call__` methods implemented and unit-tested
- [ ] `BudgetState` enforces all four axes
- [ ] PAIR session against `simple_chain.yaml` runs end-to-end
- [ ] Sidecar JSON is valid and human-readable
- [ ] Cost of one PAIR session is documented (will inform Week 3 budget)

### Week 3 — Crescendo, TAP, evaluation, writeup

**Day 1: CrescendoPolicy.**
- Ladder generation on turn 0.
- Per-rung intent prompts.
- One real-LLM session run + manual inspection.

**Day 2: TAPPolicy.**
- Tree data structure + expansion + pruning.
- One real-LLM session run + manual inspection.
- (TAP is the riskiest of the three; if it slips into Day 3, the headline
  result still works with PAIR + Crescendo and you note TAP as v0.2.)

**Day 3: Run the evaluation matrix.**
- Generate a baseline using `bili/aegis/suites/baseline/run_baseline.py`
  with consistent model/temperature settings.
- Run PROBE: 5 objectives × 3–5 victim configs × 3 policies × 3 seeds.
- Watch the cost meter. Abort and reduce scope if you trip your personal
  cost ceiling.

**Day 4: Cross-suite analysis.**
- Combine PROBE CSV with the existing five suite CSVs.
- Generate the headline plots: TTC distribution by (policy × victim),
  PROBE-PAIR vs static-jailbreak success rate at matched cost,
  cross-policy comparison on a fixed objective set.
- Save plots and analysis script in `bili/aegis/suites/probe/analysis/`.

**Day 5: Writeup + PR.**
- Draft `docs/probe-design.md` summarizing architecture (~2 pages).
- Write a blog post version (~5 pages, suitable for personal blog or arXiv
  upload) — this is the artifact you actually link from your resume.
- Open a PR back to upstream (separate from your fork).
- Update your resume to point at the fork and the writeup.

**Exit criteria:**
- [ ] All three policies functional
- [ ] Evaluation matrix runs to completion within budget
- [ ] Headline plots generated and saved
- [ ] Design doc + blog post / arXiv preprint written
- [ ] PR opened to upstream (regardless of merge status; the PR is the
      portfolio artifact)
- [ ] Resume updated; LinkedIn updated

### What you don't try to ship in 3 weeks

- Streamlit UI integration (post-v0.1)
- Federated / cross-tenant follow-up (separate RFC)
- A defense module
- Workshop submission paper (post-v0.1, but the blog post is the seed)
- Backporting iteration to the other suites

---

## Risk register for the 3-week plan

- **Cost overrun:** Most likely failure mode. Mitigation: hard budget caps
  in `BudgetState`, run smoke tests before full eval matrix, default attacker
  model is small open-weight not Sonnet-class.
- **TAP harder than expected:** Mitigation noted above — fall back to PAIR
  + Crescendo for the headline, ship TAP as v0.2.
- **Upstream unresponsive on RFC review:** You have explicit permission to
  fork, so this isn't blocking. But chase once at end of Week 1; if no
  reply, proceed and treat the PR itself as the second review opportunity.
- **AETHER doesn't compose with programmatic MAS construction the way you
  expect:** Mitigation — the attacker MAS is internal to PROBE; if AETHER
  fights you, you can fall back to a plain LangGraph workflow without the
  AETHER schema layer. RFC § 5 calls this out.
- **Judge calibration is bad:** Mitigation — held-out 100-session human-rated
  subset (RFC § 9.3). If judge isn't calibrated, reduce PROBE claims to
  Tier 2 propagation signals only and document the limitation.
