"""VADER sentiment analysis for story titles."""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize analyzer once at module level
_analyzer = SentimentIntensityAnalyzer()


def score_sentiment(text: str) -> float:
    """Score the sentiment of a text using VADER.

    Args:
        text: Text to analyze (e.g., story title).

    Returns:
        Compound sentiment score between -1 (negative) and 1 (positive).
    """
    if not text:
        return 0.0
    scores = _analyzer.polarity_scores(text)
    return scores["compound"]
