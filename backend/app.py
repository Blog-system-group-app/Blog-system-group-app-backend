from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from models import db, TokenBlocklist
from blueprints.comments import comments_bp
from blueprints.profile import profile_bp
from blueprints.posts import posts_bp
from blueprints.auth import auth_bp
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app, prefix='/api')
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Explicitly use in-memory storage for development
)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(comments_bp, url_prefix='/api')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(posts_bp, url_prefix='/api')

@app.errorhandler(404)
def not_found(e):
    return make_response({"error": "Resource not found"}, 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return make_response({"error": "Method not allowed"}, 405)

# JWT blocklist loader
@jwt.token_in_blocklist_loader
def token_in_blocklist(jwt_header, jwt_data):
    jti = jwt_data['jti']
    token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()
    return token is not None

@jwt.expired_token_loader
def expired_jwt_token(jwt_header, jwt_data):
    return make_response({'error': "Token has expired"}, 401)

@jwt.invalid_token_loader
def jwt_invalid_token(error):
    return make_response({'error': 'Invalid token'}, 401)

@jwt.unauthorized_loader
def jwt_missing_token(error):
    return make_response({'error': 'Missing token'}, 401)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)