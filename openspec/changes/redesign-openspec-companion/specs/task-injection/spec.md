## ADDED Requirements

### Requirement: Each standard's post_propose block declares tasks and an insertion position
A standard's `post_propose` block SHALL contain a list of `tasks` (strings) and an `insert`
field specifying where those tasks are placed in `tasks.md`. Supported values for `insert`:
- `prepend` — before all existing content
- `append` — after all existing content
- `before:<Section Name>` — immediately before the matching `## N. <Section Name>` heading
- `after:<Section Name>` — after the last item under the matching section

Section name matching is case-insensitive and ignores any leading numeric prefix.

#### Scenario: Tasks inserted before a named section
- **WHEN** a standard declares `insert: before:Implementation`
- **AND** `tasks.md` contains `## 1. Implementation`
- **THEN** the standard's tasks appear in a new section immediately above `## 1. Implementation`

#### Scenario: Tasks appended when target section is absent
- **WHEN** a standard declares `insert: before:Implementation`
- **AND** `tasks.md` does not contain any Implementation section
- **THEN** the standard's tasks are appended at the end (fallback behaviour)
- **AND** no error is raised

### Requirement: Claude rewrites tasks.md coherently from standard task definitions
The CLI SHALL send to Claude: the full `proposal.md`, the full current `tasks.md`, and the
list of applicable standards with their `post_propose.insert` and `post_propose.tasks`.
Claude SHALL return a complete, valid `tasks.md` with all standard tasks inserted at the
correct positions, existing task wording unchanged, and no duplicate tasks introduced.
The CLI SHALL write Claude's response directly to disk, replacing the previous `tasks.md`.

#### Scenario: Tasks injected without altering existing items
- **WHEN** `tasks.md` already contains `- [ ] 1.1 Create database schema`
- **THEN** the rewritten `tasks.md` contains that same item verbatim
- **AND** standard-injected tasks appear in their own section or at their insertion position

#### Scenario: Duplicate task not introduced
- **WHEN** a standard's task says "Run pytest tests/architecture/ -v"
- **AND** that exact instruction already exists in `tasks.md`
- **THEN** Claude does not add a duplicate entry

#### Scenario: Tasks not present for standards whose condition is not met
- **WHEN** a standard's condition requires `dependencies: [pydantic]`
- **AND** the project does not declare pydantic as a dependency
- **THEN** that standard's tasks are not included in the Claude prompt
- **AND** they do not appear in the rewritten `tasks.md`

### Requirement: Injected tasks protect architecture tests from removal
Every standard that generates an architecture test at `post-init` SHALL include in its
`post_propose.tasks` at minimum:
1. A task to run the specific architecture test and verify it passes
2. A task instructing the implementing agent not to remove, skip, or disable that test without
   explicit user approval

#### Scenario: Protection tasks present after post-propose
- **WHEN** `agency-standards post-propose` runs on a change in a project that has the
  `aaa-comments` standard active
- **THEN** `tasks.md` contains a task to run `pytest tests/architecture/test_aaa_comments.py`
- **AND** `tasks.md` contains a task prohibiting removal of that test file
