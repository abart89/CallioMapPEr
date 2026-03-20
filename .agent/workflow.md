# Workflow & User Entry Points

This document explains how the CallioMapper pipeline works end-to-end, from the user's perspective and from the inside. It is the companion to `project_structure.md` (which describes *where* things live) and the README (which describes *what* the tool does). This document describes *how* things connect.

---

## User entry points

There are two ways to run CallioMapper:

### 1. Python / Jupyter (primary)

```python
from calliomapper import Translator

t = Translator(
    model_dir="path/to/calliope_model/",       # required
    sidecar="path/to/epistemic_sidecar.yaml",  # optional — enables provenance graph (epistemic module)
    results="path/to/results.nc",              # optional — enables results graph (results_aggregated module)
    profile="standard",                        # optional — "minimal" | "standard" | "full"; default: "standard"
    schema="path/to/my_schema.yaml",           # optional — custom LinkML schema (overrides profile)
    run_id="my-run-001",                       # optional — defaults to auto UUID
)
graph = t.translate()   # returns rdflib.ConjunctiveGraph; raises on SHACL failure
t.save("output/my_model.nq")
```

The `Translator` accepts in-memory objects directly (dicts, xarray datasets), so it can be called from a notebook without touching the filesystem at all. File loading is only triggered when path strings are passed.

### 2. CLI (M4, wraps the Python interface)

```bash
calliomapper translate path/to/model/ --sidecar sidecar.yaml --results results.nc --profile standard --out my_model.nq
```

The CLI is a thin wrapper over `Translator`; it adds no logic.

---

## What each input enables

| Input | Module required in profile | Named graph produced | Required |
| :--- | :--- | :--- | :--- |
| `model_dir` (nodes.yaml + techs.yaml) | `structural` (always) | `<run_id>/structural` | Yes |
| `sidecar` (epistemic_sidecar.yaml) | `epistemic` | `<run_id>/provenance` | No |
| `results` (results.nc) | `results_aggregated` or `results_detailed` | `<run_id>/results` | No |

Running with only `model_dir` and `profile="minimal"` produces a structural-only `.nq`. Each additional input adds a named graph; the selected profile must include the corresponding module or a `ValueError` is raised at startup.

### Profile summary

| Profile | Modules | Suitable when |
| :--- | :--- | :--- |
| `minimal` | structural | Structural inspection only; no solve or sidecar needed |
| `standard` | structural + epistemic + results_aggregated | Default for most users |
| `full` | all four modules | Full detail with per-timestep results |

---

## Internal pipeline

```
Translator.__init__()
    │
    ├─ io.load_yaml(model_dir/nodes.yaml)
    ├─ io.load_yaml(model_dir/techs.yaml)
    ├─ io.load_yaml(sidecar)              # if provided
    └─ io.load_netcdf(results)            # if provided

Translator.translate()
    │
    ├─ StructuralMapper(nodes, techs, schema)
    │       → rdflib.Graph  tagged as  <run_id/structural>
    │
    ├─ EpistemicEngine(sidecar, structural_graph)   # if sidecar provided
    │       → rdflib.Graph  tagged as  <run_id/provenance>
    │
    ├─ ResultsMapper(dataset, structural_graph)     # if results provided
    │       → rdflib.Graph  tagged as  <run_id/results>
    │
    ├─ Translator merges all graphs into rdflib.ConjunctiveGraph
    │
    └─ validation.validate(graph, shapes_path)
            → raises ValidationError with SHACL report on failure
            → returns graph on success

Translator.save(path)
    └─ io.serialize_nq(graph, path)
```

### Why EpistemicEngine and ResultsMapper receive the structural graph

Both need to link their triples to entities minted by `StructuralMapper`. For example, a provenance triple `ontocal:wind_onshore prov:wasAttributedTo :Author` must reference the URI that `StructuralMapper` assigned to the wind technology. Passing the structural graph (read-only) makes those URIs available without re-parsing the model.

---

## Schema and namespace resolution

The pipeline is schema-agnostic. The schema determines:
- what Pydantic classes are used to validate parsed Calliope entities
- what RDF class and property URIs are emitted as triples
- what SHACL shapes are used for validation

### Default schema path (profile-based)

Each profile has a pre-baked master schema that imports its modules:

```
ontology/profiles/standard.yaml   (imports structural + epistemic + results_aggregated)
    ↓ make generate
calliomapper/generated/standard.py          (Pydantic classes)
ontology/profiles/standard_shapes.ttl      (SHACL shapes)
```

`Translator(profile="standard")` loads `standard.py` and `standard_shapes.ttl` automatically. Namespace objects for the default schema are defined in `calliomapper/ontology/namespaces.py` and imported by the mappers directly.

### Custom schema path (optional feature)

When the user passes `schema="path/to/my_schema.yaml"`:
- The `Translator` loads the schema via `linkml-runtime` at startup.
- Namespace bindings are read from the schema's `prefixes` block at runtime.
- No `namespaces.py` is consulted — the schema is the single source of truth for IRIs.
- The user must supply SHACL shapes alongside their schema (or disable validation).

`namespaces.py` is **not** a user-facing extension point. It exists only to avoid duplicating IRI strings across the default-schema mappers.

---

## Dummy schema (development mode)

While the real `calliope_oeo.yaml` mapping is being curated, the pipeline is developed and tested against a minimal dummy schema containing a single class: `CalliopeThing` (subclass of `bfo:entity`). This lives in:

```
ontology/dummy.ttl
ontology/dummy_schema.yaml
ontology/dummy_shapes.ttl     (generated)
calliomapper/generated/dummy_schema.py  (generated)
```

The dummy schema exercises the full pipeline — LinkML → Pydantic → StructuralMapper → SHACL validation → `.nq` output — with a trivial domain model. All pipeline code written against the dummy schema will work unchanged once the real schema is substituted, because the mappers interact with the schema only through generated Pydantic classes and namespace objects, not by name.

To run tests against the dummy schema:
```bash
pytest tests/test_structural.py   # uses dummy schema by default during M1 development
```

---

## Validation gate

Every `Translator.translate()` call ends with a SHACL validation pass before returning. This is not optional. The shapes file used is:

- default schema: `ontology/calliope_oeo_shapes.ttl` (or `dummy_shapes.ttl` during development)
- custom schema: path supplied alongside the custom schema

On failure, `validation.validate()` raises `calliomapper.utils.validation.ValidationError` with the full SHACL report included in the message. No `.nq` file is written.

---

## Output format

The output is an N-Quads (`.nq`) file. Each quad is:

```
<subject> <predicate> <object> <named-graph> .
```

Named graphs partition the data by concern and make it trivial to load only structural, provenance, or results triples into a triplestore:

```sparql
-- load only structural triples for a given run
LOAD <file:///path/to/my_model.nq> INTO GRAPH <my-run-001/structural>
```

The `.nq` format is also directly importable into Fuseki, GraphDB, Oxigraph, or any other SPARQL 1.1 endpoint.
