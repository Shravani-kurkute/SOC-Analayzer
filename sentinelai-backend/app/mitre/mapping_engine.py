from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.database.session import async_session_factory
from app.models.mitre_technique import MitreMapping, MitreTechnique

DETECTION_RULE_MAP = {
    "ssh_brute_force": ["T1110", "T1021.004", "T1133"],
    "brute_force": ["T1110", "T1078"],
    "credential_stuffing": ["T1110.003", "T1078"],
    "port_scan": ["T1046", "T1499.002"],
    "firewall_block": ["T1499.002", "T1562"],
    "web_attack": ["T1190", "T1071.001"],
    "sql_injection": ["T1190"],
    "ssh_session": ["T1021.004"],
    "rdp_brute_force": ["T1021.001", "T1133"],
    "account_manipulation": ["T1098", "T1136"],
    "command_line_detection": ["T1059", "T1059.001", "T1059.003", "T1059.004"],
    "malware_detection": ["T1204.002", "T1105"],
}

IOC_TYPE_MAP = {
    "ipv4": ["T1071", "T1110", "T1190", "T1133"],
    "ipv6": ["T1071", "T1133"],
    "domain": ["T1071", "T1071.001", "T1071.004", "T1102", "T1566", "T1568"],
    "url": ["T1071.001", "T1190", "T1566", "T1105"],
    "email": ["T1566", "T1566.001", "T1566.002"],
    "username": ["T1078", "T1110", "T1098", "T1136", "T1087", "T1552"],
    "md5": ["T1027", "T1204.002", "T1105"],
    "sha1": ["T1027", "T1204.002", "T1105"],
    "sha256": ["T1027", "T1204.002", "T1105"],
    "cve": ["T1190", "T1068"],
    "process_name": ["T1059", "T1055", "T1057"],
    "executable_path": ["T1204.002", "T1055", "T1105"],
    "command_line": ["T1059", "T1059.001", "T1059.004"],
    "registry_key": ["T1547.001"],
    "port": ["T1046"],
    "protocol": ["T1071"],
}

CORRELATION_TYPE_MAP = {
    "ssh_session": ["T1021.004", "T1133"],
    "port_scan": ["T1046", "T1499.002"],
    "firewall_block": ["T1562", "T1499.002"],
    "web_attack": ["T1190", "T1071.001"],
    "web_error_chain": ["T1190"],
    "attack_chain": ["T1059", "T1071", "T1048", "T1486"],
    "credential_stuffing": ["T1110.003", "T1078"],
    "credential_compromise": ["T1110", "T1552", "T1555"],
    "targeted_attack": ["T1190", "T1068", "T1021", "T1486"],
}


class MappingEngine:
    def __init__(self):
        self._technique_cache: list[MitreTechnique] | None = None

    async def _get_techniques(self) -> list[MitreTechnique]:
        if self._technique_cache is None:
            async with async_session_factory() as session:
                result = await session.execute(select(MitreTechnique))
                self._technique_cache = list(result.scalars().all())
        return self._technique_cache

    async def map_entity(
        self, mapped_type: str, mapped_id: str,
        mapped_name: str | None = None, context: str | None = None,
        confidence: float | None = None,
    ) -> list[MitreMapping]:
        if context:
            technique_ids = self._detect_from_context(context)
        elif mapped_type == "detection_rule":
            technique_ids = DETECTION_RULE_MAP.get(mapped_id, [])
        elif mapped_type == "ioc":
            technique_ids = IOC_TYPE_MAP.get(mapped_id, [])
        elif mapped_type == "correlation_group":
            technique_ids = CORRELATION_TYPE_MAP.get(mapped_id, [])
        else:
            technique_ids = []

        if not technique_ids:
            return []

        async with async_session_factory() as session:
            now = datetime.now(timezone.utc)
            mappings: list[MitreMapping] = []
            for tid in technique_ids:
                existing = await session.execute(
                    select(MitreMapping).where(
                        MitreMapping.technique_id == tid,
                        MitreMapping.mapped_type == mapped_type,
                        MitreMapping.mapped_id == mapped_id,
                    )
                )
                if existing.scalar_one_or_none():
                    continue
                mapping = MitreMapping(
                    technique_id=tid,
                    mapped_type=mapped_type,
                    mapped_id=mapped_id,
                    mapped_name=mapped_name,
                    confidence=confidence or 0.7,
                    source="auto",
                    context=context,
                    mapped_at=now,
                )
                session.add(mapping)
                mappings.append(mapping)
            await session.flush()
            for mapping in mappings:
                await session.refresh(mapping)
            return mappings

    def _detect_from_context(self, context: str) -> list[str]:
        context_lower = context.lower()
        found: set[str] = set()

        keyword_map = {
            "ssh": ["T1021.004", "T1133"],
            "brute force": ["T1110", "T1078"],
            "password": ["T1110", "T1552"],
            "port scan": ["T1046"],
            "firewall": ["T1562", "T1499.002"],
            "web": ["T1190", "T1071.001"],
            "sql injection": ["T1190"],
            "cve": ["T1190", "T1068"],
            "malware": ["T1204.002", "T1105"],
            "ransomware": ["T1486", "T1485"],
            "phishing": ["T1566"],
            "powershell": ["T1059.001"],
            "registry": ["T1547.001"],
            "credential": ["T1110", "T1552", "T1078"],
            "privilege": ["T1068", "T1548"],
            "lateral": ["T1021"],
            "exfiltrat": ["T1048", "T1041"],
            "cmd.exe": ["T1059.003"],
            "bash": ["T1059.004"],
            "python": ["T1059.006"],
        }
        for keyword, techniques in keyword_map.items():
            if keyword in context_lower:
                found.update(techniques)

        return list(found)

    async def auto_map_ioc(self, ioc_type: str, ioc_value: str, source: str | None = None) -> list[MitreMapping]:
        return await self.map_entity(
            mapped_type="ioc", mapped_id=ioc_type,
            mapped_name=ioc_value, context=source,
        )

    async def auto_map_detection(self, rule_id: str, rule_name: str | None = None) -> list[MitreMapping]:
        return await self.map_entity(
            mapped_type="detection_rule", mapped_id=rule_id,
            mapped_name=rule_name,
        )

    async def auto_map_correlation(self, group_type: str, group_id: str) -> list[MitreMapping]:
        return await self.map_entity(
            mapped_type="correlation_group", mapped_id=group_type,
            mapped_name=group_id,
        )
