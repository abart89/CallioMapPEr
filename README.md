# CallioMapper

An open-source Python library that transforms [Calliope](https://www.callio.pe/) v0.7 energy system models into standardized, linked-data knowledge graphs.

CallioMapper bridges the gap between Calliope-based energy modeling and the semantic web by providing an automated pipeline to map model inputs, outputs, and epistemic context to a pre-defined schema grounded in the [Open Energy Ontology (OEO)](https://openenergy-platform.org/ontology/).

## What it does

Given a Calliope v0.7 model, CallioMapper produces a validated **N-Quads (`.nq`) knowledge graph** containing:

- **Structural representation** — nodes, technologies, and parameters mapped to OEO classes
- **Epistemic provenance** — user-supplied rationale, data sources, and modeling assumptions attached as PROV-O triples
- **Aggregate results** — total energy capacities and carrier flows from a Calliope solve, represented as RDF observations

The output is designed to be loaded into a triplestore or integrated into broader urban/energy system knowledge graphs.

## Design Principles

- **Linked-data native**: outputs N-Quads with named graphs for structural data, provenance, and results
- **Validation gate**: every produced graph is validated against SHACL shapes before being returned
- **Notebook-friendly**: the `Translator` class accepts in-memory objects, not just file paths
- **Schema-driven**: the Calliope → OEO mapping is defined in a curated LinkML YAML schema, which generates Pydantic classes and SHACL shapes as build artifacts

## Project Status

Early development — pre-MVT. See [.agent/development_plan.md](.agent/development_plan.md) for the roadmap.

## Quick Start (placeholder — not yet implemented)

```python
from calliomapper import Translator

t = Translator(
    model_dir="path/to/calliope_model/",
    sidecar="path/to/epistemic_sidecar.yaml",  # optional
    results="path/to/results.nc",              # optional
)
t.translate()
t.save("output/my_model.nq")
```

## Installation

```bash
pip install -e ".[dev]"
```

## Development

```bash
make generate   # regenerate Pydantic classes and SHACL shapes from LinkML schema
make test       # run test suite
```

## License

Apache 2.0
