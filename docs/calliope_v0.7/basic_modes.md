# Modes

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/modes/

Calliope supports different optimization methods to solve energy system problems. Three primary approaches are available:

## Overview

The framework applies math in layers:

- **Base math** is always active and forms the foundation
- **Mode math** enables special cases like operate and SPORES modes
- **Extra math** provides optional additional formulations

## Base Mode

This is the default approach using perfect foresight optimization. The system determines optimal technology capacities and their dispatch across all time periods simultaneously, minimizing total investment and operating costs combined.

Investment costs are annualized using a loan repayment formula that accounts for interest rates and technology lifespans:

$$\frac{\text{investment cost} \times \text{interest rate} \times (1 + \text{interest rate})^{\text{loan period}}}{(1 + \text{interest rate})^{\text{loan period}} - 1}$$

This converts capital expenses into equivalent annual costs comparable to fuel and maintenance expenses.

## Operate Mode

This dispatch-focused approach fixes all technology capacities and optimizes operations only. It employs receding horizon control—making decisions with limited foresight rather than perfect information about the future.

**Key requirements:**
- All capacities must be specified as input parameters
- Two configuration settings needed:

```
config.build:
  operate_horizon: 48h
  operate_window: 24h
```

The horizon defines the planning window for each optimization iteration, while the window specifies which portion of results to retain. The horizon must equal or exceed the window size.

## SPORES Mode

"Spatially-explicit Practically Optimal REsultS" generates multiple alternative system configurations within a cost tolerance of the optimal solution. This enables exploration of the solution space while prioritizing spatial diversity.

**Configuration example:**

```
config.init.mode: spores
config.solve.spores.number: 10
parameters.spores_slack: 0.1
```

This generates 10 alternatives within 10% of optimal cost.

**Advanced features:**
- Target specific technologies via tracking parameters
- Save intermediate results per run to prevent total loss if interrupted
- Skip the baseline run if results already exist
- Continue from existing SPORES sets to extend exploration
