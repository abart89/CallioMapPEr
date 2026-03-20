# User-Defined Math Example: Time-varying Flow Limit

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/examples/max_time_varying/

## Description

This feature allows you to establish per-timestep variations in flow limits that would otherwise remain static. For instance, `flow_cap` can be configured to fluctuate above or below its rated capacity for each timestep. To implement this, user-defined timeseries parameters must be present in model inputs, typically defined in CSV files and loaded as data tables.

**New indexed parameter:**
- `flow_cap_max_relative_per_ts`

## YAML Definition

The following constraint implements time-varying flow limits:

```yaml
parameters:
  flow_cap_max_relative_per_ts:
    description: >
      The relative quantity of flow capacity used to limit generator
      outflow in each timestep.
    default: 1
    unit: $\frac{\text{energy}}{\text{power}}$

constraints:
  max_time_varying_flow_cap:
    description: >
      Limit flow out in each hour according to a time varying fractional
      limit that is multiplied by the technology flow cap. This represents,
      for instance, the impact of outdoor temperature on the maximum output
      of a technology relative to its rated max output.
    foreach: [nodes, techs, carriers, timesteps]
    where: "flow_cap_max_relative_per_ts"
    equations:
      - expression: >
          flow_out <=
          flow_cap_max_relative_per_ts * flow_cap * flow_out_parasitic_eff
```

This constraint multiplies the relative capacity parameter by the technology's rated capacity and efficiency to establish dynamic upper bounds on outflow per timestep.
