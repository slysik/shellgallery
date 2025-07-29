"""
Alternative Image Search Implementation
Provides multiple fallback options when Google Custom Search quota is exhausted
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
import time
import random
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class AlternativeImageSearch:
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
    
    def search_bing_images(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search Bing Images for shell craft images"""
        try:
            # Bing Image Search URL
            search_url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2&first=1&tsc=ImageBasicHover"
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image containers
            image_containers = soup.find_all('a', class_='iusc')
            
            results = []
            for container in image_containers[:num_results]:
                try:
                    # Extract image data from the container
                    m_attr = container.get('m')
                    if m_attr:
                        image_data = json.loads(m_attr)
                        
                        result = {
                            'title': image_data.get('t', 'Shell Craft'),
                            'image_url': image_data.get('murl', ''),
                            'source_url': image_data.get('purl', ''),
                            'platform': self._extract_platform(image_data.get('purl', '')),
                            'description': image_data.get('d', ''),
                            'search_query': query
                        }
                        
                        if result['image_url'] and result['source_url']:
                            results.append(result)
                            
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"Error parsing Bing image data: {e}")
                    continue
            
            logger.info(f"Bing found {len(results)} image results")
            return results
            
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
    
    def search_duckduckgo_images(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search DuckDuckGo Images for shell craft images"""
        try:
            # DuckDuckGo doesn't require API keys
            search_url = "https://duckduckgo.com/"
            
            # Get search token first
            response = requests.get(search_url, headers=self.get_headers())
            response.raise_for_status()
            
            # Extract vqd token needed for image search
            vqd_match = re.search(r'vqd=([\d-]+)', response.text)
            if not vqd_match:
                logger.error("Could not extract DuckDuckGo vqd token")
                return []
            
            vqd = vqd_match.group(1)
            
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
            response = requests.get(image_search_url, params=params, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('results', [])[:num_results]:
                result = {
                    'title': item.get('title', 'Shell Craft'),
                    'image_url': item.get('image', ''),
                    'source_url': item.get('url', ''),
                    'platform': self._extract_platform(item.get('url', '')),
                    'description': item.get('title', ''),
                    'search_query': query
                }
                
                if result['image_url'] and result['source_url']:
                    results.append(result)
            
            logger.info(f"DuckDuckGo found {len(results)} image results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def search_direct_scraping(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Direct scraping of craft websites for shell images"""
        results = []
        
        # Target craft websites known to have shell crafts
        craft_sites = [
            {
                'base_url': 'https://www.etsy.com/search?q=',
                'name': 'Etsy',
                'parser': self._parse_etsy_results
            }
        ]
        
        for site in craft_sites:
            try:
                site_results = self._scrape_craft_site(site, query, num_results // len(craft_sites))
                results.extend(site_results)
                
                if len(results) >= num_results:
                    break
                    
                time.sleep(2)  # Rate limiting between sites
                
            except Exception as e:
                logger.error(f"Error scraping {site['name']}: {e}")
                continue
        
        logger.info(f"Direct scraping found {len(results)} results")
        return results[:num_results]
    
    def _scrape_craft_site(self, site_config: Dict, query: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape a specific craft website"""
        try:
            search_url = site_config['base_url'] + quote_plus(f"{query} shell craft")
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=15)
            response.raise_for_status()
            
            return site_config['parser'](response.content, query, limit)
            
        except Exception as e:
            logger.error(f"Error scraping {site_config['name']}: {e}")
            return []
    
    def _parse_etsy_results(self, html_content: bytes, query: str, limit: int) -> List[Dict[str, Any]]:
        """Parse Etsy search results"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # Look for product listings
            listings = soup.find_all('div', {'data-test-id': 'listing-card'})
            
            for listing in listings[:limit]:
                try:
                    # Extract image
                    img_tag = listing.find('img')
                    if not img_tag or not img_tag.get('src'):
                        continue
                    
                    # Extract title and link
                    link_tag = listing.find('a', {'data-test-id': 'listing-link'})
                    if not link_tag:
                        continue
                    
                    title = img_tag.get('alt', 'Shell Craft')
                    image_url = img_tag.get('src', '')
                    source_url = urljoin('https://www.etsy.com', link_tag.get('href', ''))
                    
                    # Clean up image URL (remove Etsy's resize parameters for better quality)
                    if 'il_300x300' in image_url:
                        image_url = image_url.replace('il_300x300', 'il_600x600')
                    
                    result = {
                        'title': title,
                        'image_url': image_url,
                        'source_url': source_url,
                        'platform': 'Etsy',
                        'description': title,
                        'search_query': query
                    }
                    
                    if result['image_url'] and result['source_url']:
                        results.append(result)
                        
                except Exception as e:
                    logger.debug(f"Error parsing Etsy listing: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Etsy results: {e}")
            return []
    
    def _extract_platform(self, url: str) -> str:
        """Extract platform name from URL"""
        if not url:
            return 'Web'
        
        domain_map = {
            'etsy.com': 'Etsy',
            'amazon.com': 'Amazon',
            'pinterest.com': 'Pinterest',
            'ebay.com': 'eBay',
            'craftsy.com': 'Craftsy',
            'michaels.com': 'Michaels',
            'joann.com': 'JOANN'
        }
        
        for domain, platform in domain_map.items():
            if domain in url.lower():
                return platform
        
        return 'Web'
    
    def search_all_methods(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Try all search methods and combine results"""
        all_results = []
        
        # Try each method
        methods = [
            ('Bing', self.search_bing_images),
            ('DuckDuckGo', self.search_duckduckgo_images),
            ('Direct Scraping', self.search_direct_scraping)
        ]
        
        results_per_method = max(1, num_results // len(methods))
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} search...")
                results = method_func(query, results_per_method)
                all_results.extend(results)
                
                if len(all_results) >= num_results:
                    break
                    
                time.sleep(1)  # Rate limiting between methods
                
            except Exception as e:
                logger.error(f"{method_name} search failed: {e}")
                continue
        
        # Remove duplicates based on image URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result['image_url'] not in seen_urls:
                seen_urls.add(result['image_url'])
                unique_results.append(result)
        
        return unique_results[:num_results]