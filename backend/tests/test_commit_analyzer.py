from analytics.commit_analyzer import CommitAnalyzer


def test_timeline_month_buckets_sum_to_total(sample_commits):
    analyzer = CommitAnalyzer(sample_commits)
    buckets = analyzer.timeline("month")

    total_commits_in_buckets = sum(b["commits"] for b in buckets)
    assert total_commits_in_buckets == len(sample_commits)


def test_timeline_returns_sorted_periods(sample_commits):
    analyzer = CommitAnalyzer(sample_commits)
    buckets = analyzer.timeline("month")

    periods = [b["period"] for b in buckets]
    assert periods == sorted(periods)


def test_timeline_empty_commits_returns_empty_list():
    analyzer = CommitAnalyzer([])
    assert analyzer.timeline("month") == []


def test_summary_stats_basic_fields(sample_commits):
    analyzer = CommitAnalyzer(sample_commits)
    stats = analyzer.summary_stats()

    assert stats["total_commits"] == len(sample_commits)
    assert stats["first_commit_at"] is not None
    assert stats["last_commit_at"] is not None
    assert stats["age_days"] >= 0


def test_summary_stats_empty_commits():
    analyzer = CommitAnalyzer([])
    stats = analyzer.summary_stats()

    assert stats["total_commits"] == 0
    assert stats["first_commit_at"] is None


def test_milestones_capped_at_twenty(sample_commits):
    analyzer = CommitAnalyzer(sample_commits)
    milestones = analyzer.milestones()
    assert len(milestones) <= 20


def test_milestones_chronologically_sorted(sample_commits):
    analyzer = CommitAnalyzer(sample_commits)
    milestones = analyzer.milestones()

    years_months = [(m["year"], m["month"]) for m in milestones]
    assert years_months == sorted(years_months)
