# API Reference: Postprocess

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/postprocess/

## capacity_factor()

**Function Signature:**
```python
capacity_factor(results: xr.Dataset, model_data: xr.Dataset, systemwide=False) -> xr.DataArray
```

**Purpose:** Computes capacity factors from model results.

**Key Details:**
- Handles both operating mode (where `flow_cap` is an input parameter) and optimization mode (where it's a result variable)
- For system-wide calculations, the function applies timestep weights to ensure higher-weighted periods influence results proportionally
- Returns a DataArray containing capacity factor values

**Implementation Note:** When `systemwide=True`, the calculation aggregates production across timesteps and nodes while accounting for their respective weights.

---

## systemwide_levelised_cost()

**Function Signature:**
```python
systemwide_levelised_cost(results: xr.Dataset, model_data: xr.Dataset, total: bool = False) -> xr.DataArray
```

**Purpose:** Calculates levelized costs across the entire system.

**Parameters:**
- `results`: Model optimization results
- `model_data`: Input data and parameters
- `total`: When `False`, returns per-technology costs; when `True`, returns aggregate system cost

**Important Implementation Details:**
The function accounts for timestep weighting asymmetrically—costs already incorporate weights in constraints, but production metrics require manual scaling for consistency. This weighting adjustment occurs solely during computation and doesn't modify underlying result data.

**Return Value:** A DataArray indexed by technologies, carriers, and cost types (or carriers and costs when `total=True`).
