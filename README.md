# News Aggregator

## Overview
The **News Aggregator** is a web application that collects, categorizes, and analyzes news articles from multiple sources using Natural Language Processing (NLP). It provides a categorized and sentiment-analyzed view of the latest news to help users easily digest information.

## Features
- **News Categorization**: Automatically groups news articles into categories such as Sports, Business, Technology, Entertainment, Health, Politics, and Science.
- **Sentiment Analysis**: Analyzes the sentiment (positive, neutral, or negative) of each news article's title.
- **Dynamic Source Handling**: Leverages both source-based and keyword-based rules, combined with AI-powered classification, to ensure accurate categorization.
- **API Access**: Provides an API endpoint to retrieve categorized and analyzed news in JSON format.
- **Responsive Interface**: Displays news articles in a user-friendly web interface.

## Technologies Used
- **Python**: Backend logic and data processing.
- **Flask**: Web framework for routing and rendering templates.
- **Transformers (Hugging Face)**: NLP models for sentiment analysis and zero-shot classification.
- **TextBlob** (optional): Simple fallback sentiment analysis library.
- **News API**: Fetches the latest news articles.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/urasheed1/news-aggregator.git
   cd news-aggregator
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your API key:
   - Obtain an API key from [News API](https://newsapi.org/).
   - Replace the placeholder API key (`f2e85a990df44c5fa9cb0110bdd6e807`) in the `get_news_by_category` function in `routes.py`.

## Usage
1. Run the application:
   ```bash
   python run.py
   ```
2. Access the application in your browser:
   - Default URL: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## API Endpoint
- **Endpoint**: `/api/news`
- **Method**: GET
- **Response Format**: JSON
  ```json
  {
      "sports": [
          {"title": "Article Title", "link": "https://example.com", "source": "ESPN", "sentiment": "positive", "confidence": 0.95},
          ...
      ],
      "business": [...],
      "others": [...]
  }
  ```

## Project Structure
```
news_aggregator/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│       └── styles.css
├── run.py
├── requirements.txt
├── README.md
```

## Customization
- **Categories**: Update keywords and sources in the `categorize_news` function in `routes.py`.
- **Sentiment Analysis**: Modify the NLP models in `routes.py` if you want to use different Hugging Face pipelines.

## Known Issues
- **Ambiguous Categorization**: Some articles from generic sources like "Google News" may be miscategorized.
- **Duplicates**: Efforts are made to avoid duplicate articles, but edge cases may arise.

## Contributions
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

