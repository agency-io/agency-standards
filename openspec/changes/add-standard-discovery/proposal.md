# Change: Add standard discovery — list command and interactive post-init selection

## Why

`post-init` currently applies every standard that matches a project's condition silently,
with no way for the user to see what is available, understand what each standard does, or
choose which ones to enable. This creates two problems:

1. **No discoverability** — a user cannot browse standards or read their documentation before
   committing to them.
2. **No agency** — every matching standard is applied unconditionally; there is no opt-out
   without editing YAML.

The enriched `claude_md_section` documentation that was added to every builtin standard is
currently unused at selection time — it only appears in `CLAUDE.md` after the fact.

## What Changes

### New `list` command

A new `agency-standards list` command displays every builtin (and custom) standard with:
- ID, name, tags, and condition summary on a single line per standard
- `--verbose` / `-v` flag to also show the full `claude_md_section` documentation

Supports `--filter <tag>` to narrow by tag (e.g. `--filter bdd`).

### Interactive selection in `post-init`

`post-init` becomes a two-step process:

1. **Inspect** the project (existing behaviour).
2. **Present a checklist** of applicable standards (pre-selected by default) and let the user
   toggle each on or off using `questionary.checkbox`.
3. **Apply only the selected standards** — write their `claude_md_section` blocks to `CLAUDE.md`
   and install skills.

A `--yes` / `-y` flag skips the interactive step and selects all applicable standards
(restoring the old non-interactive behaviour, useful for CI).

### Persistence

Selected standards are persisted to `.agency-standards.yaml` at the project root so that
future `post-init` runs default to the same selection. The file is human-readable YAML.

Format:

```yaml
standards:
  enabled:
    - no-bare-except
    - file-naming
    - one-step-per-file
```

On a subsequent `post-init` run, any standard in `enabled` that matches the project condition
is pre-checked; any applicable standard NOT in the list is unchecked (but still shown).

## Impact

- New command: `agency-standards list`
- `post-init` gains interactive selection + `--yes` bypass
- `.agency-standards.yaml` introduced as a persisted selection file
- `src/agency_standards/config.py` re-introduced to load/save `.agency-standards.yaml`
- Affected specs: `standard-list-command` (new), `post-init-selection` (new)
