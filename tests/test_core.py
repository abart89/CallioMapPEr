from pathlib import Path
import pytest
from rdflib import RDF, RDFS
from calliomapper.mapper.core import MappingContext, add_structure
from calliomapper.source import SavedModel
from calliomapper.vocabulary import OC, OEO, OBO

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('directory', ['calliope-0.7.0-glpk/', 'calliope-0.7.0/', ''])
def test_effective_urban_structure_and_explicit_shared_typing(directory):
    ctx = MappingContext(SavedModel(ROOT / 'examples' / directory / 'urban_scale/results_directory'), 'urn:test:urban:')
    add_structure(ctx)
    assert len(ctx.nodes) == 4
    assert len(ctx.components) == 26
    chp = ctx.components['X1', 'chp']
    assert (chp, RDF.type, OC.CalliopeConversionTechnology) in ctx.graph
    assert (chp, RDF.type, OEO.OEO_00000276) in ctx.graph
    assert (chp, RDF.type, OBO.IAO_0000030) in ctx.graph
    assert {str(v) for v in ctx.graph.objects(chp, OC.carrierOut)} == {'electricity', 'heat'}
    assert len(list(ctx.graph.triples((None, OC.remoteNode, None)))) == 10
    assert not list(ctx.graph.subjects(RDF.type, OBO.BFO_0000040))


@pytest.mark.parametrize('directory', ['calliope-0.7.0-glpk/', 'calliope-0.7.0/', ''])
def test_technology_definition_is_separate_information(directory):
    ctx = MappingContext(SavedModel(ROOT / 'examples' / directory / 'national_scale/results_directory'), 'urn:test:national:')
    add_structure(ctx)
    from calliomapper.vocabulary import DCT, OBO
    component = ctx.components['region1', 'ccgt']
    definition = ctx.graph.value(component, DCT.source)
    assert definition != component
    assert (definition, RDF.type, OBO.IAO_0000030) in ctx.graph
    assert (definition, RDF.type, OC.CalliopeTechnology) not in ctx.graph


def test_stable_structure_records_actual_files_and_unknown_executable_version():
    from calliomapper.vocabulary import DCT, OBO
    ctx = MappingContext(SavedModel(ROOT / 'examples/calliope-0.7.0/urban_scale/results_directory'), 'urn:test:stable:')
    add_structure(ctx)
    source_paths = {str(value) for value in ctx.graph.objects(None, OC.sourcePath)}
    assert {'inputs_active.csv', 'inputs_link_from.csv', 'inputs_link_to.csv'} <= source_paths
    assert 'inputs_definition_matrix.csv' not in source_paths
    software, = [participant for participant in ctx.graph.objects(ctx.execution, OBO.RO_0000057)
                 if (participant, RDF.type, OBO.IAO_0000010) in ctx.graph]
    assert str(ctx.graph.value(software, RDFS.label)) == 'Calliope (producing version not recorded in saved export)'


@pytest.mark.parametrize('directory, expected_version', [
    ('', '0.7.0.dev7'),
    ('calliope-0.7.0/', None),
    ('calliope-0.7.0-glpk/', None),
])
def test_context_query_reports_only_the_recorded_executable_version(directory, expected_version):
    from calliomapper.queries import run_query
    source = SavedModel(ROOT / 'examples' / directory / 'national_scale/results_directory')
    ctx = MappingContext(source, 'urn:test:software-version:')
    add_structure(ctx)
    answer, = run_query(ctx.graph, 'cq02')
    assert answer.software is not None
    assert source.recorded_version == expected_version
    if expected_version is None:
        assert source.configured_version == source.version == '0.7.0'
        assert answer.softwareVersion is None
    else:
        assert str(answer.softwareVersion) == expected_version
