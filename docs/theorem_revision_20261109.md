# Mathematical revision of Configuration Drift

**Date:** 2026-11-09

**Baseline:** repository commit
[`14c9d020726d293f6f9fd19eb4f7d1c0b5f4b1d7`](https://github.com/HarshaAnandRaj/Configuration-Drift-Theory/commit/14c9d020726d293f6f9fd19eb4f7d1c0b5f4b1d7)

The [canonical statement](../configuration_drift_theorem.md) has been rebuilt
around a question that admits a precise answer: when can a full process leave
fixed fine targets while its structural projection keeps returning?

## What needed repair

The previous canonical file already rejected the universal life/death formula,
distinguished anchored and historical recurrence, and warned against treating
finite simulations as proofs. Those corrections remain.

Its principal theorem was a valid sufficient-condition lemma: finite expected
fine visits plus assumed almost-sure structural recurrence imply the split.
It did not derive structural recurrence or characterize when the split holds.
The capacity statement also left its capacity convention and exceptional
starting states unspecified. The broad diffusion/spectral language did not
fully expose the difference between transition densities and target returns.

## What the revision establishes

| Change | Reason and scope |
|---|---|
| Necessary-and-sufficient countable-chain theorem | Irreducibility, finite targets, and a strongly lumpable projection make Green convergence/divergence equivalent to almost-sure anchored separation. |
| Renewal proof | Shows why divergent expected visits imply recurrence for these chains, instead of treating this as valid for every process. |
| Infinite-fiber consequence | A recurrent structural state must aggregate infinitely many full states of the transient chain. This makes the required target geometry explicit. |
| Exact lazy product construction | The return kernel is `binom(2n,n)/4^n` per coordinate; separation holds exactly for `m <= 2 < D`. Laziness removes periodicity complications. |
| General sufficient lemma retained | The former principal theorem remains available for non-Markov processes, with the separate structural recurrence obligation visible. |
| Last-return probability bound | A summable fine return tail bounds the probability of any later fine return, providing a quantitative consequence. |
| Heavy-tail counterexample | A finite visit count can have infinite expectation; divergent Green-like sums alone are not a general recurrence theorem. |
| Brownian classification | Full escape and structural recurrence hold exactly when `(v != 0 or d >= 3)`, `Pv = 0`, and `1 <= rank(P) <= 2`, under the specified nondegenerate isotropic model. |
| Capacity claim narrowed | The planar point/neighborhood example remains; no unqualified general Hunt-process theorem is asserted. |
| Conditional Borel–Cantelli | Historical avoidance is characterized by the pathwise sum of predictable event probabilities; no deterministic summable envelope is necessary. |
| Augmented-state warning | Local-time records and clocks can prevent exact augmented-state recurrence even for neutral position dynamics. This is not a proof of position avoidance or useful behavior. |
| Empirical indexing fixed | For a path indexed `0,...,T`, the lagged historical diagnostic uses times `tau,...,T` and denominator `T-tau+1`, matching `historical_flags`. |

The product and Brownian results are applications of classical probability.
The revision makes no claim that CDT introduced the recurrence classification,
the product construction, conditional Borel–Cantelli, or Brownian polarity.

## What is deliberately not claimed

- No general theorem that any positive local-time repulsion makes position
  transient while preserving structural recurrence.
- No inference from a trajectory-cloud dimension directly to a substrate
  heat-kernel exponent, or from a limiting spectral exponent alone at two.
- No general diffusion recurrence criterion from on-diagonal density alone.
- No general capacity conclusion without a specified capacity, process,
  exceptional starting states, and recurrence assumptions.
- No equivalence between recurrence separation and life, memory quality,
  adaptive functional recovery, or optimal control.

The older model-family survey is not treated as an additional proof source.
In particular, the informal fractional-Brownian threshold is not carried
forward as a canonical theorem without a specified hitting/recurrence result.
The notebook and Git history retain the earlier discussion.

## Evidence preserved

The scripts, frozen preregistrations, recorded experiment data, evidence ledger,
figures, and checksums are unchanged. The ledger's historical “Theorem 1”
references refer to the previous sufficient condition, now Lemma 2. Existing
finite-horizon self-repulsion results retain their evidential status, including
the rare-event floor limitations. No new simulation campaign has been run or
retroactively registered.

The unresolved research target is to prove fine position avoidance and
structural recurrence under a specified realization-dependent interaction,
then test whether that interaction improves an independently measured function.

## Validation

Validation covers the existing finite-horizon diagnostics, simulation harness,
and registered-result consistency. Numerical checks of the lazy-walk return
identity check algebra at finite horizons; they do not prove infinite-time
recurrence. The proofs and their stated hypotheses carry that conclusion.

Checks completed for this revision:

- All 19 tests in the three suites below passed; both Python modules compiled.
- Exact rational convolution matched the one-coordinate return formula for
  every horizon `n=1,...,32`.
- Direct enumeration of the three-coordinate product matched full returns
  and one-/two-coordinate projected returns for `n=1,...,4`.
- Revised-document local links, math delimiters, and diff whitespace passed.

The revised theorem and README use GitHub's dollar-delimited math syntax.

Run the repository checks with:

```bash
python -m unittest -v test_cdt_empirical_audit.py test_cdt_simulation_campaign.py test_cdt_registered_results.py
python -m py_compile cdt_empirical_audit.py experiments/cdt_simulation_campaign.py
git diff --check
```
