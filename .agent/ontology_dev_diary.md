# Ontology Development Diary

Chronological log of decisions, assumptions, open questions, and deferred items.
Add entries at the top (newest first). Each entry has a date and a short tag.

---


## 2026-04-06 — Deferred: Calliope Meta-Parameters and the MVP Process Class

### The Problem: The "Everything Everywhere" Config Problem

In Calliope v0.7, the configuration files contain a high density of "meta-parameters" (found in `config.init`, `config.build`, and `config.solve`). While these are essential for the software to function, modeling them all at once risks "ontological bloat." Many of these parameters (like `bigM` penalties or `resample` frequencies) sit in a grey area between the **Energy System Model** (the physical/economic definition) and the **Optimisation Process** (the mathematical solving event).

### The Strategy: Establishing the Occurrent Pattern First

To maintain a clean separation between **Continuants** (the technologies and nodes that exist) and **Occurrents** (the act of solving the model), we have decided to defer the bulk of these meta-parameters.

Instead of a deep dive into every solver kwarg, we are implementing a **Minimum Viable Process (MVP)** for the `CalliopeRunProcess`. This allows us to prove the BFO alignment of the "Run" without getting bogged down in the minutiae of solver-specific heuristics.

### What We Are Implementing Now

We are focusing strictly on the **Temporal Boundaries** and **Exit States** of the process. This provides immediate value for provenance and performance tracking:

1. **Solver Attribution:** Linking the process to `oeo:OEO_00000392` (Solver) to identify the "instrument" of the process.
2. **Temporal Footprint:** Capturing the 8 core POSIX timestamps (`preprocess_start` through `solve_complete`) as data attributes. This defines the process in time.
3. **Termination Logic:** Using a controlled vocabulary (`TerminationConditionEnum`) to capture the outcome (e.g., `optimal`, `infeasible`).

### What We Are Skipping (The "Deferred" List)

The following categories are intentionally excluded from the current LinkML schema. These should be treated as **future refinements** for the next iteration of the agent:

* **Mathematical Heuristics:** `bigM` values, `ensure_feasibility` slacks, and `objective_cost_weights`.
* **Data Transformation Directives:** `resample` strings, `time_cluster` mappings, and `broadcast_input_data` flags.
* **SPORES Orchestration:** The entire logic for Spatially-explicit Pareto Optimal solutions (number of iterations, slack tolerances).
* **Custom Math Extensibility:** `extra_math` and `math_paths` logic.

### Note for Future Agents

When revisiting these deferred parameters, they should likely be modeled as subclasses of `oeo:OEO_00000339` (Program parameter) and linked to the `CalliopeRunProcess` via the `has_information_input` relation. This maintains the BFO principle that these are Information Content Entities that *direct* a process but are not the process itself.

**Status:** Minimal Process Class established. Physical-to-Process boundary confirmed. Proceeding to validate against instance data.

---


## 2026-03-31 — Decision: Macro Temporal Horizons and Aggregated Parameters

**Decision:** Adopted a dual-timespan architecture using BFO one-dimensional temporal regions (`bfo:0000038`) to prevent graph bloat caused by granular timestep arrays. We introduced `CalliopeDataHorizon` (the absolute temporal bounds of the underlying model dataset) and `CalliopeExecutionHorizon` (the specific temporal slice simulated by a scenario). 

**Decision:** Established a strict mereological relationship between the two temporal horizons. The `CalliopeExecutionHorizon` must be linked as a `temporal_part_of` (`bfo:0000139`) the `CalliopeDataHorizon`.

**Decision:** Implemented a controlled vocabulary (`AggregationTypeEnum`) within the `ontocal` namespace to act as a mathematical modifier (sum, average, max, min) for Information Content Entities representing statistical summaries.

**Decision:** Updated base parameter containers (e.g., `TechParameter`) to optionally accept `applies_to_time` and `aggregation_type` slots. 

**Rationale:** Simulating an entire year at hourly resolution creates massive "data multiplier" bloat in standard triple stores. While granular `oeo:time step` links are still permitted for high-fidelity needs, providing a mechanism for aggregated macros is highly pragmatic. However, simply linking a scalar value to a broad timespan creates semantic ambiguity (is it a peak max or a cumulative sum?). By forcing the explicit declaration of the mathematical operation via the enum, and distinctly separating the base model's time boundaries from the scenario's time boundaries, we preserve exact ontological precision and BFO compliance without sacrificing query performance.


## 2026-03-31 — Decision: Modeling Time-Dependent Parameters and Unit Metadata (The Pragmatic Extensions)

Having adopted the pragmatic "Data Attribute" approach (Option B) for Calliope parameters, we needed a way to handle two major complexities inherent to Calliope:

1. **Time-Series Data:** Parameters can be static scalars or dynamic arrays defined on a by-timestep basis.  
2. **Unit Tracking:** By dropping the strict oeo:quantity value wrapper, we lost the dedicated BFO structure for storing physical units and provenance.

To solve this, we extended our parameter container architecture using BFO relational hooks and LinkML inheritance, maintaining graph elegance without sacrificing queryability.

### **1\. The Temporal Hook (iao:is about)**

In BFO, an Information Content Entity (our parameter container) can be "about" multiple things. We already use iao:is about to link the parameter to the physical model component (e.g., the power plant). To handle time, we simply add a second, optional is about link pointing to a temporal region.

* **The Time Entity:** We instantiate specific model intervals (e.g., "Hour 1") using **oeo:time step** (OEO\_00030033), a subclass of BFO's temporal region.  
* **Static Parameters:** If a parameter lacks a temporal link, it is assumed to be static and applies to the overarching oeo:scenario.  
* **Dynamic Parameters:** For time-series data, we generate a distinct parameter instance for each timestep and link it directly to the corresponding oeo:time step.

### **2\. The Metadata Hooks (Units and Provenance)**

To restore unit tracking and add data provenance, we utilize LinkML's class inheritance. Rather than redundantly defining unit data on all 50+ Calliope parameters, we attach metadata slots directly to the overarching parent classes (TechParameter and NodeParameter).

* **Flexible Units (Carrier Agnostic):** For parameters like FlowCapMax (which could be MW, kg/s, or MWh depending on the user's carrier), the unit is left as a flexible string inherited from the parent class.  
* **Strict Units (Semantic Safety):** For parameters with mathematically absolute units (e.g., FlowOutEff must be a fraction; Lifetime must be years), we use LinkML's slot\_usage to hardcode the unit at the class level. This provides built-in validation while keeping the schema lean.

### **LinkML Implementation Summary**

We introduced three global slots to the schema:

1. applies\_to\_time (Mapped to IAO\_0000136, Range: TimeStep, Required: False)  
2. unit (Range: string, Required: False)  
3. source\_reference (Range: string, Required: False)

These are assigned to the TechParameter base class, granting every Calliope parameter the optional ability to act as a time-series data point and carry its own physical context.

### **Conceptual Graph Example: Time-Dependent Wind Profile**

Representing the capacity factor of a wind plant specifically at Hour 1:

Plaintext

1. // 1\. Establish the Environment and Time  
2. "Scenario\_Base"                    type          oeo:scenario  
3. "Wind\_Plant\_XX"                    type          CalliopeSupplyTechnology  
4. "TimeStep\_Hour\_1"                  type          oeo:time step  
5.   
6. // 2\. Instantiate the Parameter Container (Option B)  
7. "Wind\_CapFactor\_H1"                type          ontocal:SourceUseEquals   
8.   
9. // 3\. Apply Relational Hooks  
10. "Wind\_CapFactor\_H1"                bfo:part of      "Scenario\_Base"  
11. "Wind\_CapFactor\_H1"                iao:is about     "Wind\_Plant\_XX"     // The spatial/component link  
12. "Wind\_CapFactor\_H1"                iao:is about     "TimeStep\_Hour\_1"   // The temporal link  
13.   
14. // 4\. Apply Direct Data and Metadata  
15. "Wind\_CapFactor\_H1"                ontocal:value    0.35  
16. "Wind\_CapFactor\_H1"                ontocal:unit     "fraction"          // Enforced via slot\_usage  
17. "Wind\_CapFactor\_H1"                ontocal:source   "User CSV Upload"

18. 


## 2026-03-31 — Architecture: Linking CalliopeModelParameter to oeo:quantity values
**Decision:** Calliomapper strictly separates the software variable (the data "container") from the physical model component it describes, in accordance with BFO principles. This prevents category errors, such as asserting that a line of code physically possesses mass or energy.

However, mapping Calliope’s highly abstracted, mathematical parameters directly to OEO’s strict physical quantity value classes introduces significant engineering friction. Therefore, we have adopted a pragmatic "Data Attribute" approach for the MVP, deferring strict OEO semantic bridging to future work.

### **The Concerns with Strict OEO Mapping (Why we pivoted)**

Initially, the architecture proposed a 3-part linkage (Component \-\> Parameter Container \-\> oeo:quantity value \-\> Number/Unit). This was paused due to three major hurdles:

1. **Query Complexity:** Extracting a single numerical input (e.g., a capacity limit) required complex, multi-hop SPARQL queries, degrading user experience.  
2. **The "Carrier Agnostic" Ambiguity:** Calliope parameters like flow\_cap\_max do not dictate physics; they could represent electrical power (MW), heat energy (MWh), or water mass (kg/s). Forcing these into rigid OEO physical classes (like oeo:power value) risks introducing semantic errors depending on the user's specific model.  
3. **Non-Physical Parameters:** Calliope relies on booleans (e.g., cyclic\_storage) and enums, which violate the BFO definition of a quantity value (which mandates a numerical magnitude and unit).

### **The Current Approach: Pragmatic Data Attributes ("Option B")**

To maintain a clean graph shape while preserving BFO compliance, we retain the "Parameter Container" but drop the complex quantity value semantic bridge. Numerical values are attached directly to the parameter instance.

#### **1\. The Contextual Container (The Variable)**

The numerical feature is instantiated as a specific Information Content Entity based on our Calliope taxonomy.

* **Classification:** Typed as a specific Calliope parameter class (e.g., ontocal:FlowCapMax, which subclasses oeo:exogenous data).  
* **Targeting:** Linked to the specific model component it describes (e.g., a CalliopeSupplyTechnology) via **iao:is about**.  
* **Context:** Linked to the overarching simulation via **bfo:part of** pointing to an oeo:scenario.

#### **2\. The Direct Data Attribute**

Instead of bridging to a separate semantic magnitude, the values are stored directly on the container instance.

* **The Number:** Attached via a simple data attribute (e.g., ontocal:value \[float\]).  
* **Metadata Hooks:** This container architecture allows us to easily append arbitrary strings for unit or source directly to the parameter without breaking OEO physics rules.

### **Future Work: Strict Semantic Bridging**

A full implementation of the oeo:has quantity value bridge (mapping parameters to exact OEO classes like oeo:cost or oeo:efficiency) is flagged as future work. This can be implemented later as an optional "semantic inflation" script for users requiring strict interoperability with the wider Open Energy Ontology ecosystem.

### **Example: Mapping a Power Plant's Efficiency Limit (Current Approach)**

Plaintext

1. // 1\. Establish the Environment  
2. "Scenario\_Base"                    type  oeo:scenario  
3. "Plant\_XX"                         type  CalliopeSupplyTechnology  
4.   
5. // 2\. Instantiate and Contextualize the Data Container  
6. "Plant\_XX\_Efficiency\_Parameter"    type  ontocal:FlowOutEff  // (Subclass of oeo:exogenous data)  
7. "Plant\_XX\_Efficiency\_Parameter"    bfo:part of      "Scenario\_Base"  
8. "Plant\_XX\_Efficiency\_Parameter"    iao:is about     "Plant\_XX"  
9.   
10. // 3\. Assign the Value Directly (Pragmatic Approach)  
11. "Plant\_XX\_Efficiency\_Parameter"    ontocal:value    0.45  
12. "Plant\_XX\_Efficiency\_Parameter"    ontocal:unit     "fraction" // (Optional metadata hook)

13. 



## 2026-03-31 — Storage parameter scope: deferred

**Decision:** Storage parameters (`StorageCapMax`, `StorageCapMin`, `FlowCapPerStorageCapMax/Min`, `StorageLoss`, `StorageInitial`, `StorageDischargeDepth`, `CyclicStorage`, `CostStorageCap`) are modelled strictly as subclasses of `StorageTechParameter` in `ontocal_params.yaml`.

**Known limitation:** In Calliope v0.7, setting `include_storage: true` on a non-storage technology (e.g. a CSP supply tech with thermal storage buffer) makes all storage parameters valid for that technology too. The current schema does not capture this — a `StorageCapMax` instance cannot point at a `CalliopeSupplyTechnology` via `is_about` without violating the range constraint.

**Why deferred:** `include_storage: true` is an edge case (affects a small minority of supply techs) and the mapper handles it as a special-case flag in code. Over-engineering the schema for this now would add a mixin layer (`StorageCapableTechParameter`) with no immediate payoff.

**Future work:** If `include_storage` becomes common or a reasoner needs to enforce the constraint, introduce a `StorageCapableTechParameter` mixin that both `StorageTechParameter` and the special-case supply/conversion techs inherit from. See also the original deferral note in the 2026-03-20 entry below.

---


## 2026-03-27 - Drafitng base calliope ontology
* There will be a function to process overrides before writing the knowledge graph, since they can overwrite 
* Handling of overrides and labelling of scenarios. 
  * if the user runs the model with no overrides, the model name is set to the model name inside the config files
  * if the user runs an override:
    * if the user also sets a new model.name as override such model.name will be set as the new model name in the KG
    * if the user does not set it as override, the model name will be set to original_model_name""+"_override_name" the model name inside the config files
* scenarios 


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
