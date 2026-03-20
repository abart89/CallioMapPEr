# Loading Tabular Data (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/loading_tabular_data/

This documentation page covers methods for loading tabular data into Calliope models.

## Defining Data in Text-Based YAML Format

Data can be defined directly in YAML configuration files, which serves as the foundational approach for specifying model parameters and attributes.

## Defining Data in Tabular CSV Format

Calliope supports loading data from CSV (comma-separated values) files, enabling users to organize large datasets in spreadsheet-compatible formats. This approach is particularly useful for managing extensive parameter tables.

### Loading Directly from In-Memory Dataframes

Data can be loaded from pandas dataframes that exist in Python memory, providing flexibility for programmatic data manipulation and integration with existing Python workflows.

### Verifying Model Consistency

The documentation emphasizes the importance of validating that tabular data aligns with model structure and requirements before running optimization routines.

## Mixing YAML and Data Table Definitions

Users can combine YAML-based definitions with tabular CSV data within a single model. This hybrid approach allows leveraging the strengths of both formats—YAML for configuration and structure, CSV for bulk data management.

## Overriding Tabular Data with YAML

The system supports overriding values from CSV tables using YAML specifications. This feature enables exceptions and special cases to be handled without modifying underlying data tables.

**Note:** The page includes a downloadable Jupyter notebook demonstrating practical implementation of these data loading techniques.
