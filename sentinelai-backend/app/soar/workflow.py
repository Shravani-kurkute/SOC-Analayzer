from typing import Any


def evaluate_condition(condition: dict[str, Any], context: dict[str, Any]) -> bool:
    field = condition.get("field", "")
    operator = condition.get("operator", "equals")
    value = condition.get("value")

    actual = context.get(field, "")

    if operator == "equals":
        return actual == value
    elif operator == "not_equals":
        return actual != value
    elif operator == "contains":
        return value in str(actual) if actual else False
    elif operator == "greater_than":
        try:
            return float(actual) > float(value)
        except (ValueError, TypeError):
            return False
    elif operator == "less_than":
        try:
            return float(actual) < float(value)
        except (ValueError, TypeError):
            return False
    elif operator == "in":
        return actual in (value or [])
    elif operator == "not_in":
        return actual not in (value or [])
    elif operator == "is_empty":
        return not actual
    elif operator == "is_not_empty":
        return bool(actual)
    return False


def resolve_next_steps(steps: list[dict[str, Any]], current_index: int, context: dict[str, Any]) -> list[int]:
    current = steps[current_index] if current_index < len(steps) else None
    if not current:
        return [current_index + 1] if current_index + 1 < len(steps) else []

    node_type = current.get("type", "action")
    config = current.get("config", {})

    if node_type == "condition":
        branches = config.get("branches", [])
        for branch in branches:
            condition = branch.get("condition", {})
            if evaluate_condition(condition, context):
                target = branch.get("target_index")
                if target is not None and 0 <= target < len(steps):
                    return [target]
        default_target = config.get("default_target")
        if default_target is not None and 0 <= default_target < len(steps):
            return [default_target]
        return [current_index + 1] if current_index + 1 < len(steps) else []

    elif node_type == "delay":
        return [current_index + 1] if current_index + 1 < len(steps) else []

    elif node_type == "approval":
        return [current_index + 1] if current_index + 1 < len(steps) else []

    elif node_type == "loop":
        max_iterations = config.get("max_iterations", 3)
        loop_count = context.get(f"_loop_{current_index}", 0)
        if loop_count < max_iterations:
            context[f"_loop_{current_index}"] = loop_count + 1
            loop_body_start = config.get("body_start_index")
            if loop_body_start is not None and 0 <= loop_body_start < len(steps):
                return [loop_body_start]
        return [current_index + 1] if current_index + 1 < len(steps) else []

    return [current_index + 1] if current_index + 1 < len(steps) else []
