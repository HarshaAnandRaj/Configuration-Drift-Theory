# CDT application campaign: frozen analysis plan

This plan precedes the new campaign run. Existing illustrative results and
legacy scripts are known; this is a prospective **model/application campaign**,
not a blinded rediscovery of classical recurrence results. Source and plan
hashes, versions, seeds, and input hashes will be recorded in the run manifest.
Frozen September evidence will not be overwritten.

## Scope and stopping rule

Run each suite below once at the specified sizes, record every seed and arm,
and retain failures. Run implementation checks on small configurations before
the full campaign; do not retune thresholds or claim those checks as evidence.
Correct implementation errors only with an explicit amendment and rerun the
affected suite. Stop after all feasible suites have results and every external
dependency has a named blocker. No finite run resolves the asymptotic
self-repulsion proof or proves a real-world benefit.

Master seed: `20261110` (a seed identifier, not a claim about the run date).
Independent replicate IDs: `0,...,15`. Primary inference uses independent
replicates, not time samples. Default bootstrap: 2,000 paired replicate draws,
95% descriptive intervals. Eight directional primary tests use an exact
one-sided sign test against the listed effect margin and Bonferroni correction
over eight tests. A tie/nonfinite effect counts as no success. P-values concern
the across-replicate probability of exceeding the specified margin; they are
not tests of infinite-time recurrence. Secondary metrics are descriptive.

## Registered suites and primary contrasts

| ID | Design | Primary per-replicate contrast and margin |
|---|---|---|
| A1 rates | Three laws in `examples/cdt_use_case_demo.py`; 64 paths, 4,096 steps per replicate. | Restoring minus free last-half structural frequency > 0.25. |
| A2 Gaussian leakage | 2D Gaussian walks, 2,048 paths, 4,096 steps; neutral, hidden drift 0.08, visible drift 0.08; noise SD 1; projection first coordinate, radius 0.5; horizons 256/1024/4096. Paired increments. | Hidden minus visible projected last-half visit count at 4096 > 3. |
| A3 neural | A fitted autonomous linear recurrent oscillator with period 48 and six decaying nuisance coordinates. Fit recurrence and a two-output task decoder on 1,024 independent training states. Evaluate 16 new initial phases for 384 steps. Baseline, decoder-nullspace noise, equally scaled task-plane noise (SD 0.2), matched noise. No teacher forcing after initialization. | Visible minus hidden held-out waveform MSE > 0.05. |
| A4 memory | Eight content classes mixed with eight nuisance dimensions by a random orthogonal map. Fit the structural readout on 1,024 labeled training examples; calibrate same-content distance threshold on a separate 256 examples. Test 512 changed-context queries against an eight-item bank. Raw, learned structure, dimension-matched random map, constant map; identical queries. | Learned structural retrieval accuracy minus raw accuracy > 0.25. |
| A5 gait | Kinematic phase/forward-motion model, period 48, 2,048 steps. Baseline, changed global origin, faster translation, 96-step phase pause, reverse phase order, constant representation. Phase tracking is the functional task; no body dynamics, falls, or physical energy are simulated. | Pause minus baseline longest structural miss run > 64 steps. |
| A6 sensors | Four observed channels are an orthogonal mixture of two signal and two nuisance coordinates. Fit full and restricted readouts on 1,024 independent calibration samples. Evaluate 512 samples in a nuisance-shift × actual-signal-change factorial. Constant map included. | Under nuisance shift, restricted minus full readout RMSE > 0.5. |
| A7 gestures | Three shapes × two traversal directions; 64 samples per stroke. Sixteen training strokes/class, eight calibration/class, 32 held-out/class. Register centroid/scale normalization, paired Fourier magnitudes and signed area as structure; compare raw, random same-dimensional map, shape-only and constant maps. Test point-order permutation with identical point clouds. | Structural minus random-map held-out six-class accuracy > 0.25. |
| A8 mechanism | Reuse the frozen destination-local-time simulator, dimensions 2/3, gamma -0.5/0/0.5/2/10, 2,048 steps, 16 independent seeds/arm. Historical lag stays eight. Report anchored/historical separately, discovery, and attraction control. | D=2 neutral minus gamma=2 full historical rate > 0.10. |

Success of a primary contrast alone is insufficient for a useful application.
Registered functional checks: neural hidden-noise MSE < 0.01 and structural
cadence hits >= 0.9; memory structural accuracy >= 0.9, positive-pair acceptance
>= 0.9 and negative-pair false acceptance <= 0.1; sensors full-readout RMSE
< 0.1 and signal sign accuracy >= 0.9; gestures structural six-class accuracy
>= 0.9. Summarize the fraction of independent replicates meeting each check;
do not silently replace a failed check with a favorable primary contrast.

## Additional feasible checks

- **A9 approximation:** enumerate all six-step paths for a two-state reference
  kernel with switch probability 1/4. Perturb rows toward state one by
  delta_n=(1/32)2^-n. Record exact path-law TV and the sum bound. Also retain
  the small constant-bias counterexample as an analytic limitation.
- **A10 drawing recordings:** use both supplied CSV files, with declared stroke
  boundaries. Resample strokes to 64 arc-length points; raw RMS target radius
  8 pixels and structural descriptor radius 0.15; exclude within-stroke
  adjacency by treating each complete stroke as one observation. Compare
  actual stroke descriptors against independently point-order-permuted strokes.
  These recordings lack independent content/direction labels and participant
  metadata. Report descriptive matching and order sensitivity only; no
  discrimination accuracy, causal mechanism, or independent-subject interval.
- **A11 diagnostic:** 16 replicates of iid, stationary AR(1) rho=0.8,
  neutral Gaussian walk, and drifted Gaussian walk (drift 0.1), each length
  256 and dimension two. Evaluate repaired `gamma_hat` under phase/steps nulls,
  tau=4, M=256, K=7, nblocks=8. Report estimates, null versions, interval
  availability, and the obsolete 0.4-rule positive frequency descriptively.
  Do not call this a calibrated false-positive rate or microscopic-gamma test.
- **A12 learned gates:** repaired intrinsic-reward toy, H=8, T=96, 60 epochs,
  seeds 0,...,7; lambda 0/0.01/0.05/0.2. Compare learned sigmoid gates with
  identically initialized fixed gates at lambda=0 and 0.05. Preserve default
  legacy behavior when adding the fixed-gate switch. Record training loss,
  held-out driven identity-task MSE, free-run novelty and gate counts. This
  probes self-selected gates, not learned recovery of an autonomous memory
  task. No dimension-scaling prescription or universal alive/dead verdict.

## Blockers to record rather than replace with synthetic evidence

Physical robot stability/fall/energy trials require a robot or a validated
dynamic simulator and a specified controller. Instrument validation requires
real sensor calibration/reference data. Neural or memory deployment claims
require a user-selected task and deployment data. Behavioral discrimination
requires labeled different gestures, independent subjects, and acquisition
metadata. Asymptotic self-repulsion requires a proof; additional simulation
cannot supply it. These do not prevent the controlled suites above.
