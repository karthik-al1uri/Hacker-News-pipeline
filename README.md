# Hacker News Trend Pipeline

An end-to-end data engineering pipeline that ingests live Hacker News stories every 15 minutes, transforms and scores sentiment, stores in PostgreSQL, and visualizes trends on a live Streamlit dashboard.

## Overview

This project demonstrates a complete real-time data pipeline architecture using entirely free tools and APIs. The Hacker News Firebase API requires no authentication, making it perfect for educational data engineering projects. The pipeline pulls story data, performs sentiment analysis using VADER, and provides insights into trending topics and community mood.

## Architecture

```
                    ┌─────────────────┐
                    │   HN Firebase   │
                    │     API         │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Ingestion     │
                    │   (requests)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Transformation │
                    │  (clean + VADER)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (SQLAlchemy)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Streamlit     │
                    │   Dashboard     │
                    └─────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Ingestion | requests | Fetch data from HN Firebase API |
| Transformation | Python functions | Normalize fields, deduplicate |
| Sentiment Analysis | VADER | Score story title sentiment |
| Storage | PostgreSQL + SQLAlchemy | Persist structured story data |
| Orchestration | APScheduler | Run pipeline every 15 minutes |
| Visualization | Streamlit + Plotly | Interactive dashboard |
| Containerization | Docker Compose | Run entire stack locally |

## Features

- Pulls top 100 HN stories every 15 minutes via the free Firebase API
- Cleans and deduplicates stories before storage
- VADER sentiment scoring on story titles
- PostgreSQL storage with SQLAlchemy ORM
- Live Streamlit dashboard with trending keywords, sentiment over time, peak hours
- Fully containerized with Docker Compose

## Project Structure

```
hacker-news-trend-pipeline/
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
├── requirements.txt
├── ingestion/
│   ├── __init__.py
│   ├── hn_client.py            # HN Firebase API client (requests/httpx)
│   └── fetch_posts.py          # Fetch top/new stories, return raw dicts
├── transformation/
│   ├── __init__.py
│   ├── clean.py                # Normalize fields, remove nulls, deduplicate
│   └── sentiment.py            # Score titles with VADER
├── storage/
│   ├── __init__.py
│   ├── db.py                   # SQLAlchemy engine + session setup
│   ├── models.py               # ORM model: Story table
│   └── schema.sql              # Raw SQL schema as reference
├── pipeline/
│   ├── __init__.py
│   └── scheduler.py            # APScheduler job: ingest → clean → store every 15 min
├── dashboard/
│   ├── __init__.py
│   └── app.py                  # Streamlit app with 3 charts
├── tests/
│   ├── test_clean.py
│   └── test_fetch.py
└── notebooks/
    └── exploration.ipynb
```

## Getting Started

### Prerequisites

- Docker + Docker Compose
- Python 3.11+

### Installation

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values (only need `DB_URL`)
3. Run `docker-compose up --build` to start PostgreSQL and the scheduler
4. In a separate terminal, run `streamlit run dashboard/app.py` to view the dashboard

## Dashboard

The Streamlit dashboard provides three key visualizations:

1. **Top 10 Trending Keywords** — Bar chart showing most frequent words in story titles
2. **Sentiment Over Time** — Line chart tracking average VADER sentiment score trends
3. **Peak Activity Hours** — Bar chart showing when stories are most frequently posted

## License

MIT
