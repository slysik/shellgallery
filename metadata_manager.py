import os
import json
import logging
import time
import hashlib
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetadataManager:
    """Manages storage and retrieval of metadata"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.metadata_file = os.path.join(data_dir, 'metadata.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
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

    def save_item(self, item: Dict[str, Any], category: str) -> Optional[str]:
        """Save a single item to the metadata"""
        metadata = self._load_metadata()
        item_id = item.get('id')
        if not item_id:
            source_url = item.get('source_url', '')
            item_id = hashlib.md5(source_url.encode()).hexdigest()
            item['id'] = item_id

        if item_id in metadata:
            metadata[item_id]['category'] = category
            metadata[item_id]['last_updated'] = time.time()
        else:
            item['category'] = category
            item['saved_date'] = time.time()
            metadata[item_id] = item

        if self._save_metadata(metadata):
            return item_id
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all items from metadata"""
        metadata = self._load_metadata()
        return list(metadata.values())

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single item by its ID"""
        metadata = self._load_metadata()
        return metadata.get(item_id)

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all items in a specific category"""
        metadata = self._load_metadata()
        return [item for item in metadata.values() if item.get('category') == category]

    def delete_item(self, item_id: str) -> bool:
        """Delete an item from the metadata"""
        metadata = self._load_metadata()
        if item_id in metadata:
            del metadata[item_id]
            return self._save_metadata(metadata)
        return False
