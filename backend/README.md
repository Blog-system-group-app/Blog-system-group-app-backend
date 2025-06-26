# Blog-system-group-app-backend
Blog App Backend
A robust RESTful API for a blog application, built with Flask, SQLAlchemy, and JWT-based authentication, integrated with a React frontend for managing blog posts, comments, user profiles, and search functionality.
🚀 Features

User registration and login with JWT access and refresh tokens
CRUD operations for blog posts (create, read, update, delete)
Comment creation, retrieval, and deletion for blog posts
User profile management (view and update username/email)
Full-text search for blog posts by title or content
SQLite database with SQLAlchemy ORM
Secure authentication with password hashing (bcrypt)
Token refresh and logout functionality
Error handling for invalid requests and unauthorized access

🛠 Technologies Used

Python 3.8+
Flask 2.x
Flask-SQLAlchemy
Flask-Migrate
Flask-JWT-Extended
Flask-Bcrypt
SQLite (development database)
Postman (for API testing)

📁 Project Structure
backend/
├── api/
│   ├── blueprints/
│   │   ├── comments.py
│   │   ├── profile.py
│   │   ├── posts.py
│   ├── __init__.py
├── models/
│   ├── post.py
│   ├── user.py
│   ├── comment.py
│   ├── __init__.py
├── app.py
├── seed.py
├── requirements.txt
├── migrations/
├── blog.db
├── README.md

⚙️ Setup Instructions

Clone the repository:
git clone https://github.com/your-username/blog-app.git
cd blog-app/backend


Set up a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Set environment variables:Set the following environment variables in your terminal or add them to a .env file (requires python-dotenv):
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_URL=sqlite:///blog.db
export JWT_SECRET_KEY=your-secret-key  # Replace with a secure key

For Windows, use set instead of export.

Initialize the database:
flask db init
flask db migrate
flask db upgrade


Seed the database (optional):Run the seed script to populate the database with sample data:
python seed.py


Run the development server:
flask run

The API will be available at http://localhost:5000.

Ensure the frontend is running:Follow the frontend setup instructions in client/README.md to start the React app at http://localhost:5173.


🔐 Authentication Flow

Register: POST /api/register creates a new user with username, email, and password (hashed with bcrypt). Returns JWT access and refresh tokens.
Login: POST /api/login authenticates with username and password, returning JWT tokens.
Token Refresh: POST /api/refresh generates a new access token using the refresh token.
Logout: POST /api/logout invalidates the access token.
Protected Endpoints: Require Authorization: Bearer <access_token> header. Automatically refreshes tokens on 401 errors (handled by frontend).

📬 API Endpoints



Method
Endpoint
Auth Required?
Description



POST
/api/register
No
Register a new user


POST
/api/login
No
Login to authenticate


POST
/api/logout
Yes
Logout user (invalidate token)


POST
/api/refresh
Yes (refresh)
Refresh access token


GET
/api/posts
Yes
Retrieve all posts


POST
/api/posts
Yes
Create a new post


GET
/api/posts/<id>
Yes
Retrieve a specific post


PUT
/api/posts/<id>
Yes
Update a post


DELETE
/api/posts/<id>
Yes
Delete a post


GET
/api/comments/<post_id>
Yes
Retrieve comments for a post


POST
/api/comments/<post_id>
Yes
Create a comment for a post


DELETE
/api/comments/<post_id>/<id>
Yes
Delete a comment


GET
/api/profile
Yes
Retrieve user profile


PUT
/api/profile
Yes
Update user profile


GET
/api/search?q=<query>
Yes
Search posts by title or content


🗄 Database Models

User (users table): id, username, email, password_hash
Post (posts table): id, title, content, user_id (foreign key), created_at
Comment (comments table): id, content, post_id (foreign key), user_id (foreign key), created_at

🧪 Testing with Postman
Test API endpoints using Postman to verify functionality. Sample requests:

Register: POST /api/register{ "username": "testuser", "email": "test@example.com", "password": "Password123" }


Login: POST /api/login{ "username": "testuser", "password": "Password123" }


Get Posts: GET /api/postsHeaders: Authorization: Bearer <access_token>
Create Comment: POST /api/comments/1{ "content": "Great post!" }

Headers: Authorization: Bearer <access_token>
Search Posts: GET /api/search?q=exampleHeaders: Authorization: Bearer <access_token>

🔧 Configuration

Database: Uses SQLite (blog.db) for development. For production, configure DATABASE_URL for PostgreSQL or MySQL.
JWT: Set a secure JWT_SECRET_KEY for token signing.
CORS: Configured to allow requests from http://localhost:5173 (frontend). Update in app.py for production.

📝 Notes

Ensure the database is initialized and migrated before running the server.
Use a secure JWT_SECRET_KEY in production to prevent token tampering.
For production, replace SQLite with a production-ready database (e.g., PostgreSQL).
Blueprints (comments.py, profile.py, posts.py) modularize routes; unused blueprints (auth.py, posts.py) can be removed if not needed.
Add unit tests for backend routes using pytest for better coverage.

🚀 Deployment

Deploy to Render or Heroku, ensuring environment variables (DATABASE_URL, JWT_SECRET_KEY) are set.
Use a WSGI server (e.g., Gunicorn) for production.
Configure CORS to allow requests from the deployed frontend URL (e.g., Vercel).
