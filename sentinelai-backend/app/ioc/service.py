from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, or_, select, text

from app.database.session import async_session_factory
from app.models.ioc_entry import IocEntry


class IocService:
    def __init__(self):
        self.extractor = None

    def _get_extractor(self):
        if self.extractor is None:
            from app.ioc.extractors import IocExtractor
            self.extractor = IocExtractor()
        return self.extractor

    async def extract_from_event(self, event: dict[str, Any]) -> list[IocEntry]:
        text = self._event_to_text(event)
        raw_iocs = self._get_extractor().extract_all(text, event)
        entries: list[IocEntry] = []
        for raw in raw_iocs:
            entry = await self._upsert_ioc(raw, event)
            if entry:
                entries.append(entry)
        return entries

    async def extract_all(self, events: list[dict[str, Any]]) -> list[IocEntry]:
        all_entries: list[IocEntry] = []
        seen: set[str] = set()
        for event in events:
            if "text" in event:
                entries = await self.extract_from_text(event["text"], event.get("source"))
            else:
                entries = await self.extract_from_event(event)
            for entry in entries:
                key = f"{entry.ioc_type}:{entry.normalized_value}"
                if key not in seen:
                    seen.add(key)
                    all_entries.append(entry)
        return all_entries

    async def extract_from_text(self, text: str, source: str | None = None) -> list[IocEntry]:
        raw_iocs = self._get_extractor().extract_all(text)
        entries: list[IocEntry] = []
        for raw in raw_iocs:
            event_info = {"source_log": source} if source else None
            entry = await self._upsert_ioc(raw, event_info)
            if entry:
                entries.append(entry)
        return entries

    async def _upsert_ioc(self, raw: dict[str, Any], event: dict[str, Any] | None = None) -> IocEntry | None:
        ioc_type = raw["ioc_type"]
        normalized_value = raw["normalized_value"]
        now = datetime.now(timezone.utc)

        async with async_session_factory() as session:
            result = await session.execute(
                select(IocEntry).where(
                    IocEntry.ioc_type == ioc_type,
                    IocEntry.normalized_value == normalized_value,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.occurrences += 1
                existing.last_seen = now
                existing.confidence = min(1.0, existing.confidence + 0.05)
                if event:
                    existing.extra_data = {**(existing.extra_data or {}), **event}
                    if event.get("source_ip"):
                        existing.source_ip = event["source_ip"]
                await session.flush()
                await session.refresh(existing)
                return existing
            else:
                entry = IocEntry(
                    ioc_type=ioc_type,
                    ioc_value=raw["ioc_value"],
                    normalized_value=normalized_value,
                    confidence=self._confidence_for_type(ioc_type),
                    source_event=event.get("id") if event else None,
                    source_log=event.get("source_log") if event else None,
                    source_ip=event.get("source_ip") if event else None,
                    first_seen=now,
                    last_seen=now,
                    occurrences=1,
                    severity=self._severity_for_type(ioc_type),
                    status="active",
                    extra_data=event or {},
                )
                session.add(entry)
                await session.flush()
                await session.refresh(entry)
                return entry

    async def list_iocs(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "last_seen",
        sort_order: str = "desc",
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[IocEntry], int]:
        async with async_session_factory() as session:
            query = select(IocEntry)

            if filters:
                if filters.get("ioc_type"):
                    query = query.where(IocEntry.ioc_type == filters["ioc_type"])
                if filters.get("severity"):
                    query = query.where(IocEntry.severity == filters["severity"])
                if filters.get("status"):
                    query = query.where(IocEntry.status == filters["status"])
                if filters.get("source_ip"):
                    query = query.where(IocEntry.source_ip == filters["source_ip"])
                if filters.get("source_log"):
                    query = query.where(IocEntry.source_log == filters["source_log"])
                if filters.get("q"):
                    search = f"%{filters['q']}%"
                    query = query.where(
                        or_(
                            IocEntry.ioc_value.ilike(search),
                            IocEntry.normalized_value.ilike(search),
                            IocEntry.context.ilike(search),
                        )
                    )
                if filters.get("date_from"):
                    query = query.where(IocEntry.first_seen >= filters["date_from"])
                if filters.get("date_to"):
                    query = query.where(IocEntry.last_seen <= filters["date_to"])

            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            sort_column = getattr(IocEntry, sort_by, IocEntry.last_seen)
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            items = result.scalars().all()
            return list(items), total

    async def get_ioc(self, ioc_id: str) -> IocEntry | None:
        async with async_session_factory() as session:
            result = await session.execute(select(IocEntry).where(IocEntry.id == ioc_id))
            return result.scalar_one_or_none()

    async def get_stats(self) -> dict[str, Any]:
        async with async_session_factory() as session:
            total_q = select(func.count()).select_from(IocEntry)
            total_r = await session.execute(total_q)
            total = total_r.scalar() or 0

            type_q = select(IocEntry.ioc_type, func.count().label("cnt")).group_by(IocEntry.ioc_type).order_by(text("cnt desc"))
            type_r = await session.execute(type_q)
            by_type = {row[0]: row[1] for row in type_r}

            sev_q = select(IocEntry.severity, func.count().label("cnt")).group_by(IocEntry.severity).order_by(text("cnt desc"))
            sev_r = await session.execute(sev_q)
            by_severity = {row[0]: row[1] for row in sev_r}

            status_q = select(IocEntry.status, func.count().label("cnt")).group_by(IocEntry.status).order_by(text("cnt desc"))
            status_r = await session.execute(status_q)
            by_status = {row[0]: row[1] for row in status_r}

            top_ip_q = (
                select(IocEntry.source_ip, func.count().label("cnt"))
                .where(IocEntry.source_ip.isnot(None))
                .group_by(IocEntry.source_ip)
                .order_by(text("cnt desc"))
                .limit(10)
            )
            top_ip_r = await session.execute(top_ip_q)
            top_source_ips = [{"source_ip": row[0], "count": row[1]} for row in top_ip_r]

            latest_q = select(IocEntry).order_by(IocEntry.last_seen.desc()).limit(10)
            latest_r = await session.execute(latest_q)
            latest_iocs = [
                {"id": i.id, "ioc_type": i.ioc_type, "ioc_value": i.ioc_value, "severity": i.severity, "last_seen": i.last_seen.isoformat()}
                for i in latest_r.scalars().all()
            ]

            domain_q = select(func.count()).select_from(IocEntry).where(IocEntry.ioc_type == "domain")
            domain_r = await session.execute(domain_q)
            unique_domains = domain_r.scalar() or 0

            ip_q = select(func.count()).select_from(IocEntry).where(IocEntry.ioc_type.in_(["ipv4", "ipv6"]))
            ip_r = await session.execute(ip_q)
            unique_ips = ip_r.scalar() or 0

            hash_q = select(func.count()).select_from(IocEntry).where(IocEntry.ioc_type.in_(["md5", "sha1", "sha256"]))
            hash_r = await session.execute(hash_q)
            unique_hashes = hash_r.scalar() or 0

            return {
                "total": total,
                "by_type": by_type,
                "by_severity": by_severity,
                "by_status": by_status,
                "top_source_ips": top_source_ips,
                "latest_iocs": latest_iocs,
                "unique_domains": unique_domains,
                "unique_ips": unique_ips,
                "unique_hashes": unique_hashes,
            }

    async def search_iocs(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[IocEntry], int]:
        return await self.list_iocs(page=page, page_size=page_size, filters={"q": query})

    def _event_to_text(self, event: dict[str, Any]) -> str:
        fields = [
            event.get("raw_message", ""),
            event.get("message", ""),
            event.get("log_content", ""),
            event.get("source_ip", ""),
            event.get("destination_ip", ""),
            event.get("hostname", ""),
            event.get("username", ""),
            event.get("command", ""),
            event.get("process", ""),
            event.get("file_path", ""),
            event.get("url", ""),
            event.get("user_agent", ""),
            str(event.get("metadata", {})),
        ]
        return "\n".join(f for f in fields if f)

    def _confidence_for_type(self, ioc_type: str) -> float:
        high = {"ipv4", "ipv6", "md5", "sha1", "sha256", "cve"}
        medium = {"domain", "url", "hostname", "email", "registry_key", "windows_sid"}
        return 0.9 if ioc_type in high else 0.7 if ioc_type in medium else 0.5

    def _severity_for_type(self, ioc_type: str) -> str:
        critical = {"cve", "sha256", "command_line"}
        high = {"ipv4", "domain", "url", "md5", "sha1", "registry_key"}
        return "critical" if ioc_type in critical else "high" if ioc_type in high else "medium"
