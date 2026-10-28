# Developing and reviewing CallioMapper

Use the [notebooks](notebooks/README.md) to review the supported workflow before
changing its implementation. Useful feedback identifies the notebook or query,
the saved input involved, the observed result and the intended interpretation.
For a real modelling study, distinguish information present in the exported
files from explanations supplied separately. Do not attach confidential model
data to a public issue; a small synthetic example can demonstrate the problem.

Report issues through the [repository issue tracker](https://github.com/abart89/CallioMapPEr/issues).
The tested support boundary and known omissions are in [the usage guide](docs/usage.md).

## Local checks

From a checkout or extracted source distribution, use a separate Python environment:

```sh
python -m pip install '.[dev,notebooks]'
python -m pytest tests/ -q
python scripts/check_notebooks.py
python -m build
```

The notebook command executes each tutorial from its first cell in a fresh
kernel and writes executed copies and a report to `build/notebook-checks/`.
It fails if a cell raises an exception or an expected result fails an assertion.
Use `python scripts/check_notebooks.py --write` to refresh the output saved in
the public notebook files after reviewing a change. Numerical example files
are read-only inputs; none of these commands runs Calliope or an optimisation.

GitHub's workflow runs the source tests on Python 3.10 and 3.13, with notebook
execution and distribution building on 3.13. A workflow definition is not
evidence that a hosted run has passed; see the current evaluation report.

## Ontology and example changes

OntoCal is maintained in its own repository. Update its reviewed snapshot using
`scripts/sync_ontology_resources.py`; do not edit bundled ontology files in place.
The separate OWL checks require Java and ROBOT and are described in
[the evaluation report](docs/evaluation.md).

The original example exports and stable reference exports have separate hash
manifests. Do not overwrite them to make a changed expectation pass. New saved
executions need their own sources, version records and independent expectations.
The optional preparation script is a separate workflow requiring Calliope and a
solver, explained in [the stable examples](examples/calliope-0.7.0-glpk/README.md).

The Git checkout additionally retains the files under `ontocal/` and explicitly
marked historical schema scripts from the earlier LinkML prototype. They are not the current runtime or
verification route.

## Building and identifying a research version

A build creates a wheel for installation and a source archive containing the
examples, notebooks, documentation and tests. Install an exact wheel to keep a
research workflow on a fixed package version. Retain the graph, its companion
manifest and report, the saved Calliope source files, and any supplied annotations.
The report identifies the bundled OntoCal version as well as the package version.

Before sharing a later release, update the package version and changelog, execute
the tests and notebooks, and verify clean wheel and source installations using
`scripts/check_installation.py`. Record the exact checks and remaining limitations
in the evaluation report. Release publication is a separate action.
