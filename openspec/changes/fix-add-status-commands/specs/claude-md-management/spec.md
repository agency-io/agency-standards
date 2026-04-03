## ADDED Requirements

### Requirement: CLI writes CLAUDE.md after config changes
After any CLI command that modifies `.agency-standards.yaml`, the CLI SHALL write or update
`CLAUDE.md` in the target project root with a section for each active standard, using each
standard's `claude_md_section` field. This ensures CLAUDE.md is always current after `init`
or `add`, before the user has run the generate skill.

#### Scenario: init writes CLAUDE.md
- **WHEN** the user completes `agency-standards init`
- **THEN** `CLAUDE.md` is created (or updated) in the target project root
- **AND** it contains one section per selected standard, drawn from each standard's `claude_md_section`

#### Scenario: add updates CLAUDE.md
- **WHEN** the user runs `agency-standards add <id>` successfully
- **THEN** `CLAUDE.md` in the target project root is updated to include the new standard's section
- **AND** previously written sections for other standards are preserved

#### Scenario: generate skill also updates CLAUDE.md
- **WHEN** the user runs `/agency-standards:generate` in Claude Code
- **THEN** the skill ALSO creates or updates `CLAUDE.md` (as documented in `skills/generate.md` line 29)
- **AND** this is complementary — the CLI writes a minimal version immediately; the skill may enrich it

### Requirement: CLAUDE.md is written to the target project root only
`CLAUDE.md` SHALL be written at `<target>/CLAUDE.md`. No other CLAUDE.md files SHALL be created
by the CLI or generate skill for agency-standards purposes.

#### Scenario: Single CLAUDE.md per project
- **WHEN** `agency-standards init` or `add` runs on a project at path `/path/to/project`
- **THEN** exactly one CLAUDE.md is written at `/path/to/project/CLAUDE.md`
- **AND** no CLAUDE.md is written under `tests/`, `.claude/`, or any subdirectory
