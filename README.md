# Shell Gallery - AI-Enhanced Image Search

A Flask web application that provides intelligent image search capabilities with AI-powered visual analysis. Search for shell craft images using multiple discovery strategies including text search, visual similarity matching, and AI-enhanced "Find Similar" functionality.

## Features

### 🔍 Multi-Modal Search
- **Text Search**: Find images using natural language queries
- **Visual Search**: Upload an image to find similar items
- **AI-Enhanced Search**: Combines OpenAI image analysis with user keywords for precise results

### 🤖 AI Integration
- **OpenAI Vision**: Automatically analyzes uploaded images for visual elements, materials, and style
- **Smart Keywords**: AI-generated descriptions combined with user input for better search precision
- **Multiple Search Strategies**: Uses both Bing Visual Search and traditional image search

### 🌊 Search Engines
- **Bing Images**: Primary search engine with reliable results
- **DuckDuckGo Images**: Fallback search with quota-free access
- **No Google Dependencies**: Eliminates API quotas and limitations

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key for AI-enhanced features

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shellgallery.git
cd shellgallery
```

2. Install dependencies:
```bash
pip install flask flask-cors python-dotenv requests pillow openai trafilatura beautifulsoup4
```

3. Set up environment variables:
```bash
cp .env.sample .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the application:
```bash
python main.py
```

5. Open your browser to `http://localhost:5000`

## Usage

### Text Search
- Enter search terms like "vintage shell frame" or "coastal decor"
- Results show real images from web sources with proper attribution

### Visual Search
1. Click "Find Similar" button
2. Upload an image (JPG, PNG, WebP, GIF)
3. Optionally add descriptive keywords
4. Choose search type:
   - **Basic**: Traditional visual similarity
   - **AI-Enhanced**: Combines AI analysis with your keywords

### AI-Enhanced Features
- Upload any image and get AI-powered visual analysis
- Add keywords like "vintage", "coastal", "handmade" for better results
- AI identifies colors, materials, patterns, and style elements
- Combines visual and textual search for comprehensive results

## Technical Architecture

### Backend
- **Flask**: Web framework with CORS support
- **OpenAI API**: Image analysis and description generation
- **Multi-Engine Search**: Bing + DuckDuckGo image search
- **Image Processing**: PIL-based optimization and caching

### Frontend
- **Bootstrap 5**: Responsive design framework
- **Vanilla JavaScript**: Dynamic gallery management
- **Modal Interface**: Enhanced search experience

### Data Management
- **JSON Storage**: Metadata and image information
- **Local Caching**: Downloaded images for performance
- **Source Attribution**: Proper linking to original sources

## Project Structure

```
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── config.py             # Configuration management
├── data_manager.py       # Data storage and retrieval
├── image_search.py       # Multi-engine image search
├── bing_visual_search.py # AI-enhanced visual search
├── templates/            # HTML templates
├── static/              # CSS, JavaScript, assets
└── data/                # Image cache and metadata
```

## Environment Variables

- `OPENAI_API_KEY`: Required for AI-enhanced visual search
- `SESSION_SECRET`: Flask session security (optional)
- `FLASK_ENV`: Environment setting (default: development)
- `DEBUG`: Debug mode toggle (default: True)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Recent Updates

### AI-Enhanced Visual Search (July 2025)
- Added OpenAI integration for automatic image analysis
- Created enhanced "Find Similar" modal with keyword input
- Implemented Bing Visual Search for comprehensive similarity matching
- Combined AI insights with user keywords for better precision
- Removed Google API dependencies to eliminate quota limitations

### Multi-Engine Search Implementation
- Integrated DuckDuckGo and Bing image search engines
- Added duplicate detection across search sources
- Maintained proper source attribution and click-through functionality
- Implemented quota-free search methods for unlimited usage

## Support

For issues and questions, please open a GitHub issue in the repository.