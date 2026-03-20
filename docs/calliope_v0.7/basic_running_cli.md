# Running a Model via the Command Line

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/basic/running-cli/

## Basic Syntax

The fundamental command structure is:

```
$ calliope run testmodel/model.yaml --save_netcdf=results.nc
```

## Command Options

The `calliope run` command supports these options:

- **`--save_netcdf={filename.nc}`**: Exports the complete model and results to a NetCDF file. This approach is recommended as it maintains data integrity and enables later model reconstruction for additional analysis.

- **`--save_csv={directory name}`**: Writes results as CSV files to a specified directory, useful for further processing in spreadsheet applications.

- **`--debug`**: Activates debug mode to display additional internal details, helping diagnose model failures.

- **`--scenario={scenario}`** and **`--override_dict={yaml_string}`**: Applies scenarios or overrides to the model (see section below).

- **`--help`**: Displays all available options.

Multiple save options can be combined:

```
$ calliope run testmodel/model.yaml --save_netcdf=results.nc --save_csv=outputs
```

**Important:** By default, the command-line tool does not save results—you must explicitly specify a save option.

## Applying Scenarios or Overrides

The `--scenario` option accepts:

1. A scenario name from model configuration: `--scenario=my_scenario`
2. A single override name: `--scenario=my_override`
3. Multiple comma-separated overrides: `--scenario=my_override_1,my_override_2`

Options 2 and 3 create temporary scenarios on-the-fly without formal definition.

### Example Usage

```
$ calliope run testmodel/model.yaml --scenario=milp --save_netcdf=results.nc
```

If both a scenario and override share the same name, Calliope raises an error for disambiguation.

### Using YAML Overrides

Pass inline YAML strings via `--override_dict`, applied after `--scenario`:

```
$ calliope run testmodel/model.yaml --override_dict="{'init.subset.timesteps': ['2005-01-01', '2005-01-31']}" --save_netcdf=results.nc
```
