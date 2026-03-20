# Model Configuration

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/config/

## Overview

Calliope's configuration is organized into three stages:

- **`init`**: Used when initializing a model (`calliope.Model(...)`)
- **`build`**: Used when building the optimization problem (`calliope.Model.build(...)`)
- **`solve`**: Used when solving the problem (`calliope.Model.solve(...)`)

You can override configuration values at each stage using keyword arguments:

```python
# Override init config
model = calliope.Model("path/to/model.yaml", subset={"timesteps": ["2005-01", "2005-02"]})

# Override build config
model.build(ensure_feasibility=True)

# Override solve config
model.solve(save_logs="path/to/logs/dir")
```

While no configuration options are strictly required, you'll typically want to set `init.name`, `init.calliope_version`, `build.mode`, and `solve.solver`.

## Key Configuration Options

### Backend Selection (`config.build.backend`)

The default backend uses the Pyomo library. For Gurobi license holders, a direct Python API interface is available, which may reduce memory and time consumption. To use it:

1. Install Gurobi: `mamba install gurobi::gurobi`
2. Configure: `config.build.backend: gurobi` (YAML) or `model.build(backend="gurobi")` (Python)

### Ensuring Feasibility (`config.build.ensure_feasibility`)

Set to `true` to guarantee the solver finds a feasible solution by creating `unmet_demand` and `unused_supply` variables with very high costs. These appear only when necessary.

You can customize the "big M" parameter (`data_definitions.bigM`), which represents unmet demand costs. Default is 1×10⁹, but should align with maximum expected system costs (typically 1×10⁶ for urban models, as low as 1×10⁴ for rescaled data).

### Operating Modes (`config.build.mode`)

Three modes are available:

- **`base`** (default): Standard optimization with no additional processing
- **`operate`**: Fixed capacities; uses receding horizon control
- **`spores`**: Runs `base` mode first, then finds N alternative configurations with similar costs but different technology/location choices

### Solver Selection (`config.solve.solver`)

Supported solvers include `glpk`, `gurobi`, `cplex`, and `cbc`. All Pyomo-compatible solvers work with Calliope.

For Gurobi, the direct Python interface is typically fastest:

```yaml
config:
  solve:
    solver: gurobi
    solver_io: python
```

GLPK is recommended for beginners on Windows systems.
