import os
from database.base import Base, engine

# Import all models so SQLAlchemy's metadata is populated before create_all
from models import repository, commit, contributor, file_change  # noqa: F401


async def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    # Ensure the clone directory exists
    clone_dir = os.environ.get("REPO_CLONE_DIR", "/tmp/repos")
    os.makedirs(clone_dir, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
