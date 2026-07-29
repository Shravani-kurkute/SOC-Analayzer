import json
import os
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_report import GeneratedReport
from app.reports.builder import (
    build_executive_report,
    build_threat_report,
    build_incident_report,
    build_asset_report,
    build_compliance_report,
)
from app.reports.csv import build_csv
from app.reports.excel import build_excel
from app.reports.pdf import build_pdf
from app.reports.charts import generate_report_charts


REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "report_exports")


async def generate_report(
    db: AsyncSession,
    report_type: str,
    title: str,
    format: str,
    filters: dict | None = None,
    user_id: str | None = None,
) -> dict:
    builders = {
        "executive": build_executive_report,
        "threat": build_threat_report,
        "incident": build_incident_report,
        "asset": build_asset_report,
        "compliance": build_compliance_report,
    }

    builder = builders.get(report_type)
    if not builder:
        raise ValueError(f"Unknown report type: {report_type}")

    if report_type == "incident":
        incident_id = (filters or {}).get("incident_id")
        if not incident_id:
            raise ValueError("incident_id required for incident report")
        report_data = await builder(db, incident_id)
    else:
        report_data = await builder(db, filters)

    charts = generate_report_charts(report_data, report_type)
    report_data["_charts"] = {k: v.hex() for k, v in charts.items()}

    os.makedirs(REPORT_DIR, exist_ok=True)
    filename = f"{report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    if format == "json":
        filepath = os.path.join(REPORT_DIR, f"{filename}.json")
        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2, default=str)
        file_size = os.path.getsize(filepath)
        content = report_data
    elif format == "csv":
        csv_bytes = build_csv(report_data, report_type)
        filepath = os.path.join(REPORT_DIR, f"{filename}.csv")
        with open(filepath, "wb") as f:
            f.write(csv_bytes)
        file_size = os.path.getsize(filepath)
        content = {"message": "CSV exported", "file_path": filepath}
    elif format == "xlsx":
        xlsx_bytes = build_excel(report_data, report_type)
        filepath = os.path.join(REPORT_DIR, f"{filename}.xlsx")
        with open(filepath, "wb") as f:
            f.write(xlsx_bytes)
        file_size = os.path.getsize(filepath)
        content = {"message": "Excel exported", "file_path": filepath}
    elif format == "pdf":
        pdf_bytes = build_pdf(report_data, report_type)
        filepath = os.path.join(REPORT_DIR, f"{filename}.pdf")
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        file_size = os.path.getsize(filepath)
        content = {"message": "PDF exported", "file_path": filepath}
    else:
        raise ValueError(f"Unsupported format: {format}")

    report = GeneratedReport(
        report_type=report_type,
        title=title,
        format=format,
        status="completed",
        file_path=filepath,
        file_size=file_size,
        filters=filters,
        data=report_data if format == "json" else None,
        generated_by_id=user_id,
        created_by=user_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return {
        "id": report.id,
        "report_type": report.report_type,
        "title": report.title,
        "format": report.format,
        "status": report.status,
        "file_path": report.file_path,
        "file_size": report.file_size,
        "data": report.data if format == "json" else None,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


async def get_report_history(db: AsyncSession, limit: int = 50, offset: int = 0) -> tuple[list, int]:
    total = await db.scalar(select(func.count(GeneratedReport.id)))
    reports = (await db.execute(
        select(GeneratedReport)
        .order_by(GeneratedReport.created_at.desc())
        .offset(offset)
        .limit(limit)
    )).scalars().all()
    return list(reports), total or 0


async def get_report(db: AsyncSession, report_id: str) -> GeneratedReport | None:
    return (await db.execute(
        select(GeneratedReport).where(GeneratedReport.id == report_id)
    )).scalar_one_or_none()


async def delete_report(db: AsyncSession, report_id: str) -> bool:
    report = await get_report(db, report_id)
    if not report:
        return False
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)
    await db.delete(report)
    await db.commit()
    return True


async def increment_download_count(db: AsyncSession, report_id: str) -> None:
    report = await get_report(db, report_id)
    if report:
        report.download_count = (report.download_count or 0) + 1
        await db.commit()


async def get_report_stats(db: AsyncSession) -> dict:
    total = await db.scalar(select(func.count(GeneratedReport.id))) or 0
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await db.scalar(
        select(func.count(GeneratedReport.id)).where(GeneratedReport.created_at >= today_start)
    ) or 0

    most_downloaded = (await db.execute(
        select(GeneratedReport)
        .order_by(GeneratedReport.download_count.desc())
        .limit(5)
    )).scalars().all()

    recent = (await db.execute(
        select(GeneratedReport)
        .order_by(GeneratedReport.created_at.desc())
        .limit(5)
    )).scalars().all()

    return {
        "total_reports": total,
        "reports_today": today_count,
        "most_downloaded": [
            {"id": r.id, "title": r.title, "report_type": r.report_type, "format": r.format,
             "download_count": r.download_count, "created_at": r.created_at.isoformat()}
            for r in most_downloaded
        ],
        "recent_reports": [
            {"id": r.id, "title": r.title, "report_type": r.report_type, "format": r.format,
             "download_count": r.download_count, "created_at": r.created_at.isoformat()}
            for r in recent
        ],
    }
