# User-Defined Math Example: Demand Share Per Timestep as Decision Variable

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/demand_share_per_timestep_decision/

## Description

This feature enables models to determine how demand for a carrier is distributed among specified technologies, with each technology maintaining an identical share across all timesteps. The implementation can be extended to iterate over nodes and carriers as needed.

Key characteristics:

- The share is calculated relative to the flow from a designated demand technology (or group thereof)
- A `relaxation` parameter provides flexibility around specified values, improving model solvability
- New indexed parameters include `relaxation` and `demand_share_limit`
- Helper functions: `sum` (expression) and `select_from_lookup_arrays` (expression)

## YAML Definition

### Parameters

**demand_share_relaxation**: Controls deviation tolerance from the demand share limit. A value of 0.01 allows ±1% flexibility. Default is 0 (no relaxation).

**demand_share_limit**: Specifies the total demand share that technologies must meet. Default is 1 (full demand). Must be between 0 and 1.

### Lookups

**decide_demand_share**: Links generating technologies to consuming (demand) technologies, establishing which generator supplies what demand.

**demand_share_carrier**: Identifies the carrier being tracked between generating and consuming technologies.

### Variables

**demand_share_per_timestep_decision**: Represents the relative demand share a technology meets per node, with bounds from 0 to infinity.

### Constraints

Two primary constraints enforce consistent shares across timesteps:

1. **Minimum constraint**: Ensures technology outflow meets or exceeds its decided share
2. **Maximum constraint**: Caps technology outflow at its decided share

An optional **sum constraint** ensures all decision shares aggregate to a specified demand share limit (e.g., 50% of electricity demand).
