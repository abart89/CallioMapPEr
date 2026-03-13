# I/O utilities — the ONLY layer allowed to touch the filesystem.
#
# Responsibilities:
#   - Load Calliope YAML config files into dicts
#   - Load the epistemic sidecar YAML
#   - Load Xarray datasets from results.nc
#   - Serialize rdflib.ConjunctiveGraph to .nq file
#   - Push a ConjunctiveGraph to a SPARQL endpoint via SPARQLUpdateStore (optional)
#
# All other modules receive already-loaded data objects, never file paths.
