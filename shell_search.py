import os
import requests
import logging
import time
import json
import hashlib
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Any, Optional
from alternative_image_search import AlternativeImageSearch

logger = logging.getLogger(__name__)

class ShellSearcher:
    """Handles web scraping using Firecrawl API for shell craft content"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key or "fc-36f153c0b8b44aff97a734aeb8ad3ea4"  # Use provided key as fallback
        self.base_url = "https://api.firecrawl.dev"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize alternative search when API quotas are exhausted
        self.alternative_search = AlternativeImageSearch()
        
        # Category-specific search terms - simplified for better API results
        self.search_terms = {
            'picture_frames': [
                "shell picture frame",
                "seashell photo frame", 
                "beach frame craft",
                "coastal frame shells"
            ],
            'shadow_boxes': [
                "shell shadow box",
                "seashell collection box",
                "beach memory box",
                "shell display frame"
            ],
            'jewelry_boxes': [
                "shell jewelry box",
                "seashell storage box",
                "coastal jewelry box",
                "shell treasure box"
            ],
            'display_cases': [
                "shell display case",
                "seashell collection display",
                "shell specimen case",
                "shell museum display"
            ]
        }
        
        # Platform-specific URLs for targeted scraping
        self.target_sites = {
            'pinterest': 'https://pinterest.com/search/pins/?q=',
            'etsy': 'https://www.etsy.com/search?q='
        }

    def firecrawl_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Use Firecrawl search API to find content with retry logic"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/v0/search"
                
                payload = {
                    "query": query,
                    "limit": min(limit, 5),
                    "pageOptions": {
                        "onlyMainContent": True
                    }
                }
                
                logger.info(f"Firecrawl search attempt {attempt + 1}: {query}")
                response = requests.post(url, headers=self.headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    raw_results = data.get('data', [])
                    logger.info(f"Firecrawl found {len(raw_results)} results")
                    
                    # Process results to extract proper format with images
                    processed_results = []
                    for result in raw_results:
                        processed_item = self.process_firecrawl_result(result)
                        if processed_item:
                            processed_results.append(processed_item)
                    
                    return processed_results
                else:
                    logger.warning(f"Firecrawl API returned {response.status_code}: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return []
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Network error attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return []
            except Exception as e:
                logger.error(f"Firecrawl error: {str(e)}")
                return []
        
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
            response = requests.post(scrape_url, headers=self.headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                logger.error(f"Firecrawl scrape failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Firecrawl scrape timeout for URL: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Firecrawl connection error for URL: {url}")
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

    def process_firecrawl_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single Firecrawl search result to extract usable data"""
        try:
            # Extract basic information
            title = result.get('title', '').strip()
            url = result.get('url', '').strip()
            description = result.get('description', '').strip()
            
            if not title or not url:
                return None
            
            # Try to extract images from metadata or content
            image_url = None
            
            # Check for image in metadata
            metadata = result.get('metadata', {})
            if 'image' in metadata:
                image_url = metadata['image']
            elif 'og:image' in metadata:
                image_url = metadata['og:image']
            elif 'twitter:image' in metadata:
                image_url = metadata['twitter:image']
            
            # If no image in metadata, scrape the page
            if not image_url:
                scraped_content = self.firecrawl_scrape(url)
                if scraped_content:
                    # Try to extract images from the scraped content
                    content_html = scraped_content.get('html', '')
                    if content_html:
                        import re
                        # Look for image tags
                        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
                        img_matches = re.findall(img_pattern, content_html, re.IGNORECASE)
                        
                        # Filter for valid image URLs
                        for img_src in img_matches:
                            if img_src.startswith('http') and any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                image_url = img_src
                                break
            
            # If still no image, try common social media patterns
            if not image_url and any(site in url.lower() for site in ['pinterest', 'etsy', 'instagram']):
                # Use a placeholder approach - scrape the actual page for images
                try:
                    import requests
                    page_response = requests.get(url, timeout=10)
                    if page_response.status_code == 200:
                        import re
                        # Look for Pinterest pin images
                        if 'pinterest' in url:
                            pin_img_pattern = r'"images":{"orig":{"url":"([^"]+)"'
                            matches = re.findall(pin_img_pattern, page_response.text)
                            if matches:
                                image_url = matches[0]
                        # Look for Etsy product images
                        elif 'etsy' in url:
                            etsy_img_pattern = r'"url_fullxfull":"([^"]+)"'
                            matches = re.findall(etsy_img_pattern, page_response.text)
                            if matches:
                                image_url = matches[0]
                except Exception as e:
                    logger.warning(f"Could not extract image from {url}: {str(e)}")
            
            # Create standardized result
            processed_result = {
                'id': hashlib.md5(url.encode()).hexdigest(),
                'title': title,
                'description': description,
                'source_url': url,
                'image_url': image_url,
                'platform': self.detect_platform(url)
            }
            
            return processed_result if image_url else None
            
        except Exception as e:
            logger.error(f"Error processing Firecrawl result: {str(e)}")
            return None

    def detect_platform(self, url: str) -> str:
        """Detect the platform/source of a URL"""
        if 'pinterest' in url.lower():
            return 'Pinterest'
        elif 'etsy' in url.lower():
            return 'Etsy'
        elif 'instagram' in url.lower():
            return 'Instagram'
        elif 'facebook' in url.lower():
            return 'Facebook'
        else:
            return 'Web'

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
