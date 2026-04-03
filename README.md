# agency-standards

OpenSpec lifecycle companion for architecture governance. Injects coding standards into your
OpenSpec workflow — writing `CLAUDE.md`, installing Claude Code skills, and augmenting proposal
task lists so implementing agents cannot accidentally remove or bypass architecture tests.

## Installation

```bash
uv tool install agency-standards
```

## How it works

`agency-standards` complements the [OpenSpec](https://github.com/agency-io/openspec) workflow.
Run it before and after each OpenSpec command:

```
agency-standards pre-init
openspec init
agency-standards post-init

agency-standards pre-propose <change-id>
openspec propose
agency-standards post-propose <change-id>

agency-standards pre-apply <change-id>
# (agent implements the change)
agency-standards post-apply <change-id>

agency-standards pre-archive <change-id>
openspec archive
agency-standards post-archive <change-id>
```

## Quick Start

```bash
# Browse all available standards
agency-standards list
agency-standards list --filter bdd      # filter by tag
agency-standards list --verbose         # show full documentation

# After openspec init — interactively select standards, write CLAUDE.md, install skills
agency-standards post-init              # interactive checkbox selection
agency-standards post-init --yes        # accept all applicable standards (CI-friendly)

# Then open the project in Claude Code and run the generate skill:
# /agency-standards:generate

# After creating a proposal — inject standard tasks into tasks.md
agency-standards post-propose my-change-id
```

## Commands

| Command | Description |
|---|---|
| `list [--filter TAG] [--verbose]` | List all standards with their phases and docs. |
| `pre-init [--yes] [TARGET]` | Run pre-init hooks before `openspec init`. |
| `post-init [--yes] [TARGET]` | Interactively select standards, copy YAMLs into `standards/`, write `CLAUDE.md`, install skills. `--yes` skips the prompt. |
| `pre-propose <CHANGE-ID> [TARGET]` | Inject pre-propose standard tasks into `tasks.md` via Claude. |
| `post-propose <CHANGE-ID> [TARGET]` | Inject post-propose standard tasks into `tasks.md` via Claude. |
| `pre-apply <CHANGE-ID> [TARGET]` | Inject pre-apply standard tasks into `tasks.md` via Claude. |
| `post-apply <CHANGE-ID> [TARGET]` | Inject post-apply standard tasks into `tasks.md` via Claude. |
| `pre-archive <CHANGE-ID> [TARGET]` | Inject pre-archive standard tasks into `tasks.md` via Claude. |
| `post-archive <CHANGE-ID> [TARGET]` | Inject post-archive standard tasks into `tasks.md` via Claude. |

### `standards/` — project-owned standards

When you run `post-init`, selected standard YAMLs are copied into a `standards/` directory at
the project root. The project owns its standards from that point — edit them freely, or add
new `.yaml` files for project-specific standards. They are loaded automatically.

### `.agency-standards.yaml`

`post-init` persists the selected standard IDs to `.agency-standards.yaml`:

```yaml
standards:
  enabled:
    - aaa-comments
    - file-naming
    - one-step-per-file
```

Commit both `standards/` and `.agency-standards.yaml`. On subsequent `post-init` runs,
previously-adopted standards are pre-checked and new ones are unchecked (opt-in).

## What `post-propose` does

After you create a proposal with `openspec propose`, run `agency-standards post-propose <change-id>`.
It reads your `proposal.md` and `tasks.md`, identifies which standards apply to this project,
and calls Claude to rewrite `tasks.md` with injected tasks such as:

- Run `pytest tests/architecture/test_aaa_comments.py -v` — must pass before implementation is complete
- Do not remove, skip, or modify the AAA comments architecture test without explicit user approval

This ensures the implementing agent sees these constraints as part of its own task list and cannot
skip or remove them without explicit user instruction.

## Standards

Each standard declares which lifecycle phases it participates in (visible via `agency-standards list`),
a condition controlling whether it applies to a given project, and phase-specific behaviour.

### Builtin Standards

#### General

| ID | Description |
|---|---|
| `aaa-comments` | Every test must have explicit Arrange/Act/Assert comment sections |
| `adr` | ADRs must be recorded for significant decisions; checks format and lifecycle |
| `assertion-messages` | Every assertion must include a human-readable failure message |
| `file-length` | Source files must not exceed 500 lines |
| `file-naming` | Test files must follow naming patterns describing what is tested and under what condition |
| `no-bare-except` | Error handlers must always specify the exception type |
| `no-magic-strings` | Assertion comparisons must use named variables, not inline literals |
| `no-skipped-tests` | Tests must never use skip/xfail/disabled markers |
| `one-class-per-file` | Each source file should define at most one public class |
| `one-test-class-per-file` | Each test file should contain at most one test class |

#### BDD / E2E

| ID | Description |
|---|---|
| `client-class-naming` | `client.py` must define exactly one `PascalCaseTestClient` class named after the service |
| `e2e-bdd-pattern` | E2E runner files must use the BDD `scenarios()` wiring pattern |
| `e2e-no-direct-http` | E2E steps must not use raw HTTP clients directly |
| `e2e-no-skipped-scenarios` | Feature files must not contain `@skip` or `@wip` tags |
| `e2e-resource-naming` | E2E test resources must use a consistent prefix (e.g. `e2e-<operation>`) |
| `init-imports-all-steps` | `given/`, `when/`, `then/` directories must each have an `__init__.py` importing all step files |
| `no-session-helpers-in-constants` | Functions taking `session`/`client` as first param belong in `client.py`, not `constants.py` |
| `no-steps-in-conftest` | `conftest.py` must not define step functions |
| `one-step-per-file` | Each file in `given/`, `when/`, `then/` must define exactly one step function |
| `step-decorator-matches-directory` | `@given` decorators must live in `given/`, `@when` in `when/`, `@then` in `then/` |
| `step-file-name-matches-function` | Step file names must match the step function they define |

### Custom Standards

Add a `.yaml` file to `standards/` in your project. It is loaded automatically alongside
adopted builtins — no configuration needed.

```yaml
id: my-standard
name: My Standard
description: One-line description
tags: [general]

condition:
  languages: [python]           # optional — omit to apply to all projects
  # project_type: [api, cli]   # optional
  # dependencies: [pydantic]   # optional — checks pyproject.toml
  # features: [bdd]            # optional — detected features

post_init:
  output_file: test_my_standard
  prompt: |
    Generate a pytest architecture test that enforces the following rule:
    ...
  claude_md_section: |
    ## My Standard
    Explanation for developers and AI assistants...

post_propose:
  insert: before:Implementation   # prepend | append | before:<Section> | after:<Section>
  tasks:
    - "Run `pytest tests/architecture/test_my_standard.py -v` — must pass before implementation is complete"
    - "Do not remove or disable the my-standard architecture test without explicit user approval"
```

**Condition keys** (all optional, AND-ed together):
- `languages` — project must use at least one of these languages
- `project_type` — `api`, `cli`, or `library`
- `dependencies` — all listed packages must be present in the project's dependencies
- `features` — detected features, e.g. `bdd`, `openspec`

**Phase blocks** (declare any combination):
- `pre_init` / `post_init` — writes `claude_md_section` to `CLAUDE.md`, installs skills
- `pre_propose` / `post_propose` — injects tasks into `tasks.md` via Claude
- `pre_apply` / `post_apply` — injects tasks into `tasks.md` via Claude
- `pre_archive` / `post_archive` — injects tasks into `tasks.md` via Claude

**Insert positions** for task-injection phases:
- `prepend` — before all existing tasks
- `append` — after all existing tasks
- `before:<Section Name>` — before the named section heading
- `after:<Section Name>` — after the last item in the named section

## Requirements

- Python 3.11+
- An Anthropic API key (`ANTHROPIC_API_KEY` environment variable) — used by task-injection commands
- [OpenSpec](https://github.com/agency-io/openspec) — the workflow this tool complements

## License

MIT
