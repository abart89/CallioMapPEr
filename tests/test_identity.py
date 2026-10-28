import pytest
from rdflib import URIRef

from calliomapper.identity import entity_iri


def test_entity_kind_and_node_context_prevent_repeated_name_collisions():
    namespace = "https://example.org/research/"
    identifiers = {
        entity_iri(namespace, "node", "plant"),
        entity_iri(namespace, "technology", "plant"),
        entity_iri(namespace, "component", "north", "plant"),
        entity_iri(namespace, "component", "south", "plant"),
    }
    assert len(identifiers) == 4
    assert all(isinstance(identifier, URIRef) for identifier in identifiers)


def test_ordered_keys_and_embedded_separators_cannot_collide():
    namespace = "urn:uuid:418c2679-e337-4f0f-82d3-81c38cd5f39b:"
    identifiers = {
        entity_iri(namespace, "component", "a/b", "c"),
        entity_iri(namespace, "component", "a", "b/c"),
        entity_iri(namespace, "component", "c", "a/b"),
        entity_iri(namespace, "component", "a/b/c"),
    }
    assert len(identifiers) == 4


def test_namespace_isolates_unrelated_exports_and_same_inputs_are_stable():
    first = entity_iri("https://one.example/", "configuration", "unchanged")
    assert first == entity_iri("https://one.example/", "configuration", "unchanged")
    assert first != entity_iri("https://two.example/", "configuration", "unchanged")


@pytest.mark.parametrize("namespace", ["relative/path", "https://example.org/with space", 'https://example.org/<invalid>'])
def test_invalid_namespace_is_rejected(namespace):
    with pytest.raises(ValueError, match="absolute IRI"):
        entity_iri(namespace, "node", "a")


def test_empty_or_non_string_keys_are_rejected():
    with pytest.raises(ValueError, match="non-empty strings"):
        entity_iri("https://example.org/", "node", "")
    with pytest.raises(ValueError, match="non-empty strings"):
        entity_iri("https://example.org/", "node", 1)
