# Calliope Version History

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/version_history/

## Latest Release: 0.7.0.dev7 (2025-09-05)

### User-facing changes

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

## 0.7.0.dev6 (2025-03-24)

**Major Features:**
- Working SPORES mode with multiple scoring algorithms
- New backend `set_objective` method to switch between pre-defined objectives
- "from and to parameters (to define start and end point of a transmission link) are now link_from and link_to"

**Configuration:**
- Backwards-incompatible: operate and spores mode options now nested (e.g., `build.operate.window`)
- "templates can now be used anywhere within YAML definition files, not just in nodes, techs and data_tables sections"

---

## 0.7.0.dev5 (2024-12-04)

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

## 0.7.0.dev4 (2024-09-10)

**New Capabilities:**
- "Piecewise constraints added to the YAML math with its own unique syntax"
- Direct Gurobi Python API interface: "Tests show that using the gurobi solver via the Python API reduces peak memory consumption and runtime by at least 30%"
- Decision variables and global expressions can have titles for visualization

**Improvements:**
- "Force a header row in tabular data loaded from CSV"
- Shadow prices extraction via `config.solve.shadow_prices`
- Model stores key timestamps (creation, build started/complete, solve started/complete)

---

## 0.7.0.dev3 (2024-02-14)

- Math documentation can include YAML snippets as separate tabs
- Variables and global expressions can have default values
- Utility function `calliope.util.schema.update_model_schema(...)` for adding user parameters

---

## 0.7.0.dev2 (2024-01-26)

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

## Historical Releases (0.6.x and earlier)

**0.6.10 (2023-01-18):** Updated to NumPy 1.23, Pandas 1.5, Pyomo 6.4

**0.6.9 (2023-01-10):** Python 3.9 default; SPORES mode improvements

**0.6.8 (2022-02-07):** Storage constraint additions; parameter defaults changed to None

**0.6.0 (2018-04-20):** Near-complete rewrite; new Pyomo backend
