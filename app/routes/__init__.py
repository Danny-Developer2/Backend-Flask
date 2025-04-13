from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api

db = SQLAlchemy()
migrate = Migrate()
api = None

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    global api
    api = Api(app, version='1.0', title='Users API',
        description='A simple users API',
        doc='/docs',
        default_mediatype='application/json'
    )

    # Register blueprints
    from app.routes.web import web
    app.register_blueprint(web)

    # Register API routes
    from app.controllers import user_controller

    return app