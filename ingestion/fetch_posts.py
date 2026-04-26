"""Functions for fetching stories from Hacker News."""

from typing import List, Dict, Any
from ingestion.hn_client import get_top_story_ids, get_story_by_id


def fetch_top_stories(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch top stories from Hacker News.

    Args:
        limit: Maximum number of stories to retrieve.

    Returns:
        List of story dictionaries.
    """
    story_ids = get_top_story_ids()[:limit]
    stories = []
    for story_id in story_ids:
        story = get_story_by_id(story_id)
        if story and story.get("type") == "story":
            stories.append(story)
    return stories
