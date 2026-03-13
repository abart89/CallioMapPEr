# 1. Mission Statement
CallioMapper is an open-source Python library that transforms Calliope (v0.7+) models into standardized, linked-data representations. It addresses the  interpretability and interoperability problem in energy modeling by providing an automated pipeline to map simulation inputs and outputs, and model epistemic context to a pre-defined schema based on the Open Energy Ontology (OEO).

# 2. Core Pillars
* Input/Output data representation: CallioMapper will provide a standardized way to represent Calliope model inputs and outputs in a way that is both human-readable and machine-readable. This will be achieved by leveraging a default ontology of the Calliope framework mostly based on the Open Energy Ontology (OEO) to provide a standardized way to represent entities from Calliope models.

* Epistemic Transparency: Energy models are built on assumptions. CallioMapper treats "Rationale" as a high-priority data field which users can opt-in to include in the produced data models. It will capture why a parameter was chosen, who provided the data, and the epistemic context of the modeling decisions.

* Version 0.7 Native: Architected specifically for the flat-parameter and node-based structure of Calliope v0.7. It will be able to represent several domains of information related to models.

* Linked-Data Ecosystem: By outputting RDF-compatible data models, CallioMapper allows energy models to be more interpretable and interoperable, hence integrated into broader Urban System knowledge graphs.

# 3. Impact Goal
The goal is to have a tool that can bridge the gap between Calliope models and the broader energy modeling community, allowing for greater interpretability and interoperability of energy models by also being the gateway to scalable and automatable high-level verifications on model quality and consistency. 