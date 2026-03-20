# Migrating from v0.6 to v0.7

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/migrating/

This guide documents major user-facing changes for upgrading Calliope models from v0.6 to v0.7.

## Changes

### Flat Technology Definition

The nested structure separating `essentials`, `constraints`, and `costs` has been flattened. All technology parameters are now defined at the same level.

**v0.6 approach:**
```yaml
ccgt:
  essentials:
    name: 'Combined cycle gas turbine'
    parent: supply
    carrier_out: power
  constraints:
    energy_eff: 0.5
  costs:
    monetary:
      energy_cap: 750
```

**v0.7 approach:**
```yaml
ccgt:
  name: 'Combined cycle gas turbine'
  base_tech: supply
  carrier_out: power
  flow_out_eff: 0.5
  cost_flow_cap:
    data: 750
    index: monetary
    dims: costs
```

### Data Tables Replace file=/df= References

Timeseries data loading via `file=` or `df=` parameters is replaced with a top-level `data_tables` section for loading CSV and similar tabular data.

**v0.6 approach:**
```yaml
techs:
  demand_tech:
    constraints:
      resource: file=demand_file.csv
      force_resource: true
```

**v0.7 approach:**
```yaml
data_tables:
  demand_data:
    data: demand_file.csv
    rows: timesteps
    columns: nodes
    add_dims:
      techs: demand_tech
      parameters: sink_equals
```

### Demand Values Now Positive

Demand data must use strictly positive numbers (previously negative). The `carrier_con` decision variable is now called `flow_in`.

### Split model.run() Into Two Steps

The single `model.run()` method is replaced with:
- `model.build()` - Creates optimization problem components
- `model.solve()` - Sends problem to solver and generates results

### Configuration Reorganization

Model configuration now splits into stages:
- `config.init` - Applied during model creation
- `config.build` - Applied when building the optimization problem
- `config.solve` - Applied when solving

**v0.6 approach:**
```yaml
config:
  model:
    subset_time: ["2005-01", "2005-02"]
  run:
    solver: cbc
```

**v0.7 approach:**
```yaml
config:
  init:
    subset:
      timesteps: ["2005-01", "2005-02"]
  solve:
    solver: cbc
```

### Locations → Nodes

`locations` has been renamed to `nodes` for clarity and to avoid conflicts with pandas/xarray `.loc` accessors.

### Parent and Tech Groups → Base Tech and Templates

- `parent` is renamed `base_tech` (fixed to one of: demand, supply, conversion, transmission, storage)
- `tech_groups` is replaced with `templates` for more flexible reuse

**v0.6 approach:**
```yaml
tech_groups:
  supply_interest_rate:
    essentials:
      parent: supply
    costs:
      monetary:
        interest_rate: 0.1
techs:
  supply_tech:
    essentials:
      parent: supply_interest_rate
```

**v0.7 approach:**
```yaml
templates:
  common_interest_rate:
    cost_interest_rate:
      data: 0.1
      index: monetary
      dims: costs
techs:
  supply_tech:
    base_tech: supply
    template: common_interest_rate
```

### Transmission Links in Techs

The top-level `links` key no longer exists. Transmission technologies are defined in `techs` with `link_from`/`link_to` keys.

**v0.6 approach:**
```yaml
techs:
  ac_transmission:
    essentials:
      parent: transmission
links:
  X1,X2:
    techs:
      ac_transmission:
```

**v0.7 approach:**
```yaml
techs:
  x1_to_x2_ac_transmission:
    link_from: X1
    link_to: X2
    base_tech: transmission
```

### Parameter Renaming

Improvements to parameter clarity:
- `energy`/`carrier` → `flow` (e.g., `energy_cap_max` → `flow_cap_max`)
- `prod`/`con` → `out`/`in` (e.g., `carrier_prod` → `flow_out`)
- `resource` → `source_use` or `sink_use`
- `resource_area` → `area_use`
- `om_prod`/`om_con` → `cost_flow_out`/`cost_flow_in`
- `exists` → `active`

### Force Resource Changes

The binary `force_resource` trigger is replaced with parameters `source_use_equals` and `sink_use_equals` to directly specify required resource flows.

### Units and Purchase Consolidation

`units` and `purchased` are merged into a single `purchased_units` decision variable.

### Investment Cost Split

`cost_investment` is split into:
- `cost_investment_annualised` - Annualized capital investment
- `cost_operation_fixed` - Fixed operational and maintenance costs

### Explicit MILP and Storage Activation

Mixed-integer features now require explicit activation:
- Set `config.build.extra_math: ["milp"]` to enable integer variables
- Set `cap_method: integer` on specific technologies
- Use `include_storage: true` to add storage buffers to non-storage technologies

**v0.6 approach:**
```yaml
techs:
  supply_tech:
    constraints:
      units_max: 4
```

**v0.7 approach:**
```yaml
config:
  build:
    extra_math: ["milp"]
techs:
  supply_tech:
    units_max: 4
    cap_method: integer
```

### Data Structure Changes

Concatenated `loc::tech` and `loc::tech::carrier` sets are removed. Components are now indexed separately over `nodes`, `techs`, and `carriers`.

**v0.6 access:**
```python
model.inputs.energy_cap_max.loc[{"loc_techs": "X::pv"}]
```

**v0.7 access:**
```python
model.inputs.flow_cap_max.loc[{"nodes": "X", "techs": "pv"}]
```

### Node Coordinates

Geographic coordinates use direct `latitude`/`longitude` keys instead of nested `coordinates`.

**v0.6 approach:**
```yaml
nodes:
  X1:
    coordinates:
      lat: 1
      lon: 2
```

**v0.7 approach:**
```yaml
nodes:
  X1:
    latitude: 1
    longitude: 2
```

### Distance Units Default

Distance calculations now default to kilometres instead of metres. Set `config.init.distance_unit: m` to use metres.

### Operate Mode Inputs

In operate mode, directly specify capacity parameters (e.g., `flow_cap: 1`) instead of `_max` constraints. Operating windows and horizons use Pandas time frequencies (e.g., `12H`) rather than integer timesteps.

### Per-Technology Cyclic Storage

Cyclic storage moves from global configuration to per-technology parameters:

**v0.6 approach:**
```yaml
run:
  cyclic_storage: true
```

**v0.7 approach:**
```yaml
techs:
  storage_tech:
    base_tech: storage
    cyclic_storage: true
```

## Removals

### Equals Constraints

Parameters like `energy_cap_equals` are removed. Set `_min` and `_max` to the same value to achieve fixed parameters.

### Cartesian Coordinates

X/Y coordinates no longer supported; use `latitude`/`longitude` instead.

### Comma-Separated Node Definitions

Defining multiple nodes via comma separation (e.g., `node1,node2,node3:`) is no longer allowed. Use `templates` for reuse.

### Supply Plus and Conversion Plus

These base classes are removed:
- Replace `supply_plus` with `supply` + `include_storage: true`
- Replace `conversion_plus` with `conversion` using lists for `carrier_in`/`carrier_out`

### Carrier Key

The `carrier` alias is removed; explicitly use `carrier_in` and `carrier_out`.

### Carrier Tiers and Ratios

Complex carrier tier and ratio functionality is removed. Implement equivalent behavior through custom math or flow efficiency indexing.

### Group Constraints

Group constraints removed; reimplemented as user-defined math snippets.

### Configuration Removals

- `timeseries_data_path` - Use paths relative to `model.yaml` or absolute paths
- `run.relax_constraint` - Use user-defined math instead
- `model.file_allowed` - All parameters can be time-indexed
- `model.random_seed` and time clustering options

### Plotting

Visualization functionality moved to [Calligraph](https://calligraph.readthedocs.io/), a separate tool.

### Time Clustering

Simplified to date-matching only. Use external tools for advanced clustering.

## Additions

### Storage Buffers for All Base Classes

Any technology base class can now include `include_storage: true` for intertemporal storage capability.

### Multiple and Mixed Carriers

All base classes support multiple carriers and different inflow/outflow carriers, enabling complex technology definitions without `conversion_plus`.

### Templates for Nodes

The new `templates` feature replaces comma-separated node grouping.

**Achieving repeated node configuration:**
```yaml
templates:
  standard_tech_list:
    techs:
      battery:
      demand_electricity:
      ccgt:
nodes:
  region1:
    template: standard_tech_list
  region2:
    template: standard_tech_list
```

### Separate Inflow/Outflow Efficiencies

Parameters `flow_in_eff` and `flow_out_eff` enable different charge/discharge or input/output efficiencies.

### Carrier-Indexed Capacities and Efficiencies

Capacity and efficiency parameters are indexed over carriers, allowing per-carrier constraints:

```yaml
techs:
  dual_fuel_plant:
    base_tech: conversion
    carrier_in: [coal, biofuel]
    carrier_out: electricity
    flow_cap_max:
      data: [100, 80]
      index: [coal, biofuel]
      dims: carriers
```

### Data Definitions Outside Nodes/Techs

Top-level `data_definitions` key allows defining parameters independent of nodes and technologies.

### Arbitrary Dimension Indexing

Parameters can be indexed over custom dimensions for advanced modeling.

### Non-Timeseries Tabular Data

Expanded `data_tables` support for loading any tabular data, not just timeseries.

### YAML-Based Math Syntax

Complete math formulation redesign using readable YAML, enabling custom math and piecewise constraints.
