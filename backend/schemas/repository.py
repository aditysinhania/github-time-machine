from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


# ── Request ───────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        v = v.strip().rstrip("/")
        if "github.com" not in v:
            raise ValueError("Only GitHub repositories are supported.")
        # Normalise: strip .git suffix
        if v.endswith(".git"):
            v = v[:-4]
        return v


# ── Response shapes ───────────────────────────────────────────
class RepositoryBase(BaseModel):
    id: int
    url: str
    owner: str
    name: str
    full_name: str
    description: Optional[str]
    primary_language: Optional[str]
    status: str

    model_config = {"from_attributes": True}


class RepositoryStats(RepositoryBase):
    total_commits: int
    total_contributors: int
    total_files: int
    first_commit_at: Optional[datetime]
    last_commit_at: Optional[datetime]
    age_days: int
    analyzed_at: Optional[datetime]


class RepositoryFull(RepositoryStats):
    health_score: Optional[float]
    bus_factor_score: Optional[float]
    consistency_score: Optional[float]
    diversity_score: Optional[float]
    hotspot_score: Optional[float]
    ai_summary: Optional[str]
    error_message: Optional[str] = None


class AnalyzeResponse(BaseModel):
    message: str
    repository_id: int
    status: str
