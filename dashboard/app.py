"""Professional Hacker News Trend Dashboard.

A minimalistic, interactive dashboard for visualizing Hacker News trends.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter
import re
from datetime import datetime, timedelta

from storage.db import SessionLocal
from storage.models import Story

# Page configuration
st.set_page_config(
    page_title="HN Trends",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimalistic design
st.markdown("""
<style>
    /* Minimalist typography */
    .main-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .subtitle {
        font-size: 1rem;
        color: #666;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
    }
    .metric-label {
        font-size: 0.875rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Data table styling */
    .story-title {
        font-weight: 500;
        color: #1a1a1a;
    }
    .story-meta {
        font-size: 0.875rem;
        color: #666;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)


def load_data(hours: int = 24) -> pd.DataFrame:
    """Load stories from database."""
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


def extract_keywords(titles: pd.Series, n: int = 15) -> pd.DataFrame:
    """Extract top N keywords from titles."""
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
                 "hn", "new", "how", "why", "hn", "ask", "tell", "using",
                 "use", "used", "vs", "one", "two", "first", "more", "most",
                 "some", "many", "all", "any", "each", "every", "other",
                 "such", "only", "own", "same", "few", "much", "than",
                 "then", "now", "here", "there", "when", "where", "why",
                 "how", "all", "any", "both", "each", "few", "more",
                 "most", "other", "some", "such", "no", "nor", "not"}
    
    words = []
    for title in titles:
        found = re.findall(r'\b[a-zA-Z]{3,}\b', str(title).lower())
        words.extend([w for w in found if w not in stopwords and len(w) > 2])
    
    counter = Counter(words)
    top = counter.most_common(n)
    return pd.DataFrame(top, columns=["keyword", "count"])


def render_header():
    """Render minimalist header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-title">📊 HN Trends</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Real-time insights from Hacker News</p>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align: right; color: #666; font-size: 0.875rem;">
            <div>Last updated</div>
            <div style="font-weight: 600; color: #1a1a1a;">{datetime.now().strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)


def render_metrics(df: pd.DataFrame):
    """Render metric cards with animation."""
    if df.empty:
        return
    
    cols = st.columns(4)
    
    metrics = [
        ("STORIES", len(df), "📰"),
        ("AVG SCORE", f"{df['score'].mean():.0f}", "⭐"),
        ("SENTIMENT", f"{df['sentiment_score'].mean():.3f}", "😊"),
        ("COMMENTS", f"{df['num_comments'].sum():,}", "💬"),
    ]
    
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 1.25rem;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 0.75rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.05em;">
                    {label}
                </div>
                <div style="font-size: 1.75rem; font-weight: 600; margin-top: 0.25rem;">
                    {value}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_interactive_filters():
    """Render interactive filter bar."""
    with st.expander("🔍 Filters & Search", expanded=False):
        cols = st.columns([2, 2, 2, 1])
        
        with cols[0]:
            hours = st.select_slider(
                "Time Range",
                options=[1, 6, 12, 24, 48, 72],
                value=24,
                format_func=lambda x: f"{x}h"
            )
        
        with cols[1]:
            min_score = st.slider("Min Score", 0, 500, 0, step=10)
        
        with cols[2]:
            sort_by = st.selectbox(
                "Sort By",
                ["Score", "Comments", "Newest", "Sentiment"],
                index=0
            )
        
        with cols[3]:
            search = st.text_input("🔎 Search titles", "")
    
    return hours, min_score, sort_by, search


def render_keyword_chart(df: pd.DataFrame):
    """Render interactive keyword treemap."""
    if df.empty:
        st.info("No data available")
        return
    
    keywords_df = extract_keywords(df["title"], n=20)
    if keywords_df.empty:
        st.info("No keywords found")
        return
    
    # Create treemap for better interactivity
    fig = px.treemap(
        keywords_df,
        path=["keyword"],
        values="count",
        color="count",
        color_continuous_scale="Viridis",
        title=None,
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Mentions: %{value}<extra></extra>',
        textfont=dict(size=14, family="Inter, sans-serif"),
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        height=400,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_sentiment_gauge(df: pd.DataFrame):
    """Render sentiment gauge chart."""
    if df.empty or df["sentiment_score"].isna().all():
        st.info("No sentiment data")
        return
    
    avg_sentiment = df["sentiment_score"].mean()
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_sentiment,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'size': 40, 'family': 'Inter'}, 'valueformat': '.3f'},
        gauge={
            'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "#666"},
            'bar': {'color': "#667eea", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#ccc",
            'steps': [
                {'range': [-1, -0.3], 'color': '#ff6b6b'},
                {'range': [-0.3, 0.3], 'color': '#ffd93d'},
                {'range': [0.3, 1], 'color': '#6bcf7f'},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': avg_sentiment
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'}
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_activity_heatmap(df: pd.DataFrame):
    """Render activity heatmap by hour and day."""
    if df.empty:
        return
    
    df['hour'] = df['created_at'].dt.hour
    df['day'] = df['created_at'].dt.day_name()
    
    pivot = df.groupby(['day', 'hour']).size().reset_index(name='count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot['day'] = pd.Categorical(pivot['day'], categories=days_order, ordered=True)
    pivot = pivot.sort_values('day')
    
    fig = px.density_heatmap(
        pivot,
        x='hour',
        y='day',
        z='count',
        color_continuous_scale='Blues',
        title=None,
        labels={'hour': 'Hour of Day', 'day': '', 'count': 'Stories'}
    )
    
    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder': 'array', 'categoryarray': days_order[::-1]},
        xaxis={'tickmode': 'linear', 'dtick': 3}
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_top_stories_table(df: pd.DataFrame, search: str = ""):
    """Render interactive top stories table."""
    if df.empty:
        return
    
    # Filter by search
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False)]
    
    if df.empty:
        st.info("No stories match your search")
        return
    
    # Sort by score descending
    df_display = df.nlargest(15, 'score')[['title', 'score', 'num_comments', 'sentiment_score', 'author', 'url']]
    
    st.markdown("### Top Stories")
    
    for idx, row in df_display.iterrows():
        sentiment_emoji = "😊" if row['sentiment_score'] > 0.2 else "😐" if row['sentiment_score'] > -0.2 else "😔"
        
        with st.container():
            cols = st.columns([6, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"**{row['title']}**  
<small style='color: #666;'>by {row['author']}</small>", unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"⭐ **{row['score']}**")
            
            with cols[2]:
                st.markdown(f"💬 **{row['num_comments']}**")
            
            with cols[3]:
                st.markdown(f"{sentiment_emoji} `{row['sentiment_score']:.2f}`")
            
            if row['url']:
                st.markdown(f"<small style='color: #667eea;'>🔗 {row['url'][:60]}...</small>", unsafe_allow_html=True)
            
            st.divider()


def main():
    """Main dashboard entry point."""
    render_header()
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Run: `python pipeline/scheduler.py`")
        return
    
    # Render metrics
    render_metrics(df)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interactive filters
    hours, min_score, sort_by, search = render_interactive_filters()
    
    # Apply filters
    df_filtered = df[df['score'] >= min_score].copy()
    
    if sort_by == "Score":
        df_filtered = df_filtered.sort_values('score', ascending=False)
    elif sort_by == "Comments":
        df_filtered = df_filtered.sort_values('num_comments', ascending=False)
    elif sort_by == "Newest":
        df_filtered = df_filtered.sort_values('created_at', ascending=False)
    elif sort_by == "Sentiment":
        df_filtered = df_filtered.sort_values('sentiment_score', ascending=False)
    
    # Main layout
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Top row: Keywords and Sentiment
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Trending Topics")
        render_keyword_chart(df_filtered)
    
    with col2:
        st.markdown("### Community Mood")
        render_sentiment_gauge(df_filtered)
    
    # Second row: Activity heatmap
    st.markdown("### Activity Patterns")
    render_activity_heatmap(df_filtered)
    
    # Stories table
    st.markdown("<br>", unsafe_allow_html=True)
    render_top_stories_table(df_filtered, search)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #999; font-size: 0.875rem;">
        HN Trends • Data updates every 15 minutes • Built with Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
