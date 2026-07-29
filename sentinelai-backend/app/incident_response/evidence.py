import hashlib
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.incident_evidence import IncidentEvidence

ALLOWED_TYPES = {"pdf", "screenshot", "pcap", "txt", "log", "zip", "image", "other"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE


async def upload_evidence(
    db: AsyncSession,
    incident_id: str,
    filename: str,
    file_data: bytes,
    uploaded_by: str,
    description: str | None = None,
) -> IncidentEvidence:
    file_ext = Path(filename).suffix.lower().lstrip(".") or "bin"
    file_type = _classify_type(file_ext, filename)

    sha256 = hashlib.sha256(file_data).hexdigest()
    stored_dir = Path(settings.UPLOAD_DIR) / "evidence" / incident_id
    stored_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{sha256[:16]}_{filename}"
    stored_path = stored_dir / stored_filename
    stored_path.write_bytes(file_data)

    evidence = IncidentEvidence(
        incident_id=incident_id,
        filename=filename,
        file_type=file_type,
        file_size=len(file_data),
        stored_path=str(stored_path.relative_to(settings.UPLOAD_DIR)),
        sha256=sha256,
        uploaded_by=uploaded_by,
        description=description,
    )
    db.add(evidence)
    await db.flush()
    await db.refresh(evidence)
    return evidence


async def get_evidence_list(db: AsyncSession, incident_id: str) -> list[IncidentEvidence]:
    result = await db.execute(
        select(IncidentEvidence)
        .where(IncidentEvidence.incident_id == incident_id)
        .order_by(IncidentEvidence.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_evidence(db: AsyncSession, evidence_id: str) -> bool:
    result = await db.execute(select(IncidentEvidence).where(IncidentEvidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        return False
    file_path = Path(settings.UPLOAD_DIR) / evidence.stored_path
    if file_path.exists():
        file_path.unlink()
    await db.delete(evidence)
    return True


def _classify_type(ext: str, filename: str) -> str:
    img_exts = {"png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"}
    if ext in {"pdf"}:
        return "pdf"
    if ext in {"pcap", "pcapng", "cap"}:
        return "pcap"
    if ext in {"txt", "text"}:
        return "txt"
    if ext in {"log"}:
        return "log"
    if ext in {"zip", "gz", "tar", "rar", "7z"}:
        return "zip"
    if ext in img_exts:
        return "image"
    return "other"
