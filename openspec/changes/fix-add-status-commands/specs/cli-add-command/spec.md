## ADDED Requirements

### Requirement: Add command updates config and installs skills without generating tests
The `add` command SHALL update `.agency-standards.yaml` with the new standard ID and reinstall
Claude Code skills, then print instructions directing the user to run the generation skill.
It SHALL NOT generate test files directly.

#### Scenario: Add a known standard by ID
- **WHEN** the user runs `agency-standards add aaa-comments`
- **THEN** `aaa-comments` is appended to `.agency-standards.yaml` (no duplicates)
- **AND** `CLAUDE.md` in the target project root is updated with the standard's section
- **AND** Claude Code skills are reinstalled in the project
- **AND** the CLI prints a message telling the user to run `/agency-standards:generate`
- **AND** the process exits with code 0

#### Scenario: Add a custom standard via --describe
- **WHEN** the user runs `agency-standards add --describe "all public functions must have docstrings"`
- **THEN** a custom standard is built from the description and saved to `~/.agency-standards/standards/`
- **AND** its ID is appended to `.agency-standards.yaml`
- **AND** `CLAUDE.md` in the target project root is updated with the new standard's section
- **AND** Claude Code skills are reinstalled
- **AND** the CLI prints a message telling the user to run `/agency-standards:generate`

#### Scenario: Unknown standard ID
- **WHEN** the user runs `agency-standards add nonexistent-id`
- **THEN** the CLI prints an error indicating the standard was not found
- **AND** the process exits with a non-zero code

#### Scenario: Neither ID nor --describe provided
- **WHEN** the user runs `agency-standards add` with no arguments
- **THEN** the CLI prints an error asking for a standard ID or `--describe`
- **AND** the process exits with a non-zero code
