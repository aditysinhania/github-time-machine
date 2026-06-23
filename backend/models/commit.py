from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Commit(Base):
    __tablename__ = "commits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    repository_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Git fields
    sha: Mapped[str] = mapped_column(String(40), nullable=False)
    short_sha: Mapped[str] = mapped_column(String(8), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    message_short: Mapped[str] = mapped_column(String(200), nullable=False)  # first line only

    # Author
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Stats
    files_changed: Mapped[int] = mapped_column(Integer, default=0)
    insertions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)

    # Branch (best-effort — git doesn't store this per-commit)
    branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationship
    repository: Mapped["Repository"] = relationship("Repository", back_populates="commits")  # noqa: F821

    __table_args__ = (
        Index("ix_commits_repo_date", "repository_id", "committed_at"),
        Index("ix_commits_repo_sha", "repository_id", "sha", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Commit {self.short_sha} by {self.author_name}>"
