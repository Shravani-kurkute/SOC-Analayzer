from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import joinedload

from app.database.session import async_session_factory
from app.mitre.coverage_calculator import CoverageCalculator
from app.mitre.data import MITRE_TECHNIQUES
from app.mitre.mapping_engine import MappingEngine
from app.models.mitre_technique import CoverageStatistic, MitreMapping, MitreTechnique


class MitreService:
    def __init__(self):
        self._engine = None
        self._calculator = None

    def _get_engine(self) -> MappingEngine:
        if self._engine is None:
            self._engine = MappingEngine()
        return self._engine

    def _get_calculator(self) -> CoverageCalculator:
        if self._calculator is None:
            self._calculator = CoverageCalculator()
        return self._calculator

    async def seed_techniques(self) -> int:
        async with async_session_factory() as session:
            count = 0
            for data in MITRE_TECHNIQUES:
                existing = await session.execute(
                    select(MitreTechnique).where(MitreTechnique.technique_id == data["technique_id"])
                )
                if not existing.scalar_one_or_none():
                    technique = MitreTechnique(
                        technique_id=data["technique_id"],
                        name=data["name"],
                        tactic=data["tactic"],
                        tactic_id=data.get("tactic_id"),
                        severity=data.get("severity", "medium"),
                        score=data.get("score", 1.0),
                        kill_chain_phase=data.get("kill_chain_phase"),
                        is_subtechnique=data.get("is_subtechnique", False),
                        parent_technique_id=data.get("parent_technique_id"),
                        detection_rules=data.get("detection_rules"),
                        ioc_indicators=data.get("ioc_indicators"),
                    )
                    session.add(technique)
                    count += 1
            await session.flush()
            return count

    async def list_techniques(
        self, tactic: str | None = None, search: str | None = None,
        page: int = 1, page_size: int = 50,
    ) -> tuple[list[MitreTechnique], int]:
        async with async_session_factory() as session:
            query = select(MitreTechnique)
            if tactic:
                query = query.where(MitreTechnique.tactic == tactic)
            if search:
                q = f"%{search}%"
                query = query.where(
                    or_(
                        MitreTechnique.name.ilike(q),
                        MitreTechnique.technique_id.ilike(q),
                        MitreTechnique.description.ilike(q),
                    )
                )
            count_q = select(func.count()).select_from(query.subquery())
            total = (await session.execute(count_q)).scalar() or 0

            query = query.order_by(MitreTechnique.tactic, MitreTechnique.technique_id)
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await session.execute(query)
            return list(result.scalars().all()), total

    async def get_technique(self, technique_id: str) -> MitreTechnique | None:
        async with async_session_factory() as session:
            result = await session.execute(
                select(MitreTechnique).where(MitreTechnique.technique_id == technique_id)
            )
            return result.scalar_one_or_none()

    async def get_technique_detail(self, technique_id: str) -> dict[str, Any] | None:
        async with async_session_factory() as session:
            tech = await session.execute(
                select(MitreTechnique).where(MitreTechnique.technique_id == technique_id)
            )
            tech = tech.scalar_one_or_none()
            if not tech:
                return None

            mappings_q = select(MitreMapping).where(MitreMapping.technique_id == technique_id)
            mappings = (await session.execute(mappings_q)).scalars().all()

            if tech.parent_technique_id:
                related_q = select(MitreTechnique).where(
                    or_(
                        MitreTechnique.parent_technique_id == tech.parent_technique_id,
                        MitreTechnique.technique_id == tech.parent_technique_id,
                    )
                )
            else:
                related_q = select(MitreTechnique).where(
                    MitreTechnique.parent_technique_id == technique_id
                )
            related = (await session.execute(related_q)).scalars().all()

            return {
                "technique": tech,
                "mappings": list(mappings),
                "mapped_count": len(mappings),
                "detection_coverage": min(1.0, len(mappings) / 5.0) if mappings else 0.0,
                "related_techniques": [r for r in related if r.technique_id != technique_id],
            }

    async def list_tactics(self) -> list[dict[str, Any]]:
        async with async_session_factory() as session:
            q = select(
                MitreTechnique.tactic,
                MitreTechnique.tactic_id,
                func.count().label("technique_count"),
            ).group_by(MitreTechnique.tactic, MitreTechnique.tactic_id).order_by(MitreTechnique.tactic)
            result = await session.execute(q)
            return [{"tactic": r[0], "tactic_id": r[1], "technique_count": r[2]} for r in result]

    async def map_entity(
        self, mapped_type: str, mapped_id: str, mapped_name: str | None = None,
        context: str | None = None, confidence: float | None = None,
    ) -> list[MitreMapping]:
        engine = self._get_engine()
        return await engine.map_entity(
            mapped_type=mapped_type, mapped_id=mapped_id,
            mapped_name=mapped_name, context=context, confidence=confidence,
        )

    async def get_coverage(self) -> dict[str, Any]:
        calculator = self._get_calculator()
        return await calculator.get_coverage()

    async def search_techniques(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[MitreTechnique], int]:
        return await self.list_techniques(search=query, page=page, page_size=page_size)

    async def get_mappings_for_entity(
        self, mapped_type: str, mapped_id: str,
    ) -> list[MitreMapping]:
        async with async_session_factory() as session:
            result = await session.execute(
                select(MitreMapping).where(
                    MitreMapping.mapped_type == mapped_type,
                    MitreMapping.mapped_id == mapped_id,
                )
            )
            return list(result.scalars().all())
