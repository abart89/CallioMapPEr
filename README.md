# CallioMapper

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ontology: OEO](https://img.shields.io/badge/ontology-OEO%20Aligned-green.svg)](https://openenergy-platform.org/ontology/oeo/)
[![Framework: LinkML](https://img.shields.io/badge/schema-LinkML-orange.svg)](https://linkml.io/)
[![Validation: pySHACL](https://img.shields.io/badge/validation-SHACL-purple.svg)](https://github.com/RDFLib/pySHACL)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Status: Active Development](https://img.shields.io/badge/status-active%20development-yellow.svg)](#current-status--roadmap)

> **Zero-configuration Semantic Knowledge Graphs for Calliope Energy Models. Fully aligned with the Open Energy Ontology (OEO).**

**CallioMapper** is an open-source Python library that transforms [Calliope v0.7](https://www.callio.pe/) energy system models into structured, linked-data knowledge graphs — without requiring the modeler to know anything about ontology engineering.

It accomplishes three things:

1. **Structural Autonomy** — Auto-maps every node, carrier, and technology in a solved model to their OEO-aligned semantic counterparts, with no human intervention.
2. **Epistemic Traceability** — Built-in PROV-O pipeline for attaching funding, authorship, and scenario derivation metadata to the exact model entities they describe.
3. **From SPARQL back to Pandas** — The output is a standard N-Quads file that plugs directly into SPARQL queries and back into Pandas DataFrames, so energy modelers never have to leave their existing workflow.

---

## Why?

Energy system models like Calliope are routinely used for sensitivity studies and scenario families — dozens or hundreds of runs that explore different technology mixes, cost assumptions, or policy constraints. The results end up scattered across NetCDF files and YAML directories, with no structured way to ask cross-run questions like *"in which runs did installed gas capacity exceed 5 GW?"* or *"which runs share the same solar cost assumption?"* The answer today is a custom script per study.

At the same time, the research community is converging on a consensus (Lombardi et al., 2025) that open models are necessary but not sufficient: what matters is *practical reproducibility* — transparency about modeling assumptions that a reviewer or collaborator can actually inspect, not just a PDF supplement.

CallioMapper is a practical response to both problems. By translating a solved Calliope model into a Knowledge Graph, it turns model archives into queryable databases and turns parameter provenance into machine-readable PROV-O triples that can accompany a journal submission or a Zenodo deposit. The base layer requires no effort from the modeler — no restructuring of input files, no ontology knowledge. The epistemic extension adds structured metadata with three fields in a YAML template.

The output is also designed to be compatible with the [Open Energy Knowledge Graph (OEKG)](https://openenergy-platform.org/), the community infrastructure for structured energy model metadata — reducing the friction of contributing model descriptions to the platform.

---

## What It Looks Like

### 1. Input: Solved Calliope Definition (`attrs.yaml`)
```yaml
nodes:
  region1:
    techs: [demand_power, ccgt]
    latitude: 40.0
    longitude: -2.0
techs:
  ccgt:
    base_tech: supply
    carrier_out: power
```

### 2. Output: OEO-Aligned Semantic Knowledge Graph (`.nq`)
```turtle
# Structural & entity classification in <run-id>/core
<https://w3id.org/ontocal/runs/001/region1> a ontocal:CalliopeNetworkNode ;
    ontocal:name "region1" ;
    ontocal:latitude 40.0 ;
    ontocal:longitude -2.0 ;
    ontocal:has_assigned_technology <https://w3id.org/ontocal/runs/001/ccgt> .

<https://w3id.org/ontocal/runs/001/ccgt> a ontocal:CalliopeSupplyTechnology ;
    ontocal:name "ccgt" ;
    ontocal:carrier_out ontocal:power .
```

### 3. Query: Direct SPARQL Querying
```sparql
PREFIX ontocal: <https://w3id.org/ontocal/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?node_name ?tech_name
WHERE {
    ?node a ontocal:CalliopeNetworkNode ;
          ontocal:name ?node_name ;
          ontocal:has_assigned_technology ?tech .
    ?tech a ontocal:CalliopeSupplyTechnology ;
          ontocal:name ?tech_name .
}
```

---

## Ontology Alignment

CallioMapper provides first-class alignment between Calliope v0.7 concepts and top-level/domain ontologies (Basic Formal Ontology, Information Artifact Ontology, Open Energy Ontology, and PROV-O):

| Calliope Concept | OntoCal Class (`ontocal:`) | OEO Parent Alignment (`oeo:`) | Upper Ontology Base |
| :--- | :--- | :--- | :--- |
| **Network Node** | `CalliopeNetworkNode` | `oeo:OEO_00000276` *(model component)* | `bfo:0000029` *(site)* |
| **Supply Tech** | `CalliopeSupplyTechnology` | `oeo:energy_transformation_process` | `bfo:0000015` *(process)* |
| **Demand Tech** | `CalliopeDemandTechnology` | `oeo:energy_transformation_process` | `bfo:0000015` *(process)* |
| **Storage Tech** | `CalliopeStorageTechnology` | `oeo:energy_transformation_process` | `bfo:0000015` *(process)* |
| **Transmission Tech** | `CalliopeTransmissionTechnology` | `oeo:energy_transformation_process` | `bfo:0000015` *(process)* |
| **Energy Carrier** | `CalliopeEnergyCarrier` | `oeo:energy_carrier` | `bfo:0000040` *(material entity)* |
| **Scenario** | `CalliopeScenario` | `oeo:OEO_00140093` *(scenario)* | `iao:0000030` *(ICE)* |
| **Optimisation Run** | `CalliopeOptimisationRun` | `oeo:OEO_00000305` *(optimisation)* | `bfo:0000015` *(process)* |
| **Provenance Metadata** | Epistemic Sidecar | `prov:wasAttributedTo`, `prov:wasDerivedFrom` | `PROV-O` |

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

- **`CoreMapper`** — Reads the solver-normalized `attrs.yaml` from the `results_directory/`. This is the stable, post-solve snapshot of the model definition, independent of how the user organized their input files. Maps nodes, technologies, and carriers to OEO-aligned classes via auto-generated Pydantic objects. Produces the `core` named graph.
- **`EpistemicEngine`** *(optional)* — Ingests a user-filled YAML sidecar and generates PROV-O provenance triples at model-level and per-entity level. Produces the `provenance` named graph.
- **`ResultsMapper`** — Reads the `results_*.csv` files from the `results_directory/` and emits aggregate RDF observations (carrier flows, installed capacities, costs) linked to structural entities.
- **`Translator`** — Orchestrates all three mappers, runs `pyshacl` validation before any output is returned, and serializes the final graph to `.nq`.

### Named Graph Partitioning (N-Quads output)

Each model run produces a `.nq` file with distinct named graphs:

| Named graph | Contents |
| :--- | :--- |
| `<run-id>/core` | Nodes, technologies, carriers, and solved output variables mapped to OEO classes |
| `<run-id>/provenance` | PROV-O triples from the epistemic extension (authorship, funder, derivations) |

### Schema Pipeline (YAML-First)

```
ontocal_core.yaml      (LinkML schema — source of truth, committed to repo)
      ↓  make generate
calliomapper/generated/ontocal_core.py    (Pydantic classes — auto-generated)
ontocal/ontocal_core_shapes.ttl          (SHACL shapes — auto-generated)
ontocal/ontocal_core.ttl                 (OWL/Turtle — for Protégé/ontologists)
```

Run `make generate` to regenerate all schema artifacts after editing the LinkML schema.

---

## Installation & Setup

### Prerequisites
- Python 3.12 or higher

### Install from Source
```bash
# Clone the repository
git clone https://github.com/abart89/CallioMapPEr.git
cd CallioMapPEr

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running Tests & Schema Generation
```bash
# Run unit and validation test suite
make test

# Regenerate schema artifacts from LinkML
make generate
```

---

## Quickstart

### 1. Translate a solved model (CLI)

Point `translate` at the `results_directory/` that Calliope writes after solving:

```bash
calliomapper translate examples/national_scale/results_directory/ --out my_model.nq
```

### 2. Add epistemic metadata (optional)

Generate a blank provenance template, fill it in, then pass it at translation time:

```bash
calliomapper init-extension
calliomapper translate examples/national_scale/results_directory/ --extension epistemic_extension.yaml --out my_model.nq
```

### 3. Query the graph (SPARQL to Pandas)

Run a preset SPARQL query against the output graph and get a CSV back:

```bash
calliomapper query my_model.nq --preset installed_capacity --out results.csv
```

### 4. Python API

```python
from calliomapper import Translator

t = Translator(
    results_dir="examples/national_scale/results_directory/",
    extension="epistemic_extension.yaml",               # optional
    run_id="https://w3id.org/ontocal/runs/my-run-001",  # optional
)

# Returns validated rdflib.Dataset (raises ValidationError if SHACL fails)
graph = t.translate()

# Save to standard N-Quads
t.save("output/my_model.nq")
```

---

## Current Status & Roadmap

CallioMapper is organized in structured development phases:

| Phase / Milestone | Scope | Status |
| :--- | :--- | :--- |
| **Phase 0: Core Structural Mapping** | Node/Tech dispatch, LinkML schema, SHACL validation gate, automated test suite | **Complete (22 tests passing)** |
| **Phase 1: Verification Infrastructure** | Semantic SPARQL question catalogue & verification suite against reference fixtures | **In Progress** |
| **Phase 2: Epistemic & Provenance** | PROV-O metadata sidecar engine for author, funder, and scenario derivations | **In Progress** |
| **Phase 3: Results & Analytics** | Solved variable loading (`results_*.csv`), SOSA observations, and SPARQL-to-Pandas export | **Planned** |

---

## Examples

See `examples/national_scale/` and `examples/urban_scale/` for pre-solved Calliope v0.7 fixtures used as development references. Interactive Jupyter demonstration notebooks will be available as the results and query layers are completed.

---

## References & Academic Background

- **Calliope Framework:** Pfenninger, S., & Pickering, B. (2018). *Calliope: a multi-scale energy systems modelling framework.* Journal of Open Source Software, 3(29), 825. [doi:10.21105/joss.00825](https://doi.org/10.21105/joss.00825)
- **Open Energy Ontology (OEO):** Booshehri, M., Emele, L., Flügge, M., et al. (2021). *Introducing the Open Energy Ontology: Enhanced Representation of Energy Systems.* Energy and AI, 5, 100074. [doi:10.1016/j.egyai.2021.100074](https://doi.org/10.1016/j.egyai.2021.100074)
- **Reproducibility in Energy Modeling:** Lombardi, F., Pickering, B., Colombo, E., & Pfenninger, S. (2025). *Practical reproducibility in energy system optimization models.*
- **FAIR Principles for Research Software:** Chue Hong, N. P., et al. (2022). *FAIR Principles for Research Software (FAIR4RS Principles).* [doi:10.15497/RDA/00068](https://doi.org/10.15497/RDA/00068)

---

## License

This project is licensed under the [MIT License](LICENSE).
