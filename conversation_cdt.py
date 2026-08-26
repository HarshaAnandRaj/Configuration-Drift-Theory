"""conversation_cdt.py
THE SELF-REFERENTIAL TEST: apply Configuration-Drift to the conversation in
which it was developed.

REGISTERED PREDICTIONS (made before reading contents):
  R1 exact message repeats ~ 0            ... unless the trajectory ever
      milled (repetitive loop) -- the instrument would catch THAT instead.
  R2 shared technical vocabulary CRYSTALLIZES: term density rises over time
      (a conversation is engineered rhyme -- refrain-building).
  R3 LADDER: word-level states recurrent, message/theme level transient,
      feature-space nu > 2.
  R4 any period-lock episodes get localized in time (where did we mill?)
"""

import json
import re
import numpy as np

PATH = (r"C:\Users\Anand\Desktop\Projects\Configuration Drift Hypothesis"
        r"\Conversations\unanswered-science-questions-solvable-by-tech.json")

TERMS = ["exact", "rhyme", "drift", "recurrence", "transien", "gamma",
         "lattice", "attractor", "mutation", "pol", "heterozyg",
         "boundary", "phase", "nu"]


def load_texts():
    d = json.load(open(PATH, encoding="utf-8"))
    out = []
    for m in d["messages"]:
        role = m.get("info", {}).get("role", "?")
        txt = " ".join(p["text"] for p in m.get("parts", [])
                       if p.get("type") == "text")
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt.split()) >= 3:
            out.append((role, txt))
    return out


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


def past_recurrence(states):
    seen, hits, cut = set(), [], len(states) // 2
    for i, s in enumerate(states):
        (hits.append(s in seen) if i >= cut else seen.add(s))
    return round(float(np.mean(hits)), 3) if hits else float("nan")


def corr_dim(P):
    lo, hi = np.percentile(P, 1, axis=0), np.percentile(P, 99, axis=0)
    Q = np.clip((P - lo) / (hi - lo + 1e-12), 0, 1)
    diff = Q[:, None, :] - Q[None, :, :]
    d = np.sqrt((diff ** 2).sum(-1))
    iu = np.triu_indices(len(Q), 1)
    dp = d[iu[0], iu[1]]
    qs = np.geomspace(1, 99, 24)
    eps = np.percentile(dp, qs)
    C = np.array([(dp <= e).mean() for e in eps])
    m = (C > 0.02) & (C < 0.90)
    if m.sum() < 5 or dp.max() < 1e-9:
        return float("nan")
    return float(np.polyfit(np.log(eps[m]), np.log(C[m]), 1)[0])


if __name__ == "__main__":
    msgs = load_texts()
    print(f"messages kept: {len(msgs)} "
          f"(user {sum(1 for r,_ in msgs if r=='user')}, "
          f"assistant {sum(1 for r,_ in msgs if r=='assistant')})")

    # ---- R1 exact repeats ----
    print("\n--- R1 exact repeats ---")
    for role in ("user", "assistant"):
        seq = [norm(t) for r, t in msgs if r == role]
        seen, dup = set(), 0
        first_idx = []
        for i, s in enumerate(seq):
            frac = [j for j, (rr, tt) in enumerate(msgs)
                    if rr == role][i] / max(len(msgs), 1)
            if s in seen:
                dup += 1
                first_idx.append(round(frac, 2))
            else:
                seen.add(s)
        print(f"{role:>10}: {dup}/{len(seq)} exact repeats "
              f"({100*dup/len(seq):.1f}%)"
              + (f"  located at positions {first_idx[:12]}"
                 if first_idx else ""))

    # ---- R2 vocabulary crystallization ----
    print("\n--- R2 technical-term density per tertile (per 1k words) ---")
    thirds = [msgs[:len(msgs)//3], msgs[len(msgs)//3:2*len(msgs)//3],
              msgs[2*len(msgs)//3:]]
    base = []
    for third in thirds:
        words = re.findall(r"[a-z]+", " ".join(t.lower() for _, t in third))
        base.append(max(len(words), 1))
    row = []
    for ti, third in enumerate(thirds):
        blob = " ".join(t.lower() for _, t in third)
        cnt = sum(blob.count(tm) for tm in TERMS)
        row.append(round(1000 * cnt / base[ti], 2))
    print("tertiles:", row, "(rising => crystallization)")

    # ---- R3 ladder ----
    print("\n--- R3 recurrence ladder ---")
    toks = re.findall(r"[a-z']+", " ".join(norm(t) for _, t in msgs))
    uni = [(t,) for t in toks]
    bi = list(zip(toks[:-1], toks[1:]))
    tri = list(zip(toks[:-2], toks[1:-1], toks[2:]))
    print("word unigram rec :", past_recurrence(uni))
    print("bigram rec       :", past_recurrence(bi))
    print("trigram rec      :", past_recurrence(tri))

    feats = []
    for r, t in msgs:
        ws = t.split()
        blob = t.lower()
        td = sum(blob.count(tm) for tm in TERMS) / max(len(ws), 1)
        feats.append([len(ws), float(np.mean([len(w) for w in ws])) if ws else 0,
                      int("```" in t), td, int(r == "assistant")])
    F = np.array(feats, dtype=float)
    print("message-feature nu:", round(corr_dim(F), 3),
          "| feature ladder:", end=" ")
    h = len(F) // 2
    lo, hi = np.percentile(F, 1, axis=0), np.percentile(F, 99, axis=0)
    Fn = np.clip((F - lo) / (hi - lo + 1e-12), 0, 1)
    ladd = {}
    for B in (8, 16, 32):
        occ = set(map(tuple, (Fn[:h] * B).astype(int)))
        hits = [c in occ for c in map(tuple, (Fn[h:] * B).astype(int))]
        ladd[B] = round(float(np.mean(hits)), 3)
    print(ladd)

    # ---- R4 period-lock localization ----
    print("\n--- R4 period-lock episodes (consecutive near-duplicates) ---")
    Fn_ = F / (np.linalg.norm(F, axis=1, keepdims=True) + 1e-9)
    sims = (Fn_[1:] * Fn_[:-1]).sum(1)
    streak, episodes = 0, []
    for i, s in enumerate(sims):
        if s > 0.985:
            streak += 1
        else:
            if streak >= 2:
                episodes.append((round(i / len(sims), 2), streak + 1))
            streak = 0
    if streak >= 2:
        episodes.append((round((len(sims)) / len(sims), 2), streak + 1))
    print("episodes (pos_frac, run_length):", episodes if episodes else "none")
