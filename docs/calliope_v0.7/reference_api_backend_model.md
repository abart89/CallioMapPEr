# API Reference: Backend Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/backend_model/

## Overview

The `BackendModel` class is an abstract base class that serves as the interface between Calliope's mathematical formulation and external optimization solvers. It manages the construction and manipulation of optimization problems.

## Class Definition

```python
calliope.backend.backend_model.BackendModel(inputs, math, build_config, instance)
```

**Base Classes:** `BackendModelGenerator`, `Generic[T]`

### Parameters

| Name | Type | Description |
|------|------|-------------|
| `inputs` | `xr.Dataset` | Calliope model data |
| `math` | `AttrDict` | Calliope math specifications |
| `build_config` | `Build` | Build configuration options |
| `instance` | `T` | Interface model instance |

## Key Properties

- **config:** Build configuration settings
- **inputs:** Processed input dataset with lookups and parameters
- **math:** Mathematical formulation definitions
- **objective:** Active optimization objective name
- **variables:** Array of decision variables
- **constraints:** Array of constraint equations
- **parameters:** Array of input parameters
- **global_expressions:** Computed expressions combining variables/parameters
- **objectives:** Defined objective functions
- **lookups:** Input lookup tables
- **piecewise_constraints:** Piecewise linear constraint definitions
- **shadow_prices:** Dual values from constraint relaxation
- **has_integer_or_binary_variables:** Boolean flag indicating MILP problem

## Core Methods

### Building the Optimization Problem

- **add_optimisation_components():** Parse math and build full optimization problem
- **add_variable():** Create decision variable with bounds
- **add_parameter():** Add input parameter with default values
- **add_constraint():** Define constraint equations
- **add_global_expression():** Create arithmetic expressions
- **add_objective():** Specify objective function
- **add_lookup():** Register lookup array
- **add_piecewise_constraint():** Build piecewise linear constraints

### Accessing Components

- **get_variable():** Extract decision variable array
- **get_parameter():** Retrieve parameter values
- **get_constraint():** Access constraint definitions with optional evaluation
- **get_global_expression():** Fetch computed expressions
- **get_objective():** Retrieve objective specifications
- **get_piecewise_constraint():** Access piecewise constraint objects
- **get_variable_bounds():** Extract upper/lower bounds

### Model Manipulation

- **update_input():** Modify parameter or lookup values
- **update_variable_bounds():** Change variable min/max bounds
- **fix_variable():** Convert variable to parameter with current value
- **unfix_variable():** Restore fixed variable to decision status
- **set_objective():** Switch active optimization objective
- **delete_component():** Remove component from model

### Utilities

- **load_results():** Extract optimal solution values after solving
- **to_lp():** Export problem in LP format for debugging
- **verbose_strings():** Enhance string representations with index coordinates
- **log():** Log messages with formatted component information

## Component Validation

The `valid_component_names` property returns all recognized component identifiers in the model, supporting validation during expression parsing.
