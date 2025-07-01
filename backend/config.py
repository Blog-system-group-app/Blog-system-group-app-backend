import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ensure the instance directory exists
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(basedir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)  # Create instance/ if it doesn't exist

    SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-default-jwt-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_REFRESH_TOKEN_EXPIRES = 86400