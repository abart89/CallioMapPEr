# API Reference: Helper Functions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/helper_functions/

## Overview

Helper functions process data in Calliope's mathematical `where` and `expression` strings. Each function has a `NAME` property defining its usage in math expressions.

## Core Helper Functions

### DefaultIfEmpty
**Purpose:** "Fill empty (NaN) items in arrays."

**Allowed In:** `expression`

**Usage Example:**
```python
default_if_empty(flow_cap, 0)
```
Returns an array with NaN values filled using the provided default, or a scalar default if the variable doesn't exist in the model.

---

### Defined
**Purpose:** "Find all items of one dimension that are defined in an item of another dimension."

**Allowed In:** `where`

**Usage:**
```python
defined(techs=[tech1, tech2], within=nodes, how=any)
```
Checks whether nodes define specific technologies. The `how` parameter accepts `any` or `all` to determine matching logic.

---

### GetValAtIndex
**Purpose:** "Getter functionality for obtaining values at specific integer indices."

**Allowed In:** `expression`, `where`

**Usage:**
```python
get_val_at_index(timesteps=0)  # First timestep
get_val_at_index(timesteps=-1) # Last timestep
```

---

### GroupDatetime
**Purpose:** "Apply a summation over a datetime group on a datetime dimension."

**Allowed In:** `expression`

**Usage:**
```python
group_datetime(flow_in, timesteps, date)
group_datetime(flow_in, timesteps, month)
```
Aggregates timestep data by date, month, or other datetime periods.

---

### GroupSum
**Purpose:** "Apply a summation over an array grouping."

**Allowed In:** `expression`

**Usage:**
```python
group_sum(flow_out, power_plant_groups, emission_groups)
```
Sums array values according to a grouping dimension.

---

### ReduceCarrierDim
**Purpose:** "Sum over the carrier dimension in math components."

**Allowed In:** `expression`

**Usage:**
```python
reduce_carrier_dim(array, 'in')
reduce_carrier_dim(array, 'out')
```
Reduces arrays by summing across the carrier dimension based on flow direction.

---

### Roll
**Purpose:** "Roll (shift) items along ordered dimensions."

**Allowed In:** `expression`

**Usage:**
```python
roll(array, timesteps=1)
```
Shifts array data while maintaining coordinate labels.

---

### SelectFromLookupArrays
**Purpose:** "N-dimensional indexing functionality."

**Allowed In:** `expression`

Applies vectorized indexing across multiple dimensions using lookup arrays.

---

### Sum
**Purpose:** "Apply a summation over dimension(s) in math expressions."

**Allowed In:** `expression`

**Usage:**
```python
sum(array, over='carriers')
sum(array, over=['nodes', 'techs'])
```
NaN values are ignored; returns NaN if all values along a dimension are NaN.

---

### SumNextN
**Purpose:** "Sum the next N items in an array."

**Allowed In:** `expression`

Performs rolling-window summation, ideal for ordered data like timeseries.

---

### Where & WhereAny
**Purpose:** Conditional filtering in mathematical expressions.

**Allowed In:** `where`, `expression`

Filter constraints and expressions based on data availability conditions.

---

## ParsingHelperFunction (Base Class)

All helper functions inherit from `ParsingHelperFunction`, which defines:

- **ALLOWED_IN:** List of contexts (expression/where) where function is valid
- **NAME:** String identifier for math expressions
- **ignore_where:** Whether to bypass where-array filtering
- **as_array():** Returns n-dimensional xarray output
- **as_math_string():** Generates LaTeX math representation
