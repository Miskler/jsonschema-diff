from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    List,
    Mapping,
    Sequence,
    Type,
    TypeAlias,
    Union,
)

if TYPE_CHECKING:
    from jsonschema_diff.core.compare_base import Compare

# Key type accepted in rules: parameter name or Compare subclass
RULE_KEY: TypeAlias = Union[str, Type["Compare"]]

CONTEXT_RULES_TYPE: TypeAlias = Mapping[RULE_KEY, Sequence[RULE_KEY]]
PAIR_CONTEXT_RULES_TYPE: TypeAlias = Sequence[Sequence[RULE_KEY]]


class RenderContextHandler:
    """Expand context comparators based on pair- and directed-dependency rules."""

    @staticmethod
    def resolve(
        *,
        pair_context_rules: PAIR_CONTEXT_RULES_TYPE,
        context_rules: CONTEXT_RULES_TYPE,
        for_render: Mapping[str, "Compare"],
        not_for_render: Mapping[str, "Compare"],
    ) -> Dict[str, "Compare"]:
        """
        Build the final ordered context for rendering.

        Parameters
        ----------
        pair_context_rules : Sequence[Sequence[RULE_KEY]]
            Undirected groups: if one member is rendered, pull the rest (order preserved).
        context_rules : Mapping[RULE_KEY, Sequence[RULE_KEY]]
            Directed dependencies: ``source → [targets...]``.
        for_render : Mapping[str, Compare]
            Initial items, order defines primary screen order.
        not_for_render : Mapping[str, Compare]
            Optional items that may be added by the rules.

        Returns
        -------
        dict
            Ordered ``{name -> Compare}`` ready for UI.

        Algorithm (high-level)
        ----------------------
        * Walk through *for_render* keys.
        * While iterating, append new candidates to the tail of the scan list.
        * A candidate is added once when first matched by any rule.
        """
        out: Dict[str, "Compare"] = dict(for_render)  # preserves order
        pool_not: Dict[str, "Compare"] = dict(not_for_render)  # preserves insertion order

        seq: List[str] = list(out.keys())  # scan list
        in_out = set(seq)  # O(1) membership checks

        def _matches(rule: RULE_KEY, name: str, cmp_obj: "Compare") -> bool:
            """Return True if *rule* matches given *(name, object)* pair."""
            if isinstance(rule, str):
                return rule == name
            # rule is a comparator class
            try:
                return isinstance(cmp_obj, rule)
            except TypeError:
                return False

        def _expand(rule: RULE_KEY, pool: Mapping[str, "Compare"]) -> Iterable[str]:
            """
            Yield keys from *pool* matching *rule* (order-stable).

            * String rule → single key.
            * Class rule  → all keys whose comparator ``isinstance`` the class.
            """
            if isinstance(rule, str):
                if rule in pool:
                    yield rule
                return

            for n, obj in list(pool.items()):  # snapshot to stay safe on ``del``
                try:
                    if isinstance(obj, rule):
                        yield n
                except TypeError:
                    continue

        i = 0
        while i < len(seq):
            name = seq[i]
            cmp_obj = out[name]

            # 1) Undirected groups
            for group in pair_context_rules:
                if any(_matches(entry, name, cmp_obj) for entry in group):
                    for entry in group:
                        for cand in _expand(entry, pool_not):
                            if cand in in_out:
                                continue
                            out[cand] = pool_not[cand]
                            seq.append(cand)
                            in_out.add(cand)
                            del pool_not[cand]

            # 2) Directed dependencies
            for source, targets in context_rules.items():
                if _matches(source, name, cmp_obj):
                    for entry in targets:
                        for cand in _expand(entry, pool_not):
                            if cand in in_out:
                                continue
                            out[cand] = pool_not[cand]
                            seq.append(cand)
                            in_out.add(cand)
                            del pool_not[cand]

            i += 1

        return out
