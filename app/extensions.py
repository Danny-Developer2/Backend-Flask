from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restx import Api

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

api = Api(
    title='Sistema de Cobranza API',
    version='1.0',
    description='API documentation for Sistema de Cobranza',
    doc='/api/docs'
)