# app/__init__.py
from flask import Flask, Blueprint, Response, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path, override=True)
    else:
        print("File .env not found.")

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 28)))
    app.config['JWT_TOKEN_LOCATION'] = os.getenv('JWT_TOKEN_LOCATION')  # Indica che il JWT verrà letto dai cookie
    app.config['JWT_COOKIE_SECURE'] = os.getenv('JWT_COOKIE_SECURE', 'True').lower() in ['true', '1', 't']
    app.config['JWT_ACCESS_COOKIE_NAME'] = os.getenv('JWT_ACCESS_COOKIE_NAME', 'jwt_token')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = os.getenv('JWT_COOKIE_CSRF_PROTECT', 'False').lower() in ['true', '1', 't']
    app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, os.getenv('UPLOAD_FOLDER', 'uploads'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    jwt = JWTManager(app)

    cors_origin = os.getenv('CORS_ORIGIN')
    if cors_origin:
        cors_origins = [origin.strip() for origin in cors_origin.split(',')]
        print(f"Setting CORS origins: {cors_origins}")
    else:
        cors_origins = '*'
        print("No CORS origin specified, allowing all origins")

    CORS(app, resources={r"/*": {"origins": cors_origins}}, supports_credentials=True)

    # CORS(app,
    #     resources={r"/*": {"origins": cors_origin}}, 
    #     origins=cors_origin,
    #     allow_headers="*",
    #     allow_credentials=True,
    #     methods=['GET', 'POST', 'OPTIONS'], 
    #     supports_credentials=True)

    # @app.before_request
    # def handle_preflight():
    #     if request.method == "OPTIONS":
    #         res = Response()
    #         res.headers['X-Content-Type-Options'] = '*'
    #         res.headers['Access-Control-Allow-Origin'] = cors_origin
    #         res.headers['Access-Control-Allow-Headers'] = '*'
    #         res.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    #         res.headers['Access-Control-Allow-Credentials'] = 'true'
    #         return res

    # Documentation
    documentation_bp = Blueprint('documentation', __name__)

    @documentation_bp.route('/documentation')
    @documentation_bp.route('/documentation/<path:path>')
    def serve_sphinx_docs(path='index.html'):
        return app.send_static_file(path)

    # route imports
    with app.app_context():
        from .routes import auth_bp as auth_blueprint
        from .routes import data_bp as data_blueprint
        from .routes import statistic_bp as statistic_blueprint
        from .routes import utility_bp as utility_blueprint
        from .routes import rulebooks_bp as rulebooks_blueprint
        from .routes import scoresheets_bp as scoresheets_blueprint
        from .routes import bgg_bp as bgg_blueprint
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(data_blueprint)
        app.register_blueprint(statistic_blueprint)
        app.register_blueprint(utility_blueprint)
        app.register_blueprint(rulebooks_blueprint)
        app.register_blueprint(scoresheets_blueprint)
        app.register_blueprint(bgg_blueprint)
        app.register_blueprint(documentation_bp)
    

    return app
