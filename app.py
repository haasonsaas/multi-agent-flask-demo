#!/usr/bin/env python3
"""
Main Flask application entry point
"""
import os
from flask import Flask, render_template
from flask_cors import CORS
import logging
from api import create_api_blueprint
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for cross-origin requests
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Flask Dashboard API'}, 200
    
    # Main dashboard route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    logger.info("Flask application initialized")
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])