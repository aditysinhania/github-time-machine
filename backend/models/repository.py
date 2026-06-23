from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, Float, DateTime, Text, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from database.base import Base


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    CLONING = "cloning"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Identity
    url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), nullable=False)  # owner/name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Stats (filled after analysis)
    total_commits: Mapped[int] = mapped_column(Integer, default=0)
    total_contributors: Mapped[int] = mapped_column(Integer, default=0)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    first_commit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_commit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    age_days: Mapped[int] = mapped_column(Integer, default=0)

    # Health scores (0–100)
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bus_factor_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    consistency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    diversity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hotspot_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Job tracking
    status: Mapped[AnalysisStatus] = mapped_column(
        SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    commits: Mapped[List["Commit"]] = relationship(  # noqa: F821
        "Commit", back_populates="repository", cascade="all, delete-orphan"
    )
    contributors: Mapped[List["Contributor"]] = relationship(  # noqa: F821
        "Contributor", back_populates="repository", cascade="all, delete-orphan"
    )
    file_changes: Mapped[List["FileChange"]] = relationship(  # noqa: F821
        "FileChange", back_populates="repository", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Repository {self.full_name} [{self.status}]>"
