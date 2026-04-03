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
Run it after each OpenSpec command:

```
openspec init      →  agency-standards post-init
openspec propose   →  agency-standards post-propose <change-id>
openspec apply     →  (agent follows the augmented tasks.md)
openspec archive   →  agency-standards post-archive <change-id>
```

## Quick Start

```bash
# After openspec init — write CLAUDE.md and install Claude Code skills
agency-standards post-init

# Then open the project in Claude Code and run the generate skill:
# /agency-standards:generate

# After creating a proposal — inject standard tasks into tasks.md
agency-standards post-propose my-change-id

# Shorthand for post-propose (default command)
agency-standards my-change-id
```

## Commands

| Command | Description |
|---|---|
| `post-init [TARGET]` | Write `CLAUDE.md`, install Claude Code skills. Run after `openspec init`. |
| `post-propose <CHANGE-ID> [TARGET]` | Inject standard tasks into the change's `tasks.md` via Claude. Run after `openspec propose`. |
| `post-apply <CHANGE-ID> [TARGET]` | *(Not yet implemented)* Run after `openspec apply`. |
| `post-archive <CHANGE-ID> [TARGET]` | *(Not yet implemented)* Run after `openspec archive`. |

`post-propose` is the default — `agency-standards <change-id>` is equivalent to
`agency-standards post-propose <change-id>`.

## What `post-propose` does

After you create a proposal with `openspec propose`, run `agency-standards post-propose <change-id>`.
It reads your `proposal.md` and `tasks.md`, identifies which standards apply to this project,
and calls Claude to rewrite `tasks.md` with injected tasks such as:

- Run `pytest tests/architecture/test_aaa_comments.py -v` — must pass before implementation is complete
- Do not remove, skip, or modify the AAA comments architecture test without explicit user approval

This ensures the implementing agent sees these constraints as part of its own task list and cannot
skip or remove them without explicit user instruction.

## Standards

Each standard declares which lifecycle phases it participates in, a condition that controls
whether it applies to a given project, and phase-specific behaviour.

### Builtin Standards

#### General

| ID | Description |
|---|---|
| `aaa-comments` | Every test must have explicit Arrange/Act/Assert comment sections |
| `assertion-messages` | Every assertion must include a human-readable failure message |
| `no-magic-strings` | Assertion comparisons must use named variables, not inline literals |
| `no-bare-except` | Error handlers must always specify the exception type |
| `file-length` | Source files must not exceed 500 lines |
| `file-naming` | Test files must follow naming patterns describing what is tested and under what condition |
| `one-class-per-file` | Each source file should define at most one public class |
| `one-test-class-per-file` | Each test file should contain at most one test class |
| `no-skipped-tests` | Tests must never use skip/xfail/disabled markers |

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

Define your own standards in `~/.agency-standards/standards/` using the new YAML schema:

```yaml
id: my-standard
name: My Standard
description: One-line description

condition:
  languages: [python]           # optional — omit to apply to all projects
  # project_type: [api, cli]   # optional
  # dependencies: [pydantic]   # optional — checks pyproject.toml

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
- `features` — detected features, e.g. `bdd`

**Insert positions** for `post_propose`:
- `prepend` — before all existing tasks
- `append` — after all existing tasks
- `before:<Section Name>` — before the named section heading
- `after:<Section Name>` — after the last item in the named section

## Requirements

- Python 3.11+
- An Anthropic API key (`ANTHROPIC_API_KEY` environment variable) — used by `post-propose`
- [OpenSpec](https://github.com/agency-io/openspec) — the workflow this tool complements

## License

MIT
