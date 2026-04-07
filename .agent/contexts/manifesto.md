# 1. Mission Statement

CallioMapper is an open-source Python library that generates structured, linked-data representations of Calliope v0.7 energy system models — their topology, technology mix, parameters, and results — and exposes them as queryable RDF using a purpose-built ontology (`ontocal:`) that extends the Open Energy Ontology (OEO).

The field has reached a consensus (Lombardi et al., 2025) that open models are necessary but not sufficient: what matters is *practical usefulness*, which requires transparency about modeling assumptions and reproducibility of results. CallioMapper operationalizes that transparency for Calliope users — without requiring them to restructure their models or learn ontology engineering.

# 2. Primary Value Propositions

**1. Archive and compare across runs.** Research groups running sensitivity studies have no structured way to query across runs today. Results live in NetCDF files, configs in YAML directories, cross-run comparisons require custom scripts per study. After CallioMapper: "find all runs where installed gas capacity exceeded 5 GW" is one SPARQL query over the run archive. M1+M3 alone enables this.

**2. Provenance for publication.** Machine-readable PROV-O attribution, data sourcing, and scenario derivation chains directly answer the reviewer question: "where did these parameter values come from?" The output is a structured supplement — not a PDF — that can accompany journal submissions or Zenodo deposits. The provenance module (ships at launch) enables this.

**3. OEP/OEKG contribution pathway.** The Open Energy Knowledge Graph is the community infrastructure for structured energy model metadata, but every entry requires manual form-filling today. CallioMapper auto-generates OEO-aligned RDF compatible with the OEKG ingest format — removing the single largest friction point for modelers who want to contribute to the platform.

# 3. What CallioMapper Is NOT (at launch)

- It is **not** a semantic enrichment tool out of the box. The base layer does not guess that `ccgt_plant` is a combined-cycle gas turbine — it only maps what Calliope actually writes. Semantic enrichment (linking technologies to OEO concrete classes, physical system entities, etc.) is encouraged and architecturally supported, but happens through **extensions**, not the core.
- It is **not** a cross-framework interoperability layer. It speaks Calliope v0.7. Cross-framework alignment (PyPSA, OSeMOSYS, TIMES) is a different, much larger project.
- It is **not** an automated OEP submission tool at launch. The RDF output is OEKG-compatible by design, but automated upload/factsheet generation is deferred to a later extension.

The extension architecture means that semantic depth is opt-in and additive. The base layer gives you a sound, queryable RDF skeleton. Extensions — including the provenance module shipped at launch — progressively layer meaning on top of it.

# 4. Target Audience

**Primary:** Research groups that (a) use Calliope, (b) run many model variants (sensitivity studies, scenario families), and (c) want structured querying across runs or need to satisfy reproducibility requirements for journal submission.

**Secondary:** Projects contributing Calliope model metadata to the Open Energy Platform or other OEO-aligned initiatives (e.g., openmod community, German/European energy modeling projects).

**Not the audience:** Anyone expecting automated semantic enrichment, cross-framework interoperability, or time-series data management.

# 5. Core Design Principles

* **Map what exists, enrich through extensions.** The base layer is deterministic and requires no user effort. Semantic enrichment is encouraged but always opt-in: three fields in the provenance module produce a valid attribution graph; additional extensions progressively deepen the representation. The base layer is never wrong; extensions are never required.

* **Calliope v0.7 native.** Architected specifically for the flat-parameter, node-based structure of Calliope v0.7. No support for earlier versions, no aspirations to be framework-agnostic.

* **ontocal: as a proper OEO extension.** The `ontocal:` namespace defines Calliope-specific classes as OWL subclasses of OEO abstract classes. This is not loose annotation — OWL reasoners infer OEO types automatically. The output is OEO-compatible without requiring OEO knowledge from the user.

* **Linked-data output, local-first consumption.** The primary consumer is a local triple store (Fuseki, Oxigraph) running alongside the model archive. OEKG upload is architecturally planned but not required to get value from the tool.

* **FAIR4RS alignment.** CallioMapper is a practical implementation of FAIR principles (FAIR4RS, 2022) for energy optimization models — making Calliope model artifacts Findable, Accessible, Interoperable, and Reusable without requiring the modeler to become an ontology engineer.

# 6. Impact Goal

A research group using CallioMapper across a 50-run sensitivity study can answer cross-run structural and results queries in minutes rather than days, produce a machine-readable provenance supplement for their journal submission, and — if they choose — contribute a structured model description to the Open Energy Platform with no additional manual effort. That is the concrete impact: reducing the overhead of rigorous modeling practice, not adding to it.