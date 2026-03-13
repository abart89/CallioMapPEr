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
│   └── namespaces.py     # rdflib Namespace objects (OEO, PROV, SEMCAL) — import from here
├── generated/            # AUTO-GENERATED — Pydantic classes from LinkML. Never hand-edit.
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
      ↓ Translator merges all into rdflib.ConjunctiveGraph
      ↓ validation.py (pyshacl) — raises on failure
      ↓ io.py → .nq file (or SPARQL endpoint)
```

---

## `ontology/` — Ontology Source Files

```
ontology/
├── calliope_oeo.ttl           # SOURCE OF TRUTH — curated Turtle ontology (Calliope → OEO mapping)
├── calliope_oeo.linkml.yaml   # LinkML schema derived from .ttl — tool entry point
└── shapes.shacl.ttl           # AUTO-GENERATED SHACL shapes from LinkML (run `make generate`)
```

### Ontology pipeline
The `.ttl` file is authoritative. When the domain model changes:
1. Edit `calliope_oeo.ttl`
2. Sync changes to `calliope_oeo.linkml.yaml`
3. Run `make generate` → regenerates `calliomapper/generated/` and `shapes.shacl.ttl`

---

## `tests/` — Test Suite

```
tests/
├── fixtures/              # Committed Calliope model fixtures (no live solve needed)
│   ├── national_scale/    # Calliope built-in example — primary test fixture (M1–M3)
│   └── urban_scale/       # Calliope built-in example — integration test fixture (M4)
├── test_structural.py     # Tests for StructuralMapper (M1)
├── test_epistemic.py      # Tests for EpistemicEngine (M2)
├── test_results.py        # Tests for ResultsMapper (M3)
└── test_translator.py     # End-to-end integration tests (M4)
```

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
├── manifesto.md          # Project mission, core pillars, impact goal
├── development_plan.md   # Technical stack, feature priority table, MVT milestones, dev guidelines
└── project_structure.md  # This file
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

| Prefix | Usage |
| :--- | :--- |
| `oeo:` | Open Energy Ontology — core energy concepts |
| `prov:` | W3C PROV-O — data lineage and provenance |
| `semcal:` | Internal tool-specific predicates |

All namespace bindings are defined in `calliomapper/ontology/namespaces.py`.
