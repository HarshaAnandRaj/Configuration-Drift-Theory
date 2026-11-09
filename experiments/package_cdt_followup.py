"""Losslessly package large path records; leave the original local file intact."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out = ROOT / 'results/phenomena_followup_20261109'
    raw = out / 'long_tail_raw.json'
    archive = out / 'long_tail_raw.json.gz'
    archive.write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
    assert gzip.decompress(archive.read_bytes()) == raw.read_bytes()
    metadata = {'operation': 'lossless gzip; scientific data and original local file unchanged',
                'original_file': raw.name, 'original_sha256': digest(raw),
                'archive': archive.name, 'archive_sha256': digest(archive),
                'packager_sha256': digest(Path(__file__))}
    (out / 'packaging.json').write_text(json.dumps(metadata, indent=2) + '\n')
    paths = sorted(p for p in out.iterdir() if p.is_file() and
                   p.name not in ['long_tail_raw.json', 'SHA256SUMS.txt'])
    (out / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in paths))
    print(f'Archived {raw.stat().st_size} bytes to {archive.stat().st_size} bytes; lossless equality verified.')


if __name__ == '__main__':
    main()
