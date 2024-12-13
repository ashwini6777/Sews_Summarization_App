from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create or access the database
db = client["shortnewsapp"]

# Create or access the collection
collection = db["News_article"]

# Insert a sample document into the collection
news_data = {
    "nart_no": 1,
    "nart_summary": "Tech companies are investing heavily in AI innovation.",
    "nart_url": "https://example.com/tech-news",
    "nart_pub_date": datetime(2024, 11, 29),
    "nart_category": ["sports","politics","tech", "education"],
    "nart_img_src": "https://example.com/image.jpg",
    "nart_video_src": "https://example.com/video.mp4",
    "nart_author": "John Doe"
}

# Insert the document
# collection.insert_one(news_data)

additional_data = [
    {
        "nart_no": 2,
        "nart_summary": "Sports teams prepare for the upcoming championships.",
        "nart_url": "https://www.hindustantimes.com/",
        "nart_pub_date": datetime(2024, 11, 28),
        "nart_category": ["sports"],
        "nart_img_src": "https://example.com/sports.jpg",
        "nart_video_src": "https://example.com/sports.mp4",
        "nart_author": "Jane Smith"
    },
    {
        "nart_no": 3,
        "nart_summary": "Education reforms proposed for 2025.",
        "nart_url": "https://example.com/education-news",
        "nart_pub_date": datetime(2024, 11, 27),
        "nart_category": ["education"],
        "nart_img_src": "https://example.com/education.jpg",
        "nart_video_src": None,
        "nart_author": "Alex Brown"
    },
    {
        "nart_no": 4,
        "nart_summary": "Education reforms proposed for 2025.",
        "nart_url": "https://example.com/education-news",
        "nart_pub_date": datetime(2024, 12, 2),
        "nart_category": ["education"],
        "nart_img_src": "https://example.com/education.jpg",
        "nart_video_src": None,
        "nart_author": "Alex Brown"
    }
]

collection.insert_many(additional_data)

# Fetch and print all documents to verify
for doc in collection.find():
    print(doc)
