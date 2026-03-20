# User-Defined Math Example: Annual Energy Balance

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/annual_energy_balance/

## Description

This feature allows you to "limit or set the total (e.g. annual) outflow of a technology to a specified absolute value."

### New Parameters

The implementation introduces technology-level parameters:
- `annual_flow_max`
- `annual_source_max`

Additionally, indexed parameters and lookups are available:
- `annual_flow_max` (indexed)
- `flow_max_group` (indexed lookup)

### Helper Functions

The constraint definitions utilize the `sum` expression helper function.

## YAML Definition

The implementation defines three main parameters:

| Parameter | Description | Default | Unit |
|-----------|-------------|---------|------|
| `annual_flow_max` | Annual maximum outflow | .inf | energy |
| `annual_source_max` | Annual maximum source use | .inf | energy |
| `annual_sink_max` | Annual maximum sink use | .inf | energy |

### Constraints

Five constraints are defined:

1. **Per technology and node**: "Limit total technology annual energy production at each possible deployment site" using `sum(flow_out, over=[carriers, timesteps]) <= annual_flow_max`

2. **Global per technology**: Constrains production across all deployment sites

3. **Global multi-technology**: Limits combined technology production using sliced references

4. **Total source availability**: Restricts flow into the system from particular sources via `sum(source_use, over=[nodes, timesteps]) <= annual_source_max`

5. **Total sink availability**: Controls demand sink flows excluding pinned values
