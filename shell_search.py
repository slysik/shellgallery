import os
import requests
import logging
import time
import json
import hashlib
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ShellSearcher:
    """Handles web scraping using Firecrawl API for shell craft content"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Category-specific search terms
        self.search_terms = {
            'picture_frames': [
                "handcrafted shell picture frame DIY",
                "handmade shell frame craft",
                "DIY seashell photo frame",
                "coastal picture frame shells",
                "beach memory frame shells"
            ],
            'shadow_boxes': [
                "shell shadow box display",
                "seashell collection shadow box", 
                "beach memory shadow box",
                "coastal specimen frame",
                "shell display case vintage"
            ],
            'jewelry_boxes': [
                "handcrafted shell jewelry box",
                "handmade shell storage box",
                "artisan shell keepsake box",
                "DIY shell treasure box",
                "coastal jewelry box shells"
            ],
            'display_cases': [
                "shell specimen display case",
                "museum shell collection display",
                "educational shell exhibit",
                "shell conservation display",
                "scientific shell presentation"
            ]
        }
        
        # Platform-specific URLs for targeted scraping
        self.target_sites = {
            'pinterest': 'https://pinterest.com/search/pins/?q=',
            'etsy': 'https://www.etsy.com/search?q='
        }

    def firecrawl_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Use Firecrawl search API to find content"""
        try:
            url = f"{self.base_url}/v0/search"
            payload = {
                "query": query,
                "pageOptions": {
                    "onlyMainContent": True
                },
                "limit": limit,
                "scrapeOptions": {
                    "formats": ["markdown", "html"],
                    "onlyMainContent": True,
                    "removeCSS": True,
                    "removeJS": True
                }
            }
            
            logger.info(f"Searching Firecrawl for: {query}")
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Firecrawl search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error in Firecrawl search: {str(e)}")
            return []

    def firecrawl_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Use Firecrawl scrape API to get content from specific URL"""
        try:
            scrape_url = f"{self.base_url}/v0/scrape"
            payload = {
                "url": url,
                "pageOptions": {
                    "onlyMainContent": True
                },
                "scrapeOptions": {
                    "formats": ["markdown", "html"],
                    "onlyMainContent": True,
                    "removeCSS": True,
                    "removeJS": True,
                    "includeImages": True
                }
            }
            
            logger.info(f"Scraping URL: {url}")
            response = requests.post(scrape_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                logger.error(f"Firecrawl scrape failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in Firecrawl scrape: {str(e)}")
            return None

    def search_pinterest(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Pinterest for shell craft content"""
        pinterest_query = f"site:pinterest.com {query}"
        results = []
        
        search_results = self.firecrawl_search(pinterest_query, limit)
        
        for result in search_results:
            try:
                # Extract Pinterest-specific data
                extracted_data = self.extract_pinterest_data(result)
                if extracted_data:
                    results.append(extracted_data)
                    
                # Add delay to respect rate limits
                time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error processing Pinterest result: {str(e)}")
                continue
        
        return results

    def search_etsy(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Etsy for shell craft products"""
        etsy_query = f"site:etsy.com {query}"
        results = []
        
        search_results = self.firecrawl_search(etsy_query, limit)
        
        for result in search_results:
            try:
                # Extract Etsy-specific data
                extracted_data = self.extract_etsy_data(result)
                if extracted_data:
                    results.append(extracted_data)
                    
                # Add delay to respect rate limits
                time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error processing Etsy result: {str(e)}")
                continue
        
        return results

    def extract_pinterest_data(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured data from Pinterest scraping result"""
        try:
            url = result.get('sourceURL', '')
            content = result.get('markdown', '') or result.get('html', '')
            
            if not url or 'pinterest.com' not in url:
                return None
            
            # Generate unique ID
            unique_id = hashlib.md5(url.encode()).hexdigest()
            
            # Extract title from content
            title = self.extract_title_from_content(content)
            
            # Extract description
            description = self.extract_description_from_content(content)
            
            # Extract images from content
            images = self.extract_images_from_content(content, url)
            
            if not images:
                return None
            
            return {
                'id': unique_id,
                'image_url': images[0],  # Use first image
                'source_url': url,
                'title': title or 'Shell Craft Project',
                'description': description or 'Handcrafted shell project from Pinterest',
                'platform': 'pinterest',
                'is_diy': True,
                'scraped_date': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting Pinterest data: {str(e)}")
            return None

    def extract_etsy_data(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured data from Etsy scraping result"""
        try:
            url = result.get('sourceURL', '')
            content = result.get('markdown', '') or result.get('html', '')
            
            if not url or 'etsy.com' not in url:
                return None
            
            # Generate unique ID
            unique_id = hashlib.md5(url.encode()).hexdigest()
            
            # Extract title from content
            title = self.extract_title_from_content(content)
            
            # Extract description
            description = self.extract_description_from_content(content)
            
            # Extract images from content
            images = self.extract_images_from_content(content, url)
            
            if not images:
                return None
            
            return {
                'id': unique_id,
                'image_url': images[0],  # Use first image
                'source_url': url,
                'title': title or 'Shell Craft Product',
                'description': description or 'Handcrafted shell item from Etsy',
                'platform': 'etsy',
                'is_diy': False,
                'scraped_date': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting Etsy data: {str(e)}")
            return None

    def extract_title_from_content(self, content: str) -> str:
        """Extract title from scraped content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('#') or len(line) < 100):
                # Remove markdown headers
                title = line.lstrip('#').strip()
                if title and len(title) > 10:
                    return title[:100]  # Limit title length
        return ''

    def extract_description_from_content(self, content: str) -> str:
        """Extract description from scraped content"""
        lines = content.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('['):
                description_lines.append(line)
                if len(' '.join(description_lines)) > 200:
                    break
        
        description = ' '.join(description_lines)
        return description[:500] if description else ''

    def extract_images_from_content(self, content: str, base_url: str) -> List[str]:
        """Extract image URLs from scraped content"""
        import re
        
        # Find markdown images
        markdown_images = re.findall(r'!\[.*?\]\((.*?)\)', content)
        
        # Find HTML images
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        
        all_images = markdown_images + html_images
        valid_images = []
        
        for img_url in all_images:
            # Convert relative URLs to absolute
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                parsed_base = urlparse(base_url)
                img_url = f"{parsed_base.scheme}://{parsed_base.netloc}{img_url}"
            elif not img_url.startswith('http'):
                img_url = urljoin(base_url, img_url)
            
            # Filter for valid image URLs
            if self.is_valid_image_url(img_url):
                valid_images.append(img_url)
        
        return valid_images[:3]  # Return up to 3 images

    def is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check file extension
            path = parsed.path.lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            
            return any(path.endswith(ext) for ext in image_extensions)
            
        except Exception:
            return False

    def categorize_content(self, content: str, title: str) -> str:
        """Automatically categorize content based on keywords"""
        text = (content + ' ' + title).lower()
        
        category_keywords = {
            'picture_frames': ['picture frame', 'photo frame', 'frame', 'picture', 'photo'],
            'shadow_boxes': ['shadow box', 'display box', 'memory box', 'collection box'],
            'jewelry_boxes': ['jewelry box', 'storage box', 'keepsake box', 'treasure box'],
            'display_cases': ['display case', 'specimen', 'museum', 'educational', 'exhibit']
        }
        
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            category_scores[category] = score
        
        # Return category with highest score, default to picture_frames
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0] if best_category[1] > 0 else 'picture_frames'

    def search_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for content in a specific category"""
        if category not in self.search_terms:
            logger.error(f"Unknown category: {category}")
            return []
        
        all_results = []
        search_terms = self.search_terms[category]
        
        # Distribute limit across search terms
        per_term_limit = max(1, limit // len(search_terms))
        
        for term in search_terms:
            logger.info(f"Searching for '{term}' in category '{category}'")
            
            # Search Pinterest
            pinterest_results = self.search_pinterest(term, per_term_limit // 2)
            for result in pinterest_results:
                result['category'] = category
                result['auto_categorized'] = False
                all_results.append(result)
            
            # Search Etsy
            etsy_results = self.search_etsy(term, per_term_limit // 2)
            for result in etsy_results:
                result['category'] = category
                result['auto_categorized'] = False
                all_results.append(result)
            
            # Add delay between searches
            time.sleep(2)
            
            if len(all_results) >= limit:
                break
        
        return all_results[:limit]
