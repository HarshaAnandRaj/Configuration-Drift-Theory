"""scale_gamma.py -- is the 0.4 neutral deadband valid across ambient dimension?
gamma_hat (phase... steps null) on emergent walks D=2/3/4, gamma=+0.8/0/-0.8.
Expect HOLD/neutral/VIOLATED pattern at every D if the deadband is universal.
"""
from emergent_walk import emergent_walk
from gamma_probe import gamma_hat, _capped_walk

for D in (2, 3, 4):
    for g in (0.8, 0.0, -0.8):
        seed = 31000 + D * 131 + int(g * 10)
        X = emergent_walk(D, g, 4000, seed=seed) if g >= 0 else \
            _capped_walk(D, g, 4000, seed=seed)
        r = gamma_hat(X, seed=5)
        v = "HOLDS" if (r["est"] > 0.4 and r["lo"] > 0) else \
            ("VIOLATED" if r["hi"] < 0 else "neutral")
        print(f"D={D} gamma={g:+.1f}: hat={r['est']:+.3f} "
              f"CI=[{r['lo']:+.3f},{r['hi']:+.3f}] rhyme={r['rhyme']:.3f} -> {v}")
