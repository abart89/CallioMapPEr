# YAML as Used in Calliope

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/yaml/

## A Quick Introduction to YAML

Calliope's model configuration files use YAML, described as "a human friendly data serialisation standard for all programming languages." Configuration typically follows an `option: value` format.

### Data Types

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

### Comments

The `#` symbol marks comments. Strings containing `#` require quotation marks:

```yaml
# This is a comment
option1: "text with ##hashtags## needs quotation marks"
```

### Lists and Dictionaries

Lists use either bracket notation or dash prefixes:

```yaml
key: [option1, option2]
# or
key:
  - option1
  - option2
```

Dictionaries use either curly braces or indented key-value pairs:

```yaml
key: {option1: value1, option2: value2}
# or
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

## Calliope's Additional YAML Features

### Abbreviated Nesting

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

### Relative File Imports

The `import:` directive includes other YAML files:

```yaml
import:
  - path/to/file_1.yaml
  - path/to/file_2.yaml
```

Imported and importing files cannot define the same option. The directive supports absolute or relative paths.

### Reusing Definitions Through Templates

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

### Overriding One File with Another

Override sections can modify or extend existing data:

```yaml
# Initial configuration
one.two.three: x
four.five.six: x

# Override to apply
one.two.four: y
four.five.six: y
```

Use the special `_REPLACE_` key to entirely replace a nested dictionary instead of merging it.
