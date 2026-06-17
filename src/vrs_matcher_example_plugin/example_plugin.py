from vrs_matcher.matcher import MatchResult, jaccard, weighted_concordance
from vrs_matcher.plugins import PLUGIN_API_VERSION


class ExamplePlugin:
    name = "example"
    api_version = PLUGIN_API_VERSION

    def match_pair(self, context, sample_a, sample_b, *, candidate_vrs_ids=None):
        for sid in (sample_a, sample_b):
            if not context.sample_exists(sid):
                raise KeyError(sid)

        ids_a = context.get_vrs_ids(sample_a)
        ids_b = context.get_vrs_ids(sample_b)
        states_a = context.get_genotype_states(sample_a)
        states_b = context.get_genotype_states(sample_b)

        if candidate_vrs_ids is not None:
            ids_a = ids_a & candidate_vrs_ids
            ids_b = ids_b & candidate_vrs_ids
            states_a = {k: v for k, v in states_a.items() if k in candidate_vrs_ids}
            states_b = {k: v for k, v in states_b.items() if k in candidate_vrs_ids}

        return MatchResult(
            sample_a=sample_a,
            sample_b=sample_b,
            jaccard=jaccard(ids_a, ids_b),
            weighted_concordance=weighted_concordance(states_a, states_b),
            shared_vrs_ids=ids_a & ids_b,
            total_a=len(ids_a),
            total_b=len(ids_b),
        )

    def match_against_all(self, context, sample_id, *, top_n=None, candidate_vrs_ids=None):
        if not context.sample_exists(sample_id):
            raise KeyError(sample_id)

        results = [
            self.match_pair(context, sample_id, other, candidate_vrs_ids=candidate_vrs_ids)
            for other in context.list_samples()
            if other != sample_id
        ]
        results.sort(key=lambda result: result.jaccard, reverse=True)
        return results[:top_n] if top_n is not None else results


def create_plugin():
    return ExamplePlugin()

