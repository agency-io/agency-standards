# Capability: Post-Init Interactive Selection

## ADDED Requirements

### Requirement: `post-init` SHALL present an interactive checklist before applying standards

After inspecting the project, `post-init` MUST display a `questionary.checkbox` prompt listing
every applicable standard (those whose `condition` matches the project). Each standard MUST be
pre-selected by default (or according to `.agency-standards.yaml` if present). The user MUST
be able to toggle any standard off before proceeding. Only selected standards SHALL be applied
(CLAUDE.md written, skills installed).

#### Scenario: First-time `post-init` with no saved selection

Given a project with no `.agency-standards.yaml`
And 8 standards are applicable to the project
When the user runs `agency-standards post-init`
Then a checkbox prompt is displayed listing all 8 standards
And all 8 are pre-checked
And the user can toggle any off before pressing Enter
And only the checked standards are written to CLAUDE.md
And only the checked standards are persisted to `.agency-standards.yaml`

#### Scenario: Subsequent `post-init` with saved selection

Given a project with `.agency-standards.yaml` listing 5 enabled standards
And 8 standards are applicable to the project
When the user runs `agency-standards post-init`
Then a checkbox prompt is displayed listing all 8 standards
And the 5 previously enabled standards are pre-checked
And the 3 new-or-unselected standards are unchecked (but visible)
And the user can change the selection before confirming

#### Scenario: User deselects all standards

Given the user unchecks every standard in the prompt
When the user confirms with an empty selection
Then CLAUDE.md is not written (or existing CLAUDE.md is left unchanged)
And `.agency-standards.yaml` is written with an empty `enabled` list
And a warning "No standards selected; CLAUDE.md not updated" is printed

### Requirement: `post-init` SHALL accept `--yes` to bypass interactive selection

When the `--yes` (or `-y`) flag is passed, `post-init` MUST skip the checkbox prompt and
apply all applicable standards as if all were selected. If `.agency-standards.yaml` exists,
it is ignored in `--yes` mode and overwritten with all applicable standards.

#### Scenario: CI pipeline runs `post-init --yes`

Given a CI pipeline calls `agency-standards post-init --yes`
When the command executes
Then all applicable standards are applied without any interactive prompt
And CLAUDE.md is written with all applicable sections
And `.agency-standards.yaml` is written with all applicable standard IDs
And the command exits with code 0

### Requirement: Selected standards SHALL be persisted to `.agency-standards.yaml`

After the user confirms selection (interactive or `--yes`), `post-init` MUST write
`.agency-standards.yaml` to the project root. The file MUST contain a `standards.enabled`
list of the IDs of all standards that were applied. The file format MUST be valid YAML.

#### Scenario: `.agency-standards.yaml` is written after selection

Given the user selects 5 out of 8 applicable standards
When `post-init` completes
Then `.agency-standards.yaml` exists at the project root
And it contains `standards.enabled` with exactly those 5 standard IDs
And the file is valid YAML

#### Scenario: `.agency-standards.yaml` is human-readable

Given the file is written
Then it uses block-style YAML (not flow-style)
And the list entries appear one per line with `- ` prefix
And the file can be read and edited by hand

### Requirement: `agency-standards list` SHALL indicate which standards are currently enabled

When `.agency-standards.yaml` exists in the current directory, `list` MUST mark each standard
as enabled (`✓`) or not enabled (no marker) based on the persisted selection.

#### Scenario: List output with saved selection

Given `.agency-standards.yaml` exists with 5 enabled standards
When the user runs `agency-standards list`
Then enabled standards are marked with a green `✓`
And standards not in the enabled list are shown without a marker
