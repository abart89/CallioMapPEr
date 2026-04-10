# Agent Handover

Context summary and next steps for a fresh agent instance picking up this project.

---

## What this project is

**CallioMapper** — a Python library that translates solved Calliope v0.7 energy system models into
RDF Knowledge Graphs (N-Quads), aligned with the Open Energy Ontology (OEO). Primary output is a
`.nq` file with named graphs for structural topology, provenance, and results.

**Read before doing anything:**
1. `.agent/contexts_index.md` — index of all context and operational docs
2. `.agent/operational/workflow_implementation.md` — current implementation state, Python API, design decisions
3. `_implementation_plan.md` — phased showcase plan (Phase 0–3); phases 0 and 1 are complete

---

## Current state (as of 2026-04-10)

### What works
- `Translator(results_dir="examples/national_scale/results_directory/")` runs end-to-end
- Reads `attrs.yaml` from a Calliope `results_directory/` (not user input files — see design decision below)
- Produces valid N-Quads with 26 quads (national_scale) / 32 quads (urban_scale)
- Typed correctly: `CalliopeNetworkNode`, `CalliopeSupplyTechnology`, `CalliopeDemandTechnology`, `CalliopeStorageTechnology`, `CalliopeTransmissionTechnology`, `CalliopeConversionTechnology`
- SHACL validation passes
- 22 unit tests passing (`make test`)
- README revised and accurate

### What the KG currently contains (structural only)
For each entity: `rdf:type` + `ontocal:name` triples only. Nothing else yet. Specifically absent:
- lat/lon on nodes
- carrier relationships on technologies
- node–tech assignment triples
- results data (flows, capacities, costs)
- provenance triples

### Key design decision (do not revert)
The `Translator` reads from `results_directory/attrs.yaml`, NOT from user-authored YAML input files.
Rationale: Calliope users can structure their input files arbitrarily; `attrs.yaml` is the
solver-normalized, stable snapshot. This is documented in `.agent/operational/workflow_implementation.md`.

---

## Immediate next task — build the verification scripts

This is the agreed next step. The semantic validation infrastructure needs to be built so that
mapper development has a meaningful feedback loop.

### Files to create

**`scripts/generate_fixtures.py`**
Runs `Translator` on both example models and writes `.nq` files to `tests/fixtures/`:
- `tests/fixtures/national_scale.nq`
- `tests/fixtures/urban_scale.nq`
- (epistemic fixture TBD once EpistemicEngine exists)

Generated `.nq` files are gitignored (`*.nq` in `.gitignore`).

**`scripts/verify_kg.py`**
Loads the generated `.nq` files, runs SPARQL queries, asserts results match expected values,
prints `PASS / FAIL` per question, exits non-zero if any fail.

### Questions to implement first

Only the `Status: implemented` questions from `.agent/contexts/kg_questions.md` (Q001–Q009).
These are the ones where the mapper already emits the required triples — the assertions should
pass today. Pending questions (Q010 onwards) should be added as stubs that print `SKIP`.

### Expected answers reference
`tests/fixtures/kg_expected.yaml` — already written. Contains node names, tech names grouped by
base_tech, lat/lon per node. `verify_kg.py` should load this file and use dotted key lookups to
resolve `see kg_expected > <key>` references from `kg_questions.md`.

### Full design spec
Read `.agent/operational/validation_plan.md` before writing any code.

---

## Development loop (once scripts exist)

```
edit ontocal_core.yaml
  → make generate                        (regenerate Pydantic + SHACL)
  → update calliomapper/mapper/core.py   (if schema changed)
  → python scripts/generate_fixtures.py
  → python scripts/verify_kg.py          ← semantic correctness
  → make test                            ← mechanical correctness
  → commit
```

---

## Hook in place

`.claude/settings.json` has a `PostToolUse` agent hook on `Edit|Write` filtered to
`.agent/contexts/kg_questions.md`. When that file is edited, a subagent fires and runs the
`update-kg-questions` workflow to sync `verify_kg.py`. The workflow is at
`.agent/workflows/update-kg-questions.md`.

---

## After the verification scripts — planned work order

1. **Extend CoreMapper** to emit lat/lon, carrier, and node-tech triples (Q010–Q017 become green)
2. **Implement ResultsMapper** — reads `results_*.csv`, emits SOSA observations in `<run-id>/results` graph
3. **Implement EpistemicEngine** — reads epistemic YAML, emits PROV-O triples in `<run-id>/provenance` graph
4. **Legacy cleanup** — remove `dummy_schema.py`, `dummy_shapes.ttl`, stale test files
5. **Notebook A** — showcase notebook for national_scale structural mapping + topology visualization

---

## Key files at a glance

| File | What it is |
| :--- | :--- |
| `calliomapper/mapper/core.py` | CoreMapper — the main mapper to extend |
| `calliomapper/translator.py` | Orchestrator — `Translator(results_dir=...)` |
| `calliomapper/utils/io.py` | IO layer — `load_results_dir()` reads `attrs.yaml` |
| `ontology/ontocal_core.yaml` | LinkML schema — source of truth |
| `calliomapper/generated/ontocal_core.py` | Generated Pydantic classes — never hand-edit |
| `tests/test_core.py` | 22 passing unit tests |
| `tests/fixtures/kg_expected.yaml` | Expected answers for SPARQL verification |
| `.agent/contexts/kg_questions.md` | 21 verification questions (Q001–Q021) |
| `.agent/operational/validation_plan.md` | Full validation strategy and file format spec |
| `.agent/workflows/update-schema.md` | Runbook for ontology schema changes |
| `.agent/workflows/update-kg-questions.md` | Runbook for adding new verification questions |
| `examples/national_scale/results_directory/` | Primary test fixture (Calliope v0.7 solved) |
| `examples/urban_scale/results_directory/` | Secondary test fixture |

---

## Things to avoid

- Do not read input YAML files (`model_config/`, `locations.yaml`, etc.) — use `attrs.yaml` only
- Do not hand-edit `calliomapper/generated/ontocal_core.py` — always regenerate via `make generate`
- Do not commit `.nq` files — they are gitignored and generated by `generate_fixtures.py`
- Do not write notebooks until ResultsMapper is implemented — not enough content to be useful yet
- Do not add M1/M2/M3/M4 milestone naming — the project uses Phase 0–3 (see `_implementation_plan.md`)
