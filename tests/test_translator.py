import json
from pathlib import Path
import shutil
import yaml
import pytest
from rdflib import Dataset, Graph, RDF, URIRef
from calliomapper import Translator
from calliomapper.vocabulary import OC, PROV
from calliomapper.utils.validation import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]
NATIONAL = ROOT / 'examples/national_scale/results_directory'


@pytest.mark.parametrize('directory', ['calliope-0.7.0-glpk', 'calliope-0.7.0'])
@pytest.mark.parametrize('name', ['national_scale', 'urban_scale'])
def test_stable_report_distinguishes_file_format_from_recorded_execution_version(directory, name):
    translator = Translator(ROOT / 'examples' / directory / name / 'results_directory')
    translator.translate()
    assert translator.report['calliope_format_version'] == '0.7.0'
    assert translator.report['calliope_configured_version'] == '0.7.0'
    assert translator.report['calliope_version'] is None
    assert 'producing version not recorded' in translator.report['calliope_version_evidence']
    assert translator.report['real_fixture_tested_version'] is True
    assert translator.report['shacl'] == 'passed'


@pytest.fixture(scope='module')
def translated():
    t = Translator(NATIONAL, namespace='urn:test:integration:')
    t.translate()
    return t


def test_default_quantities_and_external_arrays(translated):
    graph = translated.translate()
    assert len(list(graph.subjects(RDF.type, OC.TimeSeriesRecord))) == 13
    assert len(list(graph.subjects(RDF.type, OC.AggregatedResultRecord))) == 13
    assert not list(graph.triples((None, OC.timeIndexLabel, None)))
    assert translated.report['numerical_records']['results.flow_cap'] == 15
    assert translated.report['numerical_records']['results.storage_cap'] == 4
    assert translated.report['shacl'] == 'passed'
    assert not list(graph.triples((None, OC.implementsScenario, None)))


def test_save_reuses_namespace_and_source_identities(tmp_path):
    path = tmp_path / 'model.nq'
    first = Translator(NATIONAL, groups={'structure'})
    first.save(path)
    second = Translator(NATIONAL, groups={'structure'})
    second.save(path)
    assert first.namespace == second.namespace
    assert first.context.configuration == second.context.configuration
    assert first.context.execution == second.context.execution
    assert first.context.export_activity != second.context.export_activity
    assert json.loads(Path(str(path) + '.manifest.json').read_text())['namespace'] == first.namespace
    with pytest.raises(ValueError, match='namespace'):
        Translator(NATIONAL, namespace='urn:different:', groups={'structure'}).save(path)
    readback = Dataset(default_union=True).parse(str(path), format='nquads')
    assert len(readback) == len(second.translate())


def test_same_configuration_new_execution_keeps_inputs_distinguishes_results(tmp_path, translated):
    clone = tmp_path / 'rerun'
    shutil.copytree(NATIONAL, clone)
    attrs = yaml.safe_load((clone / 'attrs.yaml').read_text())
    attrs['runtime']['timings']['solve_start'] += 86400
    attrs['runtime']['timings']['solve_complete'] += 86400
    (clone / 'attrs.yaml').write_text(yaml.safe_dump(attrs))
    rerun = Translator(clone, namespace=translated.namespace)
    rerun.translate()
    assert rerun.context.configuration == translated.context.configuration
    assert rerun.context.execution != translated.context.execution
    for cls in (OC.InputAssignment, OC.ResultRecord):
        before = set(translated.translate().subjects(RDF.type, cls))
        after = set(rerun.translate().subjects(RDF.type, cls))
        assert (before == after) if cls == OC.InputAssignment else before.isdisjoint(after)


def test_validation_rejects_missing_execution_configuration(translated):
    graph = Graph()
    for s, p, o, _ in translated.translate().quads():
        graph.add((s, p, o))
    graph.remove((translated.context.execution, OC.usesConfiguration, None))
    with pytest.raises(ValidationError, match='configuration'):
        validate(graph)


def test_synthetic_annotations_separate_and_do_not_change_numerical_data(translated):
    other = Translator(NATIONAL, namespace=translated.namespace, annotations=ROOT / 'examples/annotations/national.yaml')
    graph = other.translate()
    assert other.report['annotation_triples'] > 0
    assert list(graph.triples((None, OC.implementsScenario, None)))
    from collections import Counter
    assert Counter(graph.objects(None, OC.reportedNumericValue)) == Counter(translated.translate().objects(None, OC.reportedNumericValue))
    assert len([g for g in graph.graphs() if len(g)]) == 3


def test_structure_only_no_numeric_records():
    graph = Translator(NATIONAL, groups={'structure'}).translate()
    assert not list(graph.subjects(RDF.type, OC.InputAssignment))
    assert not list(graph.subjects(RDF.type, OC.ResultRecord))
