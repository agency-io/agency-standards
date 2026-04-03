# Change: Project-owned standards directory

## Why

Currently, enabled standards live only as IDs in `.agency-standards.yaml` — the YAML
definitions remain inside the installed package. This means:

- Teams cannot modify a standard without forking the package
- There is no natural place for project-specific standards
- "Custom standards" requires a separate concept and configuration

The fix is to make the project own its standards. When a standard is enabled, its YAML is
copied into a `standards/` directory at the project root. That directory is committed to
version control. The loader reads from `standards/` first and treats builtins only as a
catalog to pick from during `post-init`.

## What Changes

### `standards/` directory becomes the source of truth

After `post-init`, the project has a `standards/` directory containing one YAML file per
enabled standard. These files are committed to the repo. When any agency-standards command
runs, it loads standards from `standards/` — not from the installed package.

Builtins are used only as:
1. The browsable catalog in `agency-standards list`
2. The source files copied during `post-init` selection

### `post-init` copies selected YAMLs into `standards/`

When the user confirms their selection, each selected standard's YAML is copied from the
builtin catalog into `standards/<id>.yaml`. If a file already exists (e.g. the team has
customised it), it is left untouched — the user is notified.

### Custom standards are just new YAML files

To add a project-specific standard, a developer creates `standards/my-standard.yaml`
following the same schema. It is automatically loaded alongside the adopted builtins.

### `agency-standards list` shows both sources

`list` shows all builtin standards (with an `[adopted]` marker for those already in
`standards/`) plus any custom standards found in `standards/` that have no builtin
counterpart.

### Loader simplified

`load_project()` replaces `load_user()` — reads from `./standards/`. `load_all()` returns
project standards when present; builtins-only when `standards/` does not exist (first run).

## Impact

- `src/agency_standards/standards/loader.py` — replace `load_user` with `load_project`
- `src/agency_standards/commands/post_init_cmd.py` — copy YAMLs on selection
- `src/agency_standards/commands/list_cmd.py` — show adopted marker, surface custom standards
- `standards/` directory created in consuming projects (committed to VCS)
- `.agency-standards.yaml` `enabled` list may be removed or kept as a lightweight index
