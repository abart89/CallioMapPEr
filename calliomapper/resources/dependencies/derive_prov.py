#!/usr/bin/env python3
"""Derive the explicitly identified PROV-O candidate; preserve original and exact changes."""
import hashlib,json
from pathlib import Path
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS,OWL
from rdflib.compare import to_canonical_graph
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'prov-o-20130430.owl'
P=Namespace('http://www.w3.org/ns/prov#')
D=Namespace('http://purl.org/dc/terms/')
SOURCE_ONTOLOGY=URIRef('http://www.w3.org/ns/prov-o#')
EXTRA_ONTOLOGY=URIRef('http://www.w3.org/ns/prov#')
CANDIDATE=URIRef('urn:ontocal:dependency:prov-o-20130430-dl')
VERSION=URIRef(str(CANDIDATE)+':1')
EXPECTED_SOURCE_SHA='71ecff298c82b8c12aca0714a7bcbfd0b798cda9a7b3c89d9aeb0ef358cb79d0'
def canonical(graph):
 return ''.join(sorted(to_canonical_graph(graph).serialize(format='nt').splitlines(keepends=True)))
def triples(rows):
 h=Graph()
 for t in rows:h.add(t)
 return canonical(h)
g=Graph().parse(SOURCE,format='xml')
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
# Filled with the inspected frozen-source checksum. Reject changes before deriving.
if source_sha!=EXPECTED_SOURCE_SHA:raise SystemExit('Source SHA256 differs from inspected PROV recommendation: '+source_sha)
h=Graph()
for t in g:h.add(t)
removed_declarations={(P.wasRevisionOf,RDF.type,OWL.AnnotationProperty),(P.specializationOf,RDF.type,OWL.AnnotationProperty)}
relocated={(SOURCE_ONTOLOGY,P.wasRevisionOf,URIRef('http://www.w3.org/ns/prov-o-20120312')),(SOURCE_ONTOLOGY,P.specializationOf,URIRef('http://www.w3.org/ns/prov-o'))}
for t in removed_declarations|relocated:
 if t not in h:raise SystemExit('Expected upstream triple absent: '+str(t))
 h.remove(t)
# The new artifact must not impersonate the W3C ontology. Retain other header annotations,
# but move them to the candidate header, replacing original version/label declarations.
header_removed=set(h.triples((SOURCE_ONTOLOGY,None,None)))|{(EXTRA_ONTOLOGY,RDF.type,OWL.Ontology)}
header_added=set()
for s,p,o in list(h.triples((SOURCE_ONTOLOGY,None,None))):
 h.remove((s,p,o))
 if p not in (OWL.versionIRI,OWL.versionInfo,RDFS.label):header_added.add((CANDIDATE,p,o))
h.remove((EXTRA_ONTOLOGY,RDF.type,OWL.Ontology))
header_added|={(CANDIDATE,RDF.type,OWL.Ontology),(CANDIDATE,OWL.versionIRI,VERSION),(CANDIDATE,RDFS.label,Literal('PROV-O 2013-04-30 derived OWL 2 DL candidate for OntoCal',lang='en')),(CANDIDATE,OWL.versionInfo,Literal('Candidate derivation 1; pending review; not an official W3C release',lang='en')),(CANDIDATE,D.source,URIRef('http://www.w3.org/ns/prov-o-20130430')),(D.source,RDF.type,OWL.AnnotationProperty),(CANDIDATE,RDFS.comment,Literal('Derived from the unchanged W3C PROV-O recommendation. Two duplicate AnnotationProperty declarations are removed; two source-ontology provenance statements are preserved in a separate metadata graph. All vocabulary RDF triples outside the documented changes are retained. This is not a claim of equivalence with the complete original RDF graph.',lang='en'))}
for t in header_added:h.add(t)
out=ROOT/'derived';out.mkdir(exist_ok=True)
(out/'prov-o-dl.ttl').write_text(canonical(h))
(out/'relocated-source-metadata.ttl').write_text(triples(relocated))
(out/'removed-annotation-declarations.ttl').write_text(triples(removed_declarations))
(out/'removed-header-triples.ttl').write_text(triples(header_removed))
(out/'added-header-triples.ttl').write_text(triples(header_added))
expected_removed=removed_declarations|relocated|header_removed
expected_added=header_added
actual_removed=set(g)-set(h);actual_added=set(h)-set(g)
assert actual_removed==expected_removed
assert actual_added==expected_added-set(g)
# Blank nodes in vocabulary axioms are retained unchanged in memory; canonical output makes
# the resulting bytes reproducible across runs, independently of parser blank-node identifiers.
assert set(g)-expected_removed == set(h)-expected_added
manifest={'source':{'path':'prov-o-20130430.owl','url':'https://www.w3.org/ns/prov-o-20130430.owl','sha256':source_sha,'triples':len(g)},'candidate':{'path':'derived/prov-o-dl.ttl','ontology_iri':str(CANDIDATE),'version_iri':str(VERSION),'sha256':hashlib.sha256((out/'prov-o-dl.ttl').read_bytes()).hexdigest(),'triples':len(h)},'changes':{'removed_annotation_declarations':triples(removed_declarations),'relocated_source_metadata':triples(relocated),'removed_header_triples':triples(header_removed),'added_header_triples':triples(header_added),'removed_triples_count':len(actual_removed),'added_triples_count':len(actual_added)},'preservation_check':'Every RDF triple outside the exact documented changes remains present; all original vocabulary class/object/datatype RDF axioms retained. This does not assert full-original semantic equivalence.'}
(out/'derivation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'source_sha256':source_sha,'candidate_sha256':manifest['candidate']['sha256'],'source_triples':len(g),'candidate_triples':len(h),'removed':len(actual_removed),'added':len(actual_added)}))
