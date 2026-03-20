# Calliope v0.7 Documentation Index

This index provides a single-sentence overview of each documentation file to facilitate agentic interaction and navigation.

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/

## Getting Started
- [Home / Overview](home.md): High-level introduction to Calliope as an energy system modelling framework for capacity expansion and dispatch.
- [Installation](installation.md): Step-by-step instructions for installing Calliope and its required optimization solvers.
- [Concepts](getting_started_concepts.md): Foundational explanation of the framework's core components like carriers, technologies, and nodes.
- [Creating a Model](getting_started_creating.md): Tutorial on building a minimal functional model and organizing the project directory structure.
- [Running a Model](getting_started_running.md): Overview of the three primary methods for executing models via CLI, Python, or batch scripts.
- [Analysing a Model](getting_started_analysing.md): Guide to exploring model results using the Calligraph visualization tool or Python's xarray library.
- [Troubleshooting](troubleshooting.md): Strategies for diagnosing model errors, performance bottlenecks, and solver infeasibility.

## Building Blocks
- [Model Configuration](basic_config.md): Reference for settings applied during model initialization, building, and solving stages.
- [Modes](basic_modes.md): Explanation of standard optimization (base), dispatch (operate), and diversity (SPORES) running modes.
- [Technologies](basic_techs.md): Comprehensive guide to the five base technology types and their parameter configurations.
- [Nodes](basic_nodes.md): Detailed explanation of how nodes represent geographic locations and site-specific technology assignments.
- [Data Tables](basic_data_tables.md): Instructions for loading and filtering multi-dimensional input data from external CSV files.
- [Data Definitions](basic_data_definitions.md): Guide to specifying global parameters and scalars that exist independently of nodes or technologies.
- [Scenarios and Overrides](basic_scenarios.md): Methods for managing numerous model variations and sensitivity studies through named YAML blocks.
- [Running via CLI](basic_running_cli.md): Detailed command-line interface reference for model execution and managing result output.
- [Running via Python](basic_running_python.md): Programmatic API reference for building, solving, and analyzing models in interactive Python sessions.
- [Postprocessing](basic_postprocessing.md): Description of automated calculations for system metrics like capacity factors and levelized costs.

## Math
- [Built-in Base Math](math_base.md): Complete mathematical formulation of Calliope's foundational optimization model and constraints.
- [Other Built-in Math (overview)](math_built_in.md): Navigation hub for advanced mathematical logic including MILP and inter-cluster storage.
- [MILP Math](math_built_in_milp.md): Mathematical extensions for mixed-integer linear programming, enabling unit commitment and purchase costs.
- [Inter-cluster Storage Math](math_built_in_storage_inter_cluster.md): Specialized constraints for managing energy storage dynamics across multiple daily time clusters.
- [SPORES Mode Math](math_built_in_spores.md): Mathematical framework for identifying diverse, near-optimal system designs within cost tolerances.

## User-Defined Math
- [Overview](user_defined_math.md): High-level introduction to extending or replacing built-in math using custom YAML definitions.
- [Math Components](user_defined_math_components.md): Breakdown of custom math building blocks: decision variables, expressions, constraints, and objectives.
- [Math Syntax](user_defined_math_syntax.md): Syntax reference for the `foreach`, `where`, and equation strings used in mathematical formulations.
- [Helper Functions](user_defined_math_helper_functions.md): Catalog of specialized functions like `sum` and `roll` for use within mathematical expressions.
- [Adding Custom Math](user_defined_math_customise.md): Instructions for integrating custom math files into models and generating mathematical documentation.

## User-Defined Math Examples
- [Annual Energy Balance](udm_example_annual_energy_balance.md): Constraint example for setting annual maximum limits on energy production or source use.
- [CHP Plants](udm_example_chp_htp.md): Modeling patterns for extraction and backpressure Combined Heat and Power operational regions.
- [Demand Share Per Timestep Decision](udm_example_demand_share_per_timestep_decision.md): Implementation of decision variables to determine technology-specific demand shares per timestep.
- [Fuel Distribution](udm_example_fuel_dist.md): Methods for tracking commodity distribution in systems without explicitly defined transport networks.
- [Time-varying Flow Limit](udm_example_max_time_varying.md): Example of implementing dynamic, time-indexed upper bounds on technology flow capacities.
- [Net Import Share](udm_example_net_import_share.md): Constraints for restricting energy imports as a specific proportion of total nodal demand.
- [Piecewise Linear Costs](udm_example_piecewise_linear_costs.md): YAML definition for implementing non-linear, capacity-dependent investment cost curves.
- [Piecewise Linear Efficiency](udm_example_piecewise_linear_efficiency.md): Implementation of efficiency curves that vary with technology outflow levels.
- [Flow Share Across All Timesteps](udm_example_share_all_timesteps.md): Enforcing fixed technology production shares across the entire modeling horizon.
- [Flow Share Per Timestep](udm_example_share_per_timestep.md): Methods for setting technology-specific shares independently for each modeling timestep.
- [SOS2 Piecewise Linear Costs](udm_example_sos2_piecewise_linear_costs.md): Economies-of-scale implementation using Special Ordered Sets (SOS2) for decreasing marginal costs.
- [Uptime/Downtime Limits](udm_example_uptime_downtime_limits.md): Implementation of maintenance scheduling and annual capacity factor range constraints.

## Advanced Topics
- [Advanced Constraints](advanced_constraints.md): Exploration of complex features like co-production hubs, internal buffers, and area-based limits.
- [Time Adjustment](advanced_time.md): Techniques for managing temporal resolution through data resampling and representative day clustering.
- [Generating Scripts](advanced_scripts.md): Automation guide for creating batch scripts to execute large-scale model sensitivity runs.
- [Solver Options](advanced_solver.md): Instructions for configuring advanced parameters for Gurobi, CPLEX, and other optimization solvers.
- [Backend Choice](advanced_backend_choice.md): Comparison and selection guide for Pyomo vs. Gurobi optimization backend interfaces.
- [Backend Interface](advanced_backend_interface.md): API reference for inspecting and manipulating optimization components directly in Python.
- [Shadow Prices](advanced_shadow_prices.md): Guide to extracting and analyzing constraint dual variables (shadow prices) for economic studies.

## Examples and Tutorials
- [Examples Overview](examples_overview.md): Summary of provided national and urban scale tutorial models for learning framework features.
- [National Scale Example](examples_national_scale.md): Walkthrough of a multi-region electricity system featuring supply, demand, and battery storage.
- [Urban Scale Example](examples_urban_scale.md): Demonstration of a district-level energy system with complex co-production and heat networks.
- [MILP Example](examples_milp.md): Showcase of mixed-integer programming features like discrete unit commitment applied to the urban model.
- [Loading Tabular Data](examples_loading_tabular_data.md): Practical tutorial on workflows for managing model data via external CSV data tables.
- [Running in Different Modes](examples_modes.md): Comparison guide for executing models in optimization, dispatch, and SPORES modes.
- [Piecewise Constraints Tutorial](examples_piecewise_constraints.md): Step-by-step implementation guide for approximating non-linearities with piecewise logic.
- [Calliope Model Object](examples_calliope_model_object.md): Interaction guide for programmatically working with Calliope's Model and Backend Python objects.
- [Calliope Logging](examples_calliope_logging.md): Instructions for setting up persistent console and file-based logging for model executions.

## Reference
- [YAML in Calliope](reference_yaml.md): Syntax reference for core YAML features like nesting, imports, and component templates.
- [CLI Reference](reference_cli.md): Comprehensive documentation for all `calliope` command-line tools and utilities.
- [API: Model](reference_api_model.md): Detailed Python API documentation for the primary `calliope.Model` user interface class.
- [API: Backend Model](reference_api_backend_model.md): Interface reference for programmatically interacting with optimization problem components.
- [API: Helper Functions](reference_api_helper_functions.md): Complete catalog of mathematical helper functions available for expression parsing.
- [API: Example Models](reference_api_example_models.md): Quick-access reference for the built-in example models used throughout documentation.
- [API: AttrDict](reference_api_attrdict.md): Interaction guide for Calliope's nested attribute-dictionary data structure.
- [API: Postprocess](reference_api_postprocess.md): Reference for functions that calculate additional result metrics like capacity factors.
- [API: Exceptions](reference_api_exceptions.md): Catalog of framework-specific error and warning classes for better error handling.
- [API: Logging](reference_api_logging.md): Configuration guide for internal system timing and operational message logging.
- [Config Schema](reference_config_schema.md): Formal schema definition for all model initialization, building, and solving settings.
- [Data Table Schema](reference_data_table_schema.md): Specification guide for loading, filtering, and mapping external CSV parameter tables.
- [Model Schema](reference_model_schema.md): Structural reference for defining system components like nodes, technologies, and variables.
- [Math Schema](reference_math_schema.md): Formal specification of the YAML-based language used for mathematical programming.

## Other
- [Migrating from v0.6 to v0.7](migrating.md): Critical upgrade guide documenting architectural changes between major Calliope versions.
- [Contributing](contributing.md): Guidelines for community contributions to Calliope's code, tests, and documentation.
- [Version History](version_history.md): Historical log of framework updates, performance improvements, and feature releases.
