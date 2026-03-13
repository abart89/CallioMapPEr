# Validation utilities.
#
# Wraps pyshacl to validate a produced rdflib.ConjunctiveGraph against the SHACL
# shapes generated from the default LinkML schema.
#
# Called automatically by the Translator before any output is written or returned.
# Raises a descriptive ValidationError on failure — never silently emits invalid output.
#
# The SHACL shapes file is expected at: ontology/shapes.shacl.ttl
# (auto-generated from the LinkML schema via `make generate`)
