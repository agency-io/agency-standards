# Change: Redesign agency-standards as an OpenSpec lifecycle companion

## Why

The tool was conceived as a standalone CLI, but its real value is at specific moments in the
OpenSpec workflow — immediately after a project is initialised, and immediately after a proposal
is created. Positioning it as a lifecycle companion makes its purpose explicit, eliminates
commands that don't map to a clear moment in time, and enables standards to participate in
multiple phases with different behaviour at each.

Supersedes: `fix-add-status-commands` (those commands are being replaced entirely).

## What Changes

- **CLI commands replaced** — `init`, `add`, `update`, `status`, `standards list` are removed.
  New commands: `post-init`, `post-propose`, `post-apply`, `post-archive`. Default is
  `post-propose`.

- **Standard YAML schema extended** — each standard now declares which phases it participates
  in (`post_init`, `post_propose`, `post_apply`, `post_archive`), a `condition` block that
  gates whether the standard applies to a given project, and phase-specific behaviour blocks.
  The existing flat fields (`prompt`, `output_file`, `claude_md_section`) move under
  `post_init`.

- **All 21 builtin standards migrated** to the new schema (existing behaviour preserved under
  `post_init`; `post_propose` task injection added where appropriate).

- **`post-init`** — CLI writes CLAUDE.md from each applicable standard's `claude_md_section`,
  installs Claude Code skills, and prints instructions to run `/agency-standards:generate` in
  Claude Code. No Claude API call.

- **`post-propose`** — CLI calls the Claude API. Claude reads the proposal's `proposal.md` and
  `tasks.md`, the applicable standards' `post_propose` definitions (task lines and insertion
  position), and rewrites `tasks.md` with the standard tasks intelligently inserted.

- **`post-apply` and `post-archive`** — stubs defined for completeness; full behaviour to be
  detailed in a follow-on proposal.

## Impact

- Affected specs: `standard-schema`, `lifecycle-commands`, `task-injection`
- Affected code (all existing source replaced or removed):
  - `src/agency_standards/cli.py`
  - `src/agency_standards/commands/` (all files)
  - `src/agency_standards/builtin_standards/` (all 21 YAML files updated)
  - `src/agency_standards/generator.py` (dead code removed; remainder kept if still needed)
  - `src/agency_standards/config.py` (may be removed or repurposed)
