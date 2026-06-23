"""
Seed the database with a demo repository analysis.

Runs the real analysis pipeline (clone + extract + analytics) against a small,
well-known public repository so the dashboard has data to show immediately
after a fresh `docker compose up`.

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo.py --url https://github.com/pallets/flask
"""
import asyncio
import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from database.base import AsyncSessionLocal
from database.init_db import init_db
from models.repository import Repository, AnalysisStatus
from api.routes.repositories import run_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

DEFAULT_DEMO_URL = "https://github.com/pallets/flask"


async def seed(url: str) -> None:
    await init_db()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Repository).where(Repository.url == url))
        existing = result.scalar_one_or_none()

        if existing and existing.status == AnalysisStatus.COMPLETE:
            logger.info(f"'{url}' is already analyzed (repo id={existing.id}). Skipping.")
            return

        if existing:
            repo_id = existing.id
            existing.status = AnalysisStatus.PENDING
            await db.commit()
        else:
            parts = url.rstrip("/").split("/")
            owner, name = parts[-2], parts[-1]
            repo = Repository(
                url=url,
                owner=owner,
                name=name,
                full_name=f"{owner}/{name}",
                status=AnalysisStatus.PENDING,
            )
            db.add(repo)
            await db.flush()
            await db.commit()
            repo_id = repo.id

    logger.info(f"Seeding repository id={repo_id} from {url} — this may take 30-90s…")
    await run_analysis(repo_id, url)
    logger.info(f"Done. View it at /dashboard/{repo_id} once the frontend is running.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed a demo repository analysis.")
    parser.add_argument("--url", default=DEFAULT_DEMO_URL, help="GitHub repo URL to analyze")
    args = parser.parse_args()

    asyncio.run(seed(args.url))
