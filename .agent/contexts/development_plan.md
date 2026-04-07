> **Partially superseded.** For current implementation state, design decisions, and next planned work see `workflow_implementation.md`. The section most likely to mislead: Section 2 (TTL-as-source-of-truth — YAML-first is the actual decision; source data is `attrs.yaml` + CSV results directory, not `results.nc`). Sections still useful as reference: tech stack table (Section 1), feature priority tiers (Section 3), milestone checklists (Section 4).

---

## 1. Technical Stack & Environment

| Component                 | Choice                                           | Rationale                                                                                    |
| :------------------------ | :----------------------------------------------- | :------------------------------------------------------------------------------------------- |
| **Target Framework**      | Calliope v0.7.x                                  | Flat-parameter, node-based structure; pre-release targeted                                   |
| **Schema Language**       | [LinkML](https://linkml.io/) YAML                | Human-editable entry point; generates Pydantic, SHACL, OWL artifacts                         |
| **Pydantic Classes**      | Auto-generated from LinkML                       | Build artifact — never hand-edited; used for structured KG construction                      |
| **Graph Engine**          | `rdflib`                                         | Core RDF manipulation and serialization                                                      |
| **Validation**            | `pyshacl` + SHACL shapes (generated from LinkML) | Validates produced KG before returning to user; no OWL reasoner needed                       |
| **Primary Output Format** | N-Quads (`.nq`)                                  | Supports named graphs natively; ideal for provenance partitioning and SPARQL endpoint upload |
| **License**               | Apache 2.0 (pending supervisor sign-off)         | Permissive, compatible with OEO (CC-BY 4.0)                                                  |

### Namespace Policy

| Prefix     | IRI                                            | Usage                                          |
| :--------- | :--------------------------------------------- | :--------------------------------------------- |
| `bfo:`     | `http://purl.obolibrary.org/obo/BFO_`          | Upper-level ontology (temporal, mereological)  |
| `oeo:`     | `http://openenergy-platform.org/ontology/oeo/` | Core energy system concepts                    |
| `iao:`     | `http://purl.obolibrary.org/obo/IAO_`          | Information artifact relations                 |
| `prov:`    | `http://www.w3.org/ns/prov#`                   | Data lineage and provenance (PROV-O)           |
| `sosa:`    | `http://www.w3.org/ns/sosa/`                   | Observations and results                       |
| `ontocal:` | `https://w3id.org/ontocal/`                    | Tool-specific predicates and extensions        |

### Named Graph Partitioning Strategy (N-Quads)

Each model run produces a `.nq` file with distinct named graphs (only graphs for enabled modules are emitted):
- `<model-run-id>/structural` — nodes, technologies, parameters (always present)
- `<model-run-id>/provenance` — epistemic triples from the epistemic extension
- `<model-run-id>/results` — simulation observations (aggregate or granular, depending on profile)

### Profile System

The ontology is split into **module sub-schemas** (one per knowledge domain) and **profile master schemas** (fixed combinations of modules). Profiles are selected at runtime via `Translator(profile=...)`.

| Profile    | Modules included                                        | Use case                                           |
| :--------- | :------------------------------------------------------ | :------------------------------------------------- |
| `minimal`  | structural                                              | Quick structural inspection; no solve needed       |
| `standard` | structural + epistemic + results (aggregate)            | Default recommended profile                        |
| `full`     | structural + epistemic + results (aggregate + granular) | Full detail including per-timestep observations    |

`make generate` regenerates Pydantic classes, SHACL shapes, and OWL/Turtle for all profiles.

---

## 2. Default Ontology Pipeline

The default mapping is the canonical, team-curated representation of Calliope v0.7 in RDF. The pipeline is:

```
Calliope domain knowledge
        ↓
  LinkML YAML schema        ← source of truth; authored and committed to the repo
        ↓
  Pydantic classes          ← auto-generated build artifact (never hand-edited)
        ↓
  KG construction scripts   ← use Pydantic objects to drive rdflib triple generation
        ↓
  SHACL shapes              ← auto-generated from LinkML; used by pyshacl for validation
```

The LinkML YAML is the authoritative domain model. Changes start there, then trigger artifact
regeneration via `make generate`. A companion `.ttl` can be generated from LinkML for OWL
tooling but is not the source of truth.

---

## 3. Feature Priority

| Component                         | Priority     | Technical Scope                                                                                                                                                                  |
| :-------------------------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Structural Mapper**             | **MVT**      | Parses `attrs.yaml`. Maps flat v0.7 parameters to OEO/ontocal classes via the core LinkML schema. Includes two-phase scenario deduplication cache.                               |
| **Core Ontology Schema**          | **MVT**      | LinkML YAML covering structural entities (nodes, techs, carriers, parameters, variables, temporal regions, run process). Generates Pydantic classes and SHACL shapes.            |
| **Graph Validator**               | **MVT**      | Runs `pyshacl` against produced KG using generated SHACL shapes before any output is returned to the user.                                                                       |
| **Epistemic Engine**              | **MVT**      | Ingests a user-filled YAML template. Attaches PROV-O attribution and lineage triples (Pillars 1 & 2) to model entities. Supports model-level and entity-level annotations.       |
| **Results Mapper (aggregate)**    | **MVT**      | Reads CSV results directory, computes macro-summary observations linked to temporal horizons with `AggregationTypeEnum`. Included in `standard` and `full` profiles.             |
| **Results Mapper (granular)**     | **MVT**      | Per-timestep expansion: mints one observation instance per timestep per variable, each with its own `applies_to_time` pointer. Included in `full` profile.                       |
| **SPARQL Endpoint Upload**        | **OPTIONAL** | Uses `rdflib.SPARQLUpdateStore` to push the produced `.nq` to a configurable endpoint. Thin layer over file output.                                                              |
| **Logic Parser**                  | **OPTIONAL** | Parses Calliope v0.7 YAML-based math strings into semantic expressions.                                                                                                          |
| **Query Engine**                  | **OPTIONAL** | Pre-set SPARQL queries for common model interrogations.                                                                                                                          |
| **Custom Mapping**                | **OPTIONAL** | Allows users to supply alternative LinkML schemas to map to ontologies other than OEO.                                                                                           |
| **Model Downloader**              | **OPTIONAL** | Reconstruct a runnable Calliope model from a KG.                                                                                                                                 |

---

## 4. MVT Milestones

### M1 — Core Structural Mapping
**Goal:** Given a valid Calliope v0.7 model directory, produce a valid `.nq` file representing the model's full structural state.

**Deliverables:**
- `ontology/ontocal_core.yaml` — LinkML core schema covering nodes, techs, carriers, parameters, variables, temporal horizons, run process
- `ontology/ontocal_parameters.yaml` — parameter sub-schema (tech and node parameter hierarchy)
- `ontology/ontocal_variables.yaml` — variable sub-schema (output variable hierarchy)
- `ontology/profiles/minimal.yaml` — profile master schema importing the core schemas
- Auto-generated Pydantic classes and SHACL shapes for the `minimal` profile
- `StructuralMapper` class: reads `attrs.yaml`, resolves scenario overrides via two-phase deduplication cache, instantiates Pydantic objects, serializes to rdflib graph
- Dual temporal horizon modelling: `CalliopeDataHorizon` + `CalliopeExecutionHorizon` (mereological `temporal_part_of` relation)
- SHACL validation gate before output
- Output: `.nq` file with `<run-id>/structural` named graph

**Test:** Run against Calliope's built-in `national_scale` example. Validate the output `.nq` loads cleanly and passes SHACL.

---

### M2 — Epistemic Extension
**Goal:** Users can annotate the model with epistemic metadata; annotations appear as PROV-O triples in the output.

**Deliverables:**
- `ontology/extension_epistemic.yaml` — LinkML extension schema for PROV-O attribution and lineage (Pillars 1 & 2)
- `ontology/profiles/standard.yaml` — profile master schema importing core + epistemic + results (aggregate)
- Auto-generated Pydantic classes and SHACL shapes for the `standard` profile
- YAML input template (model-level + entity-level annotation support)
- `EpistemicEngine` class: parses template, emits PROV-O triples linked to structural entities from M1
- Output: `.nq` file now includes `<run-id>/provenance` named graph alongside structural graph

**Test:** Run against `national_scale` example with a hand-filled template. Verify provenance triples are correctly linked to structural entities.

---

### M3 — Integration & Validation
**Goal:** End-to-end pipeline — including both results modes — works as a single callable interface; validated against a second model.

**Deliverables:**
- `ontology/results.yaml` — LinkML schema for result observations (aggregate + granular, both modes)
- `ontology/profiles/full.yaml` — profile master schema importing core + epistemic + results (both modes)
- `ResultsMapper` class: reads CSV results directory, supports aggregate and granular output modes via profile flag
- `Translator` class orchestrating M1–M2 + results (decoupled from filesystem; accepts in-memory objects for Jupyter use)
- CLI entry point wrapping `Translator`
- End-to-end test against Calliope's `urban_scale` example
- End-to-end test against maintainer's own model (internal validation)

**Test:** Run full pipeline in `standard` and `full` profiles against `national_scale` and `urban_scale`. Validate all named graphs load and pass SHACL.

---

## 5. Developer Guidelines

- **Modularity:** `Translator` must accept in-memory model objects (not just file paths) to support Jupyter notebook workflows.
- **Generated artifacts:** Pydantic classes and SHACL shapes are build artifacts generated from the LinkML YAML. They live in a `generated/` directory and are never hand-edited. Regenerate them via `make generate`.
- **Validation gate:** `pyshacl` validation runs automatically before any output is written. Failures raise descriptive exceptions, not silent bad output.
- **Schema source of truth:** The LinkML YAML files are the authoritative domain model. A `.ttl` can be generated from them for OWL tooling but is not committed as the source.
- **Input source:** `attrs.yaml` (Calliope's compiled post-build attribute export) is the primary parsing input for M1. CSV results directory is the input for the results module. Raw user YAML files are not parsed.
- **Testing baseline:** Calliope's bundled `national_scale` and `urban_scale` examples are the canonical test fixtures. Tests must be reproducible without a live Calliope solve (fixture files should be committed or generated in CI).
