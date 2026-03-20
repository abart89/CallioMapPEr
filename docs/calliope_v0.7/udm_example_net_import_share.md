# User-Defined Math Example: Net Import Share

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/net_import_share/

## Description

This constraint limits carrier imports within nodes or across all nodes as a proportion of total carrier flows. It treats transmission technology outflows as imports, assuming technologies like `test_transmission_elec` and `test_transmission_heat` are defined.

**New indexed parameters:**
- `net_import_share`

**Helper functions utilized:**
- `defined` (where clause)
- `sum` (expression)
- `get_transmission_techs` (expression)

## YAML Definition

### Parameters

The `net_import_share` parameter specifies "the share of carrier out/inflows that transmission import/export at a node can account for," with a default value of 1 and unitless measurement.

### Constraints

**net_import_share_max**: Applied per node and timestep, this constraint restricts electricity imports to a specified share of all electricity outflows minus inflows.

**net_annual_import_share_max**: Similar to the above but aggregated annually across all timesteps per node.

**net_annual_import_share_max_node_group**: Extends the constraint across multiple nodes, allowing heat import limitations for a defined node subset. Uses slices to specify the node group `[a, c]` and carrier type (heat).

### Global Expressions

**flow_out_transmission_techs**: A pre-filtered transmission technology outflow list, where base_tech equals transmission, measured in energy units across nodes, technologies, carriers, and timesteps.
