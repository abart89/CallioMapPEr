# Ontology Rationale — CallioMapPEr

## Preamble: A Scope Reckoning

In March 2026, during active development of the ontology layer, a critical reassessment of the
project's scope was triggered by a mismatch between ambition and what Calliope's framework
actually encodes.

The original plan aimed at a deep alignment between Calliope model files and the Open Energy
Ontology (OEO). This was motivated by the hypothesis that Calliope models contain rich semantic
content waiting to be surfaced. The reckoning was this: **that hypothesis is largely false.**

Calliope is a deliberately generic optimization framework. It encodes:
- A topology (nodes connected by transmission technologies)
- A handful of base technology archetypes (5: supply, demand, storage, transmission, conversion)
- Numeric parameters (capacity, efficiency, cost, etc.) that are mostly unitless in the YAML
- Carrier labels that are just that — labels. `"electricity"`, `"gas"`, `"unicorns"` are
  interchangeable strings from Calliope's perspective. The framework has no knowledge of what
  a carrier physically is.

It does **not** encode:
- What a technology *is* in the real world (a gas turbine, a wind farm, a heat pump)
- What real-world energy commodity a carrier label refers to
- Why a parameter has a given value (data source, assumption, literature basis)
- What scenario or policy question the model is designed to answer
- Physical units attached to parameters
- Geographic or temporal context beyond user-assigned names and optional node coordinates

In short: **almost all of the semantically interesting and truly energy-related information in a
Calliope model lives in the user's head (or at best in free-text comments), not in the YAML
files.**

A mapper can only surface what is present. The "epistemic footprint" — the knowledge that makes
a model scientifically interpretable — was never designed into Calliope and cannot be
reverse-engineered from the files alone.

### What this means for the project

Two paths were considered:

**Path A — Comprehensive semantic lifting:** Author a full energy system taxonomy on top of
Calliope's sparse structure. Classify every technology name pattern, infer physical meaning from
naming conventions, build a domain ontology for energy modeling from scratch. Multi-year effort,
constant opinionated curation, output diverges from user intent whenever naming conventions
differ.

**Path B — Honest structural mapping + modular extensions:** Map only what Calliope actually
writes down to a minimal but sound RDF representation, using a proper `ontocal:` sub-taxonomy
that extends OEO. Complement this at launch with a provenance extension (user-supplied YAML)
that captures attribution and data sourcing. Further extensions are deferred and architecturally
planned but not shipped at launch.

**This project adopts Path B.** The rationale and scope below reflect this choice.

---

## Architecture: Base Layer vs. Extensions

The system has two tiers:

**Base layer (ships as core package):**
The deterministic, zero-opinion serialization of what Calliope encodes. Given the same model
files, two users running CallioMapper always produce identical output. No user input required
beyond pointing to a model directory. The vocabulary is a purpose-built `ontocal:` sub-taxonomy
that extends OEO abstract classes via proper OWL subclassing — not a loose annotation or a
post-hoc alignment.

**Extension layer (modular, some ship at launch):**
User-supplied or user-triggered modules that add meaning the base layer cannot derive
deterministically. The provenance extension ships at launch. Other extensions (physical system
linking, OEO concrete class annotation, scenario comparison) are architecturally planned but
deferred.

The distinction is deliberate: the base layer is a serialization tool; the extension layer is
where scientific interpretation lives. Conflating them would reproduce Path A's problems.

---

## Ontology Fitness Assessment

### Open Energy Ontology (OEO)

`oeo-full.yaml` is a 15,000+ line LinkML serialization of the OEO, built on BFO/OBO Foundry
standards. The assessment below reflects its fitness for the *base layer* specifically.

| Domain                  | Coverage  | Notes for base layer                                                                                              |
| :---------------------- | :-------- | :---------------------------------------------------------------------------------------------------------------- |
| Technology taxonomy     | Excellent | Abstract archetypes available; concrete classes (WindTurbine, etc.) unreachable without user annotation          |
| Energy carriers         | Good      | OEO carrier hierarchy is rich, but Calliope carriers are untyped labels — mapping would be fabrication            |
| Network topology        | Good      | `oeo:EnergySystemModel`, `oeo:PowerLine`, spatial regions all present and usable                                  |
| Parameters and units    | Good      | OEO native unit system sufficient; no QUDT needed                                                                 |
| Model/scenario metadata | Good      | `oeo:EnergySystemModel`, `has spatial resolution`, `has scenario year` — usable for base layer model entity       |
| Provenance (static)     | Partial   | `has author`, `has contributor` — sufficient for static attribution; activity chains need PROV-O                  |
| Observations/results    | Weak      | `measurement datum` present but thin; SOSA needed for M3                                                         |

**Key conclusion:** OEO's abstract tier is fully adequate for the base layer. OEO's concrete tier
(specific technology types, specific carrier types) is rich but unreachable from Calliope files
alone — it belongs to extensions, not the base.

### PROV-O

W3C PROV-O is the vocabulary for the provenance extension. No gaps for the launch use case:
- `wasAttributedTo`, `wasAssociatedWith` — attribution to agents (modelers, institutions)
- `wasGeneratedBy`, `used`, `wasInformedBy` — activity lineage
- `wasDerivedFrom`, `hadPrimarySource` — data sourcing
- `startedAtTime`, `endedAtTime`, `generatedAtTime` — temporal grounding

### Vocabulary gaps and resolutions

| Need                         | Status                   | Resolution                                                    |
| :--------------------------- | :----------------------- | :------------------------------------------------------------ |
| Observations/results (M3)    | Not in OEO or PROV-O     | Add SOSA namespace                                            |
| QUDT units                   | Not present              | Use OEO's native unit system; mixing would create ambiguity   |
| Spatial geometry (GeoSPARQL) | OEO regions are abstract | Out of scope; node coordinates stored as `ontocal:` literals  |
| Timeseries (input)           | Neither ontology         | Represented as SOSA observations in M3 (symmetric with output)|

---

## The ontocal: Sub-taxonomy

The `ontocal:` namespace (`https://w3id.org/ontocal/`) defines Calliope-specific classes and
predicates as a proper OWL extension of OEO — new named classes declared as `rdfs:subClassOf`
OEO abstract classes. This means:

- OWL reasoners can infer OEO types from ontocal types automatically
- The ontocal namespace is owned and versioned by this project
- OEO is not modified; alignment is achieved through subclassing, not annotation

### Class hierarchy (base layer)

```
oeo:EnergySystemModel
  └── ontocal:CalliopeModel          # the top-level model instance (one per run)

oeo:EnergySystem
  └── ontocal:CalliopeNode           # a spatial/system node

ontocal:CalliopeTechnology           # abstract base for all Calliope technologies
  ├── ontocal:SupplyTechnology       # base_tech: supply
  ├── ontocal:DemandTechnology       # base_tech: demand
  ├── ontocal:StorageTechnology      # base_tech: storage
  ├── ontocal:TransmissionTechnology # base_tech: transmission
  └── ontocal:ConversionTechnology   # base_tech: conversion

oeo:ModelComponent                   # or closest OEO parent (TBD on exact OEO class)
  └── ontocal:EnergyCarrier          # carrier instances (labels only, no OEO carrier mapping)
```

Note on `ontocal:CalliopeTechnology`: the OEO parent class for this abstract will be resolved
during formal OWL authoring. Candidate parents include `oeo:EnergyTransformationObject` or
`oeo:ModelComponent`. The key constraint is that the parent must be abstract enough to subsume
all 5 archetypes via intermediate classes if needed.

Note on `ontocal:EnergyCarrier`: Calliope carriers are untyped string labels. Mapping them to
OEO's carrier hierarchy (which encodes physical commodity types) would be fabrication — a carrier
named `"electricity"` could in principle carry anything in Calliope's math. Carriers are
therefore represented as `ontocal:EnergyCarrier` individuals with `rdfs:label` only. OEO carrier
type alignment is an extension concern (physical system extension, future).

### Key predicates (ontocal: namespace)

These are bridge predicates for Calliope-specific relationships not present in OEO:

| Predicate               | Domain                       | Range          | Notes                              |
| :---------------------- | :--------------------------- | :------------- | :--------------------------------- |
| `ontocal:baseTech`      | `ontocal:CalliopeTechnology` | xsd:string     | Preserves original Calliope value  |
| `ontocal:carrierIn`     | `ontocal:CalliopeTechnology` | `ontocal:EnergyCarrier` | For conversion/storage  |
| `ontocal:carrierOut`    | `ontocal:CalliopeTechnology` | `ontocal:EnergyCarrier` | For supply/conversion   |
| `ontocal:carrier`       | `ontocal:CalliopeTechnology` | `ontocal:EnergyCarrier` | For demand/storage      |
| `ontocal:locatedAt`     | `ontocal:CalliopeTechnology` | `ontocal:CalliopeNode`  | Tech-node assignment    |
| `ontocal:linkFrom`      | `ontocal:TransmissionTechnology` | `ontocal:CalliopeNode` |                      |
| `ontocal:linkTo`        | `ontocal:TransmissionTechnology` | `ontocal:CalliopeNode` |                      |
| `ontocal:runId`         | `ontocal:CalliopeModel`      | xsd:anyURI     | Base URI for the run               |
| `ontocal:calliopeVersion` | `ontocal:CalliopeModel`    | xsd:string     |                                    |

---

## Base Layer: What Gets Mapped (M1)

Everything Calliope encodes deterministically in `nodes.yaml`, `techs.yaml`, and
`model_config/`:

| Calliope source                   | RDF entity                          | Class                                |
| :-------------------------------- | :---------------------------------- | :----------------------------------- |
| Model root / run                  | Named individual                    | `ontocal:CalliopeModel`              |
| Node entry                        | Named individual                    | `ontocal:CalliopeNode`               |
| Technology entry (base_tech)      | Named individual                    | Appropriate `ontocal:*Technology`    |
| Carrier label                     | Named individual                    | `ontocal:EnergyCarrier`              |
| Transmission tech                 | Named individual                    | `ontocal:TransmissionTechnology`     |
| Numeric parameter (scalar)        | OEO quantity value literal          | `oeo:has_quantity_value`             |
| Timeseries parameter (input data) | `sosa:Observation` (see M3 below)   | Symmetric with output results        |

**What is NOT mapped in the base layer:**
- Parameter units (Calliope parameters are mostly unitless in YAML; unit inference is an extension)
- Node geographic coordinates (stored as `ontocal:latitude` / `ontocal:longitude` literals, not GeoSPARQL)
- Scenario overrides (scenarios are a Calliope runtime concept, not a file-level structure)
- Custom user-defined math

---

## Provenance Module (ships at launch)

The provenance module is a user-supplied YAML file (the term "sidecar" is retired) that generates
PROV-O triples in a separate named graph `<run-id>/provenance`.

**Minimal valid input (3 fields → valid PROV-O attribution graph):**

```yaml
model_name: "National Scale Example"
authors:
  - name: "Jane Smith"
    orcid: "0000-0000-0000-0000"
scenario_description: "Baseline scenario for 2030 net-zero transition"
```

This alone generates `prov:wasAttributedTo` and `prov:wasAssociatedWith` triples.

**Optional deeper fields:**
- `data_sources`: list of DOIs or URLs — generates `prov:hadPrimarySource` per referenced entity
- `derived_from`: reference to another run's URI — generates `prov:wasDerivedFrom`
- `institution`, `funding_source` — additional PROV-O agent metadata

**Scope discipline:** The provenance module at launch covers attribution and data sourcing only.
It does NOT map technologies to OEO concrete classes, does NOT infer physical units, and does
NOT produce OEP factsheet entries. Those are extension concerns.

**Template generation:** `calliomapper init <model_dir>` writes a pre-populated template
with the model's node and technology names as YAML anchors and commented-out optional fields.

---

## Results and Timeseries Module (M3)

Aggregate simulation outputs from `results.nc` and input timeseries (e.g., capacity factors,
demand profiles from `data_tables/`) are represented symmetrically as `sosa:Observation` triples.

**The symmetry is deliberate:** A capacity factor timeseries is an observation of a resource
potential; an output production timeseries is an observation of a system response. Both are
quantity values associated with a technology entity over a time context. Treating them
symmetrically simplifies the ontology and reflects how Calliope itself treats input and output
data (both live in xarray Datasets after model build).

**What is represented:**
- Aggregate results (totals per tech per carrier, installed capacity, system costs) — standard
- Input timeseries (capacity factors, demand profiles) — standard
- Per-timestep results — out of scope for launch; a future `full` profile extension

**Named graph:** `<run-id>/results`

**Vocabulary:** `sosa:Observation`, `sosa:observedProperty`, `sosa:hasSimpleResult`,
`sosa:madeBySensor` (linked to the technology entity from the structural graph),
`sosa:resultTime`. SOSA namespace must be added: `http://www.w3.org/ns/sosa/`.

---

## Extensions Architecture

Extensions are modular components that add meaning the base layer cannot derive deterministically.
They are architecturally distinct from the base and provenance module. Shipped separately,
activated by the user, each extension has its own named graph and its own input contract.

**Shipped at launch:**
- Provenance module (described above)

**Planned, not launched:**

| Extension                    | What it adds                                                      | Input required                     |
| :--------------------------- | :---------------------------------------------------------------- | :--------------------------------- |
| Physical system extension    | Links ontocal entities to real-world OEO concrete class instances | User-supplied YAML per tech/node   |
| OEO annotation extension     | Asserts OEO concrete class type on technology individuals         | User-supplied OEO class URIs       |
| Scenario comparison extension| Cross-run SPARQL views, sensitivity study summaries               | Multiple run-id graphs             |
| Unit inference extension     | Attaches OEO unit individuals to parameters using parameter name  | Lookup table (shipped as resource) |

Extensions are not second-class features. The architecture is designed so that an extension can
add triples to the same named graph as the base layer or write to its own named graph. The
Translator's profile system governs which modules run.

---

## Namespace Policy

| Prefix     | IRI                                            | Usage                                          |
| :--------- | :--------------------------------------------- | :--------------------------------------------- |
| `ontocal:` | `https://w3id.org/ontocal/`                    | Calliope-specific classes and predicates       |
| `oeo:`     | `http://openenergy-platform.org/ontology/oeo/` | Abstract class parents; unit system            |
| `prov:`    | `http://www.w3.org/ns/prov#`                   | Provenance module (PROV-O)                     |
| `sosa:`    | `http://www.w3.org/ns/sosa/`                   | Observations and results (M3)                  |

QUDT is not used. OEO provides its own unit system (`oeo:has_unit`, `oeo:has_quantity_value`).
Mixing both creates ambiguity for consuming tools.

---

## Target Consumption Model

The RDF output is designed to be ingested by, in descending priority:

1. **Local triple store (primary).** A researcher-run Apache Jena Fuseki or Oxigraph instance
   holding all runs from a sensitivity study. Immediate value: SPARQL queries across runs. No
   network dependency, no OEP account.

2. **Publication supplement (provenance module output).** The `<run-id>/provenance` named graph
   serialized as Turtle can accompany journal submissions or Zenodo deposits.

3. **OEKG SPARQL endpoint (future, extension-dependent).** Full OEKG alignment requires the OEO
   annotation extension (to assert concrete class types) and the scenario extension. Base layer
   alone gives partial OEKG alignment at the framework factsheet level only.

### Example SPARQL queries the base layer enables

```sparql
# Find all runs where a supply technology outputs to the "electricity" carrier
SELECT ?run ?tech WHERE {
  GRAPH ?run {
    ?tech rdf:type ontocal:SupplyTechnology ;
          ontocal:carrierOut ?carrier .
    ?carrier rdfs:label "electricity" .
  }
}
```

```sparql
# Compare installed capacity of storage technologies across runs
SELECT ?run ?tech ?capacity WHERE {
  GRAPH ?run {
    ?tech rdf:type ontocal:StorageTechnology ;
          oeo:has_quantity_value ?capacity .
  }
} ORDER BY ?run
```

Note: these queries use ontocal classes and carrier labels, not OEO concrete classes. The OEO
concrete class queries (e.g., `rdf:type oeo:WindTurbine`) become available only after the OEO
annotation extension is activated.

---

## OEKG Alignment

The Open Energy Knowledge Graph (OEKG) uses OEO and PROV-O. CallioMapper's base output aligns
partially:

| OEKG layer          | CallioMapper source           | Named graph              | Alignment        |
| :------------------ | :---------------------------- | :----------------------- | :--------------- |
| Framework factsheet | Base layer (CalliopeModel)    | `<run-id>/structural`    | Partial at launch|
| Model factsheet     | Provenance module             | `<run-id>/provenance`    | Full at launch   |
| Scenario bundle     | Results module (M3)           | `<run-id>/results`       | Partial at launch|

"Partial" means: the triples exist and are valid OEO/PROV-O, but full OEKG ingest requires
additional alignment work (concrete class assertions, OEKG-specific named graph conventions)
that is deferred to extensions and M4+.

---

## What Is Explicitly Out of Scope

**Forever out of scope:**
- Automated technology classification from names (no guessing `ccgt_plant` → `oeo:GasTurbine`)
- Custom user-defined math (Calliope YAML math DSL)
- Model reconstruction from KG (round-trip fidelity is not a goal)
- Cross-framework support (PyPSA, OSeMOSYS, TIMES)

**Out of scope for launch, planned as extensions:**
- OEO concrete class type assertions for technologies
- Physical system entity linking (real-world OEO instances)
- Per-timestep results
- Automated OEP/OEKG upload
- Unit inference from parameter names

---

## Value Proposition (Scoped)

The base layer + provenance module + results module is a **focused, achievable tool** with a
real but niche use case.

**What it genuinely enables:**
1. Cross-run SPARQL queries over a model archive (base + results)
2. Machine-readable attribution and data sourcing for journal submission (provenance module)
3. Structured model topology inspection without running Calliope (base)
4. A foundation for extensions that add semantic depth incrementally

**What it does not enable without extensions:**
- OEO concrete class queries (requires OEO annotation extension)
- OEP factsheet contributions (requires OEKG alignment extension)
- Physical system validation (requires physical system extension)

**Verdict:** M1 + provenance module + M3 with a well-designed template and a worked example on
`national_scale` is defensible, completable, and publishable (e.g. JOSS). The work that remains
is engineering, not ontology research.
