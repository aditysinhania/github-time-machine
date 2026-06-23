import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Dict

import pandas as pd

logger = logging.getLogger(__name__)


class CommitAnalyzer:
    """
    Turns a flat list of commit dicts into bucketed timeline data
    at week / month / year granularity.
    """

    def __init__(self, commits: List[Dict]):
        if not commits:
            self._df = pd.DataFrame()
            return

        self._df = pd.DataFrame(commits)
        # Ensure datetime column is timezone-aware
        self._df["committed_at"] = pd.to_datetime(
            self._df["committed_at"], utc=True
        )
        self._df.sort_values("committed_at", inplace=True)

    # ── Public API ────────────────────────────────────────────

    def timeline(self, granularity: str = "month") -> List[Dict]:
        """
        Returns a list of time-bucketed dicts.

        granularity: "week" | "month" | "year"

        Each dict:
          period        ISO period key  e.g. "2024-01"
          label         Human label     e.g. "Jan 2024"
          commits       int
          insertions    int
          deletions     int
          unique_authors int
        """
        if self._df.empty:
            return []

        df = self._df.copy()
        df["period"] = df["committed_at"].dt.to_period(
            "W" if granularity == "week" else ("M" if granularity == "month" else "Y")
        )

        grouped = (
            df.groupby("period")
            .agg(
                commits=("sha", "count"),
                insertions=("insertions", "sum"),
                deletions=("deletions", "sum"),
                unique_authors=("author_email", "nunique"),
            )
            .reset_index()
        )

        results = []
        for _, row in grouped.iterrows():
            period_str = str(row["period"])
            label = self._format_label(row["period"], granularity)
            results.append({
                "period": period_str,
                "label": label,
                "commits": int(row["commits"]),
                "insertions": int(row["insertions"]),
                "deletions": int(row["deletions"]),
                "unique_authors": int(row["unique_authors"]),
            })

        return results

    def milestones(self) -> List[Dict]:
        """
        Heuristically detect significant commits as milestones.
        Looks for keywords in commit messages that signal major events.
        """
        if self._df.empty:
            return []

        keyword_map = {
            "birth":   ["initial commit", "first commit", "init", "initialize", "bootstrap"],
            "release": ["release", "version", "v1.", "v2.", "v3.", "tag", "changelog", "bump version"],
            "feature": ["add", "feat:", "feature", "implement", "introduce", "new:"],
            "infra":   ["migrate", "migration", "docker", "kubernetes", "ci/cd", "pipeline", "deploy"],
            "devops":  ["github actions", "workflow", "ci:", "cd:", "jenkins", "travis"],
            "perf":    ["performance", "optimize", "speed", "refactor", "rewrite", "faster"],
        }

        results = []
        seen_years = set()

        for _, row in self._df.iterrows():
            msg = row["message_short"].lower()
            committed_at: datetime = row["committed_at"]

            for event_type, keywords in keyword_map.items():
                if any(kw in msg for kw in keywords):
                    year = committed_at.year
                    month = committed_at.month

                    # Only keep one milestone per type per year to avoid noise
                    key = (event_type, year)
                    if key in seen_years:
                        continue
                    seen_years.add(key)

                    results.append({
                        "year": year,
                        "month": month,
                        "event": row["message_short"][:120],
                        "type": event_type,
                        "commit_sha": row["short_sha"],
                        "commit_message": row["message_short"],
                    })
                    break  # one type per commit

        # Sort chronologically
        results.sort(key=lambda x: (x["year"], x["month"]))
        return results[:20]  # cap at 20 milestones

    def summary_stats(self) -> Dict:
        """Returns high-level stats for KPI cards."""
        if self._df.empty:
            return {
                "total_commits": 0,
                "first_commit_at": None,
                "last_commit_at": None,
                "age_days": 0,
                "avg_commits_per_month": 0.0,
                "most_active_day": None,
            }

        first = self._df["committed_at"].min()
        last = self._df["committed_at"].max()
        age_days = max((last - first).days, 1)
        months = max(age_days / 30, 1)

        day_counts = self._df["committed_at"].dt.day_name().value_counts()
        most_active = day_counts.idxmax() if not day_counts.empty else None

        return {
            "total_commits": len(self._df),
            "first_commit_at": first.to_pydatetime(),
            "last_commit_at": last.to_pydatetime(),
            "age_days": age_days,
            "avg_commits_per_month": round(len(self._df) / months, 1),
            "most_active_day": most_active,
        }

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _format_label(period, granularity: str) -> str:
        try:
            start = period.start_time
            if granularity == "week":
                return f"W{start.isocalendar()[1]} {start.year}"
            elif granularity == "month":
                return start.strftime("%b %Y")
            else:
                return str(period)
        except Exception:
            return str(period)
