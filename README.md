# Apple Store Reviews API

A simple FastAPI service that collects reviews from the Apple App Store, calculates metrics, and does some basic NLP sentiment analysis.

## Features
- Search for an app's iTunes ID by name
- Fetch the latest 100 reviews using the iTunes RSS feed
- Calculate average rating and rating distribution
- Basic sentiment analysis using TextBlob
- Extract top keywords from negative reviews (using NLTK for tokenization and stopword removal)
- Download the collected reviews as a CSV file

## Setup

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the API:
   ```bash
   uvicorn main:app --reload
   ```

## Endpoints

You can test all endpoints in the browser at `http://127.0.0.1:8000/docs`.

- `GET /check_id?app_name={name}` - Returns the app_id for a given app name.
- `GET /collecting?app_id={id}` - Fetches 100 reviews and saves them to `reviews.csv`.
- `GET /analyze` - Analyzes the CSV file and returns JSON with metrics, negative keywords, and a quick business insight.
- `GET /download` - Returns the `reviews.csv` file for download.

## Notes / Design Decisions
- I used the Apple iTunes RSS feed instead of web scraping because it's much faster, more stable, and doesn't require proxies.
- TextBlob and NLTK were chosen for NLP because they are lightweight and easy to set up for basic keyword extraction compared to heavier libraries like SpaCy.
- The API overwrites `reviews.csv` on each `/collecting` request to keep the analysis isolated to the current app.
