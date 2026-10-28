# Saved examples from the Calliope 0.7.0 release

These are genuine results of running the national-scale and urban-scale examples
distributed with **Calliope 0.7.0**, the stable release. They were generated locally
with **HiGHS 1.15.1**, using Calliope's native HiGHS backend. Both runs terminated
with an `optimal` result. The earlier examples under `examples/national_scale/`
and `examples/urban_scale/` are Andrea's original saved exports from
`0.7.0.dev7`; they remain unchanged.

Each example contains:

- `source/`: the complete upstream example configuration and data tables, copied
  without changes from the installed Calliope 0.7.0 distribution.
- `results_directory/`: the CSV files and `attrs.yaml` written by Calliope after
  the run. These files are the input to CallioMapper and its routine tests.
- `solver-logs/`: the log produced by HiGHS for that execution.

The [manifest](manifest.json) records source and result file hashes, runtime
metadata, dimensions, the exact Calliope and solver versions, and the upstream
release and distribution links. The preparation environment is recorded in
[preparation-requirements.txt](preparation-requirements.txt). The example sources
are attributed to the Calliope contributors and retain the
[Calliope Apache 2.0 license](CALLIOPE-LICENSE).

The upstream configurations select five days for the national model and two
days for the urban model. Those periods are retained. The preparation command
changes the backend and solver from the upstream defaults to HiGHS and asks it
to save a log; it does not change the scenario, parameter data or optimisation
objective. The urban example still includes its upstream additional mathematics.
The new release and solver can produce different numerical results from the
older developer-preview examples. Numerical checks use the values in these
new files, rather than assuming that they equal the earlier results.

## Historical preparation

These HiGHS outputs are retained as an unchanged numerical reference. The
current preparation script and primary tutorials now use GLPK. See the
[GLPK examples](../calliope-0.7.0-glpk/README.md) for the current installation
and regeneration procedure. Do not describe a new GLPK run as a reproduction
of this particular HiGHS execution.

This earlier preparation used `calliope.read_yaml(...)`,
`model.build(backend="highs")`, `model.solve(solver="highs", save_logs=...)`
and `model.to_csv(...)`, with the versions recorded above. Its saved exports,
logs, source files and manifest have not been edited. The native `attrs.yaml`
files retain the original developer's local log-directory paths as execution
metadata; these paths are not required for translation.

## Source files compared with the developer-preview copies

This is a file-level comparison of the checked-in sources. A changed file does
not, by itself, imply that a numerical parameter changed.

| Example | Identical source files | Changed source files |
| --- | --- | --- |
| National | `data_tables/cluster_days.csv`, `model_config/locations.yaml`, `model_config/techs.yaml` | `data_tables/costs.csv`, `data_tables/time_varying_params.csv`, `model.yaml`, `scenarios.yaml` |
| Urban | `additional_math.yaml`, all three `data_tables/` files, `model_config/locations.yaml`, `scenarios.yaml` | `model.yaml`, `model_config/techs.yaml` |

The saved export format also changes: stable 0.7.0 uses `inputs_active.csv` to
identify active node–technology combinations, where the earlier examples use
`inputs_definition_matrix.csv`. The stable carrier arrays contain explicit
`True` and `False` values. CallioMapper identifies the format from the available
version information and structural arrays, then verifies the coordinates before
mapping them. Stable exports normally omit the actual executable-version field;
their configured target version is not evidence that this version produced the
results. The preparation manifest independently records the software used for
these two saved executions.
