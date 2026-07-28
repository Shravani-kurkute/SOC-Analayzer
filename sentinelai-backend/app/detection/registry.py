from typing import Any


_RULES: dict[str, dict[str, Any]] = {}


def register_rule(rule: dict[str, Any]) -> None:
    _RULES[rule["id"]] = rule


def get_rule(rule_id: str) -> dict[str, Any] | None:
    return _RULES.get(rule_id)


def get_all_rules() -> list[dict[str, Any]]:
    return list(_RULES.values())


def get_rules_by_category(category: str) -> list[dict[str, Any]]:
    return [r for r in _RULES.values() if r.get("category") == category]


def get_enabled_rules() -> list[dict[str, Any]]:
    return [r for r in _RULES.values() if r.get("enabled", True)]


class DetectionRuleRegistry:
    @classmethod
    def register(cls, rule: dict[str, Any]) -> None:
        register_rule(rule)

    @classmethod
    def get(cls, rule_id: str) -> dict[str, Any] | None:
        return get_rule(rule_id)

    @classmethod
    def get_all(cls) -> list[dict[str, Any]]:
        return get_all_rules()

    @classmethod
    def get_enabled(cls) -> list[dict[str, Any]]:
        return get_enabled_rules()
