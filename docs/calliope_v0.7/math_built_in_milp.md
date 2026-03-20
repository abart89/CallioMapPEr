# Mixed Integer Linear Programming Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/milp/

## Overview

This documentation covers the **mixed integer linear programming (MILP) mathematical formulation** that applies on top of Calliope's base math when referenced as `"milp"` in `config.init.extra_math`.

## Objective Function

### Minimum Cost Optimisation

The primary objective seeks to minimize total system costs, encompassing both installation and operational expenses. When multiple cost classes exist (such as monetary and CO2 emissions), a weighted sum minimizes the total.

**Key components:**
- Sums costs across all nodes and technologies
- Applies objective cost weights to each cost class
- When `config.ensure_feasibility==true`, adds penalty terms for unmet demand and unused supply using a "big M" multiplier

## Main Constraint Categories

### Area and Capacity Constraints

- **area_use_capacity_per_loc**: Bounds total technology area at each node
- **area_use_minimum**: Sets lower bounds on area use
- **area_use_per_flow_capacity**: Fixes relationship between flow capacity and land occupation

### Flow Capacity Constraints

The framework implements multiple capacity-related constraints:

- **flow_capacity_maximum_purchase_milp**: Limits capacity for technologies with integer unit purchasing
- **flow_capacity_minimum**: Establishes lower bounds on capacity
- **flow_capacity_per_storage_capacity**: Links storage flow rates to capacity ratios
- **flow_capacity_systemwide**: Applies capacity bounds across entire system

### Flow Bounds by Operating Mode

- **flow_in_max** and **flow_in_max_milp**: Consumption limits
- **flow_out_max** and **flow_out_max_milp**: Production limits
- **flow_out_min** and **flow_out_min_milp**: Minimum output requirements

### Storage and Balance Equations

- **balance_storage**: Tracks stored carrier across timesteps accounting for losses and flows
- **balance_supply_no_storage**: Couples source consumption directly to output
- **balance_supply_with_storage**: Allows temporal offset between source use and delivery
- **balance_demand**: Constrains sink demands based on availability parameters
- **balance_conversion**: Enforces input-output relationships for conversion technologies

### Operational Flexibility

- **ramping_up** and **ramping_down**: Limit rate of change in technology operation between timesteps
- **async_flow_in_milp** and **async_flow_out_milp**: Control simultaneous inflow/outflow capability

### Unit Commitment Features

- **unit_commitment_milp**: Enforces discrete unit operation
- **operating_units**: Binary variables tracking active units
- **purchased_units**: Integer capacity purchasing

## Decision Variables

The optimization determines values for:

- **flow_cap**: Technology capacity investments
- **flow_in/flow_out**: Carrier flows per timestep
- **storage**: Stored energy levels
- **operating_units**: Active unit counts
- **purchased_units**: Total unit acquisitions
- **source_use**: Resource consumption rates

## Key Parameters

Essential input parameters include:

- **flow_cap_max/min**: Capacity bounds
- **flow_out_min_relative**: Minimum operating points
- **flow_ramping**: Rate-of-change limits
- **storage_loss**: Temporal decay rates
- **cost_***: Investment and operational expenses
- **timestep_resolution**: Duration of each modeling period

## Implementation Notes

The mathematical formulation uses conditional logic throughout: each constraint activates only when specific parameters exist or conditions hold. This enables flexible model configuration without unnecessary complexity in infeasible scenarios.
