from flask import Blueprint, render_template, jsonify
import requests
from transformers import pipeline

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("NEWS_API_KEY")

main = Blueprint('main', __name__)

# Initialize Hugging Face pipelines
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
classifier = pipeline("zero-shot-classification")

@main.route('/')
def index():
    news = get_all_news()
    categorized_news = categorize_news(news)
    analyzed_news = analyze_sentiment(categorized_news)
    # Process '[Removed]' articles to not have hyperlinks
    prepare_removed_articles(analyzed_news)
    return render_template('index.html', news=analyzed_news)

@main.route('/api/news')
def api_news():
    news = get_all_news()
    categorized_news = categorize_news(news)
    analyzed_news = analyze_sentiment(categorized_news)
    prepare_removed_articles(analyzed_news)
    return jsonify(analyzed_news)

def get_news_by_category(category):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'category': category,
        'apiKey': api_key  
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return [{'title': article['title'], 'link': article['url'], 'source': article['source']['name']} for article in articles]
    else:
        return []

def get_all_news():
    categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
    news = {category: get_news_by_category(category) for category in categories}
    return news

def categorize_news(news):
    # Define the categories for zero-shot classification
    categories = ['sports', 'politics', 'technology', 'health', 'entertainment', 'business', 'science']
    categorized_news = {category: [] for category in categories}
    categorized_news['others'] = []

    # Source-based categorization mapping
    source_to_category = {
        'ESPN': 'sports',
        'CBS Sports': 'sports',
        'NBC Sports': 'sports',
        'The Athletic': 'sports',
        'DallasCowboys.com': 'sports',
        'DetroitLions.com': 'sports',
        'TechCrunch': 'technology',
        'Bloomberg': 'business',
        'Yahoo Finance': 'business',
        'Hollywood Reporter': 'entertainment',
        'Healthline': 'health',
        'IGN': 'entertainment',
        'Kotaku': 'entertainment',
        'Space.com': 'science',
        'PsyPost': 'science',
        'BBC': None,
        'CNN': None,
        'Google News': None
    }

    for _, articles in news.items():
        for article in articles:
            added = False
            # Step 1: Attempt source-based categorization
            source_category = source_to_category.get(article['source'], None)
            if source_category:
                categorized_news[source_category].append(article)
                added = True

            # Step 2: If not categorized by source, use zero-shot classification
            if not added:
                try:
                    result = classifier(article['title'], candidate_labels=categories)
                    best_category = result['labels'][0]
                    confidence = result['scores'][0]

                    # Instead of using a high threshold, we simply choose the top category.
                    # This will reduce the size of 'others'.
                    # If you want some threshold, you can pick a lower one (e.g., 0.3).
                    if confidence > 0.3:
                        categorized_news[best_category].append(article)
                        added = True
                    else:
                        # If even the top category confidence is extremely low, fallback to 'others'
                        categorized_news['others'].append(article)
                        added = True

                except Exception as e:
                    # In case classification fails, default to others
                    article['category_error'] = str(e)
                    categorized_news['others'].append(article)
                    added = True

            if not added:
                # Catch-all if not added anywhere
                categorized_news['others'].append(article)

    return categorized_news

def analyze_sentiment(news):
    seen_articles = set()  # Track seen articles to avoid duplicates
    for category, articles in news.items():
        unique_articles = []
        for article in articles:
            if article['title'] not in seen_articles:
                try:
                    # Analyze sentiment using the Hugging Face pipeline
                    result = sentiment_analyzer(article['title'])[0]
                    article['sentiment'] = result['label'].lower()  # 'positive' or 'negative'
                    article['confidence'] = round(result['score'], 2)  # Confidence score
                    unique_articles.append(article)
                    seen_articles.add(article['title'])
                except Exception:
                    # Fallback in case of an error
                    article['sentiment'] = 'neutral'
                    article['confidence'] = 0.0
                    unique_articles.append(article)
                    seen_articles.add(article['title'])
        news[category] = unique_articles
    return news

def prepare_removed_articles(news):
    # If an article is "Removed" or "[Removed]", remove hyperlink
    for category, articles in news.items():
        for article in articles:
            # Check title or link for '[Removed]'
            if '[Removed]' in article['title'] or '[Removed]' in str(article['link']):
                article['link'] = None
