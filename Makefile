PYTHON ?= python

# OntoCal is maintained in its own repository. This copies a reviewed snapshot.
sync-ontology:
	$(PYTHON) scripts/sync_ontology_resources.py "$(ONTOCAL_DIR)"

test:
	$(PYTHON) -m pytest tests/ -q

install:
	$(PYTHON) -m pip install -e '.[dev]'
