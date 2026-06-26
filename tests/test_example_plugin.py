"""Tests for the panel-restricted ExamplePlugin.

These use a small in-memory fake ``context`` so the tests have no database
dependency. The fake mirrors the read-only context interface documented in
the main repo's docs/plugins.md.
"""

from __future__ import annotations

import pytest

from vrs_matcher.models import GenotypeState, Zygosity
from vrs_matcher_example_plugin import ExamplePlugin, create_plugin


def _het(gt="0/1"):
    return GenotypeState(gt=gt, zygosity=Zygosity.HET)


def _hom_alt(gt="1/1"):
    return GenotypeState(gt=gt, zygosity=Zygosity.HOM_ALT)


class FakeContext:
    """Minimal stand-in for the read-only plugin context.

    Sample membership mirrors the main repo's examples/example-cohort.vcf.gz:

        VRS ID            A      B      C
        ga4gh:VA.abc123   het    het    -
        ga4gh:VA.def456   hom    -      het
        ga4gh:VA.ghi789   het    het    -
    """

    def __init__(self) -> None:
        self._vrs_ids = {
            "SAMPLE_A": frozenset(
                {"ga4gh:VA.abc123", "ga4gh:VA.def456", "ga4gh:VA.ghi789"}
            ),
            "SAMPLE_B": frozenset({"ga4gh:VA.abc123", "ga4gh:VA.ghi789"}),
            "SAMPLE_C": frozenset({"ga4gh:VA.def456"}),
        }
        self._states = {
            "SAMPLE_A": {
                "ga4gh:VA.abc123": _het(),
                "ga4gh:VA.def456": _hom_alt(),
                "ga4gh:VA.ghi789": _het(),
            },
            "SAMPLE_B": {
                "ga4gh:VA.abc123": _het(),
                "ga4gh:VA.ghi789": _het(),
            },
            "SAMPLE_C": {"ga4gh:VA.def456": _het()},
        }

    def sample_exists(self, sample_id):
        return sample_id in self._vrs_ids

    def get_vrs_ids(self, sample_id):
        return self._vrs_ids[sample_id]

    def get_genotype_states(self, sample_id):
        return self._states[sample_id]

    def list_samples(self):
        return list(self._vrs_ids)


@pytest.fixture
def context():
    return FakeContext()


def test_create_plugin_returns_instance():
    plugin = create_plugin()
    assert isinstance(plugin, ExamplePlugin)
    assert plugin.name == "example"


def test_panel_restricts_scoring(context):
    """Only panel IDs count, so out-of-panel matches are excluded.

    The default panel omits ga4gh:VA.def456. Within {abc123, ghi789}:
      A & B = {abc123, ghi789} -> Jaccard 1.0
    """
    plugin = create_plugin()
    result = plugin.match_pair(context, "SAMPLE_A", "SAMPLE_B")
    assert result.jaccard == pytest.approx(1.0)
    assert result.shared_vrs_ids == {"ga4gh:VA.abc123", "ga4gh:VA.ghi789"}
    assert result.total_a == 2
    assert result.total_b == 2


def test_out_of_panel_only_match_drops_to_zero(context):
    """SAMPLE_C shares only the out-of-panel def456 with SAMPLE_A."""
    plugin = create_plugin()
    result = plugin.match_pair(context, "SAMPLE_A", "SAMPLE_C")
    assert result.jaccard == pytest.approx(0.0)
    assert result.shared_vrs_ids == set()
    assert result.total_a == 2  # A's in-panel IDs: abc123, ghi789
    assert result.total_b == 0  # C has no in-panel IDs


def test_panel_differs_from_unrestricted_identity(context):
    """The whole point: panel ranking differs from genome-wide identity.

    Unrestricted, C would share def456 with A (non-zero). Restricted to the
    panel, C drops to zero while B stays top.
    """
    plugin = create_plugin()
    results = plugin.match_against_all(context, "SAMPLE_A")
    ranked = [(r.sample_b, r.jaccard) for r in results]
    assert ranked[0][0] == "SAMPLE_B"
    assert ranked[0][1] == pytest.approx(1.0)
    # C's only shared variant is outside the panel -> 0.0
    c_score = dict(ranked)["SAMPLE_C"]
    assert c_score == pytest.approx(0.0)


def test_caller_candidate_ids_intersect_with_panel(context):
    """A caller-supplied candidate set narrows the panel further.

    Restricting to {ghi789} (a subset of the panel) leaves A & B sharing only
    ghi789 -> Jaccard still 1.0 but on one shared ID.
    """
    plugin = create_plugin()
    result = plugin.match_pair(
        context,
        "SAMPLE_A",
        "SAMPLE_B",
        candidate_vrs_ids=frozenset({"ga4gh:VA.ghi789"}),
    )
    assert result.shared_vrs_ids == {"ga4gh:VA.ghi789"}
    assert result.total_a == 1
    assert result.total_b == 1


def test_candidate_ids_outside_panel_yield_empty(context):
    """An out-of-panel candidate set intersects the panel to empty -> no IDs."""
    plugin = create_plugin()
    result = plugin.match_pair(
        context,
        "SAMPLE_A",
        "SAMPLE_B",
        candidate_vrs_ids=frozenset({"ga4gh:VA.def456"}),
    )
    assert result.total_a == 0
    assert result.total_b == 0
    assert result.shared_vrs_ids == set()


def test_missing_sample_raises_keyerror(context):
    plugin = create_plugin()
    with pytest.raises(KeyError):
        plugin.match_pair(context, "SAMPLE_A", "NOPE")
    with pytest.raises(KeyError):
        plugin.match_against_all(context, "NOPE")
