import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from models.contributor import Contributor
from models.file_change import FileChange
from models.commit import Commit
from schemas.analytics import OwnershipResponse, ModuleOwnership, OwnerEntry
from analytics.contributor_analyzer import ContributorAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["ownership"])


@router.get("/{repo_id}/ownership", response_model=OwnershipResponse)
async def get_ownership(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns per-module ownership: who owns which directory and by what %.
    Ownership is calculated from file-level commit attribution.
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    # Load file changes
    fc_result = await db.execute(
        select(FileChange).where(FileChange.repository_id == repo_id)
    )
    file_changes = [
        {
            "filepath": fc.filepath,
            "directory": fc.directory,
            "change_count": fc.change_count,
            "top_author": fc.top_author,
            "top_author_pct": fc.top_author_pct,
        }
        for fc in fc_result.scalars().all()
    ]

    # Load commits for email→name map
    commit_result = await db.execute(
        select(Commit.author_name, Commit.author_email)
        .where(Commit.repository_id == repo_id)
        .distinct()
    )
    commits = [
        {"author_name": row[0], "author_email": row[1]}
        for row in commit_result.fetchall()
    ]

    # Load contributors
    contrib_result = await db.execute(
        select(Contributor)
        .where(Contributor.repository_id == repo_id)
        .order_by(Contributor.commit_count.desc())
    )
    contributors = [
        {
            "name": c.name,
            "email": c.email,
            "commit_count": c.commit_count,
            "commit_percentage": c.commit_percentage,
        }
        for c in contrib_result.scalars().all()
    ]

    analyzer = ContributorAnalyzer(contributors, commits)
    raw_modules = analyzer.module_ownership(file_changes, commits)

    modules = [
        ModuleOwnership(
            module=m["module"],
            total_commits=m["total_commits"],
            owners=[
                OwnerEntry(
                    author=o["author"],
                    email=o["email"],
                    commit_count=o["commit_count"],
                    percentage=o["percentage"],
                )
                for o in m["owners"]
            ],
        )
        for m in raw_modules
    ]

    return OwnershipResponse(repository_id=repo_id, modules=modules)
