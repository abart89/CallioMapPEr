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
      ↓ Translator merges all into rdflib.ConjunctiveGraph
      ↓ validation.py (pyshacl) — raises on failure
      ↓ io.py → .nq file (or SPARQL endpoint)
```

---

## `ontology/` — Ontology Source Files

The ontology is split into **module sub-schemas** (one per knowledge domain) and **profile master schemas** (fixed combinations of modules). Profiles are the entry points for `make generate` and for `Translator(profile=...)`.

```
ontology/
│   # Module sub-schemas — authoring units, one per knowledge domain
├── structural.yaml            # M1: nodes, technologies, carriers, parameters
├── epistemic.yaml             # M2: scenarios, rationale, data provenance (PROV-O)
├── results_aggregated.yaml    # M3a: aggregate observations (totals per carrier/tech)
├── results_detailed.yaml      # M3b: per-timestep observations (OPTIONAL module)
│
│   # Profile master schemas — each imports a fixed set of sub-schemas.
│   # These are the `make generate` entry points and the `Translator(profile=...)` targets.
├── profiles/
│   ├── minimal.yaml           # imports: structural only
│   ├── standard.yaml          # imports: structural + epistemic + results_aggregated
│   └── full.yaml              # imports: structural + epistemic + results_aggregated + results_detailed
│
│   # Dummy schema — used during development while the real OEO mapping is being curated.
│   # Mirrors the same pipeline as the real schema; contains only CalliopeThing (BFO:entity subclass).
├── dummy_schema.yaml          # Dummy LinkML schema — authoring entry point for dev/testing
├── dummy.ttl                  # AUTO-GENERATED OWL/Turtle from dummy_schema.yaml
└── dummy_shapes.ttl           # SHACL shapes for the dummy schema
                               # NOTE: currently hand-authored because gen-shacl requires network
                               # access to resolve linkml:types.
```

### Profile → module mapping

| Profile | structural | epistemic | results_aggregated | results_detailed |
| :--- | :---: | :---: | :---: | :---: |
| `minimal` | ✓ | | | |
| `standard` | ✓ | ✓ | ✓ | |
| `full` | ✓ | ✓ | ✓ | ✓ |

### Ontology pipeline — two authoring workflows

**Preferred (YAML-first):** Edit a module sub-schema; regenerate all profiles that include it.
```
structural.yaml / epistemic.yaml / results_*.yaml   ← author these (text editor, AI-assisted)
      ↓ make generate
calliomapper/generated/<profile>.py    — Pydantic classes per profile (generated artifact)
ontology/profiles/<profile>_shapes.ttl — SHACL shapes per profile (generated artifact)
ontology/profiles/<profile>.ttl        — OWL/Turtle per profile, for Protégé (generated artifact)
```

**Alternative (TTL-first, for ontologists using Protégé):** Edit a profile TTL, then manually sync the relevant sub-schema YAML.
```
ontology/profiles/<profile>.ttl   ← edit in Protégé
      ↓ manual sync (no automated TTL→YAML tool exists)
relevant sub-schema .yaml         ← update by hand to reflect the TTL changes
      ↓ make generate
(same generated artifacts as above)
```

The manual sync is a deliberate constraint: LinkML YAML is more restricted than OWL, so not all OWL constructs translate, and the sync step forces a conscious decision about what the tool needs to represent.

The dummy schema follows the exact same pipeline. All pipeline code is schema-agnostic; only the generated artifacts differ.

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
├── project_structure.md  # This file — repository layout reference
├── workflow.md           # Data flow, user entry points, and extension points (how the pipeline works)
└── handoff.md            # Current implementation state + next steps (for incoming agent instances)
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