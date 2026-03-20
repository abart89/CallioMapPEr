# API Reference: AttrDict

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/attrdict/

## Overview

`calliope.attrdict.AttrDict` is an extended dictionary class that subclasses Python's built-in `dict` with attribute-style key access. It supports nested key operations and provides methods for working with YAML data.

## Basic Usage

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

## Methods

### `as_dict(flat=False)`
Returns the AttrDict as a pure Python dictionary. When `flat=True`, returns a flattened version; otherwise returns nested dictionaries.

### `as_dict_flat()`
Returns a completely flat dictionary with dot-notation keys.

### `as_dict_nested()`
Converts the AttrDict to a pure dict, recursively converting nested AttrDicts and those within lists.

### `copy()`
Creates a copy that returns an AttrDict (not a regular dict).

### `del_key(key)`
Deletes a key, with support for nested keys using dot notation (e.g., `"foo.bar"`).

### `get_key(key, default=_MISSING)`
Retrieves values using dot notation for nested access. Supports optional default values for missing keys.

### `init_from_dict(d)`
Initializes the AttrDict from a dictionary, converting nested dicts to AttrDicts recursively.

### `keys_nested(subkeys_as='list')`
Returns all keys including nested ones. With `subkeys_as='list'` (default), returns `['a', 'b.b1', 'b.b2']`. With `subkeys_as='dict'`, returns nested structure `['a', {'b': ['b1', 'b2']}]`.

### `set_key(key, value)`
Sets values using dot notation for nested keys, automatically creating intermediate AttrDicts as needed.

### `union(other, allow_override=False, allow_replacement=False)`
Merges another AttrDict into the current one. By default raises `KeyError` if keys already exist. Set `allow_override=True` to permit overwrites. The `allow_replacement` parameter enables the `"_REPLACE_"` special key for replacing entire sub-dictionaries.
