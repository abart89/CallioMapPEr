# Integration tests for the Translator.
#
# Test cases to implement:
#   - test_end_to_end_national_scale: full pipeline on national_scale fixture.
#     Assert output .nq file contains both named graphs and passes SHACL validation.
#   - test_end_to_end_urban_scale: same as above for urban_scale fixture.
#   - test_translator_accepts_in_memory_objects: assert Translator works when passed
#     pre-loaded dicts/Xarray datasets instead of file paths (notebook use case).
#   - test_save_produces_valid_nq_file: assert the saved file is parseable by rdflib.
