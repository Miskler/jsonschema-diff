from typing import TYPE_CHECKING, Any, List, Sequence, TypeAlias

if TYPE_CHECKING:
    from ..abstraction import Statuses
    from ..config import Config

PATH_MAKER_IGNORE_RULES_TYPE: TypeAlias = Sequence[str]


class RenderTool:
    """
    Small helper utilities used by the rendering subsystem.
    """

    # --------------------------------------------------------------------- #
    # Basic helpers
    # --------------------------------------------------------------------- #

    @staticmethod
    def make_tab(config: "Config", tab_level: int) -> str:
        """
        Return indentation string.

        Parameters
        ----------
        config : Config
            Application config that owns the ``TAB`` constant.
        tab_level : int
            Indentation depth.

        Returns
        -------
        str
            ``config.TAB`` repeated *tab_level* times.
        """
        return config.TAB * tab_level

    @staticmethod
    def make_prefix(status: "Statuses") -> str:
        """
        Convert a ``Statuses`` enum value to its printable form.

        Parameters
        ----------
        status : Statuses
            Validation status.

        Returns
        -------
        str
            ``status.value`` as plain text.
        """
        return f"{status.value}"

    # --------------------------------------------------------------------- #
    # Path builder
    # --------------------------------------------------------------------- #

    @staticmethod
    def make_path(
        schema_path: Sequence[Any],
        json_path: Sequence[Any],
        ignore: PATH_MAKER_IGNORE_RULES_TYPE = ("properties",),
    ) -> str:
        """
        Compose a human‑readable path by synchronising two parallel paths.

        The function walks through *schema_path* (tokens from JSON Schema) and
        *json_path* (real path in the JSON instance) and emits a short textual
        representation such as ``["items"][0].extra``.

        Parameters
        ----------
        schema_path : Sequence[Any]
            Tokens encountered while traversing the schema.
        json_path : Sequence[Any]
            Path tokens from the actual JSON document.
        ignore : Sequence[str], default (``"properties"``,)
            Schema‑only service tokens to skip.

        Returns
        -------
        str
            Compact path string.

        Algorithm
        ---------
        i — index in *schema_path*, j — index in *json_path*.

        1.  If *schema_path[i]* is in *ignore* and **differs** from
            *json_path[j]* → skip it.
        2.  If tokens are equal → emit as property/index and advance both.
        3.  Otherwise the token exists only in schema → emit as ``.token`` and
            advance *i*.
        4.  After the schema is exhausted, append remaining elements of
            *json_path*.

        Integer‑like tokens are rendered as ``[n]``; everything else as
        ``["key"]``.
        """
        parts: List[str] = []
        i = j = 0

        while i < len(schema_path):
            s_tok = schema_path[i]

            # 1. Ignore schema-only service tokens
            if s_tok in ignore and (j >= len(json_path) or str(s_tok) != str(json_path[j])):
                i += 1
                continue

            # 2. Token is present in both paths
            if j < len(json_path) and str(s_tok) == str(json_path[j]):
                tok = json_path[j]
                parts.append(f"[{tok}]" if isinstance(tok, int) else f'["{tok}"]')
                i += 1
                j += 1
                continue

            # 3. Token is schema-only – treat as extra property
            parts.append(f".{s_tok}")
            i += 1

        # 4. Append the rest of json_path
        for tok in json_path[j:]:
            parts.append(f"[{tok}]" if isinstance(tok, int) else f'["{tok}"]')

        return "".join(parts)
