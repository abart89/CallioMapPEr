> **Partially superseded.** For current implementation state, design decisions, and next planned work see `workflow_implementation.md`. The sections most likely to mislead: Section 2 (TTL-as-source-of-truth — YAML-first is the actual decision) and M3 deliverables (CSV directory is primary, not `results.nc`). Sections still useful as reference: tech stack table (Section 1), feature priority tiers (Section 3), M1–M4 milestone checklists (Section 4).

---

## 1. Technical Stack & Environment

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| **Target Framework** | Calliope v0.7.x | Flat-parameter, node-based structure; pre-release targeted |
| **Schema Language** | [LinkML](https://linkml.io/) YAML | Human-editable entry point; generates Pydantic, SHACL, OWL artifacts |
| **Pydantic Classes** | Auto-generated from LinkML | Build artifact — never hand-edited; used for structured KG construction |
| **Graph Engine** | `rdflib` | Core RDF manipulation and serialization |
| **Validation** | `pyshacl` + SHACL shapes (generated from LinkML) | Validates produced KG before returning to user; no OWL reasoner needed |
| **Primary Output Format** | N-Quads (`.nq`) | Supports named graphs natively; ideal for provenance partitioning and SPARQL endpoint upload |
| **License** | Apache 2.0 (pending supervisor sign-off) | Permissive, compatible with OEO (CC-BY 4.0) |
| **Naming Convention** | `nodes` (v0.7) / `link_from`+`link_to` for transmission | v0.6 `locations` terminology is deprecated |

### Namespace Policy
| Prefix | IRI | Usage |
| :--- | :--- | :--- |
| `oeo:` | Open Energy Ontology | Core energy system concepts |
| `prov:` | W3C PROV-O | Data lineage and provenance |
| `ontocal:` | Internal (TBD) | Tool-specific predicates and extensions |

### Named Graph Partitioning Strategy (N-Quads)
Each model run produces a `.nq` file with distinct named graphs (only graphs for enabled modules are emitted):
- `<model-run-id>/structural` — nodes, technologies, parameters (always present)
- `<model-run-id>/provenance` — epistemic sidecar triples (requires `epistemic` module)
- `<model-run-id>/results` — simulation observations (requires `results_aggregated` or `results_detailed` module)

### Profile System
The ontology is split into **module sub-schemas** (one per knowledge domain) and **profile master schemas** (fixed combinations of modules). Profiles are selected at runtime via `Translator(profile=...)`.

| Profile | Modules included | Use case |
| :--- | :--- | :--- |
| `minimal` | structural | Quick structural inspection; no solve needed |
| `standard` | structural + epistemic + results_aggregated | Default recommended profile |
| `full` | all four modules | Full detail including per-timestep results |

`make generate` regenerates Pydantic classes, SHACL shapes, and OWL/Turtle for all profiles.

---

## 2. Default Ontology Pipeline

The default mapping is the canonical, team-curated representation of Calliope v0.7 in RDF. The pipeline is:

```
Calliope domain knowledge
        ↓
  .ttl / .owl file         ← curated by maintainers & ontologists (source of truth)
        ↓
  LinkML YAML schema        ← machine-readable schema; entry point for the tool
        ↓
  Pydantic classes          ← auto-generated build artifact (never hand-edited)
        ↓
  KG construction scripts   ← use Pydantic objects to drive rdflib triple generation
        ↓
  SHACL shapes              ← auto-generated from LinkML; used by pyshacl for validation
```

The `.ttl` file is the domain authority. The LinkML YAML is the tool's entry point and the artifact that gets committed to the repo alongside the `.ttl`.

---

## 3. Feature Priority

| Component | Priority | Technical Scope |
| :--- | :--- | :--- |
| **Structural Mapper** | **MVT** | Parses `nodes.yaml` + `techs.yaml`. Maps flat v0.7 parameters to OEO classes via the default LinkML schema. |
| **Default Ontology** | **MVT** | `.ttl` + LinkML YAML curated mapping of the Calliope framework to OEO. Generates Pydantic classes and SHACL shapes. |
| **Graph Validator** | **MVT** | Runs `pyshacl` against produced KG using generated SHACL shapes before any output is returned to the user. |
| **Epistemic Engine** | **MVT** | Ingests a user-filled YAML sidecar template. Attaches provenance and rationale triples (using PROV-O) to model entities. Supports both model-level and entity-level annotations. |
| **Results Mapper (aggregated)** | **MVT (scoped)** | Converts `results.nc` (Xarray/NetCDF) into **aggregate** RDF observations (totals per carrier/technology over simulated timespan). Included in `standard` and `full` profiles. |
| **Results Mapper (detailed)** | **OPTIONAL** | Extends Results Mapper to represent per-timestep observations. Included in `full` profile only. |
| **SPARQL Endpoint Upload** | **OPTIONAL** | Uses `rdflib.SPARQLUpdateStore` to push the produced `.nq` to a configurable endpoint. Thin layer over file output. |
| **Logic Parser** | **OPTIONAL** | Parses Calliope v0.7 YAML-based math strings into semantic expressions. |
| **Query Engine** | **OPTIONAL** | Pre-set SPARQL queries for common model interrogations. |
| **Custom Mapping** | **OPTIONAL** | Allows users to supply alternative LinkML schemas to map to ontologies other than OEO. |
| **Full Timeseries Results** | **OPTIONAL** | Already scoped as `results_detailed` module in the `full` profile. |
| **Model Downloader** | **OPTIONAL** | Reconstruct a runnable Calliope model from a KG. |

---

## 4. MVT Milestones

### M1 — Structural Skeleton
**Goal:** Given a valid Calliope v0.7 model directory, produce a valid `.nq` file representing the model's structure.

**Deliverables:**
- `ontology/structural.yaml` — LinkML sub-schema covering `nodes`, `techs`, and core parameters
- `ontology/profiles/minimal.yaml` — profile master schema importing `structural.yaml`
- Auto-generated Pydantic classes and SHACL shapes for the `minimal` profile
- `StructuralMapper` class: parses `nodes.yaml` + `techs.yaml`, instantiates Pydantic objects, serializes to rdflib graph
- SHACL validation gate before output
- Output: `.nq` file with structural named graph

**Test:** Run against Calliope's built-in `national_scale` example. Validate the output `.nq` loads cleanly and passes SHACL.

---

### M2 — Epistemic Provenance
**Goal:** Users can annotate the model with epistemic metadata; annotations appear as provenance triples in the output.

**Deliverables:**
- `ontology/epistemic.yaml` — LinkML sub-schema for provenance and rationale
- `ontology/profiles/standard.yaml` — profile master schema importing structural + epistemic + results_aggregated
- Auto-generated Pydantic classes and SHACL shapes for the `standard` profile
- YAML sidecar template (model-level + entity-level annotation support)
- `EpistemicEngine` class: parses sidecar, emits PROV-O triples linked to structural entities from M1
- Output: `.nq` file now includes `<.../provenance>` named graph alongside structural graph

**Test:** Run against `national_scale` example with a hand-filled sidecar. Verify provenance triples are correctly linked to structural entities.

---

### M3 — Aggregate Results
**Goal:** Simulation outputs are represented as aggregate observations in the KG.

**Deliverables:**
- `ontology/results_aggregated.yaml` — LinkML sub-schema for aggregate observations
- `ResultsMapper` class: reads `results.nc` via Xarray, computes totals per carrier/technology, emits observation triples
- Curated list of represented result variables (e.g. `energy_cap`, `carrier_prod`, `carrier_con` — totals only)
- Output: `.nq` file includes `<.../results>` named graph

**Test:** Run a full Calliope `national_scale` solve, pass `results.nc` through `ResultsMapper`. Validate output triples are correctly linked to M1 structural entities.

---

### M4 — Integration & Validation
**Goal:** End-to-end pipeline works as a single callable interface; validated against a second model.

**Deliverables:**
- `Translator` class orchestrating M1–M3 (decoupled from filesystem; accepts in-memory objects for Jupyter use)
- CLI entry point wrapping `Translator`
- End-to-end test against Calliope's `urban_scale` example
- End-to-end test against maintainer's own model (internal validation)

---

## 5. Developer Guidelines

- **Modularity:** `Translator` must accept in-memory model objects (not just file paths) to support Jupyter notebook workflows.
- **Generated artifacts:** Pydantic classes and SHACL shapes are build artifacts generated from the LinkML YAML. They live in a `generated/` directory and are never hand-edited. Regenerate them via a `make generate` or equivalent command.
- **Validation gate:** `pyshacl` validation runs automatically before any output is written. Failures raise descriptive exceptions, not silent bad output.
- **Ontology source of truth:** The `.ttl`/OWL file is the authoritative domain model. The LinkML YAML must stay in sync with it. Changes to the domain model start in `.ttl`, propagate to LinkML YAML, then trigger artifact regeneration.
- **Testing baseline:** Calliope's bundled `national_scale` and `urban_scale` examples are the canonical test fixtures. Tests must be reproducible without a Calliope solve (fixture `.nc` files should be committed or generated in CI).
