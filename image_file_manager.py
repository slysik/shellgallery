import os
import logging
import requests
from typing import Optional
from urllib.parse import urlparse
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ImageFileManager:
    """Manages downloading, processing, and storing image files."""

    def __init__(self, data_dir: str = 'data'):
        self.images_dir = os.path.join(data_dir, 'images')
        os.makedirs(self.images_dir, exist_ok=True)

    def download_and_process_image(self, image_url: str, image_id: str) -> Optional[str]:
        """Download image and save locally with optimization"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            parsed_url = urlparse(image_url)
            path = parsed_url.path.lower()

            if path.endswith(('.jpg', '.jpeg')):
                ext = '.jpg'
            elif path.endswith('.png'):
                ext = '.png'
            elif path.endswith('.gif'):
                ext = '.gif'
            elif path.endswith('.webp'):
                ext = '.webp'
            else:
                content_type = response.headers.get('content-type', '').lower()
                if 'jpeg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'

            filename = f"{image_id}{ext}"
            filepath = os.path.join(self.images_dir, filename)

            try:
                image = Image.open(io.BytesIO(response.content))
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                if image.width > 800:
                    ratio = 800 / image.width
                    new_height = int(image.height * ratio)
                    image = image.resize((800, new_height), Image.Resampling.LANCZOS)
                image.save(filepath, 'JPEG', quality=85, optimize=True)
                logger.info(f"Downloaded and processed image: {filename}")
                return filename
            except Exception as e:
                logger.warning(f"Image processing failed, saving original: {str(e)}")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None

    def delete_image_file(self, filename: str) -> bool:
        """Deletes an image file from the images directory."""
        filepath = os.path.join(self.images_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except OSError as e:
                logger.error(f"Error deleting image file {filepath}: {e}")
        return False
