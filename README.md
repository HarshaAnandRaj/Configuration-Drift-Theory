# Configuration Drift Theory

Start with [`configuration_drift_theorem.md`](configuration_drift_theorem.md).
It contains the canonical theorem, proofs, counterexamples, failure envelope,
and the claim protocol for applying CDT to a new system.

The core result is a two-level recurrence separation:

\[
G_X(x,A_\varepsilon)<\infty
\quad\text{while}\quad
\pi(X)\text{ is recurrent on a declared structural target}.
\]

Under verified two-sided power-law heat-kernel assumptions, the convenient
sufficient condition is

\[
d_s(\pi(X))\le 2<d_s(X).
\]

Files:

- `configuration_drift_theorem.md` — authoritative mathematics and use rules.
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

```powershell
python -m unittest -v test_cdt_empirical_audit.py test_cdt_simulation_campaign.py test_cdt_registered_results.py
python -m py_compile cdt_empirical_audit.py experiments\cdt_simulation_campaign.py
```

Audit a trajectory (choose the scales, lag, and projection before examining the
result):

```powershell
python cdt_empirical_audit.py paths.npy `
  --epsilon 0.05 --radius 0.5 --lag 10 --projection 0,1
```

Finite output is evidence about a registered model and horizon; it is not proof
of infinite-time recurrence, causality, life, or functional success.
