# Built-in Base Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/base/

## Overview

This documentation covers the complete mathematical formulation for a Calliope model's base math, which is always applied but can be overridden with additional or custom mathematics.

## Guide to Math Documentation Structure

Math components are organized hierarchically:
- Initial conditions determine if a component applies
- Sub-conditions (indented `if` statements) specify expressions for dimension iterations
- **Bold terms** represent decision variables
- *Italic terms* represent parameters
- Parameters defined over time can be single values or timeseries loaded from files

## Objective Function

### Min Cost Optimisation (Active)

The objective minimizes total system costs. When multiple cost classes exist (e.g., monetary plus emissions), a weighted sum is minimized using the `objective_cost_weights` parameter.

Key features:
- Includes investment and operational costs
- Optionally penalizes unmet demand and unused supply when feasibility is ensured
- Scalable to multi-objective optimization

## Primary Constraint Categories

### Balance Constraints

**Conversion Balance**: Links outflow to consumption for conversion technologies

**Supply Balance**: For technologies without storage, fixes outflow to source consumption efficiency

**Supply with Storage**: Allows temporal offset between source consumption and outflow

**Demand Balance**: Sets demand technology requirements based on area use, capacity, or absolute values

**Storage Balance**: Tracks stored carrier across timesteps, accounting for losses and initial conditions

**Transmission Balance**: Ensures carrier flow conservation across links

### Capacity Constraints

**Flow In/Out Limits**: Bounds technology inflow and outflow based on installed capacity

**Storage Capacity**: Constrains stored quantity relative to storage capacity

**Source Capacity**: Limits supply resource consumption

**Ramping Constraints**: Restricts rate of change in technology output between timesteps

### System-level Constraints

**System Balance**: Ensures total carrier production equals consumption at each node/timestep

**Area Use Limits**: Caps total land area technologies can occupy

**Systemwide Capacity Bounds**: Sets technology-wide capacity limits across all nodes

## Decision Variables

Core decision variables include:

- `flow_cap`: Technology flow capacity
- `flow_in/flow_out`: Carrier flows by timestep
- `source_cap`: Supply resource capacity
- `source_use`: Resource consumption
- `storage_cap`: Energy storage capacity
- `storage`: Stored quantity by timestep
- `area_use`: Land area utilization
- `unmet_demand/unused_supply`: Feasibility slack variables (when enabled)

## Key Parameters

Essential parameters controlling model behavior:

- `cost_*`: Various cost components (investment, operational, annualized)
- `*_cap_max/min`: Capacity bounds
- `*_eff`: Efficiency factors
- `storage_loss`: Temporal storage decay
- `flow_ramping`: Rate-of-change limits
- `timestep_resolution`: Duration weights
- `lifetime`: Asset operational lifespan

## Cost Calculation

Total system cost comprises:

1. **Annualized Investment Costs**: Lifetime costs discounted to annual equivalent using interest rates and depreciation
2. **Fixed Operation Costs**: Time-invariant operational expenses
3. **Variable Operation Costs**: Timestep-dependent expenses

The annuity calculation accounts for modeling period length relative to one year and applies compound interest formulas when interest rates exceed zero.
