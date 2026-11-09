# Experiment completion ledger

All currently executable goals from the application guide and its defined
phenomena have been exercised and recorded: **12 application/model suites plus
2 separately planned remaining-phenomena checks**. Physical and deployment
claims remain blocked by the concrete dependencies below. This does not mean
all conceivable CDT experiments are exhausted or that the open mechanism has
been proved.

## Plans, records, and reproduction

- [Application plan](../experiments/cdt_application_preregistration_20261109.md),
  committed before execution as `9e9f307`.
- [Application results](../results/application_20261109/evidence_ledger.md): all
  independent replicates and arms, descriptive intervals, eight multiplicity-
  adjusted primary tests, functional checks, and negative controls.
- [Remaining-phenomena plan](../experiments/cdt_phenomena_followup_plan_20261109.md),
  separately committed before its execution as `02f1b003` after identifying two
  coverage gaps. No completed campaign threshold was changed.
- [Long-tail and clock-control results](../results/phenomena_followup_20261109/evidence_ledger.md),
  including losslessly archived per-path records.
- [Summary figure](../results/application_20261109/summary.png).

The application campaign used 16 independent replicates per main suite,
eight per learned-gate arm, and one run each for the exact enumeration and the
two supplied recordings. Smoke runs were implementation checks only. Raw
replicate records, seeds, versions, executable/plan/input hashes, analysis
metadata, CSV summaries, and checksums are included. September artifacts remain
unchanged. The only legacy training change adds an optional fixed-gate control;
the default repaired update is preserved.

## Application goals

| Goal | Executed test | Outcome and boundary |
|---|---|---|
| Preserve task states under hidden neural variation | A3 fitted autonomous linear recurrent oscillator, matched nuisance/task noise | Hidden-noise task MSE remained negligible; visible-noise mean MSE 8.23. All 16 functional checks passed. This exploits a specified invariant-subspace model, not a general neural recovery law. |
| Recognize memory content across context changes | A4 raw, learned structural, random8, constant maps; separate calibration and test sets | Structural retrieval accuracy 1.00 versus raw 0.154. Only 15/16 passed all functional checks: replicate 10 positive acceptance was 0.8848, below 0.90. Failure retained. |
| Detect gait interruption and wrong order | A5 kinematic phase control with translation, speed, pause, reversal, constant-map controls | Pause raised longest gap from 45 to 141 steps. Reversal preserved return fraction near 0.062 but tracking/order failed; constant output returned constantly while tracking failed. No physical robot validation. |
| Reject nuisance without masking true sensor changes | A6 separate calibration and factorial nuisance/signal interventions | Full readout shifted RMSE 0.0103 versus restricted 1.577; all 16 functional checks passed. Only the specified linear mixing model was tested. |
| Distinguish repeated form and action direction | A7 six synthetic classes, nuisance transformations, random/shape-only/constant/order-shuffle controls | Structural six-class accuracy 1.00; random 0.172, shape-only 0.492, point-order-shuffled 0.165. All 16 synthetic functional checks passed. |
| Check supplied drawing observations | A10 both CSV recordings, complete-stroke units, registered radii | Historical structural matching about 0.94, but zero subsequent matches to the first-stroke anchor at radius 0.15. No labeled negative gestures or independent subjects; this is not evidence of anchored recurrence. |
| Probe realization-dependent repulsion | A8 stable local-time simulator, dimensions 2/3 and gamma -0.5 to 10 | D=2 historical rate fell from 0.5695 at gamma=0 to 0.1113 at gamma=2; projected history remained high. Finite mechanism pattern reproduced; asymptotic proof remains absent. |
| Test the repaired recurrence diagnostic | A11 iid, AR(1), neutral and drifted walks under phase/steps nulls | No obsolete-rule positives in these runs; scores depended strongly on null choice. Neither diagnostic sign nor threshold identifies microscopic repulsion. |
| Test learned versus fixed dimensional gates | A12 repaired training with actual optimized gates and exactly frozen controls | Higher reward raised free-run novelty but also worsened held-out driven error. All fixed gates stayed 0.5. This identity-task probe does not demonstrate autonomous functional recovery. |

All eight primary model contrasts passed their registered exact sign-test
criterion after Bonferroni correction. This does **not** erase the memory
functional failure or validate synthetic-model assumptions in natural systems.
Several controls are deliberately constructed solvable contrasts, so their
small p-values are not evidence for a new universal law.

## Every defined phenomenon has a recorded check

| Phenomenon from the guide | Recorded check |
|---|---|
| Escape with recurring structure | A1 and A2; also the finite neural construction in A3. |
| Sparse structural recurrence | Free projection in A1, last-half fraction 0.00971 at horizon 4096 versus 0.33305 for the restoring law. Asymptotic classification remains analytic. |
| Positive structural return rate | A1 restoring model tracked the analytic 1/3 rate; mean longest observed miss run was still 71 steps. |
| Projected drift leakage | A2 hidden and neutral projected tail counts matched pathwise under paired increments; visible drift suppressed returns at the specified cutoff scale. |
| Long fine-return tails | P1: 8,192 paths/dimension, finite-horizon last observed visits plus deterministic weighted Green partial sums. D=4 Monte Carlo hit an event floor even while its analytic partial sum kept growing. |
| Novelty created by bookkeeping | P2: adding a clock made both constant and period-two paths have 257 unique augmented states and zero exact historical returns; discarding the clock restored the original metrics. |
| Recurrence without function | Reversed and constant gait controls in A5; constant memory map in A4; shape-only representation in A7. |
| Approximate structural-law robustness | A9 exact six-step path-law TV enumeration satisfied the accumulated error bound. Constant-bias long-run limitations remain analytic, not disproved by short runs. |

## Concrete blockers and unestablished claims

| Remaining claim | Missing dependency or proof obligation |
|---|---|
| Physical locomotion stability, falls, and energy | Robot hardware or a validated body/contact/energy simulator with a specified controller. Kinematic phase tracking cannot supply these outcomes. |
| Real sensor benefit | Instrument recordings paired with independent calibration/reference measurements. |
| Deployment neural/memory benefit | A specified deployed task, operating conditions, representative held-out data, and independent functional targets. |
| Real gesture discrimination and population effects | Labels for different actions and directions, independent participants, and acquisition metadata; the two supplied recordings lack these. |
| Autonomous functional recovery by learned dimensions | A training/recovery task and controller evaluated on autonomous function; driven identity reconstruction and free-run cell novelty do not establish it. |
| Infinite-time position avoidance under local-time repulsion | A model-specific recurrence/avoidance proof. More finite simulation cannot discharge it. |

## Verification

`python -m unittest discover -v` runs the existing diagnostic/registered-result
checks, repaired-instrument checks, new implementation checks, and evidence
integrity/negative-result checks. One independent PyTorch-autograd cross-check
is explicitly skipped because the optional PyTorch dependency is absent; it
is not reported as passed. Exact fixed-gate and finite-difference checks run
without it.

Final discovery result: **34 passed, 1 explicitly skipped**. Source/plan hashes,
lossless archive equality, complete replicate counts, retained negative
outcomes, output checksums, compilation, and document links were also checked.

A [baseline integrity audit](../results/application_20261109/baseline_integrity.json)
verified that the old evidence bytes match the original repository commit.
Two pre-existing summary hashes correspond to CRLF line endings while the
committed files use LF. This formatting discrepancy is recorded separately;
neither old data nor the old checksum manifest was edited. All new output
checksums match their recorded artifacts.

To reproduce the main campaign in a new directory:

```bash
python experiments/cdt_application_campaign.py --output-dir /tmp/cdt_applications_reproduction
MPLCONFIGDIR=/tmp/cdt_mpl python experiments/summarize_cdt_applications.py --input-dir /tmp/cdt_applications_reproduction
```

Follow-up reproduction and decompression instructions are in its
[README](../results/phenomena_followup_20261109/README.md). Runners refuse to
overwrite raw evidence. Derived summaries can be regenerated from frozen raw
records; their analysis source hashes are recorded separately.
