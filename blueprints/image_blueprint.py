
import logging
from flask import Blueprint, send_from_directory, jsonify

image_blueprint = Blueprint('images', __name__, url_prefix='/images')
logger = logging.getLogger(__name__)

@image_blueprint.route('/<filename>')
def serve_image(filename):
    """Serve static images"""
    try:
        return send_from_directory('data/images', filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Image not found'
        }), 404
