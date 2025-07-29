import os
import logging
import time
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from shell_search import ShellSearcher
from direct_scraper import DirectWebScraper
from data_manager import DataManager
from config import Config
from google_image_search import GoogleImageSearcher

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
google_searcher = GoogleImageSearcher()

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

@app.route('/api/upload-search', methods=['POST'])
def upload_search():
    """Search for similar images using uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image selected'
            }), 400
        
        # Check file type - also exclude HEIC which isn't supported by browsers
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        filename = file.filename or ''
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions) or '.heic' in filename.lower():
            return jsonify({
                'success': False,
                'error': 'Invalid image format. Please use JPG, PNG, WebP, or GIF. HEIC files are not supported.'
            }), 400
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join('data', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded file temporarily
        temp_filename = f"upload_{int(time.time())}_{file.filename}"
        temp_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_path)
        
        try:
            # Use Google reverse image search
            logger.info(f"Performing reverse image search for uploaded file: {file.filename}")
            results = google_searcher.reverse_image_search(temp_path)
            
            if results:
                # Process and save new images found
                saved_count = data_manager.save_scraped_data(results, 'upload_search')
                
                return jsonify({
                    'success': True,
                    'message': f'Found {len(results)} similar images',
                    'results_count': len(results),
                    'saved_count': saved_count
                })
            else:
                return jsonify({
                    'success': True,
                    'message': 'No similar images found',
                    'results_count': 0,
                    'saved_count': 0
                })
                
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Error in upload search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process image upload'
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
            
            # Search for real data using Google Image Search API
            results = {}
            search_query = f"{query} shell crafts handmade"
            
            try:
                # Use Google Custom Search to find real shell craft images
                logger.info(f"Searching Google Images for: {search_query}")
                scraped_data = google_searcher.search_images(search_query, limit)
                
                if scraped_data:
                    # Distribute results across categories based on content
                    for item in scraped_data:
                        # Determine category based on content
                        content = (item.get('title', '') + ' ' + item.get('description', '')).lower()
                        
                        if 'frame' in content or 'photo' in content:
                            category = 'picture_frames'
                        elif 'shadow box' in content or 'display' in content:
                            category = 'shadow_boxes'  
                        elif 'jewelry' in content or 'box' in content:
                            category = 'jewelry_boxes'
                        else:
                            category = 'display_cases'
                        
                        # Save individual items
                        saved_count = data_manager.save_scraped_data([item], category)
                        results[category] = results.get(category, 0) + saved_count
                else:
                    logger.warning(f"No real images found for query: {search_query}")
                    results = {'picture_frames': 0, 'shadow_boxes': 0, 'jewelry_boxes': 0, 'display_cases': 0}
                    
            except Exception as e:
                logger.error(f"Error searching with Google Images: {str(e)}")
                results = {'picture_frames': 0, 'shadow_boxes': 0, 'jewelry_boxes': 0, 'display_cases': 0}
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
                    
                    # Use Google Image Search for real shell craft content
                    try:
                        logger.info(f"Searching Google Images for category: {cat}")
                        scraped_data = google_searcher.search_by_category(cat, limit//4)
                        saved_count = data_manager.save_scraped_data(scraped_data, cat)
                        results[cat] = saved_count
                        logger.info(f"Found {saved_count} new images for {cat}")
                    except Exception as e:
                        logger.error(f"Error scraping {cat}: {str(e)}")
                        results[cat] = 0
            else:
                # Single category
                logger.info(f"Scraping category: {category}")
                
                # Use Google Image Search for real shell craft content
                try:
                    logger.info(f"Searching Google Images for category: {category}")
                    scraped_data = google_searcher.search_by_category(category, limit)
                    logger.info(f"Found {len(scraped_data)} images for {category}")
                except Exception as e:
                    logger.error(f"Error scraping {category}: {str(e)}")
                    scraped_data = []
                
                saved_count = data_manager.save_scraped_data(scraped_data, category)
                results = {category: saved_count}
        
        total_results = sum(results.values())
        query_text = ''
        if request.method == 'POST':
            data = request.get_json()
            query_text = data.get('query', '') if data else ''
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Search completed for "{query_text if query_text else "all categories"}". Gallery updated successfully.'
        })
        
    except Exception as e:
        logger.error(f"Error scraping content: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Scraping failed: {str(e)}'
        }), 500

@app.route('/api/gallery')
def get_gallery_images():
    """Get images for gallery display"""
    try:
        category = request.args.get('category', 'all')
        limit = request.args.get('limit', 12, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if category == 'all':
            images = data_manager.get_all_images(limit=limit, offset=offset)
        else:
            images = data_manager.get_images_by_category(category, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'images': images,
            'category': category
        })
    except Exception as e:
        logger.error(f"Error getting gallery images: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load gallery images'
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
