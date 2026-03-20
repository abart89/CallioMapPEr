# Choosing an Optimisation Problem Backend

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/backend_choice/

## Overview

When loading a model in Calliope, no solver backend exists initially—only the input dataset. The backend is generated when calling `build()` on the model. By default, this invokes [Pyomo](https://www.pyomo.org/) to construct the model and route it to the solver specified in `config.solve.solver`.

## Pyomo Backend

Pyomo offers **mutable input parameters**, enabling you to update parameter values without rebuilding Pyomo objects. However, it is relatively memory and time-intensive for constructing optimization problems.

## Gurobi Backend

For larger models requiring commercial solvers, Calliope provides direct integration with the Gurobi solver Python API. Testing demonstrates this approach reduces both peak memory consumption and solution time compared to using Pyomo with Gurobi.

### Setup Requirements

To use the Gurobi backend with an existing license:

1. Install the Gurobi Python library: `mamba install gurobi::gurobi`
2. Specify the backend in YAML configuration:
   ```yaml
   config.build.backend: gurobi
   ```
   Or at build time in Python:
   ```python
   model.build(backend="gurobi")
   ```

### Limitations

You can still interface with your optimization problem, but certain methods will raise exceptions when the Gurobi API doesn't support functionality available in Pyomo.
