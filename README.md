# CallioMapper

An open-source Python library that transforms [Calliope](https://www.callio.pe/) v0.7 energy system models into standardized, linked-data knowledge graphs.

CallioMapper bridges the gap between Calliope-based energy modeling and the semantic web by automating the mapping of model inputs, simulation outputs, and epistemic context to a schema grounded in the [Open Energy Ontology (OEO)](https://openenergy-platform.org/ontology/).

## What it does

Given a Calliope v0.7 model, CallioMapper produces a validated **N-Quads (`.nq`) knowledge graph** partitioned into three named graphs:

| Named graph | Contents |
| :--- | :--- |
| `<run-id>/structural>` | Nodes, technologies, and parameters mapped to OEO classes |
| `<run-id>/provenance>` | PROV-O triples from a user-supplied epistemic sidecar |
| `<run-id>/results>` | Aggregate carrier flows and energy capacities from a Calliope solve |

The output is ready to be loaded into a triplestore or integrated into broader energy system knowledge graphs.

## Architecture

The pipeline is composed of three mappers orchestrated by a single `Translator` class:

```
Calliope model directory
    ├─ nodes.yaml / techs.yaml  ──► StructuralMapper  ─┐
    ├─ epistemic_sidecar.yaml   ──► EpistemicEngine   ──┼──► Translator ──► validated .nq
    └─ results.nc               ──► ResultsMapper     ─┘
```

### Components

- **`StructuralMapper`** — Parses Calliope v0.7 YAML inputs and maps the flat-parameter structure to OEO classes using auto-generated Pydantic objects. Produces the `structural` named graph.
- **`EpistemicEngine`** — Ingests a user-filled YAML sidecar and generates PROV-O provenance triples at both model-level and per-entity level. Produces the `provenance` named graph.
- **`ResultsMapper`** — Reads a `results.nc` (Xarray/NetCDF) file and emits aggregate RDF observations (total carrier production/consumption and installed capacity per technology). Produces the `results` named graph. Timeseries representation is out of scope for MVT.
- **`Translator`** — Orchestrates all three mappers, runs `pyshacl` validation before any output is returned, and serializes the final `ConjunctiveGraph` to `.nq`.

### Schema pipeline

```
calliope_oeo.ttl      (source of truth — curated Turtle ontology)
      ↓
calliope_oeo.yaml     (LinkML schema — tool entry point, committed to repo)
      ↓
calliomapper/generated/           (Pydantic classes — never hand-edited)
ontology/calliope_oeo_shapes.ttl  (SHACL shapes — auto-generated)
```

Run `make generate` to regenerate artifacts after editing the LinkML schema.

## Quick Start

```python
from calliomapper import Translator

t = Translator(
    model_dir="path/to/calliope_model/",
    sidecar="path/to/epistemic_sidecar.yaml",  # optional
    results="path/to/results.nc",              # optional
    schema="path/to/my_schema.yaml",           # optional — custom LinkML schema
)
graph = t.translate()
t.save("output/my_model.nq")
```

See [examples/basic_usage.py](examples/basic_usage.py) for a walkthrough. The [examples/national_scale/](examples/national_scale/) and [examples/urban_scale/](examples/urban_scale/) directories contain pre-run Calliope results used as development fixtures.

## Epistemic Sidecar

Copy [templates/epistemic_sidecar.yaml](templates/epistemic_sidecar.yaml) and fill in the annotations for your model run:

```yaml
model_level:
  author: ""          # Name or ORCID
  date: ""            # ISO 8601
  purpose: ""         # What this run represents
  assumptions: []
  data_sources: []

entity_level:
  technologies:
    <tech_name>:
      rationale: ""
      data_source: ""
  nodes:
    <node_name>:
      rationale: ""
      data_source: ""
```

## Design Principles

- **Linked-data native** — outputs N-Quads with named graphs for structural data, provenance, and results
- **Validation gate** — every produced graph is validated against SHACL shapes before being returned; failures raise descriptive exceptions
- **Notebook-friendly** — `Translator` accepts in-memory objects, not just file paths
- **Schema-driven** — the Calliope → OEO mapping lives in a curated LinkML YAML; Pydantic classes and SHACL shapes are generated build artifacts

## Installation

```bash
pip install -e ".[dev]"
```

## Development

```bash
make generate   # regenerate Pydantic classes and SHACL shapes from LinkML schema
make test       # run the test suite
```

## Project Status

Active development — working toward MVT. See [.agent/development_plan.md](.agent/development_plan.md) for the full milestone plan.

**MVT milestones:**
- M1 — Structural Skeleton (StructuralMapper + ontology + SHACL validation)
- M2 — Epistemic Provenance (EpistemicEngine + sidecar template)
- M3 — Aggregate Results (ResultsMapper + results.nc support)
- M4 — Integration & CLI (Translator orchestration + end-to-end tests)

## License

Apache 2.0
