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
    from calliomapper.vocabulary import PROV
    component = ctx.components['region1', 'ccgt']
    definition = ctx.graph.value(component, PROV.wasDerivedFrom)
    assert definition != component
    assert (definition, RDF.type, OBO.IAO_0000030) in ctx.graph
    assert (definition, RDF.type, OC.CalliopeTechnology) not in ctx.graph


def test_stable_structure_records_actual_files_and_unknown_executable_version():
    from calliomapper.vocabulary import PROV
    ctx = MappingContext(SavedModel(ROOT / 'examples/calliope-0.7.0/urban_scale/results_directory'), 'urn:test:stable:')
    add_structure(ctx)
    source_paths = {str(value) for value in ctx.graph.objects(None, OC.sourcePath)}
    assert {'inputs_active.csv', 'inputs_link_from.csv', 'inputs_link_to.csv'} <= source_paths
    assert 'inputs_definition_matrix.csv' not in source_paths
    software = ctx.graph.value(ctx.execution, PROV.wasAssociatedWith)
    assert str(ctx.graph.value(software, RDFS.label)) == 'Calliope (producing version not recorded in saved export)'
