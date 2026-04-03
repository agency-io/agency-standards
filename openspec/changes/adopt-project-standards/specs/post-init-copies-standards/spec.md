# Capability: Post-Init Copies Standards

## ADDED Requirements

### Requirement: `post-init` SHALL copy selected standard YAMLs into `standards/`

After the user confirms their selection, `post-init` MUST copy each selected builtin's YAML
file from the package into `standards/<id>.yaml` at the project root. The `standards/`
directory MUST be created if it does not exist.

#### Scenario: First post-init — standards/ does not exist

Given no `standards/` directory exists
And the user selects 5 standards from the checkbox prompt
When `post-init` completes
Then `standards/` is created
And it contains exactly 5 YAML files, one per selected standard
And CLAUDE.md is written from the copied files

#### Scenario: Subsequent post-init — some standards already adopted

Given `standards/no-bare-except.yaml` already exists (possibly with local edits)
And the user runs `post-init` again and selects `no-bare-except` plus two new standards
When `post-init` completes
Then `no-bare-except.yaml` is left untouched
And a notice is printed: "no-bare-except already adopted — skipping copy"
And the two new standard YAMLs are copied in

#### Scenario: User deselects a previously adopted standard

Given `standards/no-bare-except.yaml` exists
And the user unchecks `no-bare-except` in the prompt
When `post-init` completes
Then `standards/no-bare-except.yaml` is NOT deleted (the file remains)
And `no-bare-except` is NOT included in the updated CLAUDE.md
And a notice is printed: "no-bare-except deselected — file kept in standards/ for reference"

### Requirement: `.agency-standards.yaml` SHALL remain as a lightweight selection index

`.agency-standards.yaml` MUST continue to be written after `post-init` with the list of
selected standard IDs. It acts as a fast index so tools can know which standards are active
without scanning `standards/`. The source of truth for standard definitions is `standards/`;
the source of truth for which are active is `.agency-standards.yaml`.

#### Scenario: .agency-standards.yaml reflects current selection

Given the user selects 4 standards in post-init
When post-init completes
Then `.agency-standards.yaml` lists exactly those 4 IDs under `standards.enabled`
And `standards/` contains those 4 YAML files
