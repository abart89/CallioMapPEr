# Defining Your Own Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/

## Overview

Calliope version 0.7 and later allows users to define custom mathematical formulations for optimization problems using YAML files. The same syntax used for pre-defined math can extend the framework with new constraints, decision variables, and objectives.

## Core Concepts

Mathematical components are organized under named keys containing:

- **Sets**: Dimensions over which components generate (technologies, nodes, timesteps, etc.)
- **Conditions**: Criteria determining when components build in specific models
- **Expressions**: The mathematical formulations themselves

## Component Types

The framework supports four primary math component categories:

1. **Decision variables** — values the optimization model determines
2. **Global expressions** — combinations of variables and parameters using mathematical operations
3. **Constraints** — bounds and limitations on decision variables using other elements
4. **Objectives** — expressions to minimize or maximize

## Important Constraints

**Linear Framework**: Calliope operates as a linear modeling system. Users should be aware that custom math may inadvertently create nonlinear problems, though solvers typically provide error messages when this occurs.

**Documentation Structure**: The project recommends reviewing math components first, then syntax details, followed by customization approaches and examples.

## Additional Resources

The documentation includes comprehensive coverage of math components, formulation syntax, helper functions, customization procedures, and a gallery of user-defined math examples.
