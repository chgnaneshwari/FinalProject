Project Name:
EatSmart - Calorie Tracking and Nutritional Insights

Description:
EatSmart is a web application that helps users track their daily food intake, monitor their hydration, and set personalized nutrition goals. The platform allows users to log meals, track calories, and monitor water intake. Users can also receive nutritional insights based on their food choices and set goals for weight management (weight loss, maintenance, or gain). The app provides an intuitive dashboard for tracking progress and making informed decisions about diet and health.

Purpose:
The purpose of EatSmart is to empower users to make healthier lifestyle choices by providing them with tools to track their daily calorie consumption, hydration levels, and nutritional goals. It is designed to be a personal health assistant that supports goal setting, meal logging, and hydration management to help users achieve their health objectives.

Value:
EatSmart offers significant value by promoting healthy eating habits and providing insights into food choices. It helps users stay mindful of their nutrition and hydration, supports goal tracking (e.g., weight loss or maintenance), and offers a structured way to reach fitness and health goals. By tracking food intake and hydration, users can optimize their diets for better health outcomes.

Technologies Used:
EatSmart utilizes a variety of technologies to build a robust and user-friendly web application. The backend is built using Flask, a lightweight Python web framework, which allows for rapid development and easy scalability. SQLAlchemy serves as the Object-Relational Mapping (ORM) tool, providing an abstraction layer to interact with the SQLite database where user data, meals, and hydration logs are stored. For secure authentication, Werkzeug is used to hash user passwords. The application also leverages CSV files to import calorie data and uses regular expressions (re) to clean and process this data efficiently.

On the frontend, HTML and CSS are used to create the user interface, while Jinja2 templates allow for dynamic content rendering. Flask-Session is used for managing user sessions, enabling users to log in and track their progress across multiple sessions. To provide a smooth user experience, flash messages are implemented to notify users of successes, warnings, or errors during interactions with the app. These technologies work together to create a seamless and efficient web application for calorie tracking and nutritional insights.
