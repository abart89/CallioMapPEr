# Comparison of the developer-preview and stable Calliope examples

This is the recorded comparison of the original dev7 outputs and the first stable
0.7.0 outputs prepared with HiGHS. The primary tutorials now use separate
[GLPK examples](../examples/calliope-0.7.0-glpk/README.md). Values and conclusions
below remain specific to the earlier executions.


CallioMapper now has separate saved examples from Calliope `0.7.0.dev7` and
Calliope `0.7.0`. The first version was a development preview of the 0.7 series;
the second is the completed 0.7.0 release. A development preview can differ from
the final release in its configuration syntax, mathematical definitions and
saved output format. Changing a version label would therefore be insufficient.

This comparison was completed on 27 October 2026. It examines the actual source
files, saved input arrays, mathematical definitions and selected numerical
outputs. It supports migration of these examples; it does not establish that
every model expressible in the two releases has identical behaviour.

## Which executions are being compared

| Evidence | Original examples | New stable examples |
| --- | --- | --- |
| Calliope version | `0.7.0.dev7`, recorded in the saved runtime metadata | `0.7.0`, verified from the installed package during preparation and recorded in the preparation manifest |
| Execution | Andrea's existing saved executions | New local executions of the examples distributed with Calliope 0.7.0 |
| Solver and backend | Saved configuration specifies CBC through Pyomo; its solver version was not recorded | HiGHS 1.15.1 through Calliope's native HiGHS backend |
| Termination | Both saved runs report `optimal` | Both new runs report `optimal`, also supported by the solver logs |
| National time coverage | 1–5 January 2005, 120 hourly timesteps | The same 120 timesteps |
| Urban time coverage | 1–2 July 2005, 48 hourly timesteps | The same 48 timesteps |

The stable example sources were copied unchanged from the installed upstream
distribution. Preparation selected the HiGHS backend and solver and enabled
solver logs. It retained the source configurations' time subsets, data tables,
scenario selection and objective. No old result was relabelled as a stable
result.

Stable `attrs.yaml` no longer includes the old
`runtime.calliope_version_initialised` field. Its
`config.init.calliope_version` states the intended configuration version; it is
not independent evidence of which executable produced an arbitrary export.
For our stable examples, the separate [preparation manifest](../examples/calliope-0.7.0/manifest.json)
provides that evidence. The [preparation requirements](../examples/calliope-0.7.0/preparation-requirements.txt)
record the installed Python dependencies.

## Source data and configuration changes

The numerical source data in the compared examples are unchanged. Several
source files nevertheless differ because the release changed how the data are
named and loaded.

| Source change | Finding and consequence |
| --- | --- |
| Data-table configuration | Both examples replace the `data` field with `table`, and the dimension name `parameters` with `inputs`. These changes affect configuration syntax. |
| National time-varying CSV | Only the header identifying the input names changes from `parameters` to `inputs`. Every timestamp, numerical value and source comment is otherwise identical. |
| National costs CSV | The header changes from `parameters` to `inputs`, and the supply-cost column changes from `cost_flow_in` to `cost_source_use`. All cost coefficients and unit comments are unchanged. The CCGT source-use coefficient remains `0.02`. |
| Urban technology definitions | `supply_grid_power` and `supply_gas` replace `cost_flow_in` with `cost_source_use`. The coefficients remain `0.1` and `0.025`. After that name substitution, the complete technology file is identical. |
| Urban data tables and additional mathematics | The demand, PV-resource and electricity-export tables are byte-for-byte identical. `additional_math.yaml` is also identical. |
| National optional clustering scenario | The upstream scenario now explicitly sets `cyclic_storage: false`. Neither compared national execution selects that scenario, so this setting is not applied in these saved runs. |
| Locations and other technology definitions | Both location files and the national technology file are byte-for-byte identical. No plant, node, carrier or link was added by the migration of these example sources. |

The full file-level inventory is in the [stable examples README](../examples/calliope-0.7.0/README.md).
These comparisons distinguish the original source tables from the effective
input arrays saved after Calliope processes them. In those saved arrays, small
numerical differences exist despite identical source values:

- National `source_use_max`: 15 of 360 entries differ, with maximum absolute
  difference `9.7 × 10⁻¹⁷`.
- Urban `sink_use_equals`: 28 of 288 entries differ, with maximum absolute
  difference `2 × 10⁻¹⁴`.

These differences are compatible with floating-point processing or numerical
serialization differences. This comparison does not isolate the exact library
or operation responsible. Other shared input arrays compare equal by coordinate
and value, apart from the intentional movement of supply costs to
`cost_source_use`. Both examples retain identical timestep-resolution and
timestep-weight arrays, with every value equal to `1.0`.

## Mathematical and saved-format changes

The stable release's saved mathematical definitions contain changes beyond the
source-file syntax. The following changes matter for interpreting or reading
these examples.

**Supply costs now have an explicit input name.** In the developer preview,
`cost_flow_in` had two uses: it priced carrier inflow for ordinary technologies,
but priced `source_use` for supply technologies. The stable mathematics uses
`cost_source_use * source_use` for the latter branch. Thus, the example source
files move the same supply-cost coefficients to the name expected by the new
equation. This is a semantic distinction that a reader must preserve; the two
names should not be treated as universally interchangeable.
For example, the urban boiler still uses `cost_flow_in`, because its cost applies
to carrier inflow rather than to an external source consumed by a supply
technology.

**Transmission capacity is expressed differently.** The earlier mathematics
uses a separate `link_flow_cap` variable to connect the endpoint capacities.
The stable mathematics directly equates capacities at the two ends of each
link, per carrier. Consequently, `results_link_flow_cap.csv` is absent from
both stable exports. Endpoint `flow_cap` results remain available. This is a
change in mathematical representation, rather than evidence that a physical
link disappeared.

**The conditions selecting variables and constraints have changed.** Stable
definitions explicitly check carrier availability in several places, and the
flow variables account for one-way links. Conditions for fixed operating
costs and some storage, capacity and demand constraints also differ. Some
previous conditional expressions have been simplified using default values.
These changes preclude a general claim that the two mathematical systems are
identical merely because our selected results are close.

**Active components and links have different saved metadata.** Stable exports
include `inputs_active.csv`, `inputs___active.csv`, `inputs_link_from.csv`,
`inputs_link_to.csv` and `inputs_one_way.csv`. The older
`inputs_definition_matrix.csv` is absent. The stable reader must interpret the
available structural arrays and their coordinates rather than require the old
filename. In these two snapshots, shared carrier arrays retain the same
coordinate/value information.

**Additional postprocessed results are available.** Both stable exports add
`results_total_generation.csv`; the national export also adds curtailment
results. The mathematical metadata now has an explicit `postprocessed`
section. The presence of a new output does not mean that CallioMapper already
maps it. The supported variables remain those documented in the package's
mapping specification.

## Selected numerical comparisons

The following values were read directly from the saved CSV files, independently
of CallioMapper's generated RDF. Totals of `flow_out` are sums over the stated
component and carrier across the saved period. These flows are energy per
timestep in the saved mathematical definitions, and every timestep weight is
one. The table reports the stored numerical scale; it does not infer a currency
or physical unit from the word `monetary` or from a variable name.

| Example and quantity | Developer preview | Stable 0.7.0 |
| --- | ---: | ---: |
| National minimum-cost objective | 277048.4794656496 | 277048.4786392079 |
| National sum of component costs | 277048.4794656495717 | 277048.47863920792625 |
| National `region1 / ccgt / power` capacity | 30000.0 | 30000.0 |
| National `region2 / battery` storage capacity | 5239.2461 | 5239.246080000004 |
| National `region1 / ccgt / power` output total | 3408773.846 | 3408773.843940608300 |
| National `region1_1 / csp / power` output total | 712417.995901 | 712417.99664860467875 |
| National `region2 / battery` component cost | 1581.3634042906438 | 1581.3633982540384 |
| Urban minimum-cost objective | 842.3371966358047 | 842.337196706969 |
| Urban sum of component costs | 842.3371966358047983956 | 842.3371967069690691067 |
| Urban `X1 / chp / electricity` capacity | 260.9467 | 260.9466981088434 |
| Urban `X1 / chp / heat` capacity | 208.75736 | 208.75735848707473 |
| Urban `X1 / chp / electricity` output total | 9214.089218 | 9214.08920462796891 |
| Urban `X1 / chp / heat` output total | 7371.271393 | 7371.27136370237551 |
| Urban `X1 / supply_gas` component cost | 569.1598835643474 | 569.1598848745491 |
| Urban `X2 / pv / electricity` output total | 613.41532465 | 613.4153276085627179 |

The national objective changes by approximately `−0.00082644`; the urban
objective changes by approximately `+0.00000007116`. The selected capacity,
cost and flow results are close, but they are not generally identical. Tests
of the stable export therefore use expectations derived from the stable files,
with documented tolerances where appropriate.

The comparison changes the Calliope release, mathematical implementation,
backend, solver and numerical libraries together. It cannot assign the small
differences specifically to CBC versus HiGHS, to rounding, or to one model
change. Establishing that attribution would require controlled additional
runs. Such runs are unnecessary for checking that CallioMapper accurately
represents the saved stable results, and none were performed for this comparison.

## Preservation and provenance checks

All **139 files** listed in the [original snapshot manifest](../examples/source-manifest.json)
were checked against their recorded SHA-256 hashes and remain unchanged. The
new source and result files also match the hashes in their separate
[preparation manifest](../examples/calliope-0.7.0/manifest.json). That manifest
records 15 source files and 133 saved result files across the two examples.
The source copies were additionally checked against the files in the installed
Calliope 0.7.0 distribution.

The [optional preparation script](../scripts/prepare_stable_examples.py) explains
how to produce another pair of genuine executions in a new directory. Routine
package tests and translations only read the saved exports; they do not run an
optimisation. The old snapshots remain useful evidence for compatibility with
Andrea's original work, while the stable snapshots provide the acceptance
examples for the released version.
