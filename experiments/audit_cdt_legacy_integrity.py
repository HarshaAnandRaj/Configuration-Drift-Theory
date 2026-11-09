"""Document existing CRLF/LF hash discrepancies without rewriting old evidence."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '14c9d020726d293f6f9fd19eb4f7d1c0b5f4b1d7'


def digest(b):
    return hashlib.sha256(b).hexdigest()


def main():
    records = []
    for line in (ROOT / 'results/SHA256SUMS.txt').read_text().splitlines():
        if not line.strip():
            continue
        expected, name = line.split('  ', 1)
        name = name.replace('\\', '/')
        b = (ROOT / name).read_bytes()
        baseline = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
        records.append({'file': name, 'recorded_sha256': expected.lower(),
                        'actual_sha256': digest(b), 'manifest_matches': digest(b) == expected.lower(),
                        'bytes_identical_to_baseline': b == baseline,
                        'crlf_normalization_matches': digest(b.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')) == expected.lower()})
    result = {'baseline_commit': BASE, 'audit_source_sha256': digest(Path(__file__).read_bytes()),
              'all_bytes_unchanged': all(r['bytes_identical_to_baseline'] for r in records),
              'note': 'Two existing summary hashes use CRLF while committed files use LF. No old file or checksum was edited.',
              'records': records}
    out = ROOT / 'results/application_20261109/baseline_integrity.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('Baseline bytes unchanged:', result['all_bytes_unchanged'])
    print('Existing line-ending discrepancies:', sum(not r['manifest_matches'] for r in records))


if __name__ == '__main__':
    main()
