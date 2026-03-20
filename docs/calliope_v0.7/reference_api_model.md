# API Reference: Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/model/

## Overview

The `calliope.Model` class is the primary interface for working with Calliope energy system models in Python. It inherits from `ModelStructure` and manages the complete lifecycle of optimization problems.

## Class Definition

```python
calliope.Model(inputs, attrs, results=None, _reentry=True, **kwargs)
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `inputs` | `xr.Dataset` | Input dataset for the model | Required |
| `attrs` | `CalliopeAttrs` | Model attributes and properties | Required |
| `results` | `xr.Dataset \| None` | Results from a compatible prior model run | `None` |
| `_reentry` | `bool` | Whether to reinitialize math and configuration | `True` |
| `**kwargs` | | Initialization keyword arguments | `{}` |

## Key Properties

- **`all_attrs`**: Returns all model attributes as a `CalliopeAttrs` object
- **`backend`**: The backend model interface
- **`config`**: Model configuration settings
- **`definition`**: Model definition
- **`inputs`**: Input dataset
- **`is_built`**: Boolean indicating if optimization problem is constructed
- **`is_solved`**: Boolean indicating if model has been solved
- **`math`**: Mathematical formulation
- **`name`**: The model's name
- **`results`**: Results dataset (empty until solved)
- **`runtime`**: Runtime information and timings

## Core Methods

### `build(force=False, **kwargs)`

Constructs the optimization problem in the chosen backend interface. Set `force=True` to overwrite existing results.

### `solve(force=False, warmstart=False, **kwargs)`

Solves the built optimization problem. The `warmstart` parameter can improve solution time for similar sequential problems, though it doesn't work with all solvers (CBC, GLPK).

**Raises:**
- `ModelError` if problem not yet built
- `ModelError` if results exist and `force` is not True
- `ModelError` for "operate" mode preprocessing conflicts

### `run(force_rerun=False)`

Deprecated method combining `build()` and `solve()`. Use these methods separately instead.

### `info()`

Returns a string summarizing the model name and size, including the number of valid node:tech:carrier combinations.

### `to_csv(path, dropna=True, allow_overwrite=False)`

Exports inputs and results to CSV files. Setting `dropna=True` produces smaller files by removing NaN values.

### `to_netcdf(path)`

Exports inputs, results, and attributes to a single NetCDF file.

### `dump_all_attrs()`

Returns all class attributes as a single dictionary from the Pydantic model.
