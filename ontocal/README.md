# Historical ontology schemas

This directory preserves the earlier LinkML-based prototype. These files are not used to produce or validate the current package output and are not its ontology-authoring source.

The current implementation consumes a fixed copy of the separately maintained OntoCal Turtle ontology in `calliomapper/resources/ontocal.ttl`. The accompanying snapshot manifest identifies every bundled dependency and validation file. Changes to that representation belong in the OntoCal project; `scripts/sync_ontology_resources.py` copies an approved version into the package. No LinkML installation or generated Python classes are required.
