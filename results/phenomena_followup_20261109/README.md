# Long-tail and bookkeeping evidence

See [evidence_ledger.md](evidence_ledger.md) for results. The large per-path
records are stored losslessly as `long_tail_raw.json.gz`; the original local
JSON is retained and ignored by Git. `packaging.json` records both hashes.
The package step changes no measurements.

Inspect the path records with:

```bash
gzip -dc results/phenomena_followup_20261109/long_tail_raw.json.gz > /tmp/cdt_long_tail_raw.json
```

Reproduce into a fresh checkout without this result directory, or move the
existing result directory aside first (the runner refuses to overwrite it):

```bash
python experiments/cdt_phenomena_followup.py
python experiments/package_cdt_followup.py
```

The eight-suite sign-test family belongs to the separate application campaign.
This follow-up has descriptive and exact-formula checks, not new primary tests.
