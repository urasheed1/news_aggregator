from flask import Blueprint, render_template, jsonify
import requests
from transformers import pipeline

main = Blueprint('main', __name__)

# Initialize Hugging Face pipelines
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
classifier = pipeline("zero-shot-classification")

@main.route('/')
def index():
    news = get_all_news()
    categorized_news = categorize_news(news)
    analyzed_news = analyze_sentiment(categorized_news)
    filter_removed_articles(analyzed_news)
    # Enforce a limit on the 'others' category
    limit_others_size(analyzed_news)
    return render_template('index.html', news=analyzed_news)

@main.route('/api/news')
def api_news():
    news = get_all_news()
    categorized_news = categorize_news(news)
    analyzed_news = analyze_sentiment(categorized_news)
    filter_removed_articles(analyzed_news)
    limit_others_size(analyzed_news)
    return jsonify(analyzed_news)

def get_news_by_category(category):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'category': category,
        'apiKey': 'f2e85a990df44c5fa9cb0110bdd6e807'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return [
            {
                'title': article['title'],
                'link': article['url'],
                'source': article['source']['name']
            }
            for article in articles
        ]
    else:
        return []

def get_all_news():
    categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
    news = {category: get_news_by_category(category) for category in categories}
    return news

def categorize_news(news):
    # Our known categories for zero-shot classification
    categories = ['sports', 'politics', 'technology', 'health', 'entertainment', 'business', 'science']
    categorized_news = {category: [] for category in categories}
    categorized_news['others'] = []

    # Source-based categorization
    source_to_category = {
        'ESPN': 'sports',
        'CBS Sports': 'sports',
        'NBC Sports': 'sports',
        'The Athletic': 'sports',
        'DallasCowboys.com': 'sports',
        'DetroitLions.com': 'sports',
        'TechCrunch': 'technology',
        'Bloomberg': None,
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
            # Step 1: Source-based categorization
            source_category = source_to_category.get(article['source'], None)
            if source_category:
                categorized_news[source_category].append(article)
                added = True

            # Step 2: Zero-shot classification fallback
            if not added:
                try:
                    result = classifier(article['title'], candidate_labels=categories, multi_label=False)
                    best_category = result['labels'][0]
                    # Always trust the top classification result
                    categorized_news[best_category].append(article)
                    added = True
                except Exception as e:
                    article['category_error'] = str(e)
                    categorized_news['others'].append(article)
                    added = True

            if not added:
                categorized_news['others'].append(article)

    return categorized_news

def analyze_sentiment(news):
    seen_articles = set()  # Avoid duplicates
    for category, articles in news.items():
        unique_articles = []
        for article in articles:
            if article['title'] not in seen_articles:
                try:
                    result = sentiment_analyzer(article['title'])[0]
                    article['sentiment'] = result['label'].lower()  # 'positive' or 'negative'
                    article['confidence'] = round(result['score'], 2)
                except Exception:
                    article['sentiment'] = 'neutral'
                    article['confidence'] = 0.0

                unique_articles.append(article)
                seen_articles.add(article['title'])
        news[category] = unique_articles
    return news

def filter_removed_articles(news):
    """
    Remove any articles that contain '[Removed]' in title or link so they don't show up at all.
    """
    for category in list(news.keys()):
        filtered = []
        for article in news[category]:
            if '[Removed]' not in article['title'] and '[Removed]' not in str(article['link']):
                filtered.append(article)
        news[category] = filtered

def limit_others_size(news):
    """
    If 'others' category is larger than the largest of the named categories, reassign the excess.
    """
    # Find the max size among named categories
    named_categories = [cat for cat in news.keys() if cat != 'others']
    if not named_categories:
        return  # No named categories, nothing to do

    max_len = max(len(news[cat]) for cat in named_categories)
    others_count = len(news['others'])

    # If 'others' is already within limit, we're good.
    if others_count <= max_len:
        return

    # Otherwise, reassign the excess articles out of 'others'
    excess_count = others_count - max_len
    if excess_count <= 0:
        return

    # Take the "excess" subset from the end of 'others'
    excess_articles = news['others'][-excess_count:]
    news['others'] = news['others'][:-excess_count]

    # Attempt to reclassify these excess articles among the named categories
    for article in excess_articles:
        try:
            result = classifier(article['title'], candidate_labels=named_categories, multi_label=False)
            best_category = result['labels'][0]
            news[best_category].append(article)
        except Exception:
            # If classification fails, keep them in 'others' anyway
            news['others'].append(article)
