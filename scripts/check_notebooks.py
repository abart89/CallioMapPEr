"""Execute the public tutorials from clean kernels and record the result."""
import argparse
from importlib import metadata
import json
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Refresh the outputs saved in the public notebook files.')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/notebook-checks')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    notebooks = sorted((ROOT / 'notebooks').glob('*.ipynb'))
    if not notebooks:
        raise FileNotFoundError('No public notebooks found under notebooks/')
    report = {'python': sys.version, 'versions': {name: metadata.version(name) for name in
              ['calliomapper', 'nbclient', 'nbformat', 'ipykernel', 'pandas']}, 'notebooks': []}
    for path in notebooks:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        try:
            NotebookClient(notebook, timeout=180, kernel_name='python3',
                           resources={'metadata': {'path': str(ROOT)}}).execute()
        except Exception as error:
            report['notebooks'].append({'path': str(path.relative_to(ROOT)), 'status': 'failed', 'error': str(error)})
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            raise
        # Execution timings are local diagnostics, not part of the tutorial.
        for cell in notebook.cells:
            cell.metadata.pop('execution', None)
        destination = path if args.write else output / path.name
        nbformat.write(notebook, destination)
        report['notebooks'].append({'path': str(path.relative_to(ROOT)), 'status': 'passed',
                                   'executed_cells': sum(cell.cell_type == 'code' for cell in notebook.cells)})
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(f'{path.name}: passed', flush=True)
    print(f'{len(notebooks)} notebooks passed. Report: {output / "report.json"}')


if __name__ == '__main__':
    main()
