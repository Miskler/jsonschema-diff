# Импортируем резолвер из проекта; оставлен fallback на локальный context.py
from jsonschema_diff.core.tools.context import RenderContextHandler


# ---- Заглушки компараторов для матчей по классам ----
class CmpBase: ...


class CompareType(CmpBase): ...


class CompareFormat(CmpBase): ...


class ComparePattern(CmpBase): ...


class CompareRange(CmpBase): ...


class CompareRangeLength(CmpBase): ...


class CompareItems(CmpBase): ...


class CompareUniqueItems(CmpBase): ...


class CompareRef(CmpBase): ...


class CompareDefs(CmpBase): ...


def _klist(od):
    """Ключи результата в порядке вывода."""
    return list(od.keys())


def test_no_context_added_when_no_rules_match():
    pair_rules = []
    context_rules = {}
    for_render = {"$id": CmpBase()}
    not_for_render = {"type": CompareType(), "format": CompareFormat()}
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render=for_render,
        not_for_render=not_for_render,
    )
    assert _klist(res) == ["$id"]
    # Значение сохранено как есть (по идентичности объекта)
    assert res["$id"] is for_render["$id"]


def test_pair_rule_string_adds_other_side_forward_and_reverse():
    pair_rules = [["type", "format"]]
    context_rules = {}

    # format -> подтягивает type
    res1 = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"format": CompareFormat()},
        not_for_render={"type": CompareType()},
    )
    assert _klist(res1) == ["format", "type"]

    # type -> подтягивает format
    res2 = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"type": CompareType()},
        not_for_render={"format": CompareFormat()},
    )
    assert _klist(res2) == ["type", "format"]


def test_pair_rule_class_and_string_bidirectional():
    # Группа смешанная: класс + строка
    pair_rules = [[ComparePattern, "type"]]
    context_rules = {}

    # Случай: pattern триггерит type
    res1 = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"pattern": ComparePattern()},
        not_for_render={"type": CompareType()},
    )
    assert _klist(res1) == ["pattern", "type"]

    # Обратный случай: type подтягивает ВСЕ pattern-ключи из not_for_render по их порядку
    res2 = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"type": CompareType()},
        not_for_render={
            "a": ComparePattern(),
            "b": ComparePattern(),
            "c": CompareFormat(),
        },  # 'c' не pattern
    )
    assert _klist(res2) == ["type", "a", "b"]
    # Проверяем, что подтянутые — именно исходные объекты
    assert res2["a"].__class__ is ComparePattern
    assert res2["b"].__class__ is ComparePattern


def test_context_rule_directed_string_to_class():
    # Однонаправленная зависимость: uniqueItems -> все CompareItems
    pair_rules = []
    context_rules = {"uniqueItems": [CompareItems]}
    for_render = {"uniqueItems": CompareUniqueItems()}
    not_for_render = {
        "items": CompareItems(),
        "prefixItems": CompareItems(),
        "type": CompareType(),
    }
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render=for_render,
        not_for_render=not_for_render,
    )
    # Порядок: исходный ключ, затем кандидаты из not_for_render в их порядке
    assert _klist(res) == ["uniqueItems", "items", "prefixItems"]
    # 'type' не матчится по этому правилу
    assert "type" not in res


def test_context_rule_is_one_way_not_reverse():
    # Есть правило: uniqueItems -> CompareItems
    pair_rules = []
    context_rules = {"uniqueItems": [CompareItems]}
    # Стартуем с items: обратного правила нет => uniqueItems НЕ подтянется
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"items": CompareItems()},
        not_for_render={"uniqueItems": CompareUniqueItems()},
    )
    assert _klist(res) == ["items"]


def test_no_inventing_keys_when_target_absent():
    # Есть группа [pattern, format], но в not_for_render нет pattern
    pair_rules = [["pattern", "format"]]
    context_rules = {}
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"format": CompareFormat()},
        not_for_render={"type": CompareType()},
    )
    # Ничего лишнего не «придумываем»
    assert _klist(res) == ["format"]


def test_order_preservation_append_to_tail():
    # Классический кейс: ['rangeLength', 'format'] + в not_for_render только type
    pair_rules = [["type", "format"]]
    context_rules = {}
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"rangeLength": CompareRangeLength(), "format": CompareFormat()},
        not_for_render={"type": CompareType()},
    )
    assert _klist(res) == ["rangeLength", "format", "type"]


def test_chained_expansion_via_newly_added_keys():
    # Цепочка: pattern ->(pair)-> type, а уже type ->(pair)-> format
    pair_rules = [[ComparePattern, "type"], ["type", "format"]]
    context_rules = {}
    for_render = {"pattern": ComparePattern()}
    not_for_render = {"type": CompareType(), "format": CompareFormat()}
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render=for_render,
        not_for_render=not_for_render,
    )
    assert _klist(res) == ["pattern", "type", "format"]


def test_context_rule_with_class_source_triggers_by_instance():
    # Класс-источник: ComparePattern -> ['type']
    pair_rules = []
    context_rules = {ComparePattern: ["type"]}
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"pattern": ComparePattern()},
        not_for_render={"type": CompareType()},
    )
    assert _klist(res) == ["pattern", "type"]


def test_ref_defs_directed_rule():
    # $ref -> $defs
    pair_rules = []
    context_rules = {"$ref": ["$defs"]}
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"$ref": CompareRef()},
        not_for_render={"$defs": CompareDefs()},
    )
    assert _klist(res) == ["$ref", "$defs"]
    # И значения взяты из not_for_render
    assert isinstance(res["$defs"], CompareDefs)


def test_already_present_target_not_duplicated_and_order_kept():
    pair_rules = [[ComparePattern, "type"]]
    context_rules = {}
    # target ('type') уже в for_render — порядок исходного списка сохраняется,
    # дубликатов не появляется
    res = RenderContextHandler.resolve(
        pair_context_rules=pair_rules,
        context_rules=context_rules,
        for_render={"pattern": ComparePattern(), "type": CompareType()},
        not_for_render={},
    )
    assert _klist(res) == ["pattern", "type"]
