"""Map selected saved arrays without reconstructing or solving a Calliope model."""

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import json

from rdflib import Literal, RDF, RDFS, XSD

from calliomapper.vocabulary import OC, OEO, OBO, DCT


VARIABLES = {
    "capacities": {
        "inputs": ("flow_cap_max", "storage_cap_max", "flow_in_eff", "flow_out_eff"),
        "results": ("flow_cap", "storage_cap"),
    },
    "costs": {
        "inputs": ("cost_flow_cap", "cost_storage_cap"),
        "results": ("cost",),
    },
}
COORDINATE_PROPERTIES = {
    "carriers": OC.carrierIndex,
    "costs": OC.costIndex,
    "timesteps": OC.timeIndexLabel,
}
DIMENSIONS = {"nodes", "techs", "carriers", "costs", "timesteps"}


def _text(value):
    return Literal(str(value), datatype=XSD.string)


def _number(value):
    try:
        number = Decimal(str(value))
        return number if number.is_finite() else None
    except InvalidOperation:
        return None


def _omit(ctx, group, variable, reason, coordinates=None):
    item = {"group": group, "variable": variable, "reason": reason}
    if coordinates is not None:
        item["coordinates"] = coordinates
    ctx.report.setdefault("omissions", []).append(item)


def _dimension(ctx, group, variable):
    mathematics = ctx.source.attrs.get("math", {}).get("build", {})
    sections = ("parameters",) if group == "inputs" else ("variables", "global_expressions")
    for section in sections:
        unit = mathematics.get(section, {}).get(variable, {}).get("unit")
        if unit:
            return {
                "power.": "power", "energy.": "energy", "unitless.": "dimensionless",
                r"$\frac{\{cost}}{\text{power}}$": "cost / power",
                r"$\frac{\{cost}}{\text{energy}}$": "cost / energy",
            }.get(unit, unit)
    return None


def _rows(ctx, group, variable, temporal=False):
    filename = f"{group}_{variable}.csv"
    if filename not in ctx.source.files:
        _omit(ctx, group, variable, "The saved export has no file for this selected variable.")
        return []
    rows = ctx.source.rows(group, variable)
    if not rows:
        _omit(ctx, group, variable, "The saved array has no rows.")
        return []
    dimensions = set(rows[0]) - {variable}
    unsupported = dimensions - DIMENSIONS
    if unsupported:
        _omit(ctx, group, variable, "Unsupported coordinates: " + ", ".join(sorted(unsupported)))
        return []
    if not temporal and "timesteps" in dimensions:
        _omit(ctx, group, variable, "Time-dependent values are not supported in this numerical group.")
        return []
    if variable in ("cost", "cost_flow_cap", "cost_storage_cap") and "costs" not in dimensions:
        _omit(ctx, group, variable, "The required cost coordinate is absent.")
        return []
    if variable in ("storage_cap", "cost") and "carriers" in dimensions:
        _omit(ctx, group, variable, "This carrier-indexed variant is outside the evaluated ontology profile.")
        return []
    required = {"nodes", "techs"} if group == "results" else set()
    if group == "results" and variable in ("flow_cap", "flow_out"):
        required.add("carriers")
    if temporal:
        required.add("timesteps")
    if not required <= dimensions:
        _omit(ctx, group, variable, "Required source coordinates are absent: " + ", ".join(sorted(required - dimensions)))
        return []
    return rows


def _components(ctx, coordinates):
    return [
        (key, component) for key, component in ctx.components.items()
        if ("nodes" not in coordinates or coordinates["nodes"] == key[0])
        and ("techs" not in coordinates or coordinates["techs"] == key[1])
    ]


def _context(ctx, record, variable, coordinates, component):
    graph = ctx.graph
    graph.add((record, OC.sourceKey, _text(variable)))
    graph.add((record, OC.forComponent, component))
    graph.add((record, OC.inConfiguration, ctx.configuration))
    for coordinate, predicate in COORDINATE_PROPERTIES.items():
        if coordinate in coordinates:
            graph.add((record, predicate, _text(coordinates[coordinate])))


def _record(ctx, group, variable, row, key, component, series=None):
    coordinates = {name: value for name, value in row.items() if name != variable}
    value = _number(row[variable])
    if value is None:
        _omit(ctx, group, variable, "The value is missing, non-numeric or infinite; no numerical record was created.", coordinates)
        return
    context = ctx.configuration if group == "inputs" else ctx.execution
    identity = (str(context), variable, *key, json.dumps(coordinates, sort_keys=True))
    record = ctx.iri("input" if group == "inputs" else "result", *identity)
    datum = ctx.iri("datum", str(record))
    filename = f"{group}_{variable}.csv"
    revision = ctx.revision(filename)
    graph = ctx.graph
    already_present = (record, OC.hasDatum, datum) in graph
    for entity in (record, datum):
        graph.add((entity, RDF.type, OBO.IAO_0000030))
        graph.add((entity, OC.sourceRevision, revision))
    graph.add((record, RDF.type, OC.InputAssignment if group == "inputs" else OC.ResultRecord))
    graph.add((datum, RDF.type, OBO.IAO_0000027))
    _context(ctx, record, variable, coordinates, component)
    graph.add((record, OC.hasDatum, datum))
    graph.add((record, OC.sourceLocator, _text("; ".join(f"{name}={value}" for name, value in coordinates.items()) + f"; column={variable}")))
    graph.add((datum, OC.reportedNumericValue, Literal(value, datatype=XSD.decimal)))
    dimension = _dimension(ctx, group, variable)
    if dimension:
        graph.add((record, OC.quantityDimension, _text(dimension)))
    if group == "inputs":
        graph.add((datum, RDF.type, OEO.OEO_00030029))
        graph.add((datum, OEO.OEO_00020189, ctx.execution))
        graph.add((ctx.execution, OEO.OEO_00140093, datum))
    else:
        graph.add((datum, RDF.type, OEO.OEO_00020013))
        graph.add((datum, OEO.OEO_00020190, ctx.execution))
        graph.add((ctx.execution, OEO.OEO_00140094, datum))
        graph.add((record, OEO.OEO_00020190, ctx.execution))
        if series is not None:
            graph.add((record, OC.inSeries, series))
    counts = ctx.report.setdefault("numerical_records", {})
    count_key = f"{group}.{variable}"
    if not already_present:
        counts[count_key] = counts.get(count_key, 0) + 1


def _aggregation_limitation(ctx):
    """Require the evaluated base mathematical meaning, not just a familiar name."""
    init = ctx.source.attrs.get("config", {}).get("init", {})
    if init.get("mode") != "base" or init.get("extra_math") or init.get("math_paths"):
        return "Automatic energy summaries are not supported for custom mathematics or non-base mode."
    version = ctx.source.version
    flow_conditions = {
        "0.7.0.dev7": "carrier_out",
        "0.7.0": "carrier_out AND not (one_way AND map_dim(nodes, link_from)==True)",
    }
    if version not in flow_conditions:
        return "Automatic energy summaries have not been evaluated for this saved Calliope format."
    mathematics = ctx.source.attrs.get("math", {}).get("build", {})
    flow = mathematics.get("variables", {}).get("flow_out", {})
    capacity = mathematics.get("variables", {}).get("flow_cap", {})
    constraint = mathematics.get("constraints", {}).get("flow_out_max", {})
    if version == "0.7.0":
        # Stable CSV exports omit unset values; these are the 0.7.0 schema defaults.
        flow = {"active": True, "domain": "real", **flow}
        constraint = {"active": True, "sub_expressions": {}, "slices": {}, **constraint}
        constraint["equations"] = [
            {"where": "True", **equation} for equation in constraint.get("equations", [])
        ]
    dimensions = ["nodes", "techs", "carriers", "timesteps"]
    expected_flow = {"active": True, "foreach": dimensions, "where": flow_conditions[version], "unit": "energy", "domain": "real", "bounds": {"max": float("inf"), "min": 0}}
    expected_constraint = {
        "active": True, "foreach": dimensions, "where": "carrier_out", "sub_expressions": {}, "slices": {},
        "equations": [{"where": "True", "expression": "flow_out <= flow_cap * timestep_resolution * flow_out_parasitic_eff"}],
    }
    if any(flow.get(key) != value for key, value in expected_flow.items()) or any(constraint.get(key) != value for key, value in expected_constraint.items()) or capacity.get("unit") != "power":
        return "The saved flow_out definition and capacity equation do not match the evaluated energy-per-timestep interpretation."
    parameters = mathematics.get("parameters", {})
    if parameters.get("timestep_weights", {}).get("unit") != "unitless." or parameters.get("timestep_resolution", {}).get("unit") != "hours.":
        return "The saved weight or duration interpretation does not match the evaluated temporal metadata."
    return None


def _time_values(ctx, variable):
    filename = f"inputs_{variable}.csv"
    if filename not in ctx.source.files:
        return None
    rows = ctx.source.rows("inputs", variable)
    if not rows or any(set(row) != {"timesteps", variable} for row in rows):
        return None
    values = {row["timesteps"]: _number(row[variable]) for row in rows}
    if len(values) != len(rows) or any(value is None or value < 0 or (variable == "timestep_resolution" and value == 0) for value in values.values()):
        return None
    return values


def _series(ctx, rows, aggregate=True):
    groups = defaultdict(list)
    for row in rows:
        if set(row) != {"nodes", "techs", "carriers", "timesteps", "flow_out"}:
            _omit(ctx, "results", "flow_out", "The series requires exactly node, technology, carrier and timestep coordinates.")
            return {}
        groups[(row["nodes"], row["techs"], row["carriers"])].append(row)
    series_by_coordinates = {}
    limitation = _aggregation_limitation(ctx)
    weights = _time_values(ctx, "timestep_weights")
    durations = _time_values(ctx, "timestep_resolution")
    for (node, technology, carrier), values in groups.items():
        coordinates = {"nodes": node, "techs": technology, "carriers": carrier}
        component = ctx.components.get((node, technology))
        if component is None:
            _omit(ctx, "results", "flow_out", "The source row has no active component.", coordinates)
            continue
        series = ctx.iri("series", str(ctx.execution), node, technology, carrier, "flow_out")
        coverage = ctx.iri("index-description", str(series))
        revision = ctx.revision("results_flow_out.csv")
        labels = [row["timesteps"] for row in values]
        graph = ctx.graph
        for kind in (OC.TimeSeriesRecord, OBO.IAO_0000030):
            graph.add((series, RDF.type, kind))
        _context(ctx, series, "flow_out", coordinates, component)
        graph.add((series, OC.sourceRevision, revision))
        graph.add((series, OEO.OEO_00020190, ctx.execution))
        graph.add((series, OC.sourceLocator, _text(f"nodes={node}; techs={technology}; carriers={carrier}; timesteps=all saved coordinates; column=flow_out")))
        graph.add((series, OC.hasIndexDescription, coverage))
        for kind in (OEO.OEO_00000119, OBO.IAO_0000030):
            graph.add((coverage, RDF.type, kind))
        graph.add((coverage, OC.firstIndexLabel, _text(labels[0])))
        graph.add((coverage, OC.lastIndexLabel, _text(labels[-1])))
        graph.add((coverage, OC.indexCount, Literal(len(labels), datatype=XSD.integer)))
        graph.add((coverage, OC.sourceRevision, revision))
        graph.add((coverage, RDFS.comment, _text("Labels retain the saved CSV coordinate order. They do not assert interval boundaries, a timezone or execution wall-clock dates.")))
        series_by_coordinates[(node, technology, carrier)] = series
        if not aggregate:
            continue
        if limitation:
            _omit(ctx, "results", "flow_out", limitation, coordinates)
            continue
        if weights is None or durations is None or set(labels) != set(weights) or set(labels) != set(durations) or len(set(labels)) != len(labels):
            _omit(ctx, "results", "flow_out", "No summary: complete unique matching timesteps, finite non-negative weights and positive durations are required.", coordinates)
            continue
        numbers = [_number(row["flow_out"]) for row in values]
        if any(number is None for number in numbers):
            _omit(ctx, "results", "flow_out", "No summary: the source series contains missing, non-numeric or infinite values.", coordinates)
            continue
        total = sum((number * weights[label] for number, label in zip(numbers, labels)), Decimal(0))
        _summary(ctx, series, coverage, revision, component, coordinates, total)
    ctx.report["external_output_series"] = len(series_by_coordinates)
    return series_by_coordinates


def _summary(ctx, series, coverage, revision, component, coordinates, total):
    graph = ctx.graph
    activity = ctx.iri("aggregation", str(getattr(ctx, "export_activity", ctx.execution)), str(series))
    summary = ctx.iri("aggregate-result", str(activity))
    datum = ctx.iri("datum", str(summary))
    method = ctx.iri("aggregation-method", str(summary))
    for entity in (summary, datum, method):
        graph.add((entity, RDF.type, OBO.IAO_0000030))
    graph.add((summary, RDF.type, OC.AggregatedResultRecord))
    _context(ctx, summary, "flow_out", coordinates, component)
    graph.add((summary, OC.quantityDimension, _text("energy")))
    graph.add((summary, OC.summarisesSeries, series))
    graph.add((summary, DCT.source, series))
    graph.add((summary, OC.hasIndexDescription, coverage))
    graph.add((summary, OC.hasAggregationMethod, method))
    graph.add((summary, OC.hasDatum, datum))
    graph.add((datum, OC.reportedNumericValue, Literal(total, datatype=XSD.decimal)))
    graph.add((summary, OEO.OEO_00020190, activity))
    graph.add((activity, RDF.type, OBO.BFO_0000015))
    graph.add((activity, RDF.type, OEO.OEO_00000124))
    graph.add((activity, OEO.OEO_00140093, series))
    graph.add((activity, OEO.OEO_00140093, revision))
    graph.add((activity, OEO.OEO_00140094, summary))
    graph.add((method, RDF.type, OEO.OEO_00000119))
    graph.add((method, OC.aggregationFormula, _text("sum_i flow_out[i] * timestep_weights[i]")))
    graph.add((method, OC.durationTreatment, _text("flow_out already represents energy per timestep; duration is not multiplied again. The sum covers the complete saved index with recorded weights, without annualisation.")))
    for filename in ("inputs_timestep_weights.csv", "inputs_timestep_resolution.csv", "attrs.yaml"):
        source = ctx.revision(filename)
        graph.add((method, OC.sourceRevision, source))
        graph.add((activity, OEO.OEO_00140093, source))
    ctx.report["energy_summaries"] = ctx.report.get("energy_summaries", 0) + 1


def add_quantities(ctx, groups, time_points=None):
    """Add supported quantities and report omissions; source units remain unasserted.

    ``time_points`` selectors use saved CSV coordinate names and a ``timesteps``
    list. Numerical groups never expand time-dependent arrays by default.
    """
    if time_points is not None and (not isinstance(time_points, list) or not all(isinstance(selector, dict) for selector in time_points)):
        raise ValueError("Time-point selections must be a list of selector mappings.")
    for selection in sorted(groups & VARIABLES.keys()):
        for group, variables in VARIABLES[selection].items():
            for variable in variables:
                for row in _rows(ctx, group, variable):
                    coordinates = {name: value for name, value in row.items() if name != variable}
                    components = _components(ctx, coordinates)
                    if not components:
                        _omit(ctx, group, variable, "The source row has no active component.", coordinates)
                    for key, component in components:
                        _record(ctx, group, variable, row, key, component)
    selectors = time_points or []
    need_output_series = "energy" in groups or any(selector.get("group") == "results" and selector.get("variable") == "flow_out" for selector in selectors)
    output_rows = _rows(ctx, "results", "flow_out", temporal=True) if need_output_series else []
    if "energy" not in groups:
        output_selectors = [selector for selector in selectors if selector.get("group") == "results"]
        output_rows = [row for row in output_rows if any(
            all(row.get(key) == selector[key] for key in ("nodes", "techs", "carriers") if key in selector)
            for selector in output_selectors
        )]
    series = _series(ctx, output_rows, aggregate="energy" in groups) if need_output_series else {}
    for selector in selectors:
        group, variable = selector.get("group"), selector.get("variable")
        if (group, variable) not in (("inputs", "sink_use_equals"), ("results", "flow_out")):
            raise ValueError("Time-point selection supports inputs.sink_use_equals or results.flow_out only.")
        if set(selector) - {"group", "variable", "nodes", "techs", "carriers", "timesteps"}:
            raise ValueError("A time-point selector contains unsupported fields.")
        labels = selector.get("timesteps")
        if not isinstance(labels, list) or not labels or not all(isinstance(label, str) for label in labels):
            raise ValueError("A time-point selector requires a non-empty list of timestep labels.")
        rows = output_rows if group == "results" else _rows(ctx, group, variable, temporal=True)
        matched = set()
        for row in rows:
            if row["timesteps"] not in labels or any(row.get(key) != selector[key] for key in ("nodes", "techs", "carriers") if key in selector):
                continue
            matched.add(row["timesteps"])
            for key, component in _components(ctx, row):
                source_series = series.get((*key, row.get("carriers"))) if group == "results" else None
                if group == "results" and source_series is None:
                    continue
                _record(ctx, group, variable, row, key, component, source_series)
        if set(labels) - matched:
            raise ValueError("Selected timesteps did not match source rows: " + ", ".join(sorted(set(labels) - matched)))
