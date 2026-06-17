# vrs-matcher-example-plugin 🌀

An example of a custom matching algorithm for [`vrs-matcher`](https://github.com/EllrottLab/vrs-matcher)

Built against the plugin support added in [PR #16](https://github.com/EllrottLab/vrs-matcher/pull/16)

> [!TIP]
>
> This repo follows the steps in [`plugins.md`](https://github.com/EllrottLab/vrs-matcher/blob/6cf6bd1c0b27f1cc1a3bf040dfce086a8804bc56/docs/plugins.md#recommended-development-workflow)

## Quick Start ⚡

```sh
uv sync

uv run vrs-matcher plugins list
# example
# identity

uv run vrs-matcher match-samples SAMPLE_A SAMPLE_B --db variants.db --algorithm example
```

## Developing 

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

```
vrs-matcher-example-plugin/
├── pyproject.toml          # package metadata + vrs_matcher.plugins entry point + git dep
├── README.md
└── src/
    └── vrs_matcher_example_plugin/
        ├── __init__.py         # re-exports ExamplePlugin / create_plugin
        └── example_plugin.py   # the plugin: ExamplePlugin + create_plugin()
```
