import os
import requests
import json
import base64
import hashlib
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class BingVisualSearch:
    """Bing Visual Search integration with AI-enhanced descriptive keywords"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    def get_headers(self):
        """Get headers for web requests"""
        return {
            'User-Agent': self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def analyze_image_with_ai(self, image_path: str) -> Dict[str, Any]:
        """Use OpenAI to analyze the image and generate descriptive keywords"""
        try:
            # Read and encode the image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing images and generating search keywords. Analyze the image and provide descriptive keywords that would help find similar items. Focus on style, materials, colors, craftsmanship, and purpose. Return JSON with 'description', 'keywords', and 'style_tags' fields."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image and generate descriptive keywords for finding similar items. Focus on crafting style, materials, colors, and overall aesthetic. Return JSON format with description, keywords array, and style_tags array."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"AI analysis completed: {result.get('description', '')[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"AI image analysis failed: {e}")
            return {
                "description": "Image analysis not available",
                "keywords": ["handmade", "craft", "decorative"],
                "style_tags": ["artisan", "handcrafted"]
            }
    
    def visual_search_with_keywords(self, image_path: str, user_keywords: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Perform visual search enhanced with AI-generated and user-provided keywords"""
        try:
            # Get AI analysis of the image
            ai_analysis = self.analyze_image_with_ai(image_path)
            
            # Combine AI keywords with user keywords
            ai_keywords = ai_analysis.get('keywords', [])
            style_tags = ai_analysis.get('style_tags', [])
            description = ai_analysis.get('description', '')
            
            # Create enhanced search queries combining visual analysis with keywords
            search_queries = []
            
            # Primary query: AI description + user keywords
            if user_keywords.strip():
                primary_query = f"{description} {user_keywords}".strip()
            else:
                primary_query = description
            
            search_queries.append(primary_query)
            
            # Secondary queries: specific combinations
            if user_keywords.strip():
                for keyword in ai_keywords[:3]:  # Use top 3 AI keywords
                    search_queries.append(f"{keyword} {user_keywords}")
            
            # Style-based queries
            for style in style_tags[:2]:  # Use top 2 style tags
                if user_keywords.strip():
                    search_queries.append(f"{style} {user_keywords}")
                else:
                    search_queries.append(f"{style} handmade craft")
            
            logger.info(f"Enhanced visual search with {len(search_queries)} queries")
            
            # Perform searches with the enhanced queries
            from image_search import ImageSearcher
            image_searcher = ImageSearcher()
            
            all_results = []
            results_per_query = max(1, limit // len(search_queries))
            
            for i, query in enumerate(search_queries[:4]):  # Limit to 4 queries max
                try:
                    logger.info(f"Visual search query {i+1}: {query[:100]}...")
                    results = image_searcher.search_images(query, results_per_query)
                    for result in results:
                        result['search_type'] = 'visual_enhanced'
                        result['ai_keywords'] = ai_keywords
                        result['user_keywords'] = user_keywords
                        result['description'] = f"AI-enhanced visual search: {description[:100]}..."
                    all_results.extend(results)
                    
                    if len(all_results) >= limit:
                        break
                        
                except Exception as e:
                    logger.error(f"Search query failed: {e}")
                    continue
            
            # Remove duplicates and return limited results
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result.get('image_url') not in seen_urls:
                    seen_urls.add(result.get('image_url'))
                    unique_results.append(result)
            
            logger.info(f"Visual search found {len(unique_results)} unique results")
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Visual search with keywords failed: {e}")
            return []
    
    def fallback_visual_search(self, image_path: str, user_keywords: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback visual search using related craft terms"""
        try:
            # Basic craft-related searches when visual search fails
            base_queries = [
                "handmade crafts decorative",
                "artisan handcrafted items",
                "DIY craft projects",
                "decorative art pieces"
            ]
            
            if user_keywords.strip():
                search_queries = [f"{query} {user_keywords}" for query in base_queries]
            else:
                search_queries = base_queries
            
            from image_search import ImageSearcher
            image_searcher = ImageSearcher()
            
            all_results = []
            results_per_query = max(1, limit // len(search_queries))
            
            for query in search_queries:
                try:
                    results = image_searcher.search_images(query, results_per_query)
                    for result in results:
                        result['search_type'] = 'visual_fallback'
                        result['user_keywords'] = user_keywords
                    all_results.extend(results)
                    
                    if len(all_results) >= limit:
                        break
                        
                except Exception as e:
                    logger.error(f"Fallback search failed: {e}")
                    continue
            
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Fallback visual search failed: {e}")
            return []