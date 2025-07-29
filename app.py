import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from .blueprints.api_blueprint import api_blueprint
from .blueprints.main_blueprint import main_blueprint
from .blueprints.image_blueprint import image_blueprint
from .config import Config

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    CORS(app)

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(image_blueprint)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

    return app

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data/images', exist_ok=True)
    
    app = create_app()
    config = Config()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
