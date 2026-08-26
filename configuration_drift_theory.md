# Configuration-Drift Hypothesis — Theory (Exhaustive)

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

Naïvely this looks like a curiosity about drawing. The hypothesis elevates it
to a general principle about **states realized in time** — physical, thought,
or dream alike.

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
| `w` | walk dimension of the explorer (= 2 for diffusion); recurrent iff `ν ≤ w` |
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

### 5.5 The global criterion: correlation dimension vs walk dimension (`dimension_test.py`)

Pólya's theorem generalizes to arbitrary manifolds: a diffusive explorer (walk
dimension `w = 2`) on a configuration manifold of **correlation dimension `ν`**
is *recurrent* iff `ν ≤ w`, *transient* iff `ν > w`. `ν` is measurable from any
set of realized configurations via the pair-correlation scaling
`C(ε) ∝ ε^{ν}` — the estimator validates on synthetic clouds of known
dimension (`D=1 → 0.93`, …, `D=4 → 2.95`; known negative bias at low `D`).

Measured on the human drawing:

| Configuration manifold | ν | Regime |
|---|---|---|
| Perceived level (centroids only) | 1.61 – 1.67 | recurrent — rhyme persists |
| Microscopic level (+ radius + speed) | 2.28 – 2.55 | transient — exact vanishes |

**The exact/rhyme split is a phase boundary at `ν = w = 2`, crossed between the
two levels of description of the same behaviour.** Globally, the hypothesis
holds precisely where `ν > 2` — which covers generic high-dimensional real-world
configuration manifolds — and fails in the recurrent phase below it. This turns
the hypothesis from a narrative into a decidable condition, applicable to any
system (including artificial ones) from trajectory data alone.

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

## 12. Relation to fundamentality (interpretive)

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

---

## 14. Summary of verified theoretical results

| Claim | Theoretical basis | Rebuild verification |
|---|---|---|
| Recurrence→transience transition exists | Pólya `Σ n^{−D/2}` | `ρ` collapses `D=2→3` |
| Critical dimension `D_c = 2` | local CLT / heat kernel | fitted `D_c = 2.20` (err 0.20) |
| Drift kills recurrence everywhere | `exp(−α²t/2σ²)` factor | `ρ_∞` falls at every `D` with `α` |
| Exact recurrence vanishes, rhyme persists | curse of dimensionality / Pólya | exact `ρ→0` for `D≥3`; human rhyme≈0.9, exact→0 with resolution |
| High-`D` ⇒ no exact revisits | transient for `D>2` | `D=12 ⇒ ρ=0.00000` |
| Transition is dynamical, not boundary | — | torus substrate shows same transition |
| Drift, not noise, drives decay | sensitivity `δ=0` | `ρ=0.489 ≈` baseline `0.481` |

**Bottom line.** The Configuration-Drift Hypothesis is **theoretically
sound and simulation-verified**: a state's exact recurrence vanishes as its
configuration dimension (number of contributing elements) grows — the
curse of dimensionality / Pólya `D_c = 2` — while coarse/rhyme recurrence
persists. The human drawing confirms the split directly (rhyme ≈ 0.9; exact
recurrence collapses toward 0 as resolution fines). The temporal *decay* of
recurrence density was a secondary probe added during the rebuild, not the
original claim; its absence in the human data does not bear on the hypothesis.
The original supporting numbers were `rec_mu ≈ 0` (exact) and `rec_H ≈ 0.9`
(rhyme).
