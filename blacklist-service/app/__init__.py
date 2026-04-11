from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
api = Api()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    from app.resources import BlacklistResource

    api.add_resource(BlacklistResource, "/blacklists")

    with app.app_context():
        db.create_all()

    return app
