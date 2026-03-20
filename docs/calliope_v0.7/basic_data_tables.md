# Data Tables

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/data_tables/

## Loading Tabular Data

Calliope enables loading data from CSV files or pandas dataframes using the `data_tables` configuration. The basic syntax includes:

- **data**: File path or in-memory object reference
- **rows**: Dimension(s) defined per row
- **columns**: Dimension(s) defined per column
- **select**: Filter specific dimension values
- **drop**: Remove unwanted dimensions
- **add_dims**: Inject dimensions with assigned values
- **rename_dims**: Map dimension names to Calliope conventions

## CSV File Structure Requirements

### Header Rows
CSV files must include at least one header row. Without it, Calliope will misinterpret data as dimension names and generate errors.

### Multi-Level Indexing
You can define multiple index levels per row or column to handle multi-dimensional data. For example, a table with both node and technology indices would look like:

```
nodes    | techs
---------|-------
node1    | tech1  → 15
node2    | tech2  → 5
```

### Sparse Arrays
For data with many empty cells, use a "long and thin" dense structure rather than a square sparse format.

## Practical Examples

### Loading Time Series Data

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

### Loading Technology Data

```yaml
data_tables:
  tech_data:
    data: data_tables/tech_data.csv
    rows: [techs, parameters]
```

## Advanced Features

### Selection and Filtering
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

### Adding Dimensions
Avoid repetition by adding dimensions during load:

```yaml
add_dims:
  costs: monetary
  parameters: cost_flow_cap
```

### Templates
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

### Dimension Renaming
Map non-standard dimension names to Calliope conventions:

```yaml
rename_dims:
  time: timesteps
```

## Loading from Pandas DataFrames

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

## Important Considerations

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

## Data You Cannot Load Tabulary

The following cannot be defined in tabular format:

- `active`: Technology/node activation (YAML only)
- `definition_matrix`: Auto-generated from `carrier_in` and `carrier_out`
- `template`: Template references (YAML only)
- `templates`: Template definitions (YAML only)
