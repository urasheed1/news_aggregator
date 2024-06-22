from flask import Blueprint, render_template, jsonify
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    news = get_all_news()
    return render_template('index.html', news=news)

@main.route('/api/news')
def api_news():
    news = get_all_news()
    return jsonify(news)

def get_news_by_category(category):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',  # Change the country code as needed
        'category': category,
        'apiKey': 'f2e85a990df44c5fa9cb0110bdd6e807'  # Replace with your actual News API key
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
