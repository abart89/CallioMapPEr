# Postprocessing

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/postprocessing/

Calliope implements two sequential postprocessing steps to refine model results.

## Additional Result Variables

The system generates several computed metrics:

- **capacity_factor**: Indexed by technologies, nodes, and timesteps
- **systemwide_capacity_factor**: Per-tech average across nodes and time, weighted by timestep importance
- **systemwide_levelised_cost**: Per-tech carrier production cost indexed by techs, carriers, and cost classes
- **total_levelised_cost**: Carrier-aggregate production cost indexed by carriers and cost classes
- **unmet_sum**: Combines unmet demand and supply values

### Levelised Cost Calculation

These costs are computed by dividing total cost by production: `cost / production`. The production figure uses `flow_out` + `flow_export`, temporarily scaled by weights for consistency. Since constraint-based costs already incorporate weighting, no additional adjustment occurs. Refer to the `systemwide_levelised_cost` function for implementation specifics.

> "To disable the first part of postprocessing, set `config.solve.postprocessing_active` to `false`."

## Zero Threshold

The second step applies a `zero_threshold` parameter, which converts values below this magnitude to zero. This addresses floating-point calculation artifacts. The default threshold is `1e-10`, though setting it to `0` disables this filtering entirely.
