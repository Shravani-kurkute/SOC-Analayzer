from __future__ import annotations


def build_timeline(
    alerts: list[dict],
    correlated_events: list[dict],
    iocs: list[dict],
) -> list[dict]:
    entries: list[dict] = []

    for a in alerts:
        entry = {
            "timestamp": a.get("created_at") or a.get("updated_at") or "",
            "event": f"Alert triggered: {a.get('title', 'Unknown')}",
            "source": "Detection Engine",
            "detail": f"Severity: {a.get('severity', 'N/A')} | Source: {a.get('source_ip', 'N/A')} | MITRE: {a.get('mitre_technique_id', 'N/A')}",
        }
        if entry["timestamp"]:
            entries.append(entry)

    for ev in correlated_events:
        entry = {
            "timestamp": ev.get("timestamp") or "",
            "event": f"Correlated event: {ev.get('event_type', 'Unknown')}",
            "source": ev.get("event_source", "Correlation Engine"),
            "detail": f"Action: {ev.get('action', 'N/A')} | IP: {ev.get('source_ip', 'N/A')}",
        }
        if entry["timestamp"]:
            entries.append(entry)

    for ioc in iocs:
        entry = {
            "timestamp": ioc.get("first_seen") or ioc.get("last_seen") or "",
            "event": f"IOC identified: {ioc.get('ioc_type', 'Unknown')}",
            "source": "IOC Extraction",
            "detail": f"Value: {ioc.get('ioc_value', 'N/A')} | Confidence: {ioc.get('confidence', 'N/A')}",
        }
        if entry["timestamp"]:
            entries.append(entry)

    entries.sort(key=lambda x: x.get("timestamp", ""))
    return entries
