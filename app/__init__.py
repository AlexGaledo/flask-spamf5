

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    JWTManager(app)
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"
    app.config["JWT_COOKIE_SECURE"] = True           # required for HTTPS
    app.config["JWT_COOKIE_SAMESITE"] = "None"       # allow cross-site cookies
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    from .routes import register_routes
    register_routes(app)

    #debug
    @app.route('/')
    def home():
        return jsonify({"response":"API is running"})
    
    return app

