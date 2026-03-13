# EpistemicEngine — M2 milestone.
#
# Ingests a user-filled YAML sidecar (based on the template in templates/sidecar.yaml)
# and generates PROV-O provenance triples linked to structural entities produced by
# the StructuralMapper.
#
# Supports two annotation levels:
#   - Model-level: high-level context about the model run (author, date, purpose, assumptions)
#   - Entity-level: per-technology or per-node rationale and data source annotations
#
# Builds the provenance named graph:
#   <{run_id}/provenance>
#
# Returns an rdflib.Graph for the Translator to merge.
