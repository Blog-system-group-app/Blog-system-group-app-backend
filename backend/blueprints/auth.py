from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from models import db, User, TokenBlocklist
import validators

auth_bp = Blueprint('auth', __name__)
auth_api = Api(auth_bp)

class RegisterUser(Resource):
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
        
        if User.get_user_by_username(username):
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
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return make_response({'error': 'Username and password are required'}, 400)
        
        user = User.get_user_by_username(username)
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
    def post(self):  
        jwt = get_jwt()
        jti = jwt['jti']
        token_type = jwt['type']
        
        new_jti_obj = TokenBlocklist(jti=jti)
        db.session.add(new_jti_obj)
        db.session.commit()
        
        return make_response({"message": f"{token_type} token revoked successfully"}, 200)

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):  
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        
        return make_response({'access_token': new_access_token}, 200)

auth_api.add_resource(RegisterUser, '/register')
auth_api.add_resource(LoginUser, '/login')
auth_api.add_resource(LogoutUser, '/logout')
auth_api.add_resource(RefreshToken, '/refresh')