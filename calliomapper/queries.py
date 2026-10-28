"""Execute installed competency queries without inference or fixed example IRIs."""

from importlib.resources import files
import re

from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.term import Identifier

from calliomapper.vocabulary import OC


QUERY_FILES = {
    "cq01": "cq01-structure.rq",
    "cq02": "cq02-context.rq",
    "cq03": "cq03-quantities.rq",
    "cq04": "cq04-provenance.rq",
    "cq05": "cq05-justification.rq",
    "cq06": "cq06-comparison.rq",
    "cq07": "cq07-integration.rq",
    "cq08": "cq08-correspondence.rq",
}
QUERY_REQUIREMENTS = {
    "cq01": {
        "saved_information": "The selected system structure, including component and node identifiers.",
        "additional_information": "None for model structure. Names do not identify physical plants.",
        "missing_information": "Unsupported or omitted structural information has no matching row.",
    },
    "cq02": {
        "saved_information": "Execution, configuration, solver and modelled-time metadata where recorded.",
        "additional_information": "Study question, study scope and future-scenario meaning must be supplied when absent from the saved files.",
        "missing_information": "Executions remain visible; unavailable context fields are empty.",
    },
    "cq03": {
        "saved_information": "Selected numerical inputs, outputs and supported calculated summaries.",
        "additional_information": "A particular unit requires an evidenced unit interpretation when the export does not establish it.",
        "missing_information": "Numbers remain visible without an asserted unit. Omitted quantities have no row; consult the export report.",
    },
    "cq04": {
        "saved_information": "Source-file references, recorded execution and automatic graph-generation provenance.",
        "additional_information": "Earlier dataset preparation, responsibility and derivation require recorded or supplied evidence.",
        "missing_information": "Known links remain visible with empty unavailable fields. A sourceRevision link identifies represented file content, not causal derivation.",
    },
    "cq05": {
        "saved_information": "The selected input assignment to which an assumption refers.",
        "additional_information": "An attributed assumption and its connection to an input must be supplied. Reasons and citations are optional supplied records.",
        "missing_information": "No assumption means no answer. An assumption without a reason remains visible with empty reason fields.",
    },
    "cq06": {
        "saved_information": "Successful executions, matched capacity inputs/results, and modelled-time descriptions.",
        "additional_information": "Explicit component correspondence, a common study with reference/alternative scenarios, and supported concrete unit interpretations. Bind runA and runB to select a particular pair.",
        "missing_information": "No comparison row unless prerequisites match. This query compares flow_cap_max/flow_cap or storage_cap_max/storage_cap only. It requires the same supported unit class and label, matching coordinates, and either a shared horizon descriptor or equal complete weight/duration file hashes. No conversion or causal conclusion is performed.",
    },
    "cq07": {
        "saved_information": "Named export graphs retaining model, execution, output and graph-generation identities.",
        "additional_information": "Explicit dataset-revision use and study metadata, plus a separately identified catalogue graph supplying publisher metadata.",
        "missing_information": "Only recorded dataset-revision identities join. Repeated names or other revisions do not establish shared use; missing catalogue/study facts yield no matching row.",
    },
    "cq08": {
        "saved_information": "Model component identifiers.",
        "additional_information": "An attributed, evidenced physical correspondence and its actual, aggregate or hypothetical interpretation.",
        "missing_information": "Components remain visible without claims. An empty claim field does not mean the component has no physical interpretation.",
    },
}
ALIASES = {
    "installed_capacity": ("cq03", {"kind": OC.ResultRecord, "variable": Literal("flow_cap")}),
    "system_costs": ("cq03", {"kind": OC.ResultRecord, "variable": Literal("cost")}),
}
for _alias, (_preset, _) in ALIASES.items():
    QUERY_REQUIREMENTS[_alias] = dict(QUERY_REQUIREMENTS[_preset])

QUERY_REQUIREMENTS = {
    name: "\n".join((
        "Saved information: " + requirement["saved_information"],
        "Additional information: " + requirement["additional_information"],
        "When information is missing: " + requirement["missing_information"],
    )) for name, requirement in QUERY_REQUIREMENTS.items()
}


def run_query(dataset: Graph, preset: str, bindings=None):
    """Return an RDFLib SELECT result over explicit assertions.

    ``preset`` is cq01–cq08, installed_capacity or system_costs. Optional bindings
    name query variables. Use URIRef for entity identifiers; strings are literal
    values. For example, ``bindings={"runA": URIRef(...), "runB": URIRef(...)}``
    selects two runs for cq06. Parameters are passed as RDF terms, never inserted
    into SPARQL text as user values. Named graphs remain intact.
    """
    name = preset.lower().replace("-", "")
    selected = dict(bindings or {})
    if name in ALIASES:
        name, required = ALIASES[name]
        for key, value in required.items():
            if key in selected and selected[key] != value:
                raise ValueError(f"The {preset} preset fixes {key}={value}")
            selected[key] = value
    if name not in QUERY_FILES:
        raise ValueError(f"Unknown query {preset!r}; choose cq01–cq08, installed_capacity or system_costs")
    if name == "cq07" and not isinstance(dataset, Dataset):
        raise ValueError("CQ-07 requires an RDFLib Dataset with separately identified named graphs")
    if isinstance(dataset, Dataset):
        dataset.default_union = True
    query = files("calliomapper").joinpath("query_files", QUERY_FILES[name]).read_text(encoding="utf-8")
    variables = set(re.findall(r"\?([A-Za-z_]\w*)", query))
    if set(selected) - variables:
        raise ValueError("Unknown query variables: " + ", ".join(sorted(set(selected) - variables)))
    parameters, filters = {}, []
    for name, value in selected.items():
        if isinstance(value, (URIRef, BNode)):
            parameters[name] = value
            continue
        parameter = f"__parameter_{name}"
        parameters[parameter] = value if isinstance(value, Identifier) else Literal(value)
        filters.append(f"FILTER (?{name} = ?{parameter})")
    # Value equality accepts both plain and explicit xsd:string literals, which
    # RDFLib otherwise treats as different terms in basic triple-pattern joins.
    if filters:
        query = query.replace("WHERE {", "WHERE {\n  " + "\n  ".join(filters), 1)
    return dataset.query(query, initBindings=parameters)


def get_installed_capacity(graph, technology_type=None):
    """Return direct flow-capacity records; no cross-component sum is inferred."""
    if technology_type is not None:
        raise ValueError("Filter installed_capacity by query variables such as technology or node using run_query(bindings=...)")
    return run_query(graph, "installed_capacity")


def get_system_costs(graph):
    """Return saved component cost records without inventing a currency or sum."""
    return run_query(graph, "system_costs")
