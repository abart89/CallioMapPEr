# User-Defined Math Example: Fuel Distribution

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/fuel_dist/

## Description

This example demonstrates how to track commodity distribution in systems where goods don't travel along distinct networks. The approach enables import/export of commodities without specifying exact origins or destinations, simplifying model definition at the cost of commodity source traceability. While termed "fuels" below, this applies equally to other commodities like waste or water with corresponding carriers.

### Key Parameters

- `fuel_import_max`: Maximum importable fuel amount (default: infinite)
- `fuel_export_max`: Maximum exportable fuel amount (default: infinite)
- `cost_fuel_distribution`: Cost for importing or revenue for exporting fuel (default: 0)
- `allow_fuel_distribution`: Lookup array indicating carriers eligible for distribution tracking

### Helper Functions

- `any` (where clause)
- `sum` (expression)

## YAML Definition

### Parameters Section
Defines three main parameters: maximum import limits, maximum export limits, and distribution costs, each with energy units and configurable defaults.

### Lookups Section
Contains `allow_fuel_distribution`, a boolean lookup table specifying which nodes and carriers participate in fuel distribution.

### Variables Section
The `fuel_distributor` variable represents fuel transfers between nodes. Positive values indicate imports; negative values indicate exports. It's indexed across nodes, carriers, and timesteps, with bounds from negative to positive infinity.

### Constraints Section

**System Balance Integration**: Modifies the existing system balance constraint to incorporate fuel distribution through conditional sub-expressions.

**Total Balance**: The `restrict_total_imports_and_exports` constraint ensures that system-wide fuel imports equal exports (summing across nodes equals zero per carrier/timestep).

**Nodal Limits**:
- `restrict_nodal_imports` caps imports at `fuel_import_max`
- `restrict_nodal_exports` caps exports at `fuel_export_max`

### Objectives Section

The objective function integrates fuel distribution costs. The implementation notes that cost impacts are negligible unless distribution costs vary by node or system-wide imbalances are permitted.
