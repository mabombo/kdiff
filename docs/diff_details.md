# Detailed field-level differences (diff-details)

kdiff now includes a field-level detailed diff generator. It compares individual objects from `cluster1` and `cluster2` (the normalized per-object JSON files created by `bin/kdiff`) and produces a human-friendly report that highlights per-path scalar changes.

Files produced in the output directory (`OUTDIR`):

- `diff-details.md` — Markdown report with per-object tables of changed JSON paths and values.
- `diff-details.json` — Structured JSON with the same detailed data (good for automation).
- `diff-details.html` — Simple HTML page wrapping the Markdown for quick sharing.

How to run

After running `bin/kdiff` and getting a `summary.json` in the output dir, run:

```bash
python3 lib/diff_details.py OUTDIR
```

Notes

- The tool flattens only scalar JSON values (strings, numbers, booleans) and reports path-level differences (e.g., `data.k1`, `spec.replicas`, `metadata.annotations.foo`).
- Implemented in Python to avoid Bash portability issues and to make aggregation, reporting and testing simpler.
- Requires Python 3.8+ (stdlib only).

Example

If `OUTDIR` contains:

- `cluster1/configmap__ns__cm.json` with `data.k1 = "v1"`
- `cluster2/configmap__ns__cm.json` with `data.k1 = "v2"`

The generated `diff-details.md` will contain a section for `configmap__ns__cm.json` with a table showing `data.k1` changed from `"v1"` to `"v2"`.
