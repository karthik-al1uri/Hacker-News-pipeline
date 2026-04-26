"""SQLAlchemy ORM models for the Hacker News trend pipeline."""

from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from sqlalchemy.sql import func
from storage.db import Base


class Story(Base):
    """ORM model representing a Hacker News story."""

    __tablename__ = "stories"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    num_comments = Column(Integer, nullable=False, default=0)
    url = Column(String)
    sentiment_score = Column(Float)
    story_type = Column(String, nullable=False, default="story")
    created_at = Column(BigInteger, nullable=False)  # Unix timestamp
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
