# Math Syntax

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/syntax/

## Overview

The math syntax enables formulation of math components by populating n-dimensional matrices with mathematical expressions. The approach combines three key elements: defining dimensions with `foreach`, subsetting data with `where` strings, and populating subsets with equation expressions.

## foreach Lists

Define the dimensions (sets) over which a math component is indexed. Available dimensions include: `nodes`, `techs`, `carriers`, `costs`, `timesteps`, and optionally `datesteps` (with time clustering). Custom dimensions can be added to the model dataset.

Example: `foreach: [nodes, techs]` builds the component across all nodes and technologies.

## where Strings

Subset data or model configurations using conditional statements combined with logical operators (`and`, `or`, `not`). Supported statement types:

**1. Parameter existence checks:**
- Basic: `flow_out_eff` (checks if defined)
- With aggregation: `any(resource, over=nodes)` (checks if any node has a value)

**2. Value comparisons:**
- Operators: `>`, `<`, `==`, `<=`, `>=`
- Examples: `config.mode==operate`, `flow_eff<0.5`
- Helper functions available: `get_val_at_index(dim=timesteps, idx=0)`

**3. Technology base checks:**
- Example: `base_tech==storage`

**4. Set subsetting:**
- Example: `defined(techs=[tech1, tech2], within=nodes, how=any)`

Statements can be grouped with parentheses and combined with logical operators (case-insensitive).

## Expression Strings

Combine input parameters, decision variables, global expressions, and numeric values using:

**For global expressions/objectives:** `+`, `-`, `*`, `/`, `**` (following standard operator precedence)

**For constraints:** Add comparison operators `<=`, `>=`, `==`

### Slicing Data

Subset components without fully specifying all sets. Square bracket syntax: `flow_out[carriers=electricity, nodes=[A, B]]`. The system automatically matches relevant array elements during application.

## Equations

Define one or more equation expressions with optional `where` strings to condition application:

```
equations:
  - where: flow_eff > 0
    expression: flow_out / flow_out_eff == flow_in
  - where: flow_eff == 0
    expression: flow_out == 0
```

Single equations don't require a `where` statement. Equation-level `where` strings append to top-level `where` conditions.

## Sub-expressions

Reference frequently-used expression segments using the `$` prefix:

```
equations:
  - expression: flow_out <= $adjusted_flow_in
sub_expressions:
  adjusted_flow_in:
    - where: base_tech==storage
      expression: flow_in * flow_eff
```

## Slices

Create dynamic data references within slice definitions using `$` identifiers:

```
equations:
  - expression: sum(flow_out[techs=$tech_ref]) <= flow_in
slices:
  tech_ref:
    - expression: lookup_techs
```

## default

Specify default values for variables and global expressions to fill empty array elements and prevent `NaN` values in the optimization problem.
