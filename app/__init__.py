from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.tickets import tickets_bp
from .blueprints.inventory import inventory_bp
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")


    # Initialize extensions
    db.init_app(app)  # adding our db extension to our app
    ma.init_app(app)  # adding our ma extension to our app
    limiter.init_app(app)  # Global rate limiting applied via default_limits
    cache.init_app(app)  # adding our cache extension to our app
    migrate = Migrate(app, db)  # Initialize Flask-Migrate for database migrations

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)  # Registering Swagger UI blueprint

    return app