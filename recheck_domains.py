"""recheck_domains.py -- re-run domain nu-numbers with corrected rules.

Old code used the saturation-including band (C to 0.90) and assumed d_w = 2.
This recheck uses debias_nu.nu_local + bootstrap CI and gates every verdict by
the fix-2 floor N >= 100*10**(nu/2) at the upper CI bound. Direct-measurement
claims (ladders, concentrations, exact-repeat fractions) are unaffected; only
nu-threshold verdicts are re-examined.

Covers: Lorenz, prose, SGD halves, celestial A/B, conversation message-features.
"""
import os
import numpy as np

import apply_domains as A
import celestial as C
import conversation_cdt as T
from debias_nu import nu_local_ci, n_floor

HERE = os.path.dirname(os.path.abspath(__file__))


def check(E, label, dw=2.0):
    E = np.asarray(E, dtype=float)
    E = E[np.isfinite(E).all(axis=1)]
    est, lo, hi = nu_local_ci(E, B=12, seed=11)
    fl = n_floor(hi)
    ok = len(E) >= fl
    v = "recurrent" if est <= dw else "transient"
    print(f"{label:<34} n={len(E):<5} nu={est:5.2f} CI=[{lo:5.2f},{hi:5.2f}] "
          f"floor={fl:<5} d_w={dw:4.2f} -> {v if ok else 'UNDECIDABLE'}")
    return est, (v if ok else "UNDECIDABLE")


if __name__ == "__main__":
    print("=== corrected domain recheck (nu_local + CI + floors) ===\n")
    P = A.lorenz()
    check(P, "Lorenz attractor (lit ~2.06)")
    F, info = A.prose(os.path.join(HERE, "configuration_drift_full_report.md"))
    print(f"  prose: {info['sentences']} sentences, "
          f"sent-repeat={info['exact_sent_repeat_frac']}, "
          f"uni/bi-rec={info['unigram_rec']}/{info['bigram_rec']}")
    check(F, "prose sentence-features")
    Wt, _, _ = A.sgd_traj()
    h = len(Wt) // 2
    check(Wt[:h], "SGD weights early half")
    check(Wt[h:], "SGD weights late half")
    tr, _ = C.simulate(masses=[1.0, 1e-6, 1e-6], pos0=[[0, 0], [1, 0], [1.5874, 0]],
                       vel0=[[0, 0], [0, 2 * np.pi], [0, 2 * np.pi / np.sqrt(1.5874)]])
    check(np.asarray(tr), "celestial A regular")
    tr, _ = C.simulate(masses=[1.0, 0.01, 0.01], pos0=[[0, 0], [1, 0], [1.25, 0]],
                       vel0=[[0, 0], [0, 2 * np.pi],
                             [0, 2 * np.pi / np.sqrt(1.25) * 1.03]])
    check(np.asarray(tr), "celestial B chaotic")
    msgs = T.load_texts()
    feats = []
    for r, t in msgs:
        ws = t.split()
        blob = t.lower()
        td = sum(blob.count(tm) for tm in T.TERMS) / max(len(ws), 1)
        feats.append([len(ws), float(np.mean([len(w) for w in ws])) if ws else 0,
                      int("```" in t), td, int(r == "assistant")])
    check(np.array(feats, dtype=float),
          f"conversation message-features ({len(msgs)} msgs)")
    print("\nDone. Ladders/concentrations/repeat-fractions stand independently;"
          " only nu-threshold verdicts above are affected by floors.")
