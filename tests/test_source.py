"""Saved exports are read directly; these tests never solve a Calliope model."""

from pathlib import Path
import shutil

import pytest
import yaml

from calliomapper.source import FIXTURE_TESTED_VERSIONS, SavedModel, SourceError


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture
def export(tmp_path):
    """A deliberately small artificial export for invalid-file tests."""
    attrs = {
        "definition": {"nodes": {"site": {"techs": {"plant": None}}}, "techs": {"plant": {"base_tech": "supply"}}},
        "config": {"init": {"name": "Synthetic reader test"}},
        "math": {},
        "runtime": {
            "calliope_version_initialised": "0.7.0",
            "termination_condition": "optimal",
            "timings": {"solve_start": 1000.0, "solve_complete": 1001.0},
        },
    }
    (tmp_path / "attrs.yaml").write_text(yaml.safe_dump(attrs))
    (tmp_path / "inputs_flow_cap_max.csv").write_text("nodes,techs,flow_cap_max\nsite,plant,10\n")
    (tmp_path / "results_flow_cap.csv").write_text("nodes,techs,flow_cap\nsite,plant,8\n")
    (tmp_path / "inputs_active.csv").write_text("nodes,techs,active\nsite,plant,True\n")
    (tmp_path / "inputs_base_tech.csv").write_text("techs,base_tech\nplant,supply\n")
    (tmp_path / "inputs_carrier_in.csv").write_text("nodes,techs,carriers,carrier_in\nsite,plant,electricity,False\n")
    (tmp_path / "inputs_carrier_out.csv").write_text("nodes,techs,carriers,carrier_out\nsite,plant,electricity,True\n")
    return tmp_path


def change_attrs(export, change):
    attrs = yaml.safe_load((export / "attrs.yaml").read_text())
    change(attrs)
    (export / "attrs.yaml").write_text(yaml.safe_dump(attrs))


@pytest.mark.parametrize("directory,version", [("calliope-0.7.0-glpk/", "0.7.0"), ("calliope-0.7.0/", "0.7.0"), ("", "0.7.0.dev7")])
def test_national_saved_override_and_transmission(directory, version):
    model = SavedModel(EXAMPLES / directory / "national_scale/results_directory")
    assert model.version == version
    assert model.techs["ccgt"]["flow_cap_max"] == 40000
    rows = model.rows("inputs", "flow_cap_max")
    effective = [row for row in rows if row.get("nodes") == "region1" and row["techs"] == "ccgt"]
    assert effective == [{"nodes": "region1", "techs": "ccgt", "flow_cap_max": "30000.0"}]
    components = model.active_components()
    assert len(components) == 15
    assert ("region2", "ccgt") not in components
    link = "region1_to_region2"
    assert components[("region1", link)]["remote_node"] == "region2"
    assert components[("region2", link)]["remote_node"] == "region1"
    assert model.rows("inputs", "bigM") == [{"bigM": "1000000.0"}]


@pytest.mark.parametrize("directory", ["calliope-0.7.0-glpk/", "calliope-0.7.0/", ""])
def test_urban_saved_conversion_retains_two_output_carriers(directory):
    model = SavedModel(EXAMPLES / directory / "urban_scale/results_directory")
    components = model.active_components()
    assert len(components) == 26
    assert components[("X1", "chp")] == {
        "base_tech": "conversion", "carrier_in": ["gas"], "carrier_out": ["electricity", "heat"]
    }
    assert ("N1", "X1_to_N1") in components


def test_repeated_read_and_copied_export_keep_identities(export, tmp_path):
    original = SavedModel(export)
    duplicate = export / "copied"
    shutil.copytree(export, duplicate, ignore=shutil.ignore_patterns("copied"))
    copied = SavedModel(duplicate)
    assert copied.configuration_digest == original.configuration_digest
    assert copied.execution_digest == original.execution_digest
    original.rows("results", "flow_cap")
    assert SavedModel(export).configuration_digest == original.configuration_digest


@pytest.mark.parametrize("changed", ["timings", "results"])
def test_new_run_or_new_results_do_not_change_configuration(export, changed):
    original = SavedModel(export)
    if changed == "timings":
        change_attrs(export, lambda attrs: attrs["runtime"]["timings"].update(solve_start=2000, solve_complete=2002))
    else:
        (export / "results_flow_cap.csv").write_text("nodes,techs,flow_cap\nsite,plant,8.000001\n")
    rerun = SavedModel(export)
    assert original.configuration_digest == rerun.configuration_digest
    assert original.execution_digest != rerun.execution_digest


def test_unselected_custom_inputs_still_change_configuration_identity(export):
    original = SavedModel(export)
    (export / "inputs_custom.csv").write_text("custom_dimension,custom\na,1\n")
    changed = SavedModel(export)
    assert changed.configuration_digest != original.configuration_digest
    assert changed.execution_digest != original.execution_digest
    assert changed.rows("results", "flow_cap")[0]["flow_cap"] == "8"
    with pytest.raises(SourceError, match="unsupported dimensions"):
        changed.rows("inputs", "custom")


def test_source_change_after_open_is_rejected(export):
    model = SavedModel(export)
    (export / "results_flow_cap.csv").write_text("nodes,techs,flow_cap\nsite,plant,9\n")
    with pytest.raises(SourceError, match="changed while"):
        model.rows("results", "flow_cap")


@pytest.mark.parametrize("contents,diagnostic", [
    ("nodes,techs,flow_cap\nsite,plant,8\nsite,plant,9\n", "duplicate coordinates"),
    ("nodes,techs,flow_cap\nsite,,8\n", "coordinate is missing"),
    ("nodes,techs,flow_cap\nother,plant,8\n", "unknown node"),
    ("nodes,techs,flow_cap\nsite,unknown,8\n", "unknown technology"),
    ("nodes,techs,flow_cap\nsite,plant,8,extra\n", "expected 3 columns"),
    ("nodes,techs,other_value\nsite,plant,8\n", "coordinate columns"),
    ("0\n8\n9\n", "duplicate coordinates"),
])
def test_invalid_selected_array_is_rejected(export, contents, diagnostic):
    (export / "results_flow_cap.csv").write_text(contents)
    with pytest.raises(SourceError, match=diagnostic):
        SavedModel(export).rows("results", "flow_cap")


@pytest.mark.parametrize("field,value,diagnostic", [
    ("calliope_version_initialised", "0.6.10", "Unsupported producing"),
    ("termination_condition", "infeasible", "successful 'optimal'"),
    ("timings", {}, "Equal numerical results alone"),
    ("timings", {"solve_start": 1001, "solve_complete": 1000}, "Execution identity"),
])
def test_unsupported_or_unidentifiable_execution_is_rejected(export, field, value, diagnostic):
    change_attrs(export, lambda attrs: attrs["runtime"].update({field: value}))
    with pytest.raises(SourceError, match=diagnostic):
        SavedModel(export)


def test_genuine_stable_export_does_not_record_executable_version():
    model = SavedModel(EXAMPLES / "calliope-0.7.0/national_scale/results_directory")
    assert model.version == "0.7.0"
    assert model.recorded_version is None
    assert model.configured_version == "0.7.0"
    assert model.version_evidence.startswith("config.init.calliope_version")
    assert model.version in FIXTURE_TESTED_VERSIONS


def test_stable_export_without_version_uses_identifiable_layout(export):
    change_attrs(export, lambda attrs: attrs["runtime"].pop("calliope_version_initialised"))
    model = SavedModel(export)
    assert model.version == "0.7.0"
    assert model.recorded_version is None
    assert model.version_evidence.startswith("saved activation array layout")


@pytest.mark.parametrize("recorded,filename,contents", [
    ("0.7.0", "inputs_definition_matrix.csv", "nodes,techs,carriers,definition_matrix\nsite,plant,electricity,True\n"),
    ("0.7.0.dev7", "inputs_active.csv", "nodes,techs,active\nsite,plant,True\n"),
])
def test_version_cannot_relabel_a_different_layout(export, recorded, filename, contents):
    (export / "inputs_active.csv").unlink()
    (export / filename).write_text(contents)
    change_attrs(export, lambda attrs: attrs["runtime"].update(calliope_version_initialised=recorded))
    with pytest.raises(SourceError, match="different version's layout"):
        SavedModel(export)


def test_stable_retained_inactive_components_are_excluded(export):
    change_attrs(export, lambda attrs: attrs["definition"]["techs"].update(idle={"base_tech": "supply"}))
    change_attrs(export, lambda attrs: attrs["config"]["init"].update(retain_inactive=True))
    (export / "inputs_active.csv").write_text("nodes,techs,active\nsite,plant,True\nsite,idle,False\n")
    (export / "inputs_base_tech.csv").write_text("techs,base_tech\nplant,supply\nidle,supply\n")
    with (export / "inputs_carrier_out.csv").open("a") as output:
        output.write("site,idle,electricity,True\n")
    assert set(SavedModel(export).active_components()) == {("site", "plant")}


def test_stable_saved_activation_overrides_original_inactive_definition(export):
    # Calliope permits reactivation in the inputs before building the problem.
    change_attrs(export, lambda attrs: attrs["definition"]["techs"]["plant"].update(active=False))
    assert set(SavedModel(export).active_components()) == {("site", "plant")}


@pytest.mark.parametrize("filename,contents,diagnostic", [
    ("inputs_active.csv", "nodes,techs,carriers,active\nsite,plant,electricity,True\n", "exactly these columns"),
    ("inputs_carrier_out.csv", "nodes,techs,carrier_out\nsite,plant,True\n", "carrier coordinates"),
])
def test_stable_structure_requires_correct_dimensions(export, filename, contents, diagnostic):
    (export / filename).write_text(contents)
    with pytest.raises(SourceError, match=diagnostic):
        SavedModel(export).active_components()


def test_missing_metadata_is_rejected(tmp_path):
    with pytest.raises(SourceError, match="Missing saved Calliope metadata"):
        SavedModel(tmp_path)


def test_carrier_must_be_active_in_saved_definition_matrix(export):
    change_attrs(export, lambda attrs: attrs["runtime"].update(calliope_version_initialised="0.7.0.dev7"))
    (export / "inputs_active.csv").unlink()
    (export / "inputs_definition_matrix.csv").write_text("nodes,techs,carriers,definition_matrix\nsite,plant,electricity,True\n")
    (export / "inputs_base_tech.csv").write_text("techs,base_tech\nplant,supply\n")
    (export / "inputs_carrier_in.csv").write_text("nodes,techs,carriers,carrier_in\nsite,plant,electricity,False\n")
    (export / "inputs_carrier_out.csv").write_text("nodes,techs,carriers,carrier_out\nsite,plant,heat,True\n")
    with pytest.raises(SourceError, match="inactive component/carrier"):
        SavedModel(export).active_components()
