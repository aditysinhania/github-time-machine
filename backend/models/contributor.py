from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Contributor(Base):
    __tablename__ = "contributors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    repository_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_initials: Mapped[str] = mapped_column(String(4), nullable=False)

    # Stats
    commit_count: Mapped[int] = mapped_column(Integer, default=0)
    commit_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    total_insertions: Mapped[int] = mapped_column(Integer, default=0)
    total_deletions: Mapped[int] = mapped_column(Integer, default=0)
    files_touched: Mapped[int] = mapped_column(Integer, default=0)

    # Activity window
    first_commit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_commit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    active_days: Mapped[int] = mapped_column(Integer, default=0)

    # Derived
    is_bus_risk: Mapped[bool] = mapped_column(default=False)  # owns >40% of commits
    rank: Mapped[int] = mapped_column(Integer, default=0)     # 1 = top contributor

    # Relationship
    repository: Mapped["Repository"] = relationship("Repository", back_populates="contributors")  # noqa: F821

    __table_args__ = (
        Index("ix_contributors_repo_email", "repository_id", "email", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Contributor {self.name} [{self.commit_count} commits]>"
