# Capability: Standard List Command

## ADDED Requirements

### Requirement: The CLI SHALL provide a `list` subcommand that displays all available standards

The `agency-standards list` command MUST load every builtin and custom standard and display
them in the terminal. Each standard MUST appear with its ID, name, and tags on a single line.
The command MUST NOT require a project directory argument; it lists all standards regardless
of which project is active.

#### Scenario: User runs `agency-standards list` with no flags

Given a project with no `.agency-standards.yaml`
When the user runs `agency-standards list`
Then every builtin standard is displayed, one per line
And each line shows the standard ID, name, and tags
And the output is paginated or scrollable if the terminal supports it
And the command exits with code 0

#### Scenario: User runs `agency-standards list --verbose`

Given the user wants to see full documentation
When the user runs `agency-standards list --verbose` (or `-v`)
Then every standard is displayed with its ID, name, tags, and full `claude_md_section` text
And the sections are separated by a visible divider
And the command exits with code 0

#### Scenario: User filters by tag

Given the user wants only BDD-related standards
When the user runs `agency-standards list --filter bdd`
Then only standards whose `tags` list contains `bdd` are shown
And the count of matching standards is printed at the bottom
And the command exits with code 0

#### Scenario: No standards match the filter

Given the user runs `agency-standards list --filter nonexistent`
When the command executes
Then a message "No standards match filter: nonexistent" is displayed
And the command exits with code 0
