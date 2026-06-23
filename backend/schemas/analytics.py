from typing import List, Optional, Dict
from pydantic import BaseModel


# ── Timeline ──────────────────────────────────────────────────
class TimelineBucket(BaseModel):
    period: str          # "2024-01" for month, "2024" for year, "2024-W03" for week
    label: str           # human-readable: "Jan 2024"
    commits: int
    insertions: int
    deletions: int
    unique_authors: int


class TimelineResponse(BaseModel):
    repository_id: int
    granularity: str     # "week" | "month" | "year"
    buckets: List[TimelineBucket]


# ── Hotspots ──────────────────────────────────────────────────
class HotspotFile(BaseModel):
    filepath: str
    filename: str
    extension: str
    directory: str
    change_count: int
    insertions: int
    deletions: int
    unique_authors: int
    risk_score: float
    risk_label: str
    risk_reason: str
    top_author: str
    top_author_pct: float

    model_config = {"from_attributes": True}


class HotspotsResponse(BaseModel):
    repository_id: int
    total_files: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    hotspots: List[HotspotFile]


# ── Ownership ──────────────────────────────────────────────────
class OwnerEntry(BaseModel):
    author: str
    email: str
    commit_count: int
    percentage: float


class ModuleOwnership(BaseModel):
    module: str           # directory path e.g. "src/auth"
    total_commits: int
    owners: List[OwnerEntry]  # sorted by percentage desc


class OwnershipResponse(BaseModel):
    repository_id: int
    modules: List[ModuleOwnership]


# ── Health ────────────────────────────────────────────────────
class HealthScoreBreakdown(BaseModel):
    label: str
    score: float
    weight: float
    description: str


class HealthResponse(BaseModel):
    repository_id: int
    health_score: float
    grade: str           # A / B / C / D / F
    breakdown: List[HealthScoreBreakdown]
    summary: str


# ── Milestones ─────────────────────────────────────────────────
class Milestone(BaseModel):
    year: int
    month: Optional[int]
    event: str
    type: str            # birth | release | feature | infra | devops | perf
    commit_sha: Optional[str]
    commit_message: Optional[str]


class MilestonesResponse(BaseModel):
    repository_id: int
    milestones: List[Milestone]
