# Agent Skills — Planned Definitions

Skills to be created once M1 is functional. Add them to `.claude/commands/` as slash commands.

---

## `/validate-model`

**Trigger:** development feedback loop — run after any change to a mapper class or the ontology.

**What it does:**
1. Accepts a Calliope model directory path as argument (defaults to `tests/fixtures/national_scale/`)
2. Runs the full `Translator` pipeline on it
3. Reports:
   - Did parsing succeed? (errors surfaced cleanly)
   - Did SHACL validation pass? (if not, prints constraint violations)
   - Triple count per named graph (`structural`, `provenance`, `results`)
   - Output `.nq` file size

**Placeholder invocation:**
```
/validate-model tests/fixtures/national_scale/
```

---

## `/generate-ontology-artifacts`

**Trigger:** any time `ontology/ontocal.yaml` is edited.

**What it does:**
1. Runs `make generate` to regenerate `calliomapper/generated/ontocal.py` and `ontology/ontocal_shapes.ttl`
2. Verifies the generated Pydantic module imports cleanly (`python -c "from calliomapper.generated import *"`)
3. Verifies `pyshacl` loads the new SHACL shapes without errors
4. Reports success or surfaces the first failure with context

**Placeholder invocation:**
```
/generate-ontology-artifacts
```

---

## Implementation Notes (for when these are built)

- Skills live in `.claude/commands/<skill-name>.md`
- The skill file contains the prompt that gets expanded when the slash command is invoked
- Both skills should be safe to run repeatedly (idempotent)
- `/validate-model` will need M1 complete before it does anything useful
