from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.modules import BaseDetectionModule
from app.schemas.detection import DetectionResult


class FirewallDetectionModule(BaseDetectionModule):
    name = "firewall"

    async def analyze(
        self, rule: dict[str, Any], events: list[dict[str, Any]], db_session: AsyncSession
    ) -> DetectionResult | None:
        conditions = rule.get("conditions", {})
        matching = self._find_events(events, conditions)
        if not matching:
            return None

        rule_id = rule["id"]

        if rule_id == "FW-001":
            return self._excessive_denies(rule, matching)
        elif rule_id == "FW-002":
            return self._blocked_scanning(rule, matching)
        return None

    def _excessive_denies(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_denies: dict[str, list[dict[str, Any]]] = {}
        threshold = rule.get("threshold", {}).get("min_denies", 20)
        for e in events:
            src_ip = e.get("src_ip") or e.get("source_ip")
            if src_ip:
                ip_denies.setdefault(src_ip, []).append(e)
        for ip, denies in ip_denies.items():
            if len(denies) >= threshold:
                avg_port = None
                ports = [d.get("dest_port") or d.get("destination_port") for d in denies if d.get("dest_port") or d.get("destination_port")]
                if ports:
                    avg_port = sum(ports) // len(ports)
                return self._build_result(
                    rule, None,
                    title=f"Excessive Firewall Denies from {ip}",
                    description=f"Firewall blocked {len(denies)} attempts from {ip} to {len(set([d.get('dest_ip') or d.get('destination_ip', '') for d in denies]))} different destinations.",
                    source_ip=ip,
                    destination_port=avg_port,
                    severity="medium",
                    score=45,
                    tags=["firewall", "excessive-denies", "reconnaissance", "T1595"],
                    raw_data={"source_ip": ip, "deny_count": len(denies)},
                )
        return None

    def _blocked_scanning(self, rule: dict[str, Any], events: list[dict[str, Any]]) -> DetectionResult | None:
        ip_ports: dict[str, set[int]] = {}
        threshold = rule.get("threshold", {}).get("unique_ports", 15)
        for e in events:
            src_ip = e.get("src_ip") or e.get("source_ip")
            dst_port = e.get("dest_port") or e.get("destination_port")
            if src_ip and dst_port is not None:
                ip_ports.setdefault(src_ip, set()).add(int(dst_port))
        for ip, ports in ip_ports.items():
            if len(ports) >= threshold:
                return self._build_result(
                    rule, None,
                    title=f"Blocked Port Scan from {ip}",
                    description=f"Firewall blocked systematic scanning from {ip} across {len(ports)} unique ports: {', '.join(str(p) for p in sorted(ports)[:20])}",
                    source_ip=ip,
                    severity="medium",
                    score=55,
                    tags=["firewall", "blocked-scan", "T1046"],
                    raw_data={"source_ip": ip, "ports_scanned": sorted(ports)},
                )
        return None
