# Urban Scale Example Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/urban_scale/

## Overview

This example demonstrates a district-level energy system with three buildings (nodes) connected through transmission networks. The system includes electricity supply, gas supply, solar generation, heat production, and demand management across multiple locations.

## Model Architecture

The model comprises:
- **3 demand nodes** (X1, X2, X3) representing buildings
- **1 branching node** (N1) for heat network distribution
- **5 technologies** for energy generation and conversion
- **Transmission links** for electricity and heat distribution

## Key Components

### Configuration Structure

The model separates configuration from definition. The main `model.yaml` file references:
- Technology definitions (`techs.yaml`)
- Location specifications (`locations.yaml`)
- Scenario definitions (`scenarios.yaml`)

Configuration specifies solver options, timestep subsets, and math extensions rather than system data.

### Data Loading

Time-series data loads from CSV files rather than YAML:
- **Demand profiles**: hourly electricity and heat requirements per building
- **PV resource**: solar availability with area-based scaling
- **Export pricing**: time-varying grid electricity values

The system defines data table mappings specifying rows (timesteps) and columns (nodes/technologies/carriers).

### Technology Portfolio

**Supply Technologies:**
- Grid electricity import (unlimited availability, €0.10/kWh)
- Natural gas import (unlimited availability, €0.025/kWh)
- Solar PV (area-constrained, 85% inverter efficiency, export capability)

**Conversion Technologies:**
- Natural gas boiler (85% efficiency)
- Combined Heat and Power unit (dual output with heat-to-power ratio coupling)

**Demand Technologies:**
- Electricity demand
- Heat demand

**Transmission:**
- Power lines (98% efficiency, €0.01/kW-distance)
- District heat pipes (97.5% per-unit efficiency, €0.30/kW-distance)

### Custom Mathematics

The CHP technology requires user-defined constraints to enforce simultaneous heat and electricity production with a fixed 0.8:1 ratio, since standard Calliope logic treats multiple outputs as alternatives rather than complementary products.

## Node-Specific Features

**X1** (Central building):
- Hosts CHP, PV, grid connection
- Primary heat supply source
- Grid interface point

**X2 & X3** (Secondary buildings):
- PV only (no centralized generation)
- Varied feed-in tariff structures
- Connected via heat network through N1

**N1** (Distribution hub):
- No technologies installed
- Enables efficient heat network branching

## Economic Modeling

The system captures:
- Capital costs for capacity installation
- Operational costs (fuel purchasing, maintenance)
- Revenue streams from electricity export
- Location-specific tariff variations
- Distance-dependent transmission costs

Interest rates and feasibility penalties configure the optimization objective function.
