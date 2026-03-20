# Download and Installation

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/installation/

## Requirements

Calliope operates on Linux, macOS, and Windows. Four components are necessary:

1. **Python 3.10 to 3.12**
2. **Python packages** including Pyomo, Pandas, and Xarray
3. **An optimization solver** (tested with CBC, GLPK, and Gurobi)
4. **Calliope software**

## Recommended Installation Method

The simplest approach uses the `mamba` package manager to install all components simultaneously.

First, obtain `mamba` by downloading [Miniforge for your operating system](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html). Alternatively, the Anaconda distribution offers a graphical interface (substitute `conda` for `mamba` in commands below).

Run this command to create a Calliope environment with the CBC solver:

```
mamba create -n calliope -c conda-forge conda-forge/label/calliope_dev::calliope
```

Activate the environment with:

```
mamba activate calliope
```

> "Although possible, we do not recommend installing Calliope directly via pip"—non-Python binaries necessary for stability won't be included.

## Choosing a Solver

### CBC

[CBC](https://github.com/coin-or/Cbc) is the recommended free, open-source option. Install with:

```
mamba install conda-forge::coin-or-cbc
```

### GLPK

[GLPK](https://anaconda.org/conda-forge/glpk) is free but may struggle with larger problems. Install via:

```
mamba install conda-forge::glpk
```

It supports shadow price extraction, unlike CBC.

### Gurobi

[Gurobi](https://www.gurobi.com/) is commercial, faster for large problems, and requires a license. Academic licenses are available. Install with:

```
mamba install gurobi::gurobi
```

Then obtain a license and activate it using the `grbgetkey` command.

### CPLEX

[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio) is IBM's commercial solver offering academic licenses.
