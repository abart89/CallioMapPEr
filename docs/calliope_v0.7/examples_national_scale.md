# National Scale Example Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/national_scale/

## Overview

This example demonstrates a basic energy system with two power supply technologies, demand at multiple nodes, battery storage capabilities, and transmission infrastructure linking locations.

The system comprises:
- **region1** and **region2** as primary demand centers
- **region1_1, region1_2, region1_3** as potential generation sites
- AC transmission connecting region1 to region2
- Local transmission from CSP sites to region1

## Model Configuration

The configuration file establishes how Calliope interprets the model definition:

```yaml
config:
  init:
    name: National-scale example model
    calliope_version: 0.7.0
    subset:
      timesteps: ["2005-01-01", "2005-01-05"]
    broadcast_input_data: true
    mode: base
  build:
    ensure_feasibility: true
  solve:
    solver: cbc
    zero_threshold: 1e-10
```

Key settings include timestep subsetting, feasibility constraints, and solver specifications.

## Data Loading via Tables

The model references external CSV files for time-varying and cost parameters:

```yaml
data_tables:
  time_varying_parameters:
    data: data_tables/time_varying_params.csv
    rows: timesteps
    columns: [comment, nodes, techs, parameters]
    drop: comment
  cost_parameters:
    data: data_tables/costs.csv
    rows: techs
    columns: [parameters, comment]
    drop: comment
    add_dims:
      costs: monetary
```

Cost data associates technologies with economic parameters like flow capacity costs and variable operational expenses.

## Supply Technologies

**CCGT (Combined-cycle gas turbine)** represents a conventional supply option:
- Infinite source availability
- 50% conversion efficiency
- Maximum capacity: 40 MW system-wide, 30 MW at region1
- 25-year lifetime
- $750/kW capital cost

**CSP (Concentrating solar power)** is a complex renewable supply technology featuring:
- Time-series dependent source (per unit area)
- Integrated thermal storage with 614 MWh maximum
- 40% primary conversion efficiency
- 90% parasitic efficiency (internal losses)
- Multiple cost components for storage, collection area, and conversion capacity
- Deployed across three regional sites

## Storage Technology

**Battery storage** at region2 provides temporal flexibility:
- 1 MW charge/discharge capacity
- 4:1 flow-to-storage capacity ratio
- Round-trip efficiency: ~90% (95% charging × 95% discharging)
- Zero self-discharge losses assumed

## Demand and Transmission

**Power demand** technology receives time-series data from CSV files, with demand patterns specified per location.

**Transmission technologies** include:
- AC transmission between region1 and region2 with 85% efficiency
- Local transmission from CSP sites with zero loss and cost

## Template-Based Definition

Templates reduce repetition in model definitions. The "free_transmission" template specifies local power transmission characteristics inherited by multiple region connections:

```yaml
templates:
  free_transmission:
    name: "Local power transmission"
    carrier_in: power
    carrier_out: power
    base_tech: transmission
```

## Node Configuration

Nodes define geographic locations and their available technologies:

- **region1**: Demand, CCGT generation (30 MW maximum)
- **region2**: Demand, battery storage
- **region1_1, region1_2, region1_3**: CSP generation sites with specified coordinates

Geospatial coordinates (latitude/longitude) enable transmission distance calculations for cost estimation.
