# Python tutorials

These notebooks are public, executable examples of using CallioMapper. They combine ordinary Python, explanations, compact answer tables and assertions against the supplied saved examples.

## Read them in this order

| Notebook | What you will do | Additional information required |
|---|---|---|
| [1. Saved results](01_saved_results.ipynb) | Translate the stable national and urban exports, query capacities and energy summaries, inspect omissions, and reuse an identifier manifest. | None beyond the included saved exports. Units remain unspecified when the files do not establish them. |
| [2. Supplied context](02_supplied_context.ipynb) | Compare source-only answers with supplied assumptions, reasons and unit interpretations. Distinguish an original report's author from the contributor and supplier of a new annotation. | The version 2 annotation document, whose invented context and source-based unit interpretations are labelled separately. |
| [3. Comparison and integration](03_comparison_and_integration.ipynb) | Inspect competency questions 6 and 7, query shared information using OEO and Dublin Core without OntoCal relationships, and check that incompatible information prevents comparison. | Explicit supplied component correspondence, study/scenario context, units, and a separate synthetic catalogue. |

Each notebook can also run independently. They contain their own imports and locate the repository by walking up from the current working directory. No notebook depends on another notebook's variables or generated files.

## Run the notebooks

From the repository root, install the package with its notebook dependencies:

```sh
python -m pip install ".[notebooks]"
python -m jupyter lab notebooks
```

Use the Python environment into which you installed those dependencies. Open a notebook, restart its kernel and run all cells in order. The notebooks use CallioMapper's Python interface, RDFLib and pandas; they do not import Calliope or run an optimiser. Notebook 3 calls the existing [comparison implementation](../examples/annotations/compare_exports.py), so there is one maintained implementation of that example.

Generated graphs, manifests, reports and example annotations go into:

```text
build/notebooks/01_saved_results/
build/notebooks/02_supplied_context/
build/notebooks/03_comparison_and_integration/
```

These generated files are not part of the tracked source. Re-running a notebook preserves identifiers through the manifests already in its output directory; the original CSV exports and annotation examples remain unchanged. You can inspect the full query answers in the named DataFrame variables even where a cell displays only selected columns or rows.

## Interpret the examples correctly

The numerical assertions refer to the fixed Calliope 0.7.0 examples supplied in this repository. They are not expected answers for arbitrary models. The [example preparation record](../examples/calliope-0.7.0-glpk/README.md) identifies their sources, software and solver. The original development-preview examples remain available separately.

The scientific context in tutorials 2 and 3 is deliberately invented and labelled as such. Tutorial 3 exports one unchanged saved execution twice; its two zero differences demonstrate query handling, not a real comparison between simulated futures. A fictional catalogue publisher must not be interpreted as the publisher of an empirical dataset.

Consult the [supported information and identifier rules](../docs/usage.md), [annotation guide](../examples/annotations/README.md) and [competency-question requirements](../docs/questions.md) when adapting the examples to your own work. A successful structural check does not establish the scientific truth of supplied statements.
