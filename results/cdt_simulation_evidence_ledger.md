# CDT registered simulation evidence ledger

**Run date:** 2026-09-05  
**Primary preregistration:** `experiments/cdt_simulation_preregistration.md`  
**Follow-up preregistration:** `experiments/cdt_followup_preregistration.md`  
**Master seed:** `20260905`

## Bottom line

The mathematically corrected Configuration-Drift Theorem survived every
identifiable exact-model control. The experiments also broadened its useful
mechanism class: neither high dimension nor self-repulsion is necessary. A
two-dimensional walk with drift hidden from a one-dimensional projection gives
a clean causal split.

The simulations do **not** prove the theorem's assumptions for the
self-repelling walk. They show a strong finite-horizon mechanism pattern, but
rare full-state returns make the required asymptotic transience claim
unresolved. Historical recurrence and anchored recurrence must remain separate.

## Registered verdicts

| Suite | Result | Verdict | Consequence |
|---|---|---|---|
| S1 product/projection | 18/21 fitted slopes met the registered tolerance; the remaining 3 were event-floor failures in dimensions 5-6 | supported where identifiable; no contradiction | keep `d_s(projection)<=2<d_s(full)` as a sufficient heat-kernel corollary |
| S2 D=4 drift | hidden projected ratios remained near neutral at the primary horizon; visible drift suppressed projection | projection law supported, full mechanism floor-limited | D=4 cannot establish drift-caused transience because neutral D=4 is already transient |
| S3 self-repulsion | 5 registered beneficial cells; no over-repulsive cell through `gamma=2` | historical mechanism support only | do not cite these labels as Theorem 1 evidence |
| S4 historical recurrence | anchored tail returns vanished at high `D`, while lag-8 revisits and exact two-step backtracks persisted | strong measurement-separation control | anchored transience does not mean historical non-repetition |
| S5 finite tori | return rates approached `1/|E|`; novelty rates fell as occupancy approached one | supported | infinite-space CDT is invalid on finite irreducible spaces |
| S6 counterexamples | irrational rotation and iid continuous samples had unique fraction 1 but coarse return rate about 0.10; constant projection returned 1 | supported | exact/coarse separation does not identify drift; trivial projections must be rejected |
| F1 D=2 drift | hidden drift killed full returns but preserved projected slopes; visible drift killed both | model-level causal support | hidden-coordinate drift is a sufficient example with `gamma=0` and no high-dimensional substrate |
| F2 strong self-repulsion | projected anchored slopes stayed positive through `gamma=10`; full anchored evidence was sparse/unstable | stronger finite-horizon support, asymptotic status unresolved | self-repulsion window is broader than expected in this model, but not a theorem |

## S1: product/projection phase map

For coordinate random walk on `Z^D`, the expected tail-Green slope is `1/2`
for a one-coordinate projection, `0` for two coordinates, and `1-m/2` for
`m>2`. All cells with `m<=3` matched their analytic slope. Representative
estimates were:

| `(D,m)` | fitted slope | 95% bootstrap CI | expected |
|---|---:|---:|---:|
| `(6,1)` | 0.510 | [0.494, 0.526] | 0.5 |
| `(6,2)` | 0.023 | [-0.018, 0.062] | 0 |
| `(6,3)` | -0.539 | [-0.721, -0.386] | -0.5 |
| `(4,4)` | -0.691 | [-1.032, 0.201] | -1 |

`(5,5)`, `(6,5)`, and `(6,6)` were not quantitatively identified. At the
largest horizon their expected returns were too rare for 8,000 paths, producing
zero tail counts. With zero affected paths among 8,000, the exact one-sided 95%
upper bound on the probability that one path returns in that tail window is
`1-0.05^(1/8000)=0.000374`; this bounds detection probability, not the mean
number of clustered returns. Even the accepted `m=4` slopes used only a handful
of tail events and should be treated as weak numerical controls. The analytic
theorem is known independently; these cells expose the limit of naive Monte
Carlo Green-slope estimation.

## S2 and F1: where drift works

The D=4 suite showed that drift outside the projection leaves the projected
law unchanged, while visible drift cuts it off after the dimensionless
crossover `Pe_H` becomes order one. It could not show that drift created full
transience because full D=4 returns were already at the event floor.

The preregistered D=2 correction removed that confound:

| arm | delta | full slope | projected slope | projected ratio at `H=8192` |
|---|---:|---:|---:|---:|
| neutral | 0 | -0.004 | 0.496 | 1.000 |
| hidden | 0.02 | -0.625 | 0.492 | 0.985 [0.946, 1.022] |
| hidden | 0.05 | -2.337 | 0.501 | 1.027 [0.986, 1.070] |
| hidden | 0.10 | -3.101 | 0.505 | 0.996 [0.963, 1.036] |
| visible | 0.02 | -0.612 | -0.115 | 0.095 [0.085, 0.105] |
| visible | 0.05 | -1.820 | -1.577 | 0 |

This is the campaign's cleanest positive result. CDT separation can be caused
by drift in a hidden coordinate even in full dimension two, with no
self-repulsion. The location of drift relative to the registered projection,
not merely nonzero drift, is decisive.

## S3 and F2: where self-repulsion works, and where proof stops

The registered historical-recurrence rule labeled these cells beneficial:

- `D=2`: `gamma=0.5,1,2`;
- `D=3`: `gamma=1,2`.

No D=1 cell can separate full and projected recurrence because the projection
is the full state. `D=3, gamma=0.5` strongly reduced full historical recurrence
but missed the preregistered 25% discovery-gain threshold, so it correctly
remained unlabelled.

The follow-up extended `gamma` to 10 and switched the primary diagnostic to
anchored projection. Every projected tail slope was positive, between 0.403 and
0.572, with every 95% interval above zero. At the strongest tested setting:

| setting | full historical | projected historical | discovery | projected anchored slope |
|---|---:|---:|---:|---:|
| `D=2, gamma=10` | 0.0877 | 0.9384 | 0.8969 | 0.541 [0.419, 0.660] |
| `D=3, gamma=10` | 0.00021 | 0.9554 | 0.99962 | 0.572 [0.463, 0.691] |

This is stronger than the preregistered expectation: no over-repulsive
projection window appeared. But full anchored tail counts were often zero and
their fitted slopes were unstable. Therefore the allowed conclusion is:

> Destination-local-time repulsion robustly separates finite-horizon full
> historical recurrence from both historical and anchored recurrence of a
> one-coordinate projection, through `gamma=10` in the tested model.

It is **not** yet permissible to claim almost-sure full-state transience for
that self-interacting process. A proof would need a summable conditional return
bound or another model-specific recurrence theorem.

## S4: anchored and historical recurrence diverge operationally

At `T=4096`, the D=4--6 anchored tail count was zero, but the lag-8 historical
revisit rates were 0.0436, 0.0159, and 0.0070. Two-step backtrack rates matched
their exact values `1/(2D)` to within Monte Carlo error in every dimension.

The result closes a common misuse: fixed-origin transience does not imply that
a trajectory stops repeating old configurations. The answer depends on the
anchor, exclusion lag, and normalization.

## S5: finite capacity is a separate regime

After eight steps per state, occupancy was 0.963--0.997 and the new-state rate
had fallen to 0.012--0.039. Anchored return rates were close to the stationary
uniform mass `1/|E|` (ratios 0.953--1.031 across the four tori).

Finite irreducible systems ultimately recur in every dimension while novelty
exhausts. Use cover time, mixing, occupancy, and viability metrics; do not apply
the infinite-space spectral cutoff.

## S6: separation does not identify its mechanism

- Irrational rotation: exact unique fraction `1.0`, coarse return `0.09999`.
- Iid unit-torus sampling: exact unique fraction `1.0`, coarse return `0.10339`.
- Constant projection: coarse return `1.0`, but declared non-informative.

These are successful exact/coarse separations without realization-dependent
drift or self-repulsion. CDT is a recurrence-separation theorem, not a unique
causal signature. A useful application must independently justify that its
projection preserves function or meaning.

## Corrections forced by this campaign

1. Treat the D=4 drift full-state result as floor-limited, not causal evidence.
2. State drift relative to the projection: hidden drift can create CDT;
   projected drift can destroy structural recurrence.
3. Keep historical labels out of anchored theorem claims.
4. Mark zero-event high-dimensional slope estimates unidentifiable rather than
   successful confirmations.
5. Expand the tested self-repulsion window to `gamma<=10` for this discrete
   model, while retaining `simulation support` rather than `theorem` status.
6. Require projection informativeness and a separate functional metric; a
   constant projection passes recurrence vacuously.
7. Treat isolated nominal 95% misses among many secondary cells as
   multiplicity-sensitive; primary registered contrasts and analytic controls
   take precedence.
8. Condition projected recurrence on the full initial state unless the
   projection is proved Markov/lumpable; a feature map alone does not create a
   quotient transition kernel.

## Reproduction

```powershell
python -m unittest -v test_cdt_simulation_campaign.py test_cdt_empirical_audit.py test_cdt_registered_results.py
python experiments\cdt_simulation_campaign.py --output-dir results
python experiments\cdt_followups.py --output-dir results
python experiments\plot_cdt_results.py
```

Evidence artifacts:

- `cdt_simulation_campaign.json`: readable primary summaries and intervals;
- `cdt_simulation_campaign_raw.json`: primary path-level outcomes;
- `cdt_followups.json`: readable follow-up summaries and intervals;
- `cdt_followups_raw.json`: follow-up path-level outcomes;
- `cdt_simulation_summary.png`: compact visual audit.
- `SHA256SUMS.txt`: integrity hashes for preregistrations, executable harnesses,
  and JSON evidence.

The smoke directories are implementation checks only and are not evidence.
