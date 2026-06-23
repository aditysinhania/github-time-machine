import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


SCORE_WEIGHTS = {
    "bus_factor":   0.30,   # Knowledge concentration risk
    "consistency":  0.25,   # Regularity of development activity
    "diversity":    0.25,   # Evenness of contribution spread
    "hotspot":      0.20,   # Codebase stability (inverse of hotspot concentration)
}

GRADE_THRESHOLDS = [
    (90, "A"),
    (80, "B"),
    (65, "C"),
    (50, "D"),
    (0,  "F"),
]


class HealthAnalyzer:
    """
    Computes a composite 0–100 health score from four sub-dimensions.
    Each sub-score is independently clamped to [0, 100].
    """

    def __init__(
        self,
        bus_factor_score: float,
        consistency_score: float,
        diversity_score: float,
        hotspot_score: float,
    ):
        self.scores = {
            "bus_factor":   max(0.0, min(100.0, bus_factor_score)),
            "consistency":  max(0.0, min(100.0, consistency_score)),
            "diversity":    max(0.0, min(100.0, diversity_score)),
            "hotspot":      max(0.0, min(100.0, hotspot_score)),
        }

    def compute(self) -> Dict:
        """
        Returns a dict with:
          health_score  float  composite weighted score
          grade         str    A / B / C / D / F
          breakdown     list   per-dimension details
          summary       str    one-sentence plain-English summary
        """
        health_score = sum(
            self.scores[key] * weight
            for key, weight in SCORE_WEIGHTS.items()
        )
        health_score = round(health_score, 1)
        grade = self._grade(health_score)

        breakdown = [
            {
                "label": "Bus Factor",
                "score": self.scores["bus_factor"],
                "weight": SCORE_WEIGHTS["bus_factor"],
                "description": self._bus_description(self.scores["bus_factor"]),
            },
            {
                "label": "Commit Consistency",
                "score": self.scores["consistency"],
                "weight": SCORE_WEIGHTS["consistency"],
                "description": self._consistency_description(self.scores["consistency"]),
            },
            {
                "label": "Contributor Diversity",
                "score": self.scores["diversity"],
                "weight": SCORE_WEIGHTS["diversity"],
                "description": self._diversity_description(self.scores["diversity"]),
            },
            {
                "label": "Hotspot Stability",
                "score": self.scores["hotspot"],
                "weight": SCORE_WEIGHTS["hotspot"],
                "description": self._hotspot_description(self.scores["hotspot"]),
            },
        ]

        summary = self._summary(health_score, grade)

        return {
            "health_score": health_score,
            "grade": grade,
            "breakdown": breakdown,
            "summary": summary,
        }

    # ── Grade helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _grade(score: float) -> str:
        for threshold, grade in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"

    # ── Description helpers ────────────────────────────────────────────────────

    @staticmethod
    def _bus_description(score: float) -> str:
        if score >= 80:
            return "Knowledge is well distributed across the team."
        elif score >= 55:
            return "A few key contributors hold significant knowledge — moderate risk."
        return "Critical knowledge concentrated in 1–2 people — high bus factor risk."

    @staticmethod
    def _consistency_description(score: float) -> str:
        if score >= 75:
            return "Commit activity is regular and predictable."
        elif score >= 50:
            return "Some irregularity in commit cadence — possibly sprint-based."
        return "Highly irregular commit patterns — bursts followed by silence."

    @staticmethod
    def _diversity_description(score: float) -> str:
        if score >= 75:
            return "Contributions are spread evenly across the team."
        elif score >= 45:
            return "Moderate contributor diversity with some concentration."
        return "Very few contributors dominate the codebase."

    @staticmethod
    def _hotspot_description(score: float) -> str:
        if score >= 75:
            return "Few concentrated hotspots — codebase is relatively stable."
        elif score >= 50:
            return "Several files show elevated churn — worth monitoring."
        return "Many high-risk hotspots detected — technical debt accumulating."

    @staticmethod
    def _summary(score: float, grade: str) -> str:
        if grade == "A":
            return (
                f"Excellent repository health ({score}/100). "
                "Well-distributed knowledge, consistent activity, and stable codebase."
            )
        elif grade == "B":
            return (
                f"Good repository health ({score}/100). "
                "Minor concerns worth addressing but overall in solid shape."
            )
        elif grade == "C":
            return (
                f"Average repository health ({score}/100). "
                "Several risk factors present — action recommended on high-priority items."
            )
        elif grade == "D":
            return (
                f"Below-average repository health ({score}/100). "
                "Significant risks around bus factor or codebase stability."
            )
        return (
            f"Poor repository health ({score}/100). "
            "Critical issues detected — immediate attention required."
        )
