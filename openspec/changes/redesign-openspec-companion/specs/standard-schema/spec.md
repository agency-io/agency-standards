## ADDED Requirements

### Requirement: Standard YAML declares phase participation via named blocks
Each standard YAML file SHALL declare phase-specific behaviour in named top-level blocks:
`post_init`, `post_propose`, `post_apply`, `post_archive`. A standard participates in a
phase only if the corresponding block is present. The existing flat fields (`prompt`,
`output_file`, `claude_md_section`) are moved under `post_init`. Phases not declared are
silently skipped when the corresponding lifecycle command runs.

#### Scenario: Standard with only post_init block
- **WHEN** a standard YAML contains a `post_init` block but no `post_propose` block
- **THEN** running `agency-standards post-init` processes the standard
- **AND** running `agency-standards post-propose` skips the standard silently

#### Scenario: Standard with both post_init and post_propose blocks
- **WHEN** a standard YAML contains both `post_init` and `post_propose` blocks
- **THEN** running `agency-standards post-init` processes the `post_init` block
- **AND** running `agency-standards post-propose` processes the `post_propose` block

### Requirement: Standard YAML SHALL declare an applicability condition
Each standard YAML file MAY declare a `condition` block. The CLI SHALL evaluate the condition
against the inspected project before executing any phase behaviour. If the condition is not
met, the standard SHALL be skipped for all phases. If the `condition` block is absent, the
standard SHALL always apply.

Supported condition keys (all are AND-ed; all specified keys must match):
- `languages: [...]` — intersection with detected project languages must be non-empty
- `project_type: [...]` — detected project type must be in the list
- `dependencies: [...]` — all listed packages must be present in dependency metadata
- `features: [...]` — all listed features must be detected (e.g. `bdd`)

#### Scenario: Condition languages match
- **WHEN** a standard declares `condition: {languages: [python]}` and the project contains Python files
- **THEN** the standard is included when the relevant lifecycle command runs

#### Scenario: Condition languages do not match
- **WHEN** a standard declares `condition: {languages: [python]}` and the project contains only TypeScript files
- **THEN** the standard is skipped for all phases with no error

#### Scenario: Condition dependency not present
- **WHEN** a standard declares `condition: {dependencies: [pydantic]}` and pydantic is not in the project's dependencies
- **THEN** the standard is skipped for all phases

#### Scenario: No condition block
- **WHEN** a standard YAML has no `condition` block
- **THEN** the standard applies to all projects regardless of language, type, or dependencies

### Requirement: All 21 builtin standards are migrated to the new schema
All existing builtin standard YAML files SHALL be updated so that their current flat fields
(`prompt`, `output_file`, `claude_md_section`) are nested under a `post_init` block.
Existing behaviour is preserved. Each standard SHALL also gain a `post_propose` block
defining the tasks to inject and their insertion position.

#### Scenario: Migrated standard loads correctly
- **WHEN** the standard loader reads an updated builtin YAML
- **THEN** it returns a Standard model with populated `post_init` and `post_propose` attributes
- **AND** no field from the old schema is silently dropped

#### Scenario: post_propose tasks defined for each builtin standard
- **WHEN** `agency-standards post-propose` is run on a project using a builtin standard
- **THEN** at least one task is injected into `tasks.md` from that standard's `post_propose` block
