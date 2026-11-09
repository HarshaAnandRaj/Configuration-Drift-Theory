# Configuration Drift: phenomena and use cases

This guide applies the [canonical mathematics](../configuration_drift_theorem.md).
It distinguishes **proved model phenomena**, **proposed engineering uses**, and
**observations that do not identify the proposed mechanism**. These are
operational descriptions, not claims of newly discovered natural laws.

The useful question is: **which changes in full state can be tolerated while
the structure needed for a task keeps returning reliably?** Recurrence alone
cannot decide whether that structure is meaningful or whether a task succeeds.

**Experiment status:** the proposed model tests have now been run. See the
[completion ledger](experiment_completion_20261109.md),
[twelve-suite results](../results/application_20261109/evidence_ledger.md), and
[remaining-phenomena follow-up](../results/phenomena_followup_20261109/evidence_ledger.md).
One memory replicate failed the registered functional checks. Neither supplied
drawing returned to its first-stroke anchor at the registered structural radius.
Real-world application benefits and the asymptotic mechanism remain unproved.

## 1. Phenomena that can be defined precisely

Let $X$ be the full process, $Y=\pi(X)$ a fixed structural representation,
$A$ a fine target, and $B$ a structural target. Keep scales and observation
times fixed unless a joint limit is explicitly specified.

| Phenomenon | Operational definition | Mathematical standing |
|---|---|---|
| Escape with recurring structure | Fine visits eventually stop, structural visits continue indefinitely. | Theorem 1 under its countable-chain assumptions; Proposition 3 for its Brownian model. |
| Sparse structural recurrence | Infinitely many structural visits, but their time fraction tends to zero. | Null recurrence; the one-/two-coordinate free-walk projections are exact examples. |
| Structural recurrence at a positive rate | Fine visits are finite and structural visit fraction tends to a positive value. | Corollary 1a; the restoring birth–death example has rate $1/3$. |
| Drift leaking into structure | A nuisance drift gains a nonzero projected component, eventually suppressing structural returns. | Exact in the Gaussian model; cutoff scale derived in §6 of the theorem. |
| Long fine-return tails | The last fine return is finite almost surely, but its mean time is infinite. | Exact last-exit law; lazy product walks in dimensions three and four. |
| Apparent novelty from bookkeeping | Exact repetition disappears after adding a clock, cumulative local-time field, or irrelevant identifier. | A representation artifact; no position-avoidance or functional conclusion follows. |
| Recurrence without functional preservation | A representation returns, but its associated task performance deteriorates. | A possible measured failure, not a contradiction of the recurrence theorem. |

These describe different outcomes. A rare return after a very long gap does
not provide a dependable memory refresh or control cycle. A stable fixed point
can be correct for one task and a failure for another. Function must determine
which recurrence pattern is desirable.

### A worked contrast with exact predictions

Take $X=(Y,Z)$, with $Z$ independently moving by $+1,-1,0$ with probabilities
$3/8,1/8,1/2$. Its mean displacement is $1/4$ per step, so every fixed full
state is transient. Set $A=\{(0,0)\}$, $\pi(y,z)=y$, $B=\{0\}$.

| Structural dynamics $Y$ | Anchored fine visits | Structural visits | Limiting structural fraction |
|---|---|---|---|
| Restoring birth–death chain, $p=1/2,q=1/4$ | finite almost surely | infinitely many | $1/3$ |
| Free lazy symmetric walk | finite almost surely | infinitely many | $0$ |
| Lazy biased walk with mean $1/4$ | finite almost surely | finitely many | $0$ |

The first two satisfy the original split, but only the first gives a positive
return rate. The second and third have the same limiting fraction, but differ
in whether returns eventually stop. Thus neither a single finite rate estimate
nor the original split alone is a complete operational diagnostic.
Both coordinate counts remain unchanged across the three models; their
dynamics, rather than ambient dimension alone, determine these differences.

Run the illustrative benchmark:

```bash
python examples/cdt_use_case_demo.py --steps 8192 --paths 128 --seed 20261109
```

It reports finite counts, tail-window rates, and longest observed structural
gaps beside the analytic classifications. It is a model illustration, not a
preregistered application study or proof of self-repulsion.

For the command above (NumPy `2.3.5`, seed `20261109`, 128 independent paths
per arm):

| Structural law | Mean structural fraction, steps 1–8192 | Mean structural fraction, steps 4097–8192 | Mean longest miss run, steps 1–8192 |
|---|---:|---:|---:|
| Restoring | 0.33249 | 0.33387 | 78.75 steps |
| Free symmetric | 0.01192 | 0.00611 | 5375.77 steps |
| Visible drift | 0.00045 | 0.00000 | 8182.79 steps |

These are descriptive sample means, not confidence bounds. In particular,
zero observed tail returns in the third arm do not prove transience; its
nonzero drift proves that independently. The first arm also shows why a mean
return time of three steps is not a three-step deadline guarantee.

## 2. Five proposed use cases

These are experiment designs. No real-world benefit in this table is claimed
as established by the repository's current simulations.
Their controlled-model outcomes and concrete deployment blockers are recorded
in the linked completion ledger; these designs are retained to make the
tested hypotheses and their limits explicit.

| Use case | Full state and proposed structure | Decision the analysis could support | Independent outcome |
|---|---|---|---|
| Recurrent neural systems | Hidden activations and relevant adaptation state; a fixed task-state decoder. | Distinguish harmless hidden variation from loss of task-state revisitation. | Held-out prediction/control loss, recall, and latency. |
| Memory retrieval | Context-dependent representations; a task-validated content map. | Retain recognizable content while tolerating changing context. | Retrieval accuracy, false matches, interference, and storage cost. |
| Locomotion and repetitive control | Position, joint state, contacts, loads; phase-relative gait features. | Detect disruption of a required cycle without alarming on forward motion alone. | Tracking error, falls, energy, and deadline misses. |
| Sensors under nuisance drift | Raw multichannel measurements; independently calibrated physical features. | Separate changes in calibration/context from changes in the measured phenomenon. | Error against external reference measurements and alarm performance. |
| Repeated gestures or drawing | Measured position, velocity, pressure; registered shape/gesture features. | Quantify repeated form alongside trial-level variation. | Shape recognition, execution error, or another declared behavioral task. |

### 2.1 Recurrent neural systems: a diagnostic for useful state revisitation

**Question.** Does an autonomous hidden trajectory preserve task-relevant
states while its other components vary, or is novelty masking a loss of function?

Use hidden activations plus genuinely relevant controller/adaptation variables
as the full state. Freeze a decoder $\pi$ trained on separate data to identify
task states; select structural targets from those states before evaluation.
Report several targets, their coverage, and confusion between distinct labels,
rather than recurrence to one convenient label.

**Experiment.** Compare the unchanged system, a perturbation restricted to
task-irrelevant directions, and an equally scaled perturbation in task-relevant
directions. If the decoder is differentiable, directions in its local Jacobian
kernel are only a *local approximation* to hidden nuisance directions: verify
finite perturbations on held-out data. Separately compare any learned adaptive
controller against fixed-dimensional and no-adaptation controls under matched
training/data and declared resource budgets.

**Success.** Registered structural counts and return-gap targets are met while
held-out task loss remains within its specified tolerance. Adaptive dimension
must be selected by the learner if that is the claimed mechanism; an external
gain schedule is a different intervention.

**Failure.** Distances and novelty rise but task performance falls, a constant
decoder passes the recurrence score, or teacher forcing supplies the recurrence
that was attributed to autonomous dynamics. Measure forced and free-run
windows separately, and evaluate the functional claim on the relevant windows.

**Scope.** Finite-precision networks have finite machine states. Bounded noisy
models can also be positive recurrent at finite resolution. The infinite-space
transience theorem is not an automatic model of an RNN; use finite-horizon
contracts unless its assumptions have actually been established. The existing
`adaptive_dim_demo.py` and `alive_reward_demo.py` are related exploratory toys,
subject to the [measurement-repair limits](../measurement_repair_20260912.md).

### 2.2 Memory retrieval: preserve content across changing contexts

**Question.** Can a memory be recognized after its raw context or encoding has
changed, without confusing it with a different memory?

Define $X$ as the measured encoding plus relevant context, and $\pi(X)$ as
a content representation justified by held-out labels or task outcomes. Choose
positive pairs sharing content and negative pairs differing in content before
measuring recurrence. Exact equality of floating-point embeddings is not a
meaningful fine target; declare a resolution or use registered neighborhoods.

**Experiment.** Revisit the same content under held-out context changes.
Compare raw retrieval, the fixed structural map, a constant map, and a
dimension-matched random or task-uninformed map. Match cue schedules and
storage/compute budgets. If the encoder changes during learning, use a fixed
evaluation map or a predeclared alignment protocol fitted without test outcomes.

**Success.** Context changes reduce raw matching while structural retrieval
preserves positive-pair recall **and** rejects negative pairs, with acceptable
latency and interference. Improving recurrence by merging all items fails.

**Scope.** Repeated external cues create opportunities for recurrence; they do
not establish spontaneous structural recurrence. This is a representation and
retrieval experiment unless an autonomous recurrence law is separately proved.

### 2.3 Locomotion: a recurring gait while position changes

**Question.** Can a controller maintain required gait phases while the robot
moves through changing physical configurations?

Use measured world position, joint states, contacts, and loads as $X$. Let
$\pi$ remove justified global-position nuisance variables and retain
phase-relative geometry and contact structure. A target might be a physically
defined contact phase; it must distinguish phases relevant to successful gait.

**Experiment.** Compare changes in world position or coordinate origin with
perturbations of contact timing, payload, or joint coordination. Use the same
route and disturbance schedule across controllers. Measure longest phase gaps
and transition order as well as visit counts: visiting phases in the wrong
sequence can still satisfy a recurrence count.

**Success.** The required cycle recurs within timing limits while tracking,
energy, and fall rates meet task thresholds. Mere oscillation is insufficient.

**Scope.** A physical forward displacement is a causally meaningful changing
state, unlike an appended timestamp. Nevertheless, gait cycles are often
controlled or deterministic; neither Markov lumpability nor the Brownian law
is assumed for the robot. The theorem motivates a diagnostic, not a stability
or safety proof for that controller.

### 2.4 Sensors: nuisance change versus change in the phenomenon

**Question.** Is a shift in raw measurements due to irrelevant calibration or
environmental factors, or to a change in the quantity being monitored?

Choose $X$ as raw observations and declared calibration/context variables.
Build $\pi$ using separate calibration data and a physical reference, rather
than selecting features because they look recurrent. Repeated known reference
conditions define the structural targets.

**Experiment.** Vary nuisance conditions while holding the measured quantity
fixed; then vary the measured quantity while holding nuisance conditions fixed.
Blind the evaluation to those intervention labels until the map is frozen.
Check that the map rejects nuisance variation without suppressing true changes.

**Success.** Reference-condition recognition survives nuisance interventions,
while sensitivity to actual changes and external-reference accuracy remain
within declared tolerances. A map that always emits “normal” fails.

**Scope.** Changes in sensor output alone do not identify a Markov full state.
This is an empirical invariance hypothesis. The hidden/visible-drift theorem
is a solvable control model, not an established law of sensor degradation.

### 2.5 Gestures and drawing: recurring form with trial variation

**Question.** Which aspects of a repeated action are stable, and which vary
from execution to execution?

Use only measured variables—such as position, velocity, and pressure—as $X$.
Do not call this the complete microscopic physical state. Define $\pi$ as
registered shape features, removing translation, rotation, timing, or scale
only when the task regards those differences as irrelevant.

**Experiment.** Compare repeated instances of a gesture with different
gestures, matched iid samples, and order-randomized controls. Use a lag to
exclude adjacent samples on a continuous stroke. Include velocity/pressure
or temporal-order controls so that a shape map cannot hide a different action.

**Success.** Same-gesture structural matches remain discriminative on held-out
trials despite fine-scale variation. A sparse raw match rate alone is expected
for many continuous distributions and is not supporting evidence.

**Scope.** This may establish repeatable form with variable execution. It
does not establish a universal physical self-repulsion law, consciousness,
or a particular explanation of familiarity.

## 3. What to register for an application

Specify the window $[t_0,T]$, fine and structural targets, resolution, allowed
fine-return count, required structural count/rate, maximum permitted return
gap, and independent task threshold. Choose these from application needs,
not by maximizing separation after the run. Then:

1. Validate that the representation preserves task distinctions on held-out
   positive and negative examples. Check more than a single label.
2. Use independent restarts or independent experimental units for path-level
   probabilities; keep paired comparisons paired. Visits on one path are
   not independent Bernoulli trials.
3. Compare full counts, structural counts, window occupancy, and gaps. Report
   whether a repeated cue or controller externally imposed the recurrence.
4. Use matched nuisance and structure-changing interventions to test the
   proposed causal explanation. Register multiplicity handling for multiple
   targets or use a separate confirmatory evaluation set.
5. Evaluate task performance under the same relevant operating conditions.
   A successful recurrence diagnostic with failed function is a failed use case.

If a reference structural kernel is only approximate, Proposition 5 bounds
window-level errors by accumulated conditional total-variation error. Small
estimated one-step error is not a guarantee of long-run recurrence. Time-varying
maps require their own error/alignment analysis.

## 4. Cases where the framework should decline a stronger claim

| Observation | Why it does not establish the intended use |
|---|---|
| Every continuous vector is unique | Uniqueness may hold for iid samples with no drift or interaction. |
| A finite label repeats | Finite irreducible structural chains recur automatically; semantics and function remain to be tested. |
| A finite equilibrium model changes microstates | Fine cells also recur in finite irreducible equilibrium models; use mixing, return times, and finite windows. |
| A price pattern appears again | A post-selected feature map, market nonstationarity, and costs can defeat the inference; no trading advantage is proved. |
| An RNN explores more hidden cells | Exploration may be driven by inputs, noise, or task-irrelevant dimensions and can worsen task loss. |
| A controller escapes a loop | Escape alone does not show the controller can sustain operation within constraints. |
| Human behavior or thoughts “rhyme” | Without a measured state, predeclared map, and discriminative task, this remains an analogy. |

The most direct next application is a controlled neural-state or memory
experiment with a frozen task map, matched nuisance/structure interventions,
return-gap measurements, and held-out functional evaluation. Those measurements
can test an engineering claim without pretending to resolve the open
self-repulsion theorem.
