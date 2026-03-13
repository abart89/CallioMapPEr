# ResultsMapper — M3 milestone.
#
# Reads a Calliope results.nc file (Xarray/NetCDF) and produces aggregate RDF
# observations linked to structural entities from the StructuralMapper.
#
# MVT scope — aggregates only (no timeseries):
#   - Total carrier production per technology over the simulated timespan
#   - Total carrier consumption per technology over the simulated timespan
#   - Installed energy capacity per technology (energy_cap)
#
# Timeseries representation is explicitly out of scope for MVT and tracked as an
# OPTIONAL feature in the development plan.
#
# Builds the results named graph:
#   <{run_id}/results>
#
# Returns an rdflib.Graph for the Translator to merge.
