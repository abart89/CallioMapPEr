# Data Table Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/data_table_schema/

The data table schema defines how tabular data files are loaded and processed in Calliope models.

## Required Parameters

**`data`** _(string, required)_: File path to the data source, either absolute or relative to the model configuration file location.

## Optional Parameters

**`rows`**: Specifies dimension names organized row-wise in the data file. Each name should correspond to a column containing index items, positioned to the left of data columns. Accepts a string, array of strings, or null (default).

**`columns`**: Specifies dimension names organized column-wise in the data file. Each name should correspond to a row containing index items, positioned above data rows. Accepts a string, array of strings, or null (default).

**`select`**: Filters one or more index items from a dimension before other transformations. Applied before `drop` and `add_dims` operations. Accepts an object mapping dimension names to values or null (default).

**`drop`**: Removes irrelevant rows and/or columns (e.g., comments, metadata, unit labels). Can be used to eliminate dimensions that are later reintroduced via `add_dims`. Accepts a string, array of strings, or null (default).

**`add_dims`**: Introduces data dimensions after loading. Useful for assigning identical values to multiple parameters or adding constant dimensions. Accepts an object mapping dimension names to values/arrays or null (default).

**`rename_dims`**: Maps data table dimension names to corresponding Calliope dimension names. For example: `{"time": "timesteps"}`. Accepts an object or null (default).

All string identifiers must match the pattern `^[^_^\d][\w]*$` (beginning with a letter or underscore, followed by word characters).
