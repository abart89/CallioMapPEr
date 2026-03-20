# User-Defined Math Example: Flow Share Across All Timesteps

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/share_all_timesteps/

## Description

This feature allows you to set the share of a technology's (or group of technologies') total outflow/inflow met by other technologies to specific values.

**Key capabilities:**
- Single technologies require explicit definition (e.g., `flow_in[techs=demand_power]`)
- Groups of technologies can be defined as lists or consolidated by shared attributes (e.g., `flow_out[carriers=power]`)
- Parameters can be defined per technology and optionally per node

**New technology-level parameters:**
- `demand_share_equals`
- `supply_share_equals`

**Helper functions used:**
- `sum` (expression)

## YAML Definition

The implementation includes three main sections:

**Parameters:**
- `demand_share_equals`: Share of a technology's total inflow met by other technologies (default: 1, unitless)
- `supply_share_equals`: Share of a node's total outflows met by other technologies (default: 1, unitless)

**Lookups:**
- `demand_share_tech`: Defines which demand technology receives a specified inflow share (string type)
- `supply_share_carrier`: Specifies the carrier for tracking outflow shares (string type)

**Constraints:**
Two main constraints enforce the shares:
1. `demand_share_equals_per_tech`: Relates total outflow of certain technologies to a share of demand inflow
2. `supply_share_equals_per_tech`: Sets total outflow of technologies producing a carrier to a share of total carrier outflow in each node
