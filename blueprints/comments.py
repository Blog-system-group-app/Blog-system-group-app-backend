from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Comment, Post

comments_bp = Blueprint('comments', __name__)
comments_api = Api(comments_bp)

class CommentEndpoint(Resource):
    @jwt_required()
    def post(self, post_id):
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return make_response({'error': 'Content is required'}, 400)
        
        post = Post.query.get_or_404(post_id)
        
        new_comment = Comment(
            content=content,
            post_id=post_id,
            user_id=get_jwt_identity()
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return make_response(new_comment.to_dict(), 201)
    
    @jwt_required()
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        comments = [comment.to_dict() for comment in Comment.query.filter_by(post_id=post_id).all()]
        return make_response(comments, 200)

class CommentEndpointById(Resource):
    @jwt_required()
    def delete(self, post_id, id):
        comment = Comment.query.filter_by(id=id, user_id=get_jwt_identity()).first()
        if not comment:
            return make_response({'error': 'Comment not found or unauthorized'}, 404)
        
        db.session.delete(comment)
        db.session.commit()
        
        return make_response({'message': 'Deleted successfully'}, 200)

comments_api.add_resource(CommentEndpoint, '/comments/<int:post_id>')
comments_api.add_resource(CommentEndpointById, '/comments/<int:post_id>/<int:id>')