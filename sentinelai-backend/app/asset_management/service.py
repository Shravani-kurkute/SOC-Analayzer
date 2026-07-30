from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.asset_management import discovery, inventory, relationship, risk


class AssetManagementService:
    async def list_assets(
        self, db: AsyncSession, page: int = 1, page_size: int = 20,
        sort_by: str = "created_at", sort_order: str = "desc",
        search: str | None = None, asset_type: str | None = None,
        criticality: str | None = None, status: str | None = None,
        department: str | None = None, owner: str | None = None,
        os: str | None = None, risk_level: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        items, total = await inventory.list_assets(
            db, page=page, page_size=page_size, sort_by=sort_by,
            sort_order=sort_order, search=search, asset_type=asset_type,
            criticality=criticality, status=status, department=department,
            owner=owner, os=os, risk_level=risk_level, tag=tag,
        )
        total_pages = max(1, (total + page_size - 1) // page_size)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    async def get_asset(self, db: AsyncSession, asset_id: str) -> dict[str, Any]:
        asset = await inventory.get_asset(db, asset_id)
        if not asset:
            return None

        risk_details = await db.execute(
            risk.AssetRisk.__table__.select().where(risk.AssetRisk.asset_id == asset_id)
        )
        risk_record = risk_details.scalar_one_or_none()

        incidents = await relationship.get_related_incidents(db, asset_id)
        alerts = await relationship.get_related_alerts(db, asset_id)
        iocs = await relationship.get_related_iocs(db, asset_id)
        threat_intel = await relationship.get_related_threat_intel(db, asset_id)
        ai_reports = await relationship.get_related_ai_reports(db, asset_id)
        relationships = await relationship.get_asset_relationships(db, asset_id)

        history_result = await db.execute(
            risk.AssetHistory.__table__.select().where(risk.AssetHistory.asset_id == asset_id)
        )
        history = [dict(r._mapping) for r in history_result.all()]

        return {
            **asset.to_dict(),
            "risk_details": dict(risk_record._mapping) if risk_record else None,
            "incident_count": len(incidents),
            "alert_count": len(alerts),
            "ioc_count": len(iocs),
            "threat_intel_count": len(threat_intel),
            "ai_report_count": len(ai_reports),
            "relationships": relationships,
            "history": history,
        }

    async def create_asset(self, db: AsyncSession, data: Any, created_by: str | None = None) -> Any:
        from app.schemas.asset import AssetCreate
        if isinstance(data, dict):
            data = AssetCreate(**data)
        asset = await inventory.create_asset(db, data, created_by)
        await risk.calculate_asset_risk(db, asset)
        return asset

    async def update_asset(self, db: AsyncSession, asset_id: str, data: Any, changed_by: str | None = None) -> Any:
        from app.schemas.asset import AssetUpdate
        if isinstance(data, dict):
            data = AssetUpdate(**data)
        asset = await inventory.update_asset(db, asset_id, data, changed_by)
        if asset:
            await risk.calculate_asset_risk(db, asset)
        return asset

    async def delete_asset(self, db: AsyncSession, asset_id: str) -> bool:
        return await inventory.delete_asset(db, asset_id)

    async def get_stats(self, db: AsyncSession) -> dict[str, Any]:
        return await relationship.get_asset_stats(db)

    async def import_csv(self, db: AsyncSession, content: str, created_by: str | None = None) -> Any:
        return await discovery.import_csv(db, content, created_by)

    async def import_json(self, db: AsyncSession, content: str, created_by: str | None = None) -> Any:
        return await discovery.import_json(db, content, created_by)

    async def import_api(self, db: AsyncSession, assets: list[dict], created_by: str | None = None) -> Any:
        return await discovery.import_api_results(db, assets, created_by)

    async def create_relationship(self, db: AsyncSession, source_id: str, target_id: str, rel_type: str, md: dict | None = None) -> Any:
        return await relationship.create_relationship(db, source_id, target_id, rel_type, md)

    async def get_related_incidents(self, db: AsyncSession, asset_id: str) -> list[Any]:
        return await relationship.get_related_incidents(db, asset_id)

    async def get_related_alerts(self, db: AsyncSession, asset_id: str) -> list[Any]:
        return await relationship.get_related_alerts(db, asset_id)

    async def get_related_iocs(self, db: AsyncSession, asset_id: str) -> list[Any]:
        return await relationship.get_related_iocs(db, asset_id)

    async def get_related_threat_intel(self, db: AsyncSession, asset_id: str) -> list[Any]:
        return await relationship.get_related_threat_intel(db, asset_id)

    async def get_related_ai_reports(self, db: AsyncSession, asset_id: str) -> list[Any]:
        return await relationship.get_related_ai_reports(db, asset_id)
