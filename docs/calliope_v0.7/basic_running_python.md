# Running a Model in Python

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/running-python/

## Basic Usage

To run a model programmatically, create a `calliope.Model` instance and execute its build and solve methods:

```python
import calliope
model = calliope.Model('path/to/model.yaml')
model.build()
model.solve()
```

**Note:** A model definition must be specified; omitting it raises an error.

## Alternative Loading Methods

Models can be loaded through several approaches:

- Passing an `AttrDict` or standard Python dictionary with the same nested format as YAML configuration (keys: `config`, `data_definitions`, `data_tables`, `nodes`, `techs`, etc.)
- Loading previously saved models from NetCDF: `model = calliope.read_netcdf('path/to/saved_model.nc')`

## Pre- and Post-Processing

Before calling `build()`, inspect and adjust model configuration via the xarray Dataset at `model.inputs`. After solving, access results through `model.results`. Export results using:

- `Model.to_csv()`
- `Model.to_netcdf()` (saves inputs and results)

## Applying Scenarios and Overrides

Two methods exist for overriding base models:

**By scenario:**
```python
model = calliope.Model('model.yaml', scenario='milp')
```

**By override dictionary:**
```python
model = calliope.Model(
    'model.yaml',
    override_dict={'config.solve.solver': 'gurobi'}
)
```

Both can be used simultaneously; scenarios apply first, then dictionary overrides.

## Tracking Progress

Enable verbose logging with `calliope.set_log_verbosity()` after importing. Log levels from least to most verbose:

1. **CRITICAL** - critical errors only
2. **ERROR** - errors only
3. **WARNING** - default; errors and warnings
4. **INFO** - errors, warnings, and stage messages with timestamps
5. **DEBUG** - solver logging; heavily verbose for troubleshooting

Use `include_solver_output=False` to disable solver-level logging.
