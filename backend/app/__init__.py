# app/__init__.py
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
import os

from app.services.rag import initialize_pinecone

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
    app.config['JWT_TOKEN_LOCATION'] = os.getenv('JWT_TOKEN_LOCATION')
    app.config['JWT_COOKIE_SECURE'] = os.getenv('JWT_COOKIE_SECURE', 'True').lower() in ['true', '1', 't']
    app.config['JWT_ACCESS_COOKIE_NAME'] = os.getenv('JWT_ACCESS_COOKIE_NAME', 'jwt_token')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = os.getenv('JWT_COOKIE_CSRF_PROTECT', 'False').lower() in ['true', '1', 't']
    app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, os.getenv('UPLOAD_FOLDER', 'uploads'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if os.getenv('STORAGE_TYPE', 'local') == 'local':
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if os.getenv('ENABLE_RAG') == 'True':
        app.config['PINECONE_INDEX'], app.config['PINECONE_PROVIDER'] = initialize_pinecone()

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
    def serve_sphinx_docs(path='docs/build/html/index.html'):
        return app.send_static_file(path)

    # route imports
    with app.app_context():
        from app.routes.routes_auth import auth_bp as auth_blueprint
        from app.routes.routes_players import players_bp as players_blueprint
        from app.routes.routes_games import games_bp as games_blueprint
        from app.routes.routes_matches import matches_bp as matches_blueprint
        from app.routes.routes_bgg import bgg_bp as bgg_blueprint
        from app.routes.routes_statistics import statistic_bp as statistic_blueprint
        from app.routes.routes_rulebook import rulebooks_bp as rulebooks_blueprint
        from app.routes.routes_scoresheet import scoresheets_bp as scoresheets_blueprint
        
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(players_blueprint)
        app.register_blueprint(games_blueprint)
        app.register_blueprint(matches_blueprint)
        app.register_blueprint(bgg_blueprint)
        app.register_blueprint(statistic_blueprint)
        app.register_blueprint(rulebooks_blueprint)
        app.register_blueprint(scoresheets_blueprint)
        app.register_blueprint(documentation_bp)
    

    return app
