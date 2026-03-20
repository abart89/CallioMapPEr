# Data Definitions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/data_definitions/

## Overview

The `data_definitions` section allows you to define data that isn't indexed over technologies or nodes. This can be a single value or data indexed across one or more model dimensions.

### Basic Usage

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

### Indexed Data

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

## Parameters vs. Lookups

Data definitions populate either parameters or lookups depending on how they're defined in the model math. Lookups serve as helper parameters with non-numeric values like strings or booleans.

## Broadcasting Data

When `broadcast_input_data` is enabled in configuration, a single value automatically applies to all index items:

```yaml
my_indexed_param:
  data: 1  # Applies to all index values
  index: [val1, val2, val3, val4]
  dims: my_new_dim
```

**Warning**: Broadcasting risks unintended data assignment if index values change via scenario overrides.

**Note**: Avoid `data_definitions` for large datasets (like time-indexed data) due to memory overhead.
