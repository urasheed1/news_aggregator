from flask import Blueprint, render_template, jsonify
import requests
from textblob import TextBlob

main = Blueprint('main', __name__)

@main.route('/')
def index():
    news = get_all_news()
    categorized_news = categorize_news(news)
    analyzed_news = analyze_sentiment(categorized_news)
    return render_template('index.html', news=analyzed_news)

@main.route('/api/news')
def api_news():
    news = get_all_news()
    categorized_news = categorize_news(news)
    analyzed_news = analyze_sentiment(categorized_news)
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
        return [{'title': article['title'], 'link': article['url'], 'source': article['source']['name']} for article in articles]
    else:
        return []

def get_all_news():
    categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
    news = {category: get_news_by_category(category) for category in categories}
    return news

def categorize_news(news):
    keyword_categories = {
        'sports': ['football', 'soccer', 'tennis', 'cricket', 'nba', 'mlb'],
        'politics': ['election', 'senate', 'congress', 'president', 'government'],
        'technology': ['tech', 'startup', 'gadget', 'software', 'hardware'],
        'health': ['health', 'medicine', 'doctor', 'hospital', 'vaccine'],
        'entertainment': ['movie', 'film', 'celebrity', 'music', 'concert'],
        'business': ['stock', 'market', 'finance', 'economy', 'investment']
    }

    categorized_news = {'sports': [], 'politics': [], 'technology': [], 'health': [], 'entertainment': [], 'business': [], 'others': []}

    for category, articles in news.items():
        for article in articles:
            added = False
            for cat, keywords in keyword_categories.items():
                if any(keyword in article['title'].lower() for keyword in keywords):
                    categorized_news[cat].append(article)
                    added = True
                    break
            if not added:
                categorized_news['others'].append(article)
    return categorized_news

def analyze_sentiment(news):
    for category, articles in news.items():
        for article in articles:
            analysis = TextBlob(article['title'])
            article['sentiment'] = 'positive' if analysis.sentiment.polarity > 0 else 'negative' if analysis.sentiment.polarity < 0 else 'neutral'
    return news
