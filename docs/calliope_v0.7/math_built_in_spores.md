# SPORES Mode Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/spores/

## Overview

This page documents the **Spores mode math** formulation in Calliope, which applies on top of the base mathematical framework when `config.build.mode` is set to `"spores"`. The SPORES methodology enables finding multiple diverse, near-optimal system designs.

## Key Components

### Objectives

**min_cost_optimisation (active)**: Minimizes total system installation and operation costs. When multiple cost classes exist, a weighted sum is minimized. Includes penalty terms for unmet demand when feasibility is enabled.

**min_spores (inactive)**: Applied after the baseline optimization, this objective minimizes diversity scores assigned to each technology's flow capacity at each node, helping identify alternative solutions.

### Main Constraints

The formulation includes constraints for:

- **Energy balance**: System-wide carrier production equals consumption at each node and timestep
- **Storage dynamics**: Fixed relationships between stored carrier quantities across timesteps
- **Flow limits**: Upper and lower bounds on technology inflows and outflows
- **Capacity relationships**: Constraints linking flow capacity to storage capacity and area use
- **Supply/demand**: Fixed or bounded source consumption and demand fulfillment
- **Transmission**: Relationships between bidirectional flow capacities
- **Ramping**: Limits on rate-of-change in technology output

### Cost Calculation

Total cost combines:
- Annualized investment costs
- Fixed operational costs
- Variable operational costs (summed across all timesteps)

### SPORES-Specific Feature

The **total_system_cost_max** constraint limits system cost in SPORES iterations: "total cost ≤ baseline_cost × (1 + slack_parameter)", allowing near-optimal solutions within a user-defined tolerance.

## Documentation Structure

Each constraint and objective includes:
- Mathematical formulation
- Relevant decision variables and parameters
- YAML configuration snippets
- Conditional logic for different technology types

The documentation emphasizes that parameters can be defined as single values or time-varying series loaded from data files.
