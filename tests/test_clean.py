"""Tests for data cleaning utilities."""

import pytest
from transformation.clean import clean_story


def test_clean_story_returns_expected_keys():
    """Test that clean_story returns a dict with expected keys."""
    raw = {
        "id": 12345,
        "title": "Test Story",
        "by": "testuser",
        "score": 100,
        "descendants": 50,
        "url": "https://example.com",
        "type": "story",
        "time": 1234567890,
    }
    result = clean_story(raw)
    expected_keys = {"id", "title", "author", "score", "num_comments", "url", "story_type", "created_at"}
    assert set(result.keys()) == expected_keys
