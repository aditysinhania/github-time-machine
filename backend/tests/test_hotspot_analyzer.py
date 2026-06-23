from analytics.hotspot_analyzer import HotspotAnalyzer


def test_score_and_label_returns_all_files(sample_file_changes):
    analyzer = HotspotAnalyzer(sample_file_changes)
    scored = analyzer.score_and_label()
    assert len(scored) == len(sample_file_changes)


def test_score_and_label_sorted_descending(sample_file_changes):
    analyzer = HotspotAnalyzer(sample_file_changes)
    scored = analyzer.score_and_label()

    scores = [f["risk_score"] for f in scored]
    assert scores == sorted(scores, reverse=True)


def test_score_in_valid_range(sample_file_changes):
    analyzer = HotspotAnalyzer(sample_file_changes)
    scored = analyzer.score_and_label()

    for f in scored:
        assert 0.0 <= f["risk_score"] <= 1.0


def test_risk_labels_are_valid(sample_file_changes):
    analyzer = HotspotAnalyzer(sample_file_changes)
    scored = analyzer.score_and_label()

    for f in scored:
        assert f["risk_label"] in ("high", "medium", "low")


def test_payments_file_flagged_as_sensitive(sample_file_changes):
    """charge.py lives under src/payments — should trigger sensitivity bonus."""
    analyzer = HotspotAnalyzer(sample_file_changes)
    scored = analyzer.score_and_label()

    payments_file = next(f for f in scored if "payments" in f["filepath"])
    assert "sensitive" in payments_file["risk_reason"].lower() or "payment" in payments_file["risk_reason"].lower()


def test_empty_file_list():
    analyzer = HotspotAnalyzer([])
    assert analyzer.score_and_label() == []


def test_hotspot_score_in_range(sample_file_changes):
    analyzer = HotspotAnalyzer(sample_file_changes)
    scored = analyzer.score_and_label()
    score = analyzer.hotspot_score(scored)
    assert 10.0 <= score <= 90.0


def test_hotspot_score_default_for_empty():
    analyzer = HotspotAnalyzer([])
    score = analyzer.hotspot_score([])
    assert score == 80.0
