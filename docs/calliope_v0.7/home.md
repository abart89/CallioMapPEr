# Calliope: Energy System Modelling Made Simple

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/

Calliope represents "an energy system modelling framework based on mathematical optimisation" that enables organizations to plan capacity expansion and conduct economic dispatch modeling across scales from urban districts to continents.

## Overview

The framework emphasizes spatial and temporal flexibility with a distinct separation between code and model data. Users construct models using YAML and CSV text files defining technologies, locations, and resource availability. Calliope processes these specifications, formulates optimization problems, and delivers results via xarray Datasets convertible to Pandas structures.

## Key Capabilities

The system features:
- Open-source distribution under Apache 2.0 licensing
- YAML-based model specification
- Multi-location and multi-timestep resolution capabilities
- HPC cluster compatibility
- Python-based architecture incorporating Pyomo, xarray, and Pandas libraries
- Interactive result exploration via Calligraph companion tool

## Getting Started

Newcomers should begin with the foundational concepts section, followed by tutorial materials. The documentation serves as primary reference content for users already familiar with fundamentals.

## Acknowledgments and Licensing

Project contributors are detailed on the official website. Distribution occurs under Apache 2.0 licensing since 2013. Calliope has received academic publication recognition in the Journal of Open Source Software.
