from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    api = Api(app)

    from app.resources import BlacklistResource, BlacklistCheckResource, HealthResource

    api.add_resource(BlacklistResource, "/blacklists")
    api.add_resource(BlacklistCheckResource, "/blacklists/<string:email>")
    api.add_resource(HealthResource, "/health")

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"db.create_all() failed on startup: {e}")

    return app