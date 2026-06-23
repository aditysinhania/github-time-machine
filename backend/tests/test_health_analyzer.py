from analytics.health_analyzer import HealthAnalyzer


def test_perfect_scores_yield_grade_a():
    analyzer = HealthAnalyzer(100, 100, 100, 100)
    result = analyzer.compute()
    assert result["health_score"] == 100.0
    assert result["grade"] == "A"


def test_zero_scores_yield_grade_f():
    analyzer = HealthAnalyzer(0, 0, 0, 0)
    result = analyzer.compute()
    assert result["health_score"] == 0.0
    assert result["grade"] == "F"


def test_weights_sum_correctly():
    # bus_factor=80(*0.30) + consistency=80(*0.25) + diversity=80(*0.25) + hotspot=80(*0.20) = 80
    analyzer = HealthAnalyzer(80, 80, 80, 80)
    result = analyzer.compute()
    assert result["health_score"] == 80.0
    assert result["grade"] == "B"


def test_breakdown_has_four_dimensions():
    analyzer = HealthAnalyzer(70, 60, 50, 40)
    result = analyzer.compute()
    assert len(result["breakdown"]) == 4
    labels = {b["label"] for b in result["breakdown"]}
    assert labels == {"Bus Factor", "Commit Consistency", "Contributor Diversity", "Hotspot Stability"}


def test_scores_clamped_above_100():
    analyzer = HealthAnalyzer(150, 200, 999, 100)
    result = analyzer.compute()
    assert result["health_score"] == 100.0


def test_scores_clamped_below_zero():
    analyzer = HealthAnalyzer(-50, -10, 0, 0)
    result = analyzer.compute()
    assert result["health_score"] == 0.0


def test_summary_is_nonempty_string():
    analyzer = HealthAnalyzer(85, 85, 85, 85)
    result = analyzer.compute()
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


def test_grade_boundaries():
    cases = [
        (95, "A"),
        (85, "B"),
        (70, "C"),
        (55, "D"),
        (30, "F"),
    ]
    for score, expected_grade in cases:
        analyzer = HealthAnalyzer(score, score, score, score)
        result = analyzer.compute()
        assert result["grade"] == expected_grade, f"score={score} expected={expected_grade} got={result['grade']}"
