# User-Defined Math Example: Flow Share Per Timestep

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/share_per_timestep/

## Description

This feature allows you to set the per-timestep share of a technology's (or group of technologies) inflow or outflow to be met by other technologies at specific values.

**Key characteristics:**

- For single technologies, explicit definition is required (e.g., `flow_in[techs=demand_power]`)
- For technology groups, you can either list them explicitly or consolidate them by shared attributes (e.g., `flow_out[carriers=power]`)
- Parameters support both single values and time-varying data (e.g., from CSV files)

**New technology-level parameters:**

- `demand_share_per_timestep_equals`
- `supply_share_per_timestep_equals`

**Helper functions used:**

- `sum` (expression)

## YAML Definition

The implementation includes two main constraints:

**Constraint 1: Demand Share**
Sets per-timestep outflow of certain technologies producing a specific carrier to equal a share of demand inflow:

```
flow_out (summed over carriers) ==
flow_in[demand_tech] (summed over carriers) * demand_share_per_timestep_equals
```

**Constraint 2: Supply Share**
Sets per-timestep outflow of technologies producing a carrier to equal a share of total per-timestep outflow for that carrier in each node:

```
flow_out[carrier] ==
sum(flow_out[carrier], over all techs) * supply_share_per_timestep_equals
```

Both constraints iterate across nodes, technologies, and timesteps, activated where respective parameters are defined.
