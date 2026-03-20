# Math Components

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/components/

This page documents the foundational elements needed to construct optimization problems in Calliope.

## Decision Variables

Decision variables represent unknown quantities that an optimization algorithm can adjust to meet objectives while respecting constraints. Examples include technology capacity and per-timestep carrier flows.

Key characteristics:

- **Unique naming**: Required identifier for each variable
- **Metadata**: Optional title, description, and unit annotations
- **Indexing**: Uses `foreach` lists and `where` conditions to apply variables across model dimensions
- **Domain specification**: Can be real (default), integer, or binary
- **Bounds**: Require minimum and maximum limits via either numeric values or parameter references
- **Activation control**: Can be disabled with `active: false`
- **Default values**: Help prevent undefined results in calculations

Example structure includes properties like `storage_cap` with bounds referencing input parameters.

## Global Expressions

These reusable mathematical combinations of variables and parameters appear in multiple constraints or objectives without cluttering the formulation.

Defining characteristics:

- **Reusability**: Accessed across multiple constraints and objectives
- **Result tracking**: Expressions return numeric values directly in optimization results
- **Metadata support**: Optional title, description, and unit information
- **Equation definitions**: Use expressions without comparison operators
- **Sub-expressions**: Optional nested expressions for complex calculations
- **Ordering control**: The `order` attribute allows prioritization when new expressions reference existing ones

An example tracks total costs by combining investment and operational expenses.

## Constraints

Constraints embed real-world system limitations and relationships between decision variables. They enforce physical laws and operational bounds.

Essential features:

- **Unique identification**: Named for reference
- **Dimensional indexing**: Applied via `foreach` and `where` statements
- **Equation requirements**: Must include comparison operators (==, <=, >=)
- **Sub-expressions and slices**: Optional components for complex logic
- **Deactivation capability**: Controlled via `active: false`

## Piecewise Constraints

These represent non-linear relationships using special ordered sets (SOS2) and binary variables for linear approximation.

Structure elements:

- **X and Y expressions**: Link two variables along a curve
- **Breakpoint values**: Parameters defining piecewise segments
- **Special syntax**: Unique format compared to other components

**Caution**: Piecewise constraints increase solver difficulty; convex functions may use simpler constraint approaches instead.

## Objectives

An objective function directs optimization toward minimization or maximization of a target quantity.

Properties:

- **Single activation requirement**: Only one objective can be active per model
- **Optional filtering**: `where` strings control activation without `foreach` indexing
- **Expression format**: No comparison operators in expressions
- **Sub-expressions**: Supported for complex formulations
- **Sense specification**: Explicitly declares minimization or maximization

The default objective minimizes total system costs across all technologies.
