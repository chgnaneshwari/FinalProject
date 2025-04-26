Project Name:
EatSmart:Personalized Diet and Hydration Management

Description:
EatSmart is a web application designed to help users manage their daily nutrition and wellness goals. It provides an intuitive platform for tracking food intake, hydration. The application allows users to log their meals, monitor calorie consumption, and categorize food items based on their type. Users can also track their daily water intake and create grocery lists to assist with meal planning. With features such as goal setting for weight management (including weight loss, maintenance, and weight gain) and personalized calorie recommendations, EatSmart aims to provide users with actionable insights to make informed decisions about their diet and overall health. Additionally, the app generates a pie chart to visualize meal distribution across different categories, offering a clear view of eating patterns. Whether users want to improve their dite or maintain a balanced diet, EatSmart empowers them to take control of their health in an easy-to-use, accessible format.

Purpose:
The purpose of EatSmart is to provide users with a comprehensive tool for tracking and managing their daily calories and hydration. By offering personalized insights into their food choices and hydration levels, the application empowers users to make informed decisions about their diet and health. The goal is to help individuals set and achieve realistic nutrition objectives, whether for weight management, healthier eating habits, or better hydration. Through features like meal logging, calorie tracking, goal setting, and grocery list creation, EatSmart supports users in maintaining a balanced and sustainable lifestyle, fostering long-term well-being.

Value:
EatSmart offers significant value by promoting healthy eating habits and providing insights into food choices. It helps users stay mindful of their nutrition and hydration, supports goal tracking (e.g., weight loss or maintenance), and offers a structured way to reach fitness and health goals. By tracking food intake and hydration, users can optimize their diets for better health outcomes.

Technologies Used:
EatSmart is built using a range of modern technologies to provide a seamless and interactive web experience. The backend is powered by Flask, a lightweight Python web framework, which allows for rapid development and flexibility. To manage data, the application uses SQLAlchemy, an Object-Relational Mapping (ORM) tool that interacts with an SQLite database, storing crucial information such as user profiles, meal logs, hydration data, and grocery lists. The front-end is crafted with HTML and CSS for structure and styling, while Bootstrap ensures a responsive and visually appealing interface across all devices. For dynamic interactivity, JavaScript is employed, allowing features like real-time form validation. The application also leverages Matplotlib for generating visualizations, such as pie charts, to help users analyze their meal patterns, and Pandas for efficient data manipulation and analysis. Werkzeug, a WSGI library used by Flask, handles HTTP requests, password hashing, and session management to ensure security. Lastly, the application retrieves food calorie data stored in CSV files, which users can reference while logging their meals. Together, these technologies enable EatSmart to offer users a comprehensive platform for managing their nutrition and hydration in a user-friendly and engaging way.

Setup Instructions:
step1:Install Python 3.7 or Higher

Ensure that Python 3.7 or later is installed on your system. You can download it from the official website: Python Downloads.

To verify the Python installation, run the following command:

python --version

step2:Clone the Repository from GitHub

Open your terminal (or Command Prompt) and clone the repository with this command:

git clone https://github.com/chgnaneshwari/FinalProject

Navigate to the project directory:

cd FinalProject

Then, go to the src folder:

cd src


step3:Install the Required Dependencies

pip install -r requirements.txt

step4:Run the Application

Launch the application by running the following command:

Python app.py


