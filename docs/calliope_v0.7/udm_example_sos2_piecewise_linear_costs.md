# User-Defined Math Example: SOS2 Piecewise Linear Costs (Economies of Scale)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/sos2_piecewise_linear_costs/

## Description

This feature implements a piecewise cost function that decreases the marginal investment expenses as technology capacity increases. It models "economies of scale," where deploying greater quantities of a technology reduces the per-unit investment cost.

A comprehensive example is available in the dedicated tutorial on defining piecewise linear constraints.

### New Indexed Parameters

- `piecewise_cost_investment_x` (establishes the `breakpoints` set)
- `piecewise_cost_investment_y` (establishes the `breakpoints` set)

## YAML Definition

The implementation uses three main sections:

**Dimensions:**
- `breakpoints`: Integer-type dimension representing SOS2 piecewise breakpoints

**Parameters:**
- `piecewise_cost_investment_x`: Flow capacity values at each breakpoint
- `piecewise_cost_investment_y`: Investment cost values at each breakpoint

**Variables:**
- `piecewise_cost_investment`: A non-decreasing investment cost variable applied across nodes, technologies, carriers, and cost types

**Piecewise Constraints:**
- `sos2_piecewise_costs`: Implements special ordered sets of type 2 (SOS2) to enforce the piecewise cost curve, linking flow capacity (`flow_cap`) to investment costs

The constraint applies where both x and y parameter values exist across breakpoints.
