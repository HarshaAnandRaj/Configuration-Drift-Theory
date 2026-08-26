"""genetic_drift.py
Configuration-Drift Hypothesis applied to POPULATION GENETICS.

Mapping:
  configuration      = the population's genetic composition
  realization        = reproduction (sampling noise = genetic drift)
  attraction         = no counter-force: alleles fixate, variation dies
                       (the absorbing collapse -- known since Fisher/Wright)
  gamma > 0          = MUTATION -- the whisper dose of novelty
  heterozygosity     = the recurrence-density whose temporal decay is the
                       classical signature

REGISTERED PREDICTIONS (against published math -- external validation):
  P1  no-mutation absorption times match  E[T] ~ -4N[p ln p + (1-p) ln(1-p)]
      and scale linearly with N.
  P2  heterozygosity decays at rate (1 - 1/(2N)) per generation, so log H
      vs t is linear with slope ln(1 - 1/(2N)).
  P3  with mutation, stationary heterozygosity -> theta/(1+theta), theta=4Nmu;
      the collapse/sustain boundary sits near mu_c = 1/(2N)  (whisper dose).
  P4  sequence-space genomes (L loci, alphabet 4): exact genotype re-creation
      ~ never (curse over 4^L), innovation continues forever with mu>0,
      and Hamming-rhyme returns are common early, decaying as the population
      spreads -- the exact/rhyme split in biology's own substrate.
"""

import numpy as np


def wf_absorption_times(N, p0=0.5, trials=600, tmax_cap=None, seed=0):
    """Diploid Wright-Fisher, no mutation. Returns absorption times."""
    rng = np.random.default_rng(seed)
    G = 2 * N
    ks = rng.binomial(G, p0, size=trials).astype(np.int64)
    T = np.zeros(trials, dtype=np.int64)
    alive = np.ones(trials, dtype=bool)
    cap = tmax_cap or (60 * N)
    for t in range(1, cap):
        act = alive & (ks > 0) & (ks < G)
        if not act.any():
            break
        p = ks[act] / G
        ks[act] = rng.binomial(G, p)
        done = act & ((ks == 0) | (ks == G))
        T[done] = t
        alive[done] = False
    T[alive] = cap
    return T


def wf_stationary_heterozygosity(N, mu, G_gen=150_000, reps=400, seed=1,
                                 burn_frac=0.4):
    """Vectorized replicates; returns late-time mean heterozygosity 2p(1-p)."""
    rng = np.random.default_rng(seed)
    G = 2 * N
    ks = rng.binomial(G, 0.5, size=reps).astype(np.float64)
    burn = int(G_gen * burn_frac)
    acc, acc_n = 0.0, 0
    for t in range(G_gen):
        p = ks / G
        p = p * (1.0 - mu) + (1.0 - p) * mu
        ks = rng.binomial(G, p).astype(np.float64)
        if t >= burn:
            pp = ks / G
            acc += float((2 * pp * (1 - pp)).sum())
            acc_n += reps
    return acc / acc_n


def seq_evolution(P=200, L=48, mu=0.004, G=1200, seed=2, rhyme_r=None,
                  archive_sample=150):
    """Sequence-space population. Returns per-generation records."""
    rng = np.random.default_rng(seed)
    pop = rng.integers(0, 4, size=(P, L))
    rhyme_r = rhyme_r or max(2, L // 8)
    archive = set()
    rec_new, rec_rhyme = [], []
    for g in range(G):
        mut = rng.random(pop.shape) < mu
        cand = pop.copy()
        cand[mut] = rng.integers(0, 4, size=int(mut.sum()))
        new_mask = np.zeros(P, dtype=bool)
        new_hashes = []
        for i in range(P):
            key = cand[i].astype(np.uint8).tobytes()
            if key not in archive:
                new_mask[i] = True
                new_hashes.append((key, cand[i]))
        # rhyme test: how close are NEW genotypes to anything ever lived?
        if new_hashes:
            arch_list = list(archive)
            arch_sample_idx = rng.choice(len(arch_list),
                                         size=min(archive_sample, len(arch_list)),
                                         replace=False) if arch_list else []
            refs = [np.frombuffer(arch_list[j], dtype=np.uint8)
                    for j in arch_sample_idx]
            rhymes = 0
            for _, gt in new_hashes:
                gtu = gt.astype(np.uint8)
                if refs:
                    dm = min(int((gtu != r).sum()) for r in refs)
                    if dm <= rhyme_r:
                        rhymes += 1
            rec_rhyme.append(rhymes / len(new_hashes))
            for key, arr in new_hashes:
                archive.add(key)
        else:
            rec_rhyme.append(0.0)
        rec_new.append(float(new_mask.mean()))
        pop = cand
    return {"archive_size": len(archive),
            "innov_rate_late": float(np.mean(rec_new[len(rec_new) // 2:])),
            "rhyme_early": round(float(np.mean(rec_rhyme[:len(rec_rhyme)//4])), 3),
            "rhyme_late": round(float(np.mean(rec_rhyme[-len(rec_rhyme)//4:])), 3)}


if __name__ == "__main__":
    import math

    print("=========== REGISTERED PREDICTIONS ===========")
    print("P1 absorption ~ -4N[p ln p + (1-p) ln(1-p)], linear in N")
    print("P2 log H decays with slope ln(1 - 1/(2N))")
    print("P3 stationary H -> theta/(1+theta), theta=4Nmu; boundary ~ mu=1/(2N)")
    print("P4 sequence space: innovation forever, exact re-creation ~0,")
    print("   Hamming-rhymes early-rich then decaying")
    print()

    print("=========== P1/P2: pure drift, no mutation ===========")
    print(f"{'N':>5} {'E[T] theory':>12} {'mean T sim':>11} {'ratio':>7} "
          f"{'decay slope':>12} {'theory slope':>13}")
    for N in (16, 64, 256):
        T = wf_absorption_times(N, trials=800, seed=N)
        th = -4 * N * (0.5 * math.log(0.5) * 2)
        # P2: heterozygosity decay slope from unabsorbed early trajectory
        rng = np.random.default_rng(N + 1)
        G = 2 * N
        ks = rng.binomial(G, 0.5, size=400)
        slopes = []
        Hs = []
        for t in range(min(5 * N, 300)):
            p = ks / G
            Hs.append(float((2 * p * (1 - p)).mean()))
            ks = rng.binomial(G, p)
        Hs = np.array(Hs) + 1e-9
        ts = np.arange(len(Hs))
        msk = Hs > 1e-4
        sl = np.polyfit(ts[msk], np.log(Hs[msk]), 1)[0]
        print(f"{N:>5} {th:>12.1f} {T.mean():>11.1f} {T.mean()/th:>7.3f} "
              f"{sl:>12.4f} {math.log(1 - 1/(2*N)):>13.4f}")

    print("\n=========== P3: stationary heterozygosity vs mutation ===========")
    N = 64
    mu_c = 1 / (2 * N)
    print(f"N={N}, mu_c = 1/(2N) = {mu_c:.5f}")
    print(f"{'mu':>9} {'theta':>8} {'H_sim':>8} {'H_theory':>9}  regime")
    for mu in (1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2):
        th = 4 * N * mu
        h_th = th / (1 + th)
        h_sim = wf_stationary_heterozygosity(N, mu)
        reg = "COLLAPSED-side" if mu < mu_c else "SUSTAINED-side"
        print(f"{mu:>9.5f} {th:>8.3f} {h_sim:>8.3f} {h_th:>9.3f}  {reg}")

    print("\n=========== P4: sequence-space genomes ===========")
    res = seq_evolution()
    print(res)
