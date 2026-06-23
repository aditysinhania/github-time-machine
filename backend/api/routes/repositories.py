import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from models.commit import Commit
from models.contributor import Contributor
from models.file_change import FileChange
from schemas.repository import AnalyzeRequest, AnalyzeResponse, RepositoryFull, RepositoryStats
from services.git_service import GitService
from analytics.commit_analyzer import CommitAnalyzer
from analytics.contributor_analyzer import ContributorAnalyzer
from analytics.hotspot_analyzer import HotspotAnalyzer
from analytics.health_analyzer import HealthAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["repositories"])


# ── Background analysis task ──────────────────────────────────────────────────
async def run_analysis(repo_id: int, url: str):
    """
    Full analysis pipeline runs in the background after the POST returns.
    Stages:
      1. Clone / open repository
      2. Extract commits
      3. Extract file changes
      4. Extract contributors
      5. Run all analytics
      6. Persist results
    """
    from database.base import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        repo = await db.get(Repository, repo_id)
        if not repo:
            logger.error(f"Repository {repo_id} not found in DB")
            return

        git_svc = GitService(url)

        try:
            # ── Stage 1: Clone ────────────────────────────────
            repo.status = AnalysisStatus.CLONING
            await db.commit()

            await asyncio.get_event_loop().run_in_executor(
                None, git_svc.clone_or_open
            )

            # ── Stage 2: Extract commits ─────────────────────
            repo.status = AnalysisStatus.ANALYZING
            await db.commit()

            raw_commits = await asyncio.get_event_loop().run_in_executor(
                None, git_svc.extract_commits
            )

            # ── Stage 3: Extract file changes ────────────────
            raw_files = await asyncio.get_event_loop().run_in_executor(
                None, lambda: git_svc.extract_file_changes(raw_commits)
            )

            # ── Stage 4: Extract contributors ────────────────
            raw_contribs = git_svc.extract_contributors(raw_commits)

            # ── Stage 5: Analytics ────────────────────────────
            commit_analyzer = CommitAnalyzer(raw_commits)
            contrib_analyzer = ContributorAnalyzer(raw_contribs, raw_commits)
            hotspot_analyzer = HotspotAnalyzer(raw_files)

            stats = commit_analyzer.summary_stats()
            scored_files = hotspot_analyzer.score_and_label()

            bus_score = contrib_analyzer.bus_factor_score()
            consistency = contrib_analyzer.consistency_score()
            diversity = contrib_analyzer.diversity_score()
            hotspot_s = hotspot_analyzer.hotspot_score(scored_files)

            health = HealthAnalyzer(bus_score, consistency, diversity, hotspot_s).compute()

            # ── Stage 6: Persist ──────────────────────────────
            # Update repository record
            repo.total_commits = stats["total_commits"]
            repo.total_contributors = len(raw_contribs)
            repo.total_files = len(scored_files)
            repo.first_commit_at = stats["first_commit_at"]
            repo.last_commit_at = stats["last_commit_at"]
            repo.age_days = stats["age_days"]
            repo.health_score = health["health_score"]
            repo.bus_factor_score = bus_score
            repo.consistency_score = consistency
            repo.diversity_score = diversity
            repo.hotspot_score = hotspot_s
            repo.status = AnalysisStatus.COMPLETE
            repo.analyzed_at = datetime.now(timezone.utc)

            # Bulk insert commits (skip if already exist)
            existing_shas = set()
            result = await db.execute(
                select(Commit.sha).where(Commit.repository_id == repo_id)
            )
            existing_shas = {row[0] for row in result.fetchall()}

            new_commits = [
                Commit(repository_id=repo_id, **c)
                for c in raw_commits
                if c["sha"] not in existing_shas
            ]
            db.add_all(new_commits)

            # Bulk insert contributors (upsert by email)
            for c in raw_contribs:
                existing = await db.execute(
                    select(Contributor).where(
                        Contributor.repository_id == repo_id,
                        Contributor.email == c["email"],
                    )
                )
                existing_contrib = existing.scalar_one_or_none()
                if existing_contrib:
                    for k, v in c.items():
                        setattr(existing_contrib, k, v)
                else:
                    db.add(Contributor(repository_id=repo_id, **c))

            # Bulk insert file changes (upsert by filepath)
            for f in scored_files:
                existing = await db.execute(
                    select(FileChange).where(
                        FileChange.repository_id == repo_id,
                        FileChange.filepath == f["filepath"],
                    )
                )
                existing_fc = existing.scalar_one_or_none()
                if existing_fc:
                    for k, v in f.items():
                        setattr(existing_fc, k, v)
                else:
                    db.add(FileChange(repository_id=repo_id, **f))

            await db.commit()
            logger.info(f"Analysis complete for repo {repo_id} ({url})")

        except Exception as e:
            logger.exception(f"Analysis failed for repo {repo_id}: {e}")
            repo.status = AnalysisStatus.FAILED
            repo.error_message = str(e)
            await db.commit()
        finally:
            git_svc.cleanup()


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_repository(
    body: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a GitHub URL, create a Repository record, and kick off
    the full analysis pipeline in the background.
    Returns immediately with status=pending.
    """
    # Check if already analyzed (re-use)
    result = await db.execute(
        select(Repository).where(Repository.url == body.url)
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.status == AnalysisStatus.COMPLETE:
            return AnalyzeResponse(
                message="Repository already analyzed.",
                repository_id=existing.id,
                status=existing.status.value,
            )
        if existing.status in (AnalysisStatus.CLONING, AnalysisStatus.ANALYZING):
            return AnalyzeResponse(
                message="Analysis already in progress.",
                repository_id=existing.id,
                status=existing.status.value,
            )
        # Failed — retry
        existing.status = AnalysisStatus.PENDING
        existing.error_message = None
        await db.commit()
        background_tasks.add_task(run_analysis, existing.id, body.url)
        return AnalyzeResponse(
            message="Re-running analysis.",
            repository_id=existing.id,
            status=AnalysisStatus.PENDING.value,
        )

    # Parse owner/name from URL
    parts = body.url.rstrip("/").split("/")
    owner = parts[-2] if len(parts) >= 2 else "unknown"
    name = parts[-1]

    repo = Repository(
        url=body.url,
        owner=owner,
        name=name,
        full_name=f"{owner}/{name}",
        status=AnalysisStatus.PENDING,
    )
    db.add(repo)
    await db.flush()  # get the id
    await db.commit()

    background_tasks.add_task(run_analysis, repo.id, body.url)

    return AnalyzeResponse(
        message="Analysis started. Poll GET /repositories/{id} for status.",
        repository_id=repo.id,
        status=AnalysisStatus.PENDING.value,
    )


@router.get("/{repo_id}", response_model=RepositoryFull)
async def get_repository(repo_id: int, db: AsyncSession = Depends(get_db)):
    """Get full repository details including health scores."""
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return repo


@router.get("/", response_model=list[RepositoryStats])
async def list_repositories(
    skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)
):
    """List all analyzed repositories, most recent first."""
    result = await db.execute(
        select(Repository)
        .order_by(Repository.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(repo_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a repository and all its associated data (cascade)."""
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    await db.delete(repo)
    await db.commit()
