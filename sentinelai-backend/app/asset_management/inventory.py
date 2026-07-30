from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import Asset, AssetHistory, AssetOwner, AssetRelationship, AssetRisk, AssetTag
from app.schemas.asset import AssetCreate, AssetUpdate


async def list_assets(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    search: str | None = None,
    asset_type: str | None = None,
    criticality: str | None = None,
    status: str | None = None,
    department: str | None = None,
    owner: str | None = None,
    os: str | None = None,
    risk_level: str | None = None,
    tag: str | None = None,
) -> tuple[Sequence[Asset], int]:
    query = select(Asset)

    if search:
        search_filter = or_(
            Asset.hostname.ilike(f"%{search}%"),
            Asset.ip_address.ilike(f"%{search}%"),
            Asset.mac_address.ilike(f"%{search}%"),
            Asset.os.ilike(f"%{search}%"),
            Asset.location.ilike(f"%{search}%"),
            Asset.department.ilike(f"%{search}%"),
            Asset.owner.ilike(f"%{search}%"),
            Asset.vendor.ilike(f"%{search}%"),
            Asset.serial_number.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    if criticality:
        query = query.where(Asset.criticality == criticality)
    if status:
        query = query.where(Asset.status == status)
    if department:
        query = query.where(Asset.department == department)
    if owner:
        query = query.where(Asset.owner.ilike(f"%{owner}%"))
    if os:
        query = query.where(Asset.os.ilike(f"%{os}%"))
    if tag:
        query = query.where(Asset.tags.contains([tag]))

    if risk_level:
        if risk_level == "critical":
            query = query.where(Asset.risk_score >= 70)
        elif risk_level == "high":
            query = query.where(Asset.risk_score.between(50, 69.99))
        elif risk_level == "medium":
            query = query.where(Asset.risk_score.between(30, 49.99))
        elif risk_level == "low":
            query = query.where(Asset.risk_score < 30)

    sort_column = getattr(Asset, sort_by, Asset.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total


async def get_asset(db: AsyncSession, asset_id: str) -> Asset | None:
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    return result.scalar_one_or_none()


async def create_asset(db: AsyncSession, data: AssetCreate, created_by: str | None = None) -> Asset:
    asset = Asset(
        hostname=data.hostname,
        ip_address=data.ip_address,
        mac_address=data.mac_address,
        os=data.os,
        os_version=data.os_version,
        asset_type=data.asset_type,
        criticality=data.criticality,
        environment=data.environment,
        status=data.status,
        tags=data.tags,
        location=data.location,
        department=data.department,
        owner=data.owner,
        vendor=data.vendor,
        serial_number=data.serial_number,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(asset)
    await db.flush()
    return asset


async def update_asset(db: AsyncSession, asset_id: str, data: AssetUpdate, changed_by: str | None = None) -> Asset | None:
    asset = await get_asset(db, asset_id)
    if not asset:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_value = getattr(asset, field)
        if old_value != value:
            history = AssetHistory(
                asset_id=asset_id,
                field_name=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(value) if value is not None else None,
                changed_by=changed_by,
            )
            db.add(history)
        setattr(asset, field, value)

    return asset


async def delete_asset(db: AsyncSession, asset_id: str) -> bool:
    asset = await get_asset(db, asset_id)
    if not asset:
        return False
    asset.is_active = False
    return True
