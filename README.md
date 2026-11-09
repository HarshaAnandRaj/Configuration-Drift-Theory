# Configuration Drift Theory

Start with [`configuration_drift_theorem.md`](configuration_drift_theorem.md).
It contains the canonical theorem, proofs, counterexamples, and the protocol
for applying CDT to a specified system. The
[2026-11-09 revision notes](docs/theorem_revision_20261109.md) explain the
mathematical changes and the remaining open mechanism question.

For applications, start with [use cases and phenomena](docs/use_cases_and_phenomena.md).
It defines neural-state monitoring, memory retrieval, locomotion, sensor-drift,
and repeated-gesture experiments with controls and independent functional
outcomes. These are proposed uses, not established real-world validations.

For an irreducible countable-state Markov chain with a strongly lumpable
structural projection, returns to a nonempty finite full-state target are
almost surely finite while returns to a nonempty finite structural target
are almost surely infinite **if and only if**

$$
G_P(a,a)<\infty
\quad\text{and}\quad
G_Q(b,b)=\infty.
$$

Here `P` and `Q` are the full and projected transition matrices. Every
structural fiber must then contain infinitely many full states. Two fixed
finite targets in the same irreducible chain cannot give this split.

Under two-sided pure-power return-kernel bounds, the criterion becomes

$$
d_s(\pi(X))\le 2<d_s(X).
$$

The theorem also gives an explicit lazy product walk with separation exactly
when `m <= 2 < D`, and a separate Brownian classification for drift hidden
from a projection. These use classical recurrence results. They do not prove
that realization-dependent self-repulsion causes the split; that remains a
model-specific open problem for the tested local-time walk.

Infinitely many structural returns can still have **zero long-run frequency**.
The revision now distinguishes null recurrence from positive recurrence, gives
a restoring model with structural frequency `1/3`, and defines finite-window
count and return-gap contracts. It also bounds the effect of an approximate
projected law; a small persistent drift error can destroy long-run recurrence.

Try the three-law illustration (positive-rate, sparse, and lost structural
recurrence):

```bash
python examples/cdt_use_case_demo.py --steps 8192 --paths 128 --seed 20261109
```

Its analytic classifications are specified by the model. Finite simulation
outputs are illustrative, and are separate from the frozen evidence campaign.

Files:

- `configuration_drift_theorem.md` — authoritative mathematics and use rules.
- `docs/theorem_revision_20261109.md` — change rationale and validation record.
- `docs/use_cases_and_phenomena.md` — precise phenomena, proposed applications,
  controls, and limits.
- `examples/cdt_use_case_demo.py` — positive-rate/null/transient projection comparison.
- `configuration_drift_theory.md` — research notebook and historical theory.
- `configuration_drift_full_report.md` — empirical/rebuild report.
- `cdt_empirical_audit.py` — finite-horizon trajectory diagnostics that keep
  anchored, historical, projected, and discovery observables separate.
- `test_cdt_empirical_audit.py` — regression tests for the audit utility.
- `experiments/cdt_simulation_preregistration.md` — frozen primary campaign.
- `experiments/cdt_followup_preregistration.md` — frozen corrective follow-ups.
- `results/cdt_simulation_evidence_ledger.md` — registered results, limits, and
  corrections.

Run the checks:

```bash
python -m unittest -v test_cdt_empirical_audit.py test_cdt_simulation_campaign.py test_cdt_registered_results.py
python -m py_compile cdt_empirical_audit.py experiments/cdt_simulation_campaign.py
```

Audit a trajectory (choose the scales, lag, and projection before examining the
result):

```bash
python cdt_empirical_audit.py paths.npy --epsilon 0.05 --radius 0.5 --lag 10 --projection 0,1
```

Finite output is evidence about a registered model and horizon; it is not proof
of infinite-time recurrence, causality, life, or functional success.
