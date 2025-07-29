import os
import logging
from typing import List, Dict, Any, Optional
from .metadata_manager import MetadataManager
from .image_file_manager import ImageFileManager

logger = logging.getLogger(__name__)

class DataManager:
    """Manages storage and retrieval of shell craft data"""
    
    def __init__(self, data_dir: str = 'data'):
        self.metadata_manager = MetadataManager(data_dir)
        self.image_file_manager = ImageFileManager(data_dir)

    def save_scraped_data(self, scraped_data: List[Dict[str, Any]], category: str) -> int:
        """Save scraped data with image downloads"""
        if not scraped_data:
            return 0
        
        saved_count = 0
        for item in scraped_data:
            try:
                image_url = item.get('image_url')
                if not image_url:
                    logger.warning(f"No image URL for item, skipping")
                    continue

                item_id = self.metadata_manager.save_item(item, category)
                if not item_id:
                    continue

                local_filename = self.image_file_manager.download_and_process_image(image_url, item_id)
                if local_filename:
                    item['local_image'] = local_filename
                    self.metadata_manager.save_item(item, category) # Save again to update with local filename
                    saved_count += 1
                else:
                    self.metadata_manager.delete_item(item_id) # Rollback metadata if image download fails
            except Exception as e:
                logger.error(f"Error saving item: {str(e)}")
                continue
        
        return saved_count

    def get_category_images(self, category: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get images for a specific category with valid local files only"""
        items = self.metadata_manager.get_by_category(category)
        valid_items = self._filter_valid_images(items)
        return valid_items[offset:offset + limit]

    def get_all_images(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all images across all categories with valid local files only"""
        items = self.metadata_manager.get_all()
        valid_items = self._filter_valid_images(items)
        return valid_items[offset:offset + limit]

    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get specific image by ID"""
        return self.metadata_manager.get_by_id(image_id)

    def delete_image(self, image_id: str) -> bool:
        """Delete an image and its metadata"""
        item = self.metadata_manager.get_by_id(image_id)
        if not item:
            return False

        local_image = item.get('local_image')
        if local_image:
            self.image_file_manager.delete_image_file(local_image)
        
        return self.metadata_manager.delete_item(image_id)

    def clear_category(self, category: str) -> bool:
        """Clear all items from a specific category"""
        items_to_delete = self.metadata_manager.get_by_category(category)
        for item in items_to_delete:
            self.delete_image(item['id'])
        return True

    def _filter_valid_images(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters a list of items, returning only those with valid, existing local image files."""
        valid_items = []
        for item in items:
            local_image = item.get('local_image')
            if local_image and os.path.exists(os.path.join(self.image_file_manager.images_dir, local_image)):
                valid_items.append(item)
        return valid_items
