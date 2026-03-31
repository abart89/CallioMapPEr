# Project Structure Reference

This document describes the layout of the CallioMapper repository for agent and developer navigation.

## Top-Level Layout

```
CallioMapPEr/
├── calliomapper/         # Python package (installable as `calliomapper`)
├── ontology/             # Ontology source files (TTL + LinkML YAML)
├── tests/                # Test suite
├── templates/            # User-facing templates (epistemic sidecar)
├── examples/             # Usage examples and notebooks
├── .agent/               # Project planning docs for agent/developer reference (this folder)
├── Makefile              # Automation: `make generate`, `make test`
├── pyproject.toml        # Package metadata and dependencies
└── README.md             # Public-facing project description
```

### File naming conventions

- LinkML schema files: `<name>.yaml` (no extra infix — e.g. `calliope_oeo.yaml`, not `calliope_oeo.linkml.yaml`)
- SHACL shape files: `<name>_shapes.ttl` (e.g. `calliope_oeo_shapes.ttl`)
- Turtle ontology files: `<name>.ttl`

---

## `calliomapper/` — The Python Package

The installable library. All user-facing code lives here.

```
calliomapper/
├── __init__.py           # Package init; exports Translator as public interface
├── translator.py         # Translator — main orchestration class (see below)
├── mapper/
│   ├── structural.py     # StructuralMapper: Calliope YAML → RDF structural graph (M1)
│   ├── epistemic.py      # EpistemicEngine: sidecar YAML → PROV-O provenance graph (M2)
│   └── results.py        # ResultsMapper: results.nc → aggregate observation triples (M3)
├── ontology/
│   └── namespaces.py     # rdflib Namespace objects for the DEFAULT schema (BFO, PROV, ONTOCAL)
│                         # Internal use only — not a user-facing extension point.
│                         # Custom namespaces come from a user-supplied schema via Translator(schema=...).
├── generated/            # AUTO-GENERATED — Pydantic classes from LinkML. Never hand-edit.
│                         # Regenerate with `make generate`.
└── utils/
    ├── io.py             # All filesystem I/O: load YAMLs, NetCDF, serialize .nq, push to endpoint
    └── validation.py     # pyshacl wrapper — validates graph before output
```

### Key architectural rule
`io.py` is the **only** module that touches the filesystem. All mapper classes receive already-loaded Python objects. This keeps the `Translator` usable in Jupyter notebooks without file paths.

### Data flow
```
[files on disk]
      ↓ io.py
[dicts / xarray datasets / sidecar dict]
      ↓ StructuralMapper → rdflib.Graph  (structural named graph)
      ↓ EpistemicEngine  → rdflib.Graph  (provenance named graph)
      ↓ ResultsMapper    → rdflib.Graph  (results named graph)
      ↓ Translator merges all into rdflib.Dataset
      ↓ validation.py (pyshacl) — raises on failure
      ↓ io.py → .nq file (or SPARQL endpoint)
```

---

## `ontology/` — Ontology Source Files

The ontology authoring entry point is **YAML-first**: edit the LinkML YAML schema, then run `make generate` to produce Pydantic classes, SHACL shapes, and OWL/Turtle.

**Current state (as of 2026-03-27):**

```
ontology/
├── ontocal.yaml               # THE real LinkML schema — full ontocal: class hierarchy.
│                              # Covers CalliopeModel, 5 tech subtypes, NetworkNode,
│                              # EnergyCarrier, Scenario, OptimisationRun, parameters.
├── individuals.ttl            # Named individuals (Calliope framework as oeo:SoftwareFramework)
└── calliope_oeo_shapes.ttl    # SHACL shapes — currently a placeholder (comment only).
                               # Must be generated from ontocal.yaml via `make generate`.
```

**Generated artifacts (not yet produced — pending `make generate`):**
- `calliomapper/generated/ontocal.py` — Pydantic classes for use by mappers
- `ontology/ontocal_shapes.ttl` — SHACL shapes for validation gate

**Planned long-term structure (not yet implemented):**
The module/profile architecture described in `development_plan.md` (separate `structural.yaml`, `epistemic.yaml`, `results_aggregated.yaml` + `profiles/` directory) is the intended eventual layout. For now `ontocal.yaml` is the single schema file that will grow to cover all modules.

### Ontology pipeline

**YAML-first (the active workflow):**
```
ontology/ontocal.yaml          ← author here (text editor or AI-assisted)
      ↓ make generate
calliomapper/generated/ontocal.py  — Pydantic classes (generated artifact, never hand-edit)
ontology/ontocal_shapes.ttl        — SHACL shapes (generated artifact)
ontology/ontocal.ttl               — OWL/Turtle for Protégé (generated artifact)
```

**TTL-first (alternative, for ontologists using Protégé):**
```
ontology/ontocal.ttl   ← edit in Protégé
      ↓ manual sync back to ontocal.yaml (no automated tool)
      ↓ make generate
(same generated artifacts)
```

---

## `tests/` — Test Suite

```
tests/
├── fixtures/              # Committed Calliope model fixtures (no live solve needed)
│   └── README.md          # Placeholder — no model data committed yet
├── test_structural.py     # Tests for StructuralMapper (M1) — 14 tests, passing
├── test_ontocal_schema.py # Tests for ontocal LinkML schema
├── test_epistemic.py      # Tests for EpistemicEngine (M2) — stub, not yet implemented
├── test_results.py        # Tests for ResultsMapper (M3) — stub, not yet implemented
└── test_translator.py     # End-to-end integration tests (M4) — stub, not yet implemented
```

**Note:** `fixtures/national_scale/` and `fixtures/urban_scale/` are planned but not committed. Tests currently run against in-memory fixtures.

Run tests with `make test` or `pytest tests/`.

---

## `templates/` — User-Facing Templates

```
templates/
└── epistemic_sidecar.yaml   # Template for users to fill in epistemic annotations
```

Users copy this file into their model directory and fill it in before running the Translator.

---

## `.agent/` — Planning & Reference Docs

Not part of the Python package. For agent and developer orientation only.

```
.agent/
├── manifesto.md              # Project mission, core pillars, impact goal
├── development_plan.md       # Technical stack, feature priority table, MVT milestones, dev guidelines
├── project_structure.md      # This file — repository layout reference
├── workflow.md               # Logical pipeline description (what and why, no implementation details)
├── workflow_implementation.md # Technical pipeline: current state, design decisions, next steps
├── ontology_rationale.md     # Ontology scope, OEO fitness, ontocal: hierarchy, namespace policy
├── ontologynotes.md          # Structured taxonomy reference: class hierarchy, attribute tables
├── ontology_dev_diary.md     # Chronological decision log for ontology development
├── attrs_structure.yaml      # Skeleton of Calliope v0.7 attrs.yaml — reference for input parsing
├── implementation_notes.md   # Implementation ideas from ontology work — read before coding mappers
└── contexts_index.md         # Index of all files in this folder with status notes
```

---

## Named Graph Conventions

Every `.nq` output partitions triples into named graphs by run ID:

| Named Graph | Contents |
| :--- | :--- |
| `<{run_id}/structural>` | Nodes, technologies, parameters |
| `<{run_id}/provenance>` | Epistemic sidecar triples (PROV-O) |
| `<{run_id}/results>` | Aggregate simulation observations |

---

## Namespace Prefixes

| Prefix | IRI | Usage |
| :--- | :--- | :--- |
| `bfo:` | `http://purl.obolibrary.org/obo/BFO_` | Basic Formal Ontology — top-level classes |
| `oeo:` | TBD (pending ontologist input) | Open Energy Ontology — core energy concepts |
| `prov:` | `http://www.w3.org/ns/prov#` | W3C PROV-O — data lineage and provenance |
| `ontocal:` | `https://w3id.org/ontocal/` | CallioMapper default — tool-specific classes and predicates |

Default namespace bindings are defined in `calliomapper/ontology/namespaces.py` for internal use.
When a user provides a custom schema via `Translator(schema=...)`, namespaces are resolved from that schema at runtime.