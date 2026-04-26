"""Extract stories by topic from Hacker News and save to JSON."""

import json
from typing import List, Dict, Any
from ingestion.fetch_posts import fetch_top_stories
from transformation.clean import clean_story

# Define 5 topics to search for
TOPICS = {
    "AI_ML": ["ai", "machine learning", "llm", "gpt", "neural", "artificial intelligence"],
    "Python": ["python", "django", "flask", "fastapi", "pandas"],
    "Security": ["security", "vulnerability", "exploit", "hack", "breach", "cve"],
    "Rust": ["rust", "cargo", "rustlang"],
    "Startups": ["startup", "founder", "venture", "funding", "yc", "y combinator"],
}


def matches_topic(title: str, keywords: List[str]) -> bool:
    """Check if title matches any keyword for a topic."""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in keywords)


def extract_by_topics(limit: int = 500) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch stories and categorize by topic.
    
    Args:
        limit: Number of top stories to fetch.
        
    Returns:
        Dictionary mapping topic names to lists of stories.
    """
    print(f"Fetching top {limit} stories from HN...")
    raw_stories = fetch_top_stories(limit=limit)
    print(f"Fetched {len(raw_stories)} stories")
    
    # Clean stories
    cleaned = [clean_story(s) for s in raw_stories]
    cleaned = [s for s in cleaned if s is not None]
    print(f"Cleaned to {len(cleaned)} valid stories")
    
    # Categorize by topic
    results = {topic: [] for topic in TOPICS}
    
    for story in cleaned:
        title = story.get("title", "")
        for topic, keywords in TOPICS.items():
            if matches_topic(title, keywords):
                results[topic].append(story)
    
    # Print summary
    print("\n" + "="*50)
    print("TOPIC EXTRACTION SUMMARY")
    print("="*50)
    for topic, stories in results.items():
        print(f"{topic:12}: {len(stories):3} stories")
    print("="*50)
    
    return results


def save_to_json(data: Dict[str, List[Dict]], filename: str = "topic_stories.json"):
    """Save extracted stories to JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n✓ Saved to {filename}")


if __name__ == "__main__":
    # Extract stories by topic
    topic_data = extract_by_topics(limit=200)
    
    # Save to JSON
    save_to_json(topic_data)
    
    # Print sample stories for each topic
    print("\n" + "="*50)
    print("SAMPLE STORIES BY TOPIC")
    print("="*50)
    for topic, stories in topic_data.items():
        if stories:
            print(f"\n{topic}:")
            for s in stories[:3]:  # Show top 3
                print(f"  • {s['title'][:60]}... ({s['score']} points)")
