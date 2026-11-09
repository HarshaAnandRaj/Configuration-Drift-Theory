# Configuration Drift: recurrence under a structural projection

**Author of the CDT hypothesis:** Harsha Anand Raj Pammi

**Mathematical revision:** 2026-11-09

**Status:** classical recurrence results assembled into a precise CDT framework;
no claim of a new general recurrence law.

This is the canonical mathematical layer. The
[theory notebook](configuration_drift_theory.md) and
[full report](configuration_drift_full_report.md) retain the research history.
The [revision notes](docs/theorem_revision_20261109.md) explain what changed.
The [use cases and phenomena](docs/use_cases_and_phenomena.md) distinguish
proved model behavior from proposed applications and give testable protocols.

The question is: **can a process eventually leave every fixed fine target,
while continuing to return to a declared structural class?** Yes. On countable
state spaces, a transient Markov chain with a recurrent Markov projection gives
an exact answer. Neither dimension nor the sign of a repulsion parameter alone
answers this question.

The proposed explanation—realizing a configuration changes its future
accessibility—is a separate mechanism hypothesis. Recurrence separation alone
does not establish that explanation, life, useful memory, or task success.

## 1. Specify the observable first

For a process $X_n$ with full state space $E$, choose a measurable
structural map $\pi:E\to F$ before examining recurrence outcomes. Write
$Y_n=\pi(X_n)$. For fixed targets $A\subset E$, $B\subset F$, define

$$
 V_A(T)=\sum_{n=0}^T\mathbf1_{\{X_n\in A\}},\qquad
 W_B(T)=\sum_{n=0}^T\mathbf1_{\{Y_n\in B\}}.
$$

The structural target in full space is $C=\pi^{-1}(B)$, so
$W_B(T)=V_C(T)$. Use $A\subseteq C$ when the coarse target is intended
to contain the fine one. The split studied here is

$$
 \mathbb P_x\{V_A(\infty)<\infty,\ W_B(\infty)=\infty\}=1. \tag{S}
$$

This is **anchored recurrence separation**. It says that eventually there are
no more returns to $A$. It does not say that the trajectory stops repeating
states elsewhere.

| Observable | Event or quantity | Question |
|---|---|---|
| Anchored fine | $X_n\in A$ | return to a fixed configuration target |
| Anchored structural | $Y_n\in B$ | return to a fixed structural class |
| Historical | $\min_{j\le n-\tau}d(X_n,X_j)\le r$ | return near any sufficiently old state |
| Discovery | number of occupied registered cells | growth of the observed range |

These cannot replace one another. In particular, a return probability tending
to zero, a vanishing fraction of visits, and finitely many visits are different
statements. A one-dimensional symmetric walk has return probabilities tending
to zero and nevertheless returns infinitely often.

## 2. An exact theorem on countable state spaces

### Assumptions

1. $X$ is a discrete-time, time-homogeneous, irreducible Markov chain on a
   countable space $E$, with stochastic transition matrix $P$.
2. $\pi:E\to F$ is onto a countable space and is **strongly lumpable**:
   for all $y,z\in F$,
   $$
    \sum_{w:\pi(w)=z}P(x,w)=Q(y,z)\quad
    \text{for every }x\text{ with }\pi(x)=y. \tag{L}
   $$
   Thus $Y=\pi(X)$ is a Markov chain with matrix $Q$, for every full
   initial state. Irreducibility of $P$ implies irreducibility of $Q$.
3. $A\subset E$ and $B\subset F$ are nonempty **finite** sets, with
   $A\subseteq\pi^{-1}(B)$.

No stationarity, reversibility, coordinate independence, or aperiodicity is
required. A feature process is not automatically Markov: (L) must be proved.

Define Green functions including the visit at time zero:

$$
 G_P(u,v)=\sum_{n=0}^\infty P^n(u,v),\qquad
 G_Q(y,z)=\sum_{n=0}^\infty Q^n(y,z).
$$

### Theorem 1 (transient full chain, recurrent structural chain)

Under assumptions 1–3, the following are equivalent:

1. For some $a\in E$, $b\in F$,
   $$
    G_P(a,a)<\infty,\qquad G_Q(b,b)=\infty. \tag{G}
   $$
2. Separation (S) holds for **every** starting state $x\in E$.
3. Separation (S) holds for **at least one** starting state $x\in E$.

Equivalently, (S) holds exactly when $P$ is transient and $Q$ is
recurrent. In (G), “some” can be replaced by “every.”

#### Proof

Let $T_a^+=\inf\{n\ge1:X_n=a\}$ and
$f_a=\mathbb P_a(T_a^+<\infty)$. By the strong Markov property, each
return renews the same experiment. Thus

$$
 \mathbb P_a\{V_{\{a\}}(\infty)\ge k\}=f_a^{k-1},\qquad
 G_P(a,a)=\sum_{k\ge1}f_a^{k-1}.
$$

If $f_a<1$, the visit count is finite almost surely and
$G_P(a,a)=(1-f_a)^{-1}$. If $f_a=1$, it is infinite almost surely.
Irreducibility makes recurrence or transience common to all states. In the
recurrent case every state is hit and then revisited infinitely often from
every start. In the transient case the strong Markov property at the first
hit gives finitely many visits to any target state from every start. These are
the standard irreducible-chain recurrence alternatives.

Under (G), every state in $A$ has finitely many visits. Finiteness of $A$
gives $V_A(\infty)<\infty$. Applying the recurrent alternative to $Q$,
any state in nonempty $B$ is visited infinitely often. This proves (1)
implies (2), and (2) implies (3).

Conversely, under (3), $P$ cannot be recurrent, since then every state of
$A$ would have infinitely many visits. Nor can $Q$ be transient, since
then its finite set $B$ would have finitely many visits. The recurrence
alternatives give (G). QED.

### Corollary 1a (positive return frequency)

Under assumptions 1–3, strengthen (S) by requiring

$$
 \frac{W_B(T)}{T+1}\longrightarrow\rho_B>0\quad\text{almost surely}.
 \tag{R}
$$

Finite fine visits together with (R) hold exactly when $P$ is transient and
$Q$ is **positive recurrent**. In that case $Q$ has a stationary probability
distribution $\nu$, and $\rho_B=\nu(B)$. If $Q$ is null recurrent instead,
then $W_B(T)\to\infty$ but $W_B(T)/(T+1)\to0$ for every finite $B$.

#### Proof

For an irreducible countable chain, the occupation-time ergodic theorem gives
the limit $\nu(b)$ at each state in the positive recurrent case, and zero
in the null recurrent or transient case. Summing over finite $B$ gives the
claims; Theorem 1 supplies the fine-state condition. Periodicity does not
affect these time averages. QED.

For a single structural state $b$, the mean return time when started at $b$
is $1/\nu(b)$ in the positive recurrent case and infinite in the null recurrent
case. Positive recurrence gives a positive rate, not a maximum return gap or
a deadline guarantee. Those require additional return-time tail bounds.

### Consequence: every structural fiber must be infinite

Under Theorem 1, **every** fiber $\pi^{-1}(\{b\})$ is infinite. Otherwise
recurrence of $b$ would force infinitely many visits to a finite set of a
transient chain, a contradiction.

This explains what coarse-graining does here: it groups infinitely many
escaping full configurations into one recurring structural state. In a locally
finite lattice, two fixed bounded balls are finite targets and cannot have
different recurrence classes for an irreducible chain. Enlarging a fixed radius
cannot create (S).

Finiteness matters. A transient chain may visit an infinite set infinitely
often: a symmetric walk on $\mathbb Z^3$ visits the slab $x_1=0$
infinitely often, but visits each finite set only finitely often. The slab is
a projection fiber, not a bounded coarse ball in the same space.

## 3. A complete model with an explicit return kernel

Let $X_n\in\mathbb Z^D$. At each step every coordinate independently adds
$-1,0,+1$ with probabilities $1/4,1/2,1/4$, independently over time.
Let $\pi$ retain the first $m$ coordinates, $1\le m\le D$.
Both chains are irreducible and aperiodic, and (L) holds.

For one coordinate the exact return probability is

$$
 b_n=\frac{\binom{2n}{n}}{4^n}\sim\frac1{\sqrt{\pi n}}.
$$

Indeed, a step is distributed as the sum of two independent Bernoulli$(1/2)$
variables minus one. Independence gives

$$
 P^n(0,0)=b_n^D,\qquad Q^n(0,0)=b_n^m.
$$

The Green series diverges exactly when its dimension is at most two. For
nonempty finite nested targets as in Theorem 1,

$$
 \boxed{\text{anchored separation}\quad\Longleftrightarrow\quad m\le2<D.}
 \tag{P}
$$

For example, a three-dimensional walk has finitely many full returns to the
origin and infinitely many returns to the cylinder $x_1=x_2=0$. There is
no repulsion parameter. This is a classical product-walk construction, not a
new recurrence law.

The recurrent projections in this product example ($m=1,2$) are **null
recurrent**. They demonstrate infinitely many structural returns with zero
limiting frequency. They do not demonstrate a rhythm maintained at a positive
rate.

### A model with a positive structural return rate

Let $Y_n\in\mathbb Z$ be a lazy birth–death chain. For $y\ne0$, move one
unit toward zero with probability $p$, one unit away with probability $q$,
and stay with probability $1-p-q$. At zero, move to each of $-1,+1$ with
probability $q$ and otherwise stay. Assume $0<q<p$ and $p+q<1$.

Writing $r=q/p<1$, detailed balance on every neighboring pair gives

$$
 \nu(y)=\frac{1-r}{1+r}\,r^{|y|}.
$$

The geometric sum normalizes this distribution, so $Y$ is irreducible and
positive recurrent. Independently let $Z$ have iid increments $+1,-1,0$
with probabilities $3/8,1/8,1/2$. The full chain $X=(Y,Z)$ is irreducible,
and $Z_n/n\to1/4$ almost surely, making $X$ transient. Projection onto $Y$
satisfies (L). For $A=\{(0,0)\}$ and $B=\{0\}$,

$$
 V_A(\infty)<\infty,\qquad
 \frac{W_{\{0\}}(T)}{T+1}\longrightarrow\frac{p-q}{p+q}>0
 \quad\text{almost surely}.
$$

At $p=1/2,q=1/4$, the rate is $1/3$ and the mean return time to zero is
three steps. This gives changing full configurations with recurring stabilized
structure. The restoring force is specified in the model; it has not been
derived from self-repulsion or learned dimensional adaptation.

## 4. Spectral dimension is a conditional shortcut

For the chains in Theorem 1, suppose for all sufficiently large $n$,

$$
 P^n(a,a)\asymp n^{-d_X/2},\qquad
 Q^n(b,b)\asymp n^{-d_Y/2}, \tag{H}
$$

where $\asymp$ denotes bounds by fixed positive multiples. Theorem 1 and
the series test then give exactly $\boxed{d_Y\le2<d_X}$. For periodic
chains, account for the return-time subsequence; (H) as written excludes
zero-return times. Laziness avoids that issue in §3.

With slowly varying factors, test the full series instead. In particular,

$$
 \sum_{n\ge3}\frac1{n(\log n)^q}
 \begin{cases}=\infty,&q\le1,\\ <\infty,&q>1.\end{cases}
$$

Both cases have spectral dimension two if dimension means only the limiting
power exponent. There is no contradiction with (H): nonconstant logarithmic
factors are not comparable to a constant. A rounded dimension estimate cannot
settle a critical case.

For independent synchronous product chains, return kernels multiply and
pure-power spectral dimensions add, provided the joint chain and kernels
satisfy the hypotheses used. No addition rule is established without
independence. The relation $d_s=2d_f/d_w$ requires a model identifying
substrate volume growth and a compatible heat kernel. Correlation dimension
of visited points and an MSD slope alone do not supply that model.

For diffusions, an on-diagonal transition **density** is not a return
probability. Neighborhood estimates and an applicable recurrence theorem are
needed before extending this argument to continuous spaces.

## 5. What survives without a Markov projection

For any process and fixed measurable targets, Tonelli's theorem gives

$$
 \mathbb E_x V_A(\infty)=\sum_{n\ge0}\mathbb P_x(X_n\in A).
$$

### Lemma 2 (general sufficient condition and last-return bound)

If this series is finite and
$\mathbb P_x(Y_n\in B\text{ infinitely often})=1$, then (S) holds.
For $N\ge1$, also

$$
 \mathbb P_x\{\exists n\ge N:X_n\in A\}
 \le\sum_{n\ge N}\mathbb P_x(X_n\in A). \tag{T}
$$

#### Proof

A nonnegative random variable with finite expectation is finite almost surely.
Combine this with the assumed structural recurrence. The union bound gives
(T). QED.

This was the principal theorem in the previous formulation. It is valid, but
does not derive structural recurrence. For a non-Markov feature process, that
recurrence needs a separate proof under the full starting state $x$. Strong
lumpability is sufficient for Theorem 1, not necessary for all possible splits.

If $\mathbb P_x(X_n\in A)\le c n^{-a}$ for $n\ge1$, $a>1$, then
for $N\ge2$, (T) yields

$$
 \mathbb P_x\{\text{a fine return at or after }N\}
 \le\frac{c}{a-1}(N-1)^{1-a}.
$$

This is a last-return upper bound, not a claimed exact distribution.

### An exact last-exit law for a transient state

For a transient Markov chain started at $a$, let
$L_a=\sup\{n\ge0:X_n=a\}$. The Markov property at deterministic time $n$
and the renewal identity in Theorem 1 give

$$
 \mathbb P_a(L_a=n)=\frac{P^n(a,a)}{G_P(a,a)},\qquad
 \mathbb P_a(L_a\ge N)=\frac{\sum_{n\ge N}P^n(a,a)}{G_P(a,a)}.
 \tag{E}
$$

Indeed, a last visit at $n$ means being at $a$ then never returning, whose
conditional probability is $1-f_a=1/G_P(a,a)$. Since $L_a$ is finite
almost surely, these probabilities sum to one.

Consequently $\mathbb E_a L_a<\infty$ exactly when
$\sum_n nP^n(a,a)<\infty$. In the lazy product walk, dimensions three and
four have a finite last return almost surely but an **infinite mean** last
return time; only $D>4$ gives a finite mean. Thus transience alone does not
specify a short observation window in which fine returns will disappear.

### Infinite expected visits need not mean recurrent visits

Let $L$ be a finite nonnegative integer with
$\mathbb P(L\ge n)=1/(n+1)$, $n\ge0$, and put
$Z_n=\mathbf1_{\{n\le L\}}$. Every path eventually leaves $\{1\}$,
but

$$
 \sum_{n\ge0}\mathbb P(Z_n=1)=\sum_{n\ge0}\frac1{n+1}=\infty.
$$

An infinite expectation can come from a heavy-tailed finite visit count.
The renewal/irreducibility argument in Theorem 1 supplies the additional step
absent here. Do not infer almost-sure recurrence from a divergent expected
visit count in an arbitrary process.

## 6. Continuous space: drift hidden from the projection

Let

$$
 X_t=x+vt+\sqrt{2D_0}\,W_t\quad\text{on }\mathbb R^d,\qquad D_0>0.
$$

Let $P:\mathbb R^d\to\mathbb R^k$ have rank $k\ge1$. Use a bounded
open ball around $x$ as fine target and an open ball around $Px$ as
structural target; choose radii to ensure nesting if needed. Here recurrence
means visits at arbitrarily large times, and finite returns means eventual
absence from the target, not a count of boundary crossings.

### Proposition 3 (Brownian classification)

Anchored separation holds exactly when

$$
 \boxed{(v\ne0\ \text{or}\ d\ge3),\qquad Pv=0,\qquad k\le2.} \tag{B}
$$

#### Proof

If $v\ne0$, the strong law $X_t/t\to v$ gives eventual escape from
every bounded set. With zero drift, Brownian motion is recurrent for open
balls in dimensions one and two, and eventually leaves each bounded set in
dimensions three and above.

The projection is Brownian motion with drift $Pv$ and covariance
$2D_0PP^\top$, positive definite on $\mathbb R^k$. A linear change
of coordinates reduces its zero-drift recurrence question to ordinary
$k$-dimensional Brownian motion. It returns to open balls at arbitrarily
large times exactly when $Pv=0$ and $k\le2$. Nonzero projected drift
gives eventual escape by the same strong law. QED.

In dimension two, $v=(0,c)$, $c\ne0$, and $P(x_1,x_2)=x_1$
give separation even though neutral planar Brownian motion is recurrent.
Drift in the first coordinate instead destroys structural recurrence.
Location relative to the projection is decisive.

### Small projected drift gives a long crossover

Write $\mu=Pv$ and $C=2D_0PP^\top$. The projected displacement density at
zero is exactly

$$
 p_t^Y(0)=\frac{\exp[-t\mu^\top C^{-1}\mu/2]}
                  {(2\pi t)^{k/2}\sqrt{\det C}}.
$$

For $\mu\ne0$, define the exponential cutoff scale
$t_{\rm leak}=2/(\mu^\top C^{-1}\mu)$. At times much smaller than this,
the exponential factor is close to one; at much larger times it suppresses
returns. A fixed bounded ball has the same exponential decay rate: integrate
the Gaussian density over the ball, whose spatial correction is bounded by
positive constants for large $t$. This does not identify its entire finite-time
return probability from the density at a point.

A small leakage of nuisance drift into the projection can therefore look
recurrent over a short run and still be transient. The cutoff is specific to
this Gaussian model, not a universal forgetting timescale.

### Points are different from neighborhoods

Planar Brownian motion started at a fixed point $x$ almost surely never
returns to exactly $x$ at positive time, but returns to every neighborhood
at arbitrarily large times. This is a polarity example, not transience of
fine balls or evidence for realization-induced drift. At fixed positive
radii both planar balls are recurrent.

No general Hunt-process capacity theorem is asserted here. Such an extension
must specify the process, the capacity convention (for example, 1-capacity
for a specified regular symmetric Dirichlet form), exceptional starting
states, and target recurrence. An unqualified zero-order capacity may vanish
on nonpolar sets in recurrent settings. “Positive capacity” alone is not a
recurrence proof.

In continuous time distinguish occupation duration, hitting at arbitrarily
late times, and numbers of entrances. Finite expected occupation does not
alone prove finitely many entrances for an arbitrary process. Proposition 3
uses the Brownian recurrence and escape results directly.

## 7. Historical avoidance requires its own theorem

Let $X_n$ be adapted to $\mathcal F_n$. For deterministic
$1\le\tau_n\le n$, $\varepsilon_n\ge0$, define

$$
 H_n=\left\{\min_{0\le j\le n-\tau_n}
                d_E(X_n,X_j)\le\varepsilon_n\right\},\qquad
 q_n=\mathbb P(H_n\mid\mathcal F_{n-1}).
$$

### Theorem 4 (conditional Borel–Cantelli criterion)

Up to a null event,

$$
 \boxed{\sum_n\mathbf1_{H_n}<\infty
        \quad\Longleftrightarrow\quad\sum_n q_n<\infty.} \tag{CB}
$$

No independence is required. A deterministic summable bound $q_n\le a_n$
is sufficient; more generally, pathwise finiteness of the conditional sum is
enough.

#### Proof

This is conditional Borel–Cantelli. Write
$S_N=\sum_{n\le N}\mathbf1_{H_n}$, $A_N=\sum_{n\le N}q_n$.
The martingale $M_N=S_N-A_N$ has conditional increment variance at most
$q_n$. On $\{A_\infty<\infty\}$, stopping the compensator at integer
levels bounds the expected stopped count; union over levels gives finite
$S_\infty$. On $\{A_\infty=\infty\}$, the martingale strong law for
bounded increments gives $M_N/A_N\to0$, hence $S_N\to\infty$. QED.

A historical fine/structural split also requires a separate proof that the
structural events occur infinitely often. Theorem 1 concerns fixed targets
and does not supply that historical claim.

For stationary independent increments, the pair-count identity is

$$
 I_T(A)=\sum_{0\le i<j\le T}\mathbf1_{\{X_j-X_i\in A\}},\qquad
 \mathbb E I_T(A)=\sum_{r=1}^T(T+1-r)\mathbb P(X_r-X_0\in A).
$$

If the lag probability is comparable to $r^{-a}$, $a>0$, the expectation
has order $T^{2-a}$ for $a<1$, $T\log T$ for $a=1$, and $T$
for $a>1$, assuming a positive finite-lag return probability. A transient
walk can keep making linearly many historical revisits. For a simple walk
on $\mathbb Z^3$, independent disjoint two-step backtracking trials already
give infinitely many exact historical repeats.

## 8. The mechanism hypothesis remains open

For destination-local-time repulsion on $\mathbb Z^D$, a typical rule is

$$
 \mathbb P(X_{n+1}=z\mid\mathcal F_n)
 =\frac{e^{-\gamma L_n(z)}}{\sum_{w\sim X_n}e^{-\gamma L_n(w)}},
 \qquad z\sim X_n,
$$

where $L_n(z)$ counts visits through time $n$. Position alone is
generally not Markov. The augmented state $(X_n,L_n)$ is Markov, but its
growing record changes the recurrence question: $\sum_z L_n(z)=n+1$, so
that augmented state never repeats, even at $\gamma=0$. This proves
nothing about avoidance in position.

Appending a clock likewise destroys exact-state recurrence of any process.
The full state must be causally justified, and novelty created solely by a
timestamp or cumulative record must be disclosed.

The open proof obligations for the self-repelling model are:

1. Fix position versus augmented/functional state, targets, scales, and lags.
2. Derive summable position-target return bounds for anchored avoidance, or
   prove (CB) for historical avoidance. Do not apply Theorem 1 to position
   as if it were an irreducible Markov chain.
3. Prove structural recurrence under the perturbed law. A coordinate projection
   need not have a closed Markov law.
4. Intervene on the proposed interaction with fixed representation, noise,
   and evaluation protocol to distinguish causation from separation alone.

The sign $\gamma>0$ establishes none of these by itself. Separation without
repulsion is proved in §§3 and 6. Constant projections make structural
recurrence automatic. Iid continuous samples and irrational rotations can
separate exact equality from neighborhood recurrence without the proposed
mechanism. They are controls, not evidence for realization-induced repulsion.

## 9. Function, control, and memory are additional claims

In a finite irreducible chain every state recurs; in a finite irreducible
structural chain recurrence is automatic. Neither fact distinguishes a useful
representation from a meaningless label. Justify the projection independently
and measure task performance separately.

An invariant failure set $D=A\times\{0\}$ for a controller state $(X,g)$
cannot be escaped under dynamics preserving it. That does not prove all
internal rescue impossible: an admissible internal transition may break
invariance. Sustained control requires operating sets, dynamics, constraints,
and a viability argument. Optimal intervention timing also requires a loss.

A Lipschitz map cannot increase Hausdorff dimension, but this geometric fact
does not prove improved prediction or recall. Finite prototype banks can recur
while losing task information. Evaluate memory, adaptive dimension, and rescue
with independent functional outcomes and held-out interventions. There is no
theorem here of the form `Alive iff (d_s <= 2) and (gamma > 0)`.

## 10. Empirical protocol

### A finite-horizon contract

An application should specify how much recurrence it needs, over what window,
and with what task performance. For $1\le t_0\le T$, let $V_A[t_0,T]$ and
$W_B[t_0,T]$ count fine and structural visits in that window. Choose a required
count $r\ge1$ and error budgets before observing data. A finite analogue of
separation is

$$
 \mathbb P_x\{V_A[t_0,T]=0\}\ge1-\alpha_f,\qquad
 \mathbb P_x\{W_B[t_0,T]\ge r\}\ge1-\alpha_c.
 \tag{F}
$$

Both events then hold with probability at least $1-\alpha_f-\alpha_c$ by
the union bound; independence is unnecessary. Condition (T) bounds the first
failure probability if the model supplies return probabilities. If some fine
returns are acceptable, register a nonzero count threshold instead.

If return deadlines matter, also bound the longest consecutive run of times
in $[t_0,T]$ outside $B$, including runs at both window edges. Register a
maximum permitted gap $L$ and a failure probability for exceeding it. A high
overall count can otherwise conceal a long service interruption.

This is an application contract, not an asymptotic theorem or an automatic
definition of useful behavior. Validate its path-level probabilities using
independent restarts and uncertainty intervals, and require a separate task
metric. Recurrence of a constant label must not pass the functional test.

### Proposition 5 (robustness to an approximate structural law)

Let $Y_n$ take values in a countable $F$ and be adapted to $\mathcal F_n$.
Let $Q$ be a reference Markov kernel. Suppose deterministic bounds $\delta_n$
satisfy, almost surely,

$$
 \left\|\mathcal L(Y_{n+1}\mid\mathcal F_n)-Q(Y_n,\cdot)\right\|_{\rm TV}
 \le\delta_n,\qquad n\ge0,
$$

where total variation is the supremum of differences over measurable events.
Compare the conditional law of $Y_N,\ldots,Y_T$ with a $Q$-chain started
at the same $Y_N$. For any event $D$ depending on this window, their conditional
probabilities differ by at most

$$
 \min\left(1,\sum_{n=N}^{T-1}\delta_n\right). \tag{TV}
$$

If $Q$ is irreducible recurrent and $\sum_n\delta_n<\infty$, then $Y$
visits every state of $F$ infinitely often almost surely, even if $Y$ is
not Markov. If $Q$ is positive recurrent with stationary distribution $\nu$,
then also $W_B(T)/(T+1)\to\nu(B)$ almost surely for every finite $B$.

#### Proof

Use a maximal coupling at each step while the paths agree, conditioning on
the full history of $Y$. The chance of a first mismatch at step $n+1$ is
at most $\delta_n$. The union bound proves (TV). For an infinite tail, the
same construction bounds any mismatch by $\sum_{n\ge N}\delta_n$.
A recurrent reference chain visits each state infinitely often. Failure of
this event for $Y$ therefore has probability at most that tail sum. Let
$N\to\infty$ and take the countable intersection over target states. Apply
the same argument to the reference occupation-time limit in the positive
recurrent case; a finite prefix does not change that limit. QED.

Positive-rate or deadline claims require the corresponding properties of $Q$;
recurrence alone does not supply them. A small constant error is insufficient
asymptotically: perturb a symmetric lazy walk
on $\mathbb Z$ from probabilities $(1/4,1/2,1/4)$ to
$(1/4-\eta,1/2,1/4+\eta)$, $0<\eta<1/4$. Each transition row is only
$\eta$ away in total variation, but nonzero drift makes the perturbed walk
transient. On finite windows (TV) remains useful when its sum is small.
Fitted one-step agreement on a dataset does not establish the uniform
conditional bound required here.

### Registration and estimators

Register the following before examining outcomes:

```text
Full state and why its components matter:
State space, metric, and observation times:
Structural map pi and independent justification:
Fine target A; structural target B; whether A is contained in pi^{-1}(B):
Observable: anchored | historical | discovery
Resolution, exclusion lag, and order of limits:
Markov state, irreducibility, lumpability, and kernel assumptions:
Mathematical claim and proof of each required assumption:
Finite horizon, independent restarts, and uncertainty procedure:
Mechanism intervention and matched null:
Independent functional outcome:
Required structural count/rate, maximum gap, and finite-window error budgets:
```

For $M$ independent restarts from $x$, estimate anchored quantities by

$$
 \widehat p_n(A)=\frac1M\sum_{j=1}^M\mathbf1_{\{X_n^{(j)}\in A\}},\qquad
 \widehat G_T(A)=\sum_{n=1}^T\widehat p_n(A).
$$

The empirical convention excludes time zero; the theoretical Green function
includes it. This finite constant never changes convergence. Bootstrap paths,
preserving fine/structural pairing for paired contrasts. A single long path
is not a collection of independent restarts.

For a path $X_0,\ldots,X_T$, the rate implemented by `historical_flags` is

$$
 \widehat h_T(r,\tau)=\frac1{T-\tau+1}\sum_{n=\tau}^T
 \mathbf1\left\{\min_{0\le j\le n-\tau}d(X_n,X_j)\le r\right\},
 \qquad1\le\tau\le T.
$$

Report full and projected rates separately, together with cell discovery.
Fix scales and lag; specify fixed-resolution or joint-scaling limits.
[cdt_empirical_audit.py](cdt_empirical_audit.py) computes finite diagnostics:

```bash
python cdt_empirical_audit.py paths.npy --epsilon 0.05 --radius 0.5 --lag 10 --projection 0,1
```

The utility uses Euclidean coordinate selection and enforces
`radius > epsilon`; this is an implementation convention, not a hypothesis
of Theorem 1. General projections can use different units in the two spaces.

Finite trajectories do not decide asymptotic recurrence without a justified
model. Compare power, power-with-log, and cutoff alternatives. A zero-event
tail is an estimator floor, not an arbitrarily steep exponent. With zero
affected paths among $M$ independent restarts, the one-sided 95% binomial
upper bound $1-0.05^{1/M}$ concerns the probability of **at least one**
tail-window return. It does not bound the mean count of clustered returns.

## 11. Evidence and remaining work

The [registered ledger](results/cdt_simulation_evidence_ledger.md) records the
2026-09-05 experiments. Data and preregistrations are unchanged. References to
“Theorem 1” in that historical ledger mean the earlier sufficient-condition
formulation, now Lemma 2.

| Claim | Standing |
|---|---|
| Countable transient/recurrent projection criterion | Theorem 1: necessary and sufficient under its assumptions |
| Lazy-coordinate phase boundary | exact model result (P), not inferred from simulation |
| Positive structural return rate | Corollary 1a and the restoring birth–death model; null recurrence alone gives zero frequency |
| Approximate projected dynamics | Proposition 5 under conditional total-variation bounds; small constant error does not guarantee recurrence |
| Brownian hidden drift | exact model result (B); registered discrete experiments are finite-horizon controls for their own model |
| Destination-local-time repulsion through tested $\gamma=10$ | finite-horizon evidence; asymptotic position avoidance and structural recurrence remain unproved |
| General diffusion/capacity extension | needs a separately specified process, targets, and recurrence theorem |
| Life/death, memory benefit, rescue optimality | independent functional/control claims, not established here |

Three high-dimensional registered fits were event-floor failures, not
confirmations. The later [measurement repair](measurement_repair_20260912.md)
also limits the old phase-null, capacity-probe, and novelty-reward claims;
none is used as proof here.

The [application guide](docs/use_cases_and_phenomena.md) gives definitions of
observable phenomena, finite-horizon contracts, and proposed experiments.
Those application hypotheses are not added to the registered evidence ledger.

### Separately frozen application experiments

The [completion ledger](docs/experiment_completion_20261109.md) records twelve
model/application suites and two remaining-phenomena checks, with plans
committed before their execution. The September ledger is unchanged. Positive
model contrasts coexist with a memory-calibration failure, absent anchored
structural matches in the supplied drawings, and task failures under favorable
recurrence counts. The gate experiment measures driven identity reconstruction
and free-run novelty, not autonomous functional recovery. These outcomes
exercise the framework's distinctions without proving the self-repulsion
mechanism or deployment benefit.

The unresolved CDT problem is a model-specific proof that realization-dependent
interaction causes fine avoidance while preserving meaningful structural
recurrence. Classical constructions prove the split is possible. They do not
establish that proposed causal mechanism.

### Mathematical background

The arguments use standard results: irreducible-chain recurrence and the
strong Markov property (Norris, *Markov Chains*); conditional Borel–Cantelli
and martingale laws of large numbers (Williams, *Probability with Martingales*);
Brownian recurrence and polarity (Mörters and Peres, *Brownian Motion*).
For heat-kernel geometry beyond the chains here see
[Grigor'yan and Telcs](https://arxiv.org/abs/1205.5627). General capacity claims
need a specified framework, such as Fukushima, Oshima, and Takeda,
*Dirichlet Forms and Symmetric Markov Processes*.
