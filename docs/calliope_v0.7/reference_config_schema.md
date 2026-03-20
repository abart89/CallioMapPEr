# Model Configuration Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/config_schema/

Calliope's configuration class defines all options used when initializing and running a model.

## Init Configuration

**Basic Settings:**
- `name`: Model name (string or null)
- `calliope_version`: Framework version intended for the model (string or null)
- `broadcast_input_data`: Whether to broadcast single YAML data entries across all index items (boolean, default: false)

**Dimension Management:**
- `subset`: Define dimension subsets as arrays of strings, integers, or numbers
- `resample`: Configure dimension resampling settings
- `time_cluster`: Reference an input data array name for timeseries clustering

**Data Format Settings:**
- `datetime_format`: Timestamp format for timeseries data (default: "ISO8601")
- `date_format`: Datestamp format (default: "ISO8601")
- `distance_unit`: Transmission link distance unit - either "km" or "m" (default: "km")

**Optimization Settings:**
- `mode`: Running mode - "base", "operate", or "spores" (default: "base")
- `extra_math`: List of additional math entries to apply
- `math_paths`: Define custom math file locations
- `pre_validate_math_strings`: Scan math definitions for errors at initialization (boolean, default: false)

## Build Configuration

- `backend`: "pyomo" or "gurobi" (default: "pyomo")
- `ensure_feasibility`: Include variables for unmet demand debugging (boolean, default: false)
- `objective`: Internal objective function name (default: "min_cost_optimisation")

**Operate Mode Options:**
- `window`: Rolling window as pandas frequency string (default: "24h")
- `horizon`: Rolling horizon, must be >= window (default: "48h")

## Solve Configuration

- `postprocessing_active`: Run postprocessing functions after solving (boolean, default: true)
- `save_logs`: Directory path for optimization logs (path or null)
- `shadow_prices`: Array of constraint names for shadow price calculation
- `solver`: Solver name with Pyomo interface (default: "cbc")
- `solver_io`: Solver interface option (string or null)
- `solver_options`: Key-value pairs for solver configuration
- `zero_threshold`: Postprocessing threshold for rounding artifacts (default: 1e-10)

**SPORES Mode Options:**
- `scoring_algorithm`: Update algorithm - "integer", "relative_deployment", "random", or "evolving_average"
- `number`: Iterations after initial run (integer, default: 3)
- `save_per_spore_path`: Directory for individual SPORE results (path or null)
- `use_latest_results`: Continue from existing results (boolean, default: false)
- `tracking_parameter`: Input parameter for technology filtering (string or null)
- `score_threshold_factor`: Capacity threshold factor for scoring (number, default: 0.1, minimum: 0)
