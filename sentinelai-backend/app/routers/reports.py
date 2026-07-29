import json
import os
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.reports.service import (
    generate_report,
    get_report_history,
    get_report,
    delete_report,
    increment_download_count,
    get_report_stats,
)
from app.schemas.reports import (
    ReportRequest,
    ReportListItem,
    ReportListResponse,
    ReportResponse,
    ReportStats,
    ExecutiveSOCReport,
    ThreatReportData,
    IncidentReportData,
    AssetReportData,
    ComplianceReportData,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/generate")
async def api_generate_report(
    req: ReportRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    filters = {
        "date_range_start": req.date_range_start,
        "date_range_end": req.date_range_end,
        "severity": req.severity,
        "status": req.status,
        "mitre_technique": req.mitre_technique,
        "incident_id": req.incident_id,
        "analyst_id": req.analyst_id,
    }
    filters = {k: v for k, v in filters.items() if v is not None}

    result = await generate_report(
        db=db,
        report_type=req.report_type,
        title=req.title,
        format=req.format,
        filters=filters,
        user_id=current_user.id,
    )
    return result


@router.get("")
async def api_list_reports(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    reports, total = await get_report_history(db, limit=limit, offset=offset)
    return ReportListResponse(
        items=[ReportListItem(
            id=r.id, report_type=r.report_type, title=r.title,
            format=r.format, status=r.status, file_size=r.file_size,
            download_count=r.download_count, generated_by_id=r.generated_by_id,
            created_at=r.created_at, created_by=r.created_by,
        ) for r in reports],
        total=total,
    )


@router.get("/stats")
async def api_report_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stats = await get_report_stats(db)
    return stats


@router.get("/{report_id}")
async def api_get_report(
    report_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    report = await get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse(
        id=report.id, report_type=report.report_type, title=report.title,
        format=report.format, status=report.status, file_path=report.file_path,
        file_size=report.file_size, date_range_start=report.date_range_start,
        date_range_end=report.date_range_end, filters=report.filters,
        data=report.data, download_count=report.download_count,
        generated_by_id=report.generated_by_id, created_at=report.created_at,
        created_by=report.created_by,
    )


@router.delete("/{report_id}")
async def api_delete_report(
    report_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    success = await delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"detail": "Report deleted"}


@router.get("/download/{report_id}")
async def api_download_report(
    report_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    report = await get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    await increment_download_count(db, report_id)

    media_types = {
        "pdf": "application/pdf",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "json": "application/json",
    }
    media_type = media_types.get(report.format, "application/octet-stream")
    filename = os.path.basename(report.file_path)

    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=filename,
    )
