# Capability: Project Standards Directory

## ADDED Requirements

### Requirement: The loader SHALL read standards from the project `standards/` directory

When a `standards/` directory exists at the project root, `load_all()` MUST load standards
from it. These project standards take precedence over builtins with the same ID (allowing
a team to override a builtin by placing a modified copy in `standards/`). Builtins not
present in `standards/` are NOT loaded as active standards — they remain available only as
a catalog for `list` and `post-init`.

#### Scenario: Project has a standards/ directory

Given `standards/no-bare-except.yaml` and `standards/file-naming.yaml` exist
When `load_all()` is called
Then exactly those two standards are returned
And the builtin versions are not duplicated

#### Scenario: Project has no standards/ directory (first run)

Given no `standards/` directory exists
When `load_all()` is called
Then all builtins are returned (backward-compatible behaviour)

#### Scenario: Custom standard alongside adopted builtins

Given `standards/no-bare-except.yaml` (adopted builtin) and `standards/require-request-id.yaml` (custom) exist
When `load_all()` is called
Then both standards are returned
And `require-request-id` is loaded even though it has no builtin counterpart

#### Scenario: Project standard overrides a builtin

Given `standards/no-bare-except.yaml` exists with a modified `claude_md_section`
When `load_all()` is called
Then the project version is used, not the builtin
And no duplicate is returned

### Requirement: `agency-standards list` SHALL distinguish adopted, available, and custom standards

`list` MUST show three categories when a `standards/` directory exists:
- **Adopted** — builtin standards that have been copied into `standards/` (marked `✓`)
- **Available** — builtins not yet in `standards/` (unmarked)
- **Custom** — files in `standards/` with no builtin counterpart (marked `[custom]`)

#### Scenario: List with mixed standards

Given `standards/` contains `no-bare-except.yaml` and `require-request-id.yaml`
And `require-request-id` has no builtin counterpart
When the user runs `agency-standards list`
Then `no-bare-except` is shown with `✓`
And `require-request-id` is shown with `[custom]`
And all other builtins are shown without a marker
