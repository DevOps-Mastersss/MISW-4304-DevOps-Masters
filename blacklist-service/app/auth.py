import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def build_jwt_utility_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "example-jwt-secret-key")
    JWTManager(app)
    return app


def generate_test_token(identity="postman-local-user", expires_hours=24):
    app = build_jwt_utility_app()

    with app.app_context():
        return create_access_token(
            identity=identity,
            expires_delta=timedelta(hours=expires_hours),
        )


if __name__ == "__main__":
    print(generate_test_token())
