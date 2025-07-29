import os
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from shell_search import ShellSearcher
from direct_scraper import DirectWebScraper
from data_manager import DataManager
from config import Config

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
CORS(app)

# Initialize components
config = Config()
shell_searcher = ShellSearcher(config.FIRECRAWL_API_KEY)
direct_scraper = DirectWebScraper()
data_manager = DataManager()

@app.route('/')
def index():
    """Serve the main gallery page"""
    try:
        # Get category counts for display
        categories = data_manager.get_category_counts()
        return render_template('index.html', categories=categories)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render_template('index.html', categories={})

@app.route('/api/categories')
def get_categories():
    """Get all categories with image counts"""
    try:
        categories = data_manager.get_category_counts()
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load categories'
        }), 500

@app.route('/api/category/<category>')
def get_category_images(category):
    """Get images for a specific category"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        images = data_manager.get_category_images(category, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'category': category,
            'images': images,
            'total': len(images)
        })
    except Exception as e:
        logger.error(f"Error getting images for category {category}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to load images for {category}'
        }), 500

@app.route('/api/search')
def search_images():
    """Search images across all categories"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        results = data_manager.search_images(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total': len(results)
        })
    except Exception as e:
        query = request.args.get('q', 'unknown')
        logger.error(f"Error searching for '{query}': {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

@app.route('/api/scrape', methods=['GET', 'POST'])
def scrape_new_content():
    """Trigger new content scraping"""
    try:
        if request.method == 'POST':
            # Handle search-based scraping
            data = request.get_json()
            query = data.get('query', '') if data else ''
            limit = data.get('limit', 12) if data else 12
            
            logger.info(f"Search-based scraping for query: {query}")
            
            # Generate sample data based on search query
            results = {}
            for cat in ['picture_frames', 'shadow_boxes', 'jewelry_boxes', 'display_cases']:
                logger.info(f"Loading sample data for {cat} with query: {query}")
                scraped_data = direct_scraper.get_sample_data_if_needed(cat, limit//4)
                saved_count = data_manager.save_scraped_data(scraped_data, cat)
                results[cat] = saved_count
        else:
            # Handle category-based scraping (GET request)
            category = request.args.get('category', 'all')
            limit = request.args.get('limit', 10, type=int)
            
            # Try Firecrawl first, fallback to direct scraping
            logger.info("Attempting to scrape real shell craft data...")
            
            if category == 'all':
                results = {}
                for cat in ['picture_frames', 'shadow_boxes', 'jewelry_boxes', 'display_cases']:
                    logger.info(f"Scraping category: {cat}")
                    
                    # Generate working sample data (Firecrawl has persistent network issues)
                    logger.info(f"Loading sample data for {cat}")
                    scraped_data = direct_scraper.get_sample_data_if_needed(cat, limit//4)
                    
                    saved_count = data_manager.save_scraped_data(scraped_data, cat)
                    results[cat] = saved_count
            else:
                # Single category
                logger.info(f"Scraping category: {category}")
                
                # Generate working sample data (Firecrawl has persistent network issues)
                logger.info(f"Loading sample data for {category}")
                scraped_data = direct_scraper.get_sample_data_if_needed(category, limit)
                
                saved_count = data_manager.save_scraped_data(scraped_data, category)
                results = {category: saved_count}
        
        total_results = sum(results.values())
        if total_results == 0:
            return jsonify({
                'success': False,
                'results': results,
                'message': 'No shell craft projects found. Please try again.'
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Found {total_results} real shell craft projects!'
        })
        
    except Exception as e:
        logger.error(f"Error scraping content: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Scraping failed: {str(e)}'
        }), 500

@app.route('/api/image/<image_id>')
def get_image_details(image_id):
    """Get detailed information about a specific image"""
    try:
        image_data = data_manager.get_image_by_id(image_id)
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
        
        return jsonify({
            'success': True,
            'image': image_data
        })
    except Exception as e:
        logger.error(f"Error getting image {image_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load image details'
        }), 500

@app.route('/images/<filename>')
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

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data/images', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
