"""Streamlit dashboard for visualizing Hacker News trend data."""

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
from datetime import datetime

from storage.db import SessionLocal
from storage.models import Story

st.set_page_config(page_title="Hacker News Trends", layout="wide")


def load_data(hours: int = 24) -> pd.DataFrame:
    """Load stories from database within the last N hours.
    
    Args:
        hours: Number of hours to look back.
        
    Returns:
        DataFrame of stories.
    """
    db = SessionLocal()
    try:
        stories = db.query(Story).all()
        data = [
            {
                "id": s.id,
                "title": s.title,
                "author": s.author,
                "score": s.score,
                "num_comments": s.num_comments,
                "url": s.url,
                "sentiment_score": s.sentiment_score,
                "created_at": datetime.fromtimestamp(s.created_at),
                "ingested_at": s.ingested_at,
            }
            for s in stories
        ]
        return pd.DataFrame(data)
    finally:
        db.close()


def extract_keywords(titles: pd.Series, n: int = 10) -> pd.DataFrame:
    """Extract top N keywords from titles.
    
    Args:
        titles: Series of title strings.
        n: Number of top keywords to return.
        
    Returns:
        DataFrame with keyword counts.
    """
    # Simple word extraction (lowercase, remove common stopwords)
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                 "being", "have", "has", "had", "do", "does", "did", "will",
                 "would", "could", "should", "may", "might", "must", "shall",
                 "can", "need", "dare", "ought", "used", "to", "of", "in",
                 "for", "on", "with", "at", "by", "from", "as", "into",
                 "through", "during", "before", "after", "above", "below",
                 "between", "under", "and", "but", "or", "yet", "so", "if",
                 "because", "although", "though", "while", "where", "when",
                 "that", "which", "who", "whom", "whose", "what", "this",
                 "these", "those", "i", "me", "my", "myself", "we", "our",
                 "you", "your", "he", "him", "his", "she", "her", "it",
                 "its", "they", "them", "their", "s", "t", "on", "re", "show",
                 "hn", "new", "how", "why", "hn", "ask", "tell"}
    
    words = []
    for title in titles:
        # Extract words (2+ characters, alphanumeric)
        found = re.findall(r'\b[a-zA-Z]{2,}\b', str(title).lower())
        words.extend([w for w in found if w not in stopwords])
    
    counter = Counter(words)
    top = counter.most_common(n)
    return pd.DataFrame(top, columns=["keyword", "count"])


def render_keyword_chart(df: pd.DataFrame) -> None:
    """Render bar chart of top 10 trending keywords in titles."""
    if df.empty:
        st.info("No data available. Run the pipeline first!")
        return
    
    keywords_df = extract_keywords(df["title"], n=10)
    if keywords_df.empty:
        st.info("No keywords found.")
        return
    
    fig = px.bar(
        keywords_df,
        x="count",
        y="keyword",
        orientation="h",
        title="Top 10 Trending Keywords",
        labels={"count": "Frequency", "keyword": ""},
        color="count",
        color_continuous_scale="blues",
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_timeline(df: pd.DataFrame) -> None:
    """Render line chart of average sentiment score over time."""
    if df.empty or df["sentiment_score"].isna().all():
        st.info("No sentiment data available.")
        return
    
    # Group by hour and calculate average sentiment
    df["hour"] = df["created_at"].dt.floor("h")
    hourly = df.groupby("hour")["sentiment_score"].mean().reset_index()
    
    fig = px.line(
        hourly,
        x="hour",
        y="sentiment_score",
        title="Average Sentiment Score Over Time",
        labels={"hour": "Time", "sentiment_score": "Avg Sentiment"},
        markers=True,
    )
    fig.update_layout(yaxis=dict(range=[-1, 1]))
    st.plotly_chart(fig, use_container_width=True)


def render_volume_by_hour(df: pd.DataFrame) -> None:
    """Render bar chart of story volume by hour of day."""
    if df.empty:
        st.info("No data available.")
        return
    
    df["hour_of_day"] = df["created_at"].dt.hour
    hourly_counts = df.groupby("hour_of_day").size().reset_index(name="count")
    
    fig = px.bar(
        hourly_counts,
        x="hour_of_day",
        y="count",
        title="Story Volume by Hour of Day",
        labels={"hour_of_day": "Hour (UTC)", "count": "Number of Stories"},
        color="count",
        color_continuous_scale="greens",
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    """Entry point for the Streamlit dashboard."""
    st.title("Hacker News Trend Pipeline")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    hours_back = st.sidebar.slider("Hours to show", 1, 72, 24)
    min_score = st.sidebar.slider("Min story score", 0, 1000, 0)
    
    # Load data
    df = load_data(hours=hours_back)
    
    if not df.empty:
        # Apply score filter
        df = df[df["score"] >= min_score]
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Stories", len(df))
        col2.metric("Avg Score", f"{df['score'].mean():.0f}")
        col3.metric("Avg Sentiment", f"{df['sentiment_score'].mean():.3f}")
        col4.metric("Top Story", f"{df['score'].max()} pts")
        
        st.divider()
    
    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.header("Trending Keywords")
        render_keyword_chart(df)
    
    with col_right:
        st.header("Peak Activity Hours")
        render_volume_by_hour(df)
    
    st.header("Sentiment Over Time")
    render_sentiment_timeline(df)
    
    # Raw data table
    if not df.empty:
        st.divider()
        st.header("Recent Stories")
        st.dataframe(
            df[["title", "score", "sentiment_score", "author", "url"]].sort_values("score", ascending=False).head(10),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
