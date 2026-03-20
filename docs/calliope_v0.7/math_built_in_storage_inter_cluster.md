# Inter-cluster Storage Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/storage_inter_cluster/

## Overview

This page documents **extra mathematical formulations** for inter-cluster storage that applies on top of the base mathematical model. These formulations are only activated when `"storage_inter_cluster"` is referenced in the `config.init.extra_math` list.

## Objective Function

### Minimum Cost Optimization

The system minimizes total installation and operational costs. When multiple cost classes exist (e.g., monetary and emissions), a weighted sum is minimized using the `objective_cost_weights` parameter.

The objective includes penalties for unmet demand and unused supply when feasibility is enforced via configuration settings.

## Key Constraints

### Storage Balance Across Days

**balance_storage_inter** establishes relationships between consecutive days by fixing how a storage technology's available carrier changes based on:
- Previous day's representative storage fluctuations
- Excess stored carrier accumulated across all preceding days
- Storage loss rates

### Intra-Day Storage Bounds

Two constraints limit storage within individual clustered days:

- **storage_intra_max**: Upper bounds on stored carrier within a day
- **storage_intra_min**: Lower bounds on stored carrier within a day

### Multi-Day Storage Bounds

- **storage_inter_max**: Combines inter-day storage with intra-day maximums to ensure total capacity limits
- **storage_inter_min**: Combines inter-day storage losses with intra-day minimums to maintain reserve levels

## Decision Variables

Key variables include:

- `storage_inter_cluster`: Stored carrier available across multiple days
- `storage_intra_cluster_max`: Maximum storage within a clustered day
- `storage_intra_cluster_min`: Minimum storage within a clustered day
- `storage`: Instantaneous storage level at each timestep

## Important Parameters

- `storage_loss`: Hourly decay rate (exponentiated to 24 for daily calculations)
- `storage_initial`: Initial storage fraction of capacity
- `cyclic_storage`: Enables wrap-around from final to first period
- `lookup_datestep_cluster`: Maps days to representative clusters
- `lookup_datestep_last_cluster_timestep`: Identifies final timestep of each day
