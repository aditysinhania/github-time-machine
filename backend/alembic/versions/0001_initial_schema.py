"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── repositories ──────────────────────────────────────────────────
    op.create_table(
        "repositories",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("primary_language", sa.String(length=100), nullable=True),
        sa.Column("total_commits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_contributors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("first_commit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_commit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("age_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("health_score", sa.Float(), nullable=True),
        sa.Column("bus_factor_score", sa.Float(), nullable=True),
        sa.Column("consistency_score", sa.Float(), nullable=True),
        sa.Column("diversity_score", sa.Float(), nullable=True),
        sa.Column("hotspot_score", sa.Float(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "cloning", "analyzing", "complete", "failed", name="analysisstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_repositories_id", "repositories", ["id"])
    op.create_index("ix_repositories_url", "repositories", ["url"], unique=True)

    # ── commits ───────────────────────────────────────────────────────
    op.create_table(
        "commits",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "repository_id",
            sa.Integer(),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sha", sa.String(length=40), nullable=False),
        sa.Column("short_sha", sa.String(length=8), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("message_short", sa.String(length=200), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=False),
        sa.Column("author_email", sa.String(length=255), nullable=False),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("files_changed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("insertions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("branch", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_commits_id", "commits", ["id"])
    op.create_index("ix_commits_repository_id", "commits", ["repository_id"])
    op.create_index("ix_commits_committed_at", "commits", ["committed_at"])
    op.create_index("ix_commits_repo_date", "commits", ["repository_id", "committed_at"])
    op.create_index("ix_commits_repo_sha", "commits", ["repository_id", "sha"], unique=True)

    # ── contributors ──────────────────────────────────────────────────
    op.create_table(
        "contributors",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "repository_id",
            sa.Integer(),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("avatar_initials", sa.String(length=4), nullable=False),
        sa.Column("commit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("commit_percentage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_insertions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("files_touched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("first_commit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_commit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_bus_risk", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rank", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_contributors_id", "contributors", ["id"])
    op.create_index("ix_contributors_repository_id", "contributors", ["repository_id"])
    op.create_index(
        "ix_contributors_repo_email", "contributors", ["repository_id", "email"], unique=True
    )

    # ── file_changes ──────────────────────────────────────────────────
    op.create_table(
        "file_changes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "repository_id",
            sa.Integer(),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filepath", sa.String(length=1024), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("extension", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("directory", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("change_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("insertions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_authors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_label", sa.String(length=10), nullable=False, server_default="low"),
        sa.Column("risk_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("top_author", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("top_author_pct", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_file_changes_id", "file_changes", ["id"])
    op.create_index("ix_file_changes_repository_id", "file_changes", ["repository_id"])
    op.create_index(
        "ix_file_changes_repo_filepath", "file_changes", ["repository_id", "filepath"], unique=True
    )
    op.create_index("ix_file_changes_repo_risk", "file_changes", ["repository_id", "risk_score"])


def downgrade() -> None:
    op.drop_table("file_changes")
    op.drop_table("contributors")
    op.drop_table("commits")
    op.drop_table("repositories")
    op.execute("DROP TYPE IF EXISTS analysisstatus")
