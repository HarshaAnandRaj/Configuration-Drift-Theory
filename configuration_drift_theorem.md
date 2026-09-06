# The Configuration-Drift Theorem

**Canonical mathematical statement, limits, and use protocol**  
**Author:** Harsha Anand Raj Pammi  
**Mathematical reconstruction:** 2026-09-04  
**Registered simulation audit:** 2026-09-05

This file is the authoritative theorem layer for the Configuration-Drift Theory
(CDT). The longer `configuration_drift_theory.md` remains the research notebook
and empirical history. Whenever the two disagree, use this file.

The durable insight in CDT is real, but narrower than the earlier formula

```text
Alive iff (d_s <= 2) and (gamma > 0).
```

That formula is not a theorem. The mathematically valid core is a separation
between recurrence in a full configuration space and recurrence after a
predeclared coarse-graining. The separation is controlled by Green kernels and
capacities. Spectral dimensions give a convenient corollary only when suitable
heat-kernel estimates hold.

---

## 1. Three observables that must not be conflated

Let \((X_n)_{n\geq 0}\) be a stochastic process in a metric state space
\((E,d_E)\). These are different questions.

1. **Anchored recurrence:** does \(X_n\) return to a fixed target around a fixed
   configuration \(x\)?
2. **Historical self-intersection:** is \(X_n\) close to *some* sufficiently old
   state \(X_j\), \(j<n-\tau\)?
3. **Projected or structural recurrence:** does a predeclared feature
   \(Y_n=\pi(X_n)\) return to a target in a lower-resolution space \(F\)?

Pólya's theorem and the usual Green-kernel test answer (1). They do not, by
themselves, answer (2) or (3). A mathematically sound CDT claim must say which
observable it uses.

For a measurable target \(A\subseteq E\), define the visit count and Green
potential

\[
N_A(T)=\sum_{n=1}^{T}\mathbf 1_{\{X_n\in A\}},\qquad
G_X(x,A)=\mathbb E_xN_A(\infty)
          =\sum_{n\geq1}P_x(X_n\in A).
\]

Continuous-time versions replace the sum by occupation time
\(\int_0^T\mathbf 1_A(X_t)\,dt\), with the usual qualification that occupation,
hitting, and number of entrances need not be identical for thin sets.

Let \(\pi:E\to F\) be a feature map chosen before examining the recurrence
outcome. For \(x\in E\), define

\[
A_\varepsilon(x)=B_E(x,\varepsilon),\qquad
C_R(x)=\pi^{-1}\!\left(B_F(\pi x,R)\right).
\]

`A_epsilon` is a full-configuration target. `C_R` is a structural or "rhyme"
target. The essential point is that `C_R` is a cylinder/preimage under a
coarse-graining, not merely a larger ball in the same geometry.

---

## 2. The core theorem

### Theorem 1 (Configuration-Drift / projected-recurrence separation)

Let \(X\) be a conservative process on \(E\), and define
\(Y_n=\pi(X_n)\) on \(F\). The projected process need not itself be Markov. Fix
\(x\in E\), \(\varepsilon>0\), and \(R>0\).
Assume:

1. **Full-state transience:**
   \[
   G_X(x,A_\varepsilon(x))<\infty.
   \]
2. **Structural recurrence:**
   \[
   P_x\!\left(Y_n\in B_F(\pi x,R)\ \text{infinitely often}\right)=1.
   \]

Then, with probability one,

\[
N_{A_\varepsilon(x)}(\infty)<\infty,
\qquad
N_{C_R(x)}(\infty)=\infty.
\]

Thus full configurations eventually cease to recur while their declared
structural class recurs indefinitely.

If recurrence of \(Y\) is established using a transition kernel on \(F\), one
must additionally prove that the projection is Markov/lumpable or otherwise
derive a closed law for \(Y\). The theorem itself only needs the displayed
pathwise recurrence probability under the full initial state \(x\).

We call this conclusion **CDT persistence relative to**
\((X,\pi,x,\varepsilon,R)\). The adjective is scale- and representation-relative;
it is not a synonym for biological life or task success.

#### Proof

The first assumption gives

\[
\mathbb E_x N_{A_\varepsilon(x)}(\infty)<\infty.
\]

A nonnegative extended-integer random variable with finite expectation is
finite almost surely. Hence the full target is visited only finitely often.
The second conclusion is exactly structural recurrence, because
\(X_n\in C_R(x)\) iff \(Y_n\in B_F(\pi x,R)\). QED.

### What the theorem says

CDT is valid when **the full process is transient but its structural quotient is
recurrent**. This is the rigorous form of "the exact state does not come back,
but the rhyme does."

### What the theorem does not say

The theorem does not claim that:

- high ambient dimension alone identifies the relevant state space;
- every positive self-repulsion parameter produces the split;
- two fixed radii in one homogeneous geometry have different recurrence types;
- recurrence or novelty is equivalent to biological life, consciousness,
  usefulness, or correctness.

---

## 3. Capacity form: exact targets can be polar

There is a second rigorous route to the split. For a recurrent irreducible Hunt
process, let `Cap` be the process capacity.

### Theorem 2 (capacity-separated recurrence)

Suppose \(X\) is recurrent and irreducible in the potential-theoretic sense.
Let \(A\subset C\subset E\), where:

- \(A\) is polar: \(\operatorname{Cap}(A)=0\);
- \(C\) is a relatively compact recurrent target with
  \(\operatorname{Cap}(C)>0\).

Then \(A\) is almost surely never hit after time zero, while \(C\) is visited
recurrently by the stated recurrent-target assumption. Positive capacity alone
is not being used as a universal recurrence theorem. Therefore an exact/coarse
split can exist even without
self-repulsion.

This is why "exact equality has probability zero" is not by itself evidence of
configuration drift. In continuous spaces, a point can be polar for purely
geometric reasons.

### Euclidean Brownian example

- In one dimension, Brownian motion hits points and neighborhoods repeatedly.
- In two dimensions, every fixed point is polar but every neighborhood is
  recurrent: a genuine point-versus-neighborhood split.
- In dimension three and above, bounded neighborhoods are transient, so the
  coarse recurrence side fails.

Planar Brownian motion can nevertheless have random self-intersection points.
This does not contradict polarity: a point selected from the path is not the
same object as a deterministic point fixed in advance. This distinction is one
reason anchored recurrence and historical self-intersection must remain
separate.

---

## 4. Spectral-dimension corollary

The Green kernel is primary. Spectral dimension is a derived shortcut.

Assume \(X\) is an irreducible symmetric diffusion or random walk on a
metric-measure space whose volume and heat kernel satisfy two-sided scaling

\[
\mu(B(x,r))\asymp r^{d_f},\qquad
p_t(x,x)\asymp t^{-d_f/d_w}=t^{-d_s/2},
\qquad d_s=\frac{2d_f}{d_w}.
\]

Under these assumptions,

\[
\int_1^\infty p_t(x,x)\,dt=\infty
\quad\Longleftrightarrow\quad
d_f\le d_w
\quad\Longleftrightarrow\quad
d_s\le2.
\]

The same statement holds with sums in discrete time. This is the precise scope
of the familiar `d_s = 2` boundary.

### Corollary 1 (spectral CDT)

Suppose both \(X\) and its quotient \(Y=\pi(X)\) satisfy the stated two-sided
heat-kernel assumptions. If

\[
d_s(Y)\le2<d_s(X),
\]

then Theorem 1 applies: the structural quotient is recurrent and the full
configuration is transient.

### Corollary 2 (independent product)

If \(X=(Y,Z)\), the components are independent, and their on-diagonal kernels
have pure-power exponents, then

\[
p_t^X((y,z),(y,z))=p_t^Y(y,y)p_t^Z(z,z),
\qquad d_s(X)=d_s(Y)+d_s(Z).
\]

Hence

\[
d_s(Y)\le2<d_s(Y)+d_s(Z)
\]

is a sufficient CDT condition. Extra contributing coordinates destroy
full-state recurrence while a low-dimensional structural projection can keep
recurring. This is the sound version of the "many contributing elements"
intuition.

### Critical boundary

At \(d_s=2\), the exponent alone can be insufficient. For example,

\[
p_t(x,x)\asymp \frac{1}{t(\log t)^q}
\]

is recurrent for \(q\le1\) and transient for \(q>1\). Therefore use the full
Green integral at the boundary; never classify a critical case from a rounded
spectral-dimension estimate alone.

Two-sided heat-kernel estimates and their geometric hypotheses are developed,
for example, by [Grigor'yan and Telcs](https://arxiv.org/abs/1205.5627) and by
[Barlow, Coulhon, and Kumagai](https://doi.org/10.1002/cpa.20091).

---

## 5. Two no-go results

### Proposition 1 (fixed-radius no-go)

In a homogeneous irreducible process with local heat-kernel comparability, two
fixed balls \(B(x,\varepsilon)\subset B(x,R)\) around the same anchor have the
same recurrence class. Changing a fixed radius changes a multiplicative volume
factor, not convergence of the Green sum.

Consequently, a proof cannot obtain

\[
G_\varepsilon(x)<\infty<G_R(x)
\]

merely by claiming a different spectral dimension at two fixed radii. A valid
split needs at least one of:

- a different target geometry or capacity;
- a quotient/projection \(\pi\);
- a scale that changes with time;
- a genuinely multiscale process with separately proved kernels.

### Proposition 2 (positive repulsion is not a universal criterion)

The sign of a scalar `gamma` is neither necessary nor sufficient for Theorem 1.

- It is not necessary: hidden-coordinate drift can make \(X\) transient while
  \(\pi(X)\) remains recurrent even when `gamma = 0`.
- It is not sufficient: self-interacting walks are history-dependent and their
  recurrence class depends on the interaction, geometry, and state
  augmentation. Self-repelling rules can even self-trap.

The literature contains both recurrent and transient self-interacting walks
([Peres, Popov, and Sousi](https://arxiv.org/abs/1203.3459)) and a specifically
self-trapping self-repelling construction
([Grassberger](https://arxiv.org/abs/1708.03270)). Diffusive limits for some
true self-avoiding and self-repelling models require substantial additional
conditions ([Horvath, Toth, and Veto](https://arxiv.org/abs/1009.0401)).

For the continuous occupation-field model, the formal expression

\[
b_t(x)=-\gamma\nabla\int_0^t\delta(x-X_s)\,ds
\]

is generally singular. A rigorous model must mollify the delta kernel or define
a local-time interaction where that object exists, and must include the
occupation field in the state if a Markov formulation is required.

The valid proof obligation for any self-repulsive CDT model is therefore:

\[
\sum_nP_x(X_n\in A_\varepsilon)<\infty
\quad\text{and}\quad
P_x(\pi(X_n)\in B_R\ \mathrm{i.o.})=1.
\]

`gamma > 0` may help establish these conditions in a specified model. It cannot
replace them.

### Minimal counterexamples to stronger readings

These examples locate the logical boundary sharply.

1. **Irrational rotation:** \(X_n=x_0+n\theta\pmod 1\), with irrational
   \(\theta\), never repeats an exact state but returns arbitrarily close to its
   start. It has one dimension, no randomness, and no realization-dependent
   repulsion. The split therefore does not identify the proposed mechanism.
2. **Continuous iid sampling:** iid uniform points in a bounded region almost
   surely never equal one another at sampled times, while every positive-volume
   cell is visited infinitely often. Again there is no drift or self-repulsion.
3. **Finite irreducible chain:** every state recurs, yet the fraction of newly
   discovered states eventually becomes zero. Recurrence and novelty are not
   interchangeable.
4. **Constant projection:** if \(\pi(x)\equiv c\), "rhyme" recurs forever for
   every process. Structural recurrence is meaningful only when the projection
   is nontrivial and independently justified.
5. **Transient walk with backtracking:** a simple walk on \(\mathbb Z^3\) is
   transient relative to a fixed origin but still makes historical exact
   revisits, including infinitely many local backtracks. Anchored transience is
   not historical non-repetition.

---

## 6. Exact results for important model families

### 6.1 Simple symmetric lattice walk

For simple symmetric random walk on \(\mathbb Z^d\), the return kernel obeys
\(p_{2n}(0,0)\asymp n^{-d/2}\). Hence the origin is recurrent for \(d\le2\)
and transient for \(d\ge3\).

The number of distinct sites has a different law. If \(R_T\) is the range,
then, under the standard hypotheses,

\[
\frac{|R_T|}{T}\longrightarrow P_0(T_0^+=\infty).
\]

The limit is zero in the recurrent dimensions and positive in transient
dimensions. Thus transience means a positive long-run discovery rate, not zero
self-intersections. The classical range analysis begins with
[Dvoretzky and Erdos](https://users.renyi.hu/~p_erdos/1951-14.pdf).

### 6.2 Brownian motion with constant drift

For \(dX_t=v\,dt+\sqrt{2D}\,dW_t\) on \(\mathbb R^d\),

\[
p_t(0,0)=(4\pi Dt)^{-d/2}
          \exp\!\left(-\frac{\lVert v\rVert^2t}{4D}\right).
\]

Every nonzero constant drift makes the Green integral of a fixed bounded target
finite. This is an exact theorem for this model, not a universal statement about
all forms of "drift."

Let \(P\) be a linear structural projection. The projected drift is \(Pv\).
For a nondegenerate Gaussian projection, a sufficient exact/rhyme condition is

\[
v\ne0,\qquad Pv=0,\qquad \operatorname{rank}(P\Sigma P^\top)\le2.
\]

The full configuration escapes, while the low-dimensional structure does not
inherit the directional drift and remains recurrent. If \(Pv\ne0\), the same
exponential cutoff kills anchored coarse recurrence too.

### 6.3 Symmetric alpha-stable Levy process

For an isotropic symmetric \(\alpha\)-stable process in \(\mathbb R^d\),
\(p_t(0,0)\asymp t^{-d/\alpha}\). Therefore

\[
\text{recurrent}\quad\Longleftrightarrow\quad d\le\alpha.
\]

Equivalently, its walk dimension is \(d_w=\alpha\), and the ordinary condition
\(d_f\le d_w\) already gives \(d\le\alpha\). No extra multiplication by a
second stability index is permitted. Formulas such as
`d_f <= alpha*d_w/2` double-count anomalous scaling and are incorrect for the
stable process itself.

### 6.4 Fractional Brownian motion

For \(d\)-dimensional fractional Brownian motion with Hurst exponent \(H\),
the mean-square displacement exponent is \(2H\), so the formal walk dimension
is \(d_w=1/H\). The threshold \(d\le1/H\) agrees with known recurrence/hitting
scaling, with critical cases requiring polarity analysis. Fractional Brownian
motion is not Markov unless \(H=1/2\), so a Markov heat-kernel proof cannot be
silently reused. Also, `H < 1/2` is subdiffusive and `H > 1/2` is
superdiffusive; reversing those labels is an error.

---

## 7. Historical recurrence has a different threshold and normalization

For a translation-invariant random walk with stationary independent increments,
define the pair self-intersection count

\[
I_T(A)=\sum_{0\le i<j\le T}
       \mathbf 1_{\{X_j-X_i\in A\}}.
\]

Then the following identity is exact:

\[
\mathbb E I_T(A)
=\sum_{k=1}^{T}(T+1-k)P(X_k-X_0\in A).
\]

If \(P(X_k-X_0\in A)\asymp k^{-a}\), then

\[
\mathbb EI_T(A)=
\begin{cases}
\Theta(T^{2-a}), & a<1,\\
\Theta(T\log T), & a=1,\\
\Theta(T), & a>1,
\end{cases}
\]

provided the small-lag terms are nonzero in the last case.

Therefore:

- transient walks can continue to make linearly many historical
  self-intersections;
- pair density \(I_T/T^2\) can vanish in every dimension;
- a "recurrence rate tends to zero" statement is meaningless until its
  denominator, exclusion lag, target scale, and order of limits are fixed.

For Brownian paths, exact *double-point* thresholds also differ from fixed-point
recurrence: Brownian motion has double points below dimension four and not at
or above dimension four. See the Brownian-motion case summarized in
[Dalang et al.](https://arxiv.org/abs/1009.0235). This is another direct
counterexample to using the Pólya threshold as a universal self-intersection
threshold.

---

## 8. A correct conditional theorem for realization-dependent avoidance

Historical avoidance can be proved without pretending it is an anchored Green
kernel.

Let

\[
H_n^\varepsilon=
\left\{\min_{0\le j\le n-\tau_n}d_E(X_n,X_j)\le\varepsilon_n\right\}.
\]

### Theorem 3 (conditional anti-recurrence)

If there is a deterministic summable sequence \((a_n)\) such that

\[
P(H_n^\varepsilon\mid\mathcal F_{n-1})\le a_n
\quad\text{almost surely},
\qquad
\sum_na_n<\infty,
\]

then only finitely many historical fine recurrences occur almost surely.

#### Proof

Taking expectations gives \(\sum_nP(H_n^\varepsilon)<\infty\). The first
Borel-Cantelli lemma gives \(P(H_n^\varepsilon\ \mathrm{i.o.})=0\). QED.

To obtain a full CDT split, pair this theorem with a separately proved
recurrence result for \(\pi(X_n)\). In a self-repulsive model, the actual job of
the mechanism is to establish the summable conditional bound. A parameter sign
alone is not a proof.

---

## 9. Controller and heartbeat results: the strongest valid form

Let an augmented autonomous system have state \((X_n,g_n)\), where \(g_n\) is
the controller's stored energy or gain. Let \(A\subset E\) be an undesirable
lock-in set.

### Lemma 1 (invariant-death-set obstruction)

If \(D=A\times\{0\}\) is forward invariant under the joint uncontrolled update,
then no trajectory starting in \(D\) can escape \(D\) without an admissible
input that breaks invariance.

This proves the closed-loop observation used by the endogenous-rescue
simulation. It does **not** prove that all internal rescue fails. An internal
subsystem can rescue whenever it has an admissible transition out of \(D\); an
external input is necessary only after the no-escape assumption has been
established.

### Correct control criterion

For a target operating set \(K\), sustained operation is a viability problem.
A feedback law can keep the state in \(K\) only from states in the viability
kernel

\[
\operatorname{Viab}(K)=
\{x_0:\exists\text{ admissible policy with }X_n\in K\ \forall n\}.
\]

Reach, rate, sensing, energy, and action constraints affect this kernel. They
cannot in general be multiplied into a universal scalar equivalence involving
`d_s` and `gamma`.

Likewise, "kick exactly at the boundary" is optimal only for a specified loss,
dynamics, observation model, and admissible-control set. A simulation can
support that policy for its model; it cannot establish a universal control law.

---

## 10. Memory and coarse-graining: what follows mathematically

Let \(\pi:E\to F\) be a representation or consolidation map.

1. If \(\pi\) is Lipschitz, Hausdorff dimension cannot increase:
   \[
   \dim_H\pi(E)\le\dim_HE.
   \]
2. If \(\pi\) maps into a finite prototype bank, its image has Hausdorff
   dimension zero. Under an irreducible stationary query process, prototypes
   with positive stationary mass recur.
3. Neither fact implies useful recall, low prediction loss, semantic fidelity,
   or causal benefit. Those require held-out and interventional evaluation.
4. Pruning is not automatically "dimension reduction" in the statistical
   estimate: selective deletion can decrease, preserve, or increase an
   estimated local slope. The map or pruning rule needs its own proof or test.

Thus CDT justifies a precise engineering hypothesis: a representation can make
a recurrent structural quotient out of a transient full state. It does not
guarantee that any particular clustering, HCM, or retrieval policy succeeds.

---

## 11. Exhaustive failure envelope

A CDT conclusion is not licensed when any required item below is unresolved.

| Boundary | Failure mode | Required response |
|---|---|---|
| Observable | anchored, historical, and projected recurrence are mixed | define one before analysis |
| State | hidden memory makes the process non-Markov | augment the state or use a non-Markov theorem |
| Target | "exact" is an unresolvable point in continuous data | use capacity or a declared resolution |
| Projection | rhyme map chosen after seeing results | preregister or validate out of sample |
| Metric | distances have no functional meaning | supply invariance/semantics or do not claim rhyme |
| Heat kernel | no two-sided scaling or irreducibility | use the Green sum directly |
| Criticality | estimated `d_s` is near 2 | test logarithmic corrections; return undecidable |
| Dimension | trajectory-cloud correlation dimension substituted for substrate volume dimension | estimate the correct object or withhold verdict |
| MSD | drift, confinement, aging, anisotropy, or infinite variance contaminates the slope | do not identify `d_w=2/beta` without a scaling audit |
| Self-interaction | `gamma` changes the process law | prove the perturbed kernel/conditional bound |
| Finite space | every irreducible state recurs and novelty is exhausted | use cover time/capacity, not infinite-space CDT |
| Nonstationarity | kernel or manifold changes on the measurement timescale | use local/time-inhomogeneous analysis |
| Determinism | periodic or quasiperiodic dynamics lack the assumed kernel | use dynamical-systems recurrence instead |
| Resolution | `T -> infinity` and `epsilon -> 0` are interchanged | state the order or joint scaling explicitly |
| Function | novelty is treated as usefulness | add an external performance/survival criterion |
| Causality | correlation is treated as realization-induced repulsion | intervene on the proposed mechanism |

Two especially important consequences follow.

**Correlation dimension caveat.** The correlation dimension of sampled visited
points is generally a property of the occupation/range distribution, not
automatically the Ahlfors volume exponent \(d_f\) controlling the substrate heat
kernel. For Brownian paths the range dimension can saturate even as ambient
dimension grows. A point-cloud estimator cannot be inserted into
\(d_s=2d_f/d_w\) without an identification argument.

**Finite-data caveat.** No finite trajectory proves infinite-time recurrence.
Finite data can reject a specified model, estimate finite-horizon Green sums,
and compare registered alternatives. It cannot turn an asymptotic theorem into
an observed fact.

---

## 12. Ready-to-use protocol

### 12.1 Claim template

Fill every field before using CDT.

```text
Full state:          X_t =
State space/metric:  (E, d_E) =
Structural map:      pi:E->F =
Fine target:         A_epsilon =
Coarse target:       C_R = pi^{-1}(B_F(...))
Observable:          anchored | historical | projected
Exclusion lag:       tau =
Asymptotic order:    fixed epsilon then T->infinity | joint scaling =
Full-state proof:    Green sum / capacity / conditional BC / other =
Coarse proof:        quotient Green sum / recurrence theorem / other =
Mechanism test:      intervention and null =
Finite-data status:  supported | contradicted | undecidable
Functional metric:   independent task/survival quantity =
```

### 12.2 Decision rule

Use the following hierarchy.

1. Compute or bound the full Green quantity. If it is not finite, Theorem 1 is
   not established.
2. Compute or bound the quotient Green quantity. If it is not divergent (with
   recurrence hypotheses), persistent rhyme is not established.
3. If exact targets are thin, perform a capacity/polarity analysis.
4. Use `d_s` only after verifying the heat-kernel model. At `d_s ~= 2`, return
   **undecidable** unless slowly varying corrections are controlled.
5. For self-repulsion, test the perturbed process, not the neutral substrate.
6. For historical recurrence, use Theorem 3 or an intersection theorem, not
   Pólya's fixed-origin result.
7. Report functionality separately from CDT recurrence.

### 12.3 Empirical estimands

For a single trajectory, report at least

\[
H_T(r,\tau)=\frac{1}{T-\tau}
\sum_{n=\tau+1}^{T}
\mathbf1\!\left\{\min_{j\le n-\tau}d(X_n,X_j)\le r\right\},
\]

and the same quantity after the predeclared projection \(\pi\). Also report the
number of occupied `epsilon`-cells and its growth with \(T\). These are
historical finite-horizon diagnostics, not Green-kernel proofs.

For anchored recurrence, use many independent restarts and estimate

\[
\widehat p_n(A)=\frac1M\sum_{m=1}^M
\mathbf1_{\{X_n^{(m)}\in A\}},
\qquad
\widehat G_N(A)=\sum_{n=1}^N\widehat p_n(A).
\]

Plot \(\widehat G_N\) over increasing horizons; compare pure power, power-plus-log,
and exponential-cutoff models. Use block/bootstrap intervals appropriate to the
sampling design, and keep `epsilon`, `R`, `tau`, and `pi` fixed from the
registered analysis.

The repository utility `cdt_empirical_audit.py` implements these separated
finite-horizon diagnostics for `.npy` and `.csv` trajectories:

```powershell
python cdt_empirical_audit.py paths.npy `
  --epsilon 0.05 --radius 0.5 --lag 10 --projection 0,1
```

It returns JSON and intentionally makes no asymptotic alive/dead verdict.

### 12.4 Allowed conclusions

- **Theorem:** assumptions are stated and the Green/capacity proof is complete.
- **Model theorem:** proved for one specified stochastic/control model.
- **Simulation support:** finite experiments match a registered prediction.
- **Empirical association:** observed without a causal intervention.
- **Interpretation/metaphor:** useful framing, not a mathematical result.

Do not replace one label with another.

---

## 13. Registered simulation frontier

The 2026-09-05 campaign tested the theorem and its proposed mechanisms without
using the analytic answers to retune thresholds. Full details and path-level
outputs are in `results/cdt_simulation_evidence_ledger.md`.

### What survived

1. **Product/projection phase map.** For coordinate walks on
   \(\mathbb Z^D\), every identifiable registered slope agreed with the exact
   projection threshold. Three of 21 fits were unidentifiable because fine
   returns in dimensions five and six reached the zero-event floor; they are not
   counted as confirmations or contradictions.
2. **Hidden-drift construction.** In a corrected two-dimensional causal
   control, hidden drift made full return tails decay while the one-coordinate
   projected slope remained \(0.492\)--\(0.505\), statistically tracking the
   neutral recurrent projection. The same drift applied inside the projection
   suppressed both. Thus the location of drift relative to \(\pi\), not merely
   nonzero drift, is the operative condition.
3. **Finite capacity and counterexamples.** Finite tori approached stationary
   return rates while novelty exhausted. Irrational rotation and continuous iid
   sampling produced exact/coarse separation without self-repulsion. These
   controls confirm the stated failure envelope.

### What became stronger but remains unproved

In the destination-local-time walk, the one-coordinate anchored tail slope
remained positive through \(\gamma=10\) in both tested dimensions, while full
historical recurrence fell and discovery rose. This is a wider finite-horizon
mechanism window than the original campaign expected. It is still only
simulation support: full anchored returns were too rare for stable slope
estimation, and no asymptotic theorem for the perturbed walk was supplied.

### Operational correction

A zero-event tail is an **estimator floor**, not evidence of an arbitrarily
large negative exponent. When expected returns are rare, report an upper bound
or increase independent path count; do not fit a log slope to zeros. Likewise,
historical recurrence may remain near one while anchored returns change
materially. Neither observable can substitute for the other.

---

## 14. Status of the earlier headline claims

| Earlier claim | Status | Correct replacement |
|---|---|---|
| Pólya boundary `D=2` | valid for the specified lattice walk / Brownian neighborhoods | Green-kernel criterion |
| `d_s<=2` iff recurrence | conditional | valid under two-sided heat-kernel and irreducibility assumptions; inspect logs at equality |
| `nu<=d_w` from any trajectory cloud | invalid generally | identify substrate `d_f` and walk exponent separately |
| any nonzero constant Gaussian drift kills anchored recurrence | valid for that model | use the exponential heat-kernel cutoff |
| any realization perturbation `gamma>0` kills exact recurrence | false generally | tested local-time repulsion is promising through `gamma=10`, but still requires a perturbed Green bound or Theorem 3 |
| fixed `epsilon` transient but fixed `R` recurrent in one homogeneous space | false without extra multiscale structure | use a projection, capacity gap, or time-varying scale |
| `Alive iff (d_s<=2) and (gamma>0)` | not a theorem | define `CDT-persistent` by Theorem 1; measure function separately |
| alpha-stable threshold `nu<=alpha*d_w/2` | incorrect for the stable process | `d<=alpha`, equivalently `d_f<=d_w` with `d_w=alpha` |
| self-repulsion raises `d_w` and therefore raises `d_s` | algebraically inconsistent | `d_s=2d_f/d_w`; increasing `d_w` lowers `d_s` |
| Brownian Pólya threshold governs all self-intersections | false | use the pair-count identity or a multiple-point theorem |
| heartbeat boundary trigger is uniquely optimal | model-specific simulation result | state the control objective and prove viability/optimality |
| external rescue is universally necessary | false generally | valid only when the internal death set is proved invariant |
| coarse memory must improve prediction | not mathematical | test by causal ablation on held-out behavior |
| fourteen domains prove one universal law | overclaim | separate direct measurements, model simulations, analogies, and undecidable cases |

---

## 15. Final theorem in one line

The defensible, reusable Configuration-Drift Theorem is

\[
\boxed{
G_X(x,A_\varepsilon)<\infty
\quad\text{and}\quad
\pi(X)\text{ recurrent on }B_F(\pi x,R)
\quad\Longrightarrow\quad
\text{finite returns to the registered fine target, but persistent structural returns.}
}
\]

Under verified two-sided power-law heat kernels, a convenient sufficient
condition is

\[
\boxed{d_s(\pi(X))\le2<d_s(X).}
\]

This version is mathematically sound, falsifiable, and ready for use. It keeps
CDT's central insight while exposing exactly what must be proved in every new
system.
