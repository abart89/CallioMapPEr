# Helper Functions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/user_defined_math/helper_functions/

Helper functions enable more complex operations within `where` strings and `expression` strings in Calliope's user-defined math. Here's a summary of available functions:

## any

Check if at least one non-NaN value exists in specified dimensions. For example, `any(cost, over=[nodes, techs])` verifies whether the cost variable contains at least one defined value across tech and node combinations.

## defined

Verify non-NaN values along dimensions. Examples include checking if technologies exist within nodes or carriers are defined in tech groups.

## sum

Sum over one or more dimensions of arrays (parameters, decision variables, or global expressions) using the `over=` parameter.

## select_from_lookup_arrays

Apply lookup arrays to data arrays for index mapping operations, particularly useful with time clustering operations.

## get_val_at_index

Access integer indices in dimensions. For instance, `get_val_at_index(timesteps=0)` retrieves the first timestep, while `get_val_at_index(timesteps=-1)` gets the last. Commonly used for applying different expressions at specific timestep positions.

## roll

Shift data in component arrays by N positions along a dimension. The expression `storage == roll(storage, timesteps=1) + 1` mirrors a for-loop statement `storage[t] == storage[t - 1] + 1`.

## default_if_empty

Insert placeholder values when NaN values would otherwise disrupt optimization. Most useful for user-defined parameters and decision variables when sparse arrays cause issues.

## where

Apply conditions to specific components within expressions using `where(<component>, <condition>)`, enabling selective masking and dimension broadcasting.

## group_sum

Sum across grouped dimension members efficiently. Maps combinations to grouping categories, useful for constraining transmission lines or power plant categories.

## group_datetime

Sum variables over time periods (hours, days, weeks). For example, `group_datetime(flow_in, timesteps, date)` sums flow across dates.

## sum_next_n

Sum across rolling windows using `sum_next_n(<component>, <dimension>, <window>)`. Useful for demand-side management and unit commitment constraints.
