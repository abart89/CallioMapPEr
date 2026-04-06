# Slide Notes — CallioMapper Progress

---

## Slide 1 — CallioMapper: Design Choices

### What it does
- Converts solved Calliope v0.7 models into structured, linked-data (RDF) representations: topology, technology mix, parameters, and results
- Outputs queryable RDF in N-Quads format, loadable into a local triple store (e.g. Fuseki, Oxigraph)
- Enables cross-run SPARQL queries — e.g. "find all runs where installed gas capacity exceeded 5 GW" — over a model archive, instead of custom scripts per study
- Produces machine-readable provenance (PROV-O) to accompany journal submissions or Zenodo deposits
- Generates OEO-aligned RDF compatible with the Open Energy Knowledge Graph (OEKG) ingest format, removing manual form-filling

### How users interact with it
- **Key prerequisite:** the Calliope model must already have been solved. CallioMapper does not parse raw user input files — it reads from the normalised solve output directory (`results_directory/`)
- This is intentional: Calliope inputs can be structured arbitrarily (scattered YAMLs, CSVs, inline overrides); the solve step collapses all of that into a predictable, uniform structure (`attrs.yaml` + `results_*.csv`)
- Users point the tool at a solved instance — they do not need to restructure their model or learn any ontology engineering
- Minimal Python API: `Translator(results_dir="...", sidecar="...").translate()` — one call, one output file
- CLI: `calliomapper translate path/to/results_directory/ --out my_model.nq`
- Optional provenance sidecar (a short YAML with 3 required fields: model name, authors, scenario description) enriches the output with attribution triples

### What it is NOT
- Not a semantic enrichment tool: the base layer does not guess that `ccgt_plant` is a gas turbine — it only maps what Calliope actually writes down
- Not cross-framework: speaks Calliope v0.7 only (no PyPSA, OSeMOSYS, TIMES)
- Not an automated OEP/OEKG submission tool at launch — the output is compatible, but upload is a future extension

### Current issues / things still to implement
- **M1 (structural mapping):** Pipeline functional but still using dummy Pydantic schema. Real ontology (`ontocal.yaml`) is authored — need to run `make generate` and wire the generated classes into `StructuralMapper`
- **M2 (provenance):** Stub only — `EpistemicEngine` not yet implemented
- **M3 (results):** Stub only — `ResultsMapper` not yet implemented; will read `results_*.csv` and emit SOSA observation triples
- **M4 (CLI + integration):** Not yet implemented; CLI is planned as a thin wrapper over `Translator`
- **Known technical debt:** `gen-shacl` requires network access (fails offline); `pyshacl` raises `RuntimeError` on blank-node subjects in Dataset context (worked around, not fixed)
- **Profile/module architecture** (separate YAML files per module) is the intended long-term structure but not yet implemented — currently a single `ontocal.yaml`

---

## Slide 2 — Ontocal: Ontology Design Choices

### What the ontology covers
- The `ontocal:` namespace defines Calliope-specific classes as proper OWL subclasses of OEO abstract classes — OWL reasoners can infer OEO types automatically, no OEO knowledge required from the user
- **Structural layer (M1):** model instance, network nodes, the 5 Calliope technology archetypes (supply, demand, storage, transmission, conversion), energy carriers, transmission links, scalar parameters
- **Provenance layer (M2):** attribution and data sourcing via PROV-O (`wasAttributedTo`, `hadPrimarySource`, `wasDerivedFrom`, etc.)
- **Results layer (M3):** aggregate simulation outputs and input timeseries represented symmetrically as SOSA observations linked to structural entities

### What the ontology does NOT cover (and why)
- **No technology classification from names:** Calliope carrier and technology names are arbitrary user strings — mapping `"ccgt_plant"` to `oeo:GasTurbine` would be fabrication, not mapping
- **No physical units:** Calliope parameters are unitless in the YAML — unit annotation is a planned extension, not the base layer
- **No OEO concrete class assertions:** linking to OEO's specific technology types (WindTurbine, etc.) requires user input and belongs to extensions
- **No per-timestep results at launch:** deferred to a future `full` profile extension
- **No scenario overrides:** scenarios are a Calliope runtime concept, not a file-level structure in the solve output
- **No cross-framework alignment** and no automated OEP upload

### Core ontology (`ontocal:` namespace)
Class hierarchy rooted in OEO/BFO:
- `oeo:EnergySystemModel` → `ontocal:CalliopeModel` (one per run)
- `oeo:EnergySystem` → `ontocal:CalliopeNode`
- `ontocal:CalliopeTechnology` (abstract) → 5 subtypes: Supply, Demand, Storage, Transmission, Conversion
- `ontocal:EnergyCarrier` (label-only individuals — no OEO carrier mapping in base layer)
- `bfo:process` → `oeo:optimisation` (the solver run)
- `oeo:scenario projection` (the modelling exercise context)

Key predicates: `ontocal:baseTech`, `ontocal:carrierIn/Out`, `ontocal:locatedAt`, `ontocal:linkFrom/To`, `ontocal:runId`

Namespaces in use: `ontocal:`, `oeo:`, `prov:` (PROV-O), `sosa:` (results). No QUDT — OEO's native unit system is used to avoid ambiguity.

### What is deferred to extensions (not in core)
| Extension | What it adds |
|:---|:---|
| Physical system extension | Links ontocal entities to real-world OEO concrete class instances |
| OEO annotation extension | Asserts OEO concrete class types on technology individuals (e.g. WindTurbine) |
| Unit inference extension | Attaches OEO unit individuals to parameters from a lookup table |
| Scenario comparison extension | Cross-run SPARQL views and sensitivity study summaries |
| OEKG/OEP upload extension | Automated factsheet generation and platform submission |

Extensions write to their own named graphs; they never require changes to the base layer.
