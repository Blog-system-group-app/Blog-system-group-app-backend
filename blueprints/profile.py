from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
import validators

profile_bp = Blueprint('profile', __name__)
profile_api = Api(profile_bp)

class ProfileEndpoint(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return make_response(user.to_dict(), 200)
    
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        
        if not all([username, email]):
            return make_response({'error': 'Username and email are required'}, 400)
        
        if not validators.email(email):
            return make_response({'error': 'Invalid email format'}, 400)
        
        if username != user.username and User.get_user_by_username(username):
            return make_response({'error': 'Username already in use'}, 400)
        
        if email != user.email and User.query.filter_by(email=email).first():
            return make_response({'error': 'Email already in use'}, 400)
        
        user.username = username
        user.email = email
        db.session.commit()
        
        return make_response(user.to_dict(), 200)

profile_api.add_resource(ProfileEndpoint, '/profile')