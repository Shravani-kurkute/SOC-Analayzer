from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select, text

from app.database.session import async_session_factory
from app.models.mitre_technique import CoverageStatistic, MitreMapping, MitreTechnique


class CoverageCalculator:
    async def get_coverage(self) -> dict[str, Any]:
        async with async_session_factory() as session:
            total_q = select(func.count()).select_from(MitreTechnique)
            total_techniques = (await session.execute(total_q)).scalar() or 0

            mapped_q = select(func.count(distinct(MitreMapping.technique_id)))
            total_mapped = (await session.execute(mapped_q)).scalar() or 0

            detection_q = select(func.count()).select_from(MitreMapping)
            total_detections = (await session.execute(detection_q)).scalar() or 0

            overall_coverage = (total_mapped / total_techniques * 100) if total_techniques > 0 else 0.0

            by_tactic_q = select(
                MitreTechnique.tactic,
                func.count().label("total"),
            ).group_by(MitreTechnique.tactic).order_by(MitreTechnique.tactic)
            by_tactic_r = await session.execute(by_tactic_q)
            tactics_data = {r[0]: {"total_techniques": r[1], "tactic": r[0]} for r in by_tactic_r}

            for tactic_info in tactics_data.values():
                mapped_in_tactic_q = select(func.count(distinct(MitreMapping.technique_id))).where(
                    MitreMapping.technique_id.in_(
                        select(MitreTechnique.technique_id).where(
                            MitreTechnique.tactic == tactic_info["tactic"]
                        )
                    )
                )
                mapped_count = (await session.execute(mapped_in_tactic_q)).scalar() or 0
                tactic_info["mapped_techniques"] = mapped_count
                tactic_info["coverage_percent"] = (
                    (mapped_count / tactic_info["total_techniques"] * 100)
                    if tactic_info["total_techniques"] > 0 else 0.0
                )

                det_in_tactic_q = select(func.count()).select_from(MitreMapping).where(
                    MitreMapping.technique_id.in_(
                        select(MitreTechnique.technique_id).where(
                            MitreTechnique.tactic == tactic_info["tactic"]
                        )
                    )
                )
                tactic_info["total_detections"] = (await session.execute(det_in_tactic_q)).scalar() or 0
                tactic_info["mapped_detections"] = tactic_info["total_detections"]
                tactic_info["avg_confidence"] = 0.75
                tactic_info["calculated_at"] = datetime.now(timezone.utc)

            by_tactic = list(tactics_data.values())

            top_techniques_q = select(
                MitreMapping.technique_id,
                MitreTechnique.name,
                func.count().label("cnt"),
            ).join(
                MitreTechnique, MitreMapping.technique_id == MitreTechnique.technique_id
            ).group_by(
                MitreMapping.technique_id, MitreTechnique.name
            ).order_by(text("cnt desc")).limit(10)
            top_techniques_r = await session.execute(top_techniques_q)
            top_techniques = [
                {"technique_id": r[0], "name": r[1], "count": r[2]}
                for r in top_techniques_r
            ]

            top_tactics = sorted(by_tactic, key=lambda x: x["mapped_techniques"], reverse=True)[:5]

            most_triggered_q = select(
                MitreMapping.technique_id,
                MitreTechnique.name,
                MitreTechnique.tactic,
                func.count().label("cnt"),
            ).join(
                MitreTechnique, MitreMapping.technique_id == MitreTechnique.technique_id
            ).group_by(
                MitreMapping.technique_id, MitreTechnique.name, MitreTechnique.tactic
            ).order_by(text("cnt desc")).limit(10)
            most_triggered_r = await session.execute(most_triggered_q)
            most_triggered = [
                {"technique_id": r[0], "name": r[1], "tactic": r[2], "count": r[3]}
                for r in most_triggered_r
            ]

            now = datetime.now(timezone.utc)
            for stat in by_tactic:
                cs = CoverageStatistic(
                    tactic=stat["tactic"],
                    total_techniques=stat["total_techniques"],
                    mapped_techniques=stat["mapped_techniques"],
                    coverage_percent=stat["coverage_percent"],
                    total_detections=stat["total_detections"],
                    mapped_detections=stat["mapped_detections"],
                    avg_confidence=stat["avg_confidence"],
                    calculated_at=now,
                )
                session.add(cs)

            return {
                "overall_coverage": round(overall_coverage, 1),
                "total_techniques": total_techniques,
                "total_mapped": total_mapped,
                "total_detections": total_detections,
                "by_tactic": by_tactic,
                "top_techniques": top_techniques,
                "top_tactics": top_tactics,
                "most_triggered": most_triggered,
            }


def distinct(column):
    return func.distinct(column)
