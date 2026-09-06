# CDT simulation campaign: preregistration

**Frozen:** 2026-09-05, before running `cdt_simulation_campaign.py`  
**Canonical theorem under test:** `configuration_drift_theorem.md`

## Aim

Find, without selecting only favorable cases:

1. where full-state transience and projected recurrence separate as predicted;
2. where the separation holds more broadly than the original self-repulsion
   story suggested;
3. where finite-horizon observables or proposed mechanisms fail;
4. which theorem or measurement statements must change.

The campaign distinguishes exact model theorems from Monte Carlo evidence.
Finite runs never prove infinite-time recurrence.

## Frozen conventions

- Master seed: `20260905`; suite-specific seeds are deterministic offsets.
- Primary horizons: `256, 512, 1024, 2048, 4096`.
- Baseline independent paths: `M=8000`.
- Self-repulsion paths: `M=240` per cell, `T=4096`.
- Historical-recurrence paths: `M=400` per dimension, `T=4096`.
- Finite-space paths: `M=240` per cell.
- Confidence intervals: path-level nonparametric bootstrap, 500 resamples,
  percentile 95% interval. The path, not the time step, is the resampling unit.
- Anchored return means return to the registered initial state/cell.
- Historical recurrence excludes the latest `tau=8` states.
- `fine` means exact lattice state. `rhyme` means the registered coordinate
  projection, not a post-hoc larger radius.
- A failed numerical estimator is reported as a failure; its output is not
  replaced by the analytic answer.

## Registered suites and predictions

### S1. Product/projection phase map

Model: coordinate simple random walk on `Z^D`, `D=1..6`. The structural
map keeps the first `m=1..D` coordinates.

Exact theorem prediction:

```text
full state recurrent      iff D <= 2
projected state recurrent iff m <= 2
CDT separation            iff m <= 2 < D
```

Primary outcome: tail Green increment
`sum_{t=H/2+1}^H P(X_t=0)` across horizons. Its expected scaling is
`H^(1-k/2)` for dimension `k != 2`, and `Theta(1)` per doubling window at
`k=2`. Quantitative slope error is reported; no fitted threshold changes the
analytic prediction.

### S2. Hidden versus visible drift

Model: `D=4` biased lattice walk; projection keeps coordinates `(0,1)`.
Drift strengths: `delta = 0, 0.02, 0.05, 0.10, 0.20`.

- Hidden drift acts on coordinate 3: full recurrence must be suppressed while
  projected recurrence retains the symmetric two-dimensional class.
- Visible drift acts on coordinate 0: both full and projected anchored
  recurrence must be suppressed.
- Finite-horizon crossover is expected near
  `Pe_T = |v| sqrt(T) / sigma_step ~= 1`; results are plotted/reported against
  this dimensionless number.

This suite tests a region where CDT should work **without self-repulsion** and
therefore more broadly than the old `gamma > 0` claim.

### S3. Self-repulsion map

Model: destination-local-time walk with weights
`exp(-gamma * visits(destination))`, dimensions `D=1,2,3`,
`gamma=0,0.1,0.5,1,2`. Projection keeps coordinate 0.

This is exploratory because the sign of `gamma` is not a theorem.

Registered finite-horizon labels relative to the same-dimension neutral arm:

- `beneficial window`: full historical recurrence decreases at least 25%,
  projected historical recurrence retains at least 75%, and discovery rises at
  least 25%;
- `over-repulsive`: projected recurrence retains less than 50%;
- otherwise `mixed/no material separation`.

The raw ratios and bootstrap intervals take precedence over labels.

### S4. Anchored versus historical recurrence

Model: an independent set of neutral lattice walks, `D=1..6`.

Prediction: anchored transience for `D>=3` does **not** imply historical
non-repetition. Historical revisit rates and two-step backtrack rates should
remain nonzero. Results are reported for exclusion lags `1,8,32` on an
independent subset of paths.

### S5. Finite-capacity spaces

Model: simple random walk on discrete tori:

- `(D,L)=(2,16),(2,32),(3,8),(3,12)`;
- horizons `1,2,4,8` times the number of states.

Prediction: finite irreducibility forces recurrence in every dimension, while
the new-state fraction tends downward as capacity is covered. Thus the
infinite-space spectral shortcut is inapplicable and novelty eventually
exhausts.

### S6. Mechanism-identification counterexamples

Models:

- irrational rotation on the circle;
- iid continuous sampling on the two-dimensional unit torus;
- constant structural projection.

Prediction: exact sampled equality can vanish while coarse recurrence persists
without self-repulsion, high dimension, or realization-dependent drift. A
constant projection passes structural recurrence vacuously and is flagged as
non-informative. The registered coarse cell is circular distance at most `0.05`
from the initial first coordinate (cell measure `0.10`).

## Decision discipline

After execution, corrections are made when any of the following occurs:

1. an exact model prediction is contradicted outside its Monte Carlo interval;
2. an operational estimator gives the wrong answer on a known control;
3. a proposed necessary mechanism is absent in a successful case;
4. a proposed sufficient mechanism fails in a registered case;
5. a finite-size crossover makes the advertised test unusable at the tested
   horizon;
6. a result depends on a trivial or post-hoc projection.

No hypothesis, threshold, seed, or primary observable above will be changed
after results are observed. Any follow-up experiment will be labeled as such.
