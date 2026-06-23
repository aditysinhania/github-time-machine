import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from models.contributor import Contributor
from schemas.contributor import ContributorsResponse, ContributorOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["contributors"])


@router.get("/{repo_id}/contributors", response_model=ContributorsResponse)
async def get_contributors(
    repo_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    Return all contributors for a repository, sorted by commit count desc.
    Includes bus factor score from the repository record.
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Current status: {repo.status.value}",
        )

    result = await db.execute(
        select(Contributor)
        .where(Contributor.repository_id == repo_id)
        .order_by(Contributor.commit_count.desc())
        .limit(limit)
    )
    contributors = result.scalars().all()

    return ContributorsResponse(
        repository_id=repo_id,
        total=repo.total_contributors,
        bus_factor_score=repo.bus_factor_score or 0.0,
        contributors=[ContributorOut.model_validate(c) for c in contributors],
    )
