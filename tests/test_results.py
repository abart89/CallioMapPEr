# Tests for ResultsMapper (M3).
#
# Test cases to implement:
#   - test_results_aggregates_carrier_prod: given national_scale results.nc, assert that
#     total carrier_prod triples are present for each technology/carrier pair.
#   - test_results_aggregates_energy_cap: assert energy_cap observation triples are present.
#   - test_results_linked_to_structural_entities: assert observation triples reference
#     IRIs that exist in the structural named graph (no dangling references).
