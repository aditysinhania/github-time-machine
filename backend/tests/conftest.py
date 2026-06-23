import sys
import os
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_commits():
    """20 commits spread across 3 authors over 60 days."""
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    authors = [
        ("Alice Dev", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Cara Lee", "cara@example.com"),
    ]
    commits = []
    for i in range(20):
        author_name, author_email = authors[i % len(authors)]
        # Alice gets the lion's share to simulate bus-factor risk
        if i % 3 != 0:
            author_name, author_email = authors[0]

        commits.append({
            "sha": f"sha{i:03d}" + "0" * 34,
            "short_sha": f"sha{i:03d}",
            "message": f"Commit number {i}",
            "message_short": f"Commit number {i}",
            "author_name": author_name,
            "author_email": author_email,
            "committed_at": base + timedelta(days=i * 3),
            "files_changed": 2,
            "insertions": 10 + i,
            "deletions": i,
            "branch": "main",
        })
    return commits


@pytest.fixture
def sample_file_changes():
    return [
        {
            "filepath": "src/auth/login.py",
            "filename": "login.py",
            "extension": "py",
            "directory": "src/auth",
            "change_count": 45,
            "insertions": 300,
            "deletions": 120,
            "unique_authors": 4,
            "top_author": "alice@example.com",
            "top_author_pct": 60.0,
        },
        {
            "filepath": "README.md",
            "filename": "README.md",
            "extension": "md",
            "directory": "",
            "change_count": 5,
            "insertions": 50,
            "deletions": 10,
            "unique_authors": 2,
            "top_author": "bob@example.com",
            "top_author_pct": 80.0,
        },
        {
            "filepath": "src/payments/charge.py",
            "filename": "charge.py",
            "extension": "py",
            "directory": "src/payments",
            "change_count": 30,
            "insertions": 200,
            "deletions": 80,
            "unique_authors": 1,
            "top_author": "alice@example.com",
            "top_author_pct": 100.0,
        },
    ]


@pytest.fixture
def sample_contributors():
    return [
        {"name": "Alice Dev", "email": "alice@example.com", "commit_count": 14, "commit_percentage": 70.0},
        {"name": "Bob Smith", "email": "bob@example.com", "commit_count": 4, "commit_percentage": 20.0},
        {"name": "Cara Lee", "email": "cara@example.com", "commit_count": 2, "commit_percentage": 10.0},
    ]
