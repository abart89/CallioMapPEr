# The Calliope Model and Backend Objects (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/calliope_model_object/

This tutorial covers the Calliope model object and its backend, demonstrating how to work programmatically with model data and the optimization problem.

## Overview

The `calliope.Model` object is the primary interface for interacting with Calliope models in Python. After building and solving, it provides access to:

- `model.inputs` — xarray Dataset of all input parameters and lookups
- `model.results` — xarray Dataset of all optimization results
- `model.backend` — Interface to the underlying optimization problem

## Key Operations

### Inspecting model data

```python
import calliope
model = calliope.examples.national_scale()
model.build()
model.solve()

# Access inputs
model.inputs.flow_cap_max

# Access results
model.results.flow_cap
model.results.flow_out
```

### Working with the backend

The backend provides methods for:
- Inspecting optimization components (`model.backend.parameters`, `model.backend.variables`, etc.)
- Updating parameter values before resolving
- Fixing/unfixing decision variables
- Exporting the problem as an LP file

### Post-solve analysis

Results are stored as xarray DataArrays with named dimensions (nodes, techs, carriers, timesteps, costs). Standard xarray and pandas operations apply:

```python
# Convert to pandas series, dropping NaN
model.results.flow_cap.to_series().dropna()

# Select specific dimensions
model.results.flow_out.sel(techs="ccgt")
```

**Note:** A downloadable Jupyter notebook demonstrates all key operations on the model and backend objects.
