from flask import Flask, render_template, request, redirect, url_for, jsonify, session,flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["short_news_db"]
users_collection = db["users"]
news_collection = db["articles"]

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = {
            "email": email,
            "password": hashed_password,
            "role": role,
            "subscriptions": []  # Make sure subscriptions are initialized as an empty list
        }

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        users_collection.insert_one(user)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Find the user by email in the MongoDB 'users' collection
        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            # Successful login, store username in session
            session['username'] = user['email']  # You can store username or email here
            flash("Login successful!", "success")
            return redirect(url_for("dashboard", username=user['email']))  # Pass username to the dashboard route
        else:
            # Invalid login credentials
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))
    
    return render_template("login.html")




# User dashboard where they can manage subscriptions
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if no username in session

    username = session['username']
    user = users_collection.find_one({"email": username})  # Or use username if needed
    if not user:
        return "User not found", 404

    # Ensure that 'subscriptions' exists in the user document
    subscriptions = user.get('subscriptions', [])  # Defaults to an empty list if not found

    # Fetch news based on user's subscriptions
    news = []
    if subscriptions:
        news = list(news_collection.find({"nart_category": {"$in": subscriptions}}))

    if request.method == "POST":
        categories = request.form.getlist("categories")  # List of categories user selects
        users_collection.update_one({"email": username}, {"$set": {"subscriptions": categories}})
        return redirect(url_for('dashboard'))

    return render_template("dashboard.html", user=user, news=news)

# Filter news by date or category
@app.route("/news/filter", methods=["GET"])
def filter_news():
    if 'username' not in session:
        return redirect(url_for('login'))

    date = request.args.get("date")  # e.g., '2024-12-13'
    category = request.args.get("category")  # e.g., 'sports'

    username = session['username']  # Get the logged-in username from session
    user = users_collection.find_one({"username": username})
    
    if user:
        subscribed_categories = user["subscriptions"]

        query = {}
        if date:
            start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            query["nart_pub_date"] = {"$gte": start_date, "$lt": start_date + datetime.timedelta(days=1)}
        
        if category and category in subscribed_categories:
            query["nart_category"] = category
        
        news = news_collection.find(query)
        news_list = []
        for article in news:
            article["_id"] = str(article["_id"])  # Convert ObjectId to string for JSON serialization
            news_list.append(article)

        return jsonify(news_list)

    return "User not found", 404

# Pagination for news
@app.route("/news/paginated", methods=["GET"])
def get_paginated_news():
    if 'username' not in session:
        return redirect(url_for('login'))

    page = int(request.args.get("page", 1))
    per_page = 6

    query = {}

    total_count = news_collection.count_documents(query)
    news_articles = list(news_collection.find(query).skip((page - 1) * per_page).limit(per_page))

    total_pages = (total_count + per_page - 1) // per_page  # Calculate total pages

    for article in news_articles:
        article["_id"] = str(article["_id"])

    return jsonify({
        "articles": news_articles,
        "total_pages": total_pages,
        "current_page": page
    })

# Logout route
@app.route("/logout")
def logout():
    session.pop('username', None)  # Remove the username from session
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
