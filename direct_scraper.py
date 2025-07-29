"""
Direct web scraping implementation as fallback when Firecrawl API is not available
Uses trafilatura and requests for reliable content extraction
"""

import requests
import trafilatura
import logging
import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote, urljoin
import re

logger = logging.getLogger(__name__)

class DirectWebScraper:
    """Direct web scraping for shell craft content"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Known URLs with shell craft content
        self.seed_urls = {
            'picture_frames': [
                "https://www.pinterest.com/search/pins/?q=shell%20picture%20frame",
                "https://www.etsy.com/search?q=shell%20picture%20frame",
                "https://www.allfreecrafts.com/shell-crafts/shell-picture-frames.shtml"
            ],
            'shadow_boxes': [
                "https://www.pinterest.com/search/pins/?q=shell%20shadow%20box",
                "https://www.etsy.com/search?q=seashell%20shadow%20box"
            ],
            'jewelry_boxes': [
                "https://www.pinterest.com/search/pins/?q=shell%20jewelry%20box",
                "https://www.etsy.com/search?q=seashell%20jewelry%20box"
            ],
            'display_cases': [
                "https://www.pinterest.com/search/pins/?q=shell%20display%20case",
                "https://www.etsy.com/search?q=shell%20collection%20display"
            ]
        }

    def scrape_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single URL"""
        try:
            logger.info(f"Scraping URL: {url}")
            
            response = self.session.get(url, timeout=15, allow_redirects=True)
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None
            
            # Extract main content using trafilatura
            downloaded = response.text
            text_content = trafilatura.extract(downloaded)
            
            if not text_content:
                logger.warning(f"No text content extracted from {url}")
                return None
            
            # Extract images from HTML
            images = []
            img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
            img_matches = re.findall(img_pattern, downloaded, re.IGNORECASE)
            
            for img_src in img_matches[:5]:  # Limit to first 5 images
                if img_src.startswith('http') and any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    images.append(img_src)
            
            # Create structured data
            content_data = {
                'id': hashlib.md5(url.encode()).hexdigest(),
                'title': self.extract_title(downloaded) or "Shell Craft Project",
                'description': self.extract_description(text_content),
                'source_url': url,
                'images': images,
                'content': text_content[:500],  # First 500 chars
                'platform': self.detect_platform(url),
                'scraped_date': time.time()
            }
            
            return content_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Scraping error for {url}: {str(e)}")
            return None

    def extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML"""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return None

    def extract_description(self, text: str) -> str:
        """Extract a meaningful description from text content"""
        if not text:
            return "Beautiful shell craft project"
        
        sentences = text.split('.')[:3]  # First 3 sentences
        description = '. '.join(sentences).strip()
        
        if len(description) > 200:
            description = description[:200] + "..."
        
        return description or "Beautiful shell craft project"

    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        if 'pinterest.com' in url:
            return 'pinterest'
        elif 'etsy.com' in url:
            return 'etsy'
        elif 'allfreecrafts.com' in url:
            return 'crafts_website'
        else:
            return 'web'

    def search_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for content in a specific category"""
        if category not in self.seed_urls:
            logger.error(f"Unknown category: {category}")
            return []
        
        results = []
        urls_to_try = self.seed_urls[category]
        
        for url in urls_to_try:
            if len(results) >= limit:
                break
                
            content = self.scrape_url_content(url)
            if content:
                # Add category and create individual items for each image
                for i, image_url in enumerate(content['images'][:3]):  # Max 3 per URL
                    item = {
                        'id': hashlib.md5(f"{url}_{i}".encode()).hexdigest(),
                        'title': f"{content['title']} - Style {i+1}",
                        'description': content['description'],
                        'image_url': image_url,
                        'source_url': content['source_url'],
                        'platform': content['platform'],
                        'category': category,
                        'is_diy': True,
                        'scraped_date': content['scraped_date']
                    }
                    results.append(item)
                    
                    if len(results) >= limit:
                        break
            
            # Be respectful with delays
            time.sleep(2)
        
        logger.info(f"Found {len(results)} items for category: {category}")
        return results

    def get_sample_data_if_needed(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate sample data as absolute fallback"""
        logger.info(f"Generating sample data for category: {category}")
        
        # Sample image URLs from public domain or creative commons
        sample_images = [
            "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop",
            "https://images.unsplash.com/photo-1606602606739-b6000b65b8fb?w=400&h=300&fit=crop"
        ]
        
        category_titles = {
            'picture_frames': ["Coastal Shell Picture Frame", "Beach Memory Frame", "Handcrafted Shell Frame"],
            'shadow_boxes': ["Beach Memory Shadow Box", "Seashell Collection Display", "Coastal Specimen Box"],
            'jewelry_boxes': ["Shell-Adorned Jewelry Box", "Coastal Keepsake Box", "Handmade Shell Storage"],
            'display_cases': ["Shell Specimen Display", "Museum-Style Shell Case", "Educational Shell Exhibit"]
        }
        
        results = []
        titles = category_titles.get(category, ["Shell Craft Project"])
        
        for i in range(min(limit, 3)):
            item = {
                'id': hashlib.md5(f"sample_{category}_{i}".encode()).hexdigest(),
                'title': titles[i % len(titles)],
                'description': f"Beautiful {category.replace('_', ' ')} featuring natural seashells and coastal elements.",
                'image_url': sample_images[i % len(sample_images)],
                'source_url': f"https://pinterest.com/sample/{category}/{i}",
                'platform': 'pinterest',
                'category': category,
                'is_diy': True,
                'scraped_date': time.time()
            }
            results.append(item)
        
        return results