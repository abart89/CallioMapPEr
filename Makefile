# Makefile — project automation shortcuts.

# Regenerate all artifacts from the LinkML schema.
# Produces: calliomapper/generated/ Pydantic classes, ontology/shapes.shacl.ttl
generate:
	@echo "TODO: implement LinkML code generation pipeline"
	# gen-pydantic ontology/calliope_oeo.linkml.yaml > calliomapper/generated/model.py
	# gen-shacl ontology/calliope_oeo.linkml.yaml > ontology/shapes.shacl.ttl

# Run the test suite.
test:
	pytest tests/

# Install development dependencies.
install:
	pip install -e ".[dev]"
