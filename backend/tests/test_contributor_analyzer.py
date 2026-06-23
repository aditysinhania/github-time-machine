from analytics.contributor_analyzer import ContributorAnalyzer


def test_bus_factor_single_dominant_contributor(sample_contributors, sample_commits):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    bf = analyzer.bus_factor()
    # Alice alone owns 70% > 50%, so bus factor should be 1
    assert bf == 1


def test_bus_factor_score_in_range(sample_contributors, sample_commits):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    score = analyzer.bus_factor_score()
    assert 0.0 <= score <= 100.0


def test_bus_factor_score_low_for_concentrated_ownership(sample_contributors, sample_commits):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    score = analyzer.bus_factor_score()
    # bus_factor=1 maps to ~34.6 via the log-scale formula — still well
    # below the midpoint, signaling real risk, even though not near zero.
    assert score < 50.0


def test_bus_factor_empty_contributors():
    analyzer = ContributorAnalyzer([], [])
    assert analyzer.bus_factor() == 0
    assert analyzer.bus_factor_score() == 0.0


def test_diversity_score_in_range(sample_contributors, sample_commits):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    score = analyzer.diversity_score()
    assert 0.0 <= score <= 100.0


def test_diversity_score_zero_for_single_contributor():
    contributors = [{"name": "Solo", "email": "solo@x.com", "commit_count": 10, "commit_percentage": 100.0}]
    analyzer = ContributorAnalyzer(contributors, [])
    assert analyzer.diversity_score() == 0.0


def test_diversity_score_high_for_even_distribution():
    contributors = [
        {"name": "A", "email": "a@x.com", "commit_count": 10, "commit_percentage": 33.3},
        {"name": "B", "email": "b@x.com", "commit_count": 10, "commit_percentage": 33.3},
        {"name": "C", "email": "c@x.com", "commit_count": 10, "commit_percentage": 33.3},
    ]
    analyzer = ContributorAnalyzer(contributors, [])
    score = analyzer.diversity_score()
    assert score > 90.0  # near-perfect entropy


def test_consistency_score_in_range(sample_contributors, sample_commits):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    score = analyzer.consistency_score()
    assert 0.0 <= score <= 100.0


def test_module_ownership_groups_by_top_level_dir(sample_contributors, sample_commits, sample_file_changes):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    modules = analyzer.module_ownership(sample_file_changes, sample_commits)

    module_names = {m["module"] for m in modules}
    # src/auth/login.py and src/payments/charge.py both roll up to "src"
    # README.md (directory="") rolls up to "root"
    assert "src" in module_names
    assert "root" in module_names


def test_module_ownership_owners_sorted_by_commit_count(sample_contributors, sample_commits, sample_file_changes):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    modules = analyzer.module_ownership(sample_file_changes, sample_commits)

    for module in modules:
        counts = [o["commit_count"] for o in module["owners"]]
        assert counts == sorted(counts, reverse=True)

def test_module_ownership_empty_inputs(sample_contributors, sample_commits):
    analyzer = ContributorAnalyzer(sample_contributors, sample_commits)
    assert analyzer.module_ownership([], []) == []
