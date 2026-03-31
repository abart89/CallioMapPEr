# Implementation Notes

Ideas and decisions that surfaced during ontology development, saved here for the Python implementation phase. Organized by component. Not a formal spec — see `workflow_implementation.md` for that.

Add new entries under the relevant section. If a section doesn't exist yet, create it.

---

## StructuralMapper (M1)

### Parameter deduplication and scenario instantiation

**Problem:** Calliope models define a base parameter set and scenarios as override "deltas". A naive KG implementation faces two bad options:
- Mirror the file structure → queries require SPARQL fallback logic ("check override first, then base")
- Instantiate every parameter for every scenario → combinatorial bloat (e.g. 10,000 params × 50 scenarios = 500,000 instances)

**Decision: "Deduplicated Complete State" via two-phase Python caching**

The mapper resolves the delta entirely in Python before writing any triples, using `attrs.yaml` output as input.

**Phase 1 — Base model instantiation:**
1. Parse the unaltered base model from `attrs.yaml`
2. Mint a URI for each base parameter (e.g. `ontocal:param_solar_flow_cap_max_base`)
3. Link each parameter to its structural component via `iao:is_about` and assign value via `oeo:has_quantity_value`
4. Cache: `(component_id, parameter_name) → base_uri`

**Phase 2 — Scenario resolution:**
For each scenario, reconstruct the full parameter set by cache lookup:
- **Override exists** → mint a new URI (e.g. `ontocal:param_solar_flow_cap_max_scenario_x`), assign new value, link via `iao:is_about`, assert `bfo:part_of → ScenarioX`
- **No override** → retrieve the base URI from cache, assert `bfo:part_of → ScenarioX` (no new instance minted)

**Resulting triple pattern:**

```
# Base scenario
ScenarioBase  bfo:has_part  Param_Wind_Cost_Base    # value: 80
ScenarioBase  bfo:has_part  Param_Solar_Cost_Base   # value: 100

# Scenario A (overrides Solar, reuses Wind)
ScenarioA  bfo:has_part  Param_Wind_Cost_Base           # reused — no new instance
ScenarioA  bfo:has_part  Param_Solar_Cost_Override_A    # new instance, value: 50

# Both parameters link to their technology
Param_Wind_Cost_Base         iao:is_about  CalliopeTechnology/wind
Param_Solar_Cost_Override_A  iao:is_about  CalliopeTechnology/solar
```

**BFO/OEO rationale:** Parameters are ICEs (`oeo:exogenous_data`). A single ICE can be `bfo:part_of` multiple containers simultaneously (same formula in multiple textbooks). No new instance needed unless the semantic value changed.

**Benefits:**
- Queries are a direct `Scenario → has_part → Parameter` traversal — no fallback logic needed
- Enables cross-scenario comparison: "find all scenarios sharing the baseline Wind Cost assumption"
- Provenance: when `oeo:optimisation` connects to a scenario via `has_information_input`, the scenario already contains its fully resolved parameter set

**Implementation hook:** This logic belongs in `StructuralMapper` (or a dedicated `ScenarioResolver` helper it calls). The cache is a plain dict, scoped to a single `translate()` call — no persistence needed.

---

## EpistemicEngine (M2)

*(add notes here as they arise)*

---

## ResultsMapper (M3)

*(add notes here as they arise)*

---

## Translator / orchestration

*(add notes here as they arise)*

---

## Cross-cutting concerns

### Parameter metadata slots: unit, source_reference, applies_to_time

Every `CalliopeModelParameter` instance (and all subclasses) carries three optional metadata slots:

- **`ontocal:value`** — the scalar (float, boolean, or enum string), required on every concrete parameter class
- **`ontocal:unit`** — free-form string; some subclasses enforce a fixed value via `equals_string` (e.g. `FlowOutEff` → `"fraction"`, `Lifetime` → `"year"`). For carrier-agnostic parameters (capacity bounds, costs) the mapper should write the unit string it knows from context, or omit it if unknown.
- **`ontocal:sourceReference`** — provenance string; the mapper should write the Calliope source key (e.g. `"base_config"`, `"override_scenario_x"`) to enable traceability.
- **`ontocal:appliesToTime`** — object property pointing to an `oeo:TimeStep` instance. Omit for scalar/time-invariant parameters; populate for each element of a time-series.

**Time-series expansion pattern:** For a parameter that is a timeseries array of length T, mint T separate parameter instances — one per timestep — each with the same `is_about` target and `part_of` scenario, but a distinct `applies_to_time` pointer and `value`. This is verbose but makes every data point directly queryable without array unpacking in SPARQL.
