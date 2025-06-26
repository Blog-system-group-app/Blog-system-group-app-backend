
from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, create_access_token, create_refresh_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from models import db, TokenBlocklist, User, Post
from blueprints.comments import comments_bp
from blueprints.profile import profile_bp
from blueprints.posts import posts_bp
from config import Config
import validators
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
migrate = Migrate(app, db)
api = Api(app, prefix='/api') 
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])  # Fixed Limiter initialization


app.register_blueprint(comments_bp, url_prefix='/api')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(posts_bp, url_prefix='/api')


class RegisterUser(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return make_response({'error': 'Username, email, and password are required'}, 400)
        
        if not validators.email(email):
            return make_response({'error': 'Invalid email format'}, 400)
        
        if len(password) < 8:
            return make_response({'error': 'Password must be at least 8 characters long'}, 400)
        
        if User.query.filter_by(username=username).first():  
            return make_response({'error': 'Username already in use'}, 400)
        
        if User.query.filter_by(email=email).first():
            return make_response({'error': 'Email already in use'}, 400)
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        
        return make_response({
            'message': 'User created successfully',
            'token': {
                'access': access_token,
                'refresh': refresh_token
            }
        }, 201)

class LoginUser(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return make_response({'error': 'Username and password are required'}, 400)
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return make_response({'error': 'Invalid username or password'}, 403)
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return make_response({
            'message': 'Login successful',
            'token': {
                'access': access_token,
                'refresh': refresh_token
            }
        }, 200)

class LogoutUser(Resource):
    @jwt_required(verify_type=False)
    @limiter.limit("5 per minute")
    def post(self):
        jwt = get_jwt()
        jti = jwt['jti']
        token_type = jwt['type']
        
        new_jti_obj = TokenBlocklist(jti=jti, created_at=datetime.utcnow())
        db.session.add(new_jti_obj)
        db.session.commit()
        
        return make_response({"message": f"{token_type} token revoked successfully"}, 200)

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @limiter.limit("5 per minute")
    def post(self):
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        
        return make_response({'access_token': new_access_token}, 200)

class PostEndpoint(Resource):
    @jwt_required()
    @limiter.limit("10 per minute")
    def get(self):
        user_id = get_jwt_identity()
        posts = [post.to_dict() for post in Post.query.filter_by(user_id=user_id).all()]
        return make_response(posts, 200)
    
    @jwt_required()
    @limiter.limit("10 per minute")
    def post(self):
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        
        if not all([title, content]):
            return make_response({'error': 'Title and content are required'}, 400)
        
        new_post = Post(
            title=title,
            content=content,
            user_id=get_jwt_identity(),
            created_at=datetime.utcnow()
        )
        db.session.add(new_post)
        db.session.commit()
        
        return make_response(new_post.to_dict(), 201)

class PostEndpointById(Resource):
    @jwt_required()
    @limiter.limit("10 per minute")
    def get(self, id):
        post = Post.query.filter_by(id=id, user_id=get_jwt_identity()).first()
        if not post:
            return make_response({'error': 'Post not found or unauthorized'}, 404)
        return make_response(post.to_dict(), 200)
    
    @jwt_required()
    @limiter.limit("10 per minute")
    def put(self, id):
        post = Post.query.filter_by(id=id, user_id=get_jwt_identity()).first()
        if not post:
            return make_response({'error': 'Post not found or unauthorized'}, 404)
        
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        
        if not all([title, content]):
            return make_response({'error': 'Title and content are required'}, 400)
        
        post.title = title
        post.content = content
        post.created_at = datetime.utcnow()  # Update timestamp
        db.session.commit()
        
        return make_response(post.to_dict(), 200)
    
    @jwt_required()
    @limiter.limit("10 per minute")
    def delete(self, id):
        post = Post.query.filter_by(id=id, user_id=get_jwt_identity()).first()
        if not post:
            return make_response({'error': 'Post not found or unauthorized'}, 404)
        
        db.session.delete(post)
        db.session.commit()
        
        return make_response({'message': 'Deleted successfully'}, 200)


api.add_resource(PostEndpoint, '/posts')
api.add_resource(PostEndpointById, '/posts/<int:id>')
api.add_resource(RegisterUser, '/register')
api.add_resource(LoginUser, '/login')
api.add_resource(LogoutUser, '/logout')
api.add_resource(RefreshToken, '/refresh')


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
