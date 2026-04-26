"""Tests for HN data fetching."""

import pytest
from unittest.mock import patch, MagicMock
from ingestion.fetch_posts import fetch_top_stories


def test_fetch_top_stories_returns_list():
    """Test that fetch_top_stories returns a list of stories."""
    # Mock the HN client responses
    with patch("ingestion.fetch_posts.get_top_story_ids") as mock_ids, \
         patch("ingestion.fetch_posts.get_story_by_id") as mock_story:
        
        mock_ids.return_value = [1, 2, 3]
        mock_story.return_value = {"id": 1, "title": "Test", "by": "user", "score": 10}
        
        result = fetch_top_stories(limit=3)
        
        assert isinstance(result, list)
        assert len(result) == 3
