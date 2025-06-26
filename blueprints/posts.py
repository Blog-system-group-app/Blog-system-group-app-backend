from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Post

posts_bp = Blueprint('posts', __name__)
posts_api = Api(posts_bp)

class PostEndpoint(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        posts = [post.to_dict() for post in Post.query.filter_by(user_id=user_id).all()]
        return make_response(posts, 200)
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        
        if not all([title, content]):
            return make_response({'error': 'Title and content are required'}, 400)
        
        new_post = Post(
            title=title,
            content=content,
            user_id=get_jwt_identity()
        )
        db.session.add(new_post)
        db.session.commit()
        
        return make_response(new_post.to_dict(), 201)

class PostEndpointById(Resource):
    @jwt_required()
    def get(self, id):
        post = Post.query.filter_by(id=id, user_id=get_jwt_identity()).first()
        if not post:
            return make_response({'error': 'Post not found or unauthorized'}, 404)
        return make_response(post.to_dict(), 200)
    
    @jwt_required()
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
        db.session.commit()
        
        return make_response(post.to_dict(), 200)
    
    @jwt_required()
    def delete(self, id):
        post = Post.query.filter_by(id=id, user_id=get_jwt_identity()).first()
        if not post:
            return make_response({'error': 'Post not found or unauthorized'}, 404)
        
        db.session.delete(post)
        db.session.commit()
        
        return make_response({'message': 'Deleted successfully'}, 200)

class SearchPosts(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('q', '')
        user_id = get_jwt_identity()
        posts = Post.query.filter(
            Post.user_id == user_id,
            (Post.title.ilike(f'%{query}%') | Post.content.ilike(f'%{query}%'))
        ).all()
        return make_response([post.to_dict() for post in posts], 200)

posts_api.add_resource(PostEndpoint, '/posts')
posts_api.add_resource(PostEndpointById, '/posts/<int:id>')
posts_api.add_resource(SearchPosts, '/search')