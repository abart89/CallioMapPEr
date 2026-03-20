# Interfacing with the Built Optimisation Problem

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/backend_interface/

## Overview

After loading a model, the solver backend is generated when calling `build()`. This invokes Pyomo to construct the model and send it to a solver specified in the run configuration. Once solved, users can access results through `model.results` and interact with the backend using `model.backend`.

## Key Capabilities

### 1. Inspecting Optimisation Problem Components

Query the backend to examine input parameters, decision variables, global expressions, constraints, and objectives stored as xarray.DataArray objects. The `model.backend.parameters` property provides an xarray.Dataset of input parameters transformed into mutable objects, with missing data filled using predefined defaults from Calliope's base math.

### 2. Updating Parameter Values

Use `model.backend.update_parameter()` to modify specific values. Example:

```python
new_data = xr.DataArray(0.1, coords={"techs": "ccgt", "nodes": "region1"})
model.backend.update_param("flow_out_eff", new_data)
```

Note: Changes require rerunning the backend to affect results.

### 3. Modifying Decision Variable Bounds

Most bounds are input parameters (like `flow_cap_max`), updated via `model.backend.update_parameter()`. For fixed numeric values in custom math, use `model.backend.update_variable_bounds()`:

```python
new_data = xr.DataArray(70, coords={"techs": "battery", "nodes": "region2"})
model.backend.update_variable_bounds("flow_out", max=new_data)
```

### 4. Fixing Decision Variables

Lock variables to previous optimal values using `model.backend.fix_variable()` with binary xarray.DataArray values:

```python
new_data = xr.DataArray(True, coords={"techs": "pv"})
model.backend.fix_variable("area_use", new_data)
```

Use `unfix_variable()` to reverse this action.

### 5. Rerunning Optimisation

After modifying parameters or variables, call `model.solve(force=True)` to solve with current backend state. This updates `model.results` with new solution data.
