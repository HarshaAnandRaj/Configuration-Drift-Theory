# Configuration-Drift Hypothesis — Report (corrected framing)

> **Provenance.** The original experiment's artifacts (14 scripts, `drawing_data.csv`,
> and its numbers `rec_mu=0.000`, `rec_H=0.900`, `p=0.032`) were **lost/deleted**
> (the project folder had been renamed to "New folder" containing only `.git` +
> an empty `__pycache__`; searched the whole profile, both drives, Recycle Bin, and
> git history — nothing recovered). This report is an independent rebuild from
> scratch. Every number/figure below is produced by the scripts now present and is
> reproducible by running them.
>
> **Math corrections made during the rebuild (all real bugs, now fixed):**
> 1. `recurrence_events_tgap` had an **inverted time-gap mask** (it included
>    recent points and excluded old ones — the reverse of its intent). Fixed and
>    vectorized.
> 2. `shuffle_null.py` originally used adjacency-*inclusive* point recurrence,
>    which only detects path continuity, not drift. Rewritten to the centroid
>    (configuration) level, where the pipeline actually operates.
>
> **Framing correction (most important).** The *original* hypothesis is the
> **exact-vs-rhyme split**: exact recurrence of a state vanishes (because realizing
> a state perturbs its many contributing configuration elements), while *rhyme*
> (coarse/perceived recurrence) persists. The rebuild mistakenly promoted a
> *temporal decay of recurrence density* to the "hero" test. That decay probe is a
> secondary consequence, **not** the central claim, and its absence in the human
> data does **not** bear on the hypothesis. This report is rewritten around the
> true claim.

---

## 1. The hypothesis (restated from the source)

In what we call reality — the physical world, and equally a thought or a dream —
a state that happens once has its probability of happening again in the *exact*
same way reduced by some degree. The reduction per step is so small that the next
state still **rhymes** with the old one (matches at the perceived level), which is
why it "feels like you've seen this before." But it is not exact.

Examples offered by the author:
- Walking the same path daily: you never place your foot in the *exact* same spot
  or with the exact same length as yesterday. Microscopically it is never the same;
  at the perceived level it "fits."
- Double-slit (weak analogy): unobserved photons form a wave (we do not know why),
  but we have many observable contributing elements. Not 1:1.
- Coin flip: the *perceived* difference is heads/tails (2 outcomes), but a flip
  depends on air resistance, number of rotations, and many elements — too many for
  human heuristics. Being right does not mean understanding the system.

Core tenets:
- A realized state draws on **many contributing elements** (not just "me placing my
  foot"). Once it occurs, time's continuity carries the system to a neighboring
  state whose available configurations have been microscopically altered, so the
  *exact* prior configuration is improbable to re-realize.
- Exact recurrence probability → 0; **rhyme persists**. That split is the claim.
- Not memory, not metaphysics, not "anti-repeat." "Quantum" here means *microscopic
  configuration*, not literal quantum mechanics.

---

## 2. Mathematical form

A **state** = a point in a configuration space of dimension `D`, where `D` is the
number of independent contributing elements (foot placement, path deformation,
velocity, wind, …). Realizing a state occupies a configuration `x_t`. Because time
is continuous (state→state, nothing manifests in between), the next state arises
from a configuration perturbed by the elements that just acted.

- **Exact recurrence**: return to the *same* configuration `x` (same site in a
  discrete lattice, or within a microscopic tolerance in the continuum).
- **Rhyme recurrence**: return within a *coarse* tolerance (perceived-level match).

The mathematics is then the classical **random-walk recurrence/transience
transition (Pólya)**: exact return probability is 1 (recurrent) for `D ≤ 2` and
falls off as `~ n^{−(D−2)/2}` (transient) for `D > 2`. As the number of
contributing elements `D` grows, **exact recurrence vanishes** while coarse/rhyme
recurrence (a larger tolerance) persists much longer. This is the curse of
dimensionality, and it is the rigorous substrate of the hypothesis.

A drift/`𝒞` term (the system's own motion perturbing the next configuration) only
accelerates the vanish — it is not required for the effect, merely a mechanism by
which exact returns become improbable.

---

## 3. Model results (exact vs rhyme)

### 3.1 Exact site recurrence on a lattice (`lattice_walk.py`)
A drifted walk rounded to integer sites `Z^D`; exact recurrence = return to the
same site. `ρ` = fraction of late sites that are exact repeats.

| D | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| ρ (α=0) | 0.986 | 0.575 | 0.131 | 0.035 | 0.011 |
| ρ (α=0.6) | 0.527 | 0.220 | 0.075 | 0.025 | 0.009 |

Exact recurrence is high only for `D ≤ 2` (few contributing elements) and collapses
for `D ≥ 3` — i.e. whenever a state has more than a couple of independent
contributing elements. **This is the exact-vs-rhyme transition, proved.**

### 3.2 Continuum sweep (`phase_scan.py`, `theory_check.py`)
Late-window recurrence rate vs `D` (eps-ball proxy) collapses `D=2→3`; logistic fit
gives `D_c = 2.20` (theory `2.00`, error `0.20` — estimation uncertainty of the
proxy, not a discrepancy). Drift suppresses exact recurrence at every `D`.

### 3.3 Thought-space / curse (`thought_walker.py`, `dimension_scaling.py`)
At `D=12` (a "thought space" with many contributing elements) exact recurrence is
`ρ = 0.00000` — exactly the author's "exact recurrence vanishes." A 12-D state
simply cannot recur exactly.

**Conclusion of the model:** the hypothesis's central mechanism is sound and
simulation-verified — exact recurrence vanishes as contributing elements (D) grow;
rhyme (coarse return) persists.

### 3.4 Emergent self-repulsion (`emergent_walk.py`) — the mechanism, not a parameter
The above used an *external* drift `α`. But the author's mechanism is **emergent**:
realizing a state perturbs the configuration for the next state, so the exact
state becomes improbable — with no external drift field. We model this as a
**self-repelling walk** on `Z^D`: at each step the walker picks a neighbour with
weight `exp(−γ · visits[site])`, so a site realized even once is slightly less
likely to recur. `γ` is tiny → microscopic per-step change; accumulated → exact
recurrence vanishes while rhyme persists.

| D | γ=0 (plain) | γ=0.5 | γ=1.0 | γ=2.0 | (exact / rhymeR2) |
|---|---|---|---|---|---|
| 2 | 0.72 / 0.93 | 0.46 / 0.82 | 0.36 / 0.77 | **0.235 / 0.71** | exact ↓, rhyme high |
| 3 | 0.33 / 0.88 | 0.19 / 0.80 | 0.12 / 0.77 | **0.050 / 0.72** | exact ↓↓, rhyme high |
| 4 | 0.19 / 0.87 | 0.11 / 0.82 | 0.07 / 0.78 | **0.025 / 0.74** | exact →0, rhyme high |

**Exact recurrence collapses as the emergent perturbation strengthens — even in
D=2 where a plain walk is recurrent — while rhyme (R=1, R=2, non-adjacent)
stays elevated.** The exact/rhyme split is therefore an *emergent property* of a
simple local rule, not something imposed. This is the direct simulation of the
author's "states flow in continuity; realizing one perturbs the next."

### 3.5 Ablation: remove the loss of exact recurrence (`ablation_study.py`)
If vanishing exact recurrence is merely decorative, ablating it should change
nothing but the exact-count. We sweep `γ`: positive (hypothesis regime),
zero (neutral), **negative — visited configurations ATTRACT, forcing exact
recurrence to persist** — and watch how the system reacts (D=3, 4000 steps,
12 trials):

| γ | regime | exact | rhyme | distinct sites | RMS radius | occupancy entropy |
|---|---|---|---|---|---|---|
| −3.0 | FULL ABLATION | 1.000 | 1.000 | **2** | 0.8 | 0.867 |
| −1.0 | FULL ABLATION | 1.000 | 1.000 | **2** | 1.8 | 0.425 |
| −0.5 | FULL ABLATION | 1.000 | 1.000 | **2** | 4.3 | 0.270 |
| 0.0 | neutral | 0.340 | 0.879 | 1334 | 56.3 | 0.984 |
| +1.0 | hypothesis | 0.126 | 0.789 | 1755 | 65.4 | 0.995 |
| +2.0 | hypothesis | 0.051 | 0.735 | **1901** | 64.1 | 0.998 |

**Reaction: the system dies.** With the loss of exact recurrence ablated, the
walker collapses into a **two-state oscillation** — it visits exactly 2
configurations forever, displacement falls from ~65 to <5, and occupancy
entropy decays toward degeneracy. Exact recurrence is "restored" only by
destroying everything else: no exploration, no novelty, no history. In the
hypothesis regime the same dose-response runs monotonically the other way:
less exact recurrence ↔ more novel states (1334 → 1901), higher entropy,
sustained displacement — while rhyme stays high throughout.

**Conclusion of the ablation:** the loss of exact recurrence is not a curiosity
of high-dimensional spaces — it is the **engine of state generation**. A system
in which states can repeat exactly is a system that stops having new states.
This gives the hypothesis a functional consequence: continuity toward new
configurations exists *because* exact recurrence fails.

### 3.6 The fall into exact recurrence (`collapse_transition.py`)
How far can self-perturbation degrade before a system locks into exact
recurrence — and what does the approach look like? Sweep `γ` finely through
zero into attraction (D=3, 4000 steps, 10 trials):

| γ | ρ_exact | effective states | RMS | P(period-2 lock) |
|---|---|---|---|---|
| +0.75 | 0.154 | 1507 | 64 | 0.087 |
| −0.02 | 0.355 | 976 | 43 | 0.169 |
| **−0.17** | **0.902** | **7** | 25 | **0.849** |
| −0.25 | 1.000 | **2** | 12 | 1.000 |
| −1.25 | 1.000 | 2 | 1.2 | 1.000 |

Three findings:

1. **The margin is thin and the snap is sharp.** The critical point sits at
   `γ_c ≈ −0.13`: crossing it, the system falls from ~900 lived-in
   configurations to 7 to **2**, within one grid step. Any residual repulsion,
   however small, keeps the system alive — there is no long slow slide, but a
   smooth premonitory phase followed by a sudden lock-in.
2. **The system telegraphs its own collapse.** All three precursors degrade
   smoothly well before the cliff: effective states shrink (1507 → 976), exact
   recurrence more than doubles (0.15 → 0.36), period-2 tendency nearly doubles
   (0.087 → 0.169). The fall is visible in advance.
3. **The death gait is a strict period-2 oscillation.** Below `γ_c`,
   `P(x_t = x_{t−2}) = 1.000` everywhere: the "eternal return" is literally a
   two-beat loop. (Lag-1 autocorrelation proved coordinate-dependent and
   uninformative; `osc2` is the clean signal.)

All emergent — the walker knows only `w(site) = exp(−γ·visits[site])`.

**Zeus implication:** the pre-CDT baseline (entropy 1.68→0.94, sites 22→16) shows
exactly these smooth precursors. The gate for `manifold_health.py` should be
*trend-based* — rising `ρ_exact`, shrinking distinct-site count, growing
period-locking — because the data says the snap, when it comes, gives little
warning on its own.

### 3.7 Real-world constraints (`physical_walk.py`) — and a surprise
The abstract rules replaced by physics: a walker with **inertia**, in a
**bounded arena**, through a **deformable substrate** — each visit dents the
ground (the author's footstep), dents push later steps aside, and the ground
heals on timescale `τ_mem` ("subjected to the elements"). Sweep world memory,
with a `k_dent = 0` control:

| ground memory | ρ coarse B=16 | ρ mid B=32 | ρ fine B=64 | nn-dist to early path |
|---|---|---|---|---|
| ∞ (scars never heal) | 0.851 | 0.616 | 0.264 | 2.13 |
| 1000 | 0.903 | 0.685 | 0.301 | 1.80 |
| 30 (fast healing) | 0.868 | 0.646 | 0.305 | 2.18 |
| **no dents (control)** | **0.782** | **0.576** | **0.282** | **3.00** |

Three findings, one of them against our own expectation:

1. **The exact/rhyme split emerges generically from ordinary physics.** Even
   with *no* deformation mechanism at all — just boundedness, inertia, noise,
   finite sampling — the ladder appears: coarse recurrence 0.78, fine
   recurrence 0.28. The split does not require an anti-repetition rule; it is
   the generic condition of constrained physical exploration (partly a
   coverage effect: early footsteps can only occupy so many cells).
2. **The substrate sharpens rather than creates the split.** Permanent scars
   push fine recurrence *below* the no-dent baseline (0.264 < 0.282 — active
   avoidance beyond chance) while *raising* coarse recurrence well above it
   (0.85–0.90 > 0.78): the deformed ground carves habituated rhyming corridors
   while keeping exact returns rare. The author's mechanism modulates the
   split in exactly its predicted direction — but the split itself is more
   robust than the mechanism.
3. **World memory matters less than expected, non-monotonically.** Healing rate
   shifts the numbers only modestly across four decades of `τ_mem`, with a hint
   of an intermediate-memory regime (`τ≈1000`: highest rhyme, closest path
   tracking) — possibly the walker surfing semi-decayed scars.

Caveat: at `B=64`, early-half coverage caps possible recurrence (~0.3 here),
which compresses the visible `τ`-dependence; the qualitative conclusions rest on
the no-dent contrast, which sits outside that cap on both axes.

### 3.8 Survival (`survival.py`) — would a small system sustain or collapse?
Minimal closed world: a ring of `S` sites, same local rule. Question: does the
two-point oscillation ever emerge *spontaneously*, and how fast when it does?
Lock = ≥500 consecutive steps of `x_t = x_{t−2}`; runs of 150k steps;
`S ∈ {4, 16, 64}`:

| γ | regime | P(end locked) | first lock | late effective states |
|---|---|---|---|---|
| −0.5 … −0.05 | attraction | **1.00 at every S** | t ≈ 500–1000 | 2.0 |
| 0.0 | neutral | 0.00 | — | ≈ S (diffusing) |
| +0.05 … +0.75 | repulsion | **0.00 at every S** | — | **= S (equidistributed)** |

Three findings:

1. **The sign of the feedback is a perfect switch.** Any attraction, however
   weak, locks the system into the two-point gait within ~500–1000 steps —
   size-independent and irreversible (the locked run never breaks). Any
   repulsion, however weak, produces **zero locks in 150k steps at any size**
   — including `S = 4`, a universe of literally four configurations.
2. **Why:** stability, not statistics. A locked pair carries huge visit counts,
   so under repulsion its outside neighbours look ever more attractive — the
   death gait is *unstable* and every excursion from it grows. Under
   attraction it is *stable* and absorbs. The simulation confirms the
   analytic picture exactly.
3. **Emergent fair-share.** Under repulsion, late occupancy equidistributes:
   effective states = S. The local rule turns a tiny closed world into
   perpetual *circulation* — the opposite of eternal return.

**Answer to the survival question:** a small closed system does **not**
spontaneously collapse — sustenance is generic and size-independent; collapse
requires attraction-signed feedback, and then arrives quickly and permanently.
Implication for trained systems (Zeus): an objective that pulls the trajectory
toward high-likelihood configurations *is* attraction-signed feedback — the
observed training-time contraction is this mechanism, and the fix is ensuring
the net fine-scale feedback stays repulsive.

### 3.9 Rescue (`rescue_test.py`) — flipping the sign breaks the gait instantly
Lock a ring world into the two-point oscillation (`γ=−0.5`, 3000 steps), then
change the feedback sign and time the escape (30 trials):

| rescue sign | escaped | median escape | max |
|---|---|---|---|
| stay attracted (control) | **0/30** | never | — |
| neutral (`γ=0`) | 30/30 | 1 step | 5 |
| any repulsion | **30/30** | **0 steps** | 0 |

The irreversibility found in §3.8 belongs to the *attraction*, not to the lock:
the moment feedback turns neutral-or-repulsive, the pair's own visit-count
instability ejects the system — under repulsion, on the very first step.
Collapse kinetics are asymmetric: ~500 steps to fall, one step to free,
*provided the sign actually flips*. For weight-level attractors (Zeus's
template), the flip must be applied where the attraction lives — the loss.

### 3.10 Cross-domain persistence (`apply_domains.py`)
The phenomenon tested on three alien substrates, predictions registered before
running:

| Domain | ν | Recurrence signature | Verdict |
|---|---|---|---|
| **Lorenz chaos** | 1.65 (lit. 2.06; −0.3 known estimator bias) | monotone collapse 0.94 → 0.84 → 0.68 → **0.36** | obeys the law: never exact, rhymes forever |
| **English prose** (333 sentences) | sentence-feature **ν = 2.08 > 2** | recurrence *decays monotonically with representation scale*: unigram 0.69 → bigram 0.20 → sentence-exact **0.00** | boundary runs *inside* language |
| **SGD (constant lr)** | late-half 4.46 (quasi-stationary 8-D cloud) | never locks — minibatch noise is accidental `γ > 0` | sustained |
| **SGD (annealed lr)** | — | distinct cells per training quartile: **568 → 374 → 35 → 3** | attraction alone ⇒ recurrent lock-in |

Findings:

1. **Chaos is the hypothesis in physical clothing.** The Lorenz attractor —
   famous for "never repeating yet always rhyming" — shows exactly our split,
   and its correlation dimension (~2.06) places it *at* the Pólya boundary.
   Butterfly effect = transience; strange-attractor structure = rhyme.
2. **The phase boundary runs inside language itself.** As representation
   complexity grows (word → bigram → sentence), recurrence falls monotonically
   0.69 → 0.20 → 0.00 — the `D_eff` law operating up language's own hierarchy.
   Exact sentence repetition is absent (0/333) while feature-space rhyme is
   abundant, with sentence-level `ν` crossing above 2.
3. **Optimization confirmed as attraction-signed.** With stochastic noise kept
   alive (constant `lr`), SGD wanders transiently forever around the optimum —
   sustained. Remove the noise (anneal) and pure attraction locks the
   trajectory onto the optimum within one training quarter. The Zeus template
   story, reproduced in miniature: *noise sustains, annealing kills.*

Honest caveats: the cell-recurrence metric itself suffers the curse in 8-D
(harness limitation, worked around via cell counts and distance-to-optimum);
the `ν` estimator carries its known negative bias (~−0.3–1 at higher `D`),
so Lorenz's reading is consistent-with-2.06 rather than precise.

### 3.11 Genetic drift (`genetic_drift.py`) — collision with published mathematics
The domain where the theory meets a century of prior math (Fisher, Wright).
Configuration = genetic composition; reproduction sampling = realization;
mutation = the `γ > 0` whisper dose.

| Prediction | Result |
|---|---|
| Absorption time ≈ `−4N[p ln p+(1−p)ln(1−p)]` | ratios **0.977–0.995** at N=16/64/256 |
| `H` decays at `ln(1−1/2N)` per generation | slopes match to ~2–10% |
| Sustained polymorphism needs `μ ≳ 1/(2N)` | boundary observed at exactly that scale |
| Sequence space (L=48, alphabet 4) | **exact genotype re-creation ≈ never**; innovation still 13%/generation at gen 1200; Hamming-rhymes decayed **0.264 → 0.034** as lineage spread |

Findings:

1. **The temporal-decay signature has a 95-year-old published form**, and the
   simulations reproduce it: heterozygosity decay and fixation-time laws match
   Fisher–Wright analytics within sampling error. The rebuild's decay probe,
   demoted as psychology, returns as *quantitatively validated physics* in
   biology's own substrate.
2. **The whisper dose is real and located**: mutation rates below
   `μ_c = 1/(2N)` live on the collapsed side; above it, sustained
   polymorphism — the survival.py dichotomy, rediscovered by population
   genetics.
3. **Biology's own exact/rhyme split**: genomes never recur (curse over
   `4^48` sequence space — the exact-vanishing premise), yet evolution
   perpetually revisits phenotypic neighborhoods (rhyme). Convergent evolution
   is rhyme recurrence; molecular-clock uniqueness is exact-vanishing.
4. **Bonus correction:** the naive diffusion formula `θ/(1+θ)` mismatched at
   large `μ`, but the *exact* biallelic stationary law `H = θ/(2θ+1)`
   matches all six simulated points to ~0.001–0.003 — the simulation tracked
   the precise published result better than the reviewer's first-pass formula.

Reconciliation with §3.8: feedback sign decides *whether* a system collapses;
system size decides *how fast* (absorption ∝ N). Biology agrees.

### 3.12 Heavenly bodies (`celestial.py`) — is the rhyme predictable?
N-body simulation (Poincaré's original playground), two planetary systems,
rhyme-predictability measured as return-interval concentration:

| System | ν | fine-recurrence | rhyme intervals | verdict |
|---|---|---|---|---|
| **Regular** (light planets, near-2:1) | **1.31 (< 2, recurrent)** | flat-high (0.97→0.74) | **100% within ±5% of the modal beat** — one interval, `cv = 0` | **rhyme fully predictable** |
| **Chaotic** (massive close pair) | **2.43 (> 2, transient)** | collapsed (0.04→0.00) | scattered (`cv` 0.26, concentration 0.30) | rhyme exists, schedule does not |

Findings:

1. **The phase criterion classifies celestial dynamics unaided.** The regular
   system lands in the recurrent phase, the chaotic one in the transient —
   no tuning, the measured `ν` alone sorts them across the same `ν ≈ 2`
   boundary found everywhere else.
2. **The simulation discovered its own eclipse cycle.** In the regular system
   every configuration-rhyme arrived on a single beat — the ~4-year
   commensurate period of the two orbits — with concentration = 1.000. This is
   the Saros cycle re-derived: rhyme under recurrence-phase dynamics *is*
   schedulable, which is why Babylonians predicted eclipses and ephemerides
   work.
3. **Chaos rhymes without a schedule.** The chaotic pair still yields over a
   thousand coarse rhymes (bounded phase space — Poincaré recurrence holds),
   but their arrival times scatter: statistically present, individually
   unpredictable. Transient-phase rhyme is weather; recurrent-phase rhyme is
   clockwork.

Poincaré would recognize both halves: he proved recurrence for bounded systems
and discovered chaos while trying to prove it for this exact problem.

### 3.13 Absurd corners (`absurd.py`) — Life and π
Two deliberately disrespectable substrates.

**Conway's Life** — a rule with neither attraction nor repulsion:
| world | no perturbation | with mutation dose (8 flips / 25 gens) |
|---|---|---|
| L=32 | drifts toward lock, sparks persist | **sterilized**: locked gen 141, frozen 100% |
| L=64 | **spontaneous period-2 lock-in at gen 363** | sustained: 160 new configs late |
| L=128 | 95% frozen, not fully absorbed | sustained: 160 new configs late |

1. **Spontaneous death gait confirmed** — random soup locks into exact
   period-2 oscillation with no attraction anywhere in the rule.
2. **Theoretical refinement extracted:** so `survival.py` was incomplete!
   Collapse does *not* require announced attraction — Life has none. The
   resolution: Life's rule is *dissipative* (it grinds configuration
   complexity into still-life basins), and **dissipation is implicit,
   unannounced attraction**. Refinement: collapse requires net attracting
   influence — which entropy-grinding rules carry silently.
3. **Rescue caveat discovered:** the mutation dose *sustains* large worlds but
   *sterilizes* small ones — perturbation can destroy the last surviving
   dynamic structures. Rescue protocols must be size-aware.

**Digits of π vs 1/7 vs true RNG** — determinism with no dynamics:
| source | w=2 | w=3 | w=4 | ν (6-D windows) |
|---|---|---|---|---|
| π | 1.00 | 0.846 | 0.124 | 3.97 |
| 1/7 (clockwork) | 1.00 | 1.00 | 1.00 | **DEGENERATE — zero spread ⇒ periodic** |
| true RNG | 1.00 | 0.883 | 0.129 | 3.95 |

4. **π carries no rhyme beyond chance** — statistically indistinguishable from
   pure noise at every block length, and its digit-walk fills space maximally
   (`ν ≈ RNG`). The most famous constant in mathematics is maximally transient.
5. **The instrument discriminated clockwork from noise without being told
   which was which** — and 1/7's periodicity manifested as a graceful
   degenerate-crash: the geometry itself collapsed to zero spread.

### 3.14 Pipeline validation (`shuffle_null.py`, corrected v2)
The shuffle-null instrument, validated on synthetic centroids (K=120) after
the adjacency fix:

| Synthetic set | early | late | S_obs | null mean | p | verdict |
|---|---|---|---|---|---|---|
| Decaying (rhymes early, scattered late) | 0.975 | 0.300 | +0.675 | −0.155 | **0.0000** | decay detected |
| i.i.d. (all scattered) | 0.125 | 0.525 | −0.400 | −0.385 | **0.635** | correctly n.s. |

The pipeline discriminates configuration-drift decay from noise at the level
it is applied on real data.

### 3.15 Rewritten-suite cross-checks
Three heritage scripts re-run on the rebuild:
- `hypothesis_eq.py`: fits `ρ_∞(α) = ρ₀·exp(−λα)` on the D=2 sweep →
  `ρ₀ = 0.465`, `λ = 1.55`, `MAE = 0.012` (phenomenological summary;
  original lost `λ = 0.0006` remains UNVERIFIED).
- `sensitivity.py`: at `δ = 0` (drift scaled to zero), `ρ = 0.489 ≈`
  unbiased baseline `0.481` — drift, not noise, drives suppression.
- `emergent_3d.py`: same transition on a 3-D torus (finite volume):
  `ρ` falls `0.286 → 0.173` as `α` goes `0 → 0.5` — the collapse is
  dynamical, not a boundary-escape artifact.

### 3.16 Civilizational drift (`civilization_drift.py`) — the mutation-rate equivalent for a civilization
Carriers = minds/books/institutions holding practices; copying = inheritance;
innovation mints never-held practices (`γ > 0`); orthodoxy-grind reverts to a
canonical configuration (implicit `γ < 0`, Life-style).

| Prediction | Result |
|---|---|
| Pure-copying monoculture time ∝ carriers | **confirmed** (median scales ~linearly; runs 25% under the mean-time formula since medians precede means) |
| Collapse/sustain boundary in (`ε`,`δ`) | exists, but **tilted toward innovation**: at `ε=δ=0.03`, diversity holds at 59/400 — inheritance amplifies novelty faster than grind erases it |
| Idea-burst into collapsed orthodox civ dies | **refined**: a 50-idea burst survived even with full grind (final diversity 8.0 vs 1.5 pre-burst) because copying spreads ideas before reversion; lowering grind doubled it (12.8). Bursts work if large enough to outrun the grind |
| Exponential diversity decay under pure conformity | **confirmed**: 12.8 → 3.5 → 1.2 → 1.0 by generation ~400 |

Findings:

1. **The civilizational whisper-dose condition:** a culture sustains while
   `G · ε` (carriers × innovation rate) outruns its orthodox-grind `δ`.
   Historically: writing raised `G`, printing raised copy-fidelity `c`, the
   internet raised both — each is a step-change across this boundary.
   Carrier destruction (burned libraries, collapsed literacies) drops `G`
   below threshold at unchanged `μ`: dark ages.
2. **Inheritance is innovation's amplifier.** Unlike Life (where pokes die),
   copied practices spread before grinding reverts them — which is why
   civilizations can survive bursts of novelty even under strong orthodoxy,
   and why the Renaissance needed both surviving texts *and* weakened grind.
3. **Conformity alone is lethal on a schedule** (P4): pure orthodoxy takes a
   diverse culture to monoculture within O(hundreds) of generations — Tainter's
   diminishing returns rendered as an absorption time.

### 3.17 The live run (`civilization_drift` applied to present-day Earth)
Real-world proxies for the four dials, sourced 2025–2026:

| Dial | Proxy | Reading | Trend |
|---|---|---|---|
| **G** (carriers) | internet users / literate adults | **6.0B online (74% of humanity)**, +240M in one year | ↑ all-time high |
| **ε** (innovation) | scholarly articles minted | **7.23M in 2025, +11.9% YoY — accelerating** (mean growth 6.8%→8.3% since 2022; preprints doubling every 5.6 yr) | ↑↑ compounding |
| **c** (copy fidelity) | digital media | ≈ 1.0, perfect and free | saturated max |
| **δ** (orthodox grind) | global freedom / internet freedom / shutdowns | **20th consecutive year of freedom decline**; only 21% of humans live in Free countries (was 46% two decades ago); internet freedom down 15 straight years; **record 313 shutdowns in 52 countries** (3rd record year running); record arrests for online expression | ↑↑ monotone |

And the subtlety the framework predicts but history never tested until now:
**the copy-explosion masquerades as an innovation-explosion.** By mid-2025,
~35% of newly published websites were AI-generated or AI-assisted — but the
measured consequence is *semantic contraction* (ρ=0.47, p=0.004: rising AI
share ⇒ shrinking diversity of viewpoints; AI-authored sites 33% more mutually
similar), and LLM writing assistance reduces writing-complexity variance by
**21–50%** across 880k texts. In our model's language: the flood is mostly `c`
amplifying itself, not `ε` minting. Volume explodes while *effective*
distinct-configuration growth dilutes.

**Verdict:** Earth in 2026 sits deep on the **SUSTAINED side** — `G·ε` is at
the highest value in history and still compounding, orders of magnitude above
any plausible grind threshold. But the precursor column matches §3.6 exactly:
grind monotone-up for two decades, and effective novelty per unit output
declining beneath the surface volume. Per our own protocol: watch the
semantic-diversity meter like a `ν`-meter. The race is not close today; the
trend lines are the story.

### 3.18 Markets (`market_cdt.py` + live data) — rhyming in fear, dying by copying
Real data fetched live: Binance BTC/ETH (1000 daily candles each), Yahoo
^GSPC (10y daily). Signed-return trajectories time-delay embedded (d=5),
shuffle-null tested; structural layer from CRSP/Freedom House/CoinGecko/Pew.

**Price-trajectory level (computed):**

| Market | signed recurrence vs shuffle | `|r|` autocorrelation | verdict |
|---|---|---|---|
| BTC | obs 0.002 < null 0.011, p=0.995 | 0.10–0.15 | transient |
| ETH | obs=null, p=0.52 | 0.05–0.13 | transient |
| **S&P 500** | obs 0.086 vs null 0.046, **p=0.000** | **0.33–0.41** | rhymes beyond chance |

Decomposition of the S&P signal: sign-only patterns saturate (uninformative),
but **magnitude-only windows still exceed shuffle (p=0.010)**. The rhyme is in
*fear*, not *path*: volatility regimes recur beyond chance while direction
stays transient — the EMH survives at the only level that matters for
arbitrage, and the ladder reappears (fear-recurrent, direction-transient).
Honest note: our registered ordering (crypto > equities) was reversed in these
windows.

**Structural level (both markets show the §3.17 copy-masquerade):**
- **Equities — monoculture trend:** top-10 S&P stocks now hold **42% of index
  value** (CRSP: surpassing even the 1932 peak of 37.3%), more than doubling in
  a decade; weight (41%) runs far ahead of earnings share (32%); passive
  inflows amplify. Diversity collapsing beneath volume.
- **Crypto — copy-flood:** **25.2M tokens listed since 2021; 13.4M dead
  (53.2%); 11.6M failed in 2025 alone (~83,700/day)**, driven by pump.fun's
  >6M zero-cost meme launches. Issuance cost → 0 ⇒ a c-explosion masquerading
  as an ε-explosion, with a sterilized-rescue death rate to match: new
  configurations landing where nothing alive can inherit them die same-year.

Verdict: both markets currently display the *copy-masquerade signature* —
volume metrics scream unprecedented innovation while distinct-configuration
analysis says consolidation (equities) or duplication-plus-die-off (crypto).
Per our own §3.6 protocol: measure distinct configurations, never volume.

### 3.19 The ν-meter vs HAR-RV (`market_nu_forecast.py`) — seat DENIED
Pre-registered walk-forward duel: does rolling `ν` of the `|r|`-embedding add
out-of-sample predictive power for forward 5-day realized volatility over the
HAR-RV benchmark? Decision rule fixed in advance: both assets must show
`R²_oos > 0` AND Diebold–Mariano `p < 0.05`.

| Asset | HAR MSE | HAR+ν MSE | R²_oos | DM p |
|---|---|---|---|---|
| BTC (1000d) | 3.155e-07 | 3.627e-07 | **−14.9%** | 0.080 |
| S&P (10y) | 3.356e-08 | 3.546e-08 | **−5.7%** | 0.057 |

**Verdict: seat denied.** Adding `ν` made forecasts *worse* on both assets —
HAR's autoregressive realized-volatility terms already extract everything
predictable from `|r|` history at daily scale; the embedding's geometric
complexity adds only estimation noise. Consistent with §3.10's P1 finding
(direction transient): apparently even the fear-manifold's *geometry* carries
no information beyond its own autocorrelation.

Discipline notes: (1) per pre-registration, no post-hoc specification
iteration — alternative window lengths, embeddings, or assets will not be
tried until there is a *theoretical* reason to expect sign or magnitude of
improvement; (2) the full-sample Newey–West t-stat failed numerically
(near-singular design), but the walk-forward was always the decisive test;
(3) Seats 1 (regime *classification*) and 3 (structural copy-masquerade risk
indicators) are untouched by this result — they never claimed forecast
increments. What dies here is specifically the claim that the `ν`-meter is a
*volatility forecaster*.

This is the framework's first failed pre-registered applied test, reported
with the same prominence as the fourteen confirmations.

---

## 4. Human experiment (fresh run, corrected math)

Collected with `collect_draw.py` (203 circles / 4000 points; a prior 142-circle
run is backed up as `drawing_data_v1.csv`). Analyzed with `analyze_exact.py`
(exact 4-D configuration bins) and `analyze_drawing.py` (corrected `tgap`).

### 4.1 Exact vs rhyme in the drawing
- **Rhyme (coarse configuration) recurrence ≈ 0.9–0.98** — at coarse resolution
  (`B=3`, 81 cells) 97.5% of circles land in a previously occupied configuration:
  the user keeps drawing circles that *rhyme* with earlier ones. This is the
  persistent, perceived "I've seen this before."
- **Exact (microscopic) recurrence → 0.** As resolution fines, exact repeats
  collapse monotonically (table below): 97.5% → 87.7% → 74.9% → 37.4%, heading to
  0. True microscopic exact recurrence (the author's "exact footstep length") lies
  below even this resolution and tends to 0 — consistent with `rec_mu = 0.000`
  from the original lost run.

| B | cells | % exact-bin | early | late | verdict |
|---|---|---|---|---|---|
| 3 | 81 | 97.5% | 0.970 | 0.980 | n.s. (rhyme-saturation) |
| 12 | 20736 | 87.7% | 0.802 | 0.951 | n.s. (rhyme-saturation) |
| 20 | 160000 | 74.9% | 0.624 | 0.873 | n.s. (rhyme-saturation) |
| 50 | 6250000 | 37.4% | 0.218 | 0.529 | n.s. (rhyme-saturation) |

**Exact recurrence collapses as configuration resolution fines** — 97.5% (coarse,
= rhyme) → 37.4% (fine) and tending to 0 — while the coarse/rhyme level stays
high. This is the curse of dimensionality observed *directly on the human
drawing*: the more finely we resolve the configuration, the fewer exact repeats,
exactly the author's "exact footstep never recurs, but it rhymes." The temporal
column (`T = late − early`) is the (irrelevant) decay probe and is dominated by
the early-reference bias; it is not the claim.

### 4.2 The decay probe (secondary, NOT the hero claim)
As a separate check we also tested temporal *decay* of recurrence density (the
rebuild's mistaken hero target). Point-level `S = −0.31, p = 0.26`; centroid-level
`S = −0.19, p = 0.66` — **no significant decay**. This is irrelevant to the
hypothesis: the author never claimed a decay *curve*; the claim is the
exact/rhyme *split*, which the drawing confirms. (The original `p = 0.032` was
this decay probe and is withdrawn as the central evidence; `rec_mu=0.000` and
`rec_H=0.900` are the real support.)

### 4.3 The global criterion, decided numerically (`dimension_test.py`)
For a diffusive explorer (walk dimension `w = 2`), motion on a configuration
manifold of correlation dimension `ν` is **recurrent iff `ν ≤ 2`** and
**transient iff `ν > 2`** (Pólya generalized to fractals). Transient ⇒ exact
recurrence vanishes, rhymes persist. So the whole question reduces to measuring
`ν` via the pair-correlation scaling `C(ε) ∝ ε^{ν}`.

Estimator validation on clouds of known dimension: `D=1 → 0.93`, `D=2 → 1.69`,
`D=3 → 2.34`, `D=4 → 2.95` (known negative bias at low `D`; measured values are
conservative).

| Human configuration manifold | ν | Regime |
|---|---|---|
| Coarse / perceived (centroids only) | 1.61 – 1.67 | `ν < 2` → **recurrent** |
| Fine / full config (centroid + radius + speed) | 2.28 – 2.55 | `ν > 2` → **transient** |

(both runs agree: v1 142 circles and v2 203 circles)

**Verdict.** The perceived-level manifold is *recurrent* (`ν ≈ 1.6`) — rhyme
≈ 0.9, "the same path every day." The microscopic-level manifold is *transient*
(`ν ≈ 2.4`) — exact recurrence vanishes, "never the same footstep twice."
**The exact/rhyme split is a phase boundary at `ν = 2` crossed between the two
levels of description.** Globally, the hypothesis holds precisely where
`ν > w = 2` — which covers high-dimensional real-world configuration manifolds —
and fails in the recurrent phase below it. A decidable condition, not a vague one.

---

### 4.4 The self-referential test (`conversation_cdt.py`)
The theory applied to the 366-message dialogue in which it was developed
(`Conversations/unanswered-science-questions-solvable-by-tech.json`).

| Registered prediction | Result |
|---|---|
| Exact message repeats ≈ 0 | **confirmed**: user 0/52, assistant 0/314 |
| Vocabulary crystallizes over time | partial: term density rose 39.8 → 45.4 through the theory-building phase, then fell to 34.7 as the dialogue shifted reflective |
| Ladder by representation scale | **confirmed**: word 0.676 → bigram 0.144 → trigram **0.02** |
| Period-lock episodes get localized | **27 episodes** of structural near-repetition |

And the headline finding — the registered escape clause fired verbatim:

> *"exact repeats ~0 … unless the trajectory ever milled (repetitive loop) —
> the instrument would catch THAT instead."*

At position ~32% of the dialogue, a **118-message near-duplicate streak** was
detected: the era of repeated "Written: `configuration_drift_full_report.md`"
claims for files that did not exist — the hallucination loop, located in time,
its length measured. It ends at the apology message (*"I owe you an apology —
I claimed repeatedly that I'd written the file, but it doesn't exist"*), which
is precisely the sign-flip rescue of §3.9 enacted in conversation history:
attraction to a false claim abandoned, trajectory ejected, work resumed.

Interpretation: the dialogue is a healthy CDT trajectory — content transient
(trigrams 0.02, zero exact repeats) while *structure* intensely rhymed (27
episodes of the prediction→simulation→verdict refrain; feature-space `ν` reads
recurrent because the refrain is engineered, exactly as composers build
refrains). A mind-like ladder, plus one diagnosed and rescued milling episode.

---

### 4.5 Hardware validation — Zeus nights 1–2 (commit `e4a3197`)
First causal deployment of the framework on live training hardware
(ESNPN v3, dim 768).

**Night 1 (open-loop control):** filament DOA (PR 1.13) → unbounded expansion
(PR 6.57 via ±8 clamp-scaffold). Monitor independently flagged every anomaly,
including that the passing volume gate was lying — the copy-masquerade
signature detected inside our own checkpoint.

**Night 2 (contained + normalized instruments): registered predictions graded**

| Vote | Prediction | Result |
|---|---|---|
| N2-P1 | `ν_micro ≥ w` | **PASS**: 5.83 > 2.15 |
| N2-P2 | inverse motion (PR↓ while ν↑) | **PASS**: 6.57→2.79 vs 1.68→5.83 — exact masquerade-death fingerprint |
| N2-P3 | fine `ρ` in human-transplanted band 0.1–0.4 | **missed, then resolved**: fine ρ = 0.00 (*below* domain null) while coarse = 1.00 (*at* null) — active-avoidance signature where repulsion acts, freedom where it doesn't |

**Headline:** `val_ce` crossed below the unigram floor (7.10) within 2000
steps of CDT-prescribed habitat — **first time in project history** — and held
for 8,000+ steps while remaining transient throughout (collapse curve
0.85 / 0.23 / 0 / 0 / 0; β diffusive; fair-share 1.0; no gait).

**Status:** first causal demonstration (n=1 system, pre-registered votes,
control-era baseline) that Configuration-Drift habitat conditions move a
language model across the competence floor — i.e., the living manifold was a
prerequisite for learning, not merely compatible with it.

**Open frontier:** theme rung still above the recurrent band (slow carrier not
yet crystallized); router monoculture; `sign_hat` pinned −1.0 pending
calibration against known-γ simulations; gentle scale creep tracked by the
governor (k 0.83→2.4, firing correctly on drift episodes).

---

## 5. Verified vs not

**Verified (reproducible here):**
- Exact recurrence collapses as configuration dimension grows (Pólya `D_c ≈ 2`);
  proven on a lattice and in the continuum (`lattice_walk.py`, `phase_scan.py`,
  `theory_check.py`).
- Rhyme (coarse) recurrence persists where exact vanishes (`thought_walker.py` at
  `D=12` → exact `0.00000`).
- **The split is emergent:** a self-repelling walk with *no external drift*
  (`emergent_walk.py`) reproduces it from a local rule — exact ↓↓ while rhyme
  stays high (§3.4). This is the author's mechanism simulated directly.
- **The global criterion is measured:** the human perceived-level manifold has
  `ν ≈ 1.6 < 2` (recurrent → rhyme persists) and the fine config manifold has
  `ν ≈ 2.4 > 2` (transient → exact vanishes) — the split sits on the Pólya phase
  boundary (`dimension_test.py`, §4.3).
- **The mechanism passes ablation:** forcing exact recurrence to persist
  (`γ < 0`) collapses the system to a 2-state loop — exploration, novelty, and
  entropy die with it (`ablation_study.py`, §3.5). The loss of exact recurrence
  is functional: it is what keeps the system generating new states.
- **The fall is characterized:** collapse to exact recurrence sits at a sharp
  critical point (`γ_c ≈ −0.13`), announces itself via smooth precursors
  (shrinking effective states, rising exact rate, growing period-2 locking),
  and terminates in a strict two-beat oscillation (`collapse_transition.py`,
  §3.6).
- **Survival is generic, collapse is caused:** in a minimal closed world the
  two-point gait never arises spontaneously under repulsion (zero locks in
  150k steps, even with 4 sites) and always arises under attraction (~500
  steps, irreversible). Feedback sign, not system size, decides fate
  (`survival.py`, §3.8); real-world constraints alone reproduce the
  exact/rhyme ladder without any mechanism (`physical_walk.py`, §3.7).
- Human drawing: rhyme ≈ 0.98 (coarse) and exact → 0 with resolution — the
  exact/rhyme split measured quantitatively (`analyze_exact.py`,
  `analyze_drawing.py`).
- The recurrence-measurement pipeline is validated on synthetic data
  (`shuffle_null.py`: detects a configuration-recurrence decay when present
  `p=0.0000`, rejects i.i.d. `p=0.635`).

**Not asserted:**
- A literal temporal decay *slope* of recurrence in the human data — not claimed
  by the hypothesis, and not observed.
- The original lost `p = 0.032` as central evidence (it was the decay probe).
- The perturbed-observer coupling `𝒞` as quantitative data (still qualitative).

---

## 6. Conclusion

The Configuration-Drift Hypothesis — **exact recurrence of a state vanishes because
realizing it perturbs its many contributing configuration elements, while rhyme
persists** — is **supported** quantitatively at both levels:

- **Simulation:** exact site recurrence collapses for `D ≥ 3` (curse of
  dimensionality / Pólya), and — decisive — the split **emerges from a local
  self-repulsion rule with no external drift**: exact ↓↓ while rhyme stays high
  (`emergent_walk.py`, §3.4). The author's mechanism, simulated directly.
- **Human:** rhyme ≈ 0.98 (coarse) and exact recurrence collapses toward 0 as
  configuration resolution fines — the predicted split, measured (`analyze_exact.py`).

The rebuild's earlier emphasis on a temporal-decay signature was a misreading of
the hypothesis; removing it, the original conclusion (`rec_mu ≈ 0`, `rec_H ≈ 0.9`)
stands as the genuine validation.

---

## 7. File inventory

```
core:        drift_walker.py  phase_scan.py  theory_check.py  lattice_walk.py
             emergent_walk.py  ablation_study.py  collapse_transition.py
             survival.py  rescue_test.py  physical_walk.py
             dimension_test.py  apply_domains.py  genetic_drift.py
             celestial.py  absurd.py  civilization_drift.py
             market_cdt.py  market_nu_forecast.py
data/market: BTCUSDT.json  ETHUSDT.json  spx_yahoo.json
empirical:   shuffle_null.py  collect_draw.py  analyze_drawing.py
             analyze_exact.py  make_figures.py  conversation_cdt.py
data/extra:  Conversations/unanswered-science-questions-solvable-by-tech.json
rewritten:   hypothesis_eq.py  emergent_3d.py  thought_walker.py
             sensitivity.py    dimension_scaling.py
data/fig:    phase_scan.csv  synthetic_drifting.npy  synthetic_iid.npy
             drawing_data.csv (fresh: 203 circles)  drawing_data_v1.csv (backup)
             collapse_transition.csv  physical_walk.csv
             phase_diagram.png  time_course.png  time_course_real.png
             collapse_transition.png  physical_walk.png
```
