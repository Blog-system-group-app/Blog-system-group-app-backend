from flask import Flask
from config import Config
from models import db, User, Post, Comment
from datetime import datetime
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_data():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = [
            {'username': 'john_doe', 'email': 'john@example.com', 'password': 'Password123'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'Password456'},
            {'username': 'alice_wonder', 'email': 'alice@example.com', 'password': 'Password789'}
        ]

        for user_data in users:
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(username=user_data['username'], email=user_data['email'])
                user.set_password(user_data['password'])
                db.session.add(user)
        db.session.commit()

        posts = [
            {'title': 'My First Blog Post', 'content': 'This is the content of my first blog post. Exciting times!', 'user_id': 1},
            {'title': 'Learning Flask', 'content': 'Flask is a great framework for building APIs.', 'user_id': 1},
            {'title': 'React Tips', 'content': 'Here are some tips for building better React applications.', 'user_id': 2},
            {'title': 'Why I Love Coding', 'content': 'Coding is my passion because it solves real problems.', 'user_id': 3},
            {'title': 'JWT Authentication', 'content': 'Understanding JWT for secure APIs is crucial.', 'user_id': 2}
        ]

        for post_data in posts:
            if not Post.query.filter_by(title=post_data['title']).first():
                post = Post(title=post_data['title'], content=post_data['content'], user_id=post_data['user_id'], created_at=datetime.utcnow())
                db.session.add(post)
        db.session.commit()

        comments = [
            {'content': 'Great post! Really enjoyed reading it.', 'user_id': 2, 'post_id': 1},
            {'content': 'Thanks for the Flask tips!', 'user_id': 3, 'post_id': 2},
            {'content': 'Can you share more React examples?', 'user_id': 1, 'post_id': 3},
            {'content': 'JWT is tricky but this helped!', 'user_id': 3, 'post_id': 5}
        ]

        for comment_data in comments:
            if not Comment.query.filter_by(content=comment_data['content']).first():
                comment = Comment(content=comment_data['content'], user_id=comment_data['user_id'], post_id=comment_data['post_id'], created_at=datetime.utcnow())
                db.session.add(comment)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()