from __future__ import annotations

import json
import re

from app.core.config import settings


def parse_ai_response(response_text: str) -> dict:
    text = response_text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = _fallback_parse(text)

    return {
        "summary": data.get("executive_summary") or "",
        "attack_explanation": data.get("attack_explanation") or "",
        "root_cause": data.get("root_cause") or "",
        "mitre_explanation": data.get("mitre_explanation") or "",
        "ioc_summary": data.get("ioc_summary") or "",
        "risk_explanation": data.get("risk_explanation") or "",
        "recommendations": data.get("recommendations", []),
        "containment": data.get("containment") or "",
        "recovery": data.get("recovery") or "",
        "hunting_queries": data.get("hunting_queries", []),
        "false_positive_probability": _clamp(data.get("false_positive_probability"), 0.0, 1.0),
        "confidence_score": _clamp(data.get("confidence_score"), 0.0, 1.0),
        "timeline_data": data.get("timeline", []),
    }


def _clamp(val: float | None, lo: float, hi: float) -> float | None:
    if val is None:
        return None
    try:
        return max(lo, min(hi, float(val)))
    except (ValueError, TypeError):
        return None


def _fallback_parse(text: str) -> dict:
    data: dict = {}

    section_map = {
        "executive_summary": ["executive summary", "summary"],
        "attack_explanation": ["attack explanation", "attack chain", "attack analysis"],
        "root_cause": ["root cause"],
        "mitre_explanation": ["mitre explanation", "mitre analysis"],
        "ioc_summary": ["ioc summary", "indicators of compromise"],
        "risk_explanation": ["risk explanation", "risk analysis"],
        "containment": ["containment"],
        "recovery": ["recovery"],
    }

    current_section = None
    current_lines: list[str] = []

    for line in text.split("\n"):
        lower = line.strip().lower().rstrip(":")
        for key, aliases in section_map.items():
            if any(lower.startswith(a) for a in aliases):
                if current_section and current_lines:
                    data[current_section] = "\n".join(current_lines).strip()
                current_section = key
                current_lines = []
                break
        else:
            if current_section:
                current_lines.append(line)

    if current_section and current_lines:
        data[current_section] = "\n".join(current_lines).strip()

    return data
