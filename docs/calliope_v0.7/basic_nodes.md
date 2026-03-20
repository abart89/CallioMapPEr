# Nodes

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/nodes/

## Understanding Node-Level Parameters

The `techs` parameter is mandatory for nodes, though it can be an empty dictionary (`techs: {}`). This approach works when a node serves as a junction point for transmission technologies, which are defined separately rather than within a node's `techs` specification.

Note that the parameter definition formats documented for technologies also apply to node-level parameters.

## Arbitrary Per-Node Data

Nodes support custom parameter data that becomes accessible in optimization problems, indexed along the nodes dimension. Parameters can also be populated using data definition syntax to span additional dimensions beyond nodes.

Example configuration:

```yaml
nodes:
  region1:
    custom_node_parameter: 100
    custom_node_flow_out_max:
      data: [1000, 2000]
      index: [electricity, gas]
      dims: carriers
```

In this example, `custom_node_flow_out_max` at `region1` could support custom mathematical constraints limiting total outflow of electricity and gas carriers at that location.

### Deactivating Nodes

Within overrides, you can remove nodes from the model entirely using `active: false`. This eliminates the node from the resulting dataset completely. The same mechanism works for deactivating specific technologies at a node.

**Important:** When deactivating nodes, any transmission technologies linking to that node are automatically deactivated as well.
