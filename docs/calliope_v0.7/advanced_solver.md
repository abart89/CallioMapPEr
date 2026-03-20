# Specifying Custom Solver Options

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/solver/

This documentation covers how to configure custom options for optimization solvers in Calliope.

## Gurobi

To set custom Gurobi parameters, reference the [Gurobi manual](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html) for available options. Use parameter names exactly as documented.

**Example configuration:**

```yaml
config.solve:
  solver: gurobi
  solver_options:
    Threads: 3
    NumericFocus: 2
```

## CPLEX

For CPLEX, consult the [parameter list](https://www.ibm.com/docs/en/icos/22.1.1?topic=cplex-list-parameters) and use "Interactive" parameter names, converting spaces to underscores.

**Example configuration:**

```yaml
config.solve:
  solver: cplex
  solver_options:
    mipgap: 0.01
    mip_polishafter_absmipgap: 0.1
    emphasis_mip: 1
    mip_cuts: 2
    mip_cuts_cliques: 3
```
