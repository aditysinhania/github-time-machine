from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ContributorOut(BaseModel):
    id: int
    name: str
    email: str
    avatar_initials: str
    commit_count: int
    commit_percentage: float
    total_insertions: int
    total_deletions: int
    files_touched: int
    first_commit_at: Optional[datetime]
    last_commit_at: Optional[datetime]
    active_days: int
    is_bus_risk: bool
    rank: int

    model_config = {"from_attributes": True}


class ContributorsResponse(BaseModel):
    repository_id: int
    total: int
    bus_factor_score: float
    contributors: List[ContributorOut]
