# StructuralMapper — M1 milestone.
#
# Parses Calliope v0.7 model inputs (nodes.yaml, techs.yaml, and related config files)
# and maps the flat-parameter structure to OEO classes using the default LinkML schema.
#
# Workflow:
#   1. Load and validate Calliope YAML inputs (nodes, technologies, parameters).
#   2. Instantiate auto-generated Pydantic objects (from generated/) for each entity.
#   3. Use rdflib to build the structural named graph:
#        <{run_id}/structural>
#   4. Return the populated rdflib.Graph for the Translator to merge.
#
# Key design rule: no filesystem I/O here. Accept parsed dicts or Pydantic objects,
# not raw file paths. File loading is handled by the Translator.
