# Makefile — project automation shortcuts.

VENV    := dev_calliomapper/bin
SCHEMA  := ontocal
GEN     := calliomapper/generated

# ---------------------------------------------------------------------------
# Schema generation — YAML-first workflow (preferred)
#
# Primary authoring surface is the LinkML YAML file.
# The .ttl is generated from the YAML via gen-owl and is a build artifact.
# ---------------------------------------------------------------------------

# Regenerate all artifacts from the real LinkML schema.
# Preferred entry point: edit calliope_oeo.yaml, then run this target.
# Produces:
#   calliomapper/generated/calliope_oeo.py  — Pydantic classes
#   ontocal/calliope_oeo_shapes.ttl        — SHACL shapes
#   ontocal/calliope_oeo.ttl               — OWL/Turtle (for Protégé / ontologists)
generate:
	$(VENV)/gen-pydantic $(SCHEMA)/ontocal_core.yaml > $(GEN)/ontocal_core.py
	$(VENV)/gen-shacl   $(SCHEMA)/ontocal_core.yaml > $(SCHEMA)/ontocal_core_shapes.ttl
	$(VENV)/gen-owl     $(SCHEMA)/ontocal_core.yaml > $(SCHEMA)/ontocal_core.ttl

# Regenerate artifacts from the dummy schema (development only).
generate-dummy:
	$(VENV)/gen-pydantic $(SCHEMA)/dummy_schema.yaml > $(GEN)/dummy_schema.py
	$(VENV)/gen-shacl   $(SCHEMA)/dummy_schema.yaml > $(SCHEMA)/dummy_shapes.ttl
	$(VENV)/gen-owl     $(SCHEMA)/dummy_schema.yaml > $(SCHEMA)/dummy.ttl

# ---------------------------------------------------------------------------
# TTL-first workflow (for ontologists using Protégé)
#
# If the .ttl is edited directly in Protégé, the YAML must be manually synced.
# There is no automated TTL→YAML converter. After syncing, run `make generate`.
#
# Checklist when editing .ttl in Protégé:
#   1. Edit calliope_oeo.ttl in Protégé
#   2. Manually update calliope_oeo.yaml to reflect the changes (class_uri, slots, mixins)
#   3. make generate
# ---------------------------------------------------------------------------

# Run the test suite.
test:
	$(VENV)/pytest tests/ -v

# Install development dependencies.
install:
	pip install -e ".[dev]"
