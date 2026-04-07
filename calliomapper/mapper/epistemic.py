# EpistemicEngine — Extends Core Graph.
#
# Ingests a user-filled YAML extension (based on the template in templates/epistemic_extension.yaml)
# and generates PROV-O provenance triples linked to core entities produced by
# the CoreMapper.
#
# Supports two annotation levels:
#   - Model-level: high-level context about the model run (author, date, purpose, assumptions)
#   - Entity-level: per-technology or per-node rationale and data source annotations
#
# Builds the provenance named graph:
#   <{run_id}/provenance>
#
# Returns an rdflib.Graph for the Translator to merge.
