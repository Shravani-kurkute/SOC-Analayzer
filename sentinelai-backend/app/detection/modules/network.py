from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult


class NetworkDetectionModule(BaseDetectionModule):
    name = "network"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "NET-001":
            return self._port_scan(rule, matching)
        elif rule_id == "NET-002":
            return self._internal_recon(rule, matching)
        elif rule_id == "NET-003":
            return self._lateral_movement(rule, matching)
        return None

    def _port_scan(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_ports: dict[str, set[int]] = {}
        threshold = rule.get("threshold", {}).get("unique_ports", 10)
        for e in events:
            src_ip = e.get("src_ip") or e.get("source_ip")
            dst_port = e.get("dest_port") or e.get("destination_port")
            if src_ip and dst_port is not None:
                ip_ports.setdefault(src_ip, set()).add(int(dst_port))
        for ip, ports in ip_ports.items():
            if len(ports) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Port Scan Detected from {ip}",
                    description=f"Source {ip} scanned {len(ports)} unique ports: {', '.join(str(p) for p in sorted(ports)[:20])}",
                    source_ip=ip,
                    severity="medium",
                    score=50,
                    tags=["network", "port-scan", "reconnaissance", "T1046"],
                    raw_data={"ip": ip, "ports_scanned": sorted(ports)},
                )
        return None

    def _internal_recon(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_dests: dict[str, set[str]] = {}
        threshold = rule.get("threshold", {}).get("unique_destinations", 5)
        for e in events:
            src_ip = e.get("src_ip") or e.get("source_ip")
            dst_ip = e.get("dest_ip") or e.get("destination_ip")
            if src_ip and dst_ip:
                ip_dests.setdefault(src_ip, set()).add(dst_ip)
        for ip, dests in ip_dests.items():
            if len(dests) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Internal Reconnaissance from {ip}",
                    description=f"Internal host {ip} contacted {len(dests)} unique destinations, suggesting internal scanning or lateral movement.",
                    source_ip=ip,
                    severity="high",
                    score=70,
                    tags=["network", "internal-recon", "reconnaissance", "T1595"],
                    raw_data={"source_ip": ip, "destinations": list(dests)},
                )
        return None

    def _lateral_movement(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        user_dests: dict[str, set[str]] = {}
        ip_dests: dict[str, set[str]] = {}
        threshold = rule.get("threshold", {}).get("unique_destinations", 3)
        for e in events:
            src_ip = e.get("src_ip") or e.get("source_ip")
            dst_ip = e.get("dest_ip") or e.get("destination_ip")
            username = e.get("username", "")
            if src_ip and dst_ip:
                ip_dests.setdefault(src_ip, set()).add(dst_ip)
            if username and dst_ip:
                user_dests.setdefault(username, set()).add(dst_ip)
        for ip, dests in ip_dests.items():
            if len(dests) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Lateral Movement from {ip}",
                    description=f"Host {ip} accessed {len(dests)} different internal systems: {', '.join(list(dests)[:10])}",
                    source_ip=ip,
                    severity="critical",
                    score=90,
                    tags=["network", "lateral-movement", "T1021"],
                    raw_data={"source_ip": ip, "destinations": list(dests)},
                )
        for user, dests in user_dests.items():
            if len(dests) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Lateral Movement by User {user}",
                    description=f"User {user} accessed {len(dests)} different systems: {', '.join(list(dests)[:10])}",
                    severity="critical",
                    score=90,
                    tags=["network", "lateral-movement", "T1021"],
                    raw_data={"username": user, "destinations": list(dests)},
                )
        return None
