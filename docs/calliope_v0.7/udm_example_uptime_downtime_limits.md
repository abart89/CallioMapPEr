# User-Defined Math Example: Uptime/Downtime Limits

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/uptime_downtime_limits/

## Description

This documentation outlines constraints designed to prevent technologies from operating too infrequently or excessively throughout a year. Such constraints are useful for modeling maintenance downtime or simplistic ramping limitations (applicable to technologies like nuclear power plants).

The implementation supports multiple constraint types:

- **Annual capacity factor constraints**: Establish operating ranges for technology fleets. For example, nuclear plants typically maintain annual capacity factors between 75-85%.

- **Downtime period constraint**: Enforces technology shutdown during specific timesteps by setting values for maintenance windows while leaving other periods empty (NaN).

- **Downtime period decision constraint**: Enables technologies with integer decision variables to autonomously select timesteps for non-operation, though consecutive downtime cannot be enforced.

## New Parameters

- `capacity_factor_min`: Minimum annual operating fraction (default: 0)
- `capacity_factor_max`: Maximum annual operating fraction (default: infinity)
- `downtime_periods`: Timeseries data marking scheduled downtime (boolean, default: false)
- `uptime_limit`: Maximum timesteps an asset may operate (default: infinity)

## YAML Definition

The mathematical formulation includes four constraint types:

**annual_capacity_factor_min**: Enforces minimum operation by ensuring summed weighted outflow meets or exceeds minimum capacity factor multiplied by total time.

**annual_capacity_factor_max**: Limits maximum operation similarly, using less-than-or-equal constraints.

**downtime_period**: Forces zero outflow across all carriers during designated downtime periods.

**downtime_period_decision**: Restricts operating units' total weighted timesteps to stay within the uptime limit for technologies with integer variables enabled.
