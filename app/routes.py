from flask import Blueprint, render_template, jsonify
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    news = get_news()
    print(news)  # Debug print statement to check the news data
    return render_template('index.html', news=news)

@main.route('/api/news')
def api_news():
    news = get_news()
    return jsonify(news)

def get_news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',  # Change the country code as needed
        'apiKey': 'f2e85a990df44c5fa9cb0110bdd6e807'  # Your actual News API key
    }
    response = requests.get(url, params=params)
    print("Response status code:", response.status_code)  # Debugging line
    print("Response text:", response.json())  # Print the response JSON

    if response.status_code == 200:
        articles = response.json().get('articles', [])
        news = [{'title': article['title'], 'link': article['url']} for article in articles]
        return news
    else:
        return []
