# Advanced Constraints

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/constraints/

This documentation section covers advanced features in Calliope's mathematical formulation and configuration options.

## Multiple Input/Output Carriers

Technologies can define multiple carriers in and/or out using YAML lists. Examples include:

- **Combined heat and power (CHP) plants**: One input carrier (gas) with two co-produced outputs (electricity, heat)
- **Heat pumps**: Single input (electricity) with multiple output options (cooling or heating)
- **Dual-fuel plants**: Multiple input options (coal or biofuel) with one output (electricity)
- **Nuclear plants**: Tracking auxiliary flows like nuclear waste alongside primary output

The default math assumes inflow requirements equal the sum of outflows. However, some technologies require custom relationships—for instance, CHP plants where gas consumption depends on electricity production, not the sum of all outputs.

Technologies can differentiate parameters across carriers using indexed data structures:

```yaml
techs:
  chp:
    carrier_in: gas
    carrier_out: [electricity, heat]
    flow_cap_max:
      data: 100
      index: electricity
      dims: carriers
```

## Storage Buffers in Non-Storage Technologies

Any technology can activate internal storage using `include_storage: true`. This allows carriers to be stored between timesteps and released later, useful for:

- Supply sources requiring intermediate storage (concentrated solar power, biogas production)
- Conversion technologies where stored carriers are processed on release

## Revenues and Carrier Export

Negative cost values represent revenues. Export extends this concept by removing carriers from the system without meeting demand (analogous to excess rooftop solar exported to the grid).

**Important note**: Negative capacity costs require explicit capacity limits to prevent unbounded optimization.

## Area Use Constraints

Several optional parameters manage area-related restrictions:

- `source_unit: per_area` scales resources with deployment area
- `area_use_min/max` defines spatial limits
- `area_use_per_flow_cap` links area to flow capacity (e.g., 1.5 means area equals 1.5 times capacity)
- `available_area` at nodes limits combined technology deployment space

## One-Way Transmission Links

Transmission is bidirectional by default. Enforce unidirectionality with:

```yaml
techs:
  region1_to_region2:
    link_from: region1
    link_to: region2
    base_tech: transmission
    one_way: true
```

## Per-Distance Transmission Constraints

Transmission technologies support distance-based parameters:

- `flow_out_eff_per_distance`: Efficiency loss per unit distance
- `cost_flow_cap_per_distance`: Capital cost per unit distance

Distance can be specified directly or calculated automatically from node coordinates.

## Cyclic Storage

The `cyclic_storage` parameter (enabled by default) links storage levels at the beginning and end of the timeseries. This better represents recurring yearly operations where initial storage equals final storage.

With `storage_initial: 0` and `cyclic_storage: true`, stored energy must reach zero by the horizon's end. Cyclic storage functions with time clustering but cannot be used in operate mode.
