# User-Defined Math Example: Piecewise Linear Efficiency

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/piecewise_linear_efficiency/

## Description

This documentation describes how to implement a piecewise technology efficiency function that increases efficiency as outflow rises. The approach requires enabling the `operating_units` decision variable for relevant technologies. Without this variable, technologies would have non-zero inflow requirements even at zero capacity.

The implementation introduces two new indexed parameters:

- `flow_eff_piecewise_slopes` — defines a new `pieces` set
- `flow_eff_piecewise_intercept` — defines a new `pieces` set

## YAML Definition

The configuration includes:

**Dimensions:**
- `pieces` (integer type, with iterator `piece`)

**Parameters:**
- `flow_eff_piecewise_slopes` — "The gradient of each of the piecewise limiting line defining the convex, non-linear efficiency curve"
- `flow_eff_piecewise_intercept` — "The y-axis intercept of each of the piecewise limiting line defining the convex, non-linear efficiency curve"

**Constraints:**

A `piecewise_efficiency` constraint applies across nodes, technologies, timesteps, and pieces where the relevant parameters and capacity are available. The constraint enforces that:

```
sum(flow_in, over=carriers) >=
flow_eff_piecewise_slopes * sum(flow_out, over=carriers)
+ flow_eff_piecewise_intercept * sum(available_flow_cap, over=carriers)
```

This limits inflow requirements to monotonically increase with outflow, ensuring the model follows the efficiency curve traced by superimposed pieces.
