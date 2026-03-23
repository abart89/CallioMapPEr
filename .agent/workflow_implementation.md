# Workflow — Implementation Notes

Technical counterpart to `workflow.md`. Contains class names, file paths, design decisions, known issues, and next planned work. Updated as implementation progresses.

---

## Current implementation state (as of 2026-03-20)

**M1 pipeline is fully functional with the dummy schema.**

| File | Status |
| :--- | :--- |
| `ontology/dummy_schema.yaml` | Dummy LinkML schema — `CalliopeThing` subclass of `BFO:entity` |
| `ontology/dummy.ttl` | Hand-authored Turtle (see known issues) |
| `ontology/dummy_shapes.ttl` | Hand-authored SHACL shapes (see known issues) |
| `calliomapper/generated/dummy_schema.py` | Generated Pydantic classes from dummy schema |
| `calliomapper/ontology/namespaces.py` | `BFO`, `OEO`, `PROV`, `ONTOCAL` rdflib Namespace objects |
| `calliomapper/utils/io.py` | `load_yaml`, `load_netcdf`, `serialize_nq` |
| `calliomapper/utils/validation.py` | `validate()` + `ValidationError` wrapping pyshacl |
| `calliomapper/mapper/structural.py` | `StructuralMapper` — dicts → Pydantic → rdflib named Graph |
| `calliomapper/translator.py` | `Translator` — orchestrates M1 + SHACL gate + `.nq` output |
| `calliomapper/__init__.py` | Exports `Translator` |
| `tests/test_structural.py` | 14 tests: unit, SHACL, round-trip, named graph, custom graph_id |

**Real schema files are empty placeholders:**
- `ontology/calliope_oeo.yaml` — empty placeholder
- `ontology/calliope_oeo.ttl` — empty placeholder
- `ontology/calliope_oeo_shapes.ttl` — empty placeholder
- `calliomapper/generated/calliope_oeo.py` — does not exist yet

**M2, M3, M4 are stubs only** (`epistemic.py`, `results.py`, `translator.py` M2/M3 blocks).

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

## Ontology module sub-schemas to create

- `ontology/structural.yaml` — M1 concepts (replaces dummy)
- `ontology/epistemic.yaml` — M2 provenance concepts
- `ontology/results_aggregated.yaml` — M3a aggregate observation concepts
- `ontology/results_detailed.yaml` — M3b per-timestep (optional, `full` profile only)

**Profile master schemas:**
- `ontology/profiles/minimal.yaml` — imports structural only
- `ontology/profiles/standard.yaml` — imports structural + epistemic + results_aggregated
- `ontology/profiles/full.yaml` — imports all four modules

**Iteration loop for each module:**
1. Consult Calliope v0.7 docs + OEO to identify right class URI for a concept
2. Add class to relevant sub-schema YAML
3. `make generate` → regenerates Pydantic + SHACL + TTL for all profiles that include the module
4. Extend relevant mapper's `_add_entity()` to dispatch to the new Pydantic class
5. Add/update tests → `make test` → commit

`_add_entity()` currently always emits `rdf:type ontocal:CalliopeThing`. It needs to dispatch based on `base_tech` field to the appropriate subclass. This dispatch logic is the core M1 intellectual work.

---

## Next planned work

### Immediate: real ontology (M1)

Author `ontology/structural.yaml` starting with the class hierarchy from `ontology_rationale.md`:
- `ontocal:CalliopeModel`, `ontocal:CalliopeNode`, `ontocal:EnergyCarrier`
- `ontocal:SupplyTechnology`, `ontocal:DemandTechnology`, `ontocal:StorageTechnology`, `ontocal:TransmissionTechnology`, `ontocal:ConversionTechnology`

When ready:
- Update `Translator._DEFAULT_SHAPES` to point at profile shapes file
- Update `StructuralMapper` import from `dummy_schema` to generated profile module
- Update `namespaces.py` if new namespaces needed

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
