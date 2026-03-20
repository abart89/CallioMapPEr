# Running a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/running/

Calliope offers three primary methods for executing models:

1. **Command-line interface** via `calliope run`
2. **Python API** for programmatic execution
3. **Script generation** using `calliope generate_runs` for batch processing on clusters

## Command-Line Execution

The quickest approach involves the CLI tool. To run a model and export results:

```bash
$ calliope run model.yaml --save_netcdf=results.nc
```

Alternatively, save outputs as CSV files:

```bash
$ calliope run model.yaml --save_csv=results_directory
```

This generates individual CSV files per variable. Consult the command-line documentation for details on applying scenarios or overrides.

## Optimizing Solution Speed

Large models require extended processing time. While remote execution on computing clusters is often practical, several strategies exist to accelerate solutions when immediate results are needed. The troubleshooting section provides comprehensive guidance on optimization techniques.

## Troubleshooting Failed Runs

When issues arise, investigate in this priority order:

- **Model definition errors**: Calliope identifies common mistakes and provides diagnostic messages
- **Infeasible models**: Properly structured but unsolvable models trigger solver notifications after processing
- **Calliope bugs**: Rare crashes during model construction or result processing

The troubleshooting documentation contains detailed diagnostic assistance for all three scenarios.
