import os
import csv
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Add the import for regular expressions to handle calorie data

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
    goal = db.Column(db.String(50), default=None)  # Default is None
    allergies = db.Column(db.String(200), nullable=True)  # Allergies
    dietary_restrictions = db.Column(db.String(200), nullable=True)  # Dietary Restrictions

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_item = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # New column for meal category
    portion_size = db.Column(db.Float, nullable=True)  # New column for portion size
    portion_unit = db.Column(db.String(20), nullable=True)  # New column for portion unit

class Hydration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    water_intake = db.Column(db.Float, nullable=False)

# Function to fetch calorie information from the CSV file located at the specified path
def get_calories_from_csv(food_item):
    # Path to the CSV file in your Desktop folder
    csv_file = r'C:\Users\Gnaneshwari\OneDrive\Desktop\EatSmartCalorieTrackingandNutritionalInsights\food_calories.csv'

    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            # Loop through the rows in the CSV
            for row in reader:
                # Check if the food item matches (case-insensitive)
                if row['Food'].strip().lower() == food_item.lower():
                    # Extract calories and remove the ' cal' suffix if present
                    calories = re.sub(r'\D', '', row['Calories'].strip())  # Remove non-numeric characters
                    return float(calories)  # Return calories as float
        return 0.0  # Return 0 if the food item is not found
    except FileNotFoundError:
        print("Error: CSV file not found.")
        return 0.0
    except Exception as e:
        print(f"Error fetching data from CSV: {e}")
        return 0.0

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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        # Create a new user
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
            # Handle login
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
            # Handle registration
            username = request.form.get("username")
            email = request.form.get("email")
            password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')

            # Check if the email is already registered
            if User.query.filter_by(email=email).first():
                flash("Email already registered!", "danger")
                return redirect(url_for("login"))

            # Create a new user
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
    user = User.query.get(user_id)  # Fetch the user object from the database
    meals = Meal.query.filter_by(user_id=user_id).order_by(Meal.date.desc()).all()

    # Calculate total calories consumed today
    total_calories = sum(meal.calories for meal in meals)

    # Set default daily goal to 2000
    recommended_calories = 2000

    # Hydration
    hydration_logs = Hydration.query.filter_by(user_id=user_id, date=datetime.date.today()).all()
    total_water_intake = sum(log.water_intake for log in hydration_logs) if hydration_logs else 0.0  # Ensure it's defined

    # Set goal based on user's choice or default if not set
    goal = user.goal
    if goal is None:
        recommended_calories = 2000  # Default recommended calories for Maintenance
    elif goal == "Weight Loss":
        recommended_calories = 1500
    elif goal == "Weight Gain":
        recommended_calories = 2500
    else:
        recommended_calories = 2000

    # Check if user exceeded their calorie goal
    if total_calories > recommended_calories:
        flash("You have exceeded your calorie goal for the day! Be mindful of your intake.", "danger")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_goal":
            # Handle goal update action
            new_goal = request.form.get("goal")
            user.goal = new_goal  # Update the user's goal
            db.session.commit()
            flash(f"Your goal has been updated to {new_goal}.", "success")
            return redirect(url_for("dashboard"))

        elif action == "log_meal":
            # Handle meal logging (only if it's a meal logging action)
            food_item = request.form.get("food_item")
            calories = get_calories_from_csv(food_item)  # Use the CSV lookup function
            category = request.form.get("category")
            
            # Check if portion_size is provided and valid, otherwise set to None or default
            portion_size_str = request.form.get("portion_size")
            portion_size = None
            if portion_size_str:
                try:
                    portion_size = float(portion_size_str)
                except ValueError:
                    flash("Invalid portion size entered.", "danger")
            
            portion_unit = request.form.get("portion_unit")
            today = datetime.date.today()

            if calories > 0:
                meal = Meal(user_id=user_id, food_item=food_item, calories=calories, date=today, category=category,
                            portion_size=portion_size, portion_unit=portion_unit)
                db.session.add(meal)
                db.session.commit()
                flash("Meal added successfully!", "success")
            else:
                flash("Could not find calorie data for this food item.", "danger")

        # Handle hydration logging
        elif action == "log_hydration":
            water_intake = request.form.get("water_intake")
            if water_intake:
                try:
                    water_intake = float(water_intake)
                    hydration = Hydration(user_id=user_id, date=datetime.date.today(), water_intake=water_intake)
                    db.session.add(hydration)
                    db.session.commit()
                    flash("Water intake logged successfully!", "success")
                except ValueError:
                    flash("Invalid water intake entered.", "danger")

        return redirect(url_for("dashboard"))

    # Calculate progress as percentage
    progress = (total_calories / recommended_calories) * 100 if recommended_calories > 0 else 0
    hydration_goal = 2.5  # e.g., 2.5 liters per day
    hydration_progress = (total_water_intake / hydration_goal) * 100 if hydration_goal > 0 else 0

    return render_template("dashboard.html", meals=meals, total_calories=total_calories,
                           recommended_calories=recommended_calories, progress=progress,
                           user=user, hydration_progress=hydration_progress, total_water_intake=total_water_intake)

@app.route("/clear_meals", methods=["POST"])
def clear_meals():
    # Logic to clear the meals (e.g., delete meals from the database)
    Meal.query.filter_by(user_id=session["user_id"]).delete()
    db.session.commit()
    flash("All meals have been cleared.", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("welcome"))

@app.route("/food_search", methods=["GET", "POST"])
def food_search():
    if request.method == "POST":
        food_item = request.form.get("food_item")
        calories = get_calories_from_csv(food_item)  # Use the new function
        if calories > 0:
            flash(f"Calories in {food_item}: {calories} kcal", "success")
        else:
            flash("No calorie data found for this food item.", "danger")
    return render_template("food_search.html")

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
