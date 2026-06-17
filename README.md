# vrs-matcher-example-plugin 🌀

An example of a custom matching algorithm for [`vrs-matcher`](https://github.com/EllrottLab/vrs-matcher), packaged so it is auto-discovered via the `vrs_matcher.plugins` entry-point group. Built against the plugin support added in [PR #16](https://github.com/EllrottLab/vrs-matcher/pull/16).

> [!TIP]
>
> This repo follows the steps in [`plugins.md`](https://github.com/EllrottLab/vrs-matcher/blob/6cf6bd1c0b27f1cc1a3bf040dfce086a8804bc56/docs/plugins.md#recommended-development-workflow).

## Quick Start ⚡

Install dependencies (pulls in `vrs-matcher` from git, see [`pyproject.toml`](pyproject.toml)) and confirm the plugin is discovered:

```sh
uv sync
uv run vrs-matcher plugins list
```

You should see `example` listed alongside the built-in `identity` plugin:

```
example
identity
```

Use it by passing its name to `--algorithm`:

```sh
uv run vrs-matcher match-samples SAMPLE_A SAMPLE_B --db variants.db --algorithm example
```

## Developing ⚙️

The plugin lives in [`src/vrs_matcher_example_plugin/example_plugin.py`](src/vrs_matcher_example_plugin/example_plugin.py). Following the recommended workflow, start from this example and adjust **only the scoring logic** first.

Every plugin implements:

- `name` — unique identifier (here, `"example"`)
- `api_version` — currently `PLUGIN_API_VERSION` (`"1"`)
- `match_pair(context, sample_a, sample_b, *, candidate_vrs_ids=None) -> MatchResult`
- `match_against_all(context, sample_id, *, top_n=None, candidate_vrs_ids=None) -> list[MatchResult]`
- `create_plugin()` — module-level factory returning the plugin object

The read-only `context` passed to each method provides `sample_exists()`, `get_vrs_ids()`, `get_genotype_states()`, and `list_samples()`.

### Registration

The plugin is exposed as an entry point in [`pyproject.toml`](pyproject.toml):

```toml
[project.entry-points."vrs_matcher.plugins"]
example = "vrs_matcher_example_plugin.example_plugin:create_plugin"
```

After `uv sync`, `vrs-matcher` discovers it automatically — no `--plugin-file` needed.

### Running as a script plugin

You can also load the plugin directly from its `.py` file without installing it, via `--plugin-file`:

```sh
uv run vrs-matcher match-samples SAMPLE_A SAMPLE_B \
  --db variants.db \
  --plugin-file src/vrs_matcher_example_plugin/example_plugin.py
```

This is handy for iterating on scoring logic before committing to a packaged release.

### Testing

Validate against a small cohort with known expected rankings, and compare against the built-in `identity` plugin:

```sh
# Match one sample against all others, ranked
uv run vrs-matcher match-sample SAMPLE_A --db variants.db --algorithm example

# Compare to the built-in identity plugin
uv run vrs-matcher match-sample SAMPLE_A --db variants.db --algorithm identity
```

Before sharing a real plugin, check that:

- Known duplicate / resequenced pairs rank near the top
- Unrelated samples rank lower
- Output is deterministic across runs
- Panel-restricted runs behave as expected when `candidate_vrs_ids` is supplied
- `MatchResult` fields are populated sensibly

### Project Layout

```
vrs-matcher-example-plugin/
├── pyproject.toml          # package metadata + vrs_matcher.plugins entry point + git dep
├── README.md
└── src/
    └── vrs_matcher_example_plugin/
        ├── __init__.py         # re-exports ExamplePlugin / create_plugin
        └── example_plugin.py   # the plugin: ExamplePlugin + create_plugin()
```
