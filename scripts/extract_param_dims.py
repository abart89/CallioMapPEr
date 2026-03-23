"""
Extract parameter names and index dimensions from Calliope results_directory CSV headers.

Usage:
    python scripts/extract_param_dims.py <results_directory> [--out <output.yaml>]

Outputs a YAML mapping:
    param_name:
      kind: input | result
      dims: [list of index dimensions]
      n_values: int
"""

import csv
import sys
import yaml
from pathlib import Path


def extract(results_dir: Path) -> dict:
    catalog = {}

    for kind, prefix in [("input", "inputs_"), ("result", "results_")]:
        for csv_path in sorted(results_dir.glob(f"{prefix}*.csv")):
            param_name = csv_path.stem[len(prefix):]
            with csv_path.open(newline="") as f:
                reader = csv.reader(f)
                header = next(reader, [])
                # count data rows
                n_values = sum(1 for _ in reader)

            # The index dimensions are all columns except the last one (which is the value).
            # Calliope uses a flat CSV: index columns first, then the value column.
            # Special case: single-column files have no named index — they are scalars.
            if len(header) == 1:
                dims = []
                value_col = header[0]
            else:
                dims = header[:-1]
                value_col = header[-1]

            catalog[param_name] = {
                "kind": kind,
                "dims": dims,
                "n_values": n_values,
                "value_col": value_col,
            }

    return catalog


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_param_dims.py <results_directory> [--out output.yaml]")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    out_path = None
    if "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])

    if not results_dir.is_dir():
        print(f"Not a directory: {results_dir}")
        sys.exit(1)

    catalog = extract(results_dir)

    out = yaml.dump(catalog, default_flow_style=False, sort_keys=True)

    if out_path:
        out_path.write_text(out)
        print(f"Written to {out_path}  ({len(catalog)} parameters)")
    else:
        print(out)


if __name__ == "__main__":
    main()
