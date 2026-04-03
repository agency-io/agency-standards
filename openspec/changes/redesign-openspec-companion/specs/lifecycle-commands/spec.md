## ADDED Requirements

### Requirement: post-init command sets up project governance artifacts
`agency-standards post-init [target]` SHALL inspect the target project, evaluate conditions
for all known standards, write `CLAUDE.md` from each applicable standard's
`post_init.claude_md_section`, install Claude Code skills, and print instructions to run
`/agency-standards:generate` in Claude Code. It SHALL NOT call the Claude API.

#### Scenario: post-init on a Python project
- **WHEN** the user runs `agency-standards post-init` in a Python project directory
- **THEN** the project is inspected to detect language, type, and features
- **AND** all standards whose conditions match are selected
- **AND** `CLAUDE.md` is written at the project root containing each selected standard's section
- **AND** Claude Code skills are installed under `.claude/commands/agency-standards/`
- **AND** the CLI prints instructions to run `/agency-standards:generate` in Claude Code
- **AND** no Claude API call is made

#### Scenario: post-init skips standards whose condition is not met
- **WHEN** the project does not use BDD and a standard declares `condition: {features: [bdd]}`
- **THEN** that standard's `claude_md_section` is not written to `CLAUDE.md`
- **AND** no error is raised

### Requirement: post-propose command injects tasks into a change's tasks.md via Claude
`agency-standards post-propose <change-id> [target]` SHALL load the specified change's
`proposal.md` and `tasks.md`, evaluate conditions for all standards with a `post_propose`
block, call the Claude API with the proposal content and the applicable standards' task
definitions, and write the returned updated `tasks.md` back to
`openspec/changes/<change-id>/tasks.md`. It SHALL be the default command.

#### Scenario: post-propose injects tasks for applicable standards
- **WHEN** the user runs `agency-standards post-propose add-payment-flow`
- **THEN** the CLI reads `openspec/changes/add-payment-flow/proposal.md` and `tasks.md`
- **AND** evaluates which standards have a `post_propose` block and a matching condition
- **AND** calls Claude API with the proposal content, current tasks.md, and each standard's task definitions
- **AND** writes the updated `tasks.md` returned by Claude back to disk
- **AND** prints a summary of which standards contributed tasks

#### Scenario: post-propose is the default command
- **WHEN** the user runs `agency-standards add-payment-flow` (no subcommand)
- **THEN** it behaves identically to `agency-standards post-propose add-payment-flow`

#### Scenario: change-id not found
- **WHEN** the user runs `agency-standards post-propose nonexistent-change`
- **THEN** the CLI prints an error indicating the change directory was not found
- **AND** exits with a non-zero code

### Requirement: post-apply and post-archive commands are stub placeholders
The CLI SHALL provide `post-apply <change-id>` and `post-archive <change-id>` as valid
subcommands. Their full behaviour is defined in a follow-on proposal. For now both SHALL
print a "not yet implemented" message and exit with code 0.

#### Scenario: post-apply called
- **WHEN** the user runs `agency-standards post-apply some-change`
- **THEN** the CLI prints a message indicating the command is not yet implemented
- **AND** exits with code 0

#### Scenario: post-archive called
- **WHEN** the user runs `agency-standards post-archive some-change`
- **THEN** the CLI prints a message indicating the command is not yet implemented
- **AND** exits with code 0

### Requirement: Old CLI commands are removed
The commands `init`, `add`, `update`, `status`, and `standards list` SHALL be removed.
Invoking them SHALL result in a "command not found" error from the CLI framework.

#### Scenario: Old command invoked
- **WHEN** the user runs `agency-standards init`
- **THEN** the CLI prints an unknown command error
- **AND** exits with a non-zero code
