# CDT simulation follow-ups: preregistration

**Frozen:** 2026-09-05, after the six-suite campaign and before running
`cdt_followups.py`.

These tests address two weaknesses found by the registered campaign. They do
not replace or alter its outcomes.

## F1. Does hidden drift create the split?

The first campaign used `D=4`, whose neutral full walk is already transient.
It therefore tested projection invariance but not whether hidden drift caused
full transience.

- Model: coordinate random walk on `Z^2`.
- Projection: coordinate 0.
- Arms: neutral; hidden drift on coordinate 1; visible drift on coordinate 0.
- Drift strengths: `delta=0.02,0.05,0.10`.
- Horizons: `256,512,1024,2048,4096,8192`.
- Paths: `M=12000` per arm; master seed `20260905` with new offsets.
- Outcome: anchored tail Green increment in `(H/2,H]`, for full and projected
  states; 500 path-bootstrap resamples.

Predictions:

1. Neutral full tail increments have slope approximately zero and projected
   increments slope approximately `1/2`.
2. Hidden drift suppresses full returns after `Pe_H` crosses order one while
   leaving the projected law unchanged.
3. Visible drift suppresses both.

Because exact full returns become rare after crossover, zero-event cells are
reported as floor-limited. The projected hidden-drift arm is the primary causal
control.

## F2. Does the self-repulsion result meet the theorem's observable?

The first campaign's registered labels used historical recurrence. The theorem
uses anchored projected recurrence. This follow-up measures both.

- Model: the same destination-local-time walk as S3; initial-origin local time
  is excluded, matching the original implementation.
- Dimensions: `D=2,3`.
- Projection: coordinate 0.
- Repulsion: `gamma=0,0.5,1,2,5,10`.
- Horizons: `256,512,1024,2048,4096`.
- Paths: `M=160` per cell; master seed `20260905` with new offsets.
- Outcomes: full and projected anchored tail counts at every horizon; final
  historical recurrence with lag 8; discovery fraction; 500 path bootstraps.

Diagnostic classification for the projected anchored tail slope:

- `compatible with persistent anchored projection`: slope point estimate is
  at least `-0.10`;
- `finite-horizon decay warning`: slope is below `-0.10`;
- `unestimable`: fewer than three horizons have positive mean counts.

This is deliberately a finite-horizon diagnostic, not an asymptotic proof.
Historical recurrence near one cannot override an anchored decay warning.

## Correction rules

- F1 may strengthen the hidden-drift example only if the hidden projection
  tracks neutral while full returns are suppressed beyond crossover.
- F2 may support a mechanism window only as a historical-recurrence result
  unless anchored projection is also compatible with persistence.
- Strong `gamma` behavior is reported even if it reverses the earlier pattern.
- No thresholds, arms, or seeds above will change after execution.
