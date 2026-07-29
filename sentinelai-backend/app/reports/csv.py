import csv
import io


def build_csv(report_data: dict, report_type: str) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)

    if report_type == "executive":
        writer.writerow(["Metric", "Value"])
        for key in ("total_incidents", "critical_incidents", "resolved_incidents", "open_incidents",
                     "avg_response_time_seconds", "avg_resolution_time_seconds", "soc_health_score"):
            writer.writerow([key.replace("_", " ").title(), report_data.get(key, "")])

        if report_data.get("top_risks"):
            writer.writerow([])
            writer.writerow(["Top Risks", "Count"])
            for r in report_data["top_risks"]:
                writer.writerow([r.get("name", ""), r.get("count", 0)])

        if report_data.get("top_attack_types"):
            writer.writerow([])
            writer.writerow(["Attack Type", "Count"])
            for r in report_data["top_attack_types"]:
                writer.writerow([r.get("name", ""), r.get("count", 0)])

        if report_data.get("top_countries"):
            writer.writerow([])
            writer.writerow(["Country", "Count"])
            for r in report_data["top_countries"]:
                writer.writerow([r.get("name", ""), r.get("count", 0)])

    elif report_type == "threat":
        if report_data.get("ioc_summary"):
            writer.writerow(["IOC Type", "Count"])
            for r in report_data["ioc_summary"]:
                writer.writerow([r.get("type", ""), r.get("count", 0)])

        if report_data.get("attack_categories"):
            writer.writerow([])
            writer.writerow(["Category", "Count"])
            for r in report_data["attack_categories"]:
                writer.writerow([r.get("name", ""), r.get("count", 0)])

        if report_data.get("risk_distribution"):
            writer.writerow([])
            writer.writerow(["Severity", "Count"])
            for r in report_data["risk_distribution"]:
                writer.writerow([r.get("name", ""), r.get("count", 0)])

        if report_data.get("mitre_coverage"):
            writer.writerow([])
            writer.writerow(["MITRE Tactic", "Count"])
            for r in report_data["mitre_coverage"]:
                writer.writerow([r.get("tactic", ""), r.get("count", 0)])

    elif report_type == "incident":
        writer.writerow(["Field", "Value"])
        writer.writerow(["Incident ID", report_data.get("incident_id", "")])
        writer.writerow(["Title", report_data.get("incident_title", "")])
        writer.writerow(["Severity", report_data.get("severity", "")])
        writer.writerow(["Status", report_data.get("status", "")])
        writer.writerow(["Description", report_data.get("description", "") or ""])

        if report_data.get("tasks"):
            writer.writerow([])
            writer.writerow(["Task", "Status", "Priority", "Assignee"])
            for t in report_data["tasks"]:
                writer.writerow([t.get("title", ""), t.get("status", ""), t.get("priority", ""), t.get("assignee_name", "")])

        if report_data.get("evidence"):
            writer.writerow([])
            writer.writerow(["Evidence", "Type", "Size", "SHA256"])
            for e in report_data["evidence"]:
                writer.writerow([e.get("filename", ""), e.get("file_type", ""), e.get("file_size", ""), e.get("sha256", "")])

    elif report_type == "asset":
        writer.writerow(["Asset ID", "Name", "Type", "Criticality", "Owner"])
        for a in report_data.get("assets", []):
            writer.writerow([a.get("id", ""), a.get("name", ""), a.get("type", ""), a.get("criticality", ""), a.get("owner", "")])

    elif report_type == "compliance":
        writer.writerow(["Framework", "Status", "Coverage %"])
        for framework in ("soc2", "iso27001", "nist", "cis"):
            key = f"{framework}_coverage"
            cov = report_data.get(key, {})
            writer.writerow([framework.upper(), cov.get("status", ""), cov.get("percentage", 0)])

    return buf.getvalue().encode("utf-8")
