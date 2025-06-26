import pytest
from flask import Flask
from config import Config
from models import db, User
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_user(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test12345'
    })
    assert response.status_code == 201
    assert 'access' in response.json['token']
    assert 'refresh' in response.json['token']

def test_login_user(client):
    
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test12345'
    })
    
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'Test12345'
    })
    assert response.status_code == 200
    assert 'access' in response.json['token']
    assert 'refresh' in response.json['token']

def test_invalid_login(client):
    response = client.post('/api/login', json={
        'username': 'nonexistent',
        'password': 'WrongPass'
    })
    assert response.status_code == 403
    assert response.json['error'] == 'Invalid username or password'

def test_protected_route_without_token(client):
    response = client.get('/api/profile')
    assert response.status_code == 401
    assert response.json['error'] == 'Missing token'

def test_create_post(client):
    
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test12345'
    })
    login_response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'Test12345'
    })
    token = login_response.json['token']['access']
    
    
    response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'This is a test post.'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert response.json['title'] == 'Test Post'