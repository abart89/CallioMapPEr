# Model Math Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/math_schema/

## Overview

The Model Math Schema defines the mathematical programming components available for optimization in Calliope. It supports partial definitions that can be layered on top of one another (for example, combining 'base' and 'operate' math).

## Main Components

### Dimensions
Defines the model's dimension dictionary with named dimensions. Each dimension can specify:
- **title**: Long name for visualization
- **description**: Verbose explanation
- **active**: Boolean to enable/disable during build
- **dtype**: Data type (string, datetime, date, float, integer)
- **ordered**: Whether item order is meaningful (e.g., chronological)
- **iterator**: Name for LaTeX math formulation

### Parameters
Configures input parameters with properties including:
- **default**: Fallback value if not specified in data
- **resample_method**: Aggregation approach (mean, sum, first)
- **unit**: Parameter units (kW, m, kg, etc.)

### Lookups
Defines lookup arrays with support for:
- **dtype**: Data type specification
- **one_of**: Constraint values to specific items
- **pivot_values_to_dim**: Converts lookup values into a new dimension with boolean indexing

### Variables
Specifies decision variables for the optimization problem with:
- **foreach**: Dimensions over which the variable is built
- **where**: Conditional existence criteria
- **domain**: Real (continuous) or integer values
- **bounds**: Upper and lower limits (min/max)

### Global Expressions
Reusable combinations of parameters and variables used across constraints, objectives, and other expressions. Supports:
- **equations**: Mathematical relationships
- **sub_expressions**: Component terms
- **slices**: Set items or helper function calls

### Constraints
Mathematical restrictions on the optimization problem, structured similarly to global expressions with equations, sub-expressions, and slices.

### Piecewise Constraints
Specialized constraints linking x-axis and y-axis decision variables at specified breakpoints using:
- **x_expression** and **y_expression**: Variable references
- **x_values** and **y_values**: Parameter data indexed over breakpoints

### Objectives
The optimization target function (only one active per solve). Must specify:
- **sense**: Minimize or maximize

### Checks
Input data validation with:
- **where**: Condition to evaluate
- **message**: Error/warning text
- **errors**: Response type (raise or warn)
