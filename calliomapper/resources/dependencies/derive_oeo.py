#!/usr/bin/env python3
"""Reversibly rename OEO's annotation-only PROV collision; preserve logical vocabulary."""
import hashlib,json
from pathlib import Path
from rdflib import Graph,URIRef,Literal,RDF,RDFS,OWL,Namespace
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'oeo-full.owl'
OLD=URIRef('http://www.w3.org/ns/prov#wasDerivedFrom')
NEW=URIRef('urn:ontocal:dependency:metadata:wasDerivedFrom')
ONT=URIRef('https://openenergyplatform.org/ontology/oeo/')
CANDIDATE=URIRef('urn:ontocal:dependency:oeo-2.12.0-dl');VERSION=URIRef(str(CANDIDATE)+':1')
D=Namespace('http://purl.org/dc/terms/')
EXPECTED_SOURCE_SHA='34176eea0282fbaa5f8a24aec748a72627386f796a513b2d3292bdede758dc03'
def dump(rows):
 # This is a readable audit fragment; blank nodes are local to each file.
 return ''.join(sorted(' '.join(x.n3() for x in t)+' .\n' for t in rows))
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
if sha!=EXPECTED_SOURCE_SHA:raise SystemExit('Unexpected OEO source SHA256: '+sha)
g=Graph().parse(SOURCE,format='xml')
assert (OLD,RDF.type,OWL.AnnotationProperty) in g
assert (OLD,RDF.type,OWL.ObjectProperty) not in g
assert (OLD,RDF.type,OWL.DatatypeProperty) not in g
assert len(list(g.triples((None,OLD,None))))==2087
assert len(list(g.triples((OLD,None,None))))==6
assert len(list(g.triples((None,None,OLD))))==0
h=Graph()
renamed_old=set();renamed_new=set()
for t in g:
 if OLD in t:
  n=tuple(NEW if x==OLD else x for x in t);renamed_old.add(t);renamed_new.add(n);h.add(n)
 else:h.add(t)
header_removed=set(h.triples((ONT,None,None)));header_added=set()
for s,p,o in header_removed:
 h.remove((s,p,o))
 if p not in (OWL.versionIRI,OWL.versionInfo):header_added.add((CANDIDATE,p,o))
header_added|={(CANDIDATE,OWL.versionIRI,VERSION),(CANDIDATE,OWL.versionInfo,Literal('Derived OEO 2.12.0 candidate 1; pending review; not an official OEO release')),(CANDIDATE,D.source,URIRef('https://openenergyplatform.org/ontology/oeo/releases/2.12.0/oeo.owl')),(D.source,RDF.type,OWL.AnnotationProperty),(CANDIDATE,RDFS.comment,Literal('All OEO logical class/object/datatype axioms are retained. OEO annotation-only uses of prov:wasDerivedFrom are renamed to urn:ontocal:dependency:metadata:wasDerivedFrom to avoid collision with the PROV object property. The exact RDF transformation and original source are preserved separately.'))}
for t in header_added:h.add(t)
# Remove/reintroduce only documented changes; the original graph is reconstructible.
actual_removed=set(g)-set(h);actual_added=set(h)-set(g)
expected_removed=renamed_old|header_removed;expected_added=renamed_new|header_added
assert actual_removed==expected_removed-set(h)
assert actual_added==expected_added-set(g)
assert set(g)-actual_removed==set(h)-actual_added
out=ROOT/'derived';out.mkdir(exist_ok=True)
# Transform the original RDF/XML directly. This preserves source blank-node structure
# and produces identical output bytes without expensive RDF graph canonicalisation.
text=SOURCE.read_text()
assert text.count('xmlns:prov="http://www.w3.org/ns/prov#"')==1
text=text.replace('xmlns:prov="http://www.w3.org/ns/prov#"','xmlns:sourceMetadata="urn:ontocal:dependency:metadata:"')
text=text.replace('<prov:wasDerivedFrom','<sourceMetadata:wasDerivedFrom').replace('</prov:wasDerivedFrom','</sourceMetadata:wasDerivedFrom')
assert text.count('rdf:about="'+str(OLD)+'"')==1
text=text.replace('rdf:about="'+str(OLD)+'"','rdf:about="'+str(NEW)+'"')
text=text.replace('<owl:Ontology rdf:about="'+str(ONT)+'">','<owl:Ontology rdf:about="'+str(CANDIDATE)+'">')
text=text.replace('<owl:versionIRI rdf:resource="https://openenergyplatform.org/ontology/oeo/releases/2.12.0/oeo.owl"/>','<owl:versionIRI rdf:resource="'+str(VERSION)+'"/>')
text=text.replace('<owl:versionInfo>2.12.0</owl:versionInfo>','<owl:versionInfo>Derived OEO 2.12.0 candidate 1; pending review; not an official OEO release</owl:versionInfo>')
from xml.sax.saxutils import escape
addition='\n'.join('        <'+('terms:source rdf:resource="'+str(o)+'"/>' if pr==D.source else 'rdfs:comment>'+escape(str(o))+'</rdfs:comment>') for ss,pr,o in sorted(header_added,key=lambda t: tuple(map(str,t))) if pr==D.source or (pr==RDFS.comment and str(o).startswith('All OEO logical')))
assert text.count('</owl:Ontology>')==1
text=text.replace('</owl:Ontology>',addition+'\n    </owl:Ontology>')
if (D.source,RDF.type,OWL.AnnotationProperty) not in g:text=text.replace('</rdf:RDF>','    <owl:AnnotationProperty rdf:about="http://purl.org/dc/terms/source"/>\n</rdf:RDF>')
(out/'oeo-dl.owl').write_text(text)
# The XML and graph transformation agree on the explicit URIs and counts. Full logical
# axiom preservation is independently tested through OWLAPI in the verification runner.
parsed=Graph().parse(out/'oeo-dl.owl',format='xml')
assert len(parsed)==len(h),(len(parsed),len(h))
assert len(list(parsed.triples((None,NEW,None))))==2087
assert (OLD,RDF.type,OWL.AnnotationProperty) not in parsed
assert (CANDIDATE,OWL.versionIRI,VERSION) in parsed
(out/'oeo-removed-triples.ttl').write_text(dump(actual_removed))
(out/'oeo-added-triples.ttl').write_text(dump(actual_added))
(out/'oeo-header-removed.ttl').write_text(dump(header_removed))
(out/'oeo-header-added.ttl').write_text(dump(header_added))
manifest={'source':{'path':'oeo-full.owl','url':'https://github.com/OpenEnergyPlatform/ontology/releases/download/v2.12.0/oeo-full.owl','sha256':sha,'triples':len(g)},'candidate':{'path':'derived/oeo-dl.owl','ontology_iri':str(CANDIDATE),'version_iri':str(VERSION),'sha256':hashlib.sha256((out/'oeo-dl.owl').read_bytes()).hexdigest(),'triples':len(h)},'annotation_rename':{'from':str(OLD),'to':str(NEW),'predicate_uses':2087,'subject_uses':6,'object_uses':0,'changed_triples':len(renamed_old),'original_use':'AnnotationProperty only; no ObjectProperty/DatatypeProperty declaration.'},'header':{'removed_triples':len(header_removed),'added_triples':len(header_added)},'total_delta':{'removed':len(actual_removed),'added':len(actual_added)},'limits':['This changes the annotation vocabulary and ontology header, so it is not RDF-graph equivalence.','No additional logical axiom is deliberately deleted or weakened. OWLAPI comparison separately verifies unannotated logical-axiom preservation.','The original source must remain available and retain its official identity; this candidate does not replace it.']}
(out/'oeo-derivation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'candidate':manifest['candidate'],'delta':manifest['total_delta']}))
