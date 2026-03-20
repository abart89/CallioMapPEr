# Command Line Interface Reference

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/cli/

## Overview

The `calliope` command line tool provides utilities for managing and executing energy systems models within the Calliope framework.

## Main Commands

### calliope generate_runs

Generates a script to execute multiple models sequentially.

**Usage:** `calliope generate_runs [OPTIONS] MODEL_FILE OUT_FILE`

**Key Options:**
- `--kind TEXT`: Script type (bash, bsub, sbatch, or windows)
- `--scenarios TEXT`: Specify scenarios to run
- `--cluster_threads INTEGER`: Thread allocation for cluster jobs
- `--cluster_mem TEXT`: Memory specification for cluster jobs
- `--cluster_time TEXT`: Time limit for cluster jobs
- `--additional_args TEXT`: Extra arguments passed to `calliope run`
- `--override_dict TEXT`: Override parameters
- `--debug`: Enable debug output
- `--quiet`: Reduce verbosity
- `--pdb`: Interactive debugger on errors (with --debug)

### calliope generate_scenarios

Creates scenario definitions from combinations of overrides.

**Usage:** `calliope generate_scenarios [OPTIONS] MODEL_FILE OUT_FILE [OVERRIDES]...`

**Key Options:**
- `--scenario_name_prefix TEXT`: Prefix for generated scenario names
- `--debug`: Enable debug output
- `--quiet`: Reduce verbosity
- `--pdb`: Interactive debugger on errors

### calliope new

Initializes a new model based on built-in example templates.

**Usage:** `calliope new [OPTIONS] PATH`

**Key Options:**
- `--template TEXT`: Example model to use as template
- `--debug`: Enable debug output

### calliope run

Executes a model from YAML configuration or pre-built NetCDF format.

**Usage:** `calliope run [OPTIONS] MODEL_FILE`

**Key Options:**
- `--scenario TEXT`: Specify scenario to run
- `--model_format TEXT`: Explicitly set format (yaml or netcdf)
- `--override_dict TEXT`: Override model parameters
- `--save_netcdf TEXT`: Export results to NetCDF
- `--save_csv TEXT`: Export results to CSV
- `--save_logs TEXT`: Save logging output
- `--save_lp TEXT`: Build and save optimization model (LP format)
- `--debug`: Enable debug output
- `--quiet`: Reduce verbosity
- `--profile`: Run performance profiling
- `--fail_when_infeasible / --no_fail_when_infeasible`: Exit with failure code on infeasible problems
