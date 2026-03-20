# User-Defined Math Example: CHP Plants

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/chp_htp/

## Description

This documentation describes how to model Combined Heat and Power (CHP) plants with three distinct operational configurations:

### Type 1: Extraction (Condensing) Turbines
"Some electrical efficiency can be sacrificed by diverting high-temperature steam to provide more heat." An operating region exists between the extraction line (cv) and backpressure line (cb), with fuel consumption remaining constant along the extraction curve.

### Type 2: Backpressure with Auxiliary Boilers
These units lack extraction capability but include a direct heating boiler. Heat output comes from two sources: steam from the turbine and fuel diverted to the boiler. This creates a defined operating region bounded by the backpressure line.

### Type 3: Backpressure Only
"There is no operating region; the output must follow the backpressure line." Output is strictly constrained to the backpressure relationship.

## Key Parameters

The implementation introduces four technology-level parameters:

- **turbine_type**: Specifies extraction or backpressure variants
- **power_loss_factor**: Extraction turbine parameter (cv)
- **power_to_heat_ratio**: Backpressure ratio (cb)
- **boiler_eff**: Conventional boiler efficiency

## Implementation Notes

These constraints override the base `balance_conversion` constraint using conditional "where" clauses to prevent conflicts between different CHP configurations.
