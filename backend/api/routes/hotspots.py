import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from models.file_change import FileChange
from schemas.analytics import HotspotsResponse, HotspotFile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["hotspots"])


@router.get("/{repo_id}/hotspots", response_model=HotspotsResponse)
async def get_hotspots(
    repo_id: int,
    risk: str = Query(default=None, pattern="^(high|medium|low)$"),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns files ranked by churn frequency and risk score.

    Optional ?risk=high|medium|low filter.
    Use limit to cap results (default 50).
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    query = (
        select(FileChange)
        .where(FileChange.repository_id == repo_id)
        .order_by(FileChange.risk_score.desc())
    )
    if risk:
        query = query.where(FileChange.risk_label == risk)
    query = query.limit(limit)

    result = await db.execute(query)
    files = result.scalars().all()

    # Count totals across all risk levels (ignore the filter for counts)
    all_result = await db.execute(
        select(FileChange.risk_label)
        .where(FileChange.repository_id == repo_id)
    )
    all_labels = [row[0] for row in all_result.fetchall()]

    return HotspotsResponse(
        repository_id=repo_id,
        total_files=repo.total_files,
        high_risk_count=all_labels.count("high"),
        medium_risk_count=all_labels.count("medium"),
        low_risk_count=all_labels.count("low"),
        hotspots=[HotspotFile.model_validate(f) for f in files],
    )
