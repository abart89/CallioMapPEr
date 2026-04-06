# positioning.md — Scientific Value and Placement of CallioMapper

*Living document. Rewrite sections as strategy evolves. Last updated: 2026-04-06.*

---

## What this work is, honestly

CallioMapper is a Python library that serializes Calliope v0.7 model files (topology, technologies,
parameters, results) into RDF using a purpose-built ontology (`ontocal:`) that extends OEO via
proper OWL subclassing. At launch it ships with a provenance module (PROV-O attribution and data
sourcing) and a results module (SOSA observations for inputs and outputs). Semantic enrichment
beyond that happens through opt-in extensions.

The scientific contribution is not the serialization. It is what the serialization enables:
- Cross-run queryability over model archives (resilience simulations, sensitivity studies)
- Machine-readable provenance for journal reproducibility requirements
- A foundation for the physical extension: linking model components to real-world infrastructure

The physical extension — demonstrated on the Singapore urban energy system resilience model —
is where the work becomes scientifically novel and distinct from anything in the community.

---

## What this work is not

- A semantic enrichment tool out of the box. Carriers are labels. Technology names are strings.
  The tool does not guess. OEO concrete class alignment is an extension, not built in.
- A cross-framework interoperability layer. Calliope v0.7 only.
- An automated OEP/OEKG submission pipeline at launch.
- Ontology research. The ontocal taxonomy is correct OWL engineering, not a scientific
  contribution in itself.

---

## Target audience

**Primary:** Research groups using Calliope for multi-run studies (resilience simulations,
scenario families, sensitivity analyses) who need structured cross-run querying and/or
machine-readable provenance for publication.

**Secondary:** Projects contributing to the Open Energy Platform / Open Energy Knowledge Graph
ecosystem. The RDF output is OEKG-compatible by design; automated upload is a future extension.

**Not the audience:** Anyone expecting automated semantic enrichment or cross-framework support.

---

## Honest self-assessment of weaknesses (and mitigations)

| Weakness | Mitigation |
| :--- | :--- |
| Calliope is a niche framework — audience ceiling is low | Physical extension + Singapore case opens resilience research community, which is larger |
| SPARQL is a barrier for energy researchers | Ship Python API wrapping common queries; users never write SPARQL directly |
| Provenance module is not novel on its own | It's infrastructure for the physical extension, not the scientific contribution |
| ontocal taxonomy is thin as ontology research | Correct — it's not positioned as ontology research |
| OEKG pathway depends on OEP team endorsement | Validate before it appears prominently in the paper |
| At launch, no real-world example beyond national_scale | Singapore model must be working before JOSS submission |

---

## Publication plan

### Paper 1 — JOSS (or SoftwareX)
**What:** Software tool paper for CallioMapper as a standalone Python package.
**Scope:** Base layer + provenance module + results module. Physical extension mentioned as
planned but not described in detail.
**Narrative:** Statement of need = reproducibility and cross-run queryability gap for Calliope
users. Demonstrated on national_scale (bundled example) and validated on a real urban energy
system model (Singapore, forward reference to Paper 2).
**Venue:** JOSS first choice (no novelty requirement, software quality bar). SoftwareX as
fallback if JOSS scope concerns arise.
**Timing:** Submit after step 3 of the engineering sequence (see below). Preprint first for
fast visibility and to establish a citable DOI before Paper 2 submission.

### Paper 2 — Energy & AI
**What:** Methods + application paper on urban energy system resilience modeling.
**Scope:** Singapore model, resilience simulations, physical extension of CallioMapper linking
model components to real physical infrastructure.
**Narrative:** CallioMapper (citable via Paper 1) is the methodological infrastructure. The
scientific contribution is the resilience analysis methodology and the physical linking approach.
**Timing:** Submit concurrently with or shortly after Paper 1 preprint. Can cite the preprint
if JOSS review is ongoing.

### Why this order
- Paper 1 gives CallioMapper a standalone DOI and identity before it appears as a methods section
- Paper 2 reviewers at Energy & AI don't have to read three pages about RDF; Paper 1 handles that
- Other Calliope users can adopt the tool independently of the Singapore work

---

## Community engagement plan

### Openmod forum — before Calliope developer contact
Post a brief note on the openmod forum once national_scale is working end-to-end. Lower stakes,
early feedback, and the Calliope developers are active there. Any positive response becomes
social proof when reaching out to the core team directly.

### Calliope core developers — between engineering steps 3 and 4
**Trigger:** Base layer + provenance module working on national_scale AND physical extension
prototyped enough on Singapore to confirm architecture stability. NOT before.
**Format:** Short email or GitHub discussion with a link to a running notebook demo. Not a
design document, not a pitch deck — a working demo.
**Specific asks:**
1. Would you list this in the Calliope docs under "related tools"? (small ask, high value)
2. Any planned v0.8 changes that would break our assumptions about the data model?
3. Interest in co-authorship or advisory role on Paper 1? (changes incentives significantly)
**What not to do:** Ask for permission. Ask for validation of design decisions already made.
Engage before the demo exists.

### OEP/OEO team — after Paper 1 preprint
The OEKG alignment claim needs validation from the OEP side. Engage after the tool is public,
not before. The ask: is the RDF output format compatible with OEKG ingest, and if not, what
would need to change?

---

## Engineering sequence (with engagement triggers)

1. Base layer + provenance module working on national_scale, tests passing, docs written
2. Run base layer on Singapore — validate it doesn't break, no architecture changes needed
3. Prototype physical extension on Singapore — enough to confirm base layer supports it cleanly
   → **Engage Calliope developers here**
   → **Post openmod note here**
4. Submit JOSS preprint
5. Develop Singapore paper concurrently
6. Submit Energy & AI paper (cites JOSS preprint)
   → **Engage OEP/OEO team here**

---

## Open strategic questions

- **OEKG alignment:** Is the base layer output actually compatible with OEKG ingest conventions,
  or does full compatibility require the OEO annotation extension? Currently assumed partial
  compatibility. Needs validation with OEP team before it appears prominently in Paper 1.

- **Calliope v0.8:** No information on planned data model changes. Must ask developers before
  JOSS submission to avoid publishing against a soon-to-be-deprecated API.

- **SPARQL interface:** Decision needed on whether to ship a Python query API wrapping common
  SPARQL patterns as part of the launch package, or defer. Affects JOSS statement of need
  (if energy researchers never write SPARQL, the "queryable" value prop needs a face).

- **Co-authorship:** If Calliope developers want to co-author Paper 1, scope and timeline need
  renegotiation. Worth asking; not worth waiting for.

---

## Key references for framing

- Lombardi et al. (2025) — "Open Models Are Not Enough": open models are necessary but not
  sufficient; transparency about assumptions is what matters. Primary framing reference for the
  provenance module value proposition.
- Keppo et al. (2026) — model linking requires shared semantic vocabularies; supports the OEO
  alignment rationale.
- Rosendal et al. (2025) — soft-linking investment and operational models requires documented
  model scope and parameter provenance; supports the cross-run queryability value prop.
- Pfenninger et al. (2018) — "Opening the Black Box": foundational openmod reference; positions
  this work in the transparency lineage without overclaiming.
- Ferenz et al. (2025) — FAIR4RS for energy research software; supports JOSS statement of need.
