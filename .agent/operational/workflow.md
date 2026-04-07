# Workflow — CallioMapper (Logical)

This document describes *what* CallioMapper does and *why*, without reference to implementation details (class names, file paths, code). For the technical counterpart see `workflow_implementation.md`.

---

## Prerequisite: the model must have been run

CallioMapper requires a Calliope model that has already been solved. The solve step produces a standardised output directory (`results_directory/`) and optionally a consolidated binary output (`results.nc`). These outputs are the entry point for CallioMapper.

This is a deliberate design choice: Calliope's input files can be organised in a highly flexible, creative way (scattered YAML, multiple CSV data tables, inline parameters, scenario overrides). The solve step normalises all of that into a predictable, uniform structure. Parsing the inputs directly would require handling arbitrary user organisation — parsing the solve outputs does not.

The two key artefacts after a solve:
- **`attrs.yaml`** — a single, fully-resolved model definition: nodes, technologies, parameters, carrier assignments. Everything Calliope expanded and merged before solving, in one canonical document.
- **`results_<variable>.csv` / `inputs_<parameter>.csv`** — one file per variable, with consistent index dimensions (nodes, techs, carriers, costs, timesteps).

---

## Inputs and what they enable

| Input | What it provides | Required |
| :--- | :--- | :--- |
| Path to the solve output (results directory or `.nc` file) | Everything below | Yes |
| Provenance sidecar YAML | Author/institution/data sourcing metadata | No |

Running with only the solve output produces a structural + results graph. Adding the provenance sidecar also produces a provenance graph.

---

## Processing stages

The pipeline has three logically distinct stages, each producing a separate named partition of the output graph:

### Stage 1 — Structural mapping (M1)

Reads the resolved model definition from `attrs.yaml`. Extracts:
- All nodes (spatial/system regions) and their geographic coordinates if present
- All technologies deployed at each node, classified by their Calliope archetype (supply, demand, storage, transmission, conversion)
- All energy carriers referenced in the model
- Scalar parameters (capacities, efficiencies, lifetimes, costs)
- Transmission links between nodes

Produces the topology graph: entities, their types, and the relationships between them. This is the backbone that all other stages reference.

### Stage 2 — Provenance mapping (M2, optional)

Reads the user-supplied provenance sidecar. Produces attribution triples: who authored the model, what data sources were used, what run this graph describes. Uses the entity URIs minted in Stage 1 as anchor points.

Requires a minimal sidecar with three fields (model name, authors, scenario description). Additional fields (data sources, derived-from references, funding) are optional and additive.

### Stage 3 — Results mapping (M3)

Reads the solved output variables from `results_<variable>.csv` files. Attaches result values (installed capacity, energy flows, system costs, capacity factors) to the technology and node entities from Stage 1.

At launch: aggregate results only (totals per technology per carrier). Per-timestep results are deferred to a future extension.

---

## Validation gate

After all stages complete, the full graph is validated against a set of structural rules (SHACL shapes) before any output is written. If validation fails, no output is produced and the full validation report is returned to the user. This is not optional — the gate ensures the output is always internally consistent.

---

## Output

The output is a single file in N-Quads format. It contains multiple named graphs, one per stage:

| Named graph | Contents |
| :--- | :--- |
| `<run-id>/structural` | Nodes, technologies, carriers, parameters (M1) |
| `<run-id>/provenance` | Attribution and data sourcing (M2, if sidecar provided) |
| `<run-id>/results` | Solved output values (M3) |

Named graphs allow a consuming triple store to load only the parts it needs (e.g., structural-only for topology inspection, or all three for a full run archive query).

---

## What is explicitly not done

- Automated technology classification from names (no guessing `ccgt_plant` → gas turbine)
- Parameter unit inference (Calliope parameters are unitless in the YAML; unit annotation is a planned extension)
- OEO concrete class type assertions (planned extension, not base layer)
- Per-timestep results (planned extension, not launch scope)
- Cross-run comparison or aggregation (the output is per-run; comparison is a SPARQL query concern)
- Model reconstruction from the graph (round-trip fidelity is not a goal)
