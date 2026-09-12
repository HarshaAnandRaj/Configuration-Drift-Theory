# Measurement and optimizer repair, 2026-09-12

Authorized by the user's instruction to carry out the credit/CDT/memory sequence.
The pre-edit versions of gamma_probe.py, scale_capacity.py, alive_reward_demo.py
and configuration_drift_theory.md were copied to the Zeus workspace under
runs/cdt_repair_before_20260912. All earlier exploratory output files remain intact.

Changes:
- Phase controls now multiply the original complex Fourier spectrum by common
  random phase increments. Means, per-coordinate power and the complete circular
  cross-spectrum are preserved. This does not imply every temporal revisit is
  destroyed or prove stationarity. Unknown null names raise ValueError.
- The score identifies its null version and explicitly declines calibrated wall
  authority. The inherited segment-SE interval is labelled exploratory.
- The capacity probe uses a seeded initial state of RMS 0.1, with zero available
  as an explicit control. A finite untrained trajectory is not a capacity theorem.
- The toy sparsity gradient includes sigmoid(z)*(1-sigmoid(z)); Adam increments
  its time index once per joint update rather than once per parameter array.

Old positive phase scores and numeric novelty-reward scaling prescriptions must
not be treated as repaired results. See the new invariant/gradient tests and
phase-calibration report before using this instrument. The authoritative theorem
file and old numerical reports are unchanged.

Adaptive dimensionality must ultimately be selected and controlled by the learner
and restore independently measured function without an external rescue mechanism.
Variance expansion under an externally applied gain is only a mechanism probe.
