# Generating Scripts to Repeatedly Run Variations of a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/scripts/

This documentation explains how to automate model runs with different configurations using Calliope's command-line tools.

## Generate Runs

The `calliope generate_runs` command creates automated scripts to execute models with varying parameters. Required arguments include:

- Model configuration file
- Output script filename
- `--kind`: Script type (windows for batch files, bash for Linux/macOS, bsub for LSF clusters, sbatch for SLURM clusters)
- `--scenarios`: Semicolon-separated scenario list (e.g., `scenario1;scenario2` or `override1,override2a;override1,override2b`)

**Example Windows batch script:**
```
calliope generate_runs model.yaml run_model.bat --kind=windows --scenarios "run1;run2;run3;run4"
```

**Example HPC cluster submission:**
```
calliope generate_runs model.yaml submit_runs.sh --kind=bsub --cluster_mem=1G --cluster_time=100 --cluster_threads=5 --scenarios "run1;run2;run3;run4"
```

Optional parameters include `--cluster_threads`, `--cluster_mem`, `--cluster_time`, `--additional_args`, and `--debug`.

Results save as `out_{run_number}_{scenario_name}.nc` files in the script directory.

## Generate Scenarios

The `calliope generate_scenarios` tool creates scenario definition files from existing overrides, useful when numerous override combinations exist.

**Example usage:**
```
calliope generate_scenarios model.yaml scenarios.yaml y2000;y2001;y2002;y2003;y2004;y2005;y2006;y2007;y2008;y2009;y2010 cost_low;cost_medium;cost_high --scenario_name_prefix="run_"
```

This generates named scenarios combining all specified overrides.
