"""Create the compact visual audit for the registered CDT simulations."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def main():
    campaign = json.loads((RESULTS / "cdt_simulation_campaign.json").read_text())
    followups = json.loads((RESULTS / "cdt_followups.json").read_text())

    fig, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)

    # A. Product/projection phase map.
    ax = axes[0, 0]
    s1 = campaign["suites"]["S1_projection"]
    unique = {(r["D"], r["m"]): r for r in s1}
    for (D, m), row in unique.items():
        if row["slope"] is None:
            ax.scatter(D, m, marker="x", s=80, color="black")
            ax.text(D + 0.05, m + 0.05, "floor", fontsize=7)
        else:
            color = "#2a9d8f" if m <= 2 < D else "#457b9d"
            ax.scatter(D, m, s=70, color=color)
            ax.text(D + 0.05, m + 0.05, f"{row['slope']:.2f}", fontsize=7)
    ax.axhline(2.5, color="#e76f51", linestyle="--", linewidth=1)
    ax.set(xlabel="full dimension D", ylabel="projection dimension m",
           title="A. Tail-Green slopes (x = event floor)")
    ax.set_xticks(range(1, 7)); ax.set_yticks(range(1, 7))

    # B. D=2 drift causal control at the largest horizon.
    ax = axes[0, 1]
    f1 = [r for r in followups["F1_drift_causal"] if r["horizon"] == 8192]
    for kind, marker in [("hidden", "o"), ("visible", "s")]:
        for observable, style in [("full", "--"), ("projected", "-")]:
            rows = sorted(
                [r for r in f1 if r["kind"] == kind and r["observable"] == observable],
                key=lambda r: r["delta"],
            )
            x = [r["delta"] for r in rows]
            y = [r["ratio_to_neutral"] for r in rows]
            ax.plot(x, y, marker=marker, linestyle=style,
                    label=f"{kind}, {observable}")
    ax.axhline(1, color="black", linewidth=1, alpha=0.5)
    ax.set(xlabel="drift delta", ylabel="tail count / neutral",
           title="B. Hidden drift preserves only the projection")
    ax.set_ylim(-0.05, 1.15); ax.legend(fontsize=8)

    # C. Self-repulsion projected anchored slopes.
    ax = axes[1, 0]
    f2 = [r for r in followups["F2_self_repulsion_observable"]
          if r["horizon"] == 4096]
    for D, color in [(2, "#e76f51"), (3, "#264653")]:
        rows = sorted([r for r in f2 if r["D"] == D], key=lambda r: r["gamma"])
        x = np.array([r["gamma"] for r in rows])
        y = np.array([r["projected_anchored"]["slope"] for r in rows])
        lo = np.array([r["projected_anchored"]["slope_ci_lo"] for r in rows])
        hi = np.array([r["projected_anchored"]["slope_ci_hi"] for r in rows])
        ax.errorbar(x, y, yerr=[y - lo, hi - y], marker="o", capsize=3,
                    color=color, label=f"D={D}")
    ax.axhline(0, color="black", linewidth=1)
    ax.axhline(-0.10, color="#e9c46a", linestyle="--", linewidth=1)
    ax.set(xlabel="self-repulsion gamma", ylabel="projected tail slope",
           title="C. Anchored projection remains finite-horizon compatible")
    ax.legend()

    # D. Finite-capacity exhaustion.
    ax = axes[1, 1]
    s5 = campaign["suites"]["S5_finite_capacity"]
    for (D, L), color in zip([(2, 16), (2, 32), (3, 8), (3, 12)],
                             ["#264653", "#2a9d8f", "#e9c46a", "#e76f51"]):
        rows = [r for r in s5 if r["D"] == D and r["L"] == L]
        ax.plot([r["horizon_per_state"] for r in rows],
                [r["new_state_rate"] for r in rows], marker="o",
                color=color, label=f"D={D}, L={L}")
    ax.set(xlabel="time / number of states", ylabel="new-state rate",
           title="D. Finite capacity exhausts novelty")
    ax.set_yscale("log"); ax.legend(fontsize=8)

    fig.suptitle("Configuration Drift: registered simulation audit", fontsize=16)
    output = RESULTS / "cdt_simulation_summary.png"
    fig.savefig(output, dpi=180)
    print(output)


if __name__ == "__main__":
    main()
