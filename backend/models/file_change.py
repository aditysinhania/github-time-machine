from sqlalchemy import String, Integer, Float, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class FileChange(Base):
    __tablename__ = "file_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    repository_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # File identity
    filepath: Mapped[str] = mapped_column(String(1024), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    directory: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    # Churn metrics
    change_count: Mapped[int] = mapped_column(Integer, default=0)     # commits touching this file
    insertions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    unique_authors: Mapped[int] = mapped_column(Integer, default=0)

    # Risk assessment
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)     # 0.0–1.0
    risk_label: Mapped[str] = mapped_column(String(10), default="low") # low / medium / high
    risk_reason: Mapped[str] = mapped_column(Text, default="")

    # Ownership — top author by commits on this file
    top_author: Mapped[str] = mapped_column(String(255), default="")
    top_author_pct: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationship
    repository: Mapped["Repository"] = relationship("Repository", back_populates="file_changes")  # noqa: F821

    __table_args__ = (
        Index("ix_file_changes_repo_filepath", "repository_id", "filepath", unique=True),
        Index("ix_file_changes_repo_risk", "repository_id", "risk_score"),
    )

    def __repr__(self) -> str:
        return f"<FileChange {self.filepath} [{self.risk_label}]>"
