# Mixed Integer Linear Programming (MILP) Example Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/milp/

## Overview

This example extends the Urban scale model by introducing binary and integer variables through an override applied in `scenarios.yaml`. The model demonstrates MILP functionality in Calliope, though convergence is slower with integer/binary variables. Commercial solvers like Gurobi or CPLEX are recommended for production use.

## Model Configuration

The MILP override includes:
- Model name: "Urban-scale example model with MILP"
- Extra math modules: "milp" and "additional_math"
- Solver option: mipgap of 0.05

## Key Components

### Purchased Units

The CHP technology uses a unit-based capacity approach rather than continuous capacity ranges:

- **Cap method**: integer
- **Integer dispatch**: enabled
- **Purchased units max**: 4 units
- **Flow capacity per unit**: 300 (electricity)
- **Minimum output when operating**: 20% of maximum capacity

This discrete approach allows the solver to select how many CHP units to purchase, with each unit having identical capacity. The minimum operating capacity constraint only applies when output is non-zero, differing from standard LP models.

### Purchase Cost

The boiler incorporates both unit-based and continuous capacity decisions:

- **Cap method**: integer
- **Purchased units max**: 1 (creating a binary variable)
- **Fixed purchase cost**: 2,000 (monetary units)
- **Variable cost**: 35 per capacity unit

A binary variable indicates whether to invest in the boiler. This fixed purchase cost captures infrastructure expenses independent of installed capacity.

### Asynchronous Flow Control

Heat distribution pipes employ a constraint preventing simultaneous energy flow in opposite directions:

"The `async_flow_switch` binary variable ensures this phenomenon is avoided" by restricting a link to either transmission or reception per timestep, eliminating unphysical heat dumping.
