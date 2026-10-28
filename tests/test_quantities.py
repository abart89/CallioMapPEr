"""Values below are independent acceptance anchors from the saved example files."""

import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from rdflib import Graph, Literal, RDF, URIRef, XSD

from calliomapper.mapper.quantities import add_quantities
from calliomapper.vocabulary import OC, OEO, OBO, PROV

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class Source:
    def __init__(self, example):
        self.path = EXAMPLES / example / "results_directory"
        self.attrs = yaml.safe_load((self.path / "attrs.yaml").read_text())
        self.version = self.attrs.get("runtime", {}).get("calliope_version_initialised") or self.attrs["config"]["init"].get("calliope_version")
        self.files = {path.name for path in self.path.glob("*")}
        self.overrides = {}

    def rows(self, group, variable):
        if (group, variable) in self.overrides:
            return self.overrides[group, variable]
        with (self.path / f"{group}_{variable}.csv").open() as stream:
            return list(csv.DictReader(stream))

    def file_hash(self, filename):
        return hashlib.sha256((self.path / filename).read_bytes()).hexdigest()


class Context:
    def __init__(self, example="national_scale"):
        self.source = Source(example)
        self.graph = Graph()
        self.report = {}
        self.configuration = self.iri("configuration")
        self.model = self.iri("model")
        self.execution = self.iri("execution")
        self.export_activity = self.iri("export")
        self.components = {
            (row["nodes"], row["techs"]): self.iri("component", row["nodes"], row["techs"])
            for row in self.source.rows("results", "flow_cap")
        }
        self.graph.add((self.configuration, RDF.type, OC.ConfigurationSpecification))
        self.graph.add((self.model, RDF.type, OEO.OEO_00000274))
        for kind in (PROV.Activity, OEO.OEO_00000275, OBO.BFO_0000015):
            self.graph.add((self.execution, RDF.type, kind))
        self.graph.add((self.execution, OC.usesConfiguration, self.configuration))
        self.graph.add((self.execution, OC.executionStatus, Literal("solved")))
        for (node, _), component in self.components.items():
            node_iri = self.iri("node", node)
            self.graph.add((node_iri, RDF.type, OC.CalliopeNetworkNode))
            self.graph.add((node_iri, OC.inConfiguration, self.configuration))
            self.graph.add((node_iri, OC.sourceKey, Literal(node, datatype=XSD.string)))
            self.graph.add((node_iri, OBO.BFO_0000050, self.model))
            self.graph.add((component, RDF.type, OEO.OEO_00000276))
            self.graph.add((component, OC.inConfiguration, self.configuration))

    def iri(self, kind, *keys):
        suffix = hashlib.sha256(json.dumps(keys).encode()).hexdigest()[:24]
        return URIRef(f"https://example.org/quantities/{kind}/{suffix}")

    def revision(self, filename):
        revision = self.iri("revision", filename)
        artifact = self.iri("file", filename)
        for entity in (revision, artifact):
            self.graph.add((entity, RDF.type, PROV.Entity))
        self.graph.add((revision, PROV.specializationOf, artifact))
        self.graph.add((revision, OC.sourcePath, Literal(filename, datatype=XSD.string)))
        self.graph.add((revision, OC.contentSHA256, Literal(self.source.file_hash(filename), datatype=XSD.string)))
        return revision


def records(ctx, kind, variable, node, technology):
    return [record for record in ctx.graph.subjects(RDF.type, kind)
            if ctx.graph.value(record, OC.sourceKey) == Literal(variable, datatype=XSD.string)
            and ctx.graph.value(record, OC.forComponent) == ctx.components[node, technology]]


def value(ctx, record):
    return ctx.graph.value(ctx.graph.value(record, OC.hasDatum), OC.reportedNumericValue).toPython()


def test_capacity_override_and_storage_preserve_source_dimensions():
    ctx = Context()
    add_quantities(ctx, {"capacities"})
    bound, = records(ctx, OC.InputAssignment, "flow_cap_max", "region1", "ccgt")
    result, = records(ctx, OC.ResultRecord, "flow_cap", "region1", "ccgt")
    storage, = records(ctx, OC.ResultRecord, "storage_cap", "region2", "battery")
    assert value(ctx, bound) == value(ctx, result) == Decimal("30000")
    assert bound != result
    assert value(ctx, storage) == Decimal("5239.2461")
    assert ctx.graph.value(storage, OC.carrierIndex) is None
    assert ctx.graph.value(bound, OC.carrierIndex) is None
    assert str(ctx.graph.value(result, OC.carrierIndex)) == "power"
    assert not list(ctx.graph.triples((None, OEO.OEO_00040010, None)))
    assert any("infinite" in item["reason"] for item in ctx.report["omissions"])


def test_technology_only_input_is_applied_without_inventing_source_coordinates():
    ctx = Context()
    add_quantities(ctx, {"capacities"})
    efficiency, = records(ctx, OC.InputAssignment, "flow_in_eff", "region2", "battery")
    assert value(ctx, efficiency) == Decimal("0.95")
    assert str(ctx.graph.value(efficiency, OC.sourceLocator)) == "techs=battery; column=flow_in_eff"


def test_urban_carriers_and_distinct_cost_coefficients():
    ctx = Context("urban_scale")
    add_quantities(ctx, {"capacities", "costs"})
    capacity = records(ctx, OC.ResultRecord, "flow_cap", "X1", "chp")
    by_carrier = {str(ctx.graph.value(record, OC.carrierIndex)): value(ctx, record) for record in capacity}
    assert by_carrier == {"electricity": Decimal("260.9467"), "heat": Decimal("208.75736"), "gas": Decimal("644.31283")}
    for node, expected in (("X2", "43.1"), ("X3", "78.0")):
        coefficient, = records(ctx, OC.InputAssignment, "cost_flow_cap", node, "boiler")
        assert value(ctx, coefficient) == Decimal(expected)
        assert str(ctx.graph.value(coefficient, OC.costIndex)) == "monetary"
        assert str(ctx.graph.value(coefficient, OC.carrierIndex)) == "heat"
    total, = records(ctx, OC.ResultRecord, "cost", "N1", "N1_to_X2")
    assert value(ctx, total) == Decimal("0.05167889431342691")
    assert ctx.graph.value(total, OC.carrierIndex) is None
    assert not list(ctx.graph.triples((None, OEO.OEO_00040010, None)))


def test_default_energy_retains_series_and_computes_known_total_without_points():
    ctx = Context()
    add_quantities(ctx, {"energy"})
    summary, = records(ctx, OC.AggregatedResultRecord, "flow_out", "region1", "ccgt")
    assert value(ctx, summary) == Decimal("3408773.846")
    assert not list(ctx.graph.subjects(RDF.type, OC.ResultRecord))
    series = ctx.graph.value(summary, OC.summarisesSeries)
    assert ctx.graph.value(series, PROV.wasGeneratedBy) == ctx.execution
    activity = ctx.graph.value(summary, PROV.wasGeneratedBy)
    assert activity != ctx.execution
    assert (activity, PROV.used, series) in ctx.graph
    coverage = ctx.graph.value(series, OC.hasIndexDescription)
    assert ctx.graph.value(coverage, OC.indexCount).toPython() == 120
    assert ctx.graph.value(summary, OC.hasIndexDescription) == coverage


def test_non_unit_weights_are_used_and_duration_is_not_applied_twice():
    ctx = Context()
    rows = ctx.source.rows("results", "flow_out")[:2]
    labels = [row["timesteps"] for row in rows]
    ctx.source.overrides["results", "flow_out"] = rows
    ctx.source.overrides["inputs", "timestep_weights"] = [
        {"timesteps": labels[0], "timestep_weights": "2"},
        {"timesteps": labels[1], "timestep_weights": "3"},
    ]
    ctx.source.overrides["inputs", "timestep_resolution"] = [
        {"timesteps": label, "timestep_resolution": "4"} for label in labels
    ]
    add_quantities(ctx, {"energy"})
    summary, = records(ctx, OC.AggregatedResultRecord, "flow_out", "region1", "ccgt")
    assert value(ctx, summary) == Decimal("136556.739")


@pytest.mark.parametrize("directory,storage_value,cost_value,energy_value", [
    ("calliope-0.7.0", "5239.246080000004", "1581.3633982540384", "3408773.843940608300"),
    ("calliope-0.7.0-glpk", "5239.24608", "1581.363398254037", "3411944.78014550320"),
])
def test_stable_national_capacities_costs_and_energy_match_saved_results(directory, storage_value, cost_value, energy_value):
    ctx = Context(f"{directory}/national_scale")
    add_quantities(ctx, {"capacities", "costs", "energy"})
    bound, = records(ctx, OC.InputAssignment, "flow_cap_max", "region1", "ccgt")
    capacity, = records(ctx, OC.ResultRecord, "flow_cap", "region1", "ccgt")
    storage, = records(ctx, OC.ResultRecord, "storage_cap", "region2", "battery")
    cost, = records(ctx, OC.ResultRecord, "cost", "region2", "battery")
    summary, = records(ctx, OC.AggregatedResultRecord, "flow_out", "region1", "ccgt")
    assert value(ctx, bound) == value(ctx, capacity) == Decimal("30000.0")
    assert value(ctx, storage) == Decimal(storage_value)
    assert value(ctx, cost) == Decimal(cost_value)
    assert value(ctx, summary) == Decimal(energy_value)
    assert ctx.graph.value(storage, OC.carrierIndex) is None
    assert ctx.graph.value(cost, OC.costIndex) == Literal("monetary", datatype=XSD.string)
    assert str(ctx.graph.value(capacity, OC.quantityDimension)) == "power"
    assert str(ctx.graph.value(summary, OC.quantityDimension)) == "energy"
    assert ctx.report["energy_summaries"] == ctx.report["external_output_series"] == 13
    assert not records(ctx, OC.ResultRecord, "flow_out", "region1", "ccgt")


def test_stable_weighted_summary_does_not_multiply_energy_by_duration_again():
    ctx = Context("calliope-0.7.0/national_scale")
    rows = ctx.source.rows("results", "flow_out")[:2]
    labels = [row["timesteps"] for row in rows]
    ctx.source.overrides["results", "flow_out"] = rows
    ctx.source.overrides["inputs", "timestep_weights"] = [
        {"timesteps": labels[0], "timestep_weights": "2"},
        {"timesteps": labels[1], "timestep_weights": "3"},
    ]
    ctx.source.overrides["inputs", "timestep_resolution"] = [
        {"timesteps": label, "timestep_resolution": "4"} for label in labels
    ]
    add_quantities(ctx, {"energy"})
    summary, = records(ctx, OC.AggregatedResultRecord, "flow_out", "region1", "ccgt")
    assert value(ctx, summary) == Decimal("136556.738823529404")


@pytest.mark.parametrize("directory,capacity_values,cost_value", [
    ("calliope-0.7.0", ("260.9466981088434", "644.3128348366504", "208.75735848707473"), "0.051678895602049"),
    ("calliope-0.7.0-glpk", ("260.946698108843", "644.31283483665", "208.757358487075"), "0.08229885598265695"),
])
def test_stable_urban_carriers_costs_and_custom_mathematics_are_kept_distinct(directory, capacity_values, cost_value):
    ctx = Context(f"{directory}/urban_scale")
    add_quantities(ctx, {"capacities", "costs", "energy"})
    capacities = records(ctx, OC.ResultRecord, "flow_cap", "X1", "chp")
    by_carrier = {str(ctx.graph.value(record, OC.carrierIndex)): value(ctx, record) for record in capacities}
    assert by_carrier == {
        carrier: Decimal(number) for carrier, number in
        zip(("electricity", "gas", "heat"), capacity_values)
    }
    for node, expected in (("X2", "43.1"), ("X3", "78.0")):
        coefficient, = records(ctx, OC.InputAssignment, "cost_flow_cap", node, "boiler")
        assert value(ctx, coefficient) == Decimal(expected)
        assert str(ctx.graph.value(coefficient, OC.costIndex)) == "monetary"
        assert str(ctx.graph.value(coefficient, OC.carrierIndex)) == "heat"
    cost, = records(ctx, OC.ResultRecord, "cost", "N1", "N1_to_X2")
    assert value(ctx, cost) == Decimal(cost_value)
    assert ctx.report["external_output_series"] == 21
    assert not list(ctx.graph.subjects(RDF.type, OC.AggregatedResultRecord))
    assert any("custom mathematics" in item["reason"] for item in ctx.report["omissions"])


@pytest.mark.parametrize("change", ["unknown_version", "changed_equation", "changed_variable", "inactive_constraint"])
def test_stable_summary_requires_evaluated_format_and_unmodified_energy_interpretation(change):
    ctx = Context("calliope-0.7.0/national_scale")
    mathematics = ctx.source.attrs["math"]["build"]
    if change == "unknown_version":
        ctx.source.version = "0.8.0"
    elif change == "changed_equation":
        mathematics["constraints"]["flow_out_max"]["equations"][0]["expression"] = "flow_out <= flow_cap"
    elif change == "changed_variable":
        mathematics["variables"]["flow_out"]["unit"] = "power"
    else:
        mathematics["constraints"]["flow_out_max"]["active"] = False
    add_quantities(ctx, {"energy"})
    assert list(ctx.graph.subjects(RDF.type, OC.TimeSeriesRecord))
    assert not list(ctx.graph.subjects(RDF.type, OC.AggregatedResultRecord))
    assert ctx.report["omissions"]


@pytest.mark.parametrize("change", ["declared_custom", "changed_equation", "changed_variable"])
def test_custom_or_changed_mathematics_retains_series_without_claiming_summaries(change):
    ctx = Context()
    if change == "declared_custom":
        ctx.source.attrs["config"]["init"]["extra_math"] = ["my-equations"]
    elif change == "changed_equation":
        ctx.source.attrs["math"]["build"]["constraints"]["flow_out_max"]["equations"][0]["expression"] = "flow_out <= flow_cap"
    else:
        ctx.source.attrs["math"]["build"]["variables"]["flow_out"]["unit"] = "power"
    add_quantities(ctx, {"energy"})
    assert list(ctx.graph.subjects(RDF.type, OC.TimeSeriesRecord))
    assert not list(ctx.graph.subjects(RDF.type, OC.AggregatedResultRecord))
    assert ctx.report["omissions"]


def test_missing_time_weight_does_not_produce_partial_period_summary():
    ctx = Context()
    ctx.source.overrides["inputs", "timestep_weights"] = ctx.source.rows("inputs", "timestep_weights")[:-1]
    add_quantities(ctx, {"energy"})
    assert list(ctx.graph.subjects(RDF.type, OC.TimeSeriesRecord))
    assert not list(ctx.graph.subjects(RDF.type, OC.AggregatedResultRecord))
    assert any("matching timesteps" in item["reason"] for item in ctx.report["omissions"])


def test_selected_output_and_input_points_have_distinct_roles():
    ctx = Context()
    time = "2005-01-01 00:00:00"
    add_quantities(ctx, set(), time_points=[
        {"group": "results", "variable": "flow_out", "nodes": "region1", "techs": "ccgt", "carriers": "power", "timesteps": [time]},
        {"group": "inputs", "variable": "sink_use_equals", "nodes": "region1", "techs": "demand_power", "timesteps": [time]},
    ])
    result, = records(ctx, OC.ResultRecord, "flow_out", "region1", "ccgt")
    assignment, = records(ctx, OC.InputAssignment, "sink_use_equals", "region1", "demand_power")
    assert value(ctx, result) == Decimal("27936.36")
    assert value(ctx, assignment) == Decimal("25284.48")
    assert ctx.graph.value(result, OC.inSeries) is not None
    assert ctx.graph.value(assignment, OC.inSeries) is None
    assert ctx.graph.value(assignment, OC.carrierIndex) is None
    assert not list(ctx.graph.subjects(RDF.type, OC.AggregatedResultRecord))
    assert len(list(ctx.graph.subjects(RDF.type, OC.TimeSeriesRecord))) == 1
    datum = ctx.graph.value(result, OC.hasDatum)
    assert (ctx.execution, OEO.OEO_00140094, datum) in ctx.graph


def test_unknown_time_selection_fails_instead_of_silently_omitting():
    ctx = Context()
    with pytest.raises(ValueError, match="did not match"):
        add_quantities(ctx, set(), [{"group": "inputs", "variable": "sink_use_equals", "nodes": "missing", "timesteps": ["2005-01-01 00:00:00"]}])


def test_unrecognised_dimension_and_time_dependent_capacity_are_reported():
    ctx = Context()
    ctx.source.overrides["results", "flow_cap"] = [{"nodes": "region1", "techs": "ccgt", "carriers": "power", "investment_year": "2030", "flow_cap": "30000"}]
    ctx.source.overrides["inputs", "flow_cap_max"] = [{"nodes": "region1", "techs": "ccgt", "timesteps": "2005-01-01", "flow_cap_max": "30000"}]
    add_quantities(ctx, {"capacities"})
    assert not records(ctx, OC.ResultRecord, "flow_cap", "region1", "ccgt")
    assert not records(ctx, OC.InputAssignment, "flow_cap_max", "region1", "ccgt")
    assert any("investment_year" in item["reason"] for item in ctx.report["omissions"])
    assert any("Time-dependent" in item["reason"] for item in ctx.report["omissions"])


@pytest.mark.parametrize("selection", [{}, "flow_out", ["flow_out"]])
def test_time_selection_requires_a_list_of_mappings(selection):
    with pytest.raises(ValueError, match="list of selector mappings"):
        add_quantities(Context(), set(), selection)
