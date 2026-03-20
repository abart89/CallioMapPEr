# Adding Your Own Math to a Model

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/customise/

## Overview

Once you understand math components and formulation syntax, you can introduce custom math to your Calliope model. This math can either extend the pre-defined formulation or replace it entirely.

## Adding Extra Math

The simplest approach involves extending Calliope's existing math by defining an "extra math" option. For instance, you might add a time-varying parameter to the `storage_max` constraint:

```yaml
storage_max:
  equations:
    - expression: storage <= storage_cap * time_varying_parameter
```

This preserves other constraint elements without requiring redefinition.

### Configuration

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

### Python Integration

In interactive sessions, pass math as a dictionary during model instantiation:

```python
calliope.from_yaml(..., math_dict={"my_new_math_1": {...}, ...})
```

Inspect the final applied math via `model.math.build`.

## Replacing Base Math

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

## Adding Parameter Metadata

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

## Validating Math

Enable pre-build validation to catch errors before optimization:

```yaml
config:
  init:
    pre_validate_math_strings: true
```

## Generating Documentation

Create rich-text mathematical documentation for your model:

```python
from calliope.postprocess.math_documentation import MathDocumentation

model = calliope.Model("path/to/model.yaml")
model.build()

math_documentation = MathDocumentation(model, include="valid")
math_documentation.write(filename="path/to/output/file.[tex|rst|md]")
```

For interactive online documentation with MKDocs, enable `mkdocs_features=True`.
