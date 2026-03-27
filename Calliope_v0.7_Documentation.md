# Calliope v0.7 Documentation

## Getting Started

### Calliope: Energy System Modelling Made Simple

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/

Calliope represents "an energy system modelling framework based on mathematical optimisation" that enables organizations to plan capacity expansion and conduct economic dispatch modeling across scales from urban districts to continents.

#### Overview

The framework emphasizes spatial and temporal flexibility with a distinct separation between code and model data. Users construct models using YAML and CSV text files defining technologies, locations, and resource availability. Calliope processes these specifications, formulates optimization problems, and delivers results via xarray Datasets convertible to Pandas structures.

#### Key Capabilities

The system features:
- Open-source distribution under Apache 2.0 licensing
- YAML-based model specification
- Multi-location and multi-timestep resolution capabilities
- HPC cluster compatibility
- Python-based architecture incorporating Pyomo, xarray, and Pandas libraries
- Interactive result exploration via Calligraph companion tool

#### Getting Started

Newcomers should begin with the foundational concepts section, followed by tutorial materials. The documentation serves as primary reference content for users already familiar with fundamentals.

#### Acknowledgments and Licensing

Project contributors are detailed on the official website. Distribution occurs under Apache 2.0 licensing since 2013. Calliope has received academic publication recognition in the Journal of Open Source Software.


---

### Download and Installation

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/installation/

#### Requirements

Calliope operates on Linux, macOS, and Windows. Four components are necessary:

1. **Python 3.10 to 3.12**
2. **Python packages** including Pyomo, Pandas, and Xarray
3. **An optimization solver** (tested with CBC, GLPK, and Gurobi)
4. **Calliope software**

#### Recommended Installation Method

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

#### Choosing a Solver

##### CBC

[CBC](https://github.com/coin-or/Cbc) is the recommended free, open-source option. Install with:

```
mamba install conda-forge::coin-or-cbc
```

##### GLPK

[GLPK](https://anaconda.org/conda-forge/glpk) is free but may struggle with larger problems. Install via:

```
mamba install conda-forge::glpk
```

It supports shadow price extraction, unlike CBC.

##### Gurobi

[Gurobi](https://www.gurobi.com/) is commercial, faster for large problems, and requires a license. Academic licenses are available. Install with:

```
mamba install gurobi::gurobi
```

Then obtain a license and activate it using the `grbgetkey` command.

##### CPLEX

[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio) is IBM's commercial solver offering academic licenses.


---

### Basic Concepts

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/concepts/

#### What Calliope Does

Calliope is an energy system modelling framework built on mathematical optimization. It addresses typical energy sector challenges including capacity expansion planning, economic dispatch, and power market modelling. The framework emphasizes maintainability through text-based model definitions that remain human-readable even at scale.

#### Mathematical Modelling Terminology

The framework borrows terminology from operations research:

- **Parameters**: Fixed numerical input data supplied by users
- **Variables**: Numerical values determined during model solving
- **Constraints**: Mathematical functions defining bounds on variable values
- **Objective function**: Mathematical function that is maximized or minimized to determine variable values

#### Core Calliope Concepts

A Calliope model represents real-world systems through interconnected components:

- **Carriers**: Commodities tracked through flows (electricity, heat, hydrogen, water, CO2)
- **Technologies**: Components that supply, consume, convert, store or transmit carriers
- **Nodes**: Geographic groupings containing technology collections
- **Sources and sinks**: Entry and exit points for carrier flows
- **Timesteps**: Discrete time periods for temporal representation

The framework represents space as discrete nodes and time as discrete timesteps, enabling models of varying complexity.

#### Building Blocks

##### YAML Configuration

Models use YAML text files with `key: value` entries. Two important extensions:

- **Nesting**: Hierarchical organization using dot notation (e.g., `config.solve.solver: glpk`)
- **Importing**: Spreading models across multiple files via the `import` key

##### Mathematical Structure

Calliope applies math in strict priority order:

1. **Base math**: Default capacity planning with perfect foresight
2. **Mode math**: Special processing for operate mode or SPORES
3. **Extra math**: Additional customizations (e.g., inter-cluster storage)

##### Model Components

Four key definition areas:

- `techs`: Technology specifications
- `nodes`: Node definitions
- `data_definitions`: Data parameter descriptions
- `data_tables`: Tabular data in CSV format

##### Configuration and Customization

The `config` top-level key specifies operational settings and math customizations through modes and user-defined mathematics.

##### Templates and Scenarios
udm
- **Templates**: Reusable model components reducing repetition
- **Overrides and scenarios**: Alternative configurations for model initialization

#### Model Data Structure

Model outputs contain two categories:

**Inputs:**
- Parameters: Numeric fixed values
- Lookups: Non-numeric parameters (boolean switches, etc.)

**Results:**
- Variables: Mathematical unknowns (e.g., `flow_cap`)
- Global expressions: Computed combinations (e.g., `cost`)
- Post-processed results: Calculated after solving (e.g., `capacity_factor`)


---

### Creating a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/creating/

#### What a Basic Model Needs

A minimal Calliope model requires:

- Basic model configuration
- One carrier
- One `supply` and one `demand` tech
- One node
- One timestep

The documentation provides a complete minimal example in a single `model.yaml` file, featuring a power supply technology with 100 MW maximum capacity and a power demand technology requiring 50 MWh at a single timestep.

#### Model Directory Layout

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

#### Model Configuration

Configuration specifies initialization, building, and solving parameters. It includes:

- **init**: Model name, timestep subsets, operating modes
- **build**: Backend selection (default: Pyomo)
- **solve**: Solver choice (e.g., CBC, GLPK)

#### Techs (Technologies)

Technologies require a `base_tech` designation:

- `supply`: Produces carriers from sources
- `demand`: Consumes carriers
- `storage`: Stores carriers
- `transmission`: Moves carriers between nodes
- `conversion`: Transforms between carriers

"A model must contain at least one `supply` and `demand` tech, whereas the other techs are optional."

#### Nodes

Nodes represent spatial locations where technologies operate. Node-level specifications include:

- `latitude` and `longitude` (for visualization)
- `available_area` (for area constraints)
- `techs` listing available technologies

Node-specific parameters override technology-level defaults.

#### Transmission Techs

Transmission technologies link nodes using `link_from` and `link_to` keys, enabling carrier flows between locations.

#### Data Tables

CSV files provide tabular data via the `data_tables` key, reducing YAML file size for large datasets. Configuration specifies file location, row/column treatments, and dimension additions.

#### Data Definitions

The `data_definitions` key allows parameter specification with custom dimensions, particularly useful for advanced functionality like user-defined mathematics.

#### Overrides and Scenarios

Overrides modify YAML definitions, while scenarios combine multiple overrides for exploring different model configurations and cost scenarios.

#### Creating Models from Templates

The `calliope new` command generates starter models from built-in templates:

```bash
$ calliope new my_new_model
```

Default template is the national-scale example; use `--template=urban_scale` for alternatives.


---

### Running a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/running/

Calliope offers three primary methods for executing models:

1. **Command-line interface** via `calliope run`
2. **Python API** for programmatic execution
3. **Script generation** using `calliope generate_runs` for batch processing on clusters

#### Command-Line Execution

The quickest approach involves the CLI tool. To run a model and export results:

```bash
$ calliope run model.yaml --save_netcdf=results.nc
```

Alternatively, save outputs as CSV files:

```bash
$ calliope run model.yaml --save_csv=results_directory
```

This generates individual CSV files per variable. Consult the command-line documentation for details on applying scenarios or overrides.

#### Optimizing Solution Speed

Large models require extended processing time. While remote execution on computing clusters is often practical, several strategies exist to accelerate solutions when immediate results are needed. The troubleshooting section provides comprehensive guidance on optimization techniques.

#### Troubleshooting Failed Runs

When issues arise, investigate in this priority order:

- **Model definition errors**: Calliope identifies common mistakes and provides diagnostic messages
- **Infeasible models**: Properly structured but unsolvable models trigger solver notifications after processing
- **Calliope bugs**: Rare crashes during model construction or result processing

The troubleshooting documentation contains detailed diagnostic assistance for all three scenarios.


---

### Analysing a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/getting_started/analysing/

#### Overview

Calliope is designed to make working with inputs and results straightforward. Results can be exported as NetCDF or CSV files for processing in your preferred software.

#### Easiest Approach: Using Calligraph

The simplest method for analyzing results is [Calligraph](https://calligraph.readthedocs.io/), a dedicated visualization tool for Calliope outputs.

After running your model and saving results to NetCDF format:

```bash
$ calligraph results.nc
```

This launches an interactive browser-based interface for exploring your data.

#### Accessing Model Data and Results in Python

A successfully solved model contains two primary xarray Datasets:

- **`model.inputs`**: Input data (e.g., renewable resource capacity factors)
- **`model.results`**: Output data including dispatch decisions, installed capacities, and postprocessed metrics like LCOE and capacity factor

Data is indexed across Calliope dimensions such as technologies, nodes, and timesteps. Not all dimension combinations contain values—missing data appears as NaN. You can filter filled data points using Python:

```python
model.inputs.flow_cap.to_series().dropna()
```

#### Reading Previously Saved Solutions

Load a previously saved model from a NetCDF file:

```python
solved_model = calliope.read_netcdf('my_saved_model.nc')
```

Access input and results data as shown above using `solved_model.inputs` and `solved_model.results`.

#### Visualization Options

- **Calligraph**: Interactive browser interface
- **Python**: Custom visualizations within Jupyter notebooks
- **Other tools**: Export to CSV or NetCDF for external processing


---

### Troubleshooting

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/troubleshooting/

#### General Strategies

##### Building a Smaller Model

Use `config.init.subset` to specify dimension subsets for debugging. This significantly speeds up model solutions. The documentation recommends subsetting timesteps, typically the largest dimension, using a date range format like `config.init.subset.timesteps: ['2005-01-01', '2005-01-31']`.

##### Retaining Logs and Temporary Files

Enable `config.solve.save_logs` to save solver logs and temporary files. These can reveal infeasibility insights. The LP file shows exact mathematical formulations sent to the solver. Call `model.backend.verbose_strings()` after building but before solving to expand component names for easier inspection.

##### Analysing Without Solving

Build your optimization problem with `model.build()`, then inspect components in `model.backend`. Access constraints like: `model.backend.get_constraint("flow_out_max")`. Use `as_backend_objs=False` for readable output showing constraint bounds and body text.

###### Save an LP File

Generate an LP file representing the full mathematical model:

```bash
calliope run my_model.yaml --save_lp=my_saved_model.lp
```

In Python:
```python
model.build()
model.backend.to_lp('my_saved_model.lp')
```

#### Improving Solution Times

##### Number of Variables

Reduce dimensions—nodes, techs, timesteps, carriers, or costs—to decrease decision variables. Merging nearby locations additionally removes inter-location technology links. Calliope supports time resampling or custom time clustering for significant improvements.

##### Complex Technologies

Calliope operates primarily as an LP framework. Certain constraints trigger binary or integer variables, creating MILP models. These solve slower but enable additional functionality like purchasing costs and per-timestep "on/off" logic.

##### Model Mode

The `operate` mode splits models into temporal chunks, improving solution times for large problems at the cost of fixed capacities. One approach: use heavily clustered `base` mode to determine capacities, then run `operate` mode for higher-resolution operation strategies.

#### Solver Influence on Speed

Commercial solvers (Gurobi, CPLEX) substantially outperform open-source options (GLPK, CBC). Academic researchers can obtain free licenses. Test results on extended example models show:

| Solver | National Scale | Urban Scale |
|--------|----------------|-------------|
| GLPK | 4:35:40 | >5hrs |
| CBC | 0:04:45 | 0:52:13 |
| Gurobi (1 thread) | 0:02:08 | 0:03:21 |
| CPLEX (1 thread) | 0:04:55 | 0:05:56 |

#### Understanding Infeasibility

##### Gurobi Solver

Set `config.solve.solver_options: {DualReductions: 0}` to distinguish infeasibility from unboundedness. Generate an Irreducible Inconsistent Subsystem:

```bash
gurobi_cl ResultFile=result.ilp my_saved_model.lp
```

For numerical instability, try `config.solve.solver_options: {Presolve: 0}` to prevent large numeric ranges from creating instability.

##### CPLEX Solver

Two approaches:

1. Save solver logs (`config.solve.save_logs`) and check the `.cplex.log` file for infeasible constraints.

2. Save an LP file and open it in CPLEX interactive mode (`cplex` command). Use `FeasOpt` to relax constraints or `tools conflict` to identify conflicting constraints.

Try `config.solve.solver_options: {preprocessing_presolve: 0}` or use `read_scale: 1` for aggressive scaling.

#### Rerunning Models

Modify `model.inputs` and rebuild with `model.build(force=True)`. For large problems needing small parameter changes, use `model.backend.update_parameter()` and `model.backend.update_variable_bounds()`, then call `model.solve(force=True)` to avoid full rebuilding.

#### Debugging Model Errors

##### Inspecting Debug Logs

Enable debug logging with `calliope.set_log_verbosity("debug")`. Access specific loggers:
- `logging.getLogger("calliope.preprocess")` for YAML/CSV processing
- `logging.getLogger("calliope.backend")` for math syntax processing

##### Validating Math Syntax

Run `model.validate_math_strings(my_math_dict)` for quick syntax validation before building backend models.

##### Inspecting Private Data Structures

Access internal Calliope objects:
- `model._def` for the loaded pydantic model definition
- `model.backend._dataset` for built backend objects in array format


---

## Building Blocks

### Model Configuration

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/config/

#### Overview

Calliope's configuration is organized into three stages:

- **`init`**: Used when initializing a model (`calliope.Model(...)`)
- **`build`**: Used when building the optimization problem (`calliope.Model.build(...)`)
- **`solve`**: Used when solving the problem (`calliope.Model.solve(...)`)

You can override configuration values at each stage using keyword arguments:

```python
### Override init config
model = calliope.Model("path/to/model.yaml", subset={"timesteps": ["2005-01", "2005-02"]})

### Override build config
model.build(ensure_feasibility=True)

### Override solve config
model.solve(save_logs="path/to/logs/dir")
```

While no configuration options are strictly required, you'll typically want to set `init.name`, `init.calliope_version`, `build.mode`, and `solve.solver`.

#### Key Configuration Options

##### Backend Selection (`config.build.backend`)

The default backend uses the Pyomo library. For Gurobi license holders, a direct Python API interface is available, which may reduce memory and time consumption. To use it:

1. Install Gurobi: `mamba install gurobi::gurobi`
2. Configure: `config.build.backend: gurobi` (YAML) or `model.build(backend="gurobi")` (Python)

##### Ensuring Feasibility (`config.build.ensure_feasibility`)

Set to `true` to guarantee the solver finds a feasible solution by creating `unmet_demand` and `unused_supply` variables with very high costs. These appear only when necessary.

You can customize the "big M" parameter (`data_definitions.bigM`), which represents unmet demand costs. Default is 1×10⁹, but should align with maximum expected system costs (typically 1×10⁶ for urban models, as low as 1×10⁴ for rescaled data).

##### Operating Modes (`config.build.mode`)

Three modes are available:

- **`base`** (default): Standard optimization with no additional processing
- **`operate`**: Fixed capacities; uses receding horizon control
- **`spores`**: Runs `base` mode first, then finds N alternative configurations with similar costs but different technology/location choices

##### Solver Selection (`config.solve.solver`)

Supported solvers include `glpk`, `gurobi`, `cplex`, and `cbc`. All Pyomo-compatible solvers work with Calliope.

For Gurobi, the direct Python interface is typically fastest:

```yaml
config:
  solve:
    solver: gurobi
    solver_io: python
```

GLPK is recommended for beginners on Windows systems.


---

### Modes

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/modes/

Calliope supports different optimization methods to solve energy system problems. Three primary approaches are available:

#### Overview

The framework applies math in layers:

- **Base math** is always active and forms the foundation
- **Mode math** enables special cases like operate and SPORES modes
- **Extra math** provides optional additional formulations

#### Base Mode

This is the default approach using perfect foresight optimization. The system determines optimal technology capacities and their dispatch across all time periods simultaneously, minimizing total investment and operating costs combined.

Investment costs are annualized using a loan repayment formula that accounts for interest rates and technology lifespans:

$$\frac{\text{investment cost} \times \text{interest rate} \times (1 + \text{interest rate})^{\text{loan period}}}{(1 + \text{interest rate})^{\text{loan period}} - 1}$$

This converts capital expenses into equivalent annual costs comparable to fuel and maintenance expenses.

#### Operate Mode

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

#### SPORES Mode

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


---

### Technologies

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/techs/

#### Overview

The `techs` section defines all technologies in a model. Each technology is characterized by its `base_tech`, which establishes its role in the optimization model.

#### Base Technology Types

Five base technology categories exist:

- **supply**: Draws from a source to produce a carrier
- **demand**: Consumes a carrier for an external sink
- **storage**: Stores a carrier
- **transmission**: Transmits a carrier between nodes
- **conversion**: Converts between different carriers

#### Example: Combined Cycle Gas Turbine

A sample `ccgt` technology demonstrates key parameters:

```yaml
ccgt:
  name: 'Combined cycle gas turbine'
  color: '#FDC97D'
  base_tech: supply
  carrier_out: power
  source_use_max: .inf
  flow_out_eff: 0.5
  flow_cap_max: 40000
  lifetime: 25
```

Technologies must specify a base type, output/input carriers as appropriate, and various constraints and costs for the optimization problem.

#### Template-Based Configuration

Technologies can inherit definitions using the `template` key, enabling configuration sharing across multiple technologies or nodes without duplicating specifications.

#### Transmission Technologies

Since transmission technologies span two nodes, they're defined differently than node-based technologies:

```yaml
techs:
  ac_transmission:
    base_tech: transmission
    link_from: region1
    link_to: region2
    flow_cap_max: 100
```

By default, flow directions are bidirectional unless `one_way: true` is set.

#### Required Parameters by Base Tech

- **supply**: `base_tech`, `carrier_out`
- **demand**: `base_tech`, `carrier_in`
- **storage**: `base_tech`, `carrier_in`, `carrier_out`
- **transmission**: `base_tech`, carriers, `link_to`, `link_from`
- **conversion**: `base_tech`, `carrier_in`, `carrier_out`

#### Custom Parameters

Users can add custom parameters beyond pre-defined ones, provided they don't start with underscores or numbers. Parameters beginning with `cost_` must follow the data_definitions format to specify cost classes.

#### Deactivation

Technologies can be deactivated in overrides by setting `active: false`, removing them entirely from the model.


---

### Nodes

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/nodes/

#### Understanding Node-Level Parameters

The `techs` parameter is mandatory for nodes, though it can be an empty dictionary (`techs: {}`). This approach works when a node serves as a junction point for transmission technologies, which are defined separately rather than within a node's `techs` specification.

Note that the parameter definition formats documented for technologies also apply to node-level parameters.

#### Arbitrary Per-Node Data

Nodes support custom parameter data that becomes accessible in optimization problems, indexed along the nodes dimension. Parameters can also be populated using data definition syntax to span additional dimensions beyond nodes.

Example configuration:

```yaml
nodes:
  region1:
    custom_node_parameter: 100
    custom_node_flow_out_max:
      data: [1000, 2000]
      index: [electricity, gas]
      dims: carriers
```

In this example, `custom_node_flow_out_max` at `region1` could support custom mathematical constraints limiting total outflow of electricity and gas carriers at that location.

##### Deactivating Nodes

Within overrides, you can remove nodes from the model entirely using `active: false`. This eliminates the node from the resulting dataset completely. The same mechanism works for deactivating specific technologies at a node.

**Important:** When deactivating nodes, any transmission technologies linking to that node are automatically deactivated as well.


---

### Data Tables

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/data_tables/

#### Loading Tabular Data

Calliope enables loading data from CSV files or pandas dataframes using the `data_tables` configuration. The basic syntax includes:

- **data**: File path or in-memory object reference
- **rows**: Dimension(s) defined per row
- **columns**: Dimension(s) defined per column
- **select**: Filter specific dimension values
- **drop**: Remove unwanted dimensions
- **add_dims**: Inject dimensions with assigned values
- **rename_dims**: Map dimension names to Calliope conventions

#### CSV File Structure Requirements

##### Header Rows
CSV files must include at least one header row. Without it, Calliope will misinterpret data as dimension names and generate errors.

##### Multi-Level Indexing
You can define multiple index levels per row or column to handle multi-dimensional data. For example, a table with both node and technology indices would look like:

```
nodes    | techs
---------|-------
node1    | tech1  → 15
node2    | tech2  → 5
```

##### Sparse Arrays
For data with many empty cells, use a "long and thin" dense structure rather than a square sparse format.

#### Practical Examples

##### Loading Time Series Data

```yaml
data_tables:
  pv_capacity_factor_data:
    data: data_tables/pv_resource.csv
    rows: timesteps
    add_dims:
      techs: pv
      parameters: source_use_equals
```

**Note on timestamps**: Calliope expects ISO 8601 format (`YYYY-MM-DD hh:mm:ss`) by default.
This is configurable via `config.build.time_format`.

##### Loading Technology Data

```yaml
data_tables:
  tech_data:
    data: data_tables/tech_data.csv
    rows: [techs, parameters]
```

#### Advanced Features

##### Selection and Filtering
Select specific dimension values while loading:

```yaml
data_tables:
  tech_data:
    rows: [techs, parameters]
    columns: nodes
    select:
      nodes: [node1, node2]
```

Drop unwanted dimensions (useful for scenario columns):

```yaml
select:
  scenarios: scenario1
drop: scenarios
```

##### Adding Dimensions
Avoid repetition by adding dimensions during load:

```yaml
add_dims:
  costs: monetary
  parameters: cost_flow_cap
```

##### Templates
Reuse common configurations across multiple data tables:

```yaml
templates:
  common_data_options:
    data: data_tables/tech_data.csv
    rows: timesteps
    add_dims:
      parameters: source_use_max

data_tables:
  tech_data_1:
    template: common_data_options
    add_dims:
      techs: tech1
      nodes: node1
```

##### Dimension Renaming
Map non-standard dimension names to Calliope conventions:

```yaml
rename_dims:
  time: timesteps
```

#### Loading from Pandas DataFrames

You can pass dataframes directly when initializing a model:

```python
import calliope
import pandas as pd

df1 = pd.DataFrame(...)
model = calliope.Model(
    "path/to/model.yaml",
    data_table_dfs={"data_source_1": df1}
)
```

Then reference the key in your YAML:

```yaml
data_tables:
  ds1:
    data: data_source_1
    rows: timesteps
```

#### Important Considerations

1. **Required parameter dimension**: Every data table must include a `parameters` dimension in rows, columns, or `add_dims`

2. **Processing order**:
   - Select values
   - Drop dimensions
   - Add dimensions

3. **Loading order**: Tables load sequentially; later tables override earlier ones with conflicting data

4. **File naming**: CSV files must contain `.csv` in the filename (including compressed files like `.csv.zip`)

5. **Automatic tech-node inference**: Calliope infers technology availability at nodes from tabular data containing both dimensions, though explicit YAML definition is recommended

6. **Automatic type conversion**:
   - Dimensions with "steps" suffix (e.g., `timesteps`) convert to timeseries format
   - Numeric dimension values are automatically converted to appropriate numeric types

#### Data You Cannot Load Tabulary

The following cannot be defined in tabular format:

- `active`: Technology/node activation (YAML only)
- `definition_matrix`: Auto-generated from `carrier_in` and `carrier_out`
- `template`: Template references (YAML only)
- `templates`: Template definitions (YAML only)


---

### Data Definitions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/data_definitions/

#### Overview

The `data_definitions` section allows you to define data that isn't indexed over technologies or nodes. This can be a single value or data indexed across one or more model dimensions.

##### Basic Usage

Simple scalar values:
```yaml
data_definitions:
  my_param: 10
```

Or with explicit structure:
```yaml
data_definitions:
  my_param:
    data: 10
```

These are accessible as `model.inputs.my_param` and can be used in custom math.

##### Indexed Data

Data can be indexed over existing model dimensions:
```yaml
data_definitions:
  my_indexed_param:
    data: 100
    index: monetary
    dims: costs
  my_multiindexed_param:
    data: [2, 10]
    index: [[monetary, electricity], [monetary, heat]]
    dims: [costs, carriers]
```

You can also create new custom dimensions, though these must be defined in custom math files and included in your model configuration.

#### Parameters vs. Lookups

Data definitions populate either parameters or lookups depending on how they're defined in the model math. Lookups serve as helper parameters with non-numeric values like strings or booleans.

#### Broadcasting Data

When `broadcast_input_data` is enabled in configuration, a single value automatically applies to all index items:

```yaml
my_indexed_param:
  data: 1  # Applies to all index values
  index: [val1, val2, val3, val4]
  dims: my_new_dim
```

**Warning**: Broadcasting risks unintended data assignment if index values change via scenario overrides.

**Note**: Avoid `data_definitions` for large datasets (like time-indexed data) due to memory overhead.


---

### Scenarios and Overrides

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/scenarios/

#### Overview

Calliope allows you to define variations of your model without creating separate files. This is accomplished through two complementary mechanisms:

- **Overrides**: YAML blocks that expand or replace parts of the base model configuration
- **Scenarios**: Named combinations of multiple overrides

#### Structure

Both overrides and scenarios are defined at the top level of your model configuration file. Here's the basic structure:

```yaml
scenarios:
  high_cost_2005: ["high_cost", "year2005"]
  high_cost_2006: ["high_cost", "year2006"]

overrides:
  high_cost:
    techs.onshore_wind.cost_flow_cap.data: 2000
  year2005:
    init.subset.timesteps: ['2005-01-01', '2005-12-31']
  year2006:
    init.subset.timesteps: ['2006-01-01', '2006-12-31']

config:
  ...
```

#### How They Work

Each override receives a name and can specify any model configuration settings. In the example above:
- The `high_cost` override modifies technology costs
- The `year2005` and `year2006` overrides specify different time periods

Scenarios bundle overrides together. The `high_cost_2005` scenario applies both the `high_cost` and `year2005` overrides simultaneously.

#### Usage

Overrides can be applied individually or as scenarios when running your model. This approach enables sensitivity analyses and comparative studies without file duplication.

#### Important Note

"Overrides are executed _after_ `imports:` but _before_ `templates:`," meaning you can override template values but not imported files.


---

### Running a Model via the Command Line

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/running-cli/

#### Basic Syntax

The fundamental command structure is:

```
$ calliope run testmodel/model.yaml --save_netcdf=results.nc
```

#### Command Options

The `calliope run` command supports these options:

- **`--save_netcdf={filename.nc}`**: Exports the complete model and results to a NetCDF file. This approach is recommended as it maintains data integrity and enables later model reconstruction for additional analysis.

- **`--save_csv={directory name}`**: Writes results as CSV files to a specified directory, useful for further processing in spreadsheet applications.

- **`--debug`**: Activates debug mode to display additional internal details, helping diagnose model failures.

- **`--scenario={scenario}`** and **`--override_dict={yaml_string}`**: Applies scenarios or overrides to the model (see section below).

- **`--help`**: Displays all available options.

Multiple save options can be combined:

```
$ calliope run testmodel/model.yaml --save_netcdf=results.nc --save_csv=outputs
```

**Important:** By default, the command-line tool does not save results—you must explicitly specify a save option.

#### Applying Scenarios or Overrides

The `--scenario` option accepts:

1. A scenario name from model configuration: `--scenario=my_scenario`
2. A single override name: `--scenario=my_override`
3. Multiple comma-separated overrides: `--scenario=my_override_1,my_override_2`

Options 2 and 3 create temporary scenarios on-the-fly without formal definition.

##### Example Usage

```
$ calliope run testmodel/model.yaml --scenario=milp --save_netcdf=results.nc
```

If both a scenario and override share the same name, Calliope raises an error for disambiguation.

##### Using YAML Overrides

Pass inline YAML strings via `--override_dict`, applied after `--scenario`:

```
$ calliope run testmodel/model.yaml --override_dict="{'init.subset.timesteps': ['2005-01-01', '2005-01-31']}" --save_netcdf=results.nc
```


---

### Running a Model in Python

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/running-python/

#### Basic Usage

To run a model programmatically, create a `calliope.Model` instance and execute its build and solve methods:

```python
import calliope
model = calliope.Model('path/to/model.yaml')
model.build()
model.solve()
```

**Note:** A model definition must be specified; omitting it raises an error.

#### Alternative Loading Methods

Models can be loaded through several approaches:

- Passing an `AttrDict` or standard Python dictionary with the same nested format as YAML configuration (keys: `config`, `data_definitions`, `data_tables`, `nodes`, `techs`, etc.)
- Loading previously saved models from NetCDF: `model = calliope.read_netcdf('path/to/saved_model.nc')`

#### Pre- and Post-Processing

Before calling `build()`, inspect and adjust model configuration via the xarray Dataset at `model.inputs`. After solving, access results through `model.results`. Export results using:

- `Model.to_csv()`
- `Model.to_netcdf()` (saves inputs and results)

#### Applying Scenarios and Overrides

Two methods exist for overriding base models:

**By scenario:**
```python
model = calliope.Model('model.yaml', scenario='milp')
```

**By override dictionary:**
```python
model = calliope.Model(
    'model.yaml',
    override_dict={'config.solve.solver': 'gurobi'}
)
```

Both can be used simultaneously; scenarios apply first, then dictionary overrides.

#### Tracking Progress

Enable verbose logging with `calliope.set_log_verbosity()` after importing. Log levels from least to most verbose:

1. **CRITICAL** - critical errors only
2. **ERROR** - errors only
3. **WARNING** - default; errors and warnings
4. **INFO** - errors, warnings, and stage messages with timestamps
5. **DEBUG** - solver logging; heavily verbose for troubleshooting

Use `include_solver_output=False` to disable solver-level logging.


---

### Postprocessing

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/postprocessing/

Calliope implements two sequential postprocessing steps to refine model results.

#### Additional Result Variables

The system generates several computed metrics:

- **capacity_factor**: Indexed by technologies, nodes, and timesteps
- **systemwide_capacity_factor**: Per-tech average across nodes and time, weighted by timestep importance
- **systemwide_levelised_cost**: Per-tech carrier production cost indexed by techs, carriers, and cost classes
- **total_levelised_cost**: Carrier-aggregate production cost indexed by carriers and cost classes
- **unmet_sum**: Combines unmet demand and supply values

##### Levelised Cost Calculation

These costs are computed by dividing total cost by production: `cost / production`. The production figure uses `flow_out` + `flow_export`, temporarily scaled by weights for consistency. Since constraint-based costs already incorporate weighting, no additional adjustment occurs. Refer to the `systemwide_levelised_cost` function for implementation specifics.

> "To disable the first part of postprocessing, set `config.solve.postprocessing_active` to `false`."

#### Zero Threshold

The second step applies a `zero_threshold` parameter, which converts values below this magnitude to zero. This addresses floating-point calculation artifacts. The default threshold is `1e-10`, though setting it to `0` disables this filtering entirely.


---

## Math

### Built-in Base Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/base/

#### Overview

This documentation covers the complete mathematical formulation for a Calliope model's base math, which is always applied but can be overridden with additional or custom mathematics.

#### Guide to Math Documentation Structure

Math components are organized hierarchically:
- Initial conditions determine if a component applies
- Sub-conditions (indented `if` statements) specify expressions for dimension iterations
- **Bold terms** represent decision variables
- *Italic terms* represent parameters
- Parameters defined over time can be single values or timeseries loaded from files

#### Objective Function

##### Min Cost Optimisation (Active)

The objective minimizes total system costs. When multiple cost classes exist (e.g., monetary plus emissions), a weighted sum is minimized using the `objective_cost_weights` parameter.

Key features:
- Includes investment and operational costs
- Optionally penalizes unmet demand and unused supply when feasibility is ensured
- Scalable to multi-objective optimization

#### Primary Constraint Categories

##### Balance Constraints

**Conversion Balance**: Links outflow to consumption for conversion technologies

**Supply Balance**: For technologies without storage, fixes outflow to source consumption efficiency

**Supply with Storage**: Allows temporal offset between source consumption and outflow

**Demand Balance**: Sets demand technology requirements based on area use, capacity, or absolute values

**Storage Balance**: Tracks stored carrier across timesteps, accounting for losses and initial conditions

**Transmission Balance**: Ensures carrier flow conservation across links

##### Capacity Constraints

**Flow In/Out Limits**: Bounds technology inflow and outflow based on installed capacity

**Storage Capacity**: Constrains stored quantity relative to storage capacity

**Source Capacity**: Limits supply resource consumption

**Ramping Constraints**: Restricts rate of change in technology output between timesteps

##### System-level Constraints

**System Balance**: Ensures total carrier production equals consumption at each node/timestep

**Area Use Limits**: Caps total land area technologies can occupy

**Systemwide Capacity Bounds**: Sets technology-wide capacity limits across all nodes

#### Decision Variables

Core decision variables include:

- `flow_cap`: Technology flow capacity
- `flow_in/flow_out`: Carrier flows by timestep
- `source_cap`: Supply resource capacity
- `source_use`: Resource consumption
- `storage_cap`: Energy storage capacity
- `storage`: Stored quantity by timestep
- `area_use`: Land area utilization
- `unmet_demand/unused_supply`: Feasibility slack variables (when enabled)

#### Key Parameters

Essential parameters controlling model behavior:

- `cost_*`: Various cost components (investment, operational, annualized)
- `*_cap_max/min`: Capacity bounds
- `*_eff`: Efficiency factors
- `storage_loss`: Temporal storage decay
- `flow_ramping`: Rate-of-change limits
- `timestep_resolution`: Duration weights
- `lifetime`: Asset operational lifespan

#### Cost Calculation

Total system cost comprises:

1. **Annualized Investment Costs**: Lifetime costs discounted to annual equivalent using interest rates and depreciation
2. **Fixed Operation Costs**: Time-invariant operational expenses
3. **Variable Operation Costs**: Timestep-dependent expenses

The annuity calculation accounts for modeling period length relative to one year and applies compound interest formulas when interest rates exceed zero.


---

### Other (Non-base) Built-in Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/

This documentation page serves as a navigation hub for Calliope's non-base mathematical formulations.

#### Available Sections

The documentation organizes non-base built-in math into three main categories:

1. **Mixed Integer Linear Programming Math** — Extensions for MILP problem formulations
2. **Inter-cluster Storage Math** — Mathematical constraints for storage systems spanning multiple clusters
3. **Spores Mode Math** — Specialized mathematical framework for the Spores optimization mode

#### Purpose

This section complements the "Built-in base math" documentation by providing advanced mathematical formulations that users can optionally incorporate into their Calliope energy models. These modules allow modelers to represent more complex system behaviors and constraints beyond the standard linear programming framework.

Users are encouraged to navigate using the sidebar to access detailed documentation for whichever mathematical extension matches their modeling requirements.


---

### Mixed Integer Linear Programming Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/milp/

#### Overview

This documentation covers the **mixed integer linear programming (MILP) mathematical formulation** that applies on top of Calliope's base math when referenced as `"milp"` in `config.init.extra_math`.

#### Objective Function

##### Minimum Cost Optimisation

The primary objective seeks to minimize total system costs, encompassing both installation and operational expenses. When multiple cost classes exist (such as monetary and CO2 emissions), a weighted sum minimizes the total.

**Key components:**
- Sums costs across all nodes and technologies
- Applies objective cost weights to each cost class
- When `config.ensure_feasibility==true`, adds penalty terms for unmet demand and unused supply using a "big M" multiplier

#### Main Constraint Categories

##### Area and Capacity Constraints

- **area_use_capacity_per_loc**: Bounds total technology area at each node
- **area_use_minimum**: Sets lower bounds on area use
- **area_use_per_flow_capacity**: Fixes relationship between flow capacity and land occupation

##### Flow Capacity Constraints

The framework implements multiple capacity-related constraints:

- **flow_capacity_maximum_purchase_milp**: Limits capacity for technologies with integer unit purchasing
- **flow_capacity_minimum**: Establishes lower bounds on capacity
- **flow_capacity_per_storage_capacity**: Links storage flow rates to capacity ratios
- **flow_capacity_systemwide**: Applies capacity bounds across entire system

##### Flow Bounds by Operating Mode

- **flow_in_max** and **flow_in_max_milp**: Consumption limits
- **flow_out_max** and **flow_out_max_milp**: Production limits
- **flow_out_min** and **flow_out_min_milp**: Minimum output requirements

##### Storage and Balance Equations

- **balance_storage**: Tracks stored carrier across timesteps accounting for losses and flows
- **balance_supply_no_storage**: Couples source consumption directly to output
- **balance_supply_with_storage**: Allows temporal offset between source use and delivery
- **balance_demand**: Constrains sink demands based on availability parameters
- **balance_conversion**: Enforces input-output relationships for conversion technologies

##### Operational Flexibility

- **ramping_up** and **ramping_down**: Limit rate of change in technology operation between timesteps
- **async_flow_in_milp** and **async_flow_out_milp**: Control simultaneous inflow/outflow capability

##### Unit Commitment Features

- **unit_commitment_milp**: Enforces discrete unit operation
- **operating_units**: Binary variables tracking active units
- **purchased_units**: Integer capacity purchasing

#### Decision Variables

The optimization determines values for:

- **flow_cap**: Technology capacity investments
- **flow_in/flow_out**: Carrier flows per timestep
- **storage**: Stored energy levels
- **operating_units**: Active unit counts
- **purchased_units**: Total unit acquisitions
- **source_use**: Resource consumption rates

#### Key Parameters

Essential input parameters include:

- **flow_cap_max/min**: Capacity bounds
- **flow_out_min_relative**: Minimum operating points
- **flow_ramping**: Rate-of-change limits
- **storage_loss**: Temporal decay rates
- **cost_***: Investment and operational expenses
- **timestep_resolution**: Duration of each modeling period

#### Implementation Notes

The mathematical formulation uses conditional logic throughout: each constraint activates only when specific parameters exist or conditions hold. This enables flexible model configuration without unnecessary complexity in infeasible scenarios.


---

### Inter-cluster Storage Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/storage_inter_cluster/

#### Overview

This page documents **extra mathematical formulations** for inter-cluster storage that applies on top of the base mathematical model. These formulations are only activated when `"storage_inter_cluster"` is referenced in the `config.init.extra_math` list.

#### Objective Function

##### Minimum Cost Optimization

The system minimizes total installation and operational costs. When multiple cost classes exist (e.g., monetary and emissions), a weighted sum is minimized using the `objective_cost_weights` parameter.

The objective includes penalties for unmet demand and unused supply when feasibility is enforced via configuration settings.

#### Key Constraints

##### Storage Balance Across Days

**balance_storage_inter** establishes relationships between consecutive days by fixing how a storage technology's available carrier changes based on:
- Previous day's representative storage fluctuations
- Excess stored carrier accumulated across all preceding days
- Storage loss rates

##### Intra-Day Storage Bounds

Two constraints limit storage within individual clustered days:

- **storage_intra_max**: Upper bounds on stored carrier within a day
- **storage_intra_min**: Lower bounds on stored carrier within a day

##### Multi-Day Storage Bounds

- **storage_inter_max**: Combines inter-day storage with intra-day maximums to ensure total capacity limits
- **storage_inter_min**: Combines inter-day storage losses with intra-day minimums to maintain reserve levels

#### Decision Variables

Key variables include:

- `storage_inter_cluster`: Stored carrier available across multiple days
- `storage_intra_cluster_max`: Maximum storage within a clustered day
- `storage_intra_cluster_min`: Minimum storage within a clustered day
- `storage`: Instantaneous storage level at each timestep

#### Important Parameters

- `storage_loss`: Hourly decay rate (exponentiated to 24 for daily calculations)
- `storage_initial`: Initial storage fraction of capacity
- `cyclic_storage`: Enables wrap-around from final to first period
- `lookup_datestep_cluster`: Maps days to representative clusters
- `lookup_datestep_last_cluster_timestep`: Identifies final timestep of each day


---

### SPORES Mode Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/math/built_in/spores/

#### Overview

This page documents the **Spores mode math** formulation in Calliope, which applies on top of the base mathematical framework when `config.build.mode` is set to `"spores"`. The SPORES methodology enables finding multiple diverse, near-optimal system designs.

#### Key Components

##### Objectives

**min_cost_optimisation (active)**: Minimizes total system installation and operation costs. When multiple cost classes exist, a weighted sum is minimized. Includes penalty terms for unmet demand when feasibility is enabled.

**min_spores (inactive)**: Applied after the baseline optimization, this objective minimizes diversity scores assigned to each technology's flow capacity at each node, helping identify alternative solutions.

##### Main Constraints

The formulation includes constraints for:

- **Energy balance**: System-wide carrier production equals consumption at each node and timestep
- **Storage dynamics**: Fixed relationships between stored carrier quantities across timesteps
- **Flow limits**: Upper and lower bounds on technology inflows and outflows
- **Capacity relationships**: Constraints linking flow capacity to storage capacity and area use
- **Supply/demand**: Fixed or bounded source consumption and demand fulfillment
- **Transmission**: Relationships between bidirectional flow capacities
- **Ramping**: Limits on rate-of-change in technology output

##### Cost Calculation

Total cost combines:
- Annualized investment costs
- Fixed operational costs
- Variable operational costs (summed across all timesteps)

##### SPORES-Specific Feature

The **total_system_cost_max** constraint limits system cost in SPORES iterations: "total cost ≤ baseline_cost × (1 + slack_parameter)", allowing near-optimal solutions within a user-defined tolerance.

#### Documentation Structure

Each constraint and objective includes:
- Mathematical formulation
- Relevant decision variables and parameters
- YAML configuration snippets
- Conditional logic for different technology types

The documentation emphasizes that parameters can be defined as single values or time-varying series loaded from data files.


---

## User-Defined Math

### Defining Your Own Math

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/

#### Overview

Calliope version 0.7 and later allows users to define custom mathematical formulations for optimization problems using YAML files. The same syntax used for pre-defined math can extend the framework with new constraints, decision variables, and objectives.

#### Core Concepts

Mathematical components are organized under named keys containing:

- **Sets**: Dimensions over which components generate (technologies, nodes, timesteps, etc.)
- **Conditions**: Criteria determining when components build in specific models
- **Expressions**: The mathematical formulations themselves

#### Component Types

The framework supports four primary math component categories:

1. **Decision variables** — values the optimization model determines
2. **Global expressions** — combinations of variables and parameters using mathematical operations
3. **Constraints** — bounds and limitations on decision variables using other elements
4. **Objectives** — expressions to minimize or maximize

#### Important Constraints

**Linear Framework**: Calliope operates as a linear modeling system. Users should be aware that custom math may inadvertently create nonlinear problems, though solvers typically provide error messages when this occurs.

**Documentation Structure**: The project recommends reviewing math components first, then syntax details, followed by customization approaches and examples.

#### Additional Resources

The documentation includes comprehensive coverage of math components, formulation syntax, helper functions, customization procedures, and a gallery of user-defined math examples.


---

### Math Components

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/components/

This page documents the foundational elements needed to construct optimization problems in Calliope.

#### Decision Variables

Decision variables represent unknown quantities that an optimization algorithm can adjust to meet objectives while respecting constraints. Examples include technology capacity and per-timestep carrier flows.

Key characteristics:

- **Unique naming**: Required identifier for each variable
- **Metadata**: Optional title, description, and unit annotations
- **Indexing**: Uses `foreach` lists and `where` conditions to apply variables across model dimensions
- **Domain specification**: Can be real (default), integer, or binary
- **Bounds**: Require minimum and maximum limits via either numeric values or parameter references
- **Activation control**: Can be disabled with `active: false`
- **Default values**: Help prevent undefined results in calculations

Example structure includes properties like `storage_cap` with bounds referencing input parameters.

#### Global Expressions

These reusable mathematical combinations of variables and parameters appear in multiple constraints or objectives without cluttering the formulation.

Defining characteristics:

- **Reusability**: Accessed across multiple constraints and objectives
- **Result tracking**: Expressions return numeric values directly in optimization results
- **Metadata support**: Optional title, description, and unit information
- **Equation definitions**: Use expressions without comparison operators
- **Sub-expressions**: Optional nested expressions for complex calculations
- **Ordering control**: The `order` attribute allows prioritization when new expressions reference existing ones

An example tracks total costs by combining investment and operational expenses.

#### Constraints

Constraints embed real-world system limitations and relationships between decision variables. They enforce physical laws and operational bounds.

Essential features:

- **Unique identification**: Named for reference
- **Dimensional indexing**: Applied via `foreach` and `where` statements
- **Equation requirements**: Must include comparison operators (==, <=, >=)
- **Sub-expressions and slices**: Optional components for complex logic
- **Deactivation capability**: Controlled via `active: false`

#### Piecewise Constraints

These represent non-linear relationships using special ordered sets (SOS2) and binary variables for linear approximation.

Structure elements:

- **X and Y expressions**: Link two variables along a curve
- **Breakpoint values**: Parameters defining piecewise segments
- **Special syntax**: Unique format compared to other components

**Caution**: Piecewise constraints increase solver difficulty; convex functions may use simpler constraint approaches instead.

#### Objectives

An objective function directs optimization toward minimization or maximization of a target quantity.

Properties:

- **Single activation requirement**: Only one objective can be active per model
- **Optional filtering**: `where` strings control activation without `foreach` indexing
- **Expression format**: No comparison operators in expressions
- **Sub-expressions**: Supported for complex formulations
- **Sense specification**: Explicitly declares minimization or maximization

The default objective minimizes total system costs across all technologies.


---

### Math Syntax

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/syntax/

#### Overview

The math syntax enables formulation of math components by populating n-dimensional matrices with mathematical expressions. The approach combines three key elements: defining dimensions with `foreach`, subsetting data with `where` strings, and populating subsets with equation expressions.

#### foreach Lists

Define the dimensions (sets) over which a math component is indexed. Available dimensions include: `nodes`, `techs`, `carriers`, `costs`, `timesteps`, and optionally `datesteps` (with time clustering). Custom dimensions can be added to the model dataset.

Example: `foreach: [nodes, techs]` builds the component across all nodes and technologies.

#### where Strings

Subset data or model configurations using conditional statements combined with logical operators (`and`, `or`, `not`). Supported statement types:

**1. Parameter existence checks:**
- Basic: `flow_out_eff` (checks if defined)
- With aggregation: `any(resource, over=nodes)` (checks if any node has a value)

**2. Value comparisons:**
- Operators: `>`, `<`, `==`, `<=`, `>=`
- Examples: `config.mode==operate`, `flow_eff<0.5`
- Helper functions available: `get_val_at_index(dim=timesteps, idx=0)`

**3. Technology base checks:**
- Example: `base_tech==storage`

**4. Set subsetting:**
- Example: `defined(techs=[tech1, tech2], within=nodes, how=any)`

Statements can be grouped with parentheses and combined with logical operators (case-insensitive).

#### Expression Strings

Combine input parameters, decision variables, global expressions, and numeric values using:

**For global expressions/objectives:** `+`, `-`, `*`, `/`, `**` (following standard operator precedence)

**For constraints:** Add comparison operators `<=`, `>=`, `==`

##### Slicing Data

Subset components without fully specifying all sets. Square bracket syntax: `flow_out[carriers=electricity, nodes=[A, B]]`. The system automatically matches relevant array elements during application.

#### Equations

Define one or more equation expressions with optional `where` strings to condition application:

```
equations:
  - where: flow_eff > 0
    expression: flow_out / flow_out_eff == flow_in
  - where: flow_eff == 0
    expression: flow_out == 0
```

Single equations don't require a `where` statement. Equation-level `where` strings append to top-level `where` conditions.

#### Sub-expressions

Reference frequently-used expression segments using the `$` prefix:

```
equations:
  - expression: flow_out <= $adjusted_flow_in
sub_expressions:
  adjusted_flow_in:
    - where: base_tech==storage
      expression: flow_in * flow_eff
```

#### Slices

Create dynamic data references within slice definitions using `$` identifiers:

```
equations:
  - expression: sum(flow_out[techs=$tech_ref]) <= flow_in
slices:
  tech_ref:
    - expression: lookup_techs
```

#### default

Specify default values for variables and global expressions to fill empty array elements and prevent `NaN` values in the optimization problem.


---

### Helper Functions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/helper_functions/

Helper functions enable more complex operations within `where` strings and `expression` strings in Calliope's user-defined math. Here's a summary of available functions:

#### any

Check if at least one non-NaN value exists in specified dimensions. For example, `any(cost, over=[nodes, techs])` verifies whether the cost variable contains at least one defined value across tech and node combinations.

#### defined

Verify non-NaN values along dimensions. Examples include checking if technologies exist within nodes or carriers are defined in tech groups.

#### sum

Sum over one or more dimensions of arrays (parameters, decision variables, or global expressions) using the `over=` parameter.

#### select_from_lookup_arrays

Apply lookup arrays to data arrays for index mapping operations, particularly useful with time clustering operations.

#### get_val_at_index

Access integer indices in dimensions. For instance, `get_val_at_index(timesteps=0)` retrieves the first timestep, while `get_val_at_index(timesteps=-1)` gets the last. Commonly used for applying different expressions at specific timestep positions.

#### roll

Shift data in component arrays by N positions along a dimension. The expression `storage == roll(storage, timesteps=1) + 1` mirrors a for-loop statement `storage[t] == storage[t - 1] + 1`.

#### default_if_empty

Insert placeholder values when NaN values would otherwise disrupt optimization. Most useful for user-defined parameters and decision variables when sparse arrays cause issues.

#### where

Apply conditions to specific components within expressions using `where(<component>, <condition>)`, enabling selective masking and dimension broadcasting.

#### group_sum

Sum across grouped dimension members efficiently. Maps combinations to grouping categories, useful for constraining transmission lines or power plant categories.

#### group_datetime

Sum variables over time periods (hours, days, weeks). For example, `group_datetime(flow_in, timesteps, date)` sums flow across dates.

#### sum_next_n

Sum across rolling windows using `sum_next_n(<component>, <dimension>, <window>)`. Useful for demand-side management and unit commitment constraints.


---

### Adding Your Own Math to a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/customise/

#### Overview

Once you understand math components and formulation syntax, you can introduce custom math to your Calliope model. This math can either extend the pre-defined formulation or replace it entirely.

#### Adding Extra Math

The simplest approach involves extending Calliope's existing math by defining an "extra math" option. For instance, you might add a time-varying parameter to the `storage_max` constraint:

```yaml
storage_max:
  equations:
    - expression: storage <= storage_cap * time_varying_parameter
```

This preserves other constraint elements without requiring redefinition.

##### Configuration

Reference YAML files containing custom math in your model configuration using `config.init.extra_math`. Both absolute and relative paths (relative to `model.yaml`) are supported:

```yaml
config:
  init:
    math_paths:
      my_new_math_1: "my_new_math_1.yaml"
      my_new_math_2: "/home/your_name/Documents/my_new_math_2.yaml"
```

Select which math applies during model runs:

```yaml
config:
  init:
    extra_math: [my_new_math_1, storage_inter_cluster, my_new_math_2]
```

**Priority Order:** "base math -> mode -> extra math"

##### Python Integration

In interactive sessions, pass math as a dictionary during model instantiation:

```python
calliope.from_yaml(..., math_dict={"my_new_math_1": {...}, ...})
```

Inspect the final applied math via `model.math.build`.

#### Replacing Base Math

To start from scratch, replace Calliope's pre-defined base math entirely:

```yaml
config:
  init:
    math_paths: {base: your/base_math_file.yaml}
```

Similarly, replace mode-specific math like `operate`:

```yaml
config:
  init:
    math_paths: {operate: your/operate_math_file.yaml}
```

**Warning:** Modes and pre-defined options may not function as expected with custom replacements.

#### Adding Parameter Metadata

When introducing new parameters, include their metadata in the math definition to enable validation and documentation generation:

```yaml
dims:
  techs:
    dtype: string
    title: Technologies

parameters:
  flow_cap_max:
    default: .inf
    title: Maximum rated flow capacity.
    description: Limits `flow_cap` to a maximum.
    unit: power

lookups:
  source_unit:
    default: absolute
    title: Source unit
    one_of: [absolute, per_cap, per_area]
```

#### Validating Math

Enable pre-build validation to catch errors before optimization:

```yaml
config:
  init:
    pre_validate_math_strings: true
```

#### Generating Documentation

Create rich-text mathematical documentation for your model:

```python
from calliope.postprocess.math_documentation import MathDocumentation

model = calliope.Model("path/to/model.yaml")
model.build()

math_documentation = MathDocumentation(model, include="valid")
math_documentation.write(filename="path/to/output/file.[tex|rst|md]")
```

For interactive online documentation with MKDocs, enable `mkdocs_features=True`.


---

## User-Defined Math Examples

### User-Defined Math Example: Annual Energy Balance

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/annual_energy_balance/

#### Description

This feature allows you to "limit or set the total (e.g. annual) outflow of a technology to a specified absolute value."

##### New Parameters

The implementation introduces technology-level parameters:
- `annual_flow_max`
- `annual_source_max`

Additionally, indexed parameters and lookups are available:
- `annual_flow_max` (indexed)
- `flow_max_group` (indexed lookup)

##### Helper Functions

The constraint definitions utilize the `sum` expression helper function.

#### YAML Definition

The implementation defines three main parameters:

| Parameter | Description | Default | Unit |
|-----------|-------------|---------|------|
| `annual_flow_max` | Annual maximum outflow | .inf | energy |
| `annual_source_max` | Annual maximum source use | .inf | energy |
| `annual_sink_max` | Annual maximum sink use | .inf | energy |

##### Constraints

Five constraints are defined:

1. **Per technology and node**: "Limit total technology annual energy production at each possible deployment site" using `sum(flow_out, over=[carriers, timesteps]) <= annual_flow_max`

2. **Global per technology**: Constrains production across all deployment sites

3. **Global multi-technology**: Limits combined technology production using sliced references

4. **Total source availability**: Restricts flow into the system from particular sources via `sum(source_use, over=[nodes, timesteps]) <= annual_source_max`

5. **Total sink availability**: Controls demand sink flows excluding pinned values


---

### User-Defined Math Example: CHP Plants

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/chp_htp/

#### Description

This documentation describes how to model Combined Heat and Power (CHP) plants with three distinct operational configurations:

##### Type 1: Extraction (Condensing) Turbines
"Some electrical efficiency can be sacrificed by diverting high-temperature steam to provide more heat." An operating region exists between the extraction line (cv) and backpressure line (cb), with fuel consumption remaining constant along the extraction curve.

##### Type 2: Backpressure with Auxiliary Boilers
These units lack extraction capability but include a direct heating boiler. Heat output comes from two sources: steam from the turbine and fuel diverted to the boiler. This creates a defined operating region bounded by the backpressure line.

##### Type 3: Backpressure Only
"There is no operating region; the output must follow the backpressure line." Output is strictly constrained to the backpressure relationship.

#### Key Parameters

The implementation introduces four technology-level parameters:

- **turbine_type**: Specifies extraction or backpressure variants
- **power_loss_factor**: Extraction turbine parameter (cv)
- **power_to_heat_ratio**: Backpressure ratio (cb)
- **boiler_eff**: Conventional boiler efficiency

#### Implementation Notes

These constraints override the base `balance_conversion` constraint using conditional "where" clauses to prevent conflicts between different CHP configurations.


---

### User-Defined Math Example: Demand Share Per Timestep as Decision Variable

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/demand_share_per_timestep_decision/

#### Description

This feature enables models to determine how demand for a carrier is distributed among specified technologies, with each technology maintaining an identical share across all timesteps. The implementation can be extended to iterate over nodes and carriers as needed.

Key characteristics:

- The share is calculated relative to the flow from a designated demand technology (or group thereof)
- A `relaxation` parameter provides flexibility around specified values, improving model solvability
- New indexed parameters include `relaxation` and `demand_share_limit`
- Helper functions: `sum` (expression) and `select_from_lookup_arrays` (expression)

#### YAML Definition

##### Parameters

**demand_share_relaxation**: Controls deviation tolerance from the demand share limit. A value of 0.01 allows ±1% flexibility. Default is 0 (no relaxation).

**demand_share_limit**: Specifies the total demand share that technologies must meet. Default is 1 (full demand). Must be between 0 and 1.

##### Lookups

**decide_demand_share**: Links generating technologies to consuming (demand) technologies, establishing which generator supplies what demand.

**demand_share_carrier**: Identifies the carrier being tracked between generating and consuming technologies.

##### Variables

**demand_share_per_timestep_decision**: Represents the relative demand share a technology meets per node, with bounds from 0 to infinity.

##### Constraints

Two primary constraints enforce consistent shares across timesteps:

1. **Minimum constraint**: Ensures technology outflow meets or exceeds its decided share
2. **Maximum constraint**: Caps technology outflow at its decided share

An optional **sum constraint** ensures all decision shares aggregate to a specified demand share limit (e.g., 50% of electricity demand).


---

### User-Defined Math Example: Fuel Distribution

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/fuel_dist/

#### Description

This example demonstrates how to track commodity distribution in systems where goods don't travel along distinct networks. The approach enables import/export of commodities without specifying exact origins or destinations, simplifying model definition at the cost of commodity source traceability. While termed "fuels" below, this applies equally to other commodities like waste or water with corresponding carriers.

##### Key Parameters

- `fuel_import_max`: Maximum importable fuel amount (default: infinite)
- `fuel_export_max`: Maximum exportable fuel amount (default: infinite)
- `cost_fuel_distribution`: Cost for importing or revenue for exporting fuel (default: 0)
- `allow_fuel_distribution`: Lookup array indicating carriers eligible for distribution tracking

##### Helper Functions

- `any` (where clause)
- `sum` (expression)

#### YAML Definition

##### Parameters Section
Defines three main parameters: maximum import limits, maximum export limits, and distribution costs, each with energy units and configurable defaults.

##### Lookups Section
Contains `allow_fuel_distribution`, a boolean lookup table specifying which nodes and carriers participate in fuel distribution.

##### Variables Section
The `fuel_distributor` variable represents fuel transfers between nodes. Positive values indicate imports; negative values indicate exports. It's indexed across nodes, carriers, and timesteps, with bounds from negative to positive infinity.

##### Constraints Section

**System Balance Integration**: Modifies the existing system balance constraint to incorporate fuel distribution through conditional sub-expressions.

**Total Balance**: The `restrict_total_imports_and_exports` constraint ensures that system-wide fuel imports equal exports (summing across nodes equals zero per carrier/timestep).

**Nodal Limits**:
- `restrict_nodal_imports` caps imports at `fuel_import_max`
- `restrict_nodal_exports` caps exports at `fuel_export_max`

##### Objectives Section

The objective function integrates fuel distribution costs. The implementation notes that cost impacts are negligible unless distribution costs vary by node or system-wide imbalances are permitted.


---

### User-Defined Math Example: Time-varying Flow Limit

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/max_time_varying/

#### Description

This feature allows you to establish per-timestep variations in flow limits that would otherwise remain static. For instance, `flow_cap` can be configured to fluctuate above or below its rated capacity for each timestep. To implement this, user-defined timeseries parameters must be present in model inputs, typically defined in CSV files and loaded as data tables.

**New indexed parameter:**
- `flow_cap_max_relative_per_ts`

#### YAML Definition

The following constraint implements time-varying flow limits:

```yaml
parameters:
  flow_cap_max_relative_per_ts:
    description: >
      The relative quantity of flow capacity used to limit generator
      outflow in each timestep.
    default: 1
    unit: $\frac{\text{energy}}{\text{power}}$

constraints:
  max_time_varying_flow_cap:
    description: >
      Limit flow out in each hour according to a time varying fractional
      limit that is multiplied by the technology flow cap. This represents,
      for instance, the impact of outdoor temperature on the maximum output
      of a technology relative to its rated max output.
    foreach: [nodes, techs, carriers, timesteps]
    where: "flow_cap_max_relative_per_ts"
    equations:
      - expression: >
          flow_out <=
          flow_cap_max_relative_per_ts * flow_cap * flow_out_parasitic_eff
```

This constraint multiplies the relative capacity parameter by the technology's rated capacity and efficiency to establish dynamic upper bounds on outflow per timestep.


---

### User-Defined Math Example: Net Import Share

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/net_import_share/

#### Description

This constraint limits carrier imports within nodes or across all nodes as a proportion of total carrier flows. It treats transmission technology outflows as imports, assuming technologies like `test_transmission_elec` and `test_transmission_heat` are defined.

**New indexed parameters:**
- `net_import_share`

**Helper functions utilized:**
- `defined` (where clause)
- `sum` (expression)
- `get_transmission_techs` (expression)

#### YAML Definition

##### Parameters

The `net_import_share` parameter specifies "the share of carrier out/inflows that transmission import/export at a node can account for," with a default value of 1 and unitless measurement.

##### Constraints

**net_import_share_max**: Applied per node and timestep, this constraint restricts electricity imports to a specified share of all electricity outflows minus inflows.

**net_annual_import_share_max**: Similar to the above but aggregated annually across all timesteps per node.

**net_annual_import_share_max_node_group**: Extends the constraint across multiple nodes, allowing heat import limitations for a defined node subset. Uses slices to specify the node group `[a, c]` and carrier type (heat).

##### Global Expressions

**flow_out_transmission_techs**: A pre-filtered transmission technology outflow list, where base_tech equals transmission, measured in energy units across nodes, technologies, carriers, and timesteps.


---

### User-Defined Math Example: Piecewise Linear Costs

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/piecewise_linear_costs/

#### Description

This feature allows you to implement a piecewise cost function that progressively increases investment costs as technology rated capacity grows. A critical requirement is that the binary purchase decision variable must be enabled for relevant technologies. Without this variable, the technology will incur costs regardless of whether capacity is actually deployed.

The implementation introduces two new indexed parameters:
- `cost_flow_cap_piecewise_slopes` (creates the `pieces` set)
- `cost_flow_cap_piecewise_intercept` (creates the `pieces` set)

#### YAML Definition

The configuration includes:

**Dimensions:**
- A `pieces` dimension with integer data type and `piece` iterator

**Parameters:**
- `cost_flow_cap_piecewise_slopes`: "The gradient of each of the piecewise limiting line defining the convex, non-linear cost curve"
- `cost_flow_cap_piecewise_intercept`: "The y-axis intercept of each of the piecewise limiting line defining the convex, non-linear cost curve"

**Variables:**
- `piecewise_cost_investment`: A cost variable indexed across nodes, technologies, and cost types, with bounds from 0 to infinity

**Constraints:**
The constraint `piecewise_costs` enforces that investment costs increase monotonically across pieces by relating the investment cost variable to technology flow capacity and purchased units.

**Integration:**
The new cost component integrates into the model's `cost_investment` global expression, combining with existing investment cost sources.


---

### User-Defined Math Example: Piecewise Linear Efficiency

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/piecewise_linear_efficiency/

#### Description

This documentation describes how to implement a piecewise technology efficiency function that increases efficiency as outflow rises. The approach requires enabling the `operating_units` decision variable for relevant technologies. Without this variable, technologies would have non-zero inflow requirements even at zero capacity.

The implementation introduces two new indexed parameters:

- `flow_eff_piecewise_slopes` — defines a new `pieces` set
- `flow_eff_piecewise_intercept` — defines a new `pieces` set

#### YAML Definition

The configuration includes:

**Dimensions:**
- `pieces` (integer type, with iterator `piece`)

**Parameters:**
- `flow_eff_piecewise_slopes` — "The gradient of each of the piecewise limiting line defining the convex, non-linear efficiency curve"
- `flow_eff_piecewise_intercept` — "The y-axis intercept of each of the piecewise limiting line defining the convex, non-linear efficiency curve"

**Constraints:**

A `piecewise_efficiency` constraint applies across nodes, technologies, timesteps, and pieces where the relevant parameters and capacity are available. The constraint enforces that:

```
sum(flow_in, over=carriers) >=
flow_eff_piecewise_slopes * sum(flow_out, over=carriers)
+ flow_eff_piecewise_intercept * sum(available_flow_cap, over=carriers)
```

This limits inflow requirements to monotonically increase with outflow, ensuring the model follows the efficiency curve traced by superimposed pieces.


---

### User-Defined Math Example: Flow Share Across All Timesteps

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/share_all_timesteps/

#### Description

This feature allows you to set the share of a technology's (or group of technologies') total outflow/inflow met by other technologies to specific values.

**Key capabilities:**
- Single technologies require explicit definition (e.g., `flow_in[techs=demand_power]`)
- Groups of technologies can be defined as lists or consolidated by shared attributes (e.g., `flow_out[carriers=power]`)
- Parameters can be defined per technology and optionally per node

**New technology-level parameters:**
- `demand_share_equals`
- `supply_share_equals`

**Helper functions used:**
- `sum` (expression)

#### YAML Definition

The implementation includes three main sections:

**Parameters:**
- `demand_share_equals`: Share of a technology's total inflow met by other technologies (default: 1, unitless)
- `supply_share_equals`: Share of a node's total outflows met by other technologies (default: 1, unitless)

**Lookups:**
- `demand_share_tech`: Defines which demand technology receives a specified inflow share (string type)
- `supply_share_carrier`: Specifies the carrier for tracking outflow shares (string type)

**Constraints:**
Two main constraints enforce the shares:
1. `demand_share_equals_per_tech`: Relates total outflow of certain technologies to a share of demand inflow
2. `supply_share_equals_per_tech`: Sets total outflow of technologies producing a carrier to a share of total carrier outflow in each node


---

### User-Defined Math Example: Flow Share Per Timestep

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/share_per_timestep/

#### Description

This feature allows you to set the per-timestep share of a technology's (or group of technologies) inflow or outflow to be met by other technologies at specific values.

**Key characteristics:**

- For single technologies, explicit definition is required (e.g., `flow_in[techs=demand_power]`)
- For technology groups, you can either list them explicitly or consolidate them by shared attributes (e.g., `flow_out[carriers=power]`)
- Parameters support both single values and time-varying data (e.g., from CSV files)

**New technology-level parameters:**

- `demand_share_per_timestep_equals`
- `supply_share_per_timestep_equals`

**Helper functions used:**

- `sum` (expression)

#### YAML Definition

The implementation includes two main constraints:

**Constraint 1: Demand Share**
Sets per-timestep outflow of certain technologies producing a specific carrier to equal a share of demand inflow:

```
flow_out (summed over carriers) ==
flow_in[demand_tech] (summed over carriers) * demand_share_per_timestep_equals
```

**Constraint 2: Supply Share**
Sets per-timestep outflow of technologies producing a carrier to equal a share of total per-timestep outflow for that carrier in each node:

```
flow_out[carrier] ==
sum(flow_out[carrier], over all techs) * supply_share_per_timestep_equals
```

Both constraints iterate across nodes, technologies, and timesteps, activated where respective parameters are defined.


---

### User-Defined Math Example: SOS2 Piecewise Linear Costs (Economies of Scale)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/sos2_piecewise_linear_costs/

#### Description

This feature implements a piecewise cost function that decreases the marginal investment expenses as technology capacity increases. It models "economies of scale," where deploying greater quantities of a technology reduces the per-unit investment cost.

A comprehensive example is available in the dedicated tutorial on defining piecewise linear constraints.

##### New Indexed Parameters

- `piecewise_cost_investment_x` (establishes the `breakpoints` set)
- `piecewise_cost_investment_y` (establishes the `breakpoints` set)

#### YAML Definition

The implementation uses three main sections:

**Dimensions:**
- `breakpoints`: Integer-type dimension representing SOS2 piecewise breakpoints

**Parameters:**
- `piecewise_cost_investment_x`: Flow capacity values at each breakpoint
- `piecewise_cost_investment_y`: Investment cost values at each breakpoint

**Variables:**
- `piecewise_cost_investment`: A non-decreasing investment cost variable applied across nodes, technologies, carriers, and cost types

**Piecewise Constraints:**
- `sos2_piecewise_costs`: Implements special ordered sets of type 2 (SOS2) to enforce the piecewise cost curve, linking flow capacity (`flow_cap`) to investment costs

The constraint applies where both x and y parameter values exist across breakpoints.


---

### User-Defined Math Example: Uptime/Downtime Limits

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/uptime_downtime_limits/

#### Description

This documentation outlines constraints designed to prevent technologies from operating too infrequently or excessively throughout a year. Such constraints are useful for modeling maintenance downtime or simplistic ramping limitations (applicable to technologies like nuclear power plants).

The implementation supports multiple constraint types:

- **Annual capacity factor constraints**: Establish operating ranges for technology fleets. For example, nuclear plants typically maintain annual capacity factors between 75-85%.

- **Downtime period constraint**: Enforces technology shutdown during specific timesteps by setting values for maintenance windows while leaving other periods empty (NaN).

- **Downtime period decision constraint**: Enables technologies with integer decision variables to autonomously select timesteps for non-operation, though consecutive downtime cannot be enforced.

#### New Parameters

- `capacity_factor_min`: Minimum annual operating fraction (default: 0)
- `capacity_factor_max`: Maximum annual operating fraction (default: infinity)
- `downtime_periods`: Timeseries data marking scheduled downtime (boolean, default: false)
- `uptime_limit`: Maximum timesteps an asset may operate (default: infinity)

#### YAML Definition

The mathematical formulation includes four constraint types:

**annual_capacity_factor_min**: Enforces minimum operation by ensuring summed weighted outflow meets or exceeds minimum capacity factor multiplied by total time.

**annual_capacity_factor_max**: Limits maximum operation similarly, using less-than-or-equal constraints.

**downtime_period**: Forces zero outflow across all carriers during designated downtime periods.

**downtime_period_decision**: Restricts operating units' total weighted timesteps to stay within the uptime limit for technologies with integer variables enabled.


---

## Advanced Topics

### Advanced Constraints

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/constraints/

This documentation section covers advanced features in Calliope's mathematical formulation and configuration options.

#### Multiple Input/Output Carriers

Technologies can define multiple carriers in and/or out using YAML lists. Examples include:

- **Combined heat and power (CHP) plants**: One input carrier (gas) with two co-produced outputs (electricity, heat)
- **Heat pumps**: Single input (electricity) with multiple output options (cooling or heating)
- **Dual-fuel plants**: Multiple input options (coal or biofuel) with one output (electricity)
- **Nuclear plants**: Tracking auxiliary flows like nuclear waste alongside primary output

The default math assumes inflow requirements equal the sum of outflows. However, some technologies require custom relationships—for instance, CHP plants where gas consumption depends on electricity production, not the sum of all outputs.

Technologies can differentiate parameters across carriers using indexed data structures:

```yaml
techs:
  chp:
    carrier_in: gas
    carrier_out: [electricity, heat]
    flow_cap_max:
      data: 100
      index: electricity
      dims: carriers
```

#### Storage Buffers in Non-Storage Technologies

Any technology can activate internal storage using `include_storage: true`. This allows carriers to be stored between timesteps and released later, useful for:

- Supply sources requiring intermediate storage (concentrated solar power, biogas production)
- Conversion technologies where stored carriers are processed on release

#### Revenues and Carrier Export

Negative cost values represent revenues. Export extends this concept by removing carriers from the system without meeting demand (analogous to excess rooftop solar exported to the grid).

**Important note**: Negative capacity costs require explicit capacity limits to prevent unbounded optimization.

#### Area Use Constraints

Several optional parameters manage area-related restrictions:

- `source_unit: per_area` scales resources with deployment area
- `area_use_min/max` defines spatial limits
- `area_use_per_flow_cap` links area to flow capacity (e.g., 1.5 means area equals 1.5 times capacity)
- `available_area` at nodes limits combined technology deployment space

#### One-Way Transmission Links

Transmission is bidirectional by default. Enforce unidirectionality with:

```yaml
techs:
  region1_to_region2:
    link_from: region1
    link_to: region2
    base_tech: transmission
    one_way: true
```

#### Per-Distance Transmission Constraints

Transmission technologies support distance-based parameters:

- `flow_out_eff_per_distance`: Efficiency loss per unit distance
- `cost_flow_cap_per_distance`: Capital cost per unit distance

Distance can be specified directly or calculated automatically from node coordinates.

#### Cyclic Storage

The `cyclic_storage` parameter (enabled by default) links storage levels at the beginning and end of the timeseries. This better represents recurring yearly operations where initial storage equals final storage.

With `storage_initial: 0` and `cyclic_storage: true`, stored energy must reach zero by the horizon's end. Cyclic storage functions with time clustering but cannot be used in operate mode.


---

### Time Adjustment

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/time/

#### Time Resolution Adjustment (Resampling)

Models have a default timestep length determined by the input time series data. You can adjust this resolution using the model configuration:

```yaml
config:
  init:
    resample:
      timesteps: 6h
```

This example resamples all time series data to 6-hourly intervals. Any "pandas-compatible rule describing the target resolution" can be specified. Additional dimensions with datetime types can also be resampled.

#### Time Clustering

Representative day clustering is possible by loading a file that maps dates to representative days:

```yaml
config:
  init:
    time_cluster: cluster_days_param
data_tables:
  cluster_days:
    data: /path/to/cluster_days.csv
    rows: timesteps
    add_dims:
      parameters: cluster_days_param
```

##### Storage Between Representative Days

When using representative days, you may want to enable constraints based on research by Kotzur et al. These improve carrier storage modeling between representative days by introducing the `storage_inter_cluster` decision variable, which tracks storage across all original timeseries dates. Include `storage_inter_cluster` in your additional math configuration to enable this.

##### Tools for Clustering

Calliope no longer provides built-in representative day inference. Recommended external tools include:

- **tsam**: Purpose-built for large-scale energy system models
- **scikit-learn**: General machine learning library with clustering capabilities
- **tslearn**: Timeseries-focused machine learning library

##### Example Using tsam

The documentation provides a complete Python example demonstrating how to cluster timeseries using tsam, generate representative dates, and save the results to CSV for use with Calliope.

##### Important Notes

- Resampling occurs before clustering when both are applied
- Clustered timesteps receive weights based on represented time periods
- Costs are multiplied by weights, but production values are not scaled
- Levelized costs and capacity factors account for weighting and are consistent


---

### Generating Scripts to Repeatedly Run Variations of a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/scripts/

This documentation explains how to automate model runs with different configurations using Calliope's command-line tools.

#### Generate Runs

The `calliope generate_runs` command creates automated scripts to execute models with varying parameters. Required arguments include:

- Model configuration file
- Output script filename
- `--kind`: Script type (windows for batch files, bash for Linux/macOS, bsub for LSF clusters, sbatch for SLURM clusters)
- `--scenarios`: Semicolon-separated scenario list (e.g., `scenario1;scenario2` or `override1,override2a;override1,override2b`)

**Example Windows batch script:**
```
calliope generate_runs model.yaml run_model.bat --kind=windows --scenarios "run1;run2;run3;run4"
```

**Example HPC cluster submission:**
```
calliope generate_runs model.yaml submit_runs.sh --kind=bsub --cluster_mem=1G --cluster_time=100 --cluster_threads=5 --scenarios "run1;run2;run3;run4"
```

Optional parameters include `--cluster_threads`, `--cluster_mem`, `--cluster_time`, `--additional_args`, and `--debug`.

Results save as `out_{run_number}_{scenario_name}.nc` files in the script directory.

#### Generate Scenarios

The `calliope generate_scenarios` tool creates scenario definition files from existing overrides, useful when numerous override combinations exist.

**Example usage:**
```
calliope generate_scenarios model.yaml scenarios.yaml y2000;y2001;y2002;y2003;y2004;y2005;y2006;y2007;y2008;y2009;y2010 cost_low;cost_medium;cost_high --scenario_name_prefix="run_"
```

This generates named scenarios combining all specified overrides.


---

### Specifying Custom Solver Options

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/solver/

This documentation covers how to configure custom options for optimization solvers in Calliope.

#### Gurobi

To set custom Gurobi parameters, reference the [Gurobi manual](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html) for available options. Use parameter names exactly as documented.

**Example configuration:**

```yaml
config.solve:
  solver: gurobi
  solver_options:
    Threads: 3
    NumericFocus: 2
```

#### CPLEX

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


---

### Choosing an Optimisation Problem Backend

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/backend_choice/

#### Overview

When loading a model in Calliope, no solver backend exists initially—only the input dataset. The backend is generated when calling `build()` on the model. By default, this invokes [Pyomo](https://www.pyomo.org/) to construct the model and route it to the solver specified in `config.solve.solver`.

#### Pyomo Backend

Pyomo offers **mutable input parameters**, enabling you to update parameter values without rebuilding Pyomo objects. However, it is relatively memory and time-intensive for constructing optimization problems.

#### Gurobi Backend

For larger models requiring commercial solvers, Calliope provides direct integration with the Gurobi solver Python API. Testing demonstrates this approach reduces both peak memory consumption and solution time compared to using Pyomo with Gurobi.

##### Setup Requirements

To use the Gurobi backend with an existing license:

1. Install the Gurobi Python library: `mamba install gurobi::gurobi`
2. Specify the backend in YAML configuration:
   ```yaml
   config.build.backend: gurobi
   ```
   Or at build time in Python:
   ```python
   model.build(backend="gurobi")
   ```

##### Limitations

You can still interface with your optimization problem, but certain methods will raise exceptions when the Gurobi API doesn't support functionality available in Pyomo.


---

### Interfacing with the Built Optimisation Problem

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/backend_interface/

#### Overview

After loading a model, the solver backend is generated when calling `build()`. This invokes Pyomo to construct the model and send it to a solver specified in the run configuration. Once solved, users can access results through `model.results` and interact with the backend using `model.backend`.

#### Key Capabilities

##### 1. Inspecting Optimisation Problem Components

Query the backend to examine input parameters, decision variables, global expressions, constraints, and objectives stored as xarray.DataArray objects. The `model.backend.parameters` property provides an xarray.Dataset of input parameters transformed into mutable objects, with missing data filled using predefined defaults from Calliope's base math.

##### 2. Updating Parameter Values

Use `model.backend.update_parameter()` to modify specific values. Example:

```python
new_data = xr.DataArray(0.1, coords={"techs": "ccgt", "nodes": "region1"})
model.backend.update_param("flow_out_eff", new_data)
```

Note: Changes require rerunning the backend to affect results.

##### 3. Modifying Decision Variable Bounds

Most bounds are input parameters (like `flow_cap_max`), updated via `model.backend.update_parameter()`. For fixed numeric values in custom math, use `model.backend.update_variable_bounds()`:

```python
new_data = xr.DataArray(70, coords={"techs": "battery", "nodes": "region2"})
model.backend.update_variable_bounds("flow_out", max=new_data)
```

##### 4. Fixing Decision Variables

Lock variables to previous optimal values using `model.backend.fix_variable()` with binary xarray.DataArray values:

```python
new_data = xr.DataArray(True, coords={"techs": "pv"})
model.backend.fix_variable("area_use", new_data)
```

Use `unfix_variable()` to reverse this action.

##### 5. Rerunning Optimisation

After modifying parameters or variables, call `model.solve(force=True)` to solve with current backend state. This updates `model.results` with new solution data.


---

### Shadow Prices

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/shadow_prices/

#### Overview

In linear optimization problems, you can retrieve shadow prices (dual variables) for constraints from the Pyomo backend. This feature is valuable for analyzing economic impacts and linking with other models.

To enable shadow price tracking, specify constraints in your `solve` configuration:

```yaml
config:
  solve:
    shadow_prices: ["system_balance", ...]
```

Available constraint names are listed in the "Subject to" section of the base math documentation. Custom constraints defined in user-defined math can also be referenced.

#### Important Limitations

- **Solver support varies**: Gurobi and GLPK support shadow prices; CBC does not
- **Incompatible with integer variables**: Models containing integer or binary variables cannot access shadow prices
- **Check status**: Use `model.backend.shadow_prices.is_active` to verify tracking status

#### Command-Line Usage

When using the CLI tool, shadow prices specified in YAML configuration are automatically tracked and included in results with a `shadow_price_` prefix. For example, specifying `system_balance` produces `shadow_price_system_balance` in the saved results.

#### Python Usage

In Python, you have two approaches:

**Method 1 - Manual activation:**
```python
model = calliope.examples.national_scale()
model.build()
model.backend.shadow_prices.activate()
model.solve()
balance_price = model.backend.shadow_prices.get("system_balance").to_series()
```

**Method 2 - Via solve parameters:**
```python
model = calliope.examples.national_scale()
model.build()
model.solve(shadow_prices=["system_balance"])
balance_price = model.results.shadow_price_system_balance.to_series()
```

Note: Manual activation can be memory-intensive with the Pyomo backend.


---

## Examples and Tutorials

### Examples and Tutorials Overview

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/overview/

#### Purpose

This documentation section guides users through building and running Calliope models in Python. The tutorials use built-in example models to demonstrate core components needed for models of any complexity.

#### Featured Example Models

##### National Scale Example
Demonstrates fundamental Calliope functionality including:
- Supply technologies with optional storage buffers
- Storage technology implementation
- Technology and node group inheritance patterns

##### Urban Scale Example
Shows district-level modeling with:
- Conversion technologies (single and multiple output carriers)
- Revenue generation through carrier exports
- Template-based inheritance

##### MILP Example
Extends the urban scale model by introducing binary and integer decision variables, converting linear programming models to mixed-integer linear programming.

#### Additional Resources

The documentation includes tutorials on:
- Loading tabular data
- Running models in different operational modes
- Defining piecewise linear constraints
- Working with Calliope model and backend objects
- Implementing logging features

Each example is designed to be intentionally simple, isolating key Calliope concepts that users can combine to build more sophisticated energy system models.


---

### National Scale Example Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/national_scale/

#### Overview

This example demonstrates a basic energy system with two power supply technologies, demand at multiple nodes, battery storage capabilities, and transmission infrastructure linking locations.

The system comprises:
- **region1** and **region2** as primary demand centers
- **region1_1, region1_2, region1_3** as potential generation sites
- AC transmission connecting region1 to region2
- Local transmission from CSP sites to region1

#### Model Configuration

The configuration file establishes how Calliope interprets the model definition:

```yaml
config:
  init:
    name: National-scale example model
    calliope_version: 0.7.0
    subset:
      timesteps: ["2005-01-01", "2005-01-05"]
    broadcast_input_data: true
    mode: base
  build:
    ensure_feasibility: true
  solve:
    solver: cbc
    zero_threshold: 1e-10
```

Key settings include timestep subsetting, feasibility constraints, and solver specifications.

#### Data Loading via Tables

The model references external CSV files for time-varying and cost parameters:

```yaml
data_tables:
  time_varying_parameters:
    data: data_tables/time_varying_params.csv
    rows: timesteps
    columns: [comment, nodes, techs, parameters]
    drop: comment
  cost_parameters:
    data: data_tables/costs.csv
    rows: techs
    columns: [parameters, comment]
    drop: comment
    add_dims:
      costs: monetary
```

Cost data associates technologies with economic parameters like flow capacity costs and variable operational expenses.

#### Supply Technologies

**CCGT (Combined-cycle gas turbine)** represents a conventional supply option:
- Infinite source availability
- 50% conversion efficiency
- Maximum capacity: 40 MW system-wide, 30 MW at region1
- 25-year lifetime
- $750/kW capital cost

**CSP (Concentrating solar power)** is a complex renewable supply technology featuring:
- Time-series dependent source (per unit area)
- Integrated thermal storage with 614 MWh maximum
- 40% primary conversion efficiency
- 90% parasitic efficiency (internal losses)
- Multiple cost components for storage, collection area, and conversion capacity
- Deployed across three regional sites

#### Storage Technology

**Battery storage** at region2 provides temporal flexibility:
- 1 MW charge/discharge capacity
- 4:1 flow-to-storage capacity ratio
- Round-trip efficiency: ~90% (95% charging × 95% discharging)
- Zero self-discharge losses assumed

#### Demand and Transmission

**Power demand** technology receives time-series data from CSV files, with demand patterns specified per location.

**Transmission technologies** include:
- AC transmission between region1 and region2 with 85% efficiency
- Local transmission from CSP sites with zero loss and cost

#### Template-Based Definition

Templates reduce repetition in model definitions. The "free_transmission" template specifies local power transmission characteristics inherited by multiple region connections:

```yaml
templates:
  free_transmission:
    name: "Local power transmission"
    carrier_in: power
    carrier_out: power
    base_tech: transmission
```

#### Node Configuration

Nodes define geographic locations and their available technologies:

- **region1**: Demand, CCGT generation (30 MW maximum)
- **region2**: Demand, battery storage
- **region1_1, region1_2, region1_3**: CSP generation sites with specified coordinates

Geospatial coordinates (latitude/longitude) enable transmission distance calculations for cost estimation.


---

### Urban Scale Example Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/urban_scale/

#### Overview

This example demonstrates a district-level energy system with three buildings (nodes) connected through transmission networks. The system includes electricity supply, gas supply, solar generation, heat production, and demand management across multiple locations.

#### Model Architecture

The model comprises:
- **3 demand nodes** (X1, X2, X3) representing buildings
- **1 branching node** (N1) for heat network distribution
- **5 technologies** for energy generation and conversion
- **Transmission links** for electricity and heat distribution

#### Key Components

##### Configuration Structure

The model separates configuration from definition. The main `model.yaml` file references:
- Technology definitions (`techs.yaml`)
- Location specifications (`locations.yaml`)
- Scenario definitions (`scenarios.yaml`)

Configuration specifies solver options, timestep subsets, and math extensions rather than system data.

##### Data Loading

Time-series data loads from CSV files rather than YAML:
- **Demand profiles**: hourly electricity and heat requirements per building
- **PV resource**: solar availability with area-based scaling
- **Export pricing**: time-varying grid electricity values

The system defines data table mappings specifying rows (timesteps) and columns (nodes/technologies/carriers).

##### Technology Portfolio

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

##### Custom Mathematics

The CHP technology requires user-defined constraints to enforce simultaneous heat and electricity production with a fixed 0.8:1 ratio, since standard Calliope logic treats multiple outputs as alternatives rather than complementary products.

#### Node-Specific Features

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

#### Economic Modeling

The system captures:
- Capital costs for capacity installation
- Operational costs (fuel purchasing, maintenance)
- Revenue streams from electricity export
- Location-specific tariff variations
- Distance-dependent transmission costs

Interest rates and feasibility penalties configure the optimization objective function.


---

### Mixed Integer Linear Programming (MILP) Example Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/milp/

#### Overview

This example extends the Urban scale model by introducing binary and integer variables through an override applied in `scenarios.yaml`. The model demonstrates MILP functionality in Calliope, though convergence is slower with integer/binary variables. Commercial solvers like Gurobi or CPLEX are recommended for production use.

#### Model Configuration

The MILP override includes:
- Model name: "Urban-scale example model with MILP"
- Extra math modules: "milp" and "additional_math"
- Solver option: mipgap of 0.05

#### Key Components

##### Purchased Units

The CHP technology uses a unit-based capacity approach rather than continuous capacity ranges:

- **Cap method**: integer
- **Integer dispatch**: enabled
- **Purchased units max**: 4 units
- **Flow capacity per unit**: 300 (electricity)
- **Minimum output when operating**: 20% of maximum capacity

This discrete approach allows the solver to select how many CHP units to purchase, with each unit having identical capacity. The minimum operating capacity constraint only applies when output is non-zero, differing from standard LP models.

##### Purchase Cost

The boiler incorporates both unit-based and continuous capacity decisions:

- **Cap method**: integer
- **Purchased units max**: 1 (creating a binary variable)
- **Fixed purchase cost**: 2,000 (monetary units)
- **Variable cost**: 35 per capacity unit

A binary variable indicates whether to invest in the boiler. This fixed purchase cost captures infrastructure expenses independent of installed capacity.

##### Asynchronous Flow Control

Heat distribution pipes employ a constraint preventing simultaneous energy flow in opposite directions:

"The `async_flow_switch` binary variable ensures this phenomenon is avoided" by restricting a link to either transmission or reception per timestep, eliminating unphysical heat dumping.


---

### Loading Tabular Data (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/loading_tabular_data/

This documentation page covers methods for loading tabular data into Calliope models.

#### Defining Data in Text-Based YAML Format

Data can be defined directly in YAML configuration files, which serves as the foundational approach for specifying model parameters and attributes.

#### Defining Data in Tabular CSV Format

Calliope supports loading data from CSV (comma-separated values) files, enabling users to organize large datasets in spreadsheet-compatible formats. This approach is particularly useful for managing extensive parameter tables.

##### Loading Directly from In-Memory Dataframes

Data can be loaded from pandas dataframes that exist in Python memory, providing flexibility for programmatic data manipulation and integration with existing Python workflows.

##### Verifying Model Consistency

The documentation emphasizes the importance of validating that tabular data aligns with model structure and requirements before running optimization routines.

#### Mixing YAML and Data Table Definitions

Users can combine YAML-based definitions with tabular CSV data within a single model. This hybrid approach allows leveraging the strengths of both formats—YAML for configuration and structure, CSV for bulk data management.

#### Overriding Tabular Data with YAML

The system supports overriding values from CSV tables using YAML specifications. This feature enables exceptions and special cases to be handled without modifying underlying data tables.

**Note:** The page includes a downloadable Jupyter notebook demonstrating practical implementation of these data loading techniques.


---

### Running Models in Different Modes (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/modes/

This page documents how to execute Calliope models using three distinct operational modes: base, operate, and spores.

#### Running in 'base' mode

The base mode performs a full optimization to determine the optimal system design and operation. This mode designs new infrastructure and schedules operations across the entire time horizon simultaneously, making it suitable for long-term strategic planning scenarios.

#### Running in 'operate' mode

Operating mode uses fixed infrastructure from a previous base mode run and optimizes only the operational decisions (dispatch). This approach is valuable for analyzing how an already-designed system performs under different operational constraints or demand scenarios without redesigning infrastructure.

#### Running in 'spores' mode

SPORES (Spatially-explicit Pareto Optimal Renewable Energy Solutions) generates multiple diverse solutions that represent different trade-offs in the solution space. Rather than finding a single optimal solution, this mode explores the range of feasible alternatives, each optimized under different scoring criteria. This is particularly useful for understanding solution diversity and robust design choices.

#### Visualising results

Results from any mode can be visualized and compared. The documentation includes guidance on interpreting outputs through different scoring algorithms.

##### Using different scoring algorithms

Various scoring methods can be applied to evaluate and rank solutions across different objectives, allowing stakeholders to understand performance across multiple dimensions simultaneously.

#### Comparative Analysis

**'base' vs 'operate'**: Base mode optimizes complete system design plus operation, while operate mode fixes the infrastructure and optimizes only dispatch.

**'base' vs 'spores'**: Base mode identifies one optimal solution; spores mode explores multiple diverse alternatives across the Pareto frontier.

**Comparing 'spores' scoring algorithms**: Different scoring approaches reveal how solution preferences shift based on optimization criteria.


---

### Defining Piecewise Linear Constraints (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/piecewise_constraints/

This tutorial page covers how to define piecewise linear constraints in Calliope.

#### Related Topics in User-Defined Math

Calliope supports piecewise linear formulations through two distinct approaches:

- **Piecewise linear costs** — implementing non-linear cost functions that become more or less expensive with scale
- **Piecewise linear efficiency** — modeling efficiency curves with multiple segments
- **SOS2 piecewise linear costs** — using Special Ordered Sets of type 2 for economies-of-scale cost curves

#### Overview

Piecewise linear constraints are used to approximate non-linear relationships within the linear optimization framework. Calliope provides both constraint-based approaches (for upward-sloping convex curves) and SOS2 piecewise constraints (for more general non-convex curves).

See the User-Defined Math examples for complete YAML definitions:
- [Piecewise linear costs](udm_example_piecewise_linear_costs.md) — increasing marginal costs with capacity
- [Piecewise linear efficiency](udm_example_piecewise_linear_efficiency.md) — improving efficiency with output
- [SOS2 piecewise linear costs](udm_example_sos2_piecewise_linear_costs.md) — decreasing marginal costs (economies of scale)

**Note:** The page includes a downloadable Jupyter notebook demonstrating practical implementation of piecewise constraint techniques.


---

### The Calliope Model and Backend Objects (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/calliope_model_object/

This tutorial covers the Calliope model object and its backend, demonstrating how to work programmatically with model data and the optimization problem.

#### Overview

The `calliope.Model` object is the primary interface for interacting with Calliope models in Python. After building and solving, it provides access to:

- `model.inputs` — xarray Dataset of all input parameters and lookups
- `model.results` — xarray Dataset of all optimization results
- `model.backend` — Interface to the underlying optimization problem

#### Key Operations

##### Inspecting model data

```python
import calliope
model = calliope.examples.national_scale()
model.build()
model.solve()

### Access inputs
model.inputs.flow_cap_max

### Access results
model.results.flow_cap
model.results.flow_out
```

##### Working with the backend

The backend provides methods for:
- Inspecting optimization components (`model.backend.parameters`, `model.backend.variables`, etc.)
- Updating parameter values before resolving
- Fixing/unfixing decision variables
- Exporting the problem as an LP file

##### Post-solve analysis

Results are stored as xarray DataArrays with named dimensions (nodes, techs, carriers, timesteps, costs). Standard xarray and pandas operations apply:

```python
### Convert to pandas series, dropping NaN
model.results.flow_cap.to_series().dropna()

### Select specific dimensions
model.results.flow_out.sel(techs="ccgt")
```

**Note:** A downloadable Jupyter notebook demonstrates all key operations on the model and backend objects.


---

### Calliope Logging (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/calliope_logging/

This page provides guidance on configuring logging in Calliope to monitor model execution and debug issues.

#### Using Internal Calliope Functionality

Calliope includes built-in logging capabilities that can be leveraged to track model operations. The internal logging system allows you to access debugging information and execution details throughout the modeling process.

#### Adding Your Own Console Logging Handler

You can extend Calliope's logging by implementing custom console handlers. This approach enables you to capture and display log messages directly to the console with custom formatting and filtering based on your specific requirements.

To add a console logging handler, configure the Python logging module to work alongside Calliope's logger. This allows you to:

- Direct output to standard output or error streams
- Apply custom formatting to log messages
- Filter messages by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Control which components' messages appear in console output

#### Adding Your Own File Logging Handler

For persistent record-keeping, you can configure file-based logging handlers. This approach writes log messages to files for later analysis and troubleshooting.

File logging handlers allow you to:

- Save detailed execution logs to disk
- Maintain separate files for different logging levels
- Implement log rotation to manage file sizes
- Preserve historical data about model runs

Both console and file handlers can be customized to suit your analysis workflow and debugging needs.


---

## Reference

### YAML as Used in Calliope

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/yaml/

#### A Quick Introduction to YAML

Calliope's model configuration files use YAML, described as "a human friendly data serialisation standard for all programming languages." Configuration typically follows an `option: value` format.

##### Data Types

String values may be quoted with single or double quotes, though quotation marks are optional:

```yaml
option1: "text"
option2: 'text'
option3: text
```

YAML automatically interprets unquoted values:
- Unquoted numbers become numeric types (e.g., `1`, `1e6`, `1e-10`)
- `true` and `false` become booleans
- `.inf` and `.nan` become floating-point special values
- `null` becomes `None`

##### Comments

The `#` symbol marks comments. Strings containing `#` require quotation marks:

```yaml
### This is a comment
option1: "text with ##hashtags## needs quotation marks"
```

##### Lists and Dictionaries

Lists use either bracket notation or dash prefixes:

```yaml
key: [option1, option2]
### or
key:
  - option1
  - option2
```

Dictionaries use either curly braces or indented key-value pairs:

```yaml
key: {option1: value1, option2: value2}
### or
key:
  option1: value1
  option2: value2
```

Lists of dictionaries combine these patterns:

```yaml
key:
  - option1: value1
    option2: value2
  - option3: value3
    option4: value4
```

#### Calliope's Additional YAML Features

##### Abbreviated Nesting

Deeply nested structures can use dot notation:

```yaml
one.two.three: x
```

This equals:

```yaml
one:
  two:
    three: x
```

##### Relative File Imports

The `import:` directive includes other YAML files:

```yaml
import:
  - path/to/file_1.yaml
  - path/to/file_2.yaml
```

Imported and importing files cannot define the same option. The directive supports absolute or relative paths.

##### Reusing Definitions Through Templates

The `templates` section allows components to inherit common properties:

```yaml
templates:
  interest_rate_setter:
    cost_interest_rate:
      data: 0.1
      index: monetary
      dims: costs

techs:
  ccgt:
    flow_out_eff: 0.5
    template: interest_rate_setter
```

Templates can inherit from other templates, creating inheritance chains. Local values override template values.

##### Overriding One File with Another

Override sections can modify or extend existing data:

```yaml
### Initial configuration
one.two.three: x
four.five.six: x

### Override to apply
one.two.four: y
four.five.six: y
```

Use the special `_REPLACE_` key to entirely replace a nested dictionary instead of merging it.


---

### Command Line Interface Reference

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/cli/

#### Overview

The `calliope` command line tool provides utilities for managing and executing energy systems models within the Calliope framework.

#### Main Commands

##### calliope generate_runs

Generates a script to execute multiple models sequentially.

**Usage:** `calliope generate_runs [OPTIONS] MODEL_FILE OUT_FILE`

**Key Options:**
- `--kind TEXT`: Script type (bash, bsub, sbatch, or windows)
- `--scenarios TEXT`: Specify scenarios to run
- `--cluster_threads INTEGER`: Thread allocation for cluster jobs
- `--cluster_mem TEXT`: Memory specification for cluster jobs
- `--cluster_time TEXT`: Time limit for cluster jobs
- `--additional_args TEXT`: Extra arguments passed to `calliope run`
- `--override_dict TEXT`: Override parameters
- `--debug`: Enable debug output
- `--quiet`: Reduce verbosity
- `--pdb`: Interactive debugger on errors (with --debug)

##### calliope generate_scenarios

Creates scenario definitions from combinations of overrides.

**Usage:** `calliope generate_scenarios [OPTIONS] MODEL_FILE OUT_FILE [OVERRIDES]...`

**Key Options:**
- `--scenario_name_prefix TEXT`: Prefix for generated scenario names
- `--debug`: Enable debug output
- `--quiet`: Reduce verbosity
- `--pdb`: Interactive debugger on errors

##### calliope new

Initializes a new model based on built-in example templates.

**Usage:** `calliope new [OPTIONS] PATH`

**Key Options:**
- `--template TEXT`: Example model to use as template
- `--debug`: Enable debug output

##### calliope run

Executes a model from YAML configuration or pre-built NetCDF format.

**Usage:** `calliope run [OPTIONS] MODEL_FILE`

**Key Options:**
- `--scenario TEXT`: Specify scenario to run
- `--model_format TEXT`: Explicitly set format (yaml or netcdf)
- `--override_dict TEXT`: Override model parameters
- `--save_netcdf TEXT`: Export results to NetCDF
- `--save_csv TEXT`: Export results to CSV
- `--save_logs TEXT`: Save logging output
- `--save_lp TEXT`: Build and save optimization model (LP format)
- `--debug`: Enable debug output
- `--quiet`: Reduce verbosity
- `--profile`: Run performance profiling
- `--fail_when_infeasible / --no_fail_when_infeasible`: Exit with failure code on infeasible problems


---

### API Reference: Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/model/

#### Overview

The `calliope.Model` class is the primary interface for working with Calliope energy system models in Python. It inherits from `ModelStructure` and manages the complete lifecycle of optimization problems.

#### Class Definition

```python
calliope.Model(inputs, attrs, results=None, _reentry=True, **kwargs)
```

##### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `inputs` | `xr.Dataset` | Input dataset for the model | Required |
| `attrs` | `CalliopeAttrs` | Model attributes and properties | Required |
| `results` | `xr.Dataset \| None` | Results from a compatible prior model run | `None` |
| `_reentry` | `bool` | Whether to reinitialize math and configuration | `True` |
| `**kwargs` | | Initialization keyword arguments | `{}` |

#### Key Properties

- **`all_attrs`**: Returns all model attributes as a `CalliopeAttrs` object
- **`backend`**: The backend model interface
- **`config`**: Model configuration settings
- **`definition`**: Model definition
- **`inputs`**: Input dataset
- **`is_built`**: Boolean indicating if optimization problem is constructed
- **`is_solved`**: Boolean indicating if model has been solved
- **`math`**: Mathematical formulation
- **`name`**: The model's name
- **`results`**: Results dataset (empty until solved)
- **`runtime`**: Runtime information and timings

#### Core Methods

##### `build(force=False, **kwargs)`

Constructs the optimization problem in the chosen backend interface. Set `force=True` to overwrite existing results.

##### `solve(force=False, warmstart=False, **kwargs)`

Solves the built optimization problem. The `warmstart` parameter can improve solution time for similar sequential problems, though it doesn't work with all solvers (CBC, GLPK).

**Raises:**
- `ModelError` if problem not yet built
- `ModelError` if results exist and `force` is not True
- `ModelError` for "operate" mode preprocessing conflicts

##### `run(force_rerun=False)`

Deprecated method combining `build()` and `solve()`. Use these methods separately instead.

##### `info()`

Returns a string summarizing the model name and size, including the number of valid node:tech:carrier combinations.

##### `to_csv(path, dropna=True, allow_overwrite=False)`

Exports inputs and results to CSV files. Setting `dropna=True` produces smaller files by removing NaN values.

##### `to_netcdf(path)`

Exports inputs, results, and attributes to a single NetCDF file.

##### `dump_all_attrs()`

Returns all class attributes as a single dictionary from the Pydantic model.


---

### API Reference: Backend Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/backend_model/

#### Overview

The `BackendModel` class is an abstract base class that serves as the interface between Calliope's mathematical formulation and external optimization solvers. It manages the construction and manipulation of optimization problems.

#### Class Definition

```python
calliope.backend.backend_model.BackendModel(inputs, math, build_config, instance)
```

**Base Classes:** `BackendModelGenerator`, `Generic[T]`

##### Parameters

| Name | Type | Description |
|------|------|-------------|
| `inputs` | `xr.Dataset` | Calliope model data |
| `math` | `AttrDict` | Calliope math specifications |
| `build_config` | `Build` | Build configuration options |
| `instance` | `T` | Interface model instance |

#### Key Properties

- **config:** Build configuration settings
- **inputs:** Processed input dataset with lookups and parameters
- **math:** Mathematical formulation definitions
- **objective:** Active optimization objective name
- **variables:** Array of decision variables
- **constraints:** Array of constraint equations
- **parameters:** Array of input parameters
- **global_expressions:** Computed expressions combining variables/parameters
- **objectives:** Defined objective functions
- **lookups:** Input lookup tables
- **piecewise_constraints:** Piecewise linear constraint definitions
- **shadow_prices:** Dual values from constraint relaxation
- **has_integer_or_binary_variables:** Boolean flag indicating MILP problem

#### Core Methods

##### Building the Optimization Problem

- **add_optimisation_components():** Parse math and build full optimization problem
- **add_variable():** Create decision variable with bounds
- **add_parameter():** Add input parameter with default values
- **add_constraint():** Define constraint equations
- **add_global_expression():** Create arithmetic expressions
- **add_objective():** Specify objective function
- **add_lookup():** Register lookup array
- **add_piecewise_constraint():** Build piecewise linear constraints

##### Accessing Components

- **get_variable():** Extract decision variable array
- **get_parameter():** Retrieve parameter values
- **get_constraint():** Access constraint definitions with optional evaluation
- **get_global_expression():** Fetch computed expressions
- **get_objective():** Retrieve objective specifications
- **get_piecewise_constraint():** Access piecewise constraint objects
- **get_variable_bounds():** Extract upper/lower bounds

##### Model Manipulation

- **update_input():** Modify parameter or lookup values
- **update_variable_bounds():** Change variable min/max bounds
- **fix_variable():** Convert variable to parameter with current value
- **unfix_variable():** Restore fixed variable to decision status
- **set_objective():** Switch active optimization objective
- **delete_component():** Remove component from model

##### Utilities

- **load_results():** Extract optimal solution values after solving
- **to_lp():** Export problem in LP format for debugging
- **verbose_strings():** Enhance string representations with index coordinates
- **log():** Log messages with formatted component information

#### Component Validation

The `valid_component_names` property returns all recognized component identifiers in the model, supporting validation during expression parsing.


---

### API Reference: Helper Functions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/helper_functions/

#### Overview

Helper functions process data in Calliope's mathematical `where` and `expression` strings. Each function has a `NAME` property defining its usage in math expressions.

#### Core Helper Functions

##### DefaultIfEmpty
**Purpose:** "Fill empty (NaN) items in arrays."

**Allowed In:** `expression`

**Usage Example:**
```python
default_if_empty(flow_cap, 0)
```
Returns an array with NaN values filled using the provided default, or a scalar default if the variable doesn't exist in the model.

---

##### Defined
**Purpose:** "Find all items of one dimension that are defined in an item of another dimension."

**Allowed In:** `where`

**Usage:**
```python
defined(techs=[tech1, tech2], within=nodes, how=any)
```
Checks whether nodes define specific technologies. The `how` parameter accepts `any` or `all` to determine matching logic.

---

##### GetValAtIndex
**Purpose:** "Getter functionality for obtaining values at specific integer indices."

**Allowed In:** `expression`, `where`

**Usage:**
```python
get_val_at_index(timesteps=0)  # First timestep
get_val_at_index(timesteps=-1) # Last timestep
```

---

##### GroupDatetime
**Purpose:** "Apply a summation over a datetime group on a datetime dimension."

**Allowed In:** `expression`

**Usage:**
```python
group_datetime(flow_in, timesteps, date)
group_datetime(flow_in, timesteps, month)
```
Aggregates timestep data by date, month, or other datetime periods.

---

##### GroupSum
**Purpose:** "Apply a summation over an array grouping."

**Allowed In:** `expression`

**Usage:**
```python
group_sum(flow_out, power_plant_groups, emission_groups)
```
Sums array values according to a grouping dimension.

---

##### ReduceCarrierDim
**Purpose:** "Sum over the carrier dimension in math components."

**Allowed In:** `expression`

**Usage:**
```python
reduce_carrier_dim(array, 'in')
reduce_carrier_dim(array, 'out')
```
Reduces arrays by summing across the carrier dimension based on flow direction.

---

##### Roll
**Purpose:** "Roll (shift) items along ordered dimensions."

**Allowed In:** `expression`

**Usage:**
```python
roll(array, timesteps=1)
```
Shifts array data while maintaining coordinate labels.

---

##### SelectFromLookupArrays
**Purpose:** "N-dimensional indexing functionality."

**Allowed In:** `expression`

Applies vectorized indexing across multiple dimensions using lookup arrays.

---

##### Sum
**Purpose:** "Apply a summation over dimension(s) in math expressions."

**Allowed In:** `expression`

**Usage:**
```python
sum(array, over='carriers')
sum(array, over=['nodes', 'techs'])
```
NaN values are ignored; returns NaN if all values along a dimension are NaN.

---

##### SumNextN
**Purpose:** "Sum the next N items in an array."

**Allowed In:** `expression`

Performs rolling-window summation, ideal for ordered data like timeseries.

---

##### Where & WhereAny
**Purpose:** Conditional filtering in mathematical expressions.

**Allowed In:** `where`, `expression`

Filter constraints and expressions based on data availability conditions.

---

#### ParsingHelperFunction (Base Class)

All helper functions inherit from `ParsingHelperFunction`, which defines:

- **ALLOWED_IN:** List of contexts (expression/where) where function is valid
- **NAME:** String identifier for math expressions
- **ignore_where:** Whether to bypass where-array filtering
- **as_array():** Returns n-dimensional xarray output
- **as_math_string():** Generates LaTeX math representation


---

### API Reference: Example Models

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/example_models/

#### Overview

The `calliope.examples` module provides built-in example models that can be loaded directly into a Python session for learning and testing purposes.

#### Available Example Models

##### national_scale()
"Returns the built-in national-scale example model." Loads from `national_scale/model.yaml`.

##### urban_scale()
"Returns the built-in urban-scale example model." Loads from `urban_scale/model.yaml`.

##### milp()
A variant of the urban-scale model with mixed-integer linear programming constraints enabled.

##### operate()
The urban-scale example configured to run in operate mode.

##### operate_milp()
Combines operate mode with MILP constraints on the urban-scale model.

##### time_clustering()
The national-scale example with time clustering applied.

##### time_resampling()
The national-scale example with time resampling applied.

#### Usage Pattern

All functions accept flexible arguments and keyword arguments (`*args, **kwargs`), allowing customization when loading models. Functions typically call `read_yaml()` to load model configuration files from the examples directory.


---

### API Reference: AttrDict

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/attrdict/

#### Overview

`calliope.attrdict.AttrDict` is an extended dictionary class that subclasses Python's built-in `dict` with attribute-style key access. It supports nested key operations and provides methods for working with YAML data.

#### Basic Usage

Create an AttrDict and access values as attributes:

```python
d = AttrDict({'a': 1, 'b': 2})
d.a == 1  # True
```

Nested dictionaries are automatically converted:

```python
d = AttrDict({'a': 1, 'b': {'x': 1, 'y': 2}})
d.b.x == 1  # True
```

#### Methods

##### `as_dict(flat=False)`
Returns the AttrDict as a pure Python dictionary. When `flat=True`, returns a flattened version; otherwise returns nested dictionaries.

##### `as_dict_flat()`
Returns a completely flat dictionary with dot-notation keys.

##### `as_dict_nested()`
Converts the AttrDict to a pure dict, recursively converting nested AttrDicts and those within lists.

##### `copy()`
Creates a copy that returns an AttrDict (not a regular dict).

##### `del_key(key)`
Deletes a key, with support for nested keys using dot notation (e.g., `"foo.bar"`).

##### `get_key(key, default=_MISSING)`
Retrieves values using dot notation for nested access. Supports optional default values for missing keys.

##### `init_from_dict(d)`
Initializes the AttrDict from a dictionary, converting nested dicts to AttrDicts recursively.

##### `keys_nested(subkeys_as='list')`
Returns all keys including nested ones. With `subkeys_as='list'` (default), returns `['a', 'b.b1', 'b.b2']`. With `subkeys_as='dict'`, returns nested structure `['a', {'b': ['b1', 'b2']}]`.

##### `set_key(key, value)`
Sets values using dot notation for nested keys, automatically creating intermediate AttrDicts as needed.

##### `union(other, allow_override=False, allow_replacement=False)`
Merges another AttrDict into the current one. By default raises `KeyError` if keys already exist. Set `allow_override=True` to permit overwrites. The `allow_replacement` parameter enables the `"_REPLACE_"` special key for replacing entire sub-dictionaries.


---

### API Reference: Postprocess

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/postprocess/

#### capacity_factor()

**Function Signature:**
```python
capacity_factor(results: xr.Dataset, model_data: xr.Dataset, systemwide=False) -> xr.DataArray
```

**Purpose:** Computes capacity factors from model results.

**Key Details:**
- Handles both operating mode (where `flow_cap` is an input parameter) and optimization mode (where it's a result variable)
- For system-wide calculations, the function applies timestep weights to ensure higher-weighted periods influence results proportionally
- Returns a DataArray containing capacity factor values

**Implementation Note:** When `systemwide=True`, the calculation aggregates production across timesteps and nodes while accounting for their respective weights.

---

#### systemwide_levelised_cost()

**Function Signature:**
```python
systemwide_levelised_cost(results: xr.Dataset, model_data: xr.Dataset, total: bool = False) -> xr.DataArray
```

**Purpose:** Calculates levelized costs across the entire system.

**Parameters:**
- `results`: Model optimization results
- `model_data`: Input data and parameters
- `total`: When `False`, returns per-technology costs; when `True`, returns aggregate system cost

**Important Implementation Details:**
The function accounts for timestep weighting asymmetrically—costs already incorporate weights in constraints, but production metrics require manual scaling for consistency. This weighting adjustment occurs solely during computation and doesn't modify underlying result data.

**Return Value:** A DataArray indexed by technologies, carriers, and cost types (or carriers and costs when `total=True`).


---

### API Reference: Exceptions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/exceptions/

#### Overview

The `calliope.exceptions` module handles exceptions and warning management for the Calliope modeling framework.

#### Exception Classes

##### BackendError
Inherits from Python's base `Exception` class. This exception should be raised when issues occur during backend processing operations.

##### BackendWarning
Inherits from Python's base `Warning` class. Use this warning type to flag potential backend processing issues where execution can continue despite the problem.

##### ModelError
Inherits from Python's base `Exception` class. Raise this exception when encountering problems with model formulation or input data that prevent further execution.

##### ModelWarning
Inherits from Python's base `Warning` class. This warning signals possible model issues but allows execution to proceed.

#### Functions

##### warn()
```python
warn(message: str, _class: type[Warning] = ModelWarning)
```
Raises the specified type of warning with formatted output.

##### print_warnings_and_raise_errors()
```python
print_warnings_and_raise_errors(
    warnings=None,
    errors=None,
    during='model processing',
    bullet=' * '
)
```

Processes collections of warnings and errors with formatted output.

**Key features:**
- Prints warnings without stopping execution
- Raises `ModelError` if errors are present
- Supports both list and nested dictionary formats
- Simple lists display as bullet points
- Dictionary structures create nested bullet hierarchies

**Parameters:**
- `warnings`: String list or dict of lists; None/empty lists print nothing
- `errors`: String list or dict of lists; None/empty lists raise nothing
- `during`: Contextual phase descriptor (default: "model processing")
- `bullet`: Bullet character style (default: " * ")


---

### API Reference: Logging

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/logging/

#### Overview

The `calliope.util.logging` module provides functionality for creating the Calliope logger object and applying logging tools and features throughout the system.

#### LogWriter Class

`LogWriter(logger, level, strip=False)`

A custom logger class designed to redirect solver outputs and prevent message duplication.

##### Attributes
- **logger**: The logger instance to write to
- **level**: The logging level for messages
- **strip**: Boolean flag to strip whitespace from messages

##### Methods

###### `write(message)`
Saves a message to the logger. Messages are filtered to exclude newline characters, and whitespace is optionally stripped based on configuration.

###### `flush()`
A placeholder method reserved for future flush functionality.

#### Functions

##### `log_time()`

Simultaneously logs the time of a Calliope event to both a dictionary and the logger.

**Parameters:**
- `logger`: Logger instance for recording the time
- `timings`: Dictionary storing model timing data
- `identifier`: Key for the event in the timings dictionary
- `comment`: Optional description (defaults to identifier)
- `level`: Logging level, defaulting to "info"
- `time_since_solve_start`: When enabled, appends elapsed time since solver initiation

**Returns:** POSIX timestamp of the logged event

##### `set_log_verbosity()`

Configures logging verbosity and sets up the root logger for console output with timestamp formatting.

**Parameters:**
- `verbosity`: Logging level as string or integer
- `include_solver_output`: Enables DEBUG logging for backend solver output (default: True)
- `capture_warnings`: Routes Python warnings through the logger (default: True)

##### `setup_root_logger()`

Initializes the Calliope root logger with proper formatting, handler configuration, and verbosity settings.

**Parameters:**
- `verbosity`: Logging level specification
- `capture_warnings`: Integrates Python warnings into logging system (default: True)

**Returns:** Configured logging.Logger instance


---

### Model Configuration Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/config_schema/

Calliope's configuration class defines all options used when initializing and running a model.

#### Init Configuration

**Basic Settings:**
- `name`: Model name (string or null)
- `calliope_version`: Framework version intended for the model (string or null)
- `broadcast_input_data`: Whether to broadcast single YAML data entries across all index items (boolean, default: false)

**Dimension Management:**
- `subset`: Define dimension subsets as arrays of strings, integers, or numbers
- `resample`: Configure dimension resampling settings
- `time_cluster`: Reference an input data array name for timeseries clustering

**Data Format Settings:**
- `datetime_format`: Timestamp format for timeseries data (default: "ISO8601")
- `date_format`: Datestamp format (default: "ISO8601")
- `distance_unit`: Transmission link distance unit - either "km" or "m" (default: "km")

**Optimization Settings:**
- `mode`: Running mode - "base", "operate", or "spores" (default: "base")
- `extra_math`: List of additional math entries to apply
- `math_paths`: Define custom math file locations
- `pre_validate_math_strings`: Scan math definitions for errors at initialization (boolean, default: false)

#### Build Configuration

- `backend`: "pyomo" or "gurobi" (default: "pyomo")
- `ensure_feasibility`: Include variables for unmet demand debugging (boolean, default: false)
- `objective`: Internal objective function name (default: "min_cost_optimisation")

**Operate Mode Options:**
- `window`: Rolling window as pandas frequency string (default: "24h")
- `horizon`: Rolling horizon, must be >= window (default: "48h")

#### Solve Configuration

- `postprocessing_active`: Run postprocessing functions after solving (boolean, default: true)
- `save_logs`: Directory path for optimization logs (path or null)
- `shadow_prices`: Array of constraint names for shadow price calculation
- `solver`: Solver name with Pyomo interface (default: "cbc")
- `solver_io`: Solver interface option (string or null)
- `solver_options`: Key-value pairs for solver configuration
- `zero_threshold`: Postprocessing threshold for rounding artifacts (default: 1e-10)

**SPORES Mode Options:**
- `scoring_algorithm`: Update algorithm - "integer", "relative_deployment", "random", or "evolving_average"
- `number`: Iterations after initial run (integer, default: 3)
- `save_per_spore_path`: Directory for individual SPORE results (path or null)
- `use_latest_results`: Continue from existing results (boolean, default: false)
- `tracking_parameter`: Input parameter for technology filtering (string or null)
- `score_threshold_factor`: Capacity threshold factor for scoring (number, default: 0.1, minimum: 0)


---

### Data Table Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/data_table_schema/

The data table schema defines how tabular data files are loaded and processed in Calliope models.

#### Required Parameters

**`data`** _(string, required)_: File path to the data source, either absolute or relative to the model configuration file location.

#### Optional Parameters

**`rows`**: Specifies dimension names organized row-wise in the data file. Each name should correspond to a column containing index items, positioned to the left of data columns. Accepts a string, array of strings, or null (default).

**`columns`**: Specifies dimension names organized column-wise in the data file. Each name should correspond to a row containing index items, positioned above data rows. Accepts a string, array of strings, or null (default).

**`select`**: Filters one or more index items from a dimension before other transformations. Applied before `drop` and `add_dims` operations. Accepts an object mapping dimension names to values or null (default).

**`drop`**: Removes irrelevant rows and/or columns (e.g., comments, metadata, unit labels). Can be used to eliminate dimensions that are later reintroduced via `add_dims`. Accepts a string, array of strings, or null (default).

**`add_dims`**: Introduces data dimensions after loading. Useful for assigning identical values to multiple parameters or adding constant dimensions. Accepts an object mapping dimension names to values/arrays or null (default).

**`rename_dims`**: Maps data table dimension names to corresponding Calliope dimension names. For example: `{"time": "timesteps"}`. Accepts an object or null (default).

All string identifiers must match the pattern `^[^_^\d][\w]*$` (beginning with a letter or underscore, followed by word characters).


---

### Model Definition Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/model_schema/

This page documents the schema for Calliope model definitions, which consist of three primary components:

#### Data Definitions

Data definitions comprise a dictionary where keys must match the pattern `^[^_^\d][\w]*$` (starting with a letter or underscore, followed by word characters).

Values can be:
- Primitive types (string, boolean, integer, number)
- Indexed data objects containing:
  - **`data`**: Parameter values (single value or array matching index length)
  - **`dims`**: Model dimension(s) referenced
  - **`index`**: Dimension members to apply values to
- Null values

#### Data Tables

Data tables enable loading external data files with configuration for:

- **`data`** (required): File path, relative to model config location
- **`rows`**: Dimension names defined row-wise in the spreadsheet
- **`columns`**: Dimension names defined column-wise
- **`select`**: Filter specific index items before processing
- **`drop`**: Remove irrelevant rows/columns
- **`add_dims`**: Introduce dimensions after loading
- **`rename_dims`**: Map data table dimensions to Calliope equivalents

#### Nodes

Nodes represent locations in the energy system. Each node can:

- Include latitude/longitude (WGS84/EPSG4326 coordinates)
- Toggle active status (default: true)
- Reference technologies present at that location
- Override technology-specific parameters

#### Technologies

Technologies represent energy system components (generation, storage, demand, conversion, transmission). Each tech includes:

- Active status toggle (default: true)
- Base technology classification (supply, demand, conversion, storage, transmission)
- Indexed parameter data with flexible dimensionality


---

### Model Math Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/math_schema/

#### Overview

The Model Math Schema defines the mathematical programming components available for optimization in Calliope. It supports partial definitions that can be layered on top of one another (for example, combining 'base' and 'operate' math).

#### Main Components

##### Dimensions
Defines the model's dimension dictionary with named dimensions. Each dimension can specify:
- **title**: Long name for visualization
- **description**: Verbose explanation
- **active**: Boolean to enable/disable during build
- **dtype**: Data type (string, datetime, date, float, integer)
- **ordered**: Whether item order is meaningful (e.g., chronological)
- **iterator**: Name for LaTeX math formulation

##### Parameters
Configures input parameters with properties including:
- **default**: Fallback value if not specified in data
- **resample_method**: Aggregation approach (mean, sum, first)
- **unit**: Parameter units (kW, m, kg, etc.)

##### Lookups
Defines lookup arrays with support for:
- **dtype**: Data type specification
- **one_of**: Constraint values to specific items
- **pivot_values_to_dim**: Converts lookup values into a new dimension with boolean indexing

##### Variables
Specifies decision variables for the optimization problem with:
- **foreach**: Dimensions over which the variable is built
- **where**: Conditional existence criteria
- **domain**: Real (continuous) or integer values
- **bounds**: Upper and lower limits (min/max)

##### Global Expressions
Reusable combinations of parameters and variables used across constraints, objectives, and other expressions. Supports:
- **equations**: Mathematical relationships
- **sub_expressions**: Component terms
- **slices**: Set items or helper function calls

##### Constraints
Mathematical restrictions on the optimization problem, structured similarly to global expressions with equations, sub-expressions, and slices.

##### Piecewise Constraints
Specialized constraints linking x-axis and y-axis decision variables at specified breakpoints using:
- **x_expression** and **y_expression**: Variable references
- **x_values** and **y_values**: Parameter data indexed over breakpoints

##### Objectives
The optimization target function (only one active per solve). Must specify:
- **sense**: Minimize or maximize

##### Checks
Input data validation with:
- **where**: Condition to evaluate
- **message**: Error/warning text
- **errors**: Response type (raise or warn)


---

## Other

### Migrating from v0.6 to v0.7

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/migrating/

This guide documents major user-facing changes for upgrading Calliope models from v0.6 to v0.7.

#### Changes

##### Flat Technology Definition

The nested structure separating `essentials`, `constraints`, and `costs` has been flattened. All technology parameters are now defined at the same level.

**v0.6 approach:**
```yaml
ccgt:
  essentials:
    name: 'Combined cycle gas turbine'
    parent: supply
    carrier_out: power
  constraints:
    energy_eff: 0.5
  costs:
    monetary:
      energy_cap: 750
```

**v0.7 approach:**
```yaml
ccgt:
  name: 'Combined cycle gas turbine'
  base_tech: supply
  carrier_out: power
  flow_out_eff: 0.5
  cost_flow_cap:
    data: 750
    index: monetary
    dims: costs
```

##### Data Tables Replace file=/df= References

Timeseries data loading via `file=` or `df=` parameters is replaced with a top-level `data_tables` section for loading CSV and similar tabular data.

**v0.6 approach:**
```yaml
techs:
  demand_tech:
    constraints:
      resource: file=demand_file.csv
      force_resource: true
```

**v0.7 approach:**
```yaml
data_tables:
  demand_data:
    data: demand_file.csv
    rows: timesteps
    columns: nodes
    add_dims:
      techs: demand_tech
      parameters: sink_equals
```

##### Demand Values Now Positive

Demand data must use strictly positive numbers (previously negative). The `carrier_con` decision variable is now called `flow_in`.

##### Split model.run() Into Two Steps

The single `model.run()` method is replaced with:
- `model.build()` - Creates optimization problem components
- `model.solve()` - Sends problem to solver and generates results

##### Configuration Reorganization

Model configuration now splits into stages:
- `config.init` - Applied during model creation
- `config.build` - Applied when building the optimization problem
- `config.solve` - Applied when solving

**v0.6 approach:**
```yaml
config:
  model:
    subset_time: ["2005-01", "2005-02"]
  run:
    solver: cbc
```

**v0.7 approach:**
```yaml
config:
  init:
    subset:
      timesteps: ["2005-01", "2005-02"]
  solve:
    solver: cbc
```

##### Locations → Nodes

`locations` has been renamed to `nodes` for clarity and to avoid conflicts with pandas/xarray `.loc` accessors.

##### Parent and Tech Groups → Base Tech and Templates

- `parent` is renamed `base_tech` (fixed to one of: demand, supply, conversion, transmission, storage)
- `tech_groups` is replaced with `templates` for more flexible reuse

**v0.6 approach:**
```yaml
tech_groups:
  supply_interest_rate:
    essentials:
      parent: supply
    costs:
      monetary:
        interest_rate: 0.1
techs:
  supply_tech:
    essentials:
      parent: supply_interest_rate
```

**v0.7 approach:**
```yaml
templates:
  common_interest_rate:
    cost_interest_rate:
      data: 0.1
      index: monetary
      dims: costs
techs:
  supply_tech:
    base_tech: supply
    template: common_interest_rate
```

##### Transmission Links in Techs

The top-level `links` key no longer exists. Transmission technologies are defined in `techs` with `link_from`/`link_to` keys.

**v0.6 approach:**
```yaml
techs:
  ac_transmission:
    essentials:
      parent: transmission
links:
  X1,X2:
    techs:
      ac_transmission:
```

**v0.7 approach:**
```yaml
techs:
  x1_to_x2_ac_transmission:
    link_from: X1
    link_to: X2
    base_tech: transmission
```

##### Parameter Renaming

Improvements to parameter clarity:
- `energy`/`carrier` → `flow` (e.g., `energy_cap_max` → `flow_cap_max`)
- `prod`/`con` → `out`/`in` (e.g., `carrier_prod` → `flow_out`)
- `resource` → `source_use` or `sink_use`
- `resource_area` → `area_use`
- `om_prod`/`om_con` → `cost_flow_out`/`cost_flow_in`
- `exists` → `active`

##### Force Resource Changes

The binary `force_resource` trigger is replaced with parameters `source_use_equals` and `sink_use_equals` to directly specify required resource flows.

##### Units and Purchase Consolidation

`units` and `purchased` are merged into a single `purchased_units` decision variable.

##### Investment Cost Split

`cost_investment` is split into:
- `cost_investment_annualised` - Annualized capital investment
- `cost_operation_fixed` - Fixed operational and maintenance costs

##### Explicit MILP and Storage Activation

Mixed-integer features now require explicit activation:
- Set `config.build.extra_math: ["milp"]` to enable integer variables
- Set `cap_method: integer` on specific technologies
- Use `include_storage: true` to add storage buffers to non-storage technologies

**v0.6 approach:**
```yaml
techs:
  supply_tech:
    constraints:
      units_max: 4
```

**v0.7 approach:**
```yaml
config:
  build:
    extra_math: ["milp"]
techs:
  supply_tech:
    units_max: 4
    cap_method: integer
```

##### Data Structure Changes

Concatenated `loc::tech` and `loc::tech::carrier` sets are removed. Components are now indexed separately over `nodes`, `techs`, and `carriers`.

**v0.6 access:**
```python
model.inputs.energy_cap_max.loc[{"loc_techs": "X::pv"}]
```

**v0.7 access:**
```python
model.inputs.flow_cap_max.loc[{"nodes": "X", "techs": "pv"}]
```

##### Node Coordinates

Geographic coordinates use direct `latitude`/`longitude` keys instead of nested `coordinates`.

**v0.6 approach:**
```yaml
nodes:
  X1:
    coordinates:
      lat: 1
      lon: 2
```

**v0.7 approach:**
```yaml
nodes:
  X1:
    latitude: 1
    longitude: 2
```

##### Distance Units Default

Distance calculations now default to kilometres instead of metres. Set `config.init.distance_unit: m` to use metres.

##### Operate Mode Inputs

In operate mode, directly specify capacity parameters (e.g., `flow_cap: 1`) instead of `_max` constraints. Operating windows and horizons use Pandas time frequencies (e.g., `12H`) rather than integer timesteps.

##### Per-Technology Cyclic Storage

Cyclic storage moves from global configuration to per-technology parameters:

**v0.6 approach:**
```yaml
run:
  cyclic_storage: true
```

**v0.7 approach:**
```yaml
techs:
  storage_tech:
    base_tech: storage
    cyclic_storage: true
```

#### Removals

##### Equals Constraints

Parameters like `energy_cap_equals` are removed. Set `_min` and `_max` to the same value to achieve fixed parameters.

##### Cartesian Coordinates

X/Y coordinates no longer supported; use `latitude`/`longitude` instead.

##### Comma-Separated Node Definitions

Defining multiple nodes via comma separation (e.g., `node1,node2,node3:`) is no longer allowed. Use `templates` for reuse.

##### Supply Plus and Conversion Plus

These base classes are removed:
- Replace `supply_plus` with `supply` + `include_storage: true`
- Replace `conversion_plus` with `conversion` using lists for `carrier_in`/`carrier_out`

##### Carrier Key

The `carrier` alias is removed; explicitly use `carrier_in` and `carrier_out`.

##### Carrier Tiers and Ratios

Complex carrier tier and ratio functionality is removed. Implement equivalent behavior through custom math or flow efficiency indexing.

##### Group Constraints

Group constraints removed; reimplemented as user-defined math snippets.

##### Configuration Removals

- `timeseries_data_path` - Use paths relative to `model.yaml` or absolute paths
- `run.relax_constraint` - Use user-defined math instead
- `model.file_allowed` - All parameters can be time-indexed
- `model.random_seed` and time clustering options

##### Plotting

Visualization functionality moved to [Calligraph](https://calligraph.readthedocs.io/), a separate tool.

##### Time Clustering

Simplified to date-matching only. Use external tools for advanced clustering.

#### Additions

##### Storage Buffers for All Base Classes

Any technology base class can now include `include_storage: true` for intertemporal storage capability.

##### Multiple and Mixed Carriers

All base classes support multiple carriers and different inflow/outflow carriers, enabling complex technology definitions without `conversion_plus`.

##### Templates for Nodes

The new `templates` feature replaces comma-separated node grouping.

**Achieving repeated node configuration:**
```yaml
templates:
  standard_tech_list:
    techs:
      battery:
      demand_electricity:
      ccgt:
nodes:
  region1:
    template: standard_tech_list
  region2:
    template: standard_tech_list
```

##### Separate Inflow/Outflow Efficiencies

Parameters `flow_in_eff` and `flow_out_eff` enable different charge/discharge or input/output efficiencies.

##### Carrier-Indexed Capacities and Efficiencies

Capacity and efficiency parameters are indexed over carriers, allowing per-carrier constraints:

```yaml
techs:
  dual_fuel_plant:
    base_tech: conversion
    carrier_in: [coal, biofuel]
    carrier_out: electricity
    flow_cap_max:
      data: [100, 80]
      index: [coal, biofuel]
      dims: carriers
```

##### Data Definitions Outside Nodes/Techs

Top-level `data_definitions` key allows defining parameters independent of nodes and technologies.

##### Arbitrary Dimension Indexing

Parameters can be indexed over custom dimensions for advanced modeling.

##### Non-Timeseries Tabular Data

Expanded `data_tables` support for loading any tabular data, not just timeseries.

##### YAML-Based Math Syntax

Complete math formulation redesign using readable YAML, enabling custom math and piecewise constraints.


---

### Contributing to Calliope

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/contributing/

#### Overview

Calliope welcomes contributions from volunteers across various institutions. The project offers multiple ways to get involved, from reporting issues to submitting code changes.

#### Ways to Contribute

**Reporting Issues:**
- Report bugs through the GitHub issue tracker with a bug report template
- Document missing or inconsistent information in the documentation
- Request new features or improvements

**Community Engagement:**
- Ask questions and connect with the community on the discussion board
- Review the "good first issues" list for beginner-friendly tasks
- Check GitHub milestones and projects to understand development direction

#### Development Setup

##### Environment Installation

Using mamba (recommended):

1. Install Mambaforge for your operating system
2. Clone the repository: `git clone git@github.com:calliope-project/calliope.git`
3. Create the development environment with all dependencies
4. Activate the environment and install Calliope in editable mode
5. Install the IPython kernel for documentation testing

For pip users, install with the `dev` option: `pip install -e '.[dev]'`

##### Development Tools

**pre-commit:** Runs automatic checks on each commit:
- Prevents staging large files
- Lints Python files
- Formats code to PEP8 standards

**pytest:** Run unit and integration tests with coverage reporting

#### Making Changes

##### Workflow

1. Fork the main repository on GitHub
2. Clone your fork locally
3. Create a feature branch to isolate your changes
4. Make edits and add tests covering your contribution
5. Run tests: `pytest -m "not time_intensive" --no-cov` for faster feedback
6. Commit changes with clear messages
7. Push to your fork and open a pull request

##### Testing Strategy

- Add tests for all new functionality
- Run `pytest` from the repository root
- Use `-x` flag to stop at first failure
- Use `--pdb` flag for debugging
- Integration tests can be skipped with `-m "not time_intensive"`

#### Pull Request Requirements

Before submitting, ensure you have:

1. **Test coverage** – Tests prevent future regressions and validate new functionality
2. **Documentation updates** – Added features should be documented in the docs directory
3. **Changelog entry** – Brief description prepended with `fixed`, `changed`, `added`, or `new`
4. **Code coverage** – Maintained or improved overall test coverage percentage

#### Code Standards

**Style Guide:** Follow PEP8 with ruff for formatting and linting

**Docstrings:** Use Google-style docstrings for all modules, classes, and methods

**Line Length:** Maximum 88 characters (configured in `pyproject.toml`)

**Automation:** Run `pre-commit install` to automatically format code on each commit

#### Release Process

##### Creating a Release

1. Create a release branch
2. Update version in `src/calliope/_version.py`
3. Update `CHANGELOG.md` with final version and date
4. Submit PR titled `Release vX.Y.Z` for testing
5. Merge and tag commit with version
6. Create GitHub release with user-facing changelog items

##### Post-Release

1. Add "Unreleased" section to changelog
2. Bump version to next patch with `.dev` suffix
3. Update example model version numbers

#### Licensing

Contributors agree that their work is original and licensed under the Apache 2.0 license, consistent with Calliope's licensing terms.


---

### Calliope Version History

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/version_history/

#### Latest Release: 0.7.0.dev7 (2025-09-05)

##### User-facing changes

**Performance & Structure:**
- "ModelDataFactory is no longer run twice during startup, resulting in faster initialisation"
- Model attributes are now stored directly on the model object rather than in input/results arrays
- `Model.from_dict` has been removed in favor of `calliope.read_dict`

**Configuration Updates:**
- `parameters` renamed to `data_definitions`
- `config.init.broadcast_param_data` renamed to `config.init.broadcast_input_data`
- New `config.solve.postprocess_active` option to skip postprocessing

**Math & Formulation:**
- "Math global expressions have an order option to allow user-defined math to be reordered relative to pre-defined math"
- MILP math now has its own file (`milp.yaml`)
- Backwards-incompatible: `where:` now uses `==` for equality (previously `=`)

**Loading Models:**
- YAML files loaded with `calliope.read_yaml(...)`
- In-memory dicts loaded with `calliope.Model.from_dict(...)`
- In-memory xarray datasets loaded with `calliope.Model(...)`

**Results & Output:**
- Model attributes saved to `attrs.yaml` when storing data
- New helper functions for summation and rolling window calculations
- Objective function values stored in results arrays

**SPORES Mode:**
- Baseline run renamed to `0`
- `skip_baseline_run` renamed to `use_latest_results`

---

#### 0.7.0.dev6 (2025-03-24)

**Major Features:**
- Working SPORES mode with multiple scoring algorithms
- New backend `set_objective` method to switch between pre-defined objectives
- "from and to parameters (to define start and end point of a transmission link) are now link_from and link_to"

**Configuration:**
- Backwards-incompatible: operate and spores mode options now nested (e.g., `build.operate.window`)
- "templates can now be used anywhere within YAML definition files, not just in nodes, techs and data_tables sections"

---

#### 0.7.0.dev5 (2024-12-04)

**Data Handling:**
- "Single data entries defined in YAML indexed parameters will not be automatically broadcast along indexed dimensions"
- New `where(array, condition)` math helper function
- Data tables can now inherit from templates
- Dimension renaming functionality via `rename_dims` option

**Cost Structure:**
- Cost expressions split: `cost_investment`, `cost_investment_annualised`, `cost_operation_fixed`, `cost_operation_variable`

**Terminology:**
- `data_sources` renamed to `data_tables`
- `data_sources.source` renamed to `data_tables.data`

---

#### 0.7.0.dev4 (2024-09-10)

**New Capabilities:**
- "Piecewise constraints added to the YAML math with its own unique syntax"
- Direct Gurobi Python API interface: "Tests show that using the gurobi solver via the Python API reduces peak memory consumption and runtime by at least 30%"
- Decision variables and global expressions can have titles for visualization

**Improvements:**
- "Force a header row in tabular data loaded from CSV"
- Shadow prices extraction via `config.solve.shadow_prices`
- Model stores key timestamps (creation, build started/complete, solve started/complete)

---

#### 0.7.0.dev3 (2024-02-14)

- Math documentation can include YAML snippets as separate tabs
- Variables and global expressions can have default values
- Utility function `calliope.util.schema.update_model_schema(...)` for adding user parameters

---

#### 0.7.0.dev2 (2024-01-26)

Major structural rewrite introducing:
- Storage buffers in all technology base classes
- Multiple carriers and carrier-specific capacities/efficiencies
- Parameters defined outside nodes/techs scope
- "Non-timeseries data can be loaded from CSV files or in-memory Pandas DataFrames"
- User-defined math formulations via new Calliope math syntax

Backwards-incompatible changes:
- Python >= 3.10 required
- Pandas >= 2.1, Pyomo >= 6.4, Xarray >= 2023.10
- Flat technology definitions (removed essentials/constraints/costs distinction)
- `locations` → `nodes`; `links` → transmission techs
- `model.run()` → `model.build()` + `model.solve()`
- Cost parameters flattened to indexed parameter syntax

---

#### Historical Releases (0.6.x and earlier)

**0.6.10 (2023-01-18):** Updated to NumPy 1.23, Pandas 1.5, Pyomo 6.4

**0.6.9 (2023-01-10):** Python 3.9 default; SPORES mode improvements

**0.6.8 (2022-02-07):** Storage constraint additions; parameter defaults changed to None

**0.6.0 (2018-04-20):** Near-complete rewrite; new Pyomo backend


---

