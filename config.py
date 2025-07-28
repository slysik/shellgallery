import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for the shell collection app"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Validate and set configuration
        self._validate_environment()
        
    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['FIRECRAWL_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    @property
    def FIRECRAWL_API_KEY(self) -> str:
        """Firecrawl API key for web scraping"""
        return os.getenv('FIRECRAWL_API_KEY', 'fc-36f153c0b8b44aff97a734aeb8ad3ea4')
    
    @property
    def FLASK_SECRET_KEY(self) -> str:
        """Flask secret key for sessions"""
        return os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    @property
    def FLASK_ENV(self) -> str:
        """Flask environment setting"""
        return os.getenv('FLASK_ENV', 'development')
    
    @property
    def DEBUG(self) -> bool:
        """Debug mode setting"""
        return os.getenv('DEBUG', 'True').lower() == 'true'
    
    @property
    def PORT(self) -> int:
        """Port to run the application on"""
        return int(os.getenv('PORT', 5000))
    
    @property
    def HOST(self) -> str:
        """Host to bind the application to"""
        return os.getenv('HOST', '0.0.0.0')
    
    @property
    def MAX_IMAGES_PER_CATEGORY(self) -> int:
        """Maximum images to store per category"""
        return int(os.getenv('MAX_IMAGES_PER_CATEGORY', 100))
    
    @property
    def SCRAPE_DELAY(self) -> float:
        """Delay between scraping requests (seconds)"""
        return float(os.getenv('SCRAPE_DELAY', 2.0))
    
    @property
    def IMAGE_MAX_WIDTH(self) -> int:
        """Maximum width for processed images"""
        return int(os.getenv('IMAGE_MAX_WIDTH', 800))
    
    @property
    def IMAGE_QUALITY(self) -> int:
        """JPEG quality for processed images"""
        return int(os.getenv('IMAGE_QUALITY', 85))
