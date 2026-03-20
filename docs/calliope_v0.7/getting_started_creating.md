# Creating a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/creating/

## What a Basic Model Needs

A minimal Calliope model requires:

- Basic model configuration
- One carrier
- One `supply` and one `demand` tech
- One node
- One timestep

The documentation provides a complete minimal example in a single `model.yaml` file, featuring a power supply technology with 100 MW maximum capacity and a power demand technology requiring 50 MWh at a single timestep.

## Model Directory Layout

A typical Calliope model directory structure organizes files logically:

```
example_model/
├── data_tables/
│   ├── electricity_demand.csv
│   └── solar_resource.csv
├── model_definition/
│   ├── nodes.yaml
│   └── techs.yaml
├── model.yaml
└── scenarios.yaml
```

## Model Configuration

Configuration specifies initialization, building, and solving parameters. It includes:

- **init**: Model name, timestep subsets, operating modes
- **build**: Backend selection (default: Pyomo)
- **solve**: Solver choice (e.g., CBC, GLPK)

## Techs (Technologies)

Technologies require a `base_tech` designation:

- `supply`: Produces carriers from sources
- `demand`: Consumes carriers
- `storage`: Stores carriers
- `transmission`: Moves carriers between nodes
- `conversion`: Transforms between carriers

"A model must contain at least one `supply` and `demand` tech, whereas the other techs are optional."

## Nodes

Nodes represent spatial locations where technologies operate. Node-level specifications include:

- `latitude` and `longitude` (for visualization)
- `available_area` (for area constraints)
- `techs` listing available technologies

Node-specific parameters override technology-level defaults.

## Transmission Techs

Transmission technologies link nodes using `link_from` and `link_to` keys, enabling carrier flows between locations.

## Data Tables

CSV files provide tabular data via the `data_tables` key, reducing YAML file size for large datasets. Configuration specifies file location, row/column treatments, and dimension additions.

## Data Definitions

The `data_definitions` key allows parameter specification with custom dimensions, particularly useful for advanced functionality like user-defined mathematics.

## Overrides and Scenarios

Overrides modify YAML definitions, while scenarios combine multiple overrides for exploring different model configurations and cost scenarios.

## Creating Models from Templates

The `calliope new` command generates starter models from built-in templates:

```bash
$ calliope new my_new_model
```

Default template is the national-scale example; use `--template=urban_scale` for alternatives.
