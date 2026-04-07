# Tests for EpistemicEngine (Extension).
#
# Test cases to implement:
#   - test_extension_model_level_triples: given a filled model-level extension, assert
#     that PROV-O triples for author, date, and purpose are present in the output graph.
#   - test_extension_entity_level_triples: given entity-level annotations, assert that
#     rationale triples are linked to the correct technology/node IRIs from core.
#   - test_missing_extension_produces_empty_provenance_graph: assert that omitting the
#     extension results in an empty (but valid) provenance named graph, not an error.
