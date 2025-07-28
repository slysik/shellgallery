"""
Sample data loader for shell collection gallery
This provides demonstration data when the Firecrawl API is not available
"""

import json
import time
import hashlib
from typing import Dict, List, Any

def get_sample_shell_craft_data() -> Dict[str, List[Dict[str, Any]]]:
    """Return sample shell craft data organized by category"""
    
    sample_data = {
        'picture_frames': [
            {
                'id': hashlib.md5('frame1'.encode()).hexdigest(),
                'title': 'Coastal Shell Picture Frame',
                'description': 'Beautiful handcrafted picture frame decorated with natural seashells collected from the beach. Perfect for displaying your favorite coastal memories.',
                'image_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop',
                'source_url': 'https://pinterest.com/pin/sample-shell-frame-1',
                'platform': 'pinterest',
                'category': 'picture_frames',
                'is_diy': True,
                'scraped_date': time.time()
            },
            {
                'id': hashlib.md5('frame2'.encode()).hexdigest(),
                'title': 'Rustic Driftwood Shell Frame',
                'description': 'Combine driftwood and shells for a stunning nautical frame. This DIY project brings the beach into your home with natural materials.',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
                'source_url': 'https://pinterest.com/pin/sample-shell-frame-2',
                'platform': 'pinterest',
                'category': 'picture_frames',
                'is_diy': True,
                'scraped_date': time.time()
            },
            {
                'id': hashlib.md5('frame3'.encode()).hexdigest(),
                'title': 'Elegant Shell Memory Frame',
                'description': 'Delicate shell arrangement creates an elegant frame perfect for wedding photos or special memories. Features small scallop shells and sand dollars.',
                'image_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop',
                'source_url': 'https://etsy.com/listing/sample-shell-frame-3',
                'platform': 'etsy',
                'category': 'picture_frames',
                'is_diy': False,
                'scraped_date': time.time()
            }
        ],
        
        'shadow_boxes': [
            {
                'id': hashlib.md5('shadow1'.encode()).hexdigest(),
                'title': 'Beach Memory Shadow Box',
                'description': 'Display your beach vacation memories in this beautiful shadow box featuring sand, shells, and small treasures from your coastal adventures.',
                'image_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop',
                'source_url': 'https://pinterest.com/pin/sample-shadow-box-1',
                'platform': 'pinterest',
                'category': 'shadow_boxes',
                'is_diy': True,
                'scraped_date': time.time()
            },
            {
                'id': hashlib.md5('shadow2'.encode()).hexdigest(),
                'title': 'Seashell Collection Display',
                'description': 'Organize and display your seashell collection in this elegant shadow box. Perfect for showcasing rare finds and creating a coastal focal point.',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
                'source_url': 'https://pinterest.com/pin/sample-shadow-box-2',
                'platform': 'pinterest',
                'category': 'shadow_boxes',
                'is_diy': True,
                'scraped_date': time.time()
            }
        ],
        
        'jewelry_boxes': [
            {
                'id': hashlib.md5('jewelry1'.encode()).hexdigest(),
                'title': 'Shell-Adorned Jewelry Box',
                'description': 'Handcrafted wooden jewelry box decorated with carefully selected shells and pearls. Features multiple compartments for organizing jewelry.',
                'image_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=300&fit=crop',
                'source_url': 'https://etsy.com/listing/sample-jewelry-box-1',
                'platform': 'etsy',
                'category': 'jewelry_boxes',
                'is_diy': False,
                'scraped_date': time.time()
            }
        ],
        
        'display_cases': [
            {
                'id': hashlib.md5('display1'.encode()).hexdigest(),
                'title': 'Museum-Style Shell Display',
                'description': 'Professional display case perfect for educational purposes or serious shell collectors. Features labeled compartments and protective glass.',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
                'source_url': 'https://pinterest.com/pin/sample-display-case-1',
                'platform': 'pinterest',
                'category': 'display_cases',
                'is_diy': True,
                'scraped_date': time.time()
            }
        ]
    }
    
    return sample_data

def load_sample_data_to_metadata():
    """Load sample data into the metadata.json file"""
    sample_data = get_sample_shell_craft_data()
    
    # Flatten the data structure for metadata storage
    all_items = {}
    for category, items in sample_data.items():
        for item in items:
            all_items[item['id']] = item
    
    # Save to metadata file
    with open('data/metadata.json', 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    
    print(f"Loaded {len(all_items)} sample items into metadata.json")
    return len(all_items)

if __name__ == '__main__':
    load_sample_data_to_metadata()