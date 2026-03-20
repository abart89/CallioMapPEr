# Technologies

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/techs/

## Overview

The `techs` section defines all technologies in a model. Each technology is characterized by its `base_tech`, which establishes its role in the optimization model.

## Base Technology Types

Five base technology categories exist:

- **supply**: Draws from a source to produce a carrier
- **demand**: Consumes a carrier for an external sink
- **storage**: Stores a carrier
- **transmission**: Transmits a carrier between nodes
- **conversion**: Converts between different carriers

## Example: Combined Cycle Gas Turbine

A sample `ccgt` technology demonstrates key parameters:

```yaml
ccgt:
  name: 'Combined cycle gas turbine'
  color: '#FDC97D'
  base_tech: supply
  carrier_out: power
  source_use_max: .inf
  flow_out_eff: 0.5
  flow_cap_max: 40000
  lifetime: 25
```

Technologies must specify a base type, output/input carriers as appropriate, and various constraints and costs for the optimization problem.

## Template-Based Configuration

Technologies can inherit definitions using the `template` key, enabling configuration sharing across multiple technologies or nodes without duplicating specifications.

## Transmission Technologies

Since transmission technologies span two nodes, they're defined differently than node-based technologies:

```yaml
techs:
  ac_transmission:
    base_tech: transmission
    link_from: region1
    link_to: region2
    flow_cap_max: 100
```

By default, flow directions are bidirectional unless `one_way: true` is set.

## Required Parameters by Base Tech

- **supply**: `base_tech`, `carrier_out`
- **demand**: `base_tech`, `carrier_in`
- **storage**: `base_tech`, `carrier_in`, `carrier_out`
- **transmission**: `base_tech`, carriers, `link_to`, `link_from`
- **conversion**: `base_tech`, `carrier_in`, `carrier_out`

## Custom Parameters

Users can add custom parameters beyond pre-defined ones, provided they don't start with underscores or numbers. Parameters beginning with `cost_` must follow the data_definitions format to specify cost classes.

## Deactivation

Technologies can be deactivated in overrides by setting `active: false`, removing them entirely from the model.
