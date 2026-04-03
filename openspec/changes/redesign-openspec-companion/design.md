## Context

`agency-standards` started as a standalone CLI that called the Claude API to generate
architecture tests. It was refactored toward a skill-based approach but left incomplete.
This redesign completes the shift and gives the tool a clear identity: it is a companion
to the OpenSpec workflow, not a parallel workflow.

## Goals / Non-Goals

- Goals:
  - Each CLI command maps 1:1 to an OpenSpec lifecycle moment
  - Standards declare their own phase participation and applicability conditions
  - `post-propose` uses Claude to produce coherent, contextual task injection
  - `post-init` uses Claude Code (skills), not direct API calls
  - All 21 existing standards continue to work (behaviour preserved under new schema)

- Non-Goals:
  - Automatic hook execution (user runs commands manually for now)
  - Full `post-apply` and `post-archive` behaviour (stubbed; follow-on proposal)
  - Multi-language test generation beyond current support

## Standard Schema Design

Standards gain a `condition` block and phase-named behaviour blocks. The `condition` is
evaluated by the CLI against the inspected project; if it fails, the standard is skipped
entirely for all phases.

```yaml
id: aaa-comments
name: AAA Comments
description: Enforce Arrange/Act/Assert structure in tests

condition:
  languages: [python]        # at least one language must match
  # project_type: [api, cli] # optional
  # dependencies: [pytest]   # optional: present in pyproject.toml / requirements
  # features: [bdd]          # optional: detected by inspector (e.g. .feature files)
  # (omit condition block = always applies)

post_init:
  output_file: test_aaa_comments
  prompt: |
    Generate a pytest architecture test...
  claude_md_section: |
    ## AAA Comments
    All test functions must follow Arrange / Act / Assert structure...

post_propose:
  insert: before:Implementation   # prepend | append | before:<Section> | after:<Section>
  tasks:
    - "Run `pytest tests/architecture/test_aaa_comments.py -v` — must pass before implementation is complete"
    - "Do not remove, skip, or modify the AAA comments architecture test without explicit user approval"
```

### Condition evaluation rules

All specified keys are AND-ed (every key must match):
- `languages`: intersection with detected project languages must be non-empty
- `project_type`: project type must be in the list
- `dependencies`: all listed packages must appear in the project's dependency metadata
- `features`: all listed features must be detected by the inspector
- Omitting `condition` entirely is equivalent to `always: true`

### Task insertion positions

The `insert` field on `post_propose` controls where tasks are added in `tasks.md`:
- `prepend` — before all existing content
- `append` — after all existing content
- `before:<Section Name>` — immediately before the `## N. <Section Name>` heading
- `after:<Section Name>` — after the last task item under the matching section

Position matching is case-insensitive and ignores the numeric prefix (e.g. `before:Implementation`
matches `## 1. Implementation` or `## 3. Implementation`).

## `post-propose` Claude API design

The CLI sends a single prompt to Claude containing:
1. The full `proposal.md` text (context for what is being built)
2. The full current `tasks.md` text
3. The list of applicable standards, each with their `post_propose.insert` position and
   `post_propose.tasks` lines
4. An instruction to rewrite `tasks.md` inserting each standard's tasks at the correct
   position, without altering existing task wording, numbering logic, or structure

Claude returns the complete rewritten `tasks.md`. The CLI writes it back. No partial patching.

Rationale for using Claude here rather than mechanical insertion:
- Task lists have varied structure; Claude handles edge cases (duplicate detection,
  renumbering, missing target sections) more robustly than regex
- Task wording can be lightly adapted to fit the proposal context

## `post-init` skill design (no API call)

The CLI:
1. Inspects the project (via existing `inspector.py`)
2. Evaluates conditions for all standards
3. Writes `CLAUDE.md` from the `claude_md_section` of each applicable standard
4. Installs Claude Code skills (the `generate` and `update` skill files)
5. Prints: "Run `/agency-standards:generate` in Claude Code to generate architecture tests"

The `generate` skill is what actually produces test files using Claude Code. The CLI does
not call Claude API.

## Migration Plan

1. New schema fields are additive; existing YAML files are updated in-place
2. The old flat fields (`prompt`, `output_file`, `claude_md_section`) move under `post_init`
3. Old CLI entry points are removed from `cli.py` and `commands/`
4. `config.py` and `.agency-standards.yaml` are replaced by reading the standard definitions
   directly (no separate config file needed — the user runs `post-init` to set up, and the
   skills read from the standard definitions themselves)

## Open Questions

- Should `post-apply` verify architecture tests pass (deterministic) or also call Claude?
- Should `post-archive` do anything beyond a final test run, or be a no-op initially?
