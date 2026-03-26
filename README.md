# agency-standards

AI-powered architecture governance for Python projects. Automatically generates and maintains architecture tests that enforce coding standards and structural conventions.

## Overview

`agency-standards` inspects your project, applies a set of standards, and uses Claude AI to generate pytest-based architecture tests tailored to your codebase. It also maintains a `CLAUDE.md` file so AI assistants understand your project's conventions.

## Installation

```bash
pip install agency-standards
```

## Quick Start

```bash
# Inspect your project and generate initial architecture tests
agency-standards init

# List available standards
agency-standards standards list

# Add a specific standard
agency-standards add no-bare-except

# Add a custom standard described in plain English
agency-standards add --describe "Every public function must have a docstring"

# Regenerate tests after standards change (preserves custom sections)
agency-standards update

# Check which generated files are out of date
agency-standards status
```

## Commands

| Command | Description |
|---|---|
| `init [TARGET]` | Wizard to inspect a project and generate initial architecture tests + `CLAUDE.md` |
| `update [TARGET]` | Regenerate managed test files, preserving custom sections |
| `status [TARGET]` | Show which generated files are current vs out of date |
| `add [STANDARD_ID]` | Add a standard to the project |
| `standards list` | List all available standards |

### `init` options

| Flag | Description |
|---|---|
| `--yes, -y` | Accept all defaults, skip prompts |

### `update` options

| Flag | Description |
|---|---|
| `--standard, -s` | Update a single standard by ID |

### `add` options

| Flag | Description |
|---|---|
| `--target, -t` | Project directory (default: current) |
| `--describe, -d` | Describe a custom standard in plain English |

## Builtin Standards

### General

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

### BDD / E2E

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

## Generated Files

Architecture tests are written to `tests/architecture/`. Each file includes a custom section marker:

```python
# --- CUSTOM (preserved on update) ---
```

Any code you add after this marker is preserved when you run `agency-standards update`.

## Custom Standards

You can define your own standards in `~/.agency-standards/standards/` using the same YAML format as the builtins:

```yaml
id: my-standard
name: My Standard
description: One-line description
languages: [python]
tags: [general]
output_file: test_my_standard
prompt: |
  Detailed instructions for Claude to generate the test...
claude_md_section: |
  ## My Standard
  Explanation for developers and AI assistants...
```

## Requirements

- Python 3.10+
- An Anthropic API key (`ANTHROPIC_API_KEY` environment variable)

## License

MIT
