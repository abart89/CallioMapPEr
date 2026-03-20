# Basic Concepts

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/concepts/

## What Calliope Does

Calliope is an energy system modelling framework built on mathematical optimization. It addresses typical energy sector challenges including capacity expansion planning, economic dispatch, and power market modelling. The framework emphasizes maintainability through text-based model definitions that remain human-readable even at scale.

## Mathematical Modelling Terminology

The framework borrows terminology from operations research:

- **Parameters**: Fixed numerical input data supplied by users
- **Variables**: Numerical values determined during model solving
- **Constraints**: Mathematical functions defining bounds on variable values
- **Objective function**: Mathematical function that is maximized or minimized to determine variable values

## Core Calliope Concepts

A Calliope model represents real-world systems through interconnected components:

- **Carriers**: Commodities tracked through flows (electricity, heat, hydrogen, water, CO2)
- **Technologies**: Components that supply, consume, convert, store or transmit carriers
- **Nodes**: Geographic groupings containing technology collections
- **Sources and sinks**: Entry and exit points for carrier flows
- **Timesteps**: Discrete time periods for temporal representation

The framework represents space as discrete nodes and time as discrete timesteps, enabling models of varying complexity.

## Building Blocks

### YAML Configuration

Models use YAML text files with `key: value` entries. Two important extensions:

- **Nesting**: Hierarchical organization using dot notation (e.g., `config.solve.solver: glpk`)
- **Importing**: Spreading models across multiple files via the `import` key

### Mathematical Structure

Calliope applies math in strict priority order:

1. **Base math**: Default capacity planning with perfect foresight
2. **Mode math**: Special processing for operate mode or SPORES
3. **Extra math**: Additional customizations (e.g., inter-cluster storage)

### Model Components

Four key definition areas:

- `techs`: Technology specifications
- `nodes`: Node definitions
- `data_definitions`: Data parameter descriptions
- `data_tables`: Tabular data in CSV format

### Configuration and Customization

The `config` top-level key specifies operational settings and math customizations through modes and user-defined mathematics.

### Templates and Scenarios
udm
- **Templates**: Reusable model components reducing repetition
- **Overrides and scenarios**: Alternative configurations for model initialization

## Model Data Structure

Model outputs contain two categories:

**Inputs:**
- Parameters: Numeric fixed values
- Lookups: Non-numeric parameters (boolean switches, etc.)

**Results:**
- Variables: Mathematical unknowns (e.g., `flow_cap`)
- Global expressions: Computed combinations (e.g., `cost`)
- Post-processed results: Calculated after solving (e.g., `capacity_factor`)
