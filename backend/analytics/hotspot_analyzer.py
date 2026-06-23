import logging
import math
from typing import List, Dict

logger = logging.getLogger(__name__)

# Files matching these patterns are considered more sensitive
SENSITIVE_PATTERNS = [
    "auth", "security", "password", "secret", "token", "jwt", "oauth",
    "payment", "billing", "crypto", "encrypt", "config", "env", "migration",
    "database", "schema", "seed",
]

# These extensions are typically code files worth tracking
CODE_EXTENSIONS = {
    "py", "ts", "tsx", "js", "jsx", "go", "rs", "java", "cs", "cpp", "c",
    "rb", "php", "swift", "kt", "scala", "ex", "exs",
}


class HotspotAnalyzer:
    """
    Scores files by churn and computes risk labels.
    
    Risk score formula (0.0–1.0):
      - 40% change frequency (normalised against max)
      - 20% author spread (more authors = higher risk)
      - 20% churn ratio (deletions / total lines)
      - 20% sensitivity bonus (auth, payments, config, etc.)
    """

    def __init__(self, file_changes: List[Dict]):
        self._files = file_changes

    def score_and_label(self) -> List[Dict]:
        """
        Returns the file_changes list enriched with:
          risk_score (float 0–1)
          risk_label (low / medium / high)
          risk_reason (human-readable explanation)
        """
        if not self._files:
            return []

        # Normalise change_count
        max_changes = max((f.get("change_count", 0) for f in self._files), default=1)
        max_authors = max((f.get("unique_authors", 0) for f in self._files), default=1)

        scored = []
        for fc in self._files:
            score, reason = self._score_file(fc, max_changes, max_authors)
            label = self._label(score)
            scored.append({
                **fc,
                "risk_score": round(score, 3),
                "risk_label": label,
                "risk_reason": reason,
            })

        # Sort by risk_score descending
        scored.sort(key=lambda x: x["risk_score"], reverse=True)
        return scored

    def hotspot_score(self, scored_files: List[Dict]) -> float:
        """
        Returns a 0–100 score representing how healthy the codebase
        hotspot distribution is.
        High = few concentrated hotspots (good).
        Low  = many high-risk files (bad).
        """
        if not scored_files:
            return 80.0

        high_risk = sum(1 for f in scored_files if f["risk_label"] == "high")
        total = len(scored_files)
        high_ratio = high_risk / total

        # penalty curve: 0% high → 90, 20% high → 60, 50%+ → 20
        score = 90.0 - (high_ratio * 140.0)
        return round(max(10.0, min(90.0, score)), 1)

    # ── Private helpers ───────────────────────────────────────

    def _score_file(
        self, fc: Dict, max_changes: int, max_authors: int
    ) -> tuple:
        filepath = fc.get("filepath", "").lower()
        filename = fc.get("filename", "").lower()
        extension = fc.get("extension", "").lower()
        change_count = fc.get("change_count", 0)
        unique_authors = fc.get("unique_authors", 0)
        insertions = fc.get("insertions", 0)
        deletions = fc.get("deletions", 0)

        reasons = []

        # ── 1. Frequency component (0–0.4) ───────────────────
        freq = (change_count / max(max_changes, 1)) * 0.4
        if change_count > max_changes * 0.6:
            reasons.append(f"Changed {change_count}× (very frequent)")
        elif change_count > max_changes * 0.3:
            reasons.append(f"Changed {change_count}× (frequent)")

        # ── 2. Author spread component (0–0.2) ───────────────
        author_component = (unique_authors / max(max_authors, 1)) * 0.2
        if unique_authors >= 5:
            reasons.append(f"{unique_authors} different authors")

        # ── 3. Churn ratio component (0–0.2) ─────────────────
        total_lines = insertions + deletions
        churn_ratio = deletions / max(total_lines, 1)
        churn_component = churn_ratio * 0.2
        if churn_ratio > 0.5:
            reasons.append("High line deletion ratio")

        # ── 4. Sensitivity bonus (0–0.2) ─────────────────────
        sensitivity = 0.0
        for pattern in SENSITIVE_PATTERNS:
            if pattern in filepath or pattern in filename:
                sensitivity = 0.2
                reasons.append(f"Security-sensitive path ({pattern})")
                break

        # Only code files get scored — binary/lock files get near-zero
        if extension not in CODE_EXTENSIONS and extension not in ("yaml", "yml", "json", "toml", "env"):
            freq *= 0.3
            author_component *= 0.3
            churn_component *= 0.3
            sensitivity *= 0.3

        score = freq + author_component + churn_component + sensitivity
        reason = "; ".join(reasons) if reasons else "Normal activity level"
        return min(score, 1.0), reason

    @staticmethod
    def _label(score: float) -> str:
        if score >= 0.55:
            return "high"
        elif score >= 0.30:
            return "medium"
        return "low"
