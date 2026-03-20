# Time Adjustment

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/time/

## Time Resolution Adjustment (Resampling)

Models have a default timestep length determined by the input time series data. You can adjust this resolution using the model configuration:

```yaml
config:
  init:
    resample:
      timesteps: 6h
```

This example resamples all time series data to 6-hourly intervals. Any "pandas-compatible rule describing the target resolution" can be specified. Additional dimensions with datetime types can also be resampled.

## Time Clustering

Representative day clustering is possible by loading a file that maps dates to representative days:

```yaml
config:
  init:
    time_cluster: cluster_days_param
data_tables:
  cluster_days:
    data: /path/to/cluster_days.csv
    rows: timesteps
    add_dims:
      parameters: cluster_days_param
```

### Storage Between Representative Days

When using representative days, you may want to enable constraints based on research by Kotzur et al. These improve carrier storage modeling between representative days by introducing the `storage_inter_cluster` decision variable, which tracks storage across all original timeseries dates. Include `storage_inter_cluster` in your additional math configuration to enable this.

### Tools for Clustering

Calliope no longer provides built-in representative day inference. Recommended external tools include:

- **tsam**: Purpose-built for large-scale energy system models
- **scikit-learn**: General machine learning library with clustering capabilities
- **tslearn**: Timeseries-focused machine learning library

### Example Using tsam

The documentation provides a complete Python example demonstrating how to cluster timeseries using tsam, generate representative dates, and save the results to CSV for use with Calliope.

### Important Notes

- Resampling occurs before clustering when both are applied
- Clustered timesteps receive weights based on represented time periods
- Costs are multiplied by weights, but production values are not scaled
- Levelized costs and capacity factors account for weighting and are consistent
