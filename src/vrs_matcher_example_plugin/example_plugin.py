"""Example custom matcher plugin for vrs-matcher: panel-restricted matching.

This plugin demonstrates the idea not shown by the other bundled examples in
the main repo (``examples/plugins/jaccard_floor_plugin.py`` and
``examples/plugins/my_plugin.py``): restricting matching to a fixed set of VRS
IDs that the *plugin itself* owns -- e.g. a disease gene panel -- rather than
relying solely on the caller-supplied ``candidate_vrs_ids``.

Scoring is otherwise identical to the built-in ``identity`` matcher: plain
Jaccard over the restricted ID sets. The point of the example is the
*restriction*, not the scoring.

The panel below holds real VRS IDs from the main repo's
``examples/example-cohort.vcf.gz`` so the example produces meaningful rankings
out of the box. Replace it with VRS IDs from your own gene panel.

NOTE: panel-restricted similarity is NOT genome-wide identity. Make sure QC
users know the matching is restricted to the panel.
"""

from __future__ import annotations

from vrs_matcher.matcher import MatchResult, jaccard, weighted_concordance
from vrs_matcher.plugins import PLUGIN_API_VERSION

# A small illustrative "panel" using real VRS IDs from the main repo's example
# cohort (examples/example-cohort.vcf.gz). ga4gh:VA.def456 is deliberately
# omitted, so panel-restricted rankings differ from the built-in identity
# matcher -- demonstrating that panel similarity != genome-wide identity.
# Replace this with a curated set of VRS IDs for your own panel, e.g. loaded
# from a sidecar file or packaged alongside this plugin.
EXAMPLE_PANEL: frozenset[str] = frozenset(
    {
        "ga4gh:VA.abc123",
        "ga4gh:VA.ghi789",
    }
)


class ExamplePlugin:
    """Restrict matching to a fixed panel of VRS IDs, then score by Jaccard."""

    name = "example"
    api_version = PLUGIN_API_VERSION

    def __init__(self, panel: frozenset[str] = EXAMPLE_PANEL) -> None:
        self.panel = panel

    def _restrict(self, candidate_vrs_ids: frozenset[str] | None) -> frozenset[str]:
        """Combine the plugin's panel with any caller-supplied candidate set.

        The plugin always restricts to its own panel; if the caller also passes
        ``candidate_vrs_ids``, we intersect so both constraints apply.
        """
        if candidate_vrs_ids is None:
            return self.panel
        return self.panel & candidate_vrs_ids

    def match_pair(
        self,
        context,
        sample_a: str,
        sample_b: str,
        *,
        candidate_vrs_ids: frozenset[str] | None = None,
    ) -> MatchResult:
        for sid in (sample_a, sample_b):
            if not context.sample_exists(sid):
                raise KeyError(sid)

        allowed = self._restrict(candidate_vrs_ids)

        ids_a = context.get_vrs_ids(sample_a) & allowed
        ids_b = context.get_vrs_ids(sample_b) & allowed
        states_a = {
            k: v for k, v in context.get_genotype_states(sample_a).items() if k in allowed
        }
        states_b = {
            k: v for k, v in context.get_genotype_states(sample_b).items() if k in allowed
        }

        return MatchResult(
            sample_a=sample_a,
            sample_b=sample_b,
            jaccard=jaccard(ids_a, ids_b),
            weighted_concordance=weighted_concordance(states_a, states_b),
            shared_vrs_ids=ids_a & ids_b,
            total_a=len(ids_a),
            total_b=len(ids_b),
        )

    def match_against_all(
        self,
        context,
        sample_id: str,
        *,
        top_n: int | None = None,
        candidate_vrs_ids: frozenset[str] | None = None,
    ) -> list[MatchResult]:
        if not context.sample_exists(sample_id):
            raise KeyError(sample_id)

        results = [
            self.match_pair(context, sample_id, other, candidate_vrs_ids=candidate_vrs_ids)
            for other in context.list_samples()
            if other != sample_id
        ]
        results.sort(key=lambda result: result.jaccard, reverse=True)
        return results[:top_n] if top_n is not None else results


def create_plugin() -> ExamplePlugin:
    return ExamplePlugin()
