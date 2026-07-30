import csv
import io
import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.asset_management.inventory import create_asset
from app.schemas.asset import AssetCreate, AssetImportResult


def _parse_row_to_asset(row: dict[str, str]) -> AssetCreate:
    return AssetCreate(
        hostname=row.get("hostname", row.get("Hostname", row.get("name", ""))),
        ip_address=row.get("ip_address", row.get("IP", row.get("ip", ""))),
        mac_address=row.get("mac_address", row.get("MAC", row.get("mac", ""))),
        os=row.get("os", row.get("OS", "")),
        os_version=row.get("os_version", row.get("OS Version", row.get("os_version", ""))),
        asset_type=row.get("asset_type", row.get("Type", row.get("type", "server"))),
        criticality=row.get("criticality", row.get("Criticality", "medium")),
        status=row.get("status", row.get("Status", "unknown")),
        environment=row.get("environment", row.get("Environment", "")),
        location=row.get("location", row.get("Location", "")),
        department=row.get("department", row.get("Department", "")),
        owner=row.get("owner", row.get("Owner", "")),
        vendor=row.get("vendor", row.get("Vendor", "")),
        serial_number=row.get("serial_number", row.get("Serial", row.get("Serial Number", ""))),
        notes=row.get("notes", row.get("Notes", "")),
        tags=[t.strip() for t in row.get("tags", row.get("Tags", "")).split(",") if t.strip()] if row.get("tags") else None,
    )


async def import_csv(db: AsyncSession, content: str, created_by: str | None = None) -> AssetImportResult:
    result = AssetImportResult()
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        try:
            data = _parse_row_to_asset(row)
            await create_asset(db, data, created_by)
            result.imported += 1
        except Exception as e:
            result.failed += 1
            result.errors.append(str(e))
    return result


async def import_json(db: AsyncSession, content: str, created_by: str | None = None) -> AssetImportResult:
    result = AssetImportResult()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        result.failed += 1
        result.errors.append(f"Invalid JSON: {e}")
        return result

    items = data if isinstance(data, list) else [data]
    for item in items:
        try:
            if isinstance(item, dict):
                flat = {k.lower().replace(" ", "_"): v for k, v in item.items()}
                flat_str = {k: str(v) if not isinstance(v, str) else v for k, v in flat.items()}
                data = _parse_row_to_asset(flat_str)
                await create_asset(db, data, created_by)
                result.imported += 1
            else:
                result.failed += 1
                result.errors.append("Invalid item format")
        except Exception as e:
            result.failed += 1
            result.errors.append(str(e))
    return result


async def import_api_results(db: AsyncSession, assets: list[dict[str, Any]], created_by: str | None = None) -> AssetImportResult:
    result = AssetImportResult()
    for item in assets:
        try:
            flat = {k.lower().replace(" ", "_"): v for k, v in item.items()}
            flat_str = {k: str(v) if not isinstance(v, str) else v for k, v in flat.items()}
            data = _parse_row_to_asset(flat_str)
            await create_asset(db, data, created_by)
            result.imported += 1
        except Exception as e:
            result.failed += 1
            result.errors.append(str(e))
    return result
