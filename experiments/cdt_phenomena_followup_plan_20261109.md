# Remaining-phenomena follow-up: frozen before execution

The twelve-suite application campaign is complete. This separate follow-up
covers two phenomena defined in the application guide but not explicitly
measured by that campaign: long fine-return tails and bookkeeping novelty.
It does not change any completed campaign threshold or inference family.

- **P1 long return tails:** independent-coordinate lazy walks on Z^D for
  D=3,4,5; 16 independent seeds, 512 paths/seed, 4,096 steps. Use seeds
  `20391110 + D*1000 + replicate`. Retain last *observed* origin visits at
  horizons 256,1024,4096, counts of origin returns after the half-window,
  and late-affected paths. A finite run censors the true last return. Rare
  high-dimensional events are estimator floors, not evidence of saturation.
  Independently calculate the analytic partial weighted Green sum
  `sum_{n=1}^N n*(binom(2n,n)/4^n)^D` at N=256,1024,4096,16384,65536.
  This is a partial sum proportional to the true mean last exit in the
  infinite limit, not a finite-simulation estimate of that mean. The known
  asymptotic tail predicts divergence for D=3,4 and convergence for D=5;
  the proof remains analytic. Report all dimensions without a fitted
  recurrence verdict or significance test.
- **P2 bookkeeping:** constant and period-two scalar paths, 256 time steps.
  Compare raw paths to those paths augmented by the step counter. Count
  unique states, anchored visits excluding time zero, and exact historical
  revisits with lag two. A predeclared projection discards the counter.
  Demonstrate that clock augmentation changes the recurrence metric without
  changing the underlying behavior. This is a deterministic negative control.

Record the plan and executable hashes, versions, seeds, raw per-path last
observed visits, aggregate records, and a short evidence note. No new causal
claim or functional benefit is predicted. No new real-world data is acquired.
