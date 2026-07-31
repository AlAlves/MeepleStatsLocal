from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required, decode_token
from jwt.exceptions import InvalidTokenError
from werkzeug.security import generate_password_hash, check_password_hash
import os

from app.services.db import find_one, insert_one   


# ---------------------
#   AUTH MANAGEMENT
# ---------------------

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    """Check the authentication status of the user.

    Request: GET

    Returns: 
        JSON: "authenticated" (bool)

    """
    jwt_storage = os.getenv('JWT_STORAGE', 'cookie')
    
    token = None
    if jwt_storage == 'cookie':
        token = request.cookies.get('jwt_token')
    elif jwt_storage == 'localstorage':
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
    if not token:
        return jsonify({'authenticated': False}), 401
    try:
        decode_token(token)
        return jsonify({'authenticated': True}), 200
    except InvalidTokenError:
        return jsonify({'authenticated': False}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user.

    Request: POST
        username (str):
            The username for the new user.
        password (str):
            The password for the new user.
        email (str, optionnal):
            The email address for the new user.

    Returns: 
        JSON:
            'message': str, 
            'jwt_token': access_token

    """

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    # Check if the username already exists
    # MONGO_DEL user = players_collection.find_one({'username': username})
    user = find_one("players", {'username': username})

    if user:
        return jsonify({'error': 'Username already exists'}), 400
    
    # Hash password and save the user
    user_data = {
        "username": username,
        "password": generate_password_hash(password),
        "email": email,
        "image": "",
        "created_at": datetime.now(),
        "total_matches": 0,
        "wins": 0,
        "winstreak": 0,
        "longest_winstreak": 0
    }

    # MONGO_DEL players_collection.insert_one(user_data)
    insert_one("players", user_data)

    # Generate the JWT token and return it
    access_token = create_access_token(identity=username)
    
    jwt_storage = os.getenv('JWT_STORAGE', 'cookie')


    if jwt_storage == 'cookie':
        response = jsonify({'message': 'Register successful'})
        response.set_cookie('jwt_token', access_token, httponly=True, secure=True, max_age=timedelta(weeks=4)) # FIXME: use this in HTTPS environment
        #response.set_cookie('jwt_token', access_token, httponly=True, secure=False, max_age=timedelta(weeks=4))    
    else:
        response = jsonify({'message': 'Register successful', 'jwt_token': access_token})
    return response, 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login an existing user.

    Request: POST
        username (str):
            The username for the existing user.
        password (str):
            The password for the existing user.

    Returns: 
        JSON:
            'message': str, 
            'jwt_token': access_token

    """

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    # Check if the user exists
    user = find_one("players", {'username': username})

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 400

    # Generate the JWT token and return it
    access_token = create_access_token(identity=username)
    
    jwt_storage = os.getenv('JWT_STORAGE')
    if jwt_storage == 'cookie':
        response = jsonify({'message': 'Login successful'})
        # HTTPS response.set_cookie('jwt_token', access_token, httponly=True, secure=True, max_age=timedelta(weeks=4), samesite="None", partitioned=True) # FIXME: use this in HTTPS environment
        response.set_cookie('jwt_token', access_token, httponly=True, secure=False, max_age=timedelta(weeks=4) ) # , samesite="Lax")
    elif jwt_storage == 'localstorage':
        response = jsonify({'message': 'Login successful', 'jwt_token': access_token}) 
    return response, 200

# FIXME: logout route
@auth_bp.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    """Logout TODO

    Returns:
        _type_: _description_
    """
    response = jsonify({'message': 'Logout successful'})
    response.set_cookie('jwt_token', '', expires=0)
    return response, 200

@auth_bp.route('/uploads/<path:filename>')
def get_uploaded_file(filename):
    """Load a stored file. TODO

    Args:
        filename (str): name of file to load.

    Returns:
        json: error
    """
    try:
        # Send the file from the upload folder
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': f"Failed to retrieve file: {str(e)}"}), 404
