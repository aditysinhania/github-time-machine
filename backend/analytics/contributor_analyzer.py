import logging
import math
from typing import List, Dict

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ContributorAnalyzer:
    """
    Computes bus factor, contributor diversity score, and
    per-module ownership from contributor + file-change data.
    """

    def __init__(self, contributors: List[Dict], commits: List[Dict]):
        self._contributors = contributors
        self._commits = commits
        self._df_commits = pd.DataFrame(commits) if commits else pd.DataFrame()

    # ── Bus Factor ────────────────────────────────────────────

    def bus_factor(self) -> int:
        """
        Returns the minimum number of contributors whose removal
        would account for >50% of the total commits.
        Classic bus-factor calculation.
        """
        if not self._contributors:
            return 0

        sorted_contribs = sorted(
            self._contributors, key=lambda x: x["commit_count"], reverse=True
        )
        total = sum(c["commit_count"] for c in sorted_contribs)
        if total == 0:
            return 0

        cumulative = 0
        for i, c in enumerate(sorted_contribs):
            cumulative += c["commit_count"]
            if cumulative / total >= 0.5:
                return i + 1

        return len(sorted_contribs)

    def bus_factor_score(self) -> float:
        """
        Converts raw bus factor (integer) into a 0–100 score.
        bus_factor=1 → ~35  (risky — one person holds majority knowledge)
        bus_factor=5 → ~74  (healthier spread)
        bus_factor≥10 → ~92 (well distributed)
        Uses logarithmic scaling; floor is 10, cap is 95.
        """
        bf = self.bus_factor()
        if bf <= 0:
            return 0.0
        # log scale: score = min(95, 10 + 85 * log(bf) / log(10))
        score = min(95.0, 10.0 + 85.0 * math.log(bf + 1) / math.log(11))
        return round(score, 1)

    # ── Diversity Score ───────────────────────────────────────

    def diversity_score(self) -> float:
        """
        Measures how evenly distributed contributions are.
        Uses normalised Shannon entropy over contributor commit shares.
        Score 0–100. Higher = more evenly distributed.
        """
        if not self._contributors:
            return 0.0

        counts = [c["commit_count"] for c in self._contributors if c["commit_count"] > 0]
        total = sum(counts)
        if total == 0 or len(counts) == 1:
            return 0.0

        probs = [c / total for c in counts]
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        max_entropy = math.log(len(counts))

        if max_entropy == 0:
            return 0.0

        normalised = entropy / max_entropy  # 0–1
        return round(normalised * 100, 1)

    # ── Consistency Score ─────────────────────────────────────

    def consistency_score(self) -> float:
        """
        Measures regularity of commit activity over time.
        High variance in monthly commit counts → low score.
        Score 0–100.
        """
        if self._df_commits.empty:
            return 0.0

        df = self._df_commits.copy()
        df["committed_at"] = pd.to_datetime(df["committed_at"], utc=True)
        df["month"] = df["committed_at"].dt.to_period("M")
        monthly = df.groupby("month").size()

        if len(monthly) < 2:
            return 50.0

        mean = monthly.mean()
        std = monthly.std()
        if mean == 0:
            return 0.0

        cv = std / mean  # coefficient of variation — lower = more consistent
        # Map cv 0→100, cv 2→0
        score = max(0.0, 100.0 - (cv * 50.0))
        return round(score, 1)

    # ── Module Ownership ──────────────────────────────────────

    def module_ownership(self, file_changes: List[Dict], commits: List[Dict]) -> List[Dict]:
        """
        Groups files by top-level directory (module) and calculates
        ownership percentages per author within each module.

        Returns a list of module ownership dicts.
        """
        if not commits or not file_changes:
            return []

        # Build filepath → directory map
        dir_map: Dict[str, str] = {}
        for fc in file_changes:
            filepath = fc.get("filepath", "")
            directory = fc.get("directory", "")
            # Use top-level or second-level dir as module name
            parts = directory.split("/")
            if parts and parts[0] not in ("", "."):
                module = parts[0] if len(parts) < 3 else "/".join(parts[:2])
            else:
                module = "root"
            dir_map[filepath] = module

        # Build module → {author_email → count}
        module_author: Dict[str, Dict[str, int]] = {}
        email_name: Dict[str, str] = {
            c["author_email"]: c["author_name"] for c in commits
        }

        # We need per-commit file data — approximate using file_changes top_author
        for fc in file_changes:
            filepath = fc.get("filepath", "")
            module = dir_map.get(filepath, "root")
            author = fc.get("top_author", "unknown")
            count = fc.get("change_count", 0)

            if module not in module_author:
                module_author[module] = {}
            module_author[module][author] = (
                module_author[module].get(author, 0) + count
            )

        results = []
        for module, author_counts in module_author.items():
            total = sum(author_counts.values())
            if total == 0:
                continue

            owners = []
            for email, count in sorted(
                author_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]:  # top 5 owners per module
                owners.append({
                    "author": email_name.get(email, email.split("@")[0]),
                    "email": email,
                    "commit_count": count,
                    "percentage": round(count / total * 100, 1),
                })

            results.append({
                "module": module,
                "total_commits": total,
                "owners": owners,
            })

        # Sort by total_commits desc
        results.sort(key=lambda x: x["total_commits"], reverse=True)
        return results[:15]  # top 15 modules
