"""Summarize the frozen CDT application campaign without retuning its tests."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from math import comb
from pathlib import Path

import numpy as np


CONTRASTS = {
    'A1': ('Restoring minus free tail frequency', .25),
    'A2': ('Hidden minus visible tail visits', 3.),
    'A3': ('Visible minus hidden neural MSE', .05),
    'A4': ('Structural minus raw memory accuracy', .25),
    'A5': ('Pause minus baseline longest gap', 64.),
    'A6': ('Restricted minus full sensor RMSE', .5),
    'A7': ('Structural minus random gesture accuracy', .25),
    'A8': ('Neutral minus repelled historical rate', .1),
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sign_tail(successes, n):
    return sum(comb(n, k) for k in range(successes, n + 1)) / 2 ** n


def mean_ci(values, rng):
    values = np.asarray(values, dtype=float)
    draws = rng.choice(values, size=(2000, len(values)), replace=True).mean(axis=1)
    return [float(values.mean()), float(np.quantile(draws, .025)), float(np.quantile(draws, .975))]


def arm_summary(records):
    grouped = {}
    for record in records:
        for arm in record.get('arms', []):
            keys = [k for k in ['arm', 'mode', 'D', 'gamma', 'horizon', 'case', 'null',
                                'lambda', 'learned_gates', 'nuisance_shift', 'signal_changed'] if k in arm]
            key = ', '.join(f'{k}={arm[k]}' for k in keys)
            group = grouped.setdefault(key, {'identity': {k: arm[k] for k in keys}, 'rows': []})
            group['rows'].append(arm)
    result = []
    for key, group in grouped.items():
        rows = group['rows']
        numeric = sorted({k for r in rows for k, v in r.items()
                          if isinstance(v, (int, float, bool)) and k not in group['identity']})
        means = {k: float(np.mean([r[k] for r in rows if isinstance(r.get(k), (int, float, bool))]))
                 for k in numeric}
        result.append({'key': key, **group['identity'], 'n': len(rows), 'means': means})
    return result


def select(groups, **identity):
    rows = [g for g in groups if all(g.get(k) == v for k, v in identity.items())]
    if len(rows) != 1:
        raise ValueError(f'ambiguous selection: {identity}')
    return rows[0]['means']


def summarize(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['smoke_only']:
        raise ValueError('smoke outputs cannot be summarized as evidence')
    suites = {}
    for i in range(1, 13):
        suite = f'A{i}'
        data = json.loads((directory / (suite + '.json')).read_text())
        if data['smoke_only'] or any('error' in r for r in data['records']):
            raise ValueError(f'{suite}: incomplete or smoke evidence')
        expected = 1 if i in [9, 10] else (8 if i == 12 else 16)
        if len(data['records']) != expected:
            raise ValueError(f'{suite}: unexpected replicate count')
        suites[suite] = data
    rng = np.random.default_rng(20261111)
    primary = []
    for suite, (label, margin) in CONTRASTS.items():
        records = suites[suite]['records']
        values = np.array([r['primary_effect'] for r in records])
        if not np.all(np.isfinite(values)):
            raise ValueError(f'{suite}: nonfinite primary outcome')
        successes = int(np.sum(values > margin))
        p = sign_tail(successes, len(values))
        row = {'suite': suite, 'contrast': label, 'margin': margin, 'n': len(values),
               'effect_mean_ci95': mean_ci(values, rng), 'exceeding_margin': successes,
               'sign_p_one_sided': p, 'bonferroni_p': min(1, 8 * p),
               'primary_supported': 8 * p < .05}
        if 'functional_pass' in records[0]:
            row['functional_passes'] = sum(r['functional_pass'] for r in records)
        primary.append(row)
    result = {'primary': primary,
              'arm_summaries': {s: arm_summary(data['records']) for s, data in suites.items()},
              'drawing_recordings': suites['A10']['records'][0]['recordings'],
              'exact_TV': suites['A9']['records'][0],
              'inference': 'Eight exact sign tests with Bonferroni correction; bootstrap intervals descriptive.',
              'scope': 'Controlled model campaign plus two unlabeled drawing recordings; no deployment validation.'}
    (directory / 'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    with (directory / 'primary_results.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['suite', 'contrast', 'margin', 'mean', 'ci95_low', 'ci95_high',
                         'replicates_above_margin', 'n', 'bonferroni_p', 'functional_passes'])
        for r in primary:
            writer.writerow([r['suite'], r['contrast'], r['margin'], *r['effect_mean_ci95'],
                             r['exceeding_margin'], r['n'], r['bonferroni_p'], r.get('functional_passes', '')])
    return result, suites, manifest


def write_report(directory, result, suites, manifest):
    a = result['arm_summaries']
    p = result['primary']
    passed = sum(r['primary_supported'] for r in p)
    lines = [
        '# CDT application campaign: results and completion ledger', '',
        f"Run started: `{manifest['started_at']}`; finished: `{manifest['finished_at']}`.", '',
        'The twelve planned suites completed. These are controlled model tests plus',
        'two unlabeled drawing recordings, not real-world deployment validations.',
        'The plan was committed before execution as',
        f"[`{manifest['plan_commit'][:7]}`](https://github.com/HarshaAnandRaj/Configuration-Drift-Theory/commit/{manifest['plan_commit']}).",
        'All arms and independent-replicate records are retained in `A1.json` through',
        '`A12.json`. Smoke runs are excluded. September evidence is unchanged.', '',
        '## Registered primary results', '',
        f'{passed}/8 primary contrasts met the registered sign-test criterion after',
        'Bonferroni correction. That supports the specified *model contrasts*, not a',
        'universal mechanism. CIs below are descriptive bootstrap intervals across',
        'independent replicates. Sign tests ask whether the effect exceeds its',
        'registered margin more often than half the time; units differ by row.', '',
        '| Suite | Contrast | Mean effect [95% CI] | Margin | Replicates above margin | Adjusted p | Functional checks |',
        '|---|---|---:|---:|---:|---:|---|',
    ]
    for row in p:
        m, lo, hi = row['effect_mean_ci95']
        functional = f"{row['functional_passes']}/{row['n']}" if 'functional_passes' in row else 'not an application task'
        lines.append(f"| {row['suite']} | {row['contrast']} | {m:.5g} [{lo:.5g}, {hi:.5g}] | {row['margin']:g} | {row['exceeding_margin']}/{row['n']} | {row['bonferroni_p']:.5g} | {functional} |")
    lines += ['', 'A favorable contrast does not override a failed functional check. Training',
              'and test distributions, nuisance coordinates, and task labels are specified',
              'by these synthetic models; applicability to real systems remains untested.', '',
              '## A1–A2: recurrence rate and projected drift', '',
              '| Structural law | Mean last-half frequency at 4096 | Mean longest observed miss run |',
              '|---|---:|---:|']
    for mode in ['restoring', 'free', 'visible_drift']:
        x = select(a['A1'], mode=mode, horizon=4096)
        lines.append(f"| {mode} | {x['structural_tail_frequency_mean']:.5f} | {x['longest_structural_miss_run_mean']:.2f} |")
    lines += ['', 'The positive-rate example still has long gaps. Return rate and deadline',
              'performance must be reported separately. For A2, the Gaussian cutoff scale',
              'is 312.5 steps at visible drift 0.08 and noise variance one.', '',
              '| A2 arm | Projected last-half visits at 4096 | Full last-half visits |',
              '|---|---:|---:|']
    for mode in ['neutral', 'hidden', 'visible']:
        x = select(a['A2'], arm=mode, horizon=4096)
        lines.append(f"| {mode} | {x['structural_tail_mean']:.5f} | {x['full_tail_mean']:.5f} |")
    lines += ['', 'Zero tail events remain finite-horizon detection floors; the analytic',
              'model, not those zeros, establishes transience.', '',
              '## A3–A7: application models', '',
              '### Autonomous recurrent neural model', '',
              '| Intervention | Held-out waveform MSE | Structural cadence-hit fraction | Full cadence-hit fraction |',
              '|---|---:|---:|---:|']
    for mode in ['baseline', 'hidden_noise', 'visible_noise']:
        x = select(a['A3'], arm=mode)
        lines.append(f"| {mode} | {x['waveform_mse']:.5g} | {x['structural_cadence_hit_fraction']:.4f} | {x['full_cadence_hit_fraction']:.4f} |")
    lines += ['', 'The recurrence matrix and task decoder were fitted on independent training',
              'states; evaluation was autonomous after initialization. This is a linear',
              'oscillator with known invariant subspaces, not a general nonlinear RNN or',
              'a learned adaptive-dimensional recovery demonstration.', '',
              '### Memory under changed context', '',
              '| Map | Retrieval accuracy | Positive-pair acceptance | Negative-pair false acceptance |',
              '|---|---:|---:|---:|']
    for mode in ['raw', 'structure', 'random8', 'constant']:
        x = select(a['A4'], arm=mode)
        lines.append(f"| {mode} | {x['accuracy']:.4f} | {x['positive_acceptance']:.4f} | {x['negative_false_acceptance']:.4f} |")
    failed_memory = [r['replicate'] for r in suites['A4']['records'] if not r['functional_pass']]
    lines += ['', f'Memory replicates failing any registered functional check: `{failed_memory}`.',
              'The raw score improvement is not a substitute for acceptance calibration.',
              'Constant-map acceptance is deliberately exposed as a false semantic match.', '',
              '### Gait timing and order', '',
              '| Intervention | Structural fraction | Longest miss run | Ordered transitions | Tracking MSE |',
              '|---|---:|---:|---:|---:|']
    for mode in ['baseline', 'translated', 'faster', 'pause', 'reverse', 'constant']:
        x = select(a['A5'], arm=mode)
        order = f"{x['ordered_transition_fraction']:.4f}" if 'ordered_transition_fraction' in x else 'undefined'
        lines.append(f"| {mode} | {x['structural_fraction']:.4f} | {x['longest_miss']:.2f} | {order} | {x['phase_tracking_mse']:.5g} |")
    lines += ['', 'This is kinematic phase tracking. It cannot measure real falls, body',
              'stability, contact forces, or physical energy. Reversed or constant',
              'representations can have favorable recurrence counts and fail the task.', '',
              '### Sensor nuisance shift', '',
              '| Readout | RMSE after nuisance shift | Sign accuracy after actual signal change |',
              '|---|---:|---:|']
    for mode in ['full', 'restricted', 'constant']:
        base = select(a['A6'], arm=mode, nuisance_shift=4, signal_changed=False)
        changed = select(a['A6'], arm=mode, nuisance_shift=4, signal_changed=True)
        lines.append(f"| {mode} | {base['rmse']:.5g} | {changed['sign_accuracy']:.4f} |")
    lines += ['', 'The full readout is calibrated on separate samples of a specified linear',
              'mixing model. It demonstrates that nuisance rejection can coexist with',
              'sensitivity to true changes; it does not establish real instrument accuracy.', '',
              '### Synthetic shapes and traversal direction', '',
              '| Representation | Held-out six-class accuracy |', '|---|---:|']
    for mode in ['raw', 'structure', 'random9', 'shape_only', 'constant', 'structure_point_order_permuted']:
        x = select(a['A7'], arm=mode)
        lines.append(f"| {mode} | {x['accuracy']:.4f} |")
    lines += ['', 'Labels distinguish circle/ellipse/triangle and traversal direction. The',
              'signed-area feature preserves the task-relevant direction distinction;',
              'a shape-only map deliberately loses it. Point-order permutation preserves',
              'the point cloud but changes the action.', '',
              '## A8–A11: mechanism, robustness, recordings, and diagnostic', '',
              '| Dimension | Gamma | Full historical rate | Projected historical rate | Full anchored tail count | Discovery fraction |',
              '|---|---:|---:|---:|---:|---:|']
    for D in [2, 3]:
        for gamma in [-.5, 0, .5, 2, 10]:
            x = select(a['A8'], D=D, gamma=gamma)
            lines.append(f"| {D} | {gamma:g} | {x['full_historical']:.4f} | {x['projected_historical']:.4f} | {x['full_anchored_count']:.4f} | {x['discovery_fraction']:.4f} |")
    lines += ['', 'Self-repulsion and attraction change finite historical recurrence. Anchored',
              'and historical measurements remain separate. This repeats a model-specific',
              'finite-horizon effect and does not prove asymptotic position avoidance.', '',
              f"A9 exact six-step path TV: `{result['exact_TV']['exact_path_TV']}`;",
              f"sum bound: `{result['exact_TV']['exact_sum_bound']}`; bound holds:",
              f"`{result['exact_TV']['bound_holds']}`. Small constant errors remain an",
              'analytic counterexample to universal recurrence preservation.', '',
              '### Supplied drawing recordings (descriptive only)', '',
              '| File | Strokes | Fine anchored fraction | Structural anchored fraction | Structural historical fraction | Permuted anchored fraction |',
              '|---|---:|---:|---:|---:|---:|']
    for r in result['drawing_recordings']:
        lines.append(f"| {r['file']} | {r['strokes']} | {r['raw_anchor_fraction_excluding_first']:.4f} | {r['structural_anchor_fraction_excluding_first']:.4f} | {r['structural_historical_fraction']:.4f} | {r['permuted_anchor_fraction']:.4f} |")
    lines += ['', 'Each stroke is closed and resampled by arc length to 64 points; centering,',
              'RMS scale normalization, Fourier magnitudes, and signed area define the',
              'structural map. There are no independent gesture-class labels or subject',
              'metadata, so these fractions cannot establish semantic discrimination,',
              'population uncertainty, or a realization-induced causal mechanism.', '',
              'At the registered structural tolerance, neither recording returned to its',
              'first-stroke anchor. High historical matching refers to other strokes and',
              'must not be cited as evidence of anchored structural recurrence.', '',
              '### Repaired diagnostic on processes without local-time repulsion', '',
              '| Process | Null | Mean diagnostic estimate | Obsolete 0.4-rule positive fraction |',
              '|---|---|---:|---:|']
    for case in ['iid', 'AR08', 'walk', 'drift']:
        for null in ['phase', 'steps']:
            x = select(a['A11'], case=case, null=null)
            lines.append(f"| {case} | {null} | {x['est']:.4f} | {x['obsolete_rule_positive']:.4f} |")
    lines += ['', 'These rates are not calibrated false-positive rates. They demonstrate the',
              'behavior of the repaired instrument under specified null processes.',
              'Neither sign nor the obsolete threshold identifies microscopic repulsion.', '',
              '## A12: self-selected gates versus fixed gates', '',
              '| Lambda | Gates learned | Held-out driven MSE | Free-run new-cell fraction | Mean gate sum | Mean open-gate count |',
              '|---|---|---:|---:|---:|---:|']
    for learned, lam in [(True, 0), (True, .01), (True, .05), (True, .2), (False, 0), (False, .05)]:
        x = select(a['A12'], learned_gates=learned, **{'lambda': lam})
        lines.append(f"| {lam:g} | {learned} | {x['heldout_driven_mse']:.5g} | {x['free_run_new_cell_fraction']:.4f} | {x['gate_sum']:.4f} | {x['open_gate_count']:.3f} |")
    lines += ['', 'The gates are actually optimized in learned arms and exactly frozen at',
              '0.5 in fixed arms. The task is driven input reconstruction; free-run',
              'novelty is not a functional memory score. This experiment cannot establish',
              'autonomous adaptive recovery, and novelty increases alone are not success.', '',
              'Open-gate count uses the legacy strict threshold g > 0.5. Fixed controls',
              'therefore report zero above-threshold gates while all eight gates remain',
              'half open (gate sum four); zero here does not mean zero active capacity.', '',
              '## Completion and blockers', '',
              '| Goal | Experiment completed | Remaining limit |', '|---|---|---|',
              '| Rates, drift, approximate kernels | A1, A2, A9 | Specified stochastic models only; no finite proof of a new asymptotic law. |',
              '| Neural state preservation | A3 | Linear recurrent model; nonlinear/deployment task validation needs a specified task and data. |',
              '| Memory retrieval | A4 | Synthetic labeled task; retain the failed functional check(s). |',
              '| Locomotion | A5 kinematic control | Physical stability, falls, and energy need hardware or a validated dynamic simulator/controller. |',
              '| Sensor invariance | A6 calibration model | Real instrument/reference calibration data absent. |',
              '| Repeated form | A7 labeled synthetic actions; A10 both supplied recordings | Real action discrimination needs class labels, independent participants, and acquisition metadata. |',
              '| Local-time mechanism | A8 | Asymptotic avoidance and projected recurrence still require a model-specific proof. |',
              '| Repaired recurrence score | A11 | No transferable gamma or alive/dead threshold established. |',
              '| Learned dimensional gates | A12 | Identity-task probe is not autonomous functional recovery. |',
              '', 'All twelve feasible suites have recorded results. The blocked deployment',
              'and proof claims have not been replaced by synthetic evidence.', '',
              '## Reproduction and integrity', '',
              '```bash',
              'python experiments/cdt_application_campaign.py --output-dir /tmp/cdt_application_reproduction',
              'python experiments/summarize_cdt_applications.py --input-dir /tmp/cdt_application_reproduction',
              '```', '',
              'The runner refuses to overwrite suite evidence. `manifest.json` hashes',
              'the frozen plan and executable sources. `analysis_manifest.json` records',
              'summary inputs and analysis code. `SHA256SUMS.txt` covers raw records and',
              'derived files. Bootstrap intervals and sample outcomes may be regenerated',
              'with the recorded versions and seeds.', '',
              'Baseline audit: `baseline_integrity.json` separately records that all old',
              'evidence bytes match the original repository commit. Two old summary-file',
              'checksums correspond to CRLF while their committed files use LF. This',
              'pre-existing discrepancy is disclosed; no old file or checksum is edited.', '']
    (directory / 'evidence_ledger.md').write_text('\n'.join(lines))


def plot(directory, result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    a = result['arm_summaries']
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    modes = ['restoring', 'free', 'visible_drift']
    axes[0, 0].bar(modes, [select(a['A1'], mode=m, horizon=4096)['structural_tail_frequency_mean'] for m in modes])
    axes[0, 0].set(title='A1: structural returns in the last half', ylabel='Mean visit fraction')
    axes[0, 0].axhline(1 / 3, ls='--', color='black', lw=1, label='Restoring analytic limit 1/3')
    axes[0, 0].legend(fontsize=8)
    names = ['structure', 'raw', 'random', 'constant']
    xx = np.arange(4)
    memory = [select(a['A4'], arm=m)['accuracy'] for m in ['structure', 'raw', 'random8', 'constant']]
    gestures = [select(a['A7'], arm=m)['accuracy'] for m in ['structure', 'raw', 'random9', 'constant']]
    axes[0, 1].bar(xx - .18, memory, .36, label='Synthetic memory')
    axes[0, 1].bar(xx + .18, gestures, .36, label='Synthetic gestures')
    axes[0, 1].set(xticks=xx, xticklabels=names, ylim=(0, 1.05), ylabel='Mean held-out accuracy', title='A4/A7: recurrence must preserve distinctions')
    axes[0, 1].legend(fontsize=8)
    for g in a['A12']:
        m = g['means']
        axes[1, 0].scatter(m['free_run_new_cell_fraction'], m['heldout_driven_mse'],
                           marker='o' if g['learned_gates'] else 'x', s=60)
        offset = (-74, -3) if g['lambda'] == .2 else ((5, -13) if g['learned_gates'] and g['lambda'] == 0 else (5, 5))
        axes[1, 0].annotate(f"{'learned' if g['learned_gates'] else 'fixed'} {g['lambda']}",
                            (m['free_run_new_cell_fraction'], m['heldout_driven_mse']),
                            xytext=offset, textcoords='offset points', fontsize=7)
    axes[1, 0].set(xlabel='Free-run new-cell fraction', ylabel='Held-out driven MSE',
                    title='A12: novelty is separate from task quality', yscale='log')
    gate_mse = [g['means']['heldout_driven_mse'] for g in a['A12']]
    axes[1, 0].set_ylim(min(gate_mse) * .8, max(gate_mse) * 1.15)
    cases = ['iid', 'AR08', 'walk', 'drift']
    for off, null in [(-.17, 'phase'), (.17, 'steps')]:
        axes[1, 1].bar(np.arange(4) + off, [select(a['A11'], case=c, null=null)['est'] for c in cases], .34, label=null)
    axes[1, 1].set(xticks=np.arange(4), xticklabels=cases, ylabel='Mean exploratory score', title='A11: diagnostic depends on the null')
    axes[1, 1].axhline(0, color='black', lw=.7)
    axes[1, 1].set_yscale('symlog', linthresh=.2)
    axes[1, 1].set_ylabel('Mean exploratory score (symlog)')
    scores = [g['means']['est'] for g in a['A11']]
    axes[1, 1].set_ylim(min(scores) * 1.2, max(.02, max(scores) * 1.2))
    axes[1, 1].legend(fontsize=8)
    fig.suptitle('CDT controlled application campaign — model evidence, not deployment validation', fontsize=13)
    fig.savefig(directory / 'summary.png', dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    args = parser.parse_args()
    result, suites, manifest = summarize(args.input_dir)
    write_report(args.input_dir, result, suites, manifest)
    plot(args.input_dir, result)
    inputs = list(args.input_dir.glob('A*.json')) + [args.input_dir / 'manifest.json']
    analysis = {'created_at': datetime.now(timezone.utc).isoformat(),
                'analysis_source_sha256': digest(__file__), 'bootstrap_seed': 20261111,
                'input_sha256': {p.name: digest(p) for p in inputs}}
    (args.input_dir / 'analysis_manifest.json').write_text(json.dumps(analysis, indent=2) + '\n')
    paths = sorted(p for p in args.input_dir.iterdir() if p.is_file() and p.name != 'SHA256SUMS.txt')
    (args.input_dir / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in paths))
    print('Summary, ledger, plot, and integrity manifest written.')


if __name__ == '__main__':
    main()
