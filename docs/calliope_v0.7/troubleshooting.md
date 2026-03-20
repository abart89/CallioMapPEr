# Troubleshooting

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/troubleshooting/

## General Strategies

### Building a Smaller Model

Use `config.init.subset` to specify dimension subsets for debugging. This significantly speeds up model solutions. The documentation recommends subsetting timesteps, typically the largest dimension, using a date range format like `config.init.subset.timesteps: ['2005-01-01', '2005-01-31']`.

### Retaining Logs and Temporary Files

Enable `config.solve.save_logs` to save solver logs and temporary files. These can reveal infeasibility insights. The LP file shows exact mathematical formulations sent to the solver. Call `model.backend.verbose_strings()` after building but before solving to expand component names for easier inspection.

### Analysing Without Solving

Build your optimization problem with `model.build()`, then inspect components in `model.backend`. Access constraints like: `model.backend.get_constraint("flow_out_max")`. Use `as_backend_objs=False` for readable output showing constraint bounds and body text.

#### Save an LP File

Generate an LP file representing the full mathematical model:

```bash
calliope run my_model.yaml --save_lp=my_saved_model.lp
```

In Python:
```python
model.build()
model.backend.to_lp('my_saved_model.lp')
```

## Improving Solution Times

### Number of Variables

Reduce dimensions—nodes, techs, timesteps, carriers, or costs—to decrease decision variables. Merging nearby locations additionally removes inter-location technology links. Calliope supports time resampling or custom time clustering for significant improvements.

### Complex Technologies

Calliope operates primarily as an LP framework. Certain constraints trigger binary or integer variables, creating MILP models. These solve slower but enable additional functionality like purchasing costs and per-timestep "on/off" logic.

### Model Mode

The `operate` mode splits models into temporal chunks, improving solution times for large problems at the cost of fixed capacities. One approach: use heavily clustered `base` mode to determine capacities, then run `operate` mode for higher-resolution operation strategies.

## Solver Influence on Speed

Commercial solvers (Gurobi, CPLEX) substantially outperform open-source options (GLPK, CBC). Academic researchers can obtain free licenses. Test results on extended example models show:

| Solver | National Scale | Urban Scale |
|--------|----------------|-------------|
| GLPK | 4:35:40 | >5hrs |
| CBC | 0:04:45 | 0:52:13 |
| Gurobi (1 thread) | 0:02:08 | 0:03:21 |
| CPLEX (1 thread) | 0:04:55 | 0:05:56 |

## Understanding Infeasibility

### Gurobi Solver

Set `config.solve.solver_options: {DualReductions: 0}` to distinguish infeasibility from unboundedness. Generate an Irreducible Inconsistent Subsystem:

```bash
gurobi_cl ResultFile=result.ilp my_saved_model.lp
```

For numerical instability, try `config.solve.solver_options: {Presolve: 0}` to prevent large numeric ranges from creating instability.

### CPLEX Solver

Two approaches:

1. Save solver logs (`config.solve.save_logs`) and check the `.cplex.log` file for infeasible constraints.

2. Save an LP file and open it in CPLEX interactive mode (`cplex` command). Use `FeasOpt` to relax constraints or `tools conflict` to identify conflicting constraints.

Try `config.solve.solver_options: {preprocessing_presolve: 0}` or use `read_scale: 1` for aggressive scaling.

## Rerunning Models

Modify `model.inputs` and rebuild with `model.build(force=True)`. For large problems needing small parameter changes, use `model.backend.update_parameter()` and `model.backend.update_variable_bounds()`, then call `model.solve(force=True)` to avoid full rebuilding.

## Debugging Model Errors

### Inspecting Debug Logs

Enable debug logging with `calliope.set_log_verbosity("debug")`. Access specific loggers:
- `logging.getLogger("calliope.preprocess")` for YAML/CSV processing
- `logging.getLogger("calliope.backend")` for math syntax processing

### Validating Math Syntax

Run `model.validate_math_strings(my_math_dict)` for quick syntax validation before building backend models.

### Inspecting Private Data Structures

Access internal Calliope objects:
- `model._def` for the loaded pydantic model definition
- `model.backend._dataset` for built backend objects in array format
