# Saved examples and test data

The current tests read the national-scale and urban-scale CSV exports under
[`examples/calliope-0.7.0-glpk/`](../../examples/calliope-0.7.0-glpk/README.md). Each export
contains `attrs.yaml`, effective input arrays and saved numerical results from
a genuine Calliope 0.7.0 execution. The preparation manifest records source and
result checksums, software versions and execution metadata.

The original `0.7.0.dev7` exports remain under
[`examples/national_scale/`](../../examples/national_scale/) and
[`examples/urban_scale/`](../../examples/urban_scale/). Tests retain explicit
checks of that earlier format. Their preservation and attribution are described
in the [example documentation](../../examples/README.md).

Routine tests read saved CSV files; they do not load NetCDF files, instantiate
Calliope models or run an optimiser. Tests also construct small synthetic
exports and RDF graphs in temporary directories to check invalid input,
identifiers, annotations and query behaviour. Those invented cases are not
represented as real model executions.

`kg_expected.yaml` in this directory is a historical reference from the earlier
prototype. The current test suite does not read it. Current expectations are
defined in the tests and checked against the appropriate saved example or
explicitly synthetic case.

To prepare a new genuine example, follow the optional regeneration procedure in
the [stable example documentation](../../examples/calliope-0.7.0-glpk/README.md).
Keep existing snapshots unchanged and record a new execution separately.
