# API Reference: Example Models

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/example_models/

## Overview

The `calliope.examples` module provides built-in example models that can be loaded directly into a Python session for learning and testing purposes.

## Available Example Models

### national_scale()
"Returns the built-in national-scale example model." Loads from `national_scale/model.yaml`.

### urban_scale()
"Returns the built-in urban-scale example model." Loads from `urban_scale/model.yaml`.

### milp()
A variant of the urban-scale model with mixed-integer linear programming constraints enabled.

### operate()
The urban-scale example configured to run in operate mode.

### operate_milp()
Combines operate mode with MILP constraints on the urban-scale model.

### time_clustering()
The national-scale example with time clustering applied.

### time_resampling()
The national-scale example with time resampling applied.

## Usage Pattern

All functions accept flexible arguments and keyword arguments (`*args, **kwargs`), allowing customization when loading models. Functions typically call `read_yaml()` to load model configuration files from the examples directory.
