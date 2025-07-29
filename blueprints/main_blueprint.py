
import logging
from flask import Blueprint, render_template
from ..data_manager import DataManager

main_blueprint = Blueprint('main', __name__)
logger = logging.getLogger(__name__)
data_manager = DataManager()

@main_blueprint.route('/')
def index():
    """Serve the main gallery page"""
    try:
        categories = data_manager.get_category_counts()
        return render_template('index.html', categories=categories)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render_template('index.html', categories={})
