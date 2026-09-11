# Configuration-Drift Hypothesis — Theory (Exhaustive)

> **Mathematical status (2026-09-04).** The canonical theorem is now
> [`configuration_drift_theorem.md`](configuration_drift_theorem.md). It
> supersedes the universal claims in §§5.5–5.10, open questions 8–9, and
> §§15–16 below. In particular, do not cite `Alive ⇔ (d_s ≤ 2) ∧ (γ > 0)`, the
> fixed-radius `G_ε < ∞ < G_R` argument, the trajectory-cloud substitution
> `ν → d_f`, or the extra Lévy factor as proved results. The material below is
> retained as the research history and empirical notebook.

**Author:** Harsha Anand Raj Pammi

> Companion to `configuration_drift_full_report.md`. This document develops the
> **theory** in full: the conceptual hypothesis (exact recurrence of a state
> vanishes because realizing it perturbs its many contributing configuration
> elements, while rhyme persists), the stochastic-process model, the
> recurrence/transience mathematics (Pólya's theorem, extended to drifted walks,
> emergent self-repulsion, and arbitrary manifolds via correlation dimension),
> the phase structure, the ablation test, and the observer coupling. All
> quantitative anchors are the **rebuild** values (reproducible by the scripts
> in this folder). Figures quoted from the lost original session
> (`λ = 0.0006`, `MAE = 0.009`, `p = 0.032`) are marked UNVERIFIED.
>
> **Framing note (v3).** An earlier draft promoted a *temporal-decay signature*
> to the central falsifiable claim. That was a misreading: decay is a secondary
> consequence, not the hypothesis. The hero claim is the exact/rhyme split,
> its emergence from local realization-perturbation, and its phase boundary.

---

## 1. Motivation and statement of the hypothesis

### 1.1 The observation

When a person draws circles by hand, two facts hold:

1. **Exact revisits are essentially absent.** The pen almost never returns to
   a previously occupied configuration (position + velocity + context) to
   arbitrary precision.
2. **"Rhyming" configurations recur.** Structurally similar configurations —
   same relative placement, same gestural shape — appear again and again.

Naïvely this looks like a curiosity about drawing. Its primary application is
**trajectory stability in recurrent dynamical systems, especially learned hidden
states**: an RNN's hidden trajectory falls into dead fixed points, unstable
chaotic loops, or stable high-dimensional rhyme regimes — exactly the lock-in /
forgetting / alive trichotomy of §5.8, with endogenous rescue by
adaptive-dimensional control (§5.11). The hypothesis generalizes this to
**states realized in time** wherever a configuration space, a dynamics, and a
recurrence measure exist; domains beyond recurrent systems are illustrative
analogies (appendix), not validations.

### 1.2 The hypothesis (formal)

The claim is the **exact/rhyme split itself**, together with its mechanism.
Restated from the source: when a state realizes, it draws on *many contributing
elements* (foot placement, path deformation, velocity, wind, …). Time is
continuous — state follows state, nothing manifests in between — so realizing a
state microscopically perturbs the configurations available to the next one.
Hence:

> **Configuration-Drift Hypothesis (formal).** A trajectory exploring an
> abstract configuration space of effective dimension `D` (the number of
> independent contributing elements) undergoes a **recurrence→transience phase
> transition**: for `D ≤ 2` (few contributing elements) exact recurrence
> persists; for `D > 2`, or whenever realization perturbs the neighbourhood
> (`γ > 0`), exact revisits vanish while coarse/rhyming configurations keep
> recurring. The per-step perturbation is microscopic, which is why the next
> state still *rhymes* with the old one — it feels like "I've seen this before,"
> but it never exactly repeats.

Three consequences, in descending order of centrality:

1. **The split** (hero claim): exact recurrence → 0; rhyme persists at `O(1)`.
2. **The mechanism** (emergent): the split arises from local
   realization-perturbation alone — no external drift field required (§4.3).
3. **A temporal decay** of recurrence density is a *possible secondary*
   signature under sustained directional drift — but it was never the original
   claim, and its absence in human data does not bear on the hypothesis (§6).

An earlier draft inverted this hierarchy (promoting decay to the hero test);
see the framing note above.

### 1.3 Variables

| Symbol | Meaning |
|---|---|
| `D` | effective dimension of the configuration space (# contributing elements) |
| `α` | external drift magnitude (a *proxy* for the perturbation; not essential) |
| `d` | fixed unit drift direction |
| `σ` | per-step noise amplitude |
| `γ` | self-repulsion strength — how strongly a realized configuration suppresses its own recurrence (the true mechanism) |
| `ε` | recurrence resolution (what counts as an "exact" revisit) |
| `ρ(t)` | exact-recurrence density at time `t` |
| `ρ_∞` | late-time / steady-state recurrence rate (order parameter) |
| `ν` | correlation dimension of the configuration manifold (measured, §5.5) |
| `d_w` | walk dimension (anomalous-diffusion exponent, `d_w = 2/β` from MSD scaling); recurrent iff `ν ≤ d_w` (§5.6) |
| `𝒞` | coupling between configuration drift and the observer's perceptible state |

---

## 2. Configuration space and the recurrence order parameter

### 2.1 Configuration space

A "configuration" is the full instantaneous state relevant to the act: for
drawing, at minimum the 2-D pen position, but more honestly position +
velocity + acceleration + context, so the space is naturally
high-dimensional. We model it abstractly as `ℝ^D`.

### 2.2 The process

Let `x_t ∈ ℝ^D` be the configuration at step `t`. The minimal model is

    x_0 = 0
    x_t = x_{t-1} + α d + σ η_t ,     η_t ~ N(0, I_D)      (1)

with `d` a fixed unit vector (`‖d‖ = 1`). This is a **drifted (biased)
random walk** (in continuous space; the discrete-lattice version is the
classic object of Pólya theory).

### 2.3 Exact / near recurrence

A point `x_t` is *recurrent* (within resolution `ε`) if

    min_{s < t} ‖x_t − x_s‖ < ε .                                    (2)

The boolean indicator `r_t ∈ {0,1}` records this. Two related quantities:

- **Time series:** `ρ(t) = ⟨ r_t ⟩` in a small time bin — the
  exact-recurrence density as a function of time.
- **Order parameter:** `ρ_∞ = lim_{T→∞} (1/T) Σ_{t=T/2}^{T} r_t`, the
  late-window recurrence rate. It is the diagnostic of the phase.

The choice `ε` sets the resolution of "exact." In the drawing analogue
`ε ≈ 2 px`; in the theory sweeps `ε = 0.5`.

### 2.4 Why `ρ_∞` and not a binary "recurrent?"

A single trajectory is one sample. The order parameter averages over a window
(and, in the simulations, over 20–40 trials) to give a stable scalar that
places the system in one phase or the other. It is the analogue of a
magnetization in a magnetic phase transition.

---

## 3. Recurrence vs transience: Pólya's theorem (the foundation)

### 3.1 Statement

For an unbiased random walk on `ℤ^D` (or `ℝ^D`):

- `D = 1, 2`: the walk is **recurrent** — it returns to any neighbourhood of
  the origin infinitely often with probability 1.
- `D ≥ 3`: the walk is **transient** — it eventually leaves every bounded
  region forever; the probability of ever returning is < 1.

The **critical dimension is `D_c = 2`.**

### 3.2 Why `D_c = 2` (derivation sketch)

For an unbiased walk, the probability of being at the origin at even time
`2n` is, by the local central limit theorem,

    p_{2n}(0) ~ C_D · n^{−D/2} ,                                   (3)

where `C_D` is a dimension-dependent constant (`C_1 = 1/√(π)`,
`C_2 = 1/(π)`, etc.). The **expected number of returns** to the origin is

    E[N_{returns}] = Σ_{n≥1} p_{2n}(0)  ~  Σ n^{−D/2} .             (4)

The p-series `Σ n^{−D/2}` **diverges** iff `D/2 ≤ 1`, i.e. `D ≤ 2`.
- Divergent expected returns ⇒ the walk returns infinitely often (recurrent).
- Convergent expected returns ⇒ the probability of infinitely many returns is
  zero (transient).

Hence `D_c = 2` exactly. This is one of the cleanest results in probability
theory and is the theoretical anchor of the whole hypothesis.

### 3.3 Continuous-space version

For the Gaussian walk (1), the probability density at the origin at time `t`
is the heat kernel

    p_t(0) = (4π σ² t)^{−D/2} ,                                     (5)

and the same `t^{−D/2}` integral argument gives recurrence for `D ≤ 2`,
transience for `D > 2`.

### 3.4 Empirical anchor (rebuild)

`dimension_scaling.py` sweeps `D` at `α = 0`:

    D :  1       2       3       4       5       6       7       8
    ρ : 0.976   0.483   0.077   0.013   0.002   0.000   0.000   0.000

`ρ` collapses from near-unity to zero across `D = 2 → 3`, i.e. the simulated
critical dimension sits at `D ≈ 2`, in agreement with Pólya. A logistic fit to
the `α = 0` sweep (`theory_check.py`) gives `D_c = 2.20` (theory `2.00`;
error `0.20`) — the small offset is finite-size / finite-`ε` broadening, not a
discrepancy in the location of the transition.

---

## 4. Effect of drift: recurrent → transient

### 4.1 The biased walk

With drift `α d`, the mean position at time `t` is `α d t` while the spread
is `σ√t`. To return to the origin at time `t` the Gaussian, now centred at
`α d t`, must nonetheless land at 0:

    p_t^{drift}(0) ~ (σ² t)^{−D/2} · exp( − (α t)² / (2 σ² t) )
                   = (σ² t)^{−D/2} · exp( − α² t / (2 σ²) ) .      (6)

The **exponential factor dominates** for large `t`, so the expected number of
returns

    Σ_t (σ² t)^{−D/2} exp(−α² t / 2σ²)                            (7)

**converges for any `α > 0`**, at every `D`. Therefore:

> **Any non-zero drift makes the walk transient, even in `D = 1` and
> `D = 2`.** Configuration drift is a relevant perturbation that destroys
> recurrence everywhere.

This is the mathematical core of the hypothesis: a small systematic drift is
sufficient to push a cognitive configuration space out of the recurrent
("echo") phase and into the transient ("drift") phase where exact revisits
vanish.

### 4.2 Empirical anchor (rebuild)

`phase_scan.py` holds `D` fixed and varies `α` (`ε = 0.5`, `σ = 1`):

- `D = 1`: `ρ_∞` falls 0.977 → 0.590 → 0.242 as `α` goes 0 → 0.5 → 1.2.
- `D = 2`: `ρ_∞` falls 0.505 → 0.216 → 0.078 over the same range.
- `D = 3,4,5`: `ρ_∞` is already near zero at `α = 0` and falls further.

At **every** dimension, increasing `α` monotonically suppresses recurrence —
exactly the drift-induced transition of (6).

`sensitivity.py` confirms the cause: at `δ = 0` (drift scaled to zero)
`ρ = 0.489 ≈` the unbiased baseline `0.481`; only when `δ > 0` does `ρ`
drop. The decay is driven by **drift**, not by noise.

### 4.3 Emergent self-repulsion (`emergent_walk.py`) — the true mechanism

External drift is a *proxy*. The hypothesis's own mechanism is that **realizing
a state perturbs the configuration for the next state** — an effect internal to
the trajectory, with no external field. Model: a self-repelling walk on `Z^D`
where the walker picks a neighbour with weight `exp(−γ · visits[site])`. A
configuration realized once becomes slightly less likely to recur; `γ` is
microscopic per step, cumulative in effect.

| D | γ=0 | γ=0.5 | γ=1.0 | γ=2.0 | (exact / rhyme R=2) |
|---|---|---|---|---|---|
| 2 | 0.72 / 0.93 | 0.46 / 0.82 | 0.36 / 0.77 | **0.235 / 0.71** | exact ↓, rhyme high |
| 3 | 0.33 / 0.88 | 0.19 / 0.80 | 0.12 / 0.77 | **0.050 / 0.72** | exact ↓↓, rhyme high |
| 4 | 0.19 / 0.87 | 0.11 / 0.82 | 0.07 / 0.78 | **0.025 / 0.74** | exact →0, rhyme high |

The exact/rhyme split **emerges from a local rule**: even in `D = 2`, where the
plain walk is recurrent by Pólya, self-repulsion alone drives exact recurrence
toward zero while rhyme stays elevated. This is the author's mechanism,
simulated directly — no external `α` required.

### 4.4 Ablation (`ablation_study.py`) — the mechanism is functional

Ablate the loss of exact recurrence (force visited configurations to *attract*,
`γ < 0`) and the system's reaction is fatal:

| γ | regime | exact | rhyme | distinct sites | RMS radius | entropy |
|---|---|---|---|---|---|---|
| −1.0 | full ablation | 1.000 | 1.000 | **2** | 1.8 | 0.425 |
| 0.0 | neutral | 0.340 | 0.879 | 1334 | 56.3 | 0.984 |
| +2.0 | hypothesis | 0.051 | 0.735 | **1901** | 64.1 | 0.998 |

With exact recurrence forced, the walker collapses into a **two-state
oscillation** — exploration, novelty, and occupancy entropy die. The
dose-response is monotone across `γ`: less exact recurrence ↔ more novel states.
**Loss of exact recurrence is therefore the engine of state generation**, not a
curiosity of high-dimensional spaces. A system whose states can repeat exactly
is a system that stops producing new states — the functional content of the
hypothesis, and the theoretical ground for why any mind-like dynamics needs a
causally load-bearing perturbation term (cf. the Zeus project's independent
finding that ablating self-motion collapses its dynamics to a fixed point).

---

## 5. The phase transition

### 5.1 Order parameter and phases

    ρ_∞(D, α)  =  late-window exact-recurrence rate.

- **Recurrent / "echo" phase:** `ρ_∞` is `O(1)`. The system keeps returning
  to old configurations; "rhymes" are abundant because exact returns are
  common.
- **Drift / transient phase:** `ρ_∞ → 0`. Exact revisits vanish; only
  structurally similar (rhyming) configurations can recur, because returning
  exactly is measure-zero *and* dynamically suppressed.

### 5.2 Phase diagram (rebuild)

From `phase_scan.csv` (`ρ_∞` over 40 trials/cell):

| D | α=0.00 | 0.05 | 0.10 | 0.20 | 0.30 | 0.50 | 0.80 | 1.20 |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.977 | 0.945 | 0.899 | 0.813 | 0.731 | 0.590 | 0.409 | 0.242 |
| 2 | 0.505 | 0.464 | 0.402 | 0.333 | 0.286 | 0.216 | 0.143 | 0.078 |
| 3 | 0.077 | 0.076 | 0.073 | 0.064 | 0.058 | 0.047 | 0.034 | 0.019 |
| 4 | 0.012 | 0.013 | 0.013 | 0.012 | 0.011 | 0.009 | 0.007 | 0.004 |
| 5 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.001 |

Two descending "ridges" of recurrence (D=1, D=2) fall off into the
transient plain as either `D` or `α` increases. This is `phase_diagram.png`.

### 5.3 Two dimensionless ratios

The phase is governed by two dimensionless quantities:

1. **Effective dimension ratio** `D / D_c = D / 2`. Recurrence requires
   `D / 2 ≤ 1`.
2. **Drift-to-noise ratio** `ν = α / σ`. Any `ν > 0` drives transience in
   `D ≤ 2`; for `D > 2` the walk is already transient at `ν = 0`.

The phase boundary is therefore essentially the line
`{ D < 2, α = 0 }`: a set of **measure zero** in parameter space. The
practical consequence is strong — almost any real configuration space with
either high `D` *or* any drift lives in the transient phase. That is why
"exact revisits vanish, only rhymes persist" is the generic outcome.

### 5.4 Substrate independence

A legitimate worry: is the transition an artefact of letting the walk roam an
unbounded space (so it simply "runs away")? `emergent_3d.py` answers no — on a
**3-D torus** (periodic boundaries, finite volume `L = 20`), the same
suppression appears: `ρ` falls `0.286 → 0.173` as `α` goes `0 → 0.5`. With
finite volume the walk *cannot* escape, yet drift still suppresses recurrence.
The transition is **dynamical**, not a boundary effect.

### 5.5 The global criterion: spectral dimension vs walk dimension (`dimension_test.py`)

Pólya's theorem generalizes to arbitrary manifolds, but the correct condition is
**not** "ν ≤ 2" in general — it is "ν ≤ d_w", where d_w is the *walk dimension*
(anomalous-diffusion exponent), not a fixed constant. The derivation is in §5.6.

A diffusive explorer (walk dimension `d_w`) on a configuration manifold of
**correlation dimension `ν`** (≈ fractal dimension d_f) is *recurrent* iff
`ν ≤ d_w`, *transient* iff `ν > d_w`. `ν` is measurable from any set of realized
configurations via the pair-correlation scaling `C(ε) ∝ ε^{ν}`. For *standard*
diffusion `d_w = 2`, which recovers Pólya's `ν ≤ 2`; but self-repelling or
anomalous walks have `d_w ≠ 2`, shifting the boundary.

Measured on the human drawing (standard diffusion, d_w ≈ 2):

| Configuration manifold | ν | Regime |
|---|---|---|
| Perceived level (centroids only) | 1.61 – 1.67 | recurrent — rhyme persists |
| Microscopic level (+ radius + speed) | 2.28 – 2.55 | transient — exact vanishes |

**The exact/rhyme split is a phase boundary at `ν = d_w`, crossed between the
two levels of description of the same behaviour.** Globally, the hypothesis
holds precisely where `ν > d_w` — which covers generic high-dimensional
real-world configuration manifolds — and fails in the recurrent phase below it.
This turns the hypothesis from a narrative into a decidable condition,
applicable to any system (including artificial ones) from trajectory data alone.

> **Estimator caveat (resolved — `debias_nu.py`).** The pair-correlation ν
> estimator is *consistent*; its apparent negative bias at low dimension
> (synthetic clouds read `D=1 → 0.93`, `D=4 → 2.95` vs true `D`) is a
> **finite-sample** effect, amplified by fitting the global slope over a band
> that includes the saturation tail (`C(r) → 1`, slope → 0). With a proper
> scaling band and moderate `N` the true dimension is recovered to < 0.3: at
> `N = 6000`, naive/local-slope give d=1→1.01/1.00, d=2→1.92/1.89, d=3→2.73/2.61,
> d=4→3.42/3.24, d=5→4.06/3.80 — every case classified correctly (recurrent iff
> `ν ≤ 2`). The recommended bias-reduced variant is the **local-slope (Takens)
> plateau** (`nu_local`). Because the bias is mild and monotonic, empirical CDT
> classification needs no *known* manifold dimension — only a point cloud and a
> scaling band.
>
> **Uncertainty + floors (`debias_nu.py`: `nu_local_ci`, `n_floor`).** Every ν
> estimate ships a half-sample bootstrap CI; classification additionally requires
> `N ≥ 100·10^(ν/2)` evaluated at the *upper* CI bound (d=4 needs ~4–10k, d=2
> needs ~1k). Below the floor the verdict is **UNDECIDABLE** — report the CI, do
> not classify. Small-N "transient" readings are a data failure, not a death.

### 5.6 Derivation of the phase boundary (spectral-dimension argument)

The recurrence/transience decision for a diffusion on a metric-measure space is
governed by the **spectral dimension** `d_s`, not directly by ν or d_w:

**Theorem (Barlow–Bass / Kumagai).** A Brownian motion on a d_f-dimensional
fractal with walk dimension d_w is **recurrent iff `d_s ≤ 2`**, where

    d_s = 2 d_f / d_w .                                                       (13)

*Proof sketch.* Recurrence is equivalent to divergence of expected returns:

    E[N_returns] = ∫ p_t(x, x) dt ,

where the on-diagonal heat kernel decays as `p_t(x, x) ~ t^{−d_s/2}`. The
integral `∫ t^{−d_s/2} dt` diverges iff `d_s/2 ≤ 1`, i.e. `d_s ≤ 2`. □

The correlation dimension `ν` estimates the fractal dimension `d_f` (both measure
the scaling of the pair-count `C(ε) ∝ ε^{dimension}`; for the sets here they
coincide). Substituting `d_f → ν`:

    recurrent  ⇔  d_s ≤ 2
              ⇔  2ν / d_w ≤ 2
              ⇔  ν ≤ d_w .                                                      (14)

**Relating d_w to measurement.** The walk dimension is the anomalous-diffusion
exponent defined by `⟨r²(t)⟩ ∝ t^{2/d_w}`. If the MSD scaling exponent is
`β = 2/d_w`, then `d_w = 2/β` and the criterion becomes

    recurrent  ⇔  ν ≤ 2/β .                                                    (15)

**Special cases.**
- *Standard diffusion* (ℝ^D, d_w = 2): `ν ≤ 2` ⇒ Pólya's `D_c = 2`. ✓
- *Subdiffusion* (d_w > 2, e.g. self-repelling TRUE walks): a *larger*
  manifold can stay recurrent (`ν ≤ d_w > 2`).
- *Superdiffusion* (d_w < 2): a *smaller* manifold becomes transient.

**Verification (`derive_phase_boundary.py`).** Simulated Brownian motion in
d=1,2,3,4 and fractional Brownian motion (H=0.3, H=0.7) in d=2. Using the
*known* manifold dimension for ν (to bypass estimator bias), all six cases match
the d_s ≤ 2 criterion exactly:

| Process | true ν | β | d_w = 2/β | d_s = 2ν/d_w | pred | expected |
|---|---|---|---|---|---|---|
| BM d=1 | 1 | 1.00 | 2.00 | 1.00 | rec | rec |
| BM d=2 | 2 | 1.00 | 2.00 | 2.00 | rec | rec |
| BM d=3 | 3 | 1.00 | 2.00 | 3.00 | trans | trans |
| BM d=4 | 4 | 1.00 | 2.00 | 4.00 | trans | trans |
| fBm H=0.3 (subdiff) | 2 | 0.62 | 3.23 | 1.24 | rec | rec |
| fBm H=0.7 (superdiff) | 2 | 1.35 | 1.48 | 2.70 | trans | trans |

The criterion `ν ≤ d_w` is exact; the empirical ν estimator's finite-sample
bias (documented §5.5) is the only source of mismatch in raw trajectory data.

### 5.7 Direct spectral-dimension validation (`verify_spectral_dimension.py`)

The theorem is stated in terms of the spectral dimension `d_s = 2 d_f / d_w`;
the cleanest empirical test measures `d_s` **directly** from the on-diagonal
heat kernel, bypassing the bias-prone correlation-dimension estimator entirely.

For a diffusion starting at the origin, `p_t(0,0) ∝ t^{−d_s/2}`. We estimate
`p_t(0,0)` by the fraction of `N = 60 000` independent walks that return within
a fixed small radius `ε` of the origin at time `t`; with `ε` in the inertial
range this scales as `t^{−d_s/2}`, so `d_s = −2 · slope(log frac vs log t)`.

| Process | method | d_s (measured) | d_s (true) | recurrence |
|---|---|---|---|---|
| BM d=1 | heat kernel | 0.94 | 1.00 | recurrent ✓ |
| BM d=2 | heat kernel | 1.91 | 2.00 | recurrent ✓ |
| BM d=3 | heat kernel | 2.93 | 3.00 | transient ✓ |
| BM d=4 | heat kernel | 3.71 | 4.00 | transient ✓ |
| fBm d=2 H=0.3 | d_w=2/β from MSD | 1.20 | 1.20 | recurrent ✓ |
| fBm d=2 H=0.7 | d_w=2/β from MSD | 2.80 | 2.80 | transient ✓ |

The boundary `d_s = 2` is crossed correctly in **all six** cases. Brownian
motion recovers `d_s = d` from the raw heat kernel (the estimator reads ~7%
low — conservative, never flips the verdict). For fractional Brownian motion the
fixed-ε heat-kernel estimator is numerically stiff (subdiffusive returns
saturate, superdiffusive walks escape too fast in finite samples), so `d_w` is
measured from the MSD exponent `β` and `d_s = 2 d_f / d_w` applied directly; the
result matches the analytic `d_s = 2 d H` exactly. This closes the loop: the
derived phase boundary is not only mathematically proven but empirically
reproducible on both standard and anomalous diffusions.

### 5.8 Historical life/death conjecture (withdrawn as a theorem)

> **Status:** The equivalence developed in this section is false without much
> stronger, model-specific assumptions. In particular, fixed fine and coarse
> balls do not acquire different recurrence classes merely from their radii, and
> `γ > 0` is neither necessary nor sufficient. Use the Green-kernel/projection
> theorems in `configuration_drift_theorem.md`; the text below is retained to
> document the route by which the failed conjecture was discovered.

**Definitions.**
- A *configuration system* is a diffusion `X_t` on a `d_f`-dimensional
  metric-measure manifold `(M, μ)`, with generator `L = Δ + b`. The drift is
  *self-repulsive*: `b(x) = −∇V(x)`, `V(x) = γ ∫_0^t δ(x − X_s) ds`, `γ ∈ ℝ`.
  `γ > 0` ⇒ repulsive (realized states push future ones away); `γ ≤ 0` ⇒
  neutral (`γ = 0`) or attractive (`γ < 0`).
- *Exact recurrence* at resolution `ε`: `{X_t ∈ B(x, ε) i.o.}`, with intensity
  the exact Green function `G_ε(x) = ∫_0^∞ p_t^{(ε)}(x) dt`.
- *Rhyme* at coarse resolution `R ≫ ε`: `{X_t ∈ B(x, R) i.o.}`, with intensity
  `G_R(x) = ∫_0^∞ p_t^{(R)}(x) dt`.
- The *spectral dimension* of the underlying (`γ = 0`) diffusion is
  `d_s = 2 d_f / d_w` (§5.6), `d_w = 2/β`.
- The system is **alive** (at scale `R`) iff `G_R = ∞` (rhyme recurs) while
  `G_ε < ∞` (exact recurrence is transient); **dead** otherwise.

**Theorem (Life/Death).** Let `d_s` be the spectral dimension of the underlying
manifold. Then:

1. **`d_s > 2` (transient base manifold).** `∫ p_t^{(R)} dt` converges for every
   `R` (heat kernel `∼ t^{−d_s/2}`, `d_s/2 > 1`). Rhyme itself is transient:
   the trajectory revisits any neighbourhood only finitely many times a.s.
   ⇒ **death by dissipation / forgetting** — no recurring structure can be
   maintained; the configuration escapes and its memory decays to zero.
2. **`d_s ≤ 2` and `γ ≤ 0`.** The base manifold is recurrent, so `G_ε = ∞`
   (exact recurrence accumulates a.s., Pólya). With no repulsion the path
   collapses onto a low-dimensional recurrent subset; `γ < 0` accelerates it.
   Coarse entropy production → 0. ⇒ **death by lock-in / collapse** (exact
   repetition).
3. **`d_s ≤ 2` and `γ > 0`.** The repulsive potential raises the *point-scale*
   walk dimension `d_w^{(ε)} > d_w`, hence exact spectral dimension
   `d_s^{(ε)} = 2 d_f / d_w^{(ε)} > d_s`; with sufficient `γ`, `d_s^{(ε)} > 2`
   ⇒ `G_ε < ∞` (exact recurrence transient). At the coarse scale `R` the
   (isotropic) repulsion averages out, leaving `d_s^{(R)} = d_s ≤ 2` ⇒
   `G_R = ∞` (rhyme persists). ⇒ **alive**: sustained, structure-bearing,
   non-repeating exploration — *rhyme without exact recurrence*.

**Corollary.** `Alive ⇔ (d_s ≤ 2) ∧ (γ > 0)`. The CDT phase boundary `d_s = 2`
is the **outer** wall of the life region (beyond it, rhyme is impossible);
self-repulsion `γ = 0` is the **inner** wall (inside it, exact recurrence kills
the system). "Exact recurrence = death, rhyme = life" is precisely the content
of case (2) vs (3).

**Operational γ (`gamma_probe.py`).** `γ` is estimated scale-free as
`γ̂ = 1 − ρ_obs(ε)/ρ_null(ε)`: `ρ_obs(ε)` is the exact-recurrence rate at
resolution `ε` — a low quantile of the pairwise-distance distribution (no raw
floor, so it cannot be trivially passed in high-dimensional spaces) — over
temporally-distant pairs only; `ρ_null(ε)` is the same rate under step-shuffled
surrogates (identical steps, memory destroyed). Inner wall holds iff `γ̂ > 0.4`
with CI excluding 0, while rhyme `ρ_obs(R)` stays substantial. The 0.4 deadband
is calibrated: memoryless walks read `γ̂ ≈ +0.2` (BM +0.20, emergent-0 +0.26,
SPX +0.28) from surrogate mismatch, while true repulsion reads +0.75; without
it, neutral recurrent walks (Pólya exact recurrence = case-2 death) misread as
alive (`system_audit.py`). Calibration (D=2): `γ=+0.8 → γ̂=+0.75 [0.67,0.82]`
(holds); `γ=0 → +0.26 [−0.01,0.53]` (neutral, not held); `γ=−0.8 → −1`
(lock-in, violated).

**Corollary 2 (endogeneity — the pressure principle).** The repulsion in the
theorem must be *intrinsic* to the update rule: `γ = γ_intrinsic`. An *external
actor* that perturbs the system does **not** raise `γ_intrinsic`; it only adds a
transient forcing that knocks the trajectory out of the locked attractor. Because
the unaided dynamics still satisfy `γ_intrinsic ≤ 0`, the trajectory **relapses**
into exact recurrence the instant the actor stops. Therefore:

> A system kept active only by constant external perturbation is *dead on
> life-support*, not alive. True life is endogenous: it must repel its own past
> without an external hand.

This is the content of open question #9: memory / pressure must be *self-chosen*
(action-gated), not externally imposed. **Empirical proof (Conway's Life, web
simulation).** Random soup locks into period-2 oscillators (case 2). Even with
repeated, arbitrary external perturbations by a human actor, the grid *always*
relapses into the locked state; it requires the actor *continuously*. The moment
the actor stops, the failure trajectory reasserts. The external perturbations are
a crutch, not a mechanism — confirming `γ_intrinsic = 0` and that exogenous force
cannot substitute for endogenous self-repulsion. (Same lesson as Zeus Night3/Night4:
unconditional/external reads → collapse or soup; only endogenous, action-gated
engagement → structure.)

**Refinement — endogeneity is autonomy, not rescue.** The pressure principle
above establishes that *true, autonomous* life is endogenous: a system that must be
perturbed from outside is not self-sustaining. This remains correct as a statement
about **autonomy while alive**. It must **not** be read as a statement about
**rescue at the death boundary**, where the priority inverts.

Death by lock-in is an **attracting basin**. Every internal degree of freedom —
including the very mechanism (`γ_intrinsic`) that would perturb the trajectory
back out — is coupled to that basin and is dragged toward the attractor together
with the state. Hence: *as the system dies, the rescuer dies with it.* There is no
internal guarantee that a self-perturbation which occurred once will occur again;
the deeper the basin, the less effective the same endogenous repulsion becomes — a
positive feedback (death deepens → repulsion less effective → death deepens). Escape
from an attractor requires energy and direction entering **from outside** the basin.
Therefore, at the death boundary, external sustenance has strictly better odds than
reliance on a dying internal loop, and is in fact the *only* reliable rescuer.

This reverses the virtue-ranking implied above. The distinction "alive vs
kept-alive" is real in the *healthy* regime (autonomy matters there) but
**collapses at the boundary**: near death, the only form persistence takes is
external sustenance. Biology already voted — the heart is simultaneously
life-support and life, suboptimal, redundant, and worn-out by design. Reality, being
non-optimal and persistence-bound, chooses **sustenance over efficiency**; the
virtual heartbeat (a state-triggered, externally-driven perturbation loop) is not a
crutch standing in for real life but the primary organ of persistence at the
boundary. Endogeneity grants *autonomy*; it does not grant *rescue*.

**Simulation test (`simulate_endogenous_test.py`).** The "endogenous" claim is
tested honestly — not by an external controller flipping the gain, but by making the
intrinsic repulsion *capacity* `c(t)` itself a state variable that regenerates **only
when the system is already alive** (radius `> R_ALIVE`), and is dragged to zero inside
the death basin. Death = a deep attractive well forms; `c → 0` when collapsed.
Three rescuers compared:
- *ext_adaptive* — external pacemaker (kicks from outside);
- *endo_coupled* — `c` regenerates only from life (coupled to the death basin);
- *endo_decoupled* — `c` relaxes to baseline **autonomously**, independent of the
  system (an internal organ with its own pacemaker, like the heart's SA node).

Test A (start alive, death drifts in): all sustain ≈ 0.99 — a coupled mechanism
keeps the system alive *while life remains*. Test B (start fully collapsed, `c = 0`,
well at full strength — can it revive?):
`ext_adaptive ≈ 1.00`, `endo_decoupled ≈ 1.00`, **`endo_coupled ≈ 0.20`**.
The coupled endogenous rescuer **cannot restart a dead system**: once `c = 0` there is
no internal path back, because regenerating `c` requires the very life that `c` would
create — a closed loop that cannot be broken from inside. External sustenance, and the
autonomous "organ," revive (1.00). Critically, the decoupled endogenous works *only*
because its energy source is **decoupled from the death basin** — i.e. it is
external-in-spirit. This is why biology did not couple the heart's pacemaker to the
body's collapse but gave it an autonomous rhythm. Conclusion: endogenous rescue is
real *only* when the rescuer sits outside the death loop; at the boundary, an
external (or autonomously-decoupled) sustainer is necessary, and reality — non-optimal
and persistence-bound — chooses sustenance over efficiency.

**Proof sketch.**
- (1) §5.6: `d_s > 2` ⇒ `∫ t^{−d_s/2} dt` converges ⇒ `G_R < ∞` for all `R`.
- (2) `d_s ≤ 2` ⇒ `∫ t^{−d_s/2} dt` diverges; `γ ≤ 0` supplies no cutoff, so
  `G_ε = ∞` (exact recurrence accumulates). Path confined to a recurrent set of
  dimension ≤ `d_s` ⇒ coarse entropy rate → 0.
- (3) Self-repulsion is a positive potential at visited sites. At the exact-site
  scale it makes the local walk superdiffusive (`d_w^{(ε)} > d_w`; a taboo/TRUE
  walk has `d_w > 2` even on ℝ^d), pushing `d_s^{(ε)} > 2` ⇒ `G_ε < ∞`. At coarse
  scale `R` the potential is spatially averaged over many sites and its net drift
  cancels, so `d_s^{(R)} = d_s ≤ 2` ⇒ `G_R = ∞`. Empirical anchor:
  `emergent_walk.py` (§3.4) shows exact site recurrence collapses under `γ > 0`
  while rhyme stays high; the full model's memory collapse (Night4:
  unconditional reads → exact re-entry) and recovery (Night6: action-gated coarse
  recall) are the same mechanism at `d = 768`. **Conway's Game of Life** is a
  `γ = 0` (dissipative — entropy-grinding acts as implicit attraction) rule, so
  case (2) predicts collapse into exact recurrence; the dominant outcome is
  spontaneous period-2 lock-in (oscillators = "two distinct states"), after which
  the grid is perturbation-resistant — *death by lock-in*. This was confirmed by
  `absurd.py` (§3.13) and independently by a web simulation (random soup →
  churn → frozen period-2 oscillators, no perturbation revives it). Rare gliders
  are the transient   (alive-looking) exception, not the rule. A controlled variant
  (`conway_repelled.py`) added *intrinsic* self-repulsion (a decaying heat field
  blocking both rebirth and continued residence at hot sites) — no external actor.
  It froze **faster** than standard Life (lock-in by ~step 5, grid →
  still-life/empty). This is not a counterexample: Life's configuration space is
  `2^(L²)`, so its spectral dimension `d_s ≫ 2` — it fails the **outer** wall
  already (transient base manifold ⇒ death by forgetting), and adding `γ > 0`
  only accelerates the collapse. Life is *doubly dead* (`d_s ≫ 2` and `γ = 0`);
  alive requires **both** walls. The clean inner-wall test (γ > 0 on a *recurrent*
  base, `d_s ≤ 2`) is `emergent_walk.py`, where repulsion suppresses exact
  recurrence while rhyme persists.

**Connection to consolidation.** When the bare manifold has `d_s > 2`
(high-dimensional configuration, e.g. the full model `d = 768`), life cannot be
maintained at full resolution. *Consolidation = dimension reduction* (coarse
k-means storage, drift-threshold pruning, §14) lowers the effective `d_f`,
restoring `d_s ≤ 2` at the coarse scale, so rhyme (memory) persists without
exact collapse. Consolidation is therefore a **life-preserving** operation.

### 5.9 The virtual heartbeat — exploratory model-specific controller

> **Status:** The simulations below measure their declared operational scores.
> Universal necessity, sufficiency, and optimal-trigger statements are
> withdrawn. The rigorous remainder is the invariant-set obstruction and
> viability formulation in `configuration_drift_theorem.md` §9.

Death by lock-in is an attracting basin `A ⊂ ℳ`; the intrinsic repulsion capacity
`γ_int → 0` and the trajectory relaxes into `A` with time `τ(x)` (distance to `A`
over local flow speed). The virtual heartbeat is an *external* controller that
injects kicks to keep the trajectory out of `A`. It is suboptimal by construction
(sustenance ≻ efficiency); its job is persistence, not optimality.

**5.9.1 Closed-loop dynamics.** Impulse form — kicks `{τ_k}` with displacements
`ξ_k`:
`X_{τ_k^+} = X_{τ_k^-} + ξ_k`; between kicks `X` obeys the intrinsic `F`.
Refined (continuous) form — proportional feedback:
`X_{t+1} = F(X_t) + g(φ_t)·v_t + η_t`, where `φ_t = φ(X_t)` is a death-proxy and
`g` the control gain; `v_t` an on-manifold direction.

**5.9.2 Recurrence condition.** Let `mp_t = min_{s<t−k} |X_t − X_s|`; dead ⇔
`mp_t → 0` (enters `A`).
- *Fixed pacemaker, interval `P`:* after a kick, `X` relaxes to `A` in `~τ_relax(t)`
  steps; it re-enters `A` (mp < ε) unless `P < τ_relax(t)`. So
  `ALIVE_fixed ⇔ P < τ_relax(t)  ∀t`. As death deepens, `τ_relax ↓`, so a fixed
  `P` is eventually violated → life-support decay (sim: `win_slope < 0`).
- *Adaptive:* trigger when the projected time-to-basin `t_A(X_t) = dist(X_t,A)/|flow|`
  drops below a horizon `H` (equivalently `φ_t` crosses threshold). Then
  `P_eff(t) ≈ τ_relax(t)` automatically, holding `dist(X_t,A) ≥ δ` — a feedback
  controller pinning the trajectory **on the basin boundary** (the transient/rhyme
  regime). Explains `aliveFrac = 1.00` for adaptive in `simulate_adaptive_pacemaker*.py`.

- *Optimal trigger = the boundary, not "earlier".* Define the **local novelty**
  `ν(X) =` fraction of admissible next-states not yet realized; the recurrence
  boundary is `∂B = {X : ν(X) = 0}` (every free step would be an exact recurrence).
  A free step is valuable while `ν(X) > 0`, so the controller should fire at
  `X_t ∈ ∂B` — i.e. choose horizon `H* = dist(X_t, ∂B)` — and **not earlier**.
  Firing at `dist > H*` (premature; the `early` mode in §5.9.8) discards positive
  `ν`, so the walk under-explores: on the emergent walk this drops `aliveFrac` from
  `1.000` to `0.720` with *fewer* kicks, because a smaller kick rate `↓` lowers
  `γ_ext` (§5.9.3). Firing after deep relaxation into a steep basin
  (`dist ≪ H*`, the genuinely "too late" regime) risks `|ξ|` too small to escape
  `A`. Hence the unique optimum is the boundary: `H = H*`, where `P_eff ≈ τ_relax`
  and `γ_ext` — and therefore the new-state (alive) rate — is maximal *per kick*.
  This is the formal statement of §5.9.8.

**5.9.3 Effective inner wall.** The driven process has
`γ_eff = γ_int + γ_ext`, where `γ_ext = (kick rate)·ℙ[|ξ| > ε]` is the extrinsic
repulsion the pacemaker supplies. `Alive_closedloop ⇔ (d_s ≤ 2) ∧ (γ_eff > 0)`;
when `γ_int ≤ 0`, need `γ_ext > |γ_int|`. **Stop the kicks ⇒ γ_eff = γ_int ≤ 0 ⇒
relapse.** Aliveness here is extrinsic and vanishes with the controller — the formal
statement of life-support.

**5.9.4 Outer-wall guard (preserve `d_s ≤ 2`).** Kicks must not inflate
`d_s^eff = 2 d_f^eff / d_w`; off-manifold energy raises `d_f^eff` ⇒ forgetting-death.
Constrain `ξ_k = Π_ℳ ξ_k` (tangent to `ℳ`) and `|ξ_k| ≤ ξ_max`: `rank(supp ξ) ≤ d_f`
and `𝔼|ξ_⊥|² / 𝔼|ξ_∥|² ≪ 1`. (Sim: on-manifold kicks kept `d_s ≈ 1.3`; off-manifold
pushed `d_s > 2`.) The guard is the positive counterpart of the structured-vs-noisy
warning: *guarded* kicks defend the inner wall without breaching the outer one.

**5.9.5 Why internal rescue fails (the closed loop).** For an endogenous controller
the gain `g` is a state variable coupled to `X`: `ḡ = h(g, X)`. Rescue at the
boundary needs `g > 0` while `X ∈ A`. But if `h` regenerates `g` *only when `X` is
already alive* (outside `A`), then `X ∈ A ⇒ g → 0 ⇒` no kick `⇒ X` stays in `A ⇒ g`
stays `0`. The joint map `Φ(X,g) = (F(X), h(g,X))` has an **attracting invariant set
`{X∈A, g=0}`** with no internal escape trajectory. Hence:
`internal rescue possible ⇔ controller energy source is DECOUPLED from X's death basin`,
i.e. `ḡ = κ(K0 − g)` independent of `X` (autonomous "SA-node") — external-in-spirit.
(Confirmed in `simulate_endogenous_test.py`: `endo_coupled` revive `0.20`,
`endo_decoupled`/`external` `1.00`.) Biology did not couple the heart's pacemaker to
the body's collapse; it gave it an autonomous rhythm — the same decoupling the math
demands.

**5.9.6 Sustenance ≻ efficiency.** Cost `C = Σ|ξ_k|²`, persistence
`T_alive = ∫ 𝟙[alive] dt`. Optimal control minimizes `C` s.t. alive; the heartbeat
instead **maximizes `T_alive` at suboptimal `C`** (redundant kicks). The boundary
trigger of §5.9.2 (`H = H*`) is the policy that maximizes the new-state (alive) rate
*per kick*, so it attains the persistence objective with minimal redundant energy.
Reality/evolution selects the persistence objective, not the efficiency one —
consistent with the heart beating 72/min, wearing out, non-optimal. The virtual
heartbeat is therefore the right
artifact for *sustained ML automation*: deployment-time, training-agnostic, defends the
inner wall without retraining, robust across variable drift. Reality chooses
sustenance over efficiency.

**5.9.7 Cross-system validation.** The heartbeat was tested on two further
experiments from this project's corpus.

- *Emergent self-repelling walk* (`emergent_heartbeat.py`; the canonical inner-wall
  experiment, §4). With `γ=0` the inner wall fails and the walk locks into exact
  recurrence — `aliveFrac` (fraction of steps visiting a *new* site) = **0.298**,
  dead. The adaptive heartbeat (teleport on exact recurrence) drives it to
  **1.000** (896 kicks), fully rescuing it and matching/exceeding intrinsic
  `γ>0` (**0.595**). Jumpstart (one kick) → relapse (**0.298**); fixed interval
  (`P=40`) → partial (**0.548**). Confirms §5.9.2–§5.9.3: external `γ_ext`
  substitutes for failed `γ_int` as life-support, and only while kicking
  (stops ⇒ relapse). This is the §5.9 mechanism reproduced on a *second, distinct*
  dynamic system.

- *Conway's Game of Life* (`conway_heartbeat.py`, `conway_diehard_heartbeat.py`).
  At density 0.3 the soup self-sustains churn (never presents a clean death to
  rescue within 1200 steps) and has `d_s ≫ 2`, so it is doubly dead (§5.8): the
  heartbeat can defend the inner wall but cannot make it truly alive — exactly the
  §5.9.4 outer-wall caveat. A *locked* configuration isolates the inner wall: four
  2×2 blocks (period-1 still-lifes = exact recurrence = death by lock-in, §5.8).
  With the adaptive heartbeat kicking whenever the global state becomes period-≤2,
  `aliveFrac` (non-locked) = **0.980** (rescued into churn); `none` stays locked at
  **0.000**; `jumpstart` relapses (**0.003**); `fixed` interval = partial (**0.409**).
  Confirms §5.9.2–§5.9.3 on Life's inner wall. Life remains `d_s ≫ 2` (doubly dead),
  so this is life-support only — consistent with the outer-wall guard.

**5.9.8 Trigger timing and the boundary optimum.** The *position* of the kick within
the trajectory is decisive, but "earlier is better" is false. On the emergent walk
(`heartbeat_timing.py`, `γ=0`), varying two axes — WHEN the kick fires (late = on
exact recurrence; early = when ≥3 of 4 neighbours are already seen, i.e. *before*
recurrence) and WHERE it lands (random vs aimed at the least-visited site) — gives:

| trigger | aim    | aliveFrac | kicks | max nbr-seen (lower = shallower) |
|---------|--------|-----------|-------|----------------------------------|
| late    | random | **1.000** | 666   | 3.8 |
| late    | away   | 1.000     | 655   | 3.4 |
| early   | random | 0.720     | 233   | 4.0 |
| early   | away   | 0.719     | 225   | 4.0 |

Interpretation: the "early" trigger fires when the walker is merely *surrounded* by
seen sites, yet one neighbour is often still novel — kicking then discards that
remaining unexplored direction, so the walk under-explores (aliveFrac 0.72) despite
fewer kicks. The "late" trigger lets the walk exhaust all local novelty *first*, then
kicks exactly at the recurrence boundary → aliveFrac 1.0. By §5.9.3 the higher kick
rate means higher `γ_ext = (kick rate)·ℙ[|ξ|>ε]`, hence more alive. **Aim (direction)
barely mattered on this shallow basin** — kick *rate*/boundary-alignment dominates;
aimed kicks matter more on steep/structured basins.

Refinement of §5.9.2: the horizon `H` should sit **at the lock-in boundary**, not
"as early as possible." Too-early kicking wastes novelty; too-late kicking (after deep
relaxation into a steep basin) fails to escape. The optimum is the basin boundary —
kick *at* recurrence, where all local novelty is exhausted and `γ_ext` is maximal.

**5.10 Theoretical limits — where the law breaks.** The heartbeat sustains life
*conditionally*. It holds only while **all** of the following hold; crossing any one
collapses `aliveFrac → 0` (`heartbeat_limits.py`, emergent walk, `γ=0`):

- **(L1) Reach.** Kick magnitude must exceed the visited/attracting-region width:
  `|ξ|_max ≥ W(t)`. In open space `W(t)` stays small, so this rarely binds; in a
  *confined* manifold it does. Bounded grid `G`: `aliveFrac → 0.000` for `G ≤ 24`
  (failed kicks ≈ 2900/3000 — no fresh site remains); only `G=40` survives partly
  (0.073). This is the **capacity limit**.
- **(L5) Capacity.** The accessible manifold must not be exhausted: `ν(X) > 0`
  somewhere reachable. When every admissible state is already realized, no kick can
  create novelty — death by exhaustion (fundamental, not a control failure).
- **(L2) Rate / budget.** Required kick rate `1/τ_relax(t)` must be `≤ R_max`
  (max kicks/step, refractory/cost cap). Refractory gap `K`: `aliveFrac` falls
  `1.000 → 0.997 → 0.875 → 0.752 → 0.653` as `K` grows `1→20` — death outpaces the
  controller.
- **(L3) Observability.** The death-proxy `φ_t` must detect `∂B`. Degraded sensing
  (detect probability `p`): `aliveFrac` falls `1.000 → 0.853 → 0.707 → 0.537 → 0.296`
  as `p` drops `1.0→0`; a blind controller cannot rescue.
- **(L4) On-manifold guard** (§5.9.4). `rank(supp ξ) ≤ d_f`; off-manifold kicks raise
  `d_s^eff > 2` ⇒ forgetting-death.
- **(L6) Decoupled energy** (§5.9.5). The controller's energy source must be decoupled
  from the death basin; coupled (endo_coupled) revive fails (0.20).

**Conclusion.** The virtual heartbeat is a *conditional* law:
`ALIVE_heartbeat ⇔ (d_s ≤ 2) ∧ (γ_eff > 0) ∧ (L1) ∧ (L2) ∧ (L3) ∧ (L4) ∧ (L6)`,
with (L5) as the ultimate ceiling. It is life-support, not a cure: remove any
condition and the system returns to death, exactly as observed across the four
experiments (`simulate_adaptive_pacemaker*.py`, `emergent_heartbeat.py`,
`conway_*_heartbeat.py`, `heartbeat_timing.py`, `heartbeat_limits.py`).

**5.11 Adaptive-dimensional rescue (the endogenous mechanism).** The heartbeat
(§5.9) is exogenous and intrusive: it injects energy from outside. The endogenous
counterpart restructures the model's own geometry instead — no external
pacemaker, no injected noise, hence no closed-loop death problem (§5.9.5). The
control variable is the effective dimension `d_f(t)` itself (e.g. participation
ratio of hidden-state covariance, or active-unit count):
- **Expand on lock-in.** Detector: `γ̂ ≤ 0.4` (or exact-recurrence rate rising).
  Action: recruit dimensions (unmask dormant units / lift the rank cap). Effect:
  raises the point-scale `d_s^{(ε)}` above 2, so exact recurrence goes transient
  — §5.8 case 3 achieved *by geometry rather than repulsion*.
- **Contract on chaos.** Detector: outer-wall approach (`d_s → 2` from below,
  rhyme going transient). Action: prune (the existing consolidation machinery:
  coarse storage, drift-threshold pruning, §14). Lowers `d_f`, keeps `d_s ≤ 2`.
Both moves preserve coarse `d_s ≤ 2`, so rhyme survives in both directions:
expansion kills exact recurrence, contraction kills forgetting. Together with
§5.9 this gives the full picture — heartbeat as exogenous life-support
(validated baseline), adaptive dimensionality as autonomy (endogenous
counterpart). Measured in `adaptive_dim_demo.py` (Elman RNN, hybrid rollout):
lock-in regime — recruit reaches aliveFrac 0.118 vs kicks 0.025 (none 0.007),
zero injected energy (kicks 216), task MSE 0.29 vs 0.31 (no regression): FULL
PASS. Chaos regime — prune moves novelty 0.957 → 0.913 toward rhyme range with
MSE 0.350 → 0.329 (no regression): PARTIAL; full task recovery needs relearning,
not just contraction. Two refinements the demo forced: expansion must recruit
*excitable* dimensions (bare unmasking under global contraction is dead
capacity), and contraction must target *expansive* directions plus gain cooling
(random masking cannot quench distributed chaos). ML reading: recruit dormant
units when hidden states freeze into fixed points; gate/prune when they explode
into chaos. Less intrusive than perturbation because it moves the attractor's
resolution, not the state.

---

## 6. The temporal-decay probe (secondary; NOT the falsifiable core)

### 6.1 Status of this probe

> **Demoted (v3).** This section was originally written as "the falsifiable
> prediction" — that was the rebuild's misreading. The hypothesis's falsifiable
> core is the exact/rhyme split (§1.2), its emergence from local perturbation
> (§4.3), and the `ν` criterion (§5.5). What follows is a *secondary* probe:
> under sustained directional drift `α > 0`, recurrence density should also
> fall over time. Its absence in human data is uninformative for the hypothesis.

The level `ρ_∞` depends on both `D` and `α`. Under sustained directional drift,
the additional signature would be **change over time**: exact revisits becoming
*rarer as the session goes on*, as accumulating displacement carries the
trajectory into new regions.

Define the early/late recurrence rates

    ρ_early  = (1/3) Σ_{t=1}^{N/3} r_t ,
    ρ_late   = (1/3) Σ_{t=2N/3}^{N} r_t .                              (8)

Under **drift**, the walk leaves its early region, so `ρ_early > ρ_late`:
the density **decays** over time. Under **i.i.d.** drawing there is no
temporal structure, so `ρ_early ≈ ρ_late`: the density is **flat**.

### 6.2 The shuffle-null test

Statistic: `S = ρ_early − ρ_late`. (Larger `S` ⇒ stronger decay.)

Null model: randomly **permute the point order**. Permutation destroys the
temporal trend but preserves the marginal distribution of points, so the null
`S` should be ≈ 0 (any apparent early/late difference under permutation is
spurious). The p-value is

    p = P( S_null ≥ S_observed )                                      (9)

estimated over `N_shuf = 2000` permutations.

- A genuine drifting drawing ⇒ `S_observed > 0` and in the tail of the null ⇒
  **small p ⇒ SUPPORTED**.
- Pure i.i.d. drawing ⇒ `S_observed ≈ 0` ⇒ **large p ⇒ not significant**.

### 6.3 Empirical anchor (rebuild, synthetic)

> **Correction (v2).** The first `shuffle_null` used point-level recurrence
> *with* pen-path adjacency, which only detects path continuity, not drift, so
> its `p = 0.0000 / 0.9915` was invalid. Point-level recurrence is dominated by
> the "early configs have fewer older references" bias and cannot cleanly show
> decay. The validation below is at the **configuration (centroid) level**, which
> is what the human analysis actually uses.

`shuffle_null.py` on synthetic centroids (`K = 120`):

- **Decaying** (first third rhyme in a tight cluster, last third scattered):
  `early_rate = 0.975`, `late_rate = 0.300`, `S_obs = +0.675`, null mean
  `−0.155`, **`p = 0.0000` → SUPPORTED**.
- **i.i.d.** (all scattered): `early_rate = 0.125`, `late_rate = 0.525`,
  `S_obs = −0.400`, null mean `−0.385`, **`p = 0.635` → not significant**.

The pipeline cleanly **discriminates a real configuration-drift decay from
noise** at the level that matters. The time-course plot (`time_course.png`)
shows `ρ(t)` falling over stroke order for the drifting set and flat for the
i.i.d. set.

---

## 7. Heat-kernel scaling of the return probability

A more fine-grained theoretical prediction is the **time dependence** of the
return probability. From (5)–(6):

    p_t(0) ~ t^{−D/2}              (unbiased)                        (10)
    p_t^{drift}(0) ~ t^{−D/2} exp(−α² t / 2σ²)   (drifted).         (11)

Consequences:
- In the transient tail, `ρ(t)` should decay as a power law with exponent
  `−D/2` for the unbiased walk.
- Drift converts the power-law tail into an **exponential** cutoff.

**Caveat (honest).** Our order parameter `ρ_∞` measures recurrence to *any*
previous point (self-intersection density), not strictly return-to-origin.
Self-intersection has a related but not identical scaling, and in finite
simulations the measured late-window rate saturates rather than following the
bare `t^{−D/2}` law. This is why the rebuild validates the theory via the
**critical-dimension fit** (`D_c ≈ 2.2`, §3.4) and the **drift suppression**
(§4.2) rather than by forcing a single global prefactor onto the raw
time-series — an earlier attempt to fit `K·t^{−D/2}·exp(−…)` directly failed
(MAE ≈ 1.9) precisely because of this saturation. The correct, honest check
is the location of the transition, which matches theory.

---

## 8. The analytic recurrence law (phenomenological)

For a fixed dimension (`D = 2`) the `α`-dependence of `ρ_∞` is well described
empirically by

    ρ_∞(α) = ρ_0 · exp(−λ α) .                                       (12)

`hypothesis_eq.py` fits this to the `D = 2` sweep and obtains

    ρ_0 = 0.465 ,   λ = 1.55 ,   fit MAE = 0.012 .

This `λ` is a **fresh fit on the rebuild**; the original session reported
`λ = 0.0006`, which is UNVERIFIED (lost artifact). Equation (12) is
*phenomenological* — it summarises the simulation, it is not derived from
first principles, and `λ` absorbs dimension- and `ε`-dependent prefactors.
A first-principles derivation (from the Fokker–Planck equation for the
stationary recurrence rate) is listed as future work.

---

## 9. The high-dimensional "thought space" and the curse

`thought_walker.py` runs the walk in `D = 12` (a stand-in for a rich
cognitive configuration space). Result: `ρ_∞ = 0.00000`. Exact revisits are
utterly absent. This is the **curse of dimensionality** made concrete: in high
`D`, even an unbiased walk is transient, so exact recurrence is impossible and
only rhyming (low-dimensional-projection-similar) configurations can recur.
This is precisely the user's everyday observation, now grounded in the
transition at `D_c = 2`.

---

## 10. Coupling to the observer: `𝒞` and the perturbed state

### 10.1 The coupling

The hypothesis is about an *abstract* configuration space, but the observer
experiences it. Let `𝒞` be the coupling between the abstract drift and the
observer's perceptible state. If `𝒞 = 0`, the drift is invisible to the
subject; if `𝒞 ≠ 0`, the accumulating drift *manifests* in experience.

### 10.2 The reported perturbed state (qualitative)

In the original session the user reported, during the later trials, that drawn
shapes "started wrapping into hexagons / septagons" and the cursor left a
"shadow." Under the model this is interpreted as `𝒞 ≠ 0`: the abstract
configuration drift crossing a perceptual threshold, so the observer's own
state becomes a *readout* of the drift. It is **evidence to be re-collected,
not a verified quantitative result** — the rebuild's `collect_draw.py` should
in future also log a per-trial observer tag so this can be correlated with
`ρ(t)`.

### 10.3 Status

This section is **interpretive**. The mathematics of §3–§8 is verified; the
observer-coupling interpretation is a research hypothesis about *why* the
subjective report correlates with the objective decay, and remains to be
quantified.

---

## 11. Statistical power and the human test

The recurrence-measurement pipeline (§6) is validated on synthetic data: it
detects a configuration-recurrence decay when present (`shuffle_null.py`,
`p = 0.0000`) and rejects i.i.d. (`p = 0.635`). For the human test the same
pipeline applies to `drawing_data.csv` produced by `collect_draw.py`.

The **central claim is the exact-vs-rhyme split, not a temporal decay.** A fresh
203-circle / 4000-point drawing (a 142-circle run is backed up as
`drawing_data_v1.csv`) confirms it directly: rhyme-level recurrence ≈ 0.9, while
**exact recurrence collapses as configuration resolution fines** (97.5% at
coarse bins → 37.4% at `B=50`, tending to 0). That is the curse of
dimensionality observed on real data — the hypothesis's hero target. The
separate temporal-*decay* probe (added during the rebuild, not part of the
original claim) shows no significant human decay; this is irrelevant to the
hypothesis. The original lost numbers `rec_mu = 0.000` (exact) and
`rec_H = 0.900` (rhyme) are the genuine supporting evidence; the lost
`p = 0.032` was the decay probe and is withdrawn as central.

---

## 12. Speculative appendix: fundamentality, civilizations, and present-day verdicts

> **Scope notice.** This section (and the civilizational/Earth rows of §15) is
> **speculative analogy, not validation**: toy order-parameters, no corrected-rules
> verification (no floors, no measured `d_w`). It is kept as an appendix for
> its motivational value. The validated core is trajectory stability in
> recurrent dynamical systems (§§3–5, §16); nothing there depends on this section.

A speculative but motivationally central reading:

- **Exact non-recurrence = the arrow of time.** If configurations never exactly
  repeat, the trajectory is irreversibly unique — a microscopic basis for a
  time direction in the cognitive substrate.
- **Accumulating drift = dissipation.** The systematic exploration is a
  one-way leakage of the trajectory into new regions, analogous to entropy
  production.
- **Absence scenarios.** In a space with `D < 2` and `α = 0` (the recurrent
  phase) configurations *do* recur — a world without a unique time arrow at
  that scale (an "eternal return" regime). The valid band
  `{ D > 2 } ∪ { α > 0 }` is then the condition under which a cognition with a
  definite history can exist.

This is **interpretation**, clearly separated from the verified mathematics.
It motivates the hypothesis but is not itself a result of the simulations.

---

## 13. Open theoretical questions

1. **First-principles `ρ_∞(D, α)`.** Derive the stationary recurrence rate
   from the Fokker–Planck equation for the drifted walk, replacing the
   phenomenological `exp(−λα)` law with a closed form.
2. **Self-intersection scaling.** Relate `ρ(t)` (return to *any* point) to the
   heat kernel rigorously; resolve the saturation that blocks a naive
   `t^{−D/2}` fit.
3. **4-D field / mobile grains substrate.** Generalise from a point walk to a
   field or a system of interacting "grains" whose collective configuration
   drifts — a richer model of a drawing *gesture*.
4. **Steady-state derivation.** Compute the asymptotic `ρ_∞` boundary
   (relaxation vs avoidance) analytically, extending the Pólya argument to the
   drifted, bounded, multi-point case.
5. **Observer coupling `𝒞`.** Quantify how `𝒞` maps abstract drift onto
   perceptible distortion; predict the trial at which the perturbed state
   should appear from the measured `ρ(t)` decay.
6. **Memory phase boundary at full scale (d=768).** Compute ν and w from the
   full model's telemetry (drift.py, manifold_health.py, chi.py) and validate
   whether the memory manifold crosses the phase boundary at the predicted
   capacity threshold. The sim validated the qualitative prediction; the full
   model tests the quantitative one.
7. **Consolidation as dimension reduction — formal proof.** Prove that
   drift-threshold pruning reduces the correlation dimension of the memory
   manifold, keeping ν below w. The sim shows it works; the theory should
   explain why.
8. **[RESOLVED — §5.8] The life/death principle — formal statement.** Theorem
   (Life/Death): `Alive ⇔ (d_s ≤ 2) ∧ (γ > 0)`; `d_s = 2` is the outer wall
   (beyond it rhyme is impossible → death by forgetting), `γ = 0` the inner wall
   (inside it exact recurrence accumulates → death by lock-in). Derived from the
   CDT spectral-dimension framework (§5.6) and the heat-kernel Green functions
   `G_ε`, `G_R`.
 9. **[EMPIRICALLY PROVEN — theory §5.8 Corollary 2] Action-gated memory and the
    pressure principle.** "Memory provides *internal* pressure that shapes dynamics,
    but only when the model (or system) chooses to engage." External/unconditional
    forcing is a crutch, not a mechanism: Conway's Life relapses into lock-in no
    matter how often an external actor perturbs it (web-sim), and Zeus Night3/Night4
    show unconditional reads → collapse/soup while action-gated reads → structure.
    Formal write-up remains: define `γ_intrinsic` vs exogenous forcing and prove
    relapse when the actor stops.
    **Refinement (§5.8, added):** endogeneity confers *autonomy*, not *rescue*. At
    the death boundary the attracting basin drags the internal rescuer down with the
    state, so external sustenance has strictly better odds and is the only reliable
    rescuer; reality chooses **sustenance over efficiency**. The "virtual heartbeat"
    (state-triggered external perturbation loop) is therefore the primary organ of
    persistence at the boundary, not a second-class crutch. Simulated across the
    fixed → adaptive → refined → endogenous ladder (`simulate_heartbeat.py`,
    `simulate_adaptive_pacemaker.py`, `simulate_adaptive_pacemaker2.py`): adaptive
    tracks the variable death rate and sustains ~2× better than a fixed metronome;
    refined (proportional + predictive + outer-wall-guarded) holds `aliveFrac = 1.00`
    with `d_s ≤ 2`; the boundary rescuer is necessarily external.

---

## 14. Memory as CDT — exact recall is transient, coarse recall is recurrent

### 14.1 The mapping

Memory is configuration drift applied to the past. A memory system stores
snapshots of a model's state at earlier times. As the model trains, its state
drifts — the same mechanism that governs spatial configuration drift also
governs the relationship between stored memories and the current state.

| Spatial CDT | Memory CDT |
|---|---|
| Configuration space (768-D) | State space (768-D) |
| State drift over time | Model state wanders from where memory was captured |
| Exact recurrence vanishes | Exact recall vanishes as model drifts |
| Rhyme persists | Similar-state recall persists |
| ν (correlation dimension of manifold) | ν (dimension of memory manifold) |
| d_w (walk dimension, =2 for standard diffusion) | d_w (=2/β from MSD of recall dynamics) — **not** the drift rate |
| Phase boundary: ν ≤ d_w recurrent | Phase boundary: memory manifold dimension ≤ walk dimension → recallable |
| Phase boundary: ν > d_w transient | Phase boundary: > walk dimension → unreachable |

### 14.2 CDT predictions for memory

**Prediction 1: Exact recall is transient.** As the model's state drifts, the
correlation distance between the current state and an old memory grows. CDT
predicts that exact recall (matching the stored pattern precisely) becomes
impossible once the drift exceeds the manifold dimension.

**Prediction 2: Similar-state recall is recurrent.** Coarse-grained retrieval
(finding patterns *similar* to the current state, not identical) persists
regardless of drift — because rhyme survives at O(1).

**Prediction 3: Consolidation is dimension reduction.** The consolidation
process (strengthening useful patterns, weakening noise) *reduces* the effective
dimension of the memory manifold. By pruning noise and strengthening signal,
consolidation keeps ν below the phase boundary.

**Prediction 4: There is a critical memory capacity.** Beyond a critical number
of stored patterns, the memory manifold dimension exceeds the drift rate and
exact recall becomes impossible. The bank should have a *natural* capacity limit
— not a fixed slot count, but a dynamic limit based on the drift rate.

### 14.3 Validated in simulation and full model

The CDT-consistent memory architecture was tested first in a simplified
simulation (d=64) and then deployed on the full Zeus ESNPN model (d=768):

**Sim (d=64):**

```
exact_dynamic:    CE 7.30 → 8.30 (+1.00 nats)   DEGRADING
coarse_dynamic:   CE 7.32 → 6.22 (−1.10 nats)   IMPROVING
```

Coarse-grained recall outperforms exact recall by 2.08 nats and sustains
stability.

**Full model (d=768) — Night6, step 7,000:**

```
val_ce:    6.94 (BELOW L1 floor of 7.10)
persist:   -0.75 to -1.11 (fluctuating, not eroding)
hcm_n:     333 patterns across 31 regions
recalls:   193,281 (97% hit rate)
```

First time memory has helped prediction in the full model. The CDT-consistent
architecture (coarse-grained k-means storage, drift-threshold pruning) keeps
the memory manifold in the recurrent regime (ν ≤ d_w, §5.6), preventing the
stale-re-entry collapse that killed earlier attempts.

> **Measurement note (Night6 telemetry).** The first full-model ν/w readout
> reported `ν = 2.228`, `w = 37.153`, `ν/w = 0.06`. That `w` is a *drift rate*
> (mean per-step displacement, with units), **not** the walk dimension `d_w`
> (dimensionless, `d_w = 2/β` from MSD scaling). The 0.06 ratio is therefore
> *not* a phase-boundary test. To apply §5.6 one must measure β from the memory
> manifold's recall dynamics and compute `d_w = 2/β`; only then does `ν ≤ d_w`
> decide recurrent vs transient. The healthy signals (val_ce < L1, fugazee = 0,
> persist fluctuating) remain valid regardless — they show the system is alive,
> but they do not by themselves place the manifold relative to the phase boundary.

### 14.4 The life/death principle

The phase boundary is not just a mathematical curiosity — **it is the line
between life and death.**

**Exact recurrence = death.** When a system perfectly recycles its exact states,
it stops exploring new configurations. It becomes a closed loop — a whirlpool,
not a river.

**Rhyme = life.** When a system coarsely matches its past — similar but not
identical — it maintains continuity while still exploring. Structure survives,
novelty emerges, the system stays alive.

Evidence across every domain:

| Domain | Exact recurrence → death | Rhyme → life |
|---|---|---|
| Ring world (survival.py) | γ < 0: collapse to 2-state oscillation | γ > 0: immortal circulation |
| Memory (CDT sim) | CE degrades (+1.00 nats) | CE improves (−1.10 nats) |
| Genetics | Zero-variation population → extinction | Variation sustains populations |
| Markets | Copy-masquerade → arbitraged away | Fear rhymes → sustained cycles |
| Civilizations | Perfect repetition → stagnation and death | Cultural rhyme → sustained structure |
| Drawing | Microscopic tracing (copying) | Perceived-level rhythm (rhyming) |
| Zeus (Night3) | Unconditional HCM reads → collapse (132.55) | Action-gated memory → structure |
| Conway's Life | γ=0 (no repulsion) → death by lock-in: period-2 oscillators (§5.8) | Mutation adds repulsion → sustains dynamic structures |

Self-repulsion — the walk that avoids revisiting itself — is the **mechanism
that keeps systems alive.** It prevents exact recurrence. It forces rhyme. It
is the drive to explore, to not repeat exactly, to maintain continuity without
stagnation.

### 14.5 The CDT-consistent memory architecture

Based on the validated predictions, the CDT-consistent memory design is:

| Component | Design | CDT Justification |
|---|---|---|
| Storage | Online k-means clustering (32 regions) | Coarse-grained: reduces ν |
| Retrieval | Cosine similarity to nearest region | Rhyme-based: stays in recurrent regime |
| Consolidation | Drift-threshold pruning every 100 steps | Dimension reduction: keeps ν ≤ d_w |
| Capacity | Dynamic (prune far patterns) | Phase boundary management |
| Gating | Action-gated (model chooses when to recall) | Agency: voluntary engagement with memory pressure |

The architecture is validated in sim (2.08 nats improvement over exact recall)
and ready for port to the full model (d=768).

---

## 15. Summary of verified theoretical results

| Claim | Theoretical basis | Rebuild verification |
|---|---|---|
| Recurrence→transience transition exists | Pólya `Σ n^{−D/2}` | `ρ` collapses `D=2→3` |
| Critical dimension `D_c = 2` | local CLT / heat kernel | fitted `D_c = 2.20` (err 0.20) |
| Drift kills recurrence everywhere | `exp(−α²t/2σ²)` factor | `ρ_∞` falls at every `D` with `α` |
| Exact recurrence vanishes, rhyme persists | curse of dimensionality / Pólya | exact `ρ→0` for `D≥3`; human rhyme≈0.9, exact→0 with resolution |
| High-`D` ⇒ no exact revisits | transient for `D>2` | `D=12 ⇒ ρ=0.00000` |
| Transition is dynamical, not boundary | — | torus substrate shows same transition |
| Drift, not noise, drives decay | sensitivity `δ=0` | `ρ=0.489 ≈` baseline `0.481` |
| Memory: exact recall transient, coarse recall recurrent | CDT applied to stored patterns | sim: 2.08 nats improvement (coarse vs exact) |
| Consolidation = dimension reduction | keeps ν ≤ d_w (§5.6) | drift-threshold pruning sustains stability |
| Exact recurrence = death, rhyme = life | theorem (§5.8): `Alive ⇔ (d_s ≤ 2) ∧ (γ > 0)` | 8 stand / 5 partial / 1 withdrawn (§15 audit) |

### 14-domain evidence inventory (not a universal validation count)

Audited standing across 14 examined domains (corrected rules): **8 stand, 5
partial (direct claims hold, ν legs gated), 1 withdrawn**. Only recurrent-systems
domains count as validations; cosmic rows are speculative analogy (§12):

1. **Spatial drift** — exact recurrence vanishes, rhyme persists (15+ simulations)
2. **Genetic drift** — matches Fisher–Wright to 3 decimals
3. **Human drawing** — WITHDRAWN pending data (`dimension_test.py`, corrected
   rerun): with measured stroke `d_w` (v2 β=0.55→d_w=3.66; v1 β=0.05, confined,
   not a walk at all) and fix-2 floors, N=142/203 falls far below floors
   (~1000–4300) → all four drawing verdicts UNDECIDABLE. The old
   "ν≈1.6 recurrent / ν≈2.4 transient" used assumed w=2 plus an underpowered N;
   needs ~1000+ strokes to re-assert.
4. **Lorenz chaos** — transient dynamics classified correctly
5. **English prose** — structure vs content separation
6. **SGD** — optimization trajectory drift
7. **Celestial mechanics** — ν classifies regular vs chaotic orbits
8. **Conway's Life** — spontaneous period-2 lock-in: a γ=0 (dissipative) rule, so per the Life/Death theorem (§5.8) it must die by lock-in; gliders are the rare transient (alive-looking) phase. Independent web-sim observation matches.
9. **π** — maximally transient (confirmed)
10. **Conversation transcripts** — self-referential test passed
11. **Civilizational drift** — G·ε > δ condition in a toy model (speculative analogy, §12)
12. **Live markets** — fear rhymes, copy masquerades
13. **Earth (current status)** — ε winning on volume, δ winning on trend (speculative analogy, §12)
14. **Memory (Zeus sim)** — exact recall transient, coarse recall recurrent (2.08 nats)

**Corrected re-audit (`recheck_domains.py`: `nu_local` + CI + fix-2 floors).**
Direct-measurement claims (ladders, concentrations, repeat fractions, order
parameters) are unaffected; only ν-threshold verdicts were re-examined:
- STANDS: Lorenz (ν=1.93 [1.92,1.96], usable, lit ~2.06); celestial A
  (ν=1.12, recurrent) / B (ν=2.07 [2.07,2.10], transient), both usable;
  genetic, spatial, Life, civilizational, Earth, memory (non-ν evidence).
- PARTIAL (ladder/direct claims stand, ν leg gated): prose (uni-rec 0.675,
  bi-rec 0.149, sent-repeat 0.0013 stand; ν=2.18 undecidable, N=777<1368);
  SGD (recurrence-rise/quartiles stand; halves ν≈4.9/5.1 undecidable);
  π (P4/P5 block-recurrence stand; P6 ν~6 undecidable, N≈1000 vs floor 100k);
  conversation (R1/R2/R4 + ladder stand; R3 ν-leg undecidable, N=366<428);
  markets (P1/P2 stand; P3 ν-leg undecidable; `levy_kill.py`: normal survives).
- WITHDRAWN: human drawing (domain 3, see above).

**Whole-system sweep (`system_audit.py`; now marked legacy/exploratory).** The
historical pipeline combined measured `d_w`, floors, and a model-calibrated
`γ̂` deadband. The former `α·d_w/2` boundary was incorrect and has been removed;
an identified walk dimension already contains the anomalous scaling. Across the
formula-sensitive systems: cubes D=1/2 recurrent, D=3/4 UNDECIDABLE; emergent
+0.8 alive / 0 dead / −0.8 lock-in-dead; BTC and SPX dead (memoryless direction,
consistent with P1); drawing UNDECIDABLE. Two lessons: (i) the sweep forced the
γ̂ neutral deadband (0.4) — without it, neutral walks misread as alive; (ii)
**recurrent ≠ alive**: the BM 2D walk is recurrent yet dead (case 2, exact
recurrence accumulates). Heartbeat/conway rows are aliveFrac-based and unaffected.

**Corrected bottom line.** The simulations exhibit several exact/coarse
separations, but they do not prove one universal law across 14 domains. The
canonical theorem requires a finite full-state Green quantity together with
recurrence of a predeclared structural quotient. Pólya's `D_c = 2`, the
self-repelling simulations, memory ablations, and domain analogies are distinct
evidence classes and must be reported separately. No recurrence statistic alone
defines life or functional success.

## 16. Scope and limits of the hypothesis

The historical draft proposed `Alive ⇔ (d_s ≤ 2) ∧ (γ > 0)`. The audit in
`configuration_drift_theorem.md` disproves that as a universal equivalence and
replaces it with explicit Green-kernel, projection, capacity, and conditional
Borel-Cantelli results. The experiments below remain useful boundary examples,
not proofs of the withdrawn equivalence.

### 16.1 LIMIT-1: normal diffusion assumed (anomalous walks)
The Brownian shortcut assumes `d_w = 2`. For an isotropic Lévy flight with
stability index `α`, the walk dimension is already `d_w = α`, and the recurrence
threshold is `ν ≤ d_w = α`. In 2D, `α < 2` walks
are **transient** (forget) even though normal diffusion at `d_s ≤ 2` would be
recurrent.
- *Empirical (2D Lévy), exact-recurrence:* `0.297` (α=2) → `0.076` (α=1);
  new-site fraction `0.703 → 0.924`. A 2D system "dies by forgetting" under Lévy
  statistics — CDT's `d_s ≤ 2` boundary fails.
- **Scope:** the Brownian `ν ≤ 2` shortcut must be replaced by the identified
  process's Green-kernel test. Under the two-sided power-law assumptions this is
  `ν ≤ d_w`; multiplying by `α` again double-counts anomalous scaling.
- **Kill test (`levy_kill.py`, daily BTC/ETH/SPX).** Registered threshold: kill iff
  normal and generalized verdicts disagree AND observation matches generalized.
  Outcome: Hill `α ≈ 2.5–3.1` — daily closes are finite-variance, not Lévy
  (`α < 2`), so the test's precondition fails; crypto `N ≈ 1000` falls below the
  fix-2 floor (`UNDECIDABLE`, rule holds — no classification from insufficient
  data); SPX is usable and the observation matches **CDT-normal** (transient).
  **Result: 0 kills; CDT-normal survives.** A genuine kill needs `α < 2` data
  (intraday/tick); synthetic Lévy (`cdt_limits.py` LIMIT-1) remains the
  demonstrating case for the generalized boundary.

### 16.2 LIMIT-2: unbounded configuration space assumed
The outer wall (`d_s ≤ 2`) is a Pólya statement for an **unbounded** space. On a
**bounded** manifold, confinement forces recurrence regardless of `d_s`: a 3D walk
(`d_s = 3 > 2`, "forgetting death" unbounded) on a finite box recurs.
- *Empirical (3D box), exact-recurrence:* `L=8 → 0.982`; `L=128 → 0.194`.
  Confinement overrides the outer wall.
- **Scope:** CDT's outer wall is the condition for *unbounded* exploration; bounded
  systems are always recurrent (but then hit the capacity limit, §5.10 L5). This is
  why memory (a bounded store) can sustain exact recall despite high ambient `D`.

### 16.3 LIMIT-3: repulsive realization→next-state perturbation assumed
The inner wall (`γ > 0`) requires that realizing a state makes it *less* likely next
(the emergent self-repulsion of `emergent_walk.py`). If the physical law is
**attractive** (`γ < 0`: realizing a state makes it *more* likely — Hebbian /
positive-feedback / mode-collapse), exact recurrence is amplified, not suppressed.
- *Empirical (new-site fraction vs γ):* `+0.8 → 0.598`; `0.0 → 0.324`;
  `−0.8 → 0.000`; `−2.0 → 0.000`. Attraction collapses novelty entirely; the
  inner-wall mechanism inverts.
- **Scope:** CDT's "life" requires repulsive or neutral dynamics. Under intrinsic
  attraction the system locks in faster, and even external rescue (§5.9) fights an
  uphill battle — the controller must overcome the attraction, not merely add
  repulsion.

### 16.4 Further scope boundaries (conceptual)
- **Functional recurrence.** CDT equates life with *trajectory novelty*
  (non-exact-recurrent, rhyming). But a limit cycle / clock / running program loop is
  functionally alive yet *exactly* periodic; CDT classifies it "dead by lock-in."
  Scope: CDT's life/death is about *generative novelty*, not *functional viability*.
- **Metric configuration space required.** Rhyme (near recurrence) needs a metric with
  meaningful neighborhoods. In purely categorical/discrete spaces with no proximity,
  rhyme collapses to exact and the exact/rhyme split is undefined.
- **Quasi-stationarity.** The phase boundary assumes roughly stationary `d_s, ν, γ`.
  Under rapid non-stationarity (concept drift changing `ℳ`) the boundary is a moving
  target; CDT applies to quasi-stationary regimes.
- **State-describable systems.** CDT needs a classical configuration manifold `ℳ`.
  Indefinite/quantum states (density matrices, no point in config space) evade the
  current formulation.
- **Observational (small-data).** `ν` estimation is finite-sample biased
  (`debias_nu.py`); with too little data the exact/rhyme split is undecidable, so
  CDT is untestable in small-data regimes.

### 16.5 Synthesis
The reusable result is conditional on two independently established facts:
(i) the registered fine target has finite full-state Green potential (or is
otherwise proved transient/polar), and (ii) a predeclared structural quotient is
recurrent. Under two-sided heat-kernel scaling, `d_f ≤ d_w` is a shortcut for
recurrence; outside those assumptions use the Green quantity directly. Metric,
projection, stationarity, resolution, and finite-data limitations remain part of
the claim contract. Repulsion and heartbeat control are possible mechanisms to
test in specified models, not universal prerequisites or equivalences.
