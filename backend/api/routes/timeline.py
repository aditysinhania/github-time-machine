import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from models.commit import Commit
from schemas.analytics import TimelineResponse, TimelineBucket, MilestonesResponse, Milestone
from analytics.commit_analyzer import CommitAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["timeline"])


def _load_commits_as_dicts(commits) -> list:
    return [
        {
            "sha": c.sha,
            "short_sha": c.short_sha,
            "message": c.message,
            "message_short": c.message_short,
            "author_name": c.author_name,
            "author_email": c.author_email,
            "committed_at": c.committed_at,
            "insertions": c.insertions,
            "deletions": c.deletions,
            "files_changed": c.files_changed,
        }
        for c in commits
    ]


@router.get("/{repo_id}/timeline", response_model=TimelineResponse)
async def get_timeline(
    repo_id: int,
    granularity: str = Query(default="month", pattern="^(week|month|year)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns commit activity bucketed by week / month / year.
    Use granularity=week for recent detailed view,
        granularity=year for long-running repos.
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    result = await db.execute(
        select(Commit)
        .where(Commit.repository_id == repo_id)
        .order_by(Commit.committed_at.asc())
    )
    commits = result.scalars().all()
    commit_dicts = _load_commits_as_dicts(commits)

    analyzer = CommitAnalyzer(commit_dicts)
    buckets = analyzer.timeline(granularity)

    return TimelineResponse(
        repository_id=repo_id,
        granularity=granularity,
        buckets=[TimelineBucket(**b) for b in buckets],
    )


@router.get("/{repo_id}/milestones", response_model=MilestonesResponse)
async def get_milestones(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns AI-heuristic detected milestones extracted from commit messages.
    These represent major events: releases, migrations, features, etc.
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    result = await db.execute(
        select(Commit)
        .where(Commit.repository_id == repo_id)
        .order_by(Commit.committed_at.asc())
    )
    commits = result.scalars().all()
    commit_dicts = _load_commits_as_dicts(commits)

    analyzer = CommitAnalyzer(commit_dicts)
    raw_milestones = analyzer.milestones()

    return MilestonesResponse(
        repository_id=repo_id,
        milestones=[Milestone(**m) for m in raw_milestones],
    )
