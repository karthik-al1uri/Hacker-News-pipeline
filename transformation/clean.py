"""Data cleaning and deduplication utilities."""

from typing import List, Dict, Any


def clean_story(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and clean a raw HN story dictionary.

    Args:
        raw: Raw story data from the API.

    Returns:
        Cleaned story dictionary with normalized fields.
    """
    if not raw or raw.get("type") != "story":
        return None
    
    return {
        "id": raw.get("id"),
        "title": raw.get("title", "").strip(),
        "author": raw.get("by", "").strip(),
        "score": raw.get("score", 0) or 0,
        "num_comments": raw.get("descendants", 0) or 0,
        "url": raw.get("url", ""),
        "story_type": raw.get("type", "story"),
        "created_at": raw.get("time", 0),
    }


def deduplicate(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate stories based on story ID.

    Args:
        stories: List of story dictionaries.

    Returns:
        Deduplicated list of stories.
    """
    seen = set()
    unique = []
    for story in stories:
        if story and story.get("id") and story["id"] not in seen:
            seen.add(story["id"])
            unique.append(story)
    return unique
