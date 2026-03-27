# Ontology Development Diary

Chronological log of decisions, assumptions, open questions, and deferred items.
Add entries at the top (newest first). Each entry has a date and a short tag.

---

## 2026-03-25 — Ontology Modeling Decisions: Calliope v0.7 to OEO/BFO Mapping

## **1\. Taxonomy and Namespace Conventions**

* Developed a simplified taxonomy inside `ontologynotes.md`.  
  * **Namespace Rule**: Individuals are listed as "individual". Any class or entity without a stated namespace explicitly belongs to the new `ontocal` (Calliomapper) extension.  
  * **BFO Alignment**: All mappings strictly adhere to BFO upper-level ontology, drawing a hard line between software constructs (Informational Entities / Continuants) and the computational acts that generate them (Processes / Occurrents).

  ## **2\. Process Representation (The Occurrents)**

* **The Core Process**: The act of computing a Calliope model is represented as an instance of `oeo:optimisation` (`OEO_00000313`), which is a subclass of BFO `process`.  
* **Scenario Linkage**: Rather than creating a monolithic "solved model" entity, the `oeo:optimisation` process is contextualized within a broader `oeo:scenario projection` (`OEO_00010262`) via the `part of` relation. The projection itself is linked to the narrative `oeo:scenario` (`OEO_00000364`) via `is based on` (`OEO_00020226`).

  ## **3\. Data Inputs and Outputs (The Containers)**

* **Information Content Entities (ICE)**: Variables and parameters existing within the Calliope software are generically dependent continuants. They do not possess physical mass or energy.  
* **Inputs**: Calliope v0.7 parameters (e.g., limits, demands) are modeled as instances of `oeo:exogenous data` (`OEO_00030029`) or `oeo:program parameter` (`OEO_00000339`).  
  * They link to the process via: `oeo:optimisation` \-\> `oeo:has information input` (`OEO_00140093`) \-\> `oeo:exogenous data`.  
* **Outputs**: Calculated results (e.g., flow capacities, objective costs) are modeled as instances of `oeo:output data` (`OEO_00020013`), which is a subclass of endogenous data.  
  * They link from the process via: `oeo:optimisation` \-\> `oeo:has information output` (`OEO_00140094`) \-\> `oeo:output data`.

  ## **4\. Semantic Values (The Content)**

* **Separating Data from Meaning**: We explicitly decouple the data "container" (the variable) from its semantic "content" (the magnitude and unit).  
* **The "Reality Trap" Avoided**: We **DO NOT** use `oeo:quantity value of` (`OEO_00020056`), as this would falsely assert that the software model is grounded in physical reality (e.g., stating the computer RAM literally costs 1 billion EUR or produces physical megawatts).  
* **The Correct Linkage**: Both `oeo:exogenous data` and `oeo:output data` instances use the object property `oeo:has quantity value` (`OEO_00140002`) to link to an instance of `oeo:quantity value` (such as `oeo:cost` or `oeo:energy value`).  
* **Numerical Assignment**: The actual numbers and units are assigned strictly to the `oeo:quantity value` instance:  
  * Uses data property: `oeo:has number` (`OEO_00140178`)  
  * Uses object property: `oeo:has unit` (`OEO_00040010`)

  ## **5\. Scope: The "Model Footprint" vs. YAML Input Files**

* **Targeting the Solved Instance**: Calliomapper operates exclusively on the "model footprint" (the standardized, compiled xarray/netCDF data set generated after a Calliope v0.7 run).  
* **Rejecting File Representation**: We deliberately **do not** model the physical Information Bearing Entities (IBEs) (e.g., `techs.yaml`, `locations.yaml`).  
  * *Reason 1 (Syntactic Variance)*: Calliope allows users to spread input information arbitrarily across multiple files or override them in run-commands. Modeling the files captures arbitrary user habits, not the definitive mathematical state of the model.  
  * *Reason 2 (Knowledge Graph Purpose)*: The knowledge graph's goal is to answer *what* the model simulated and *how* the energy system was mathematically conceptualized, not to reverse-engineer directory trees or text files.  
* **Provenance Fallback**: If file origin must be tracked, we use lightweight data properties (e.g., a simple string URI like `has_source_repository`) attached to the `oeo:scenario`, avoiding structural clutter in the graph.

  ## **6\. Topology and Space (The "Is About" Relation)**

* **System vs. Component**: `CalliopeTechnology` and `CalliopeNetworkNode` are strictly categorized as `oeo:model component` (the parts), not `oeo:energy system model` (the whole). They are linked to the overarching `CalliopeModel` via BFO's `has part` (`BFO_0000051`).  
* **Real vs. Hypothetical Space**: Nodes are informational entities containing arbitrary coordinates as `exogenous data`.  
  * If the model corresponds to physical reality (e.g., Singapore), the `CalliopeNetworkNode` uses the IAO relation `is about` (`IAO_0000136`) to point to a physical `oeo:region of relevance`.  
  * If the model is hypothetical/generic, the `is about` relation is entirely omitted, preventing BFO category errors.

  ## **7\. Modeling Time and Resolution**

* **Simulation Time vs Modeled Time**:  
  * Real-world execution time is handled by the `oeo:optimisation` process (occurrent) via standard BFO temporal boundaries.  
  * The modeled time horizon is purely informational and linked to the `scenario` via `is about` (`IAO_0000136`).  
* **Linking Timesteps**: Timesteps are strictly linked to the *data containers* (`endo/exogenous data`) using `is about` (`IAO_0000136`). They are **never** linked to the `quantity value`, which remains a timeless magnitude.  
* **Temporal Resolution Handling**:  
  * **Aggregated Approach**: To summarize a run, link the data container to a single, overarching `oeo:time step` (`OEO_00030033`) representing the full span. OEO's `has aggregation type` (`OEO_00390023`) can be used to denote sum, average, etc. Avoid using `oeo:scenario horizon` unless the simulation is explicitly multi-year investment planning.  
  * **Detailed Approach (Timeseries)**: To represent specific operational horizons (e.g., a 168-hour dispatch), group data inside an `oeo:time series` (`OEO_00030034`) or `oeo:typical period` (`OEO_00020089`). Link this container via `has part` to individual data points, where each point `is about` its own specific hour/`time step`.  
* 



## 2026-03-20 — Initial taxonomy sketch

**Decision:** Author the taxonomy first as a plain nested YAML (`taxonomy.yaml`), not directly in LinkML. Reason: easier to reason about the class hierarchy without LinkML boilerplate getting in the way. Promote to `structural.yaml` (proper LinkML) once the hierarchy stabilises.

**Decision:** Namespace prefix is `ocal:` (short for ontocalliope), not `ontocal:`. Update `namespaces.py` when confirmed.

**Decision:** `EnergyCarrier` individuals are minted from unique carrier strings found in the model. No mapping to OEO concrete carrier classes (e.g. `oeo:ElectricEnergy`) at the base layer — Calliope carriers are untyped labels and any such mapping would be fabrication. OEO carrier alignment is deferred to a future extension.

**Decision:** `definition_matrix` (auto-generated by Calliope from carrier_in/carrier_out) is skipped in M1 mapping. It is redundant given that carrier_in and carrier_out are already mapped.

**Decision:** `color` field is omitted from the ontology. Visualization metadata only, no semantic content.

**Open question:** What is the correct OEO parent for `ocal:CalliopeTechnology`?
Candidates: `oeo:EnergyTransformationObject`, `oeo:ModelComponent`, `bfo:object`.
The problem: the parent must subsume all 5 archetypes including `DemandTechnology` (pure consumer), which may not fit under `oeo:EnergyTransformationObject`. Need to check `oeo-full.yaml` for `oeo:EnergyConsumer` and whether a common ancestor of producer + consumer exists.
→ **ACTION:** Search `docs/ontologies/oeo-full.yaml` for relevant class hierarchy before finalising.

**Open question:** Is `oeo:EnergySystem` the right parent for `ocal:CalliopeNode`?
Could also be `oeo:PowerGridRegion` or a BFO spatial region class. The distinction matters: `oeo:EnergySystem` implies a functioning system, whereas a Calliope node is more of a model abstraction (an aggregated region). Check OEO docs.

**Open question:** Should `ocal:CalliopeTechnology` be split into two abstract branches if no single OEO ancestor spans supply + demand?
- `ocal:EnergySourceTechnology` (supply, conversion, storage, transmission) → `oeo:EnergyTransformationObject`
- `ocal:EnergyDemandTechnology` (demand) → `oeo:EnergyConsumer` or similar
Holding until OEO parent resolution above.

**Deferred:** `include_storage: true` on a supply technology (e.g. CSP with thermal storage) creates hybrid behaviour. A composite class or annotation may be needed. Not blocking M1 — map as `SupplyTechnology` for now and add a flag.

**Deferred:** Parameter units. Calliope parameters are unitless in the YAML. Unit annotation (e.g. `oeo:kilowatt` for `flow_cap_max`) is a planned extension, not base layer.

---

## 2026-03-20 — Parameter catalog completed

**Decision:** `parameter_catalog.yaml` is the authoritative reference for all 35 input parameters and 27 result variables — their dimensions, data types, applicability, and informal OEO alignment notes. It is a companion document, not imported by the LinkML schema directly. Slot definitions in `structural.yaml` are a subset of the catalog (only the slots actually used as class attributes).

**Decision:** Parsing pipeline uses `attrs.yaml` as the primary source for structural entity extraction (nodes, techs, carriers, base_tech classification), and `results_*.csv` files for result values. Raw model input files (the user's YAML/CSV) are not parsed.

---

## 2026-03-20 — Scope and architecture settled

**Decision:** Path B adopted — honest structural mapping + modular extensions. No automated technology classification from names. The base layer is deterministic and zero-opinion.

**Decision:** `ocal:` namespace (prefix for `https://w3id.org/ontocal/`). Classes defined as OWL subclasses of OEO abstract classes via `rdfs:subClassOf`. OEO is not modified.

**Decision:** OEO's abstract tier is sufficient for the base layer. OEO's concrete tier (specific technology types, carrier types) belongs to extensions.

**Decision:** SOSA used for M3 observations (results). OEO's measurement datum classes are too thin for the launch use case.

**Decision:** QUDT not used. OEO provides its own unit system. Mixing both creates ambiguity.
