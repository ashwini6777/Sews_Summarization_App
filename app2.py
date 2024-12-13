from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["short_news_db"]
collection = db["articles"]

@app.route("/", methods=["GET"])
def index():
    return render_template("index2.html")

# Route to filter news by date with pagination
@app.route("/news/filter/date/<date>/<category>/<int:page>", methods=["GET"])
def filter_news_by_date_and_category(date, category, page):
    try:
        # Handling the date filter
        start_date = datetime.strptime(date, "%Y-%m-%d") if date != 'all' else None
        end_date = start_date.replace(hour=23, minute=59, second=59) if start_date else None

        # Querying MongoDB
        query = {}
        if start_date and end_date:
            query["nart_pub_date"] = {"$gte": start_date, "$lte": end_date}
        if category != 'all':
            query["nart_category"] = category

        # Count the total number of articles for pagination
        total_count = collection.count_documents(query)

        # Define pagination: for simplicity, we are setting one article per page
        articles_per_page = 1
        news_articles = list(collection.find(query).skip((page - 1) * articles_per_page).limit(articles_per_page))

        for article in news_articles:
            article["_id"] = str(article["_id"])

        # Calculate the total number of pages
        total_pages = (total_count + articles_per_page - 1) // articles_per_page

        return jsonify({
            "articles": news_articles,
            "currentPage": page,
            "totalPages": total_pages
        })

    except Exception as e:
        print(f"Error fetching news by date and category: {e}")
        return jsonify({"error": "Unable to fetch news for this filter"}), 500
    
if __name__ == "__main__":
    app.run(debug=True,port=5002)


