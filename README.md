# Overview 🌀

An example of a custom matching algorithm for [`vrs-matcher`](https://github.com/EllrottLab/vrs-matcher)!

This plugin **restricts matching to a fixed panel of VRS IDs** (e.g. a disease
gene panel) before scoring with plain Jaccard. It shows how a plugin can carry
its own data and combine it with the caller's `candidate_vrs_ids`. The panel in
[`example_plugin.py`](src/vrs_matcher_example_plugin/example_plugin.py) uses
real VRS IDs from the main repo's `examples/example-cohort.vcf.gz` — **replace
`EXAMPLE_PANEL` with VRS IDs from your own panel.**

> [!WARNING]
>
> Panel-restricted similarity is **not** genome-wide identity. The restriction
> deliberately changes the ranking versus the built-in `identity` matcher —
> make sure QC users know matching is limited to the panel.


> [!TIP]
>
> Built against [vrs-matcher/PR #14](https://github.com/EllrottLab/vrs-matcher/pull/14) + following the steps in [`plugins.md`](https://github.com/EllrottLab/vrs-matcher/blob/6cf6bd1c0b27f1cc1a3bf040dfce086a8804bc56/docs/plugins.md#recommended-development-workflow)

## Quick Start ⚡

```sh
uv sync

uv run vrs-matcher plugins list
# example
# identity

uv run vrs-matcher match-samples SAMPLE_A SAMPLE_B --db variants.db --algorithm example
```

## Developing ⚙️

### Running as a script plugin

```sh
uv run vrs-matcher match-samples SAMPLE_A SAMPLE_B \
  --db variants.db \
  --plugin-file src/vrs_matcher_example_plugin/example_plugin.py
```

### Testing

Validate against a small cohort with known expected rankings, and compare against the built-in `identity` plugin:

```sh
# Match one sample against all others, ranked
uv run vrs-matcher match-sample SAMPLE_A --db variants.db --algorithm example

# Compare to the built-in identity plugin
uv run vrs-matcher match-sample SAMPLE_A --db variants.db --algorithm identity
```

### Project Layout

```sh
vrs-matcher-example-plugin/
├── pyproject.toml
├── README.md
└── src/
    └── vrs_matcher_example_plugin/
        ├── __init__.py
        └── example_plugin.py   # Example Plugin
```
