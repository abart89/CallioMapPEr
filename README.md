# CallioMapper

> **Zero-configuration Semantic Knowledge Graphs for Calliope Energy Models. Fully aligned with the Open Energy Ontology (OEO).**

**CallioMapper** is an open-source Python library that transforms [Calliope v0.7](https://www.callio.pe/) energy system models into structured, linked-data knowledge graphs — without requiring the modeler to know anything about ontology engineering.

It accomplishes three things:

1. **Structural Autonomy** — Auto-maps every node, carrier, and technology in a solved model to their OEO-aligned semantic counterparts, with no human intervention.
2. **Epistemic Traceability** — Built-in PROV-O pipeline for attaching funding, authorship, and scenario derivation metadata to the exact model entities they describe.
3. **From SPARQL back to Pandas** — The output is a standard N-Quads file that plugs directly into SPARQL queries and back into Pandas DataFrames, so energy modelers never have to leave their existing workflow.

*(For academic motivation, literature reviews, and background on why combining linear optimization with Knowledge Graphs matters, see the `paper/` directory.)*

---

## Why?

Energy system models like Calliope are routinely used for sensitivity studies and scenario families — dozens or hundreds of runs that explore different technology mixes, cost assumptions, or policy constraints. The results end up scattered across NetCDF files and YAML directories, with no structured way to ask cross-run questions like *"in which runs did installed gas capacity exceed 5 GW?"* or *"which runs share the same solar cost assumption?"* The answer today is a custom script per study.

At the same time, the research community is converging on a consensus (Lombardi et al., 2025) that open models are necessary but not sufficient: what matters is *practical reproducibility* — transparency about modeling assumptions that a reviewer or collaborator can actually inspect, not just a PDF supplement.

CallioMapper is a practical response to both problems. By translating a solved Calliope model into a Knowledge Graph, it turns model archives into queryable databases and turns parameter provenance into machine-readable PROV-O triples that can accompany a journal submission or a Zenodo deposit. The base layer requires no effort from the modeler — no restructuring of input files, no ontology knowledge. The epistemic extension adds structured metadata with three fields in a YAML template.

The output is also designed to be compatible with the [Open Energy Knowledge Graph (OEKG)](https://openenergy-platform.org/), the community infrastructure for structured energy model metadata — reducing the friction of contributing model descriptions to the platform.

---

## Architecture

The pipeline is composed of three mappers orchestrated by a single `Translator` class:

```
Calliope results_directory/
    ├─ attrs.yaml          ──► CoreMapper       ─┐
    ├─ results_*.csv       ──► ResultsMapper    ──┼──► Translator ──► validated .nq
    └─ epistemic_ext.yaml  ──► EpistemicEngine  ─┘
```

### Components

- **`CoreMapper`** — Reads the solver-normalized `attrs.yaml` from the `results_directory/`. This is the stable, post-solve snapshot of the model definition, independent of how the user organized their input files. Maps nodes, technologies, and carriers to OEO-aligned classes via auto-generated Pydantic objects. Produces the `structural` named graph.
- **`EpistemicEngine`** *(optional)* — Ingests a user-filled YAML sidecar and generates PROV-O provenance triples at model-level and per-entity level. Produces the `provenance` named graph.
- **`ResultsMapper`** — Reads the `results_*.csv` files from the `results_directory/` and emits aggregate RDF observations (carrier flows, installed capacities, costs) linked to structural entities. Produces the `results` named graph.
- **`Translator`** — Orchestrates all three mappers, runs `pyshacl` validation before any output is returned, and serializes the final graph to `.nq`.

### Named Graph Partitioning (N-Quads output)

Each model run produces a `.nq` file with distinct named graphs:

| Named graph | Contents |
| :--- | :--- |
| `<run-id>/structural` | Nodes, technologies, and carriers mapped to OEO classes |
| `<run-id>/provenance` | PROV-O triples from the epistemic extension (optional) |
| `<run-id>/results` | Aggregate carrier flows, capacities, and costs from the solve |

### Schema pipeline

```
ontocal_core.yaml      (LinkML schema — source of truth, committed to repo)
      ↓  make generate
calliomapper/generated/ontocal_core.py    (Pydantic classes — never hand-edited)
ontology/ontocal_core_shapes.ttl          (SHACL shapes — auto-generated)
ontology/ontocal_core.ttl                 (OWL/Turtle — for Protégé/ontologists)
```

Run `make generate` to regenerate all artifacts after editing the LinkML schema.

---

## Quickstart

### 1. Translate a solved model

Point `translate` at the `results_directory/` that Calliope writes after solving:

```bash
calliomapper translate path/to/results_directory/ --out my_model.nq
```

### 2. Add epistemic metadata (optional)

Generate a blank provenance template, fill it in, then pass it at translation time:

```bash
calliomapper init-extension
calliomapper translate path/to/results_directory/ --extension epistemic_extension.yaml --out my_model.nq
```

### 3. Query the graph (SPARQL to Pandas)

Run a preset SPARQL query against the output graph and get a CSV back:

```bash
calliomapper query my_model.nq --preset installed_capacity --out results.csv
```

### Python API

```python
from calliomapper import Translator

t = Translator(
    results_dir="path/to/results_directory/",
    extension="path/to/epistemic_extension.yaml",  # optional
    run_id="https://w3id.org/ontocal/runs/my-run-001",  # optional
)
graph = t.translate()
t.save("output/my_model.nq")
```

---

## Current Status

CallioMapper is under active development. The structural mapping layer (`CoreMapper`) is complete and validated against Calliope's bundled `national_scale` and `urban_scale` examples. The `ResultsMapper` and `EpistemicEngine` are in progress.

| Component | Status |
| :--- | :--- |
| CoreMapper (nodes, techs → OEO classes) | Complete |
| SHACL validation gate | Complete |
| EpistemicEngine (PROV-O provenance) | In progress |
| ResultsMapper (aggregate results) | In progress |
| SPARQL preset queries | Planned |

---

## Examples

See `examples/national_scale/` and `examples/urban_scale/` for pre-solved Calliope fixtures used as development references. Interactive notebooks will be added as the results and query layers are completed.
