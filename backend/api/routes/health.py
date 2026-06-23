import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from schemas.analytics import HealthResponse, HealthScoreBreakdown
from analytics.health_analyzer import HealthAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["health"])


@router.get("/{repo_id}/health", response_model=HealthResponse)
async def get_health(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the composite health score (0–100) with a full breakdown
    of the four sub-dimensions: bus factor, consistency, diversity, hotspot.

    Grade mapping:
      A = 90+  |  B = 80+  |  C = 65+  |  D = 50+  |  F = <50
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    analyzer = HealthAnalyzer(
        bus_factor_score=repo.bus_factor_score or 0.0,
        consistency_score=repo.consistency_score or 0.0,
        diversity_score=repo.diversity_score or 0.0,
        hotspot_score=repo.hotspot_score or 0.0,
    )
    result = analyzer.compute()

    return HealthResponse(
        repository_id=repo_id,
        health_score=result["health_score"],
        grade=result["grade"],
        breakdown=[HealthScoreBreakdown(**b) for b in result["breakdown"]],
        summary=result["summary"],
    )
