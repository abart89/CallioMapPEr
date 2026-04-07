# Workflow — Implementation Notes

Technical counterpart to `workflow.md`. Contains class names, file paths, design decisions, known issues, and next planned work. Updated as implementation progresses.

---

## Current implementation state (as of 2026-03-27)

**M1 pipeline is functional with the dummy schema. Real ontology (`ontocal.yaml`) is now authored — Pydantic generation not yet run.**

| File | Status |
| :--- | :--- |
| `ontology/ontocal.yaml` | **Real** LinkML schema — full class hierarchy (CalliopeModel, 5 tech subtypes, NetworkNode, EnergyCarrier, Scenario, OptimisationRun, parameters). Committed 2026-03-27. |
| `ontology/individuals.ttl` | Named individuals (Calliope framework instance as `oeo:SoftwareFramework`). |
| `ontology/calliope_oeo_shapes.ttl` | Placeholder — contains only a comment. SHACL shapes must be generated from `ontocal.yaml` via `make generate`. |
| `calliomapper/generated/dummy_schema.py` | Generated Pydantic classes from old dummy schema — still the active import in `StructuralMapper`. Will be replaced once `make generate` is run against `ontocal.yaml`. |
| `calliomapper/ontology/namespaces.py` | `BFO`, `OEO`, `PROV`, `ONTOCAL` rdflib Namespace objects |
| `calliomapper/utils/io.py` | `load_yaml`, `load_netcdf`, `serialize_nq` |
| `calliomapper/utils/validation.py` | `validate()` + `ValidationError` wrapping pyshacl |
| `calliomapper/mapper/structural.py` | `StructuralMapper` — dicts → Pydantic → rdflib named Graph (currently still using dummy Pydantic classes) |
| `calliomapper/translator.py` | `Translator` — orchestrates M1 + SHACL gate + `.nq` output |
| `calliomapper/__init__.py` | Exports `Translator` |
| `tests/test_structural.py` | 14 tests: unit, SHACL, round-trip, named graph, custom graph_id |
| `tests/test_ontocal_schema.py` | Tests for ontocal schema validation |

**Pending to complete M1 with real schema:**
1. Run `make generate` against `ontocal.yaml` → produces `calliomapper/generated/ontocal.py` + `ontology/ontocal_shapes.ttl`
2. Update `StructuralMapper` to import from `ontocal.py` and dispatch on `base_tech` to the appropriate subclass
3. Update `Translator._DEFAULT_SHAPES` to point at `ontocal_shapes.ttl`

**M2, M3, M4 are stubs only** (`epistemic.py`, `results.py`, `translator.py` M2/M3 blocks).

**Note on ontology module sub-schema structure:** `ontocal.yaml` covers only what Calliope itself encodes in its core files (nodes, techs, parameters, carriers) — as designed by the Calliope authors. It does NOT grow to absorb extension modules. Extension modules (`epistemic.yaml`, `results_aggregated.yaml`) are and remain separate LinkML sub-schema files. The modular layout (`structural.yaml` → `ontocal.yaml`, `epistemic.yaml`, `results_aggregated.yaml`, `profiles/`) described in `development_plan.md` is still the intended structure. The profile system is valid and its implementation follows the original plan.

---

## Python API

```python
from calliomapper import Translator

t = Translator(
    results_dir="path/to/calliope_model/results_directory/",  # required
    sidecar="path/to/provenance_sidecar.yaml",                # optional — enables M2
    profile="standard",                                        # "minimal" | "standard" | "full"
    schema="path/to/my_schema.yaml",                          # optional — overrides profile
    run_id="my-run-001",                                       # optional — defaults to auto UUID
)
graph = t.translate()   # returns rdflib.Dataset; raises ValidationError on SHACL failure
t.save("output/my_model.nq")
```

Note: `workflow.md` and earlier `workflow.md` drafts referenced `model_dir` and `results.nc` as separate inputs. The decision (2026-03-20) is to use the `results_directory/` as the single entry point (see parsing strategy below). The `.nc` file is available as an alternative but the CSV directory is preferred for M3 due to its per-variable file structure.

## CLI

```bash
calliomapper translate path/to/results_directory/ --sidecar sidecar.yaml --profile standard --out my_model.nq
```

CLI is a thin wrapper over `Translator`; it adds no logic. Implemented in M4.

---

## Input parsing strategy (decided 2026-03-20)

**Primary entry point: `results_directory/`**, not the raw model input files.

Rationale: Calliope's input files can be structured in arbitrarily creative ways (scattered YAML, CSV data tables, inline parameters). The solve step normalises everything into a predictable, uniform output. Parsing the raw inputs would require handling arbitrary user organisation.

**Parsing pipeline:**

```
attrs.yaml  (inside results_directory/)
  └─► build entity graph: nodes, techs, carriers, node-tech assignments
  └─► extract scalar parameters: efficiencies, capacities, costs, lifetimes

results_<variable>.csv  (loop over all files in results_directory/)
  └─► attach result values to existing entities
  └─► filename → predicate mapping (e.g. results_flow_cap → ontocal:flow_cap)

inputs_source_use_max.csv, inputs_sink_use_equals.csv  (time-varying inputs only)
  └─► attach timeseries if needed (out of scope for launch; future full profile)
```

**Why attrs.yaml for structure, not inputs_*.csv:**
`attrs.yaml` is the single resolved model definition — it contains the full entity graph (nodes, techs, carriers, base_tech classification) already merged and expanded by Calliope. Reconstructing topology from dozens of `inputs_*.csv` files by inferring structure from column index combinations would be fragile and redundant.

**Why individual CSVs for results, not attrs.yaml:**
`attrs.yaml` does not contain solved results. Result CSVs have one file per variable, each mapping cleanly to one RDF predicate/property type. The per-file structure makes iteration straightforward.

---

## Internal pipeline (component names)

```
Translator.__init__()
    │
    ├─ io.load_yaml(results_dir/attrs.yaml)
    ├─ io.load_csv_results(results_dir/)        # glob results_*.csv
    ├─ io.load_yaml(sidecar)                    # if provided
    └─ (results.nc loading: alternative path, lower priority)

Translator.translate()
    │
    ├─ StructuralMapper(attrs, schema)
    │       → rdflib.Graph  tagged as  <run_id/structural>
    │
    ├─ EpistemicEngine(sidecar, structural_graph)   # if sidecar provided
    │       → rdflib.Graph  tagged as  <run_id/provenance>
    │
    ├─ ResultsMapper(results_csvs, structural_graph)
    │       → rdflib.Graph  tagged as  <run_id/results>
    │
    ├─ Translator merges all graphs into rdflib.Dataset
    │
    └─ validation.validate(dataset, shapes_path)
            → raises ValidationError with SHACL report on failure
            → returns dataset on success

Translator.save(path)
    └─ io.serialize_nq(dataset, path)
```

---

## Key design decisions

- `rdflib.Dataset` is used throughout (not `ConjunctiveGraph`, deprecated in rdflib 7)
- Named graph URI (4th quad element) is set via `Translator(run_id=...)`, defaults to auto UUID
- Entity URIs are always anchored to `run_id`, independent of `graph_id`
- `io.py` is the only filesystem-touching module; mappers receive pre-loaded Python objects
- `namespaces.py` is an internal default; user custom schemas plug in via `Translator(schema=...)`
- SHACL validation runs automatically before any `.nq` is written; raises `ValidationError` on failure
- YAML is the preferred authoring entry point for the ontology; TTL is a generated artifact

---

## Schema and namespace resolution

### Profile-based (default)

Each profile has a pre-baked master schema that imports its modules:

```
ontology/profiles/standard.yaml   (imports structural + epistemic + results_aggregated)
    ↓ make generate
calliomapper/generated/standard.py          (Pydantic classes)
ontology/profiles/standard_shapes.ttl      (SHACL shapes)
```

`Translator(profile="standard")` loads `standard.py` and `standard_shapes.ttl` automatically.

### Custom schema (optional)

When `schema="path/to/my_schema.yaml"` is passed:
- `Translator` loads schema via `linkml-runtime` at startup
- Namespace bindings read from schema's `prefixes` block at runtime
- No `namespaces.py` consulted — schema is the single source of truth for IRIs
- User must supply SHACL shapes alongside their schema (or disable validation)

---

## Ontology schema structure

**Current approach:** single `ontocal.yaml` covering all modules, rather than separate files per module. The profile/module architecture described in `development_plan.md` and `project_structure.md` is still the *intended* long-term structure but has not been implemented — `ontocal.yaml` is the working schema for now.

**Iteration loop for adding new concepts:**
1. Consult Calliope v0.7 docs + OEO to identify right class URI for a concept
2. Add class/slot to `ontology/ontocal.yaml`
3. `make generate` → regenerates Pydantic + SHACL + TTL artifacts
4. Extend relevant mapper's dispatch logic to the new Pydantic class
5. Add/update tests → `make test` → commit

`_add_entity()` currently always emits `rdf:type ontocal:CalliopeThing` (dummy schema). Once updated, it must dispatch based on `base_tech` field to the appropriate subclass. This dispatch logic is the core M1 intellectual work.

---

## Next planned work

### Immediate: wire real ontology into M1

`ontocal.yaml` is authored. Next steps:
1. Run `make generate` → produces `calliomapper/generated/ontocal.py` + `ontology/ontocal_shapes.ttl`
2. Update `StructuralMapper`:
   - Replace `dummy_schema.py` import with `ontocal.py`
   - Update `_add_entity()` dispatch to use `base_tech` field → appropriate subclass (`CalliopeSupplyTechnology`, `CalliopeDemandTechnology`, etc.)
3. Update `Translator._DEFAULT_SHAPES` to point at `ontocal_shapes.ttl`
4. Run `make test` — fix any failures
5. Commit M1 completion

### M2 — EpistemicEngine

Implement `calliomapper/mapper/epistemic.py`:
- Accepts sidecar dict + structural graph (read-only, for entity URIs)
- Emits PROV-O triples: `prov:wasAttributedTo`, `prov:generatedAtTime`, etc.
- Returns named Graph tagged `<run_id>/provenance`
- Add `tests/test_epistemic.py`
- Fill in `templates/provenance_sidecar.yaml`

### M3 — ResultsMapper

Implement `calliomapper/mapper/results.py`:
- Accepts dict of parsed result CSVs + structural graph
- Computes aggregate totals per carrier/technology
- Emits SOSA observation triples linked to structural entities
- Returns named Graph tagged `<run_id>/results`
- Add `tests/test_results.py` (fixture: `results_directory/` from national_scale)

### M4 — Integration & CLI

- Wire M1+M2+M3 fully in `Translator`
- Implement CLI entry point
- End-to-end tests against `national_scale` and `urban_scale` fixtures
- `calliomapper init <results_dir>` command that writes a pre-populated provenance sidecar template

---

## Known issues / technical debt

1. **`gen-shacl` requires network access** to resolve `linkml:types` from `linkml.io`. Fails offline. `dummy_shapes.ttl` is hand-authored as workaround. Investigate `--importmap` or local schema resolution.

2. **`dummy.ttl` is hand-authored**, not generated. Will be overwritten by `make generate-dummy` once gen-shacl network issue is resolved.

3. **`pyshacl` raises `RuntimeError`** (not a validation failure) when a blank-node subject appears in a `Dataset` context. Caught in `validation.py` and re-raised as `ValidationError`. pyshacl limitation, not a bug in our code.

---

## How to run

```bash
# activate venv
source dev_calliomapper/bin/activate

# run tests
make test

# regenerate dummy schema artifacts (gen-shacl step will fail — known issue)
make generate-dummy

# regenerate real schema artifacts (once structural.yaml is populated)
make generate
```
