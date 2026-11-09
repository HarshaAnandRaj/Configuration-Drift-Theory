# CDT application campaign: results and completion ledger

Run started: `2026-11-09T18:17:30.257717+00:00`; finished: `2026-11-09T18:18:41.282268+00:00`.

The twelve planned suites completed. These are controlled model tests plus
two unlabeled drawing recordings, not real-world deployment validations.
The plan was committed before execution as
[`9e9f307`](https://github.com/HarshaAnandRaj/Configuration-Drift-Theory/commit/9e9f307ef55376b0cb0d079d11feeef562092eac).
All arms and independent-replicate records are retained in `A1.json` through
`A12.json`. Smoke runs are excluded. September evidence is unchanged.

## Registered primary results

8/8 primary contrasts met the registered sign-test criterion after
Bonferroni correction. That supports the specified *model contrasts*, not a
universal mechanism. CIs below are descriptive bootstrap intervals across
independent replicates. Sign tests ask whether the effect exceeds its
registered margin more often than half the time; units differ by row.

| Suite | Contrast | Mean effect [95% CI] | Margin | Replicates above margin | Adjusted p | Functional checks |
|---|---|---:|---:|---:|---:|---|
| A1 | Restoring minus free tail frequency | 0.32334 [0.3219, 0.32465] | 0.25 | 16/16 | 0.00012207 | not an application task |
| A2 | Hidden minus visible tail visits | 15.138 [14.957, 15.306] | 3 | 16/16 | 0.00012207 | not an application task |
| A3 | Visible minus hidden neural MSE | 8.2306 [7.2622, 9.2131] | 0.05 | 16/16 | 0.00012207 | 16/16 |
| A4 | Structural minus raw memory accuracy | 0.8457 [0.83374, 0.85693] | 0.25 | 16/16 | 0.00012207 | 15/16 |
| A5 | Pause minus baseline longest gap | 96 [96, 96] | 64 | 16/16 | 0.00012207 | not an application task |
| A6 | Restricted minus full sensor RMSE | 1.5668 [1.3969, 1.7231] | 0.5 | 16/16 | 0.00012207 | 16/16 |
| A7 | Structural minus random gesture accuracy | 0.82812 [0.81999, 0.83496] | 0.25 | 16/16 | 0.00012207 | 16/16 |
| A8 | Neutral minus repelled historical rate | 0.45813 [0.39617, 0.5254] | 0.1 | 16/16 | 0.00012207 | not an application task |

A favorable contrast does not override a failed functional check. Training
and test distributions, nuisance coordinates, and task labels are specified
by these synthetic models; applicability to real systems remains untested.

## A1–A2: recurrence rate and projected drift

| Structural law | Mean last-half frequency at 4096 | Mean longest observed miss run |
|---|---:|---:|
| restoring | 0.33305 | 71.03 |
| free | 0.00971 | 2566.67 |
| visible_drift | 0.00000 | 4088.73 |

The positive-rate example still has long gaps. Return rate and deadline
performance must be reported separately. For A2, the Gaussian cutoff scale
is 312.5 steps at visible drift 0.08 and noise variance one.

| A2 arm | Projected last-half visits at 4096 | Full last-half visits |
|---|---:|---:|
| neutral | 15.14487 | 0.08585 |
| hidden | 15.14487 | 0.00000 |
| visible | 0.00644 | 0.00000 |

Zero tail events remain finite-horizon detection floors; the analytic
model, not those zeros, establishes transience.

## A3–A7: application models

### Autonomous recurrent neural model

| Intervention | Held-out waveform MSE | Structural cadence-hit fraction | Full cadence-hit fraction |
|---|---:|---:|---:|
| baseline | 8.3325e-27 | 1.0000 | 1.0000 |
| hidden_noise | 8.4235e-27 | 1.0000 | 0.0840 |
| visible_noise | 8.2306 | 0.0029 | 0.0010 |

The recurrence matrix and task decoder were fitted on independent training
states; evaluation was autonomous after initialization. This is a linear
oscillator with known invariant subspaces, not a general nonlinear RNN or
a learned adaptive-dimensional recovery demonstration.

### Memory under changed context

| Map | Retrieval accuracy | Positive-pair acceptance | Negative-pair false acceptance |
|---|---:|---:|---:|
| raw | 0.1543 | 0.0000 | 0.0000 |
| structure | 1.0000 | 0.9385 | 0.0000 |
| random8 | 0.1398 | 0.0089 | 0.0068 |
| constant | 0.1250 | 1.0000 | 1.0000 |

Memory replicates failing any registered functional check: `[10]`.
The raw score improvement is not a substitute for acceptance calibration.
Constant-map acceptance is deliberately exposed as a false semantic match.

### Gait timing and order

| Intervention | Structural fraction | Longest miss run | Ordered transitions | Tracking MSE |
|---|---:|---:|---:|---:|
| baseline | 0.0620 | 45.00 | 1.0000 | 8.9821e-06 |
| translated | 0.0620 | 45.00 | 1.0000 | 8.9821e-06 |
| faster | 0.0620 | 45.00 | 1.0000 | 8.9821e-06 |
| pause | 0.0591 | 141.00 | 0.8839 | 0.04688 |
| reverse | 0.0620 | 45.00 | 0.0000 | 0.99876 |
| constant | 1.0000 | 0.00 | undefined | 1.0036 |

This is kinematic phase tracking. It cannot measure real falls, body
stability, contact forces, or physical energy. Reversed or constant
representations can have favorable recurrence counts and fail the task.

### Sensor nuisance shift

| Readout | RMSE after nuisance shift | Sign accuracy after actual signal change |
|---|---:|---:|
| full | 0.01025 | 1.0000 |
| restricted | 1.577 | 0.5632 |
| constant | 0.81694 | 0.4977 |

The full readout is calibrated on separate samples of a specified linear
mixing model. It demonstrates that nuisance rejection can coexist with
sensitivity to true changes; it does not establish real instrument accuracy.

### Synthetic shapes and traversal direction

| Representation | Held-out six-class accuracy |
|---|---:|
| raw | 0.1709 |
| structure | 1.0000 |
| random9 | 0.1719 |
| shape_only | 0.4922 |
| constant | 0.1667 |
| structure_point_order_permuted | 0.1647 |

Labels distinguish circle/ellipse/triangle and traversal direction. The
signed-area feature preserves the task-relevant direction distinction;
a shape-only map deliberately loses it. Point-order permutation preserves
the point cloud but changes the action.

## A8–A11: mechanism, robustness, recordings, and diagnostic

| Dimension | Gamma | Full historical rate | Projected historical rate | Full anchored tail count | Discovery fraction |
|---|---:|---:|---:|---:|---:|
| 2 | -0.5 | 1.0000 | 1.0000 | 64.0000 | 0.0041 |
| 2 | 0 | 0.5695 | 0.9804 | 0.6875 | 0.3224 |
| 2 | 0.5 | 0.2621 | 0.9258 | 0.0625 | 0.5724 |
| 2 | 2 | 0.1113 | 0.9095 | 0.0000 | 0.8124 |
| 2 | 10 | 0.0629 | 0.9010 | 0.0000 | 0.9238 |
| 3 | -0.5 | 1.0000 | 1.0000 | 0.0000 | 0.0117 |
| 3 | 0 | 0.1517 | 0.9482 | 0.0000 | 0.6649 |
| 3 | 0.5 | 0.0639 | 0.9417 | 0.0000 | 0.8031 |
| 3 | 2 | 0.0114 | 0.9519 | 0.0000 | 0.9542 |
| 3 | 10 | 0.0002 | 0.9587 | 0.0000 | 0.9996 |

Self-repulsion and attraction change finite historical recurrence. Anchored
and historical measurements remain separate. This repeats a model-specific
finite-horizon effect and does not prove asymptotic position avoidance.

A9 exact six-step path TV: `1214409497/34359738368`;
sum bound: `63/1024`; bound holds:
`True`. Small constant errors remain an
analytic counterexample to universal recurrence preservation.

### Supplied drawing recordings (descriptive only)

| File | Strokes | Fine anchored fraction | Structural anchored fraction | Structural historical fraction | Permuted anchored fraction |
|---|---:|---:|---:|---:|---:|
| drawing_data.csv | 203 | 0.0000 | 0.0000 | 0.9455 | 0.0000 |
| drawing_data_v1.csv | 142 | 0.0000 | 0.0000 | 0.9433 | 0.0000 |

Each stroke is closed and resampled by arc length to 64 points; centering,
RMS scale normalization, Fourier magnitudes, and signed area define the
structural map. There are no independent gesture-class labels or subject
metadata, so these fractions cannot establish semantic discrimination,
population uncertainty, or a realization-induced causal mechanism.

At the registered structural tolerance, neither recording returned to its
first-stroke anchor. High historical matching refers to other strokes and
must not be cited as evidence of anchored structural recurrence.

### Repaired diagnostic on processes without local-time repulsion

| Process | Null | Mean diagnostic estimate | Obsolete 0.4-rule positive fraction |
|---|---|---:|---:|
| iid | phase | -0.0063 | 0.0000 |
| iid | steps | -30.8653 | 0.0000 |
| AR08 | phase | 0.0057 | 0.0000 |
| AR08 | steps | -5.7414 | 0.0000 |
| walk | phase | -0.1980 | 0.0000 |
| walk | steps | -0.1159 | 0.0000 |
| drift | phase | -0.2871 | 0.0000 |
| drift | steps | -0.1447 | 0.0000 |

These rates are not calibrated false-positive rates. They demonstrate the
behavior of the repaired instrument under specified null processes.
Neither sign nor the obsolete threshold identifies microscopic repulsion.

## A12: self-selected gates versus fixed gates

| Lambda | Gates learned | Held-out driven MSE | Free-run new-cell fraction | Mean gate sum | Mean open-gate count |
|---|---|---:|---:|---:|---:|
| 0 | True | 0.0033711 | 0.0046 | 4.2911 | 6.000 |
| 0.01 | True | 0.0033815 | 0.0046 | 4.2921 | 6.000 |
| 0.05 | True | 0.0034753 | 0.0054 | 4.2974 | 6.000 |
| 0.2 | True | 0.0050187 | 0.0212 | 4.3421 | 6.500 |
| 0 | False | 0.0039064 | 0.0046 | 4.0000 | 0.000 |
| 0.05 | False | 0.0039873 | 0.0058 | 4.0000 | 0.000 |

The gates are actually optimized in learned arms and exactly frozen at
0.5 in fixed arms. The task is driven input reconstruction; free-run
novelty is not a functional memory score. This experiment cannot establish
autonomous adaptive recovery, and novelty increases alone are not success.

Open-gate count uses the legacy strict threshold g > 0.5. Fixed controls
therefore report zero above-threshold gates while all eight gates remain
half open (gate sum four); zero here does not mean zero active capacity.

## Completion and blockers

| Goal | Experiment completed | Remaining limit |
|---|---|---|
| Rates, drift, approximate kernels | A1, A2, A9 | Specified stochastic models only; no finite proof of a new asymptotic law. |
| Neural state preservation | A3 | Linear recurrent model; nonlinear/deployment task validation needs a specified task and data. |
| Memory retrieval | A4 | Synthetic labeled task; retain the failed functional check(s). |
| Locomotion | A5 kinematic control | Physical stability, falls, and energy need hardware or a validated dynamic simulator/controller. |
| Sensor invariance | A6 calibration model | Real instrument/reference calibration data absent. |
| Repeated form | A7 labeled synthetic actions; A10 both supplied recordings | Real action discrimination needs class labels, independent participants, and acquisition metadata. |
| Local-time mechanism | A8 | Asymptotic avoidance and projected recurrence still require a model-specific proof. |
| Repaired recurrence score | A11 | No transferable gamma or alive/dead threshold established. |
| Learned dimensional gates | A12 | Identity-task probe is not autonomous functional recovery. |

All twelve feasible suites have recorded results. The blocked deployment
and proof claims have not been replaced by synthetic evidence.

## Reproduction and integrity

```bash
python experiments/cdt_application_campaign.py --output-dir /tmp/cdt_application_reproduction
python experiments/summarize_cdt_applications.py --input-dir /tmp/cdt_application_reproduction
```

The runner refuses to overwrite suite evidence. `manifest.json` hashes
the frozen plan and executable sources. `analysis_manifest.json` records
summary inputs and analysis code. `SHA256SUMS.txt` covers raw records and
derived files. Bootstrap intervals and sample outcomes may be regenerated
with the recorded versions and seeds.

Baseline audit: `baseline_integrity.json` separately records that all old
evidence bytes match the original repository commit. Two old summary-file
checksums correspond to CRLF while their committed files use LF. This
pre-existing discrepancy is disclosed; no old file or checksum is edited.
