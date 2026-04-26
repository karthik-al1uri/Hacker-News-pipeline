"""Hacker News Firebase API client using requests."""

import requests
from typing import List, Dict, Any

BASE_URL = "https://hacker-news.firebaseio.com/v0"


def get_top_story_ids() -> List[int]:
    """Fetch the current top 500 story IDs from Hacker News.

    Returns:
        List of story ID integers.
    """
    response = requests.get(f"{BASE_URL}/topstories.json")
    response.raise_for_status()
    return response.json()


def get_story_by_id(story_id: int) -> Dict[str, Any]:
    """Fetch a single story's details by its HN ID.

    Args:
        story_id: The Hacker News story ID.

    Returns:
        Dictionary containing story data (title, url, score, etc.).
    """
    response = requests.get(f"{BASE_URL}/item/{story_id}.json")
    response.raise_for_status()
    return response.json()
