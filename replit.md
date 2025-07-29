# Shell Collection Gallery

## Overview

This is a Flask-based web application that creates a gallery of handcrafted shell craft projects. The application scrapes real content from the web using the Firecrawl API and displays categorized shell craft images with click-through functionality to original sources. The system emphasizes authentic content sourcing and proper attribution to original creators.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with CORS support
- **Configuration Management**: Environment-based configuration using python-dotenv
- **Data Storage**: File-based JSON storage for metadata with local image caching
- **Web Scraping**: Firecrawl API integration for content discovery
- **Image Processing**: PIL-based image optimization and local storage

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 framework
- **Styling**: CSS custom properties with coastal color scheme
- **JavaScript**: Vanilla JS with class-based gallery management
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Data Flow
1. **Content Discovery**: ShellSearcher uses Firecrawl API to find craft content
2. **Data Processing**: Images are downloaded, optimized, and stored locally
3. **Metadata Management**: JSON-based storage tracks source URLs and categorization
4. **Gallery Display**: Frontend renders categorized galleries with click-through links

## Key Components

### Core Application (`app.py`)
- Flask application setup with CORS configuration
- Route handlers for main gallery and API endpoints
- Integration of ShellSearcher and DataManager components
- Error handling and logging configuration

### Configuration Management (`config.py`)
- Environment variable validation and loading
- Centralized configuration with property-based access
- Required API key validation (Firecrawl API)
- Development/production environment handling

### Data Management (`data_manager.py`)
- JSON-based metadata storage and retrieval
- Local image downloading and optimization
- Category-based organization system
- Duplicate detection and source URL tracking

### Search Engine (`shell_search.py`)
- Firecrawl API integration for web scraping
- Category-specific search term management
- Content filtering and validation
- Source attribution preservation

### Frontend Components
- **Templates**: HTML5 semantic structure with Bootstrap components
- **CSS**: Custom coastal-themed design system with CSS custom properties
- **JavaScript**: Gallery class for dynamic content loading and search functionality

## Data Flow

1. **Initial Load**: Application serves main gallery page with category counts
2. **Content Discovery**: ShellSearcher queries Firecrawl API with category-specific terms
3. **Image Processing**: DataManager downloads and optimizes images locally
4. **Metadata Storage**: Source URLs, categories, and image data stored in JSON format
5. **Gallery Rendering**: Frontend displays categorized images with source attribution
6. **Click-Through**: Users can click images to visit original source pages

## External Dependencies

### Primary Dependencies
- **Flask**: Web framework and templating
- **Firecrawl API**: Web scraping and content discovery service
- **PIL/Pillow**: Image processing and optimization
- **Bootstrap 5**: Frontend CSS framework
- **Font Awesome**: Icon library for UI elements

### Environment Variables
- `FIRECRAWL_API_KEY`: Required API key for web scraping service
- `SESSION_SECRET`: Flask session security (optional, has fallback)
- `FLASK_ENV`: Environment setting (defaults to development)
- `DEBUG`: Debug mode toggle (defaults to True)

### File System Dependencies
- `data/` directory for metadata and image storage
- `data/images/` subdirectory for cached images
- `data/metadata.json` file for structured data storage

## Deployment Strategy

### Development Setup
- Local Flask development server
- File-based storage for rapid prototyping
- Environment variable configuration via `.env` file
- Debug logging enabled for development

### Production Considerations
- The current architecture uses file-based storage suitable for small to medium deployments
- Static file serving handled by Flask (consider nginx for production)
- Image optimization reduces storage requirements
- API key security managed through environment variables

### Scalability Notes
- JSON file storage may need migration to database for larger datasets
- Image caching strategy suitable for moderate traffic
- Firecrawl API rate limiting considerations for content discovery
- Category-based organization supports horizontal scaling

### Key Categories
The application organizes content into four main categories:
1. **Picture Frames**: Handcrafted shell picture frames and photo displays
2. **Shadow Boxes**: Shell specimen displays and collection showcases  
3. **Jewelry Boxes**: Decorative shell storage and keepsake boxes
4. **Display Cases**: Museum-style shell presentations and educational displays

Each category maintains its own search terms and content filtering to ensure relevant results and proper source attribution.

## Recent Changes

### 2025-07-29: DuckDuckGo and Bing Image Search Implementation
- Removed Google Custom Search API dependencies to eliminate quota limitations
- Implemented DuckDuckGo Image Search using web scraping with vqd token extraction
- Added Bing Image Search with JSON parsing from HTML containers
- Created unified ImageSearcher class combining both search engines for better coverage
- Searches now split results between DuckDuckGo and Bing for maximum variety
- Added duplicate detection to prevent showing same images from different sources
- Maintained proper source attribution and click-through functionality to original sites
- All searches now use quota-free methods while finding real shell craft images