import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.models.log_file import LogFile
from app.models.user import User
from app.schemas.log import LogFileListResponse, LogFileResponse, LogStatsResponse, LogUploadResponse

logger = structlog.get_logger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".log", ".txt", ".json"}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE
UPLOAD_DIR = settings.UPLOAD_DIR / "logs"


def ensure_upload_dir():
    path = Path(str(UPLOAD_DIR))
    path.mkdir(parents=True, exist_ok=True)
    return path


def detect_source_type(filename: str) -> str:
    name = filename.lower()
    if "auth" in name:
        return "linux-auth"
    if "syslog" in name or "secure" in name:
        return "linux-syslog"
    if "apache" in name or "access" in name:
        return "apache-access"
    if "nginx" in name:
        return "nginx"
    if "pfsense" in name or "firewall" in name:
        return "firewall"
    if "cisco" in name:
        return "cisco-asa"
    if "fortinet" in name:
        return "fortinet"
    if "evtx" in name:
        return "windows-evtx"
    if name.endswith(".json"):
        return "json-log"
    return "generic"


async def compute_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(str(file_path), "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.2f} GB"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.2f} MB"
    if size_bytes >= 1_024:
        return f"{size_bytes / 1_024:.2f} KB"
    return f"{size_bytes} B"


@router.post("/upload", response_model=LogUploadResponse, status_code=201)
async def upload_log(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    ext = Path(file.filename or "file").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({format_size(file_size)}). Maximum: {format_size(MAX_FILE_SIZE)}",
        )

    sha256 = hashlib.sha256(content).hexdigest()

    existing = await db.execute(
        select(LogFile).where(
            LogFile.checksum_sha256 == sha256,
            LogFile.is_deleted == False,
        )
    )
    dup = existing.scalar_one_or_none()
    if dup:
        raise ConflictError(
            f"Duplicate file detected (SHA-256: {sha256[:16]}...). "
            f"Originally uploaded as '{dup.original_filename}' on {dup.upload_time.strftime('%Y-%m-%d %H:%M:%S')}."
        )

    upload_dir = ensure_upload_dir()
    date_prefix = datetime.now(timezone.utc).strftime("%Y%m%d")
    dest_dir = upload_dir / date_prefix
    dest_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    stored_path = dest_dir / stored_name

    with open(str(stored_path), "wb") as f:
        f.write(content)

    source_type = detect_source_type(file.filename or "generic.log")

    log_file = LogFile(
        original_filename=file.filename or "untitled",
        stored_path=str(stored_path),
        source_type=source_type,
        source_name=source_type.replace("-", " ").title(),
        size=file_size,
        mime_type=file.content_type or "text/plain",
        checksum_sha256=sha256,
        status="uploaded",
        uploaded_by=current_user.email,
        upload_time=datetime.now(timezone.utc),
    )
    db.add(log_file)
    await db.flush()
    await db.commit()
    await db.refresh(log_file)

    logger.info(
        "log_uploaded",
        file_id=log_file.id,
        filename=file.filename,
        size=file_size,
        checksum=sha256[:16],
        source_type=source_type,
        uploaded_by=current_user.email,
    )

    return LogUploadResponse(
        id=log_file.id,
        original_filename=log_file.original_filename,
        size=file_size,
        checksum_sha256=sha256,
        status="uploaded",
        upload_time=log_file.upload_time,
        message=f"File '{file.filename}' uploaded successfully ({format_size(file_size)}, SHA-256: {sha256[:16]}...)",
    )


@router.get("", response_model=LogFileListResponse)
async def list_log_files(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_type: str | None = Query(None),
    status: str | None = Query(None),
):
    query = select(LogFile).where(LogFile.is_deleted == False)
    count_query = select(func.count(LogFile.id)).where(LogFile.is_deleted == False)

    if source_type:
        query = query.where(LogFile.source_type == source_type)
        count_query = count_query.where(LogFile.source_type == source_type)
    if status:
        query = query.where(LogFile.status == status)
        count_query = count_query.where(LogFile.status == status)

    total = (await db.execute(count_query)).scalar() or 0

    result = (
        await db.execute(
            query.order_by(LogFile.upload_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    return LogFileListResponse(
        items=[LogFileResponse(
            id=f.id,
            original_filename=f.original_filename,
            source_type=f.source_type,
            source_name=f.source_name,
            size=f.size,
            mime_type=f.mime_type,
            checksum_sha256=f.checksum_sha256,
            status=f.status,
            error_message=f.error_message,
            uploaded_by=f.uploaded_by,
            upload_time=f.upload_time,
            processing_started_at=f.processing_started_at,
            processing_completed_at=f.processing_completed_at,
            parsed_entries=f.parsed_entries,
            failed_entries=f.failed_entries,
            tags=f.tags,
        ) for f in result],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=LogStatsResponse)
async def get_log_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    base = select(LogFile).where(LogFile.is_deleted == False)

    total_files = (await db.execute(select(func.count(LogFile.id)).where(LogFile.is_deleted == False))).scalar() or 0
    total_size = (await db.execute(select(func.coalesce(func.sum(LogFile.size), 0)).where(LogFile.is_deleted == False))).scalar() or 0
    total_parsed = (await db.execute(select(func.coalesce(func.sum(LogFile.parsed_entries), 0)).where(LogFile.is_deleted == False))).scalar() or 0

    by_source = (await db.execute(
        select(LogFile.source_type, func.count(LogFile.id).label("c"))
        .where(LogFile.is_deleted == False)
        .group_by(LogFile.source_type)
    )).all()
    by_source_dict = {r.source_type: r.c for r in by_source}

    by_status = (await db.execute(
        select(LogFile.status, func.count(LogFile.id).label("c"))
        .where(LogFile.is_deleted == False)
        .group_by(LogFile.status)
    )).all()
    by_status_dict = {r.status: r.c for r in by_status}

    recent = (await db.execute(
        select(func.count(LogFile.id))
        .where(
            LogFile.is_deleted == False,
            LogFile.upload_time >= func.now() - text("INTERVAL '24 hours'"),
        )
    )).scalar() or 0

    return LogStatsResponse(
        total_files=total_files,
        total_size=total_size,
        total_parsed_entries=total_parsed,
        by_source_type=by_source_dict,
        by_status=by_status_dict,
        recent_uploads=recent,
        avg_file_size=round(total_size / total_files, 2) if total_files > 0 else 0,
        storage_used=format_size(total_size),
    )


@router.get("/{file_id}", response_model=LogFileResponse)
async def get_log_file(
    file_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(LogFile).where(LogFile.id == file_id, LogFile.is_deleted == False)
    )
    log_file = result.scalar_one_or_none()
    if not log_file:
        raise NotFoundError("Log file")

    return LogFileResponse(
        id=log_file.id,
        original_filename=log_file.original_filename,
        source_type=log_file.source_type,
        source_name=log_file.source_name,
        size=log_file.size,
        mime_type=log_file.mime_type,
        checksum_sha256=log_file.checksum_sha256,
        status=log_file.status,
        error_message=log_file.error_message,
        uploaded_by=log_file.uploaded_by,
        upload_time=log_file.upload_time,
        processing_started_at=log_file.processing_started_at,
        processing_completed_at=log_file.processing_completed_at,
        parsed_entries=log_file.parsed_entries,
        failed_entries=log_file.failed_entries,
        tags=log_file.tags,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_log_file(
    file_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(LogFile).where(LogFile.id == file_id, LogFile.is_deleted == False)
    )
    log_file = result.scalar_one_or_none()
    if not log_file:
        raise NotFoundError("Log file")

    log_file.is_deleted = True

    stored = Path(log_file.stored_path)
    if stored.exists():
        try:
            stored.unlink()
            logger.info("log_file_deleted_from_disk", path=str(stored))
        except OSError as e:
            logger.warning("failed_to_delete_file_from_disk", path=str(stored), error=str(e))

    await db.flush()
    await db.commit()

    logger.info("log_file_deleted", file_id=file_id, filename=log_file.original_filename, deleted_by=current_user.email)
