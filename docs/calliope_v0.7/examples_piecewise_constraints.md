# Defining Piecewise Linear Constraints (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/piecewise_constraints/

This tutorial page covers how to define piecewise linear constraints in Calliope.

## Related Topics in User-Defined Math

Calliope supports piecewise linear formulations through two distinct approaches:

- **Piecewise linear costs** — implementing non-linear cost functions that become more or less expensive with scale
- **Piecewise linear efficiency** — modeling efficiency curves with multiple segments
- **SOS2 piecewise linear costs** — using Special Ordered Sets of type 2 for economies-of-scale cost curves

## Overview

Piecewise linear constraints are used to approximate non-linear relationships within the linear optimization framework. Calliope provides both constraint-based approaches (for upward-sloping convex curves) and SOS2 piecewise constraints (for more general non-convex curves).

See the User-Defined Math examples for complete YAML definitions:
- [Piecewise linear costs](udm_example_piecewise_linear_costs.md) — increasing marginal costs with capacity
- [Piecewise linear efficiency](udm_example_piecewise_linear_efficiency.md) — improving efficiency with output
- [SOS2 piecewise linear costs](udm_example_sos2_piecewise_linear_costs.md) — decreasing marginal costs (economies of scale)

**Note:** The page includes a downloadable Jupyter notebook demonstrating practical implementation of piecewise constraint techniques.
