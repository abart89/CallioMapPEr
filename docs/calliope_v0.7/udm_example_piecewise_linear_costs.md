# User-Defined Math Example: Piecewise Linear Costs

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/piecewise_linear_costs/

## Description

This feature allows you to implement a piecewise cost function that progressively increases investment costs as technology rated capacity grows. A critical requirement is that the binary purchase decision variable must be enabled for relevant technologies. Without this variable, the technology will incur costs regardless of whether capacity is actually deployed.

The implementation introduces two new indexed parameters:
- `cost_flow_cap_piecewise_slopes` (creates the `pieces` set)
- `cost_flow_cap_piecewise_intercept` (creates the `pieces` set)

## YAML Definition

The configuration includes:

**Dimensions:**
- A `pieces` dimension with integer data type and `piece` iterator

**Parameters:**
- `cost_flow_cap_piecewise_slopes`: "The gradient of each of the piecewise limiting line defining the convex, non-linear cost curve"
- `cost_flow_cap_piecewise_intercept`: "The y-axis intercept of each of the piecewise limiting line defining the convex, non-linear cost curve"

**Variables:**
- `piecewise_cost_investment`: A cost variable indexed across nodes, technologies, and cost types, with bounds from 0 to infinity

**Constraints:**
The constraint `piecewise_costs` enforces that investment costs increase monotonically across pieces by relating the investment cost variable to technology flow capacity and purchased units.

**Integration:**
The new cost component integrates into the model's `cost_investment` global expression, combining with existing investment cost sources.
