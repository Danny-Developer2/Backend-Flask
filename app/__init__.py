from flask import Flask
from flask_restful import Api, Resource
from datetime import timedelta
from app.extensions import db, migrate, login_manager
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('config.Config')
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Swagger UI configuration
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Backend Flask API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login_manager
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.web import web
    app.register_blueprint(web)
    
    # Initialize and register API
    api = Api(app)
    
    # Add API resources
    class ExampleResource(Resource):
        def get(self):
            return {'message': 'API funcionando!'}
    
    api.add_resource(ExampleResource, '/api/example')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app