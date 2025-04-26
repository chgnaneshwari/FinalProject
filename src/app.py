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

# Data Science Feature: Predicting daily calorie consumption trends
def predict_calories_trend(user_id):
    meals = Meal.query.filter_by(user_id=user_id).order_by(Meal.date).all()
    meal_data = pd.DataFrame([(meal.date, meal.calories) for meal in meals], columns=['date', 'calories'])

    # Check if there's enough data to predict
    if len(meal_data) < 7:  # At least one week of data required for a trend
        return None

    # Calculate daily average calorie intake
    meal_data['date'] = pd.to_datetime(meal_data['date'])
    meal_data.set_index('date', inplace=True)

    # Resample to daily data (even if some days have missing meals, it will still work)
    daily_data = meal_data.resample('D').sum()

    # Apply a simple linear regression model to predict next day's calorie consumption trend
    from sklearn.linear_model import LinearRegression
    from datetime import timedelta

    # Prepare data for regression
    daily_data['day_num'] = np.arange(len(daily_data))  # Day number
    X = daily_data['day_num'].values.reshape(-1, 1)
    y = daily_data['calories'].values

    # Train the model
    model = LinearRegression()
    model.fit(X, y)

    # Predict calories for the next day
    next_day_num = len(daily_data) + 1
    predicted_calories = model.predict([[next_day_num]])[0]

    return predicted_calories

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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")

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

        elif action == "register":
            username = request.form.get("username")
            email = request.form.get("email")
            password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')

            if User.query.filter_by(email=email).first():
                flash("Email already registered!", "danger")
                return redirect(url_for("login"))

            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)
    meals = Meal.query.filter_by(user_id=user_id).order_by(Meal.date.desc()).all()

    total_calories = sum(meal.calories for meal in meals)

    # Predict future calorie consumption trend
    predicted_calories = predict_calories_trend(user_id)

    # Set default daily goal to 2000
    recommended_calories = 2000

    # Hydration
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

        if action == "update_goal":
            new_goal = request.form.get("goal")
            user.goal = new_goal
            db.session.commit()
            flash(f"Your goal has been updated to {new_goal}.", "success")
            return redirect(url_for("dashboard"))

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

    return render_template("dashboard.html", user=user, meals=meals, total_calories=total_calories, recommended_calories=recommended_calories, predicted_calories=predicted_calories, total_water_intake=total_water_intake, hydration_logs=hydration_logs)
@app.route("/clear_meals", methods=["POST"])
def clear_meals():
    Meal.query.filter_by(user_id=session["user_id"]).delete()
    db.session.commit()
    flash("All meals have been cleared.", "success")
    return redirect(url_for("dashboard"))


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
@app.route("/meal_prep", methods=["GET", "POST"])
def meal_prep():
    if "user_id" not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    
    if request.method == "POST":
        ingredients = request.form.get("ingredients")
        
        # Ensure ingredients are not empty
        if not ingredients:
            flash("Please enter ingredients.", "warning")
            return redirect(url_for("meal_prep"))
        
        # Add ingredients to the grocery list
        grocery_list = GroceryList(user_id=user_id, ingredients=ingredients)
        db.session.add(grocery_list)
        db.session.commit()

        flash("Your grocery list has been created.", "success")
        return redirect(url_for("meal_prep"))

    # Retrieve the grocery list for the logged-in user
    grocery_list = GroceryList.query.filter_by(user_id=user_id).all()
    
    # Extract only the ingredients from the grocery list
    ingredients_list = [item.ingredients for item in grocery_list]
    
    return render_template("meal_prep.html", grocery_list=ingredients_list)



@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("welcome"))




if __name__ == "__main__":
    with app.app_context():  # Creating an application context
        db.create_all()  # This will now work within the context
    app.run(debug=True)
