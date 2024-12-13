from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["short_news_db"]
articles_collection = db["articles"]
categories_collection = db["categories"]

# Ensure the categories collection is populated with default categories
def initialize_categories():
    categories = ["sports", "politics", "technology", "health", "education", "entertainment", "business","food"]
    for category in categories:
        if not categories_collection.find_one({"name": category}):
            categories_collection.insert_one({"name": category})

initialize_categories()

# Summarize an article
def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return {
            "url": url,
            "title": article.title,
            "summary": article.summary,
            "image_src": article.top_image if article.top_image else "",  
            "author": ", ".join(article.authors) if article.authors else "Unknown"
        }
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return {
            "url": url,
            "title": "Failed to Fetch Title",
            "summary": "Failed to summarize article.",
            "image_src": "",
            "author": "Unknown"
        }

# Scrape links from a URL
def fetch_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Find all links with "href" attribute and filter out non-news links
        links = [a["href"] for a in soup.find_all("a", href=True) if "http" in a["href"]]
        return links
    except Exception as e:
        print(f"Error fetching links: {e}")
        return []

# Route: Home page
@app.route("/")
def index():
    return render_template("index.html")

# Route: Fetch news articles
@app.route("/fetch", methods=["POST"])
def fetch_news():
    url = request.json.get("url")
    links = fetch_links(url)
    articles = []

    for link in links[:30]:  # Limit to the first 30 links to avoid overwhelming the response
        articles.append(summarize_article(link))

    return jsonify(articles)

# Route: Save an article to MongoDB
@app.route("/add", methods=["POST"])
def add_article():
    data = request.json

    # Check if the category is valid
    if data["category"] not in ["sports", "politics", "technology", "health", "education", "entertainment", "business","food"]:
        return jsonify({"message": "Invalid category selected!"}), 400

    # Fetch the last article by sorting on 'nart_no' in descending order
    last_article = articles_collection.find_one(sort=[("nart_no", -1)])

    # Determine the next 'nart_no'
    if last_article and "nart_no" in last_article:
        next_nart_no = last_article["nart_no"] + 1
    else:
        next_nart_no = 1  # Start with 1 if no articles exist or 'nart_no' is missing

    # Prepare the article document
    article = {
        "nart_no": next_nart_no,
        "nart_summary": data["summary"],
        "nart_url": data["url"],
        "nart_pub_date": datetime.now(),
        "nart_category": data["category"],
        "nart_img_src": data["image_src"],
        "nart_author": data["author"],
        "nart_keywords_csv": data.get("keywords_csv", ""),
        "nart_labels_csv": data.get("labels_csv", "")
    }

    # Save the article to the database
    articles_collection.update_one(
        {"nart_url": data["url"]},
        {"$set": article},
        upsert=True
    )

    return jsonify({"message": "Article added to the database!"})

if __name__ == "__main__":
    app.run(debug=True,port=5001)
