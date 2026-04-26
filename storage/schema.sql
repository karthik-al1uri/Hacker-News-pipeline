-- Schema for the Hacker News Trend Pipeline database

CREATE TABLE IF NOT EXISTS stories (
    id              INTEGER PRIMARY KEY,
    title           VARCHAR(512) NOT NULL,
    author          VARCHAR(128) NOT NULL,
    score           INTEGER NOT NULL,
    num_comments    INTEGER NOT NULL DEFAULT 0,
    url             VARCHAR(1024),
    sentiment_score FLOAT,
    story_type      VARCHAR(32) NOT NULL DEFAULT 'story',
    created_at      BIGINT NOT NULL,
    ingested_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
