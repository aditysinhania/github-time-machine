import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.base import get_db
from models.repository import Repository, AnalysisStatus
from models.contributor import Contributor
from models.file_change import FileChange
from schemas.ai import AISummaryResponse, ChatRequest, ChatResponse, ChatMessage
from services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/repositories", tags=["ai"])


async def _build_repo_data(repo: Repository, db: AsyncSession) -> dict:
    """Build the context dict passed to the AI service."""
    # Top contributor
    contrib_result = await db.execute(
        select(Contributor)
        .where(Contributor.repository_id == repo.id)
        .order_by(Contributor.commit_count.desc())
        .limit(1)
    )
    top_contrib = contrib_result.scalar_one_or_none()

    # High-risk files
    risk_result = await db.execute(
        select(FileChange.filepath)
        .where(
            FileChange.repository_id == repo.id,
            FileChange.risk_label == "high",
        )
        .order_by(FileChange.risk_score.desc())
        .limit(5)
    )
    high_risk_files = [row[0] for row in risk_result.fetchall()]

    # Top modules (directories)
    module_result = await db.execute(
        select(FileChange.directory)
        .where(FileChange.repository_id == repo.id)
        .distinct()
        .limit(8)
    )
    modules = [row[0] for row in module_result.fetchall() if row[0]]

    return {
        "full_name": repo.full_name,
        "primary_language": repo.primary_language or "Unknown",
        "total_commits": repo.total_commits,
        "total_contributors": repo.total_contributors,
        "age_days": repo.age_days,
        "health_score": repo.health_score or 0,
        "bus_factor_score": repo.bus_factor_score or 0,
        "top_contributor": top_contrib.name if top_contrib else "N/A",
        "top_pct": top_contrib.commit_percentage if top_contrib else 0,
        "high_risk_files": high_risk_files,
        "modules": modules,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/{repo_id}/ai/summary", response_model=AISummaryResponse)
async def get_ai_summary(
    repo_id: int,
    refresh: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate (or return cached) AI summary for a repository.
    Pass ?refresh=true to force regeneration even if cached.

    Returns structured insights: purpose, risks, strengths, recommendations.
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    # Return cached summary unless refresh requested
    if repo.ai_summary and not refresh:
        import json
        try:
            cached = json.loads(repo.ai_summary)
            return AISummaryResponse(
                repository_id=repo_id,
                summary=cached.get("summary", ""),
                purpose=cached.get("purpose", ""),
                risks=cached.get("risks", []),
                strengths=cached.get("strengths", []),
                recommendations=cached.get("recommendations", []),
            )
        except Exception:
            pass  # fall through to regenerate

    repo_data = await _build_repo_data(repo, db)

    ai = AIService()
    result = await ai.generate_summary(repo_data)

    # Cache the result as JSON in the DB
    import json
    await db.execute(
        update(Repository)
        .where(Repository.id == repo_id)
        .values(ai_summary=json.dumps(result))
    )
    await db.commit()

    return AISummaryResponse(
        repository_id=repo_id,
        summary=result.get("summary", ""),
        purpose=result.get("purpose", ""),
        risks=result.get("risks", []),
        strengths=result.get("strengths", []),
        recommendations=result.get("recommendations", []),
    )


@router.post("/{repo_id}/ai/chat", response_model=ChatResponse)
async def chat_with_repo(
    repo_id: int,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Natural language Q&A grounded in the repository's analysis data.

    Send conversation history in body.history to enable multi-turn chat.
    The new message goes in body.message.

    Example questions:
      "Who knows the payment module best?"
      "What changed most in 2024?"
      "Which files should I review before touching auth?"
    """
    repo = await db.get(Repository, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status != AnalysisStatus.COMPLETE:
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not complete yet. Status: {repo.status.value}",
        )

    repo_data = await _build_repo_data(repo, db)

    # Build message list for AI
    messages = [
        {"role": m.role, "content": m.content}
        for m in (body.history or [])
    ]
    messages.append({"role": "user", "content": body.message})

    ai = AIService()
    answer = await ai.chat(repo_data, messages)

    # Return updated history
    updated_history = [
        ChatMessage(role=m["role"], content=m["content"]) for m in messages
    ]
    updated_history.append(ChatMessage(role="assistant", content=answer))

    return ChatResponse(
        repository_id=repo_id,
        answer=answer,
        history=updated_history,
    )
