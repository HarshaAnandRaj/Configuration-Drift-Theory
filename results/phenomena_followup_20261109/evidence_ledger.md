# Remaining-phenomena follow-up results

The follow-up plan was committed before execution as `02f1b003`.
The Monte Carlo last visits below are censored observations, not the
true last-exit distribution or estimates of an infinite mean.

| Dimension | Horizon | Mean last observed visit | Late-affected paths / 8192 |
|---|---:|---:|---:|
| 3 | 256 | 3.9579 | 55 / 8192 |
| 3 | 1024 | 7.9235 | 30 / 8192 |
| 3 | 4096 | 15.9536 | 15 / 8192 |
| 4 | 256 | 0.4650 | 3 / 8192 |
| 4 | 1024 | 0.6084 | 0 / 8192 |
| 4 | 4096 | 0.6084 | 0 / 8192 |
| 5 | 256 | 0.1063 | 1 / 8192 |
| 5 | 1024 | 0.1063 | 0 / 8192 |
| 5 | 4096 | 0.1063 | 0 / 8192 |

High-dimensional tails hit event floors. A missing late event cannot
establish saturation of the mean or decide recurrence.

| Dimension | Partial weighted Green sum at 256 | At 4096 | At 65536 |
|---|---:|---:|---:|
| 3 | 5.33978 | 22.56963 | 91.52846 |
| 4 | 0.55176 | 0.83231 | 1.11321 |
| 5 | 0.10544 | 0.11079 | 0.11213 |

These deterministic partial sums use the analytic return formula.
The asymptotic series test, not finite numerical growth, proves infinite
mean last exit for dimensions three/four and finite mean for dimension five.

| Behavior | Representation | Unique states | Anchored visits after t=0 | Historical lag-2 fraction |
|---|---|---:|---:|---:|
| constant | raw | 1 | 256 | 1.0 |
| constant | clock_augmented | 257 | 0 | 0.0 |
| constant | projected_without_clock | 1 | 256 | 1.0 |
| period_two | raw | 2 | 128 | 1.0 |
| period_two | clock_augmented | 257 | 0 | 0.0 |
| period_two | projected_without_clock | 2 | 128 | 1.0 |

Appending a clock manufactures novelty in both behaviors. Discarding it
restores the original recurrence measurements. Neither behavior nor task
performance improved. This is an explicit negative control for interpreting
augmented-state transience as a mechanism.
