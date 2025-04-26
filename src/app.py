# Import necessary modules
import os
import csv
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eatsmart.db'  # Using SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.String(50), default=None)
    allergies = db.Column(db.String(200), nullable=True)
    dietary_restrictions = db.Column(db.String(200), nullable=True)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_item = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    portion_size = db.Column(db.Float, nullable=True)
    portion_unit = db.Column(db.String(20), nullable=True)

class Hydration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    water_intake = db.Column(db.Float, nullable=False)

class GroceryList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)

# Function to fetch calorie information from the CSV file located at the specified path
def get_calories_from_csv(food_item):
    csv_file = r'C:\Users\Gnaneshwari\OneDrive\Desktop\EatSmartCalorieTrackingandNutritionalInsights\food_calories.csv'

    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Food'].strip().lower() == food_item.lower():
                    calories = re.sub(r'\D', '', row['Calories'].strip())
                    return float(calories)
        return 0.0
    except FileNotFoundError:
        print("Error: CSV file not found.")
        return 0.0
    except Exception as e:
        print(f"Error fetching data from CSV: {e}")
        return 0.0

# Function to create and save the pie chart for meal categories
def create_pie_chart(user_id):
    meals = Meal.query.filter_by(user_id=user_id).all()
    categories = [meal.category for meal in meals]

    category_counts = pd.Series(categories).value_counts()

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90, colors=['#66b3ff', '#99ff99', '#ffcc99', '#ff6666', '#ffcc00'])
    ax.axis('equal')  # Equal aspect ratio ensures that pie chart is drawn as a circle.

    # Save the pie chart to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return img_base64

# Routes
@app.route("/")
def home():
    return redirect(url_for("welcome"))

@app.route("/welcome")
def welcome():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("welcome.html", username=user.username)
    return render_template("welcome.html", username="Guest")

# Add a route for displaying the pie chart image
@app.route('/pie_chart/<int:user_id>')
def pie_chart(user_id):
    img_base64 = create_pie_chart(user_id)
    return render_template("pie_chart.html", pie_chart_img=img_base64)

# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')

        # Check if the email already exists in the database
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")

        # If the action is login, authenticate the user
        if action == "login":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials, please try again.", "danger")

        # If the action is register, create a new user
        elif action == "register":
            username = request.form.get("username")
            email = request.form.get("email")
            password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')

            # Check if the email already exists in the database
            if User.query.filter_by(email=email).first():
                flash("Email already registered!", "danger")
                return redirect(url_for("login"))

            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

# Route for user dashboard where they can see their meals, hydration, and set goals
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)
    meals = Meal.query.filter_by(user_id=user_id).order_by(Meal.date.desc()).all()

    total_calories = sum(meal.calories for meal in meals)
    # Set default daily goal to 2000 calories
    recommended_calories = 2000

    # Hydration logic: calculating total water intake
    hydration_logs = Hydration.query.filter_by(user_id=user_id, date=datetime.date.today()).all()
    total_water_intake = sum(log.water_intake for log in hydration_logs) if hydration_logs else 0.0

    goal = user.goal
    if goal is None:
        recommended_calories = 2000
    elif goal == "Weight Loss":
        recommended_calories = 1500
    elif goal == "Weight Gain":
        recommended_calories = 2500
    else:
        recommended_calories = 2000

    if total_calories > recommended_calories:
        flash("You have exceeded your calorie goal for the day!", "danger")

    if request.method == "POST":
        action = request.form.get("action")

        # If user wants to update their goal
        if action == "update_goal":
            new_goal = request.form.get("goal")
            user.goal = new_goal
            db.session.commit()
            flash(f"Your goal has been updated to {new_goal}.", "success")
            return redirect(url_for("dashboard"))

        # If user logs a meal
        elif action == "log_meal":
            food_item = request.form.get("food_item")
            calories = get_calories_from_csv(food_item)
            category = request.form.get("category")
            
            portion_size_str = request.form.get("portion_size")
            portion_size = None
            portion_unit = None
            if portion_size_str:
                portion_size_match = re.match(r'(\d+\.?\d*)\s*(\w+)', portion_size_str)
                if portion_size_match:
                    portion_size = float(portion_size_match.group(1))
                    portion_unit = portion_size_match.group(2)
            
            if calories > 0:
                new_meal = Meal(user_id=user_id, food_item=food_item, calories=calories, date=datetime.date.today(), category=category, portion_size=portion_size, portion_unit=portion_unit)
                db.session.add(new_meal)
                db.session.commit()
                flash("Meal logged successfully!", "success")
            else:
                flash("Food item not found or no calories available.", "danger")
            return redirect(url_for("dashboard"))

    return render_template("dashboard.html", user=user, meals=meals, total_calories=total_calories, recommended_calories=recommended_calories,  total_water_intake=total_water_intake, hydration_logs=hydration_logs)

# Route to clear all meals for the user
@app.route("/clear_meals", methods=["POST"])
def clear_meals():
    Meal.query.filter_by(user_id=session["user_id"]).delete()
    db.session.commit()
    flash("All meals have been cleared.", "success")
    return redirect(url_for("dashboard"))

# Route for food search where users can look up the calorie content of food items
@app.route("/food_search", methods=["GET", "POST"])
def food_search():
    search_result = None
    if request.method == "POST":
        food_item = request.form.get("food_item")
        calories = get_calories_from_csv(food_item)
        
        if calories > 0:
            search_result = {
                'food': food_item,
                'calories': calories,
                'category': 'N/A',
                'portion_size': None,
                'portion_unit': 'g'
            }
        else:
            search_result = None
            flash("Food item not found in the database.", "danger")
    
    return render_template("food_search.html", search_result=search_result)

# Route for meal preparation where users can add ingredients to a grocery list
@app.route("/meal_prep", methods=["GET", "POST"])
def meal_prep():
    if "user_id" not in session:
        flash("You must be logged in to access the meal prep.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    grocery_list = GroceryList.query.filter_by(user_id=user_id).first()

    if request.method == "POST":
        action = request.form.get("action")

        # Add new grocery list or update existing one
        if action == "update_grocery_list":
            ingredients = request.form.get("ingredients")
            if grocery_list:
                grocery_list.ingredients = ingredients
            else:
                grocery_list = GroceryList(user_id=user_id, ingredients=ingredients)
                db.session.add(grocery_list)
            db.session.commit()
            flash("Grocery list updated successfully!", "success")
            return redirect(url_for("meal_prep"))

    return render_template("meal_prep.html", grocery_list=grocery_list)

# Run the Flask application
if __name__ == "__main__":
    db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
