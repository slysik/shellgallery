"""
Alternative Image Search Implementation
Uses DuckDuckGo and Bing for finding shell craft images without API quotas
"""

import requests
import json
import logging
import hashlib
import time
import random
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ImageSearcher:
    """Search for shell craft images using DuckDuckGo and Bing"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    def get_headers(self):
        """Get random headers to avoid blocking"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def search_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for images using both DuckDuckGo and Bing"""
        all_results = []
        
        # Split limit between the two search engines
        ddg_limit = limit // 2
        bing_limit = limit - ddg_limit
        
        # Try DuckDuckGo first
        try:
            ddg_results = self.search_duckduckgo_images(query, ddg_limit)
            all_results.extend(ddg_results)
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
        
        # Add delay between search engines
        time.sleep(2)
        
        # Try Bing search
        try:
            bing_results = self.search_bing_images(query, bing_limit)
            all_results.extend(bing_results)
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
        
        # Remove duplicates based on image URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result['image_url'] not in seen_urls:
                seen_urls.add(result['image_url'])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    def search_duckduckgo_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search DuckDuckGo Images for shell craft images"""
        try:
            # First make a request to get the vqd token
            search_url = "https://duckduckgo.com/"
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            # Try multiple patterns to extract vqd token
            vqd_patterns = [
                r'vqd=([\d-]+)',
                r'"vqd":"([\d-]+)"',
                r'vqd":\s*"([\d-]+)"',
                r'vqd=([^&,\s]+)'
            ]
            
            vqd = None
            for pattern in vqd_patterns:
                vqd_match = re.search(pattern, response.text)
                if vqd_match:
                    vqd = vqd_match.group(1)
                    break
            
            if not vqd:
                # DuckDuckGo token extraction failed - this is common due to anti-bot measures
                # Skip DuckDuckGo silently since Bing provides good results
                return []
            
            # Perform image search
            image_search_url = "https://duckduckgo.com/i.js"
            params = {
                'l': 'us-en',
                'o': 'json',
                'q': query,
                'vqd': vqd,
                'f': ',,,',
                'p': '1'
            }
            
            time.sleep(1)  # Rate limiting
            response = requests.get(image_search_url, params=params, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('results', [])[:limit]:
                try:
                    title = item.get('title', 'Shell Craft')
                    image_url = item.get('image', '')
                    source_url = item.get('url', '')
                    
                    if image_url and source_url:
                        result = {
                            'id': hashlib.md5(image_url.encode()).hexdigest(),
                            'title': title,
                            'image_url': image_url,
                            'source_url': source_url,
                            'platform': self.detect_platform(source_url),
                            'description': f"Shell craft found via DuckDuckGo search for '{query}'",
                            'search_query': query
                        }
                        results.append(result)
                except Exception as e:
                    logger.debug(f"Error processing DuckDuckGo item: {e}")
                    continue
            
            logger.info(f"DuckDuckGo found {len(results)} image results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def search_bing_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Bing Images for shell craft images"""
        try:
            logger.info(f"Searching Bing Images for: {query}")
            search_url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2"
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image containers
            image_containers = soup.find_all('a', class_='iusc')
            
            results = []
            for container in image_containers[:limit]:
                try:
                    # Extract image data from the container
                    m_attr = container.get('m')
                    if m_attr:
                        try:
                            image_data = json.loads(m_attr)
                            
                            title = image_data.get('t', 'Shell Craft')
                            image_url = image_data.get('murl', '')
                            source_url = image_data.get('purl', '')
                            
                            if image_url and source_url:
                                result = {
                                    'id': hashlib.md5(image_url.encode()).hexdigest(),
                                    'title': title,
                                    'image_url': image_url,
                                    'source_url': source_url,
                                    'platform': self.detect_platform(source_url),
                                    'description': f"Shell craft found via Bing Images search for '{query}'",
                                    'search_query': query
                                }
                                results.append(result)
                                
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(f"Error parsing Bing image data: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error processing Bing container: {e}")
                    continue
            
            logger.info(f"Bing found {len(results)} image results")
            return results
            
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
    
    def reverse_image_search(self, image_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar images using related shell craft terms"""
        # Since we don't have direct reverse image search, use related queries
        related_queries = [
            "handmade shell picture frames crafts",
            "seashell shadow box display",
            "coastal shell jewelry box",
            "beach decor shell crafts DIY"
        ]
        
        all_results = []
        results_per_query = max(1, limit // len(related_queries))
        
        for query in related_queries:
            results = self.search_images(query, results_per_query)
            all_results.extend(results)
            
            if len(all_results) >= limit:
                break
            
            time.sleep(1)  # Rate limiting
        
        return all_results[:limit]
    
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
        
        # Use the most specific query for the category
        if queries:
            return self.search_images(queries[0], limit)
        
        return []
    
    def detect_platform(self, url: str) -> str:
        """Detect the platform/source of a URL"""
        if not url:
            return 'Web'
            
        url_lower = url.lower()
        platform_map = {
            'pinterest': 'Pinterest',
            'etsy': 'Etsy',
            'amazon': 'Amazon',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'youtube': 'YouTube',
            'flickr': 'Flickr',
            'ebay': 'eBay',
            'craftsy': 'Craftsy',
            'michaels': 'Michaels',
            'joann': 'JOANN'
        }
        
        for domain, platform in platform_map.items():
            if domain in url_lower:
                return platform
        
        return 'Web'