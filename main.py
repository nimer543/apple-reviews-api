from fastapi import FastAPI
import requests
import csv
import pandas as pd
from textblob import TextBlob
from collections import Counter
from fastapi.responses import FileResponse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os


app = FastAPI()


#Check id and full name

def check_id(app_name: str):
    url = f"https://itunes.apple.com/search?term={app_name}&entity=software&limit=1" 
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        app_info = data['results'][0]

    return f"App: {app_info['trackName']} id: {app_info['trackId']}"


#Collecting reviews into csv

def collecting(app_id: int):
    file_name = '/tmp/reviews.csv'
    id = 0
    

    with open(file_name, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Id', 'Author','Title', 'Rating', 'Text'])
        for page in range(1,3):
            url = f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
            response = requests.get(url)
            data = response.json()

            reviews = data.get("feed", {}).get("entry", [])

            for item in reviews:
                if "author" not in item:
                    continue
                id += 1
                rating = int(item["im:rating"]["label"])
                title = item["title"]["label"]
                text = item["content"]["label"]
                author = item["author"]["name"]["label"]
        
                writer.writerow([id,author,title,rating,text])
    if response.status_code == 200:
        return "Successfully collected 100 reviews"
    else:
        return f"Error {response.status_code}"







def analysis():
    df = pd.read_csv('/tmp/reviews.csv')

    #Average rating
    average_rating = df['Rating'].mean()
    
    #Percentage rating
    rating_result = df['Rating'].value_counts(normalize=True) * 100
    

    #Sentiment analysis
    def get_sentiment(text):
        blob = TextBlob(str(text))
        score = blob.sentiment.polarity
        if score > 0:
            text_score = "Positive"
        elif score < 0:
            text_score = "Negative"
        else:
            text_score = "Neutral"
        return text_score
    

    df['Sentiment'] = df['Text'].apply(get_sentiment)

    nltk_dir = '/tmp/nltk_data'
    os.makedirs(nltk_dir, exist_ok=True)
    nltk.data.path.append(nltk_dir)
    nltk.download('punkt_tab', download_dir=nltk_dir)
    nltk.download('punkt', download_dir=nltk_dir)
    nltk.download('stopwords', download_dir=nltk_dir)

    #Delete stop words
    stop_words = set(stopwords.words('english'))
    negative_reviews = df[df['Sentiment'] == 'Negative']
    
    all_negative_text = " ".join(negative_reviews['Text'])
    words = word_tokenize(all_negative_text.lower())
    filtered_text = [word for word in words if word not in stop_words and word.isalpha()]
    counts = Counter(filtered_text)
    top_words = counts.most_common(10)
    bad_words = [word[0] for word in top_words] 
    
    #Filter for result
    actionable_insight = f"Users often mention these topics: {', '.join(bad_words[:3])}. Consider investigating them further."
    
    if any(word in bad_words for word in ['crash', 'bug', 'freeze', 'loading', 'slow', 'broken', 'error']):
        actionable_insight = "Critical issue: Users are complaining about bugs and app crashes. Immediate technical optimization is recommended."
    elif any(word in bad_words for word in ['money', 'price', 'expensive', 'scam', 'pay']):
        actionable_insight = "Monetization issue: Complaints regarding pricing or subscriptions. Consider reviewing the pricing model."
    elif any(word in bad_words for word in ['ui', 'design', 'ugly', 'interface', 'confusing']):
        actionable_insight = "UX/UI issue: Users find the interface confusing or unappealing. UI redesign is recommended."
    
        

    
    return {"average_rating": average_rating,
    "rating_distribution": rating_result.to_dict(), 
    "top_negative_words": top_words,
    "actionable_insight": actionable_insight}


    



@app.get('/check_id')
def search_app_id(app_name: str):
    result = check_id(app_name)
    return {'id': result} 

@app.get('/collecting')
def collect_reviews(app_id: int):
  result = collecting(app_id)
  return {'reviews': result}


@app.get('/analysis')
def get_analysis():
     result = analysis()
     return {'analysis': result}

@app.get('/download')
def download():
    return FileResponse('/tmp/reviews.csv', media_type='text/csv', filename='reviews.csv')

@app.get('/visualize')
def visualize():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    df = pd.read_csv('/tmp/reviews.csv')
    df['Rating'].value_counts().plot.pie(autopct='%1.1f%%')
    plt.savefig('/tmp/rating.png')
    plt.clf()
    return FileResponse('/tmp/rating.png', media_type='image/png')
