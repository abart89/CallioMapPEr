# Scenarios and Overrides

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/scenarios/

## Overview

Calliope allows you to define variations of your model without creating separate files. This is accomplished through two complementary mechanisms:

- **Overrides**: YAML blocks that expand or replace parts of the base model configuration
- **Scenarios**: Named combinations of multiple overrides

## Structure

Both overrides and scenarios are defined at the top level of your model configuration file. Here's the basic structure:

```yaml
scenarios:
  high_cost_2005: ["high_cost", "year2005"]
  high_cost_2006: ["high_cost", "year2006"]

overrides:
  high_cost:
    techs.onshore_wind.cost_flow_cap.data: 2000
  year2005:
    init.subset.timesteps: ['2005-01-01', '2005-12-31']
  year2006:
    init.subset.timesteps: ['2006-01-01', '2006-12-31']

config:
  ...
```

## How They Work

Each override receives a name and can specify any model configuration settings. In the example above:
- The `high_cost` override modifies technology costs
- The `year2005` and `year2006` overrides specify different time periods

Scenarios bundle overrides together. The `high_cost_2005` scenario applies both the `high_cost` and `year2005` overrides simultaneously.

## Usage

Overrides can be applied individually or as scenarios when running your model. This approach enables sensitivity analyses and comparative studies without file duplication.

## Important Note

"Overrides are executed _after_ `imports:` but _before_ `templates:`," meaning you can override template values but not imported files.
