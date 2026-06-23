import os
import re
import shutil
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import git
from git import Repo, InvalidGitRepositoryError

from core.config import settings

logger = logging.getLogger(__name__)


def _repo_dir(url: str) -> str:
    """Deterministic directory name for a given repo URL."""
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", url.split("github.com/")[-1])
    uid = hashlib.md5(url.encode()).hexdigest()[:8]
    return os.path.join(settings.REPO_CLONE_DIR, f"{slug}_{uid}")


def _make_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"


# ── Main entry point ──────────────────────────────────────────────────────────
class GitService:
    """Handles cloning and raw data extraction from a git repository."""

    def __init__(self, url: str):
        self.url = url
        self.clone_dir = _repo_dir(url)
        self.repo: Optional[Repo] = None

    # ── Clone / open ──────────────────────────────────────────
    def clone_or_open(self, on_progress=None) -> None:
        """Clone if not present, otherwise open existing clone."""
        if os.path.exists(self.clone_dir):
            try:
                self.repo = Repo(self.clone_dir)
                logger.info(f"Opened existing clone at {self.clone_dir}")
                return
            except InvalidGitRepositoryError:
                shutil.rmtree(self.clone_dir, ignore_errors=True)

        logger.info(f"Cloning {self.url} → {self.clone_dir}")
        os.makedirs(self.clone_dir, exist_ok=True)

        env = {}
        if settings.GITHUB_TOKEN:
            # Inject token for private repos
            authed = self.url.replace(
                "https://github.com",
                f"https://{settings.GITHUB_TOKEN}@github.com",
            )
        else:
            authed = self.url

        self.repo = Repo.clone_from(
            authed,
            self.clone_dir,
            progress=on_progress,
            env=env,
        )

    def cleanup(self) -> None:
        """Remove the local clone to free disk space."""
        if os.path.exists(self.clone_dir):
            shutil.rmtree(self.clone_dir, ignore_errors=True)

    # ── Repository metadata ───────────────────────────────────
    def get_repo_info(self) -> Dict:
        """Extract owner/name/description from the remote URL."""
        parts = self.url.rstrip("/").split("/")
        owner = parts[-2] if len(parts) >= 2 else "unknown"
        name = parts[-1].replace(".git", "")
        return {
            "url": self.url,
            "owner": owner,
            "name": name,
            "full_name": f"{owner}/{name}",
            "description": None,  # GitHub API needed for description
        }

    # ── Commit extraction ─────────────────────────────────────
    def extract_commits(self) -> List[Dict]:
        """
        Walk all commits on the default branch.
        Returns a list of dicts — one per commit.
        Capped at MAX_COMMITS to avoid memory issues on huge repos.
        """
        if not self.repo:
            raise RuntimeError("Repository not cloned yet.")

        commits = []
        seen_shas = set()
        cap = settings.MAX_COMMITS

        try:
            branch = self.repo.active_branch.name
        except TypeError:
            branch = "HEAD"

        for commit in self.repo.iter_commits(branch, max_count=cap):
            sha = commit.hexsha
            if sha in seen_shas:
                continue
            seen_shas.add(sha)

            # Stats
            try:
                stats = commit.stats.total
                files_changed = stats.get("files", 0)
                insertions = stats.get("insertions", 0)
                deletions = stats.get("deletions", 0)
            except Exception:
                files_changed = insertions = deletions = 0

            committed_at = datetime.fromtimestamp(
                commit.committed_date, tz=timezone.utc
            )

            msg = commit.message.strip()
            commits.append({
                "sha": sha,
                "short_sha": sha[:8],
                "message": msg,
                "message_short": msg.split("\n")[0][:200],
                "author_name": commit.author.name or "Unknown",
                "author_email": (commit.author.email or "").lower(),
                "committed_at": committed_at,
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
                "branch": branch,
            })

        logger.info(f"Extracted {len(commits)} commits from {self.url}")
        return commits

    # ── File change extraction ────────────────────────────────
    def extract_file_changes(self, commits: List[Dict]) -> List[Dict]:
        """
        Build per-file stats from commit history.
        Returns a list of dicts with churn metrics per file.
        """
        if not self.repo:
            raise RuntimeError("Repository not cloned yet.")

        # file → {author_email → count}
        file_author_counts: Dict[str, Dict[str, int]] = {}
        file_stats: Dict[str, Dict] = {}

        for commit_obj in self.repo.iter_commits(
            self.repo.active_branch.name, max_count=settings.MAX_COMMITS
        ):
            author_email = (commit_obj.author.email or "").lower()
            try:
                for filepath, detail in commit_obj.stats.files.items():
                    if filepath not in file_stats:
                        file_stats[filepath] = {
                            "insertions": 0, "deletions": 0, "change_count": 0
                        }
                        file_author_counts[filepath] = {}

                    file_stats[filepath]["change_count"] += 1
                    file_stats[filepath]["insertions"] += detail.get("insertions", 0)
                    file_stats[filepath]["deletions"] += detail.get("deletions", 0)

                    cnt = file_author_counts[filepath]
                    cnt[author_email] = cnt.get(author_email, 0) + 1
            except Exception:
                continue

        results = []
        for filepath, stats in file_stats.items():
            p = Path(filepath)
            author_counts = file_author_counts.get(filepath, {})
            unique_authors = len(author_counts)

            top_author_email = ""
            top_author_pct = 0.0
            if author_counts:
                top_author_email = max(author_counts, key=author_counts.get)
                total = sum(author_counts.values())
                top_author_pct = round(author_counts[top_author_email] / total * 100, 1)

            results.append({
                "filepath": filepath,
                "filename": p.name,
                "extension": p.suffix.lstrip(".").lower(),
                "directory": str(p.parent),
                "change_count": stats["change_count"],
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
                "unique_authors": unique_authors,
                "top_author": top_author_email,
                "top_author_pct": top_author_pct,
            })

        logger.info(f"Extracted stats for {len(results)} files")
        return results

    # ── Contributor extraction ────────────────────────────────
    def extract_contributors(self, commits: List[Dict]) -> List[Dict]:
        """Aggregate per-author stats from the commit list."""
        from collections import defaultdict

        author_data: Dict[str, Dict] = defaultdict(lambda: {
            "commit_count": 0,
            "insertions": 0,
            "deletions": 0,
            "dates": [],
            "name": "",
        })

        for c in commits:
            email = c["author_email"]
            author_data[email]["commit_count"] += 1
            author_data[email]["insertions"] += c["insertions"]
            author_data[email]["deletions"] += c["deletions"]
            author_data[email]["dates"].append(c["committed_at"])
            if not author_data[email]["name"]:
                author_data[email]["name"] = c["author_name"]

        total_commits = len(commits)
        results = []
        for email, data in author_data.items():
            dates = sorted(data["dates"])
            active_days = (dates[-1] - dates[0]).days + 1 if len(dates) > 1 else 1
            pct = round(data["commit_count"] / total_commits * 100, 2) if total_commits else 0.0

            results.append({
                "name": data["name"] or email.split("@")[0],
                "email": email,
                "avatar_initials": _make_initials(data["name"] or email),
                "commit_count": data["commit_count"],
                "commit_percentage": pct,
                "total_insertions": data["insertions"],
                "total_deletions": data["deletions"],
                "files_touched": 0,  # filled in by contributor_analyzer
                "first_commit_at": dates[0],
                "last_commit_at": dates[-1],
                "active_days": active_days,
                "is_bus_risk": pct > 40,
                "rank": 0,  # assigned after sorting
            })

        # Sort and rank
        results.sort(key=lambda x: x["commit_count"], reverse=True)
        for i, r in enumerate(results):
            r["rank"] = i + 1

        return results
