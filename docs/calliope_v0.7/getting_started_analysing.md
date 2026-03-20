# Analysing a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/analysing/

## Overview

Calliope is designed to make working with inputs and results straightforward. Results can be exported as NetCDF or CSV files for processing in your preferred software.

## Easiest Approach: Using Calligraph

The simplest method for analyzing results is [Calligraph](https://calligraph.readthedocs.io/), a dedicated visualization tool for Calliope outputs.

After running your model and saving results to NetCDF format:

```bash
$ calligraph results.nc
```

This launches an interactive browser-based interface for exploring your data.

## Accessing Model Data and Results in Python

A successfully solved model contains two primary xarray Datasets:

- **`model.inputs`**: Input data (e.g., renewable resource capacity factors)
- **`model.results`**: Output data including dispatch decisions, installed capacities, and postprocessed metrics like LCOE and capacity factor

Data is indexed across Calliope dimensions such as technologies, nodes, and timesteps. Not all dimension combinations contain values—missing data appears as NaN. You can filter filled data points using Python:

```python
model.inputs.flow_cap.to_series().dropna()
```

## Reading Previously Saved Solutions

Load a previously saved model from a NetCDF file:

```python
solved_model = calliope.read_netcdf('my_saved_model.nc')
```

Access input and results data as shown above using `solved_model.inputs` and `solved_model.results`.

## Visualization Options

- **Calligraph**: Interactive browser interface
- **Python**: Custom visualizations within Jupyter notebooks
- **Other tools**: Export to CSV or NetCDF for external processing
