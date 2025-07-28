import os
import json
import logging
import time
import hashlib
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from PIL import Image
import io

logger = logging.getLogger(__name__)

class DataManager:
    """Manages storage and retrieval of shell craft data"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.images_dir = os.path.join(data_dir, 'images')
        self.metadata_file = os.path.join(data_dir, 'metadata.json')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Initialize metadata file if it doesn't exist
        if not os.path.exists(self.metadata_file):
            self._save_metadata({})

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from JSON file"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return {}

    def _save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            return False

    def download_and_process_image(self, image_url: str, image_id: str) -> Optional[str]:
        """Download image and save locally with optimization"""
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Get file extension from URL or content type
            parsed_url = urlparse(image_url)
            path = parsed_url.path.lower()
            
            if path.endswith('.jpg') or path.endswith('.jpeg'):
                ext = '.jpg'
            elif path.endswith('.png'):
                ext = '.png'
            elif path.endswith('.gif'):
                ext = '.gif'
            elif path.endswith('.webp'):
                ext = '.webp'
            else:
                # Try to determine from content type
                content_type = response.headers.get('content-type', '').lower()
                if 'jpeg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'  # Default fallback
            
            filename = f"{image_id}{ext}"
            filepath = os.path.join(self.images_dir, filename)
            
            # Process and optimize image
            try:
                # Open image with PIL
                image = Image.open(io.BytesIO(response.content))
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                
                # Resize if too large (max 800px width)
                if image.width > 800:
                    ratio = 800 / image.width
                    new_height = int(image.height * ratio)
                    image = image.resize((800, new_height), Image.Resampling.LANCZOS)
                
                # Save optimized image
                image.save(filepath, 'JPEG', quality=85, optimize=True)
                
                logger.info(f"Downloaded and processed image: {filename}")
                return filename
                
            except Exception as e:
                # If PIL processing fails, save original
                logger.warning(f"Image processing failed, saving original: {str(e)}")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filename
                
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None

    def save_scraped_data(self, scraped_data: List[Dict[str, Any]], category: str) -> int:
        """Save scraped data with image downloads"""
        if not scraped_data:
            return 0
        
        metadata = self._load_metadata()
        saved_count = 0
        
        for item in scraped_data:
            try:
                item_id = item.get('id')
                if not item_id:
                    # Generate ID if not provided
                    source_url = item.get('source_url', '')
                    item_id = hashlib.md5(source_url.encode()).hexdigest()
                    item['id'] = item_id
                
                # Skip if already exists
                if item_id in metadata:
                    logger.info(f"Item {item_id} already exists, skipping")
                    continue
                
                # Download image
                image_url = item.get('image_url')
                if image_url:
                    local_filename = self.download_and_process_image(image_url, item_id)
                    if local_filename:
                        item['local_image'] = local_filename
                    else:
                        logger.warning(f"Failed to download image for {item_id}")
                        continue
                else:
                    logger.warning(f"No image URL for item {item_id}")
                    continue
                
                # Add metadata
                item['category'] = category
                item['saved_date'] = time.time()
                
                # Validate required fields
                required_fields = ['id', 'source_url', 'title']
                if all(field in item for field in required_fields):
                    metadata[item_id] = item
                    saved_count += 1
                    logger.info(f"Saved item {item_id}: {item.get('title', 'Untitled')}")
                else:
                    logger.warning(f"Item {item_id} missing required fields")
                
            except Exception as e:
                logger.error(f"Error saving item: {str(e)}")
                continue
        
        # Save updated metadata
        if saved_count > 0:
            self._save_metadata(metadata)
            logger.info(f"Saved {saved_count} new items to category {category}")
        
        return saved_count

    def get_category_images(self, category: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get images for a specific category"""
        metadata = self._load_metadata()
        
        # Filter by category
        category_items = [
            item for item in metadata.values() 
            if item.get('category') == category
        ]
        
        # Sort by scraped_date (newest first)
        category_items.sort(key=lambda x: x.get('scraped_date', 0), reverse=True)
        
        # Apply pagination
        paginated_items = category_items[offset:offset + limit]
        
        return paginated_items

    def get_category_counts(self) -> Dict[str, int]:
        """Get count of images in each category"""
        metadata = self._load_metadata()
        
        counts = {
            'picture_frames': 0,
            'shadow_boxes': 0,
            'jewelry_boxes': 0,
            'display_cases': 0
        }
        
        for item in metadata.values():
            category = item.get('category')
            if category in counts:
                counts[category] += 1
        
        return counts

    def search_images(self, query: str) -> List[Dict[str, Any]]:
        """Search images across all categories"""
        metadata = self._load_metadata()
        query_lower = query.lower()
        
        matching_items = []
        
        for item in metadata.values():
            # Search in title, description, and category
            title = item.get('title', '').lower()
            description = item.get('description', '').lower()
            category = item.get('category', '').lower()
            
            if (query_lower in title or 
                query_lower in description or 
                query_lower in category):
                matching_items.append(item)
        
        # Sort by relevance (title matches first, then description)
        def relevance_score(item):
            title = item.get('title', '').lower()
            description = item.get('description', '').lower()
            score = 0
            
            if query_lower in title:
                score += 10
            if query_lower in description:
                score += 5
                
            return score
        
        matching_items.sort(key=relevance_score, reverse=True)
        
        return matching_items

    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get specific image by ID"""
        metadata = self._load_metadata()
        return metadata.get(image_id)

    def delete_image(self, image_id: str) -> bool:
        """Delete an image and its metadata"""
        metadata = self._load_metadata()
        
        if image_id not in metadata:
            return False
        
        item = metadata[image_id]
        
        # Delete local image file
        local_image = item.get('local_image')
        if local_image:
            image_path = os.path.join(self.images_dir, local_image)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.info(f"Deleted image file: {local_image}")
            except Exception as e:
                logger.error(f"Error deleting image file {local_image}: {str(e)}")
        
        # Remove from metadata
        del metadata[image_id]
        
        # Save updated metadata
        self._save_metadata(metadata)
        
        logger.info(f"Deleted item {image_id}")
        return True

    def cleanup_orphaned_images(self) -> int:
        """Remove image files that don't have corresponding metadata"""
        metadata = self._load_metadata()
        
        # Get all local image filenames from metadata
        referenced_images = set()
        for item in metadata.values():
            local_image = item.get('local_image')
            if local_image:
                referenced_images.add(local_image)
        
        # Get all image files in directory
        try:
            actual_files = set(os.listdir(self.images_dir))
        except FileNotFoundError:
            return 0
        
        # Find orphaned files
        orphaned_files = actual_files - referenced_images
        
        # Remove orphaned files
        removed_count = 0
        for filename in orphaned_files:
            try:
                filepath = os.path.join(self.images_dir, filename)
                os.remove(filepath)
                removed_count += 1
                logger.info(f"Removed orphaned image: {filename}")
            except Exception as e:
                logger.error(f"Error removing orphaned image {filename}: {str(e)}")
        
        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the data"""
        metadata = self._load_metadata()
        
        stats = {
            'total_items': len(metadata),
            'categories': self.get_category_counts(),
            'platforms': {},
            'oldest_item': None,
            'newest_item': None
        }
        
        # Platform stats
        for item in metadata.values():
            platform = item.get('platform', 'unknown')
            stats['platforms'][platform] = stats['platforms'].get(platform, 0) + 1
        
        # Date stats
        if metadata:
            dates = [item.get('scraped_date', 0) for item in metadata.values()]
            stats['oldest_item'] = min(dates) if dates else None
            stats['newest_item'] = max(dates) if dates else None
        
        return stats
