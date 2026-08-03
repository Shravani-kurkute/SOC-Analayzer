from __future__ import annotations

import json


def build_investigation_prompt(
    incident: dict,
    alerts: list[dict],
    iocs: list[dict],
    threat_intel: list[dict],
    mitre_techniques: list[dict],
    correlated_events: list[dict],
    timeline: list[dict],
) -> str:
    alert_summary = []
    for a in alerts:
        alert_summary.append({
            "title": a.get("title"),
            "severity": a.get("severity"),
            "source_ip": a.get("source_ip"),
            "destination_ip": a.get("destination_ip"),
            "source_port": a.get("source_port"),
            "destination_port": a.get("destination_port"),
            "protocol": a.get("protocol"),
            "mitre_technique_id": a.get("mitre_technique_id"),
            "mitre_tactic": a.get("mitre_tactic"),
            "score": a.get("score"),
            "country": a.get("country"),
            "recommendation": a.get("recommendation"),
            "tags": a.get("tags"),
            "raw_data": a.get("raw_data"),
            "created_at": a.get("created_at"),
        })

    incident_data = {
        "id": incident.get("id"),
        "title": incident.get("title"),
        "description": incident.get("description"),
        "severity": incident.get("severity"),
        "status": incident.get("status"),
        "category": incident.get("category"),
        "alert_count": len(alerts),
    }

    return _build_prompt(incident_data, alert_summary, iocs, threat_intel, mitre_techniques, correlated_events, timeline)


def _build_prompt(
    incident: dict,
    alerts: list[dict],
    iocs: list[dict],
    threat_intel: list[dict],
    mitre_techniques: list[dict],
    correlated_events: list[dict],
    timeline: list[dict],
) -> str:
    prompt = f"""You are an expert SOC analyst investigating a security incident.

## Incident
{json.dumps(incident, indent=2, default=str)}

## Alerts ({len(alerts)})
{json.dumps(alerts, indent=2, default=str) if alerts else "None"}

## IOCs ({len(iocs)})
{json.dumps(iocs, indent=2, default=str) if iocs else "None"}

## Threat Intelligence ({len(threat_intel)})
{json.dumps(threat_intel, indent=2, default=str) if threat_intel else "None"}

## MITRE ATT&CK Techniques ({len(mitre_techniques)})
{json.dumps(mitre_techniques, indent=2, default=str) if mitre_techniques else "None"}

## Correlated Events ({len(correlated_events)})
{json.dumps(correlated_events, indent=2, default=str) if correlated_events else "None"}

## Timeline ({len(timeline)})
{json.dumps(timeline, indent=2, default=str) if timeline else "None"}

---
Analyze this incident using ONLY the data provided above. Do not fabricate information.

Return a JSON object with these exact keys (use null for any section that cannot be determined):
- "executive_summary": string - concise overview for management
- "attack_explanation": string - technical walkthrough of the attack chain
- "root_cause": string - what enabled the attack
- "mitre_explanation": string - explain each MITRE technique observed and its significance
- "ioc_summary": string - summarize indicators of compromise with their context
- "risk_explanation": string - explain the business and security risk
- "recommendations": array of {{"priority": "critical|high|medium|low", "action": string, "details": string}}
- "containment": string - immediate steps to contain the incident
- "recovery": string - steps to restore normal operations
- "hunting_queries": array of {{"type": string, "query": string, "description": string}}
- "false_positive_probability": float 0.0 to 1.0
- "confidence_score": float 0.0 to 1.0
- "timeline": array of {{"timestamp": string, "event": string, "source": string, "detail": string}}"""
    return prompt
