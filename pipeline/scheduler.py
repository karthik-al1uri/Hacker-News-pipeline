"""Pipeline scheduler using APScheduler."""

from apscheduler.schedulers.blocking import BlockingScheduler
import logging

from ingestion.fetch_posts import fetch_top_stories
from transformation.clean import clean_story, deduplicate
from transformation.sentiment import score_sentiment
from storage.db import SessionLocal
from storage.models import Story

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Execute a single end-to-end pipeline run: fetch, clean, score, store.

    Returns:
        None
    """
    logger.info("Starting pipeline run...")
    
    # Fetch raw stories
    raw_stories = fetch_top_stories(limit=100)
    logger.info(f"Fetched {len(raw_stories)} raw stories")
    
    # Clean stories
    cleaned = [clean_story(s) for s in raw_stories]
    cleaned = [s for s in cleaned if s is not None]  # Remove None values
    logger.info(f"Cleaned to {len(cleaned)} stories")
    
    # Deduplicate
    unique_stories = deduplicate(cleaned)
    logger.info(f"Deduplicated to {len(unique_stories)} stories")
    
    # Score sentiment and save to DB
    db = SessionLocal()
    try:
        saved_count = 0
        for story_data in unique_stories:
            # Check if story already exists
            existing = db.query(Story).filter(Story.id == story_data["id"]).first()
            if existing:
                continue
            
            # Score sentiment
            sentiment = score_sentiment(story_data["title"])
            
            # Create Story object
            story = Story(
                id=story_data["id"],
                title=story_data["title"],
                author=story_data["author"],
                score=story_data["score"],
                num_comments=story_data["num_comments"],
                url=story_data["url"],
                story_type=story_data["story_type"],
                created_at=story_data["created_at"],
                sentiment_score=sentiment,
            )
            db.add(story)
            saved_count += 1
        
        db.commit()
        logger.info(f"Saved {saved_count} new stories to database")
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, "interval", minutes=15)
    logger.info("Starting scheduler - running every 15 minutes")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
