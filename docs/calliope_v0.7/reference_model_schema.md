# Model Definition Schema

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/model_schema/

This page documents the schema for Calliope model definitions, which consist of three primary components:

## Data Definitions

Data definitions comprise a dictionary where keys must match the pattern `^[^_^\d][\w]*$` (starting with a letter or underscore, followed by word characters).

Values can be:
- Primitive types (string, boolean, integer, number)
- Indexed data objects containing:
  - **`data`**: Parameter values (single value or array matching index length)
  - **`dims`**: Model dimension(s) referenced
  - **`index`**: Dimension members to apply values to
- Null values

## Data Tables

Data tables enable loading external data files with configuration for:

- **`data`** (required): File path, relative to model config location
- **`rows`**: Dimension names defined row-wise in the spreadsheet
- **`columns`**: Dimension names defined column-wise
- **`select`**: Filter specific index items before processing
- **`drop`**: Remove irrelevant rows/columns
- **`add_dims`**: Introduce dimensions after loading
- **`rename_dims`**: Map data table dimensions to Calliope equivalents

## Nodes

Nodes represent locations in the energy system. Each node can:

- Include latitude/longitude (WGS84/EPSG4326 coordinates)
- Toggle active status (default: true)
- Reference technologies present at that location
- Override technology-specific parameters

## Technologies

Technologies represent energy system components (generation, storage, demand, conversion, transmission). Each tech includes:

- Active status toggle (default: true)
- Base technology classification (supply, demand, conversion, storage, transmission)
- Indexed parameter data with flexible dimensionality
