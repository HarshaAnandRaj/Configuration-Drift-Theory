"""Execute the separately frozen long-tail and bookkeeping checks."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'experiments/cdt_phenomena_followup_plan_20261109.md'
PLAN_HASH = '8c831999213ac55a15e9c86e1b47e0ffbc48158195d377028a9439580ad15172'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = ROOT / 'results/phenomena_followup_20261109'
    if out.exists():
        raise RuntimeError('refusing to overwrite evidence')
    if sha(PLAN) != PLAN_HASH:
        raise RuntimeError('frozen follow-up plan changed')
    out.mkdir()
    manifest = {'started_at': datetime.now(timezone.utc).isoformat(),
                'plan_commit': '02f1b003571cb514c5789740adf9c4ec51330899',
                'plan_sha256': sha(PLAN), 'source_sha256': sha(__file__),
                'numpy': np.__version__, 'python': platform.python_version()}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    n = np.arange(1, 65537, dtype=float)
    b = np.cumprod((2 * n - 1) / (2 * n))
    analytic = []
    raw, rows = [], []
    for D in [3, 4, 5]:
        weighted = np.cumsum(n * b ** D)
        for N in [256, 1024, 4096, 16384, 65536]:
            analytic.append({'D': D, 'horizon': N, 'partial_weighted_Green': float(weighted[N - 1])})
        for rep in range(16):
            seed = 20391110 + D * 1000 + rep
            rng = np.random.default_rng(seed)
            position = np.zeros((512, D), dtype=np.int32)
            last = np.zeros(512, dtype=int)
            returns = np.zeros(512, dtype=int)
            halves = {}
            for t in range(1, 4097):
                u = rng.integers(0, 4, size=position.shape)
                position += np.where(u == 0, -1, np.where(u == 1, 1, 0))
                hit = np.all(position == 0, axis=1)
                last[hit] = t
                returns += hit
                if t in [128, 512, 2048]:
                    halves[t] = returns.copy()
                if t in [256, 1024, 4096]:
                    tail = returns - halves[t // 2]
                    raw.append({'D': D, 'replicate': rep, 'seed': seed, 'horizon': t,
                                'last_observed_visit': last.tolist(), 'late_return_count': tail.tolist()})
                    rows.append({'D': D, 'replicate': rep, 'horizon': t,
                                 'last_observed_mean': float(last.mean()),
                                 'late_affected_paths': int(np.sum(tail > 0)),
                                 'late_return_count_mean': float(tail.mean())})
        print(f'Finished long-tail dimension {D}', flush=True)
    (out / 'long_tail_raw.json').write_text(json.dumps(raw, indent=2) + '\n')
    (out / 'long_tail_summary.json').write_text(json.dumps({'monte_carlo': rows, 'analytic_partial_sums': analytic}, indent=2) + '\n')
    bookkeeping = []
    for mode in ['constant', 'period_two']:
        n = np.arange(257)
        x = np.zeros(257, dtype=int) if mode == 'constant' else n % 2
        for kind, path in [('raw', x[:, None]), ('clock_augmented', np.column_stack([x, n])),
                           ('projected_without_clock', x[:, None])]:
            anchored = np.all(path[1:] == path[0], axis=1)
            historical = [bool(np.any(np.all(path[:t - 1] == path[t], axis=1))) for t in range(2, 257)]
            bookkeeping.append({'case': mode, 'representation': kind,
                                'unique_states': len(set(map(tuple, path))),
                                'anchored_visits_excluding_t0': int(anchored.sum()),
                                'lag2_historical_fraction': float(np.mean(historical))})
    (out / 'bookkeeping.json').write_text(json.dumps(bookkeeping, indent=2) + '\n')
    lines = ['# Remaining-phenomena follow-up results', '',
             'The follow-up plan was committed before execution as `02f1b003`.',
             'The Monte Carlo last visits below are censored observations, not the',
             'true last-exit distribution or estimates of an infinite mean.', '',
             '| Dimension | Horizon | Mean last observed visit | Late-affected paths / 8192 |',
             '|---|---:|---:|---:|']
    for D in [3, 4, 5]:
        for N in [256, 1024, 4096]:
            group = [r for r in rows if r['D'] == D and r['horizon'] == N]
            lines.append(f"| {D} | {N} | {np.mean([r['last_observed_mean'] for r in group]):.4f} | {sum(r['late_affected_paths'] for r in group)} / 8192 |")
    lines += ['', 'High-dimensional tails hit event floors. A missing late event cannot',
              'establish saturation of the mean or decide recurrence.', '',
              '| Dimension | Partial weighted Green sum at 256 | At 4096 | At 65536 |',
              '|---|---:|---:|---:|']
    for D in [3, 4, 5]:
        vals = [next(r['partial_weighted_Green'] for r in analytic if r['D'] == D and r['horizon'] == N) for N in [256, 4096, 65536]]
        lines.append(f"| {D} | {vals[0]:.5f} | {vals[1]:.5f} | {vals[2]:.5f} |")
    lines += ['', 'These deterministic partial sums use the analytic return formula.',
              'The asymptotic series test, not finite numerical growth, proves infinite',
              'mean last exit for dimensions three/four and finite mean for dimension five.', '',
              '| Behavior | Representation | Unique states | Anchored visits after t=0 | Historical lag-2 fraction |',
              '|---|---|---:|---:|---:|']
    for r in bookkeeping:
        lines.append(f"| {r['case']} | {r['representation']} | {r['unique_states']} | {r['anchored_visits_excluding_t0']} | {r['lag2_historical_fraction']:.1f} |")
    lines += ['', 'Appending a clock manufactures novelty in both behaviors. Discarding it',
              'restores the original recurrence measurements. Neither behavior nor task',
              'performance improved. This is an explicit negative control for interpreting',
              'augmented-state transience as a mechanism.', '']
    (out / 'evidence_ledger.md').write_text('\n'.join(lines))
    manifest['finished_at'] = datetime.now(timezone.utc).isoformat()
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (out / 'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))


if __name__ == '__main__':
    main()
