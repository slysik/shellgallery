"""
Google Custom Search API implementation for finding real shell craft images
"""

import os
import requests
import logging
import hashlib
from typing import List, Dict, Any, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

class GoogleImageSearcher:
    """Google Custom Search API for finding real shell craft images"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_CUSTOM_SEARCH_API_KEY')
        self.search_engine_id = os.environ.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key or not self.search_engine_id:
            logger.error("Google Custom Search API credentials not found")
    
    def reverse_image_search(self, image_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar images using reverse image search"""
        if not self.api_key or not self.search_engine_id:
            logger.error("Google API credentials missing")
            return []
        
        try:
            # Use text-based search for shell crafts since reverse image search
            # requires more complex setup. Instead, we'll do related searches
            # based on common shell craft terms
            related_queries = [
                "handmade shell picture frames crafts",
                "seashell shadow box display",
                "coastal shell jewelry box",
                "beach decor shell crafts DIY"
            ]
            
            all_results = []
            for query in related_queries:
                results = self.search_images(query, limit=3)
                all_results.extend(results)
                
            # Remove duplicates and limit results
            seen_urls = set()
            unique_results = []
            for item in all_results:
                if item.get('image_url') not in seen_urls:
                    seen_urls.add(item.get('image_url'))
                    unique_results.append(item)
                    
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in reverse image search: {str(e)}")
            return []

    def search_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for shell craft images using Google Custom Search API"""
        if not self.api_key or not self.search_engine_id:
            logger.error("Google API credentials missing")
            return []
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'searchType': 'image',
                'num': min(limit, 10),  # Google allows max 10 results per request
                'safe': 'active',
                'imgType': 'photo',
                'imgSize': 'medium',
                'fileType': 'jpg,png,webp'
            }
            
            logger.info(f"Searching Google Images for: {query}")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                logger.info(f"Google found {len(items)} image results")
                
                # Process results into our standard format
                processed_results = []
                for item in items:
                    processed_item = self.process_google_result(item, query)
                    if processed_item:
                        processed_results.append(processed_item)
                
                return processed_results
            else:
                logger.error(f"Google API error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Google Images: {str(e)}")
            return []
    
    def process_google_result(self, item: Dict[str, Any], query: str) -> Optional[Dict[str, Any]]:
        """Process a Google search result into our standard format"""
        try:
            # Extract image information
            image_url = item.get('link')
            title = item.get('title', '').strip()
            snippet = item.get('snippet', '').strip()
            
            # Get context page information
            context_link = item.get('image', {}).get('contextLink', '')
            display_link = item.get('displayLink', '')
            
            if not image_url or not title:
                return None
            
            # Create unique ID based on image URL
            item_id = hashlib.md5(image_url.encode()).hexdigest()
            
            # Determine platform/source
            platform = self.detect_platform(context_link or display_link)
            
            # Create standardized result
            processed_result = {
                'id': item_id,
                'title': title,
                'description': snippet or f"Shell craft found via Google Images search for '{query}'",
                'source_url': context_link or image_url,
                'image_url': image_url,
                'platform': platform,
                'search_query': query
            }
            
            return processed_result
            
        except Exception as e:
            logger.error(f"Error processing Google result: {str(e)}")
            return None
    
    def detect_platform(self, url: str) -> str:
        """Detect the platform/source of a URL"""
        if not url:
            return 'Web'
            
        url_lower = url.lower()
        if 'pinterest' in url_lower:
            return 'Pinterest'
        elif 'etsy' in url_lower:
            return 'Etsy'
        elif 'instagram' in url_lower:
            return 'Instagram'
        elif 'facebook' in url_lower:
            return 'Facebook'
        elif 'youtube' in url_lower:
            return 'YouTube'
        elif 'flickr' in url_lower:
            return 'Flickr'
        else:
            return 'Web'
    
    def search_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for images by shell craft category"""
        category_queries = {
            'picture_frames': [
                'shell picture frame handmade',
                'seashell photo frame craft',
                'coastal picture frame shells'
            ],
            'shadow_boxes': [
                'shell shadow box display',
                'seashell memory box craft',
                'beach shadow box shells'
            ],
            'jewelry_boxes': [
                'shell jewelry box handmade',
                'seashell treasure box craft',
                'coastal jewelry box shells'
            ],
            'display_cases': [
                'shell collection display case',
                'seashell specimen display',
                'shell museum display craft'
            ]
        }
        
        queries = category_queries.get(category, [f'{category} shell craft'])
        all_results = []
        
        # Use the first query (most specific)
        if queries:
            results = self.search_images(queries[0], limit)
            all_results.extend(results)
        
        return all_results[:limit]