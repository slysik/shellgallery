/**
 * Shell Collection Gallery JavaScript
 * Handles image loading, search, and click-to-source functionality
 */

class ShellGallery {
    constructor() {
        this.currentOffsets = {
            picture_frames: 0,
            shadow_boxes: 0,
            jewelry_boxes: 0,
            display_cases: 0
        };
        
        this.isLoading = {
            picture_frames: false,
            shadow_boxes: false,
            jewelry_boxes: false,
            display_cases: false
        };
        
        this.searchResults = [];
        this.isSearchMode = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.updateCategoryCounts();
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        
        if (searchInput && searchBtn) {
            searchBtn.addEventListener('click', () => this.performSearch());
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
            
            // Clear search when input is empty
            searchInput.addEventListener('input', (e) => {
                if (e.target.value.trim() === '') {
                    this.clearSearch();
                }
            });
        }
        
        // Load more buttons
        document.querySelectorAll('.load-more-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.getAttribute('data-category');
                this.loadMoreImages(category);
            });
        });
        
        // Image upload functionality
        this.setupImageUpload();
    }

    setupImageUpload() {
        const uploadArea = document.getElementById('upload-area');
        const imageUpload = document.getElementById('imageUpload');
        const similarSearchBtn = document.getElementById('similarSearchBtn');

        if (!uploadArea || !imageUpload || !similarSearchBtn) return;

        // Click to upload
        uploadArea.addEventListener('click', () => {
            imageUpload.click();
        });

        // File selection handler
        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleImageUpload(file);
            }
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    imageUpload.files = files;
                    this.handleImageUpload(file);
                }
            }
        });

        // Similar search button
        similarSearchBtn.addEventListener('click', () => {
            this.performSimilarSearch();
        });
    }

    handleImageUpload(file) {
        const uploadPrompt = document.getElementById('upload-prompt');
        const uploadPreview = document.getElementById('upload-preview');
        const previewImg = document.getElementById('preview-img');
        const previewName = document.getElementById('preview-name');
        const similarSearchBtn = document.getElementById('similarSearchBtn');

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewName.textContent = file.name;
            
            uploadPrompt.classList.add('d-none');
            uploadPreview.classList.remove('d-none');
            similarSearchBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
    
    resetImageUpload() {
        const uploadPrompt = document.getElementById('upload-prompt');
        const uploadPreview = document.getElementById('upload-preview');
        
        if (uploadPrompt && uploadPreview) {
            uploadPrompt.classList.remove('d-none');
            uploadPreview.classList.add('d-none');
        }
        
        document.getElementById('similarSearchBtn').disabled = true;
    }

    async performSimilarSearch() {
        const imageUpload = document.getElementById('imageUpload');
        const similarSearchBtn = document.getElementById('similarSearchBtn');
        
        if (!imageUpload.files[0]) {
            alert('Please select an image first');
            return;
        }

        try {
            // Clear previous results first
            this.clearAllCategories();
            
            similarSearchBtn.disabled = true;
            similarSearchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';

            const formData = new FormData();
            formData.append('image', imageUpload.files[0]);

            const response = await fetch('/api/upload-search', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                // Display search results and show success message
                await this.displaySearchResults(data.images || []);
                const imageCount = data.images ? data.images.length : 0;
                this.showSuccess(`Found ${imageCount} similar shell crafts`);
                
                // Clear the image upload
                imageUpload.value = '';
                this.resetImageUpload();
            } else {
                this.showError(`Search failed: ${data.error}`);
            }
        } catch (error) {
            console.error('Similar search error:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            similarSearchBtn.disabled = false;
            similarSearchBtn.innerHTML = '<i class="fas fa-images me-2"></i>Find Similar';
        }
    }

    clearAllCategories() {
        // Clear the results section for new search results
        const resultsSection = document.querySelector('.categories-section');
        if (resultsSection) {
            resultsSection.innerHTML = '<!-- Search results will appear here -->';
        }
    }

    async displaySearchResults(images) {
        const resultsSection = document.querySelector('.categories-section');
        if (!resultsSection || !images || images.length === 0) {
            return;
        }

        // Create search results grid
        const resultsHTML = `
            <div class="search-results-section mb-5">
                <div class="category-header mb-4">
                    <h2 class="category-title">
                        <i class="fas fa-search me-3"></i>
                        Search Results
                        <span class="badge bg-coastal-accent ms-3">${images.length}</span>
                    </h2>
                    <p class="category-description">Your search found these shell craft items</p>
                </div>
                <div class="image-grid" id="search-results-grid">
                    ${images.map(item => `
                        <div class="image-item" data-item-id="${item.id}">
                            <div class="image-card">
                                <img src="/static/images/${item.filename}" 
                                     alt="${item.title || 'Shell craft'}" 
                                     class="img-fluid" 
                                     loading="lazy"
                                     data-bs-toggle="modal" 
                                     data-bs-target="#imageModal"
                                     data-title="${item.title || 'Shell Craft'}"
                                     data-url="${item.source_url || '#'}"
                                     data-platform="${item.platform || 'Unknown'}"
                                     data-category="${item.category || 'Craft'}">
                                <div class="image-overlay">
                                    <div class="overlay-content">
                                        <h6 class="overlay-title">${item.title || 'Shell Craft'}</h6>
                                        <p class="overlay-platform">${item.platform || 'Unknown Source'}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        resultsSection.innerHTML = resultsHTML;
    }

    async loadAllCategories() {
        const categories = ['picture_frames', 'shadow_boxes', 'jewelry_boxes', 'display_cases'];
        
        for (const category of categories) {
            await this.loadCategoryImages(category, 6, 0);
        }
    }
    
    async loadInitialData() {
        // Don't load any images initially - only load when user performs a search
        console.log('Gallery initialized - no initial images loaded');
    }
    
    async loadCategoryImages(category, limit = 6, offset = 0) {
        if (this.isLoading[category]) return;
        
        this.isLoading[category] = true;
        this.showLoading(category, true);
        
        try {
            const response = await fetch(`/api/category/${category}?limit=${limit}&offset=${offset}`);
            const data = await response.json();
            
            if (data.success && data.images) {
                this.renderImages(data.images, category, offset === 0);
                this.currentOffsets[category] = offset + data.images.length;
                
                // Hide load more button if no more images
                if (data.images.length < limit) {
                    this.hideLoadMoreButton(category);
                }
            } else {
                this.showError('Failed to load images for ' + category);
            }
        } catch (error) {
            console.error('Error loading category images:', error);
            this.showError('Network error while loading images');
        } finally {
            this.isLoading[category] = false;
            this.showLoading(category, false);
        }
    }
    
    async loadMoreImages(category) {
        await this.loadCategoryImages(category, 6, this.currentOffsets[category]);
    }
    
    async updateCategoryCounts() {
        // Category sections no longer exist - skip count updates for clean search interface
        console.log('Category counts update skipped - using search-only interface');
    }
    
    async performSearch() {
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a search term');
            return;
        }
        
        // Clear previous results first
        this.clearAllCategories();
        this.showSearchLoading(true);
        
        try {
            // Search for new content based on the query
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    limit: 12
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Display search results and show success message
                await this.displaySearchResults(data.images || []);
                const imageCount = data.images ? data.images.length : 0;
                this.showSuccess(`Found ${imageCount} new shell crafts for "${query}"`);
                
                // Clear the search input
                searchInput.value = '';
            } else {
                this.showError('Search failed: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed due to network error: ' + (error.message || error));
        } finally {
            this.showSearchLoading(false);
        }
    }
    
    clearSearch() {
        this.isSearchMode = false;
        this.searchResults = [];
        
        // Show all categories again
        document.querySelectorAll('.category-section').forEach(section => {
            section.style.display = 'block';
        });
        
        // Hide search results
        const searchResultsSection = document.getElementById('searchResults');
        if (searchResultsSection) {
            searchResultsSection.remove();
        }
    }
    
    displaySearchResults() {
        // Hide category sections
        document.querySelectorAll('.category-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Create or update search results section
        let searchResultsSection = document.getElementById('searchResults');
        if (!searchResultsSection) {
            searchResultsSection = document.createElement('div');
            searchResultsSection.id = 'searchResults';
            searchResultsSection.className = 'category-section mb-5';
            
            const categoriesSection = document.querySelector('.categories-section');
            categoriesSection.insertBefore(searchResultsSection, categoriesSection.firstChild);
        }
        
        const query = document.getElementById('searchInput').value.trim();
        
        searchResultsSection.innerHTML = `
            <div class="category-header">
                <div class="row align-items-center">
                    <div class="col">
                        <h2 class="category-title">
                            <i class="fas fa-search me-3"></i>
                            Search Results for "${query}"
                            <span class="badge bg-coastal-accent ms-3">${this.searchResults.length}</span>
                        </h2>
                        <p class="category-description">Click any image to view the original source</p>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-outline-coastal" onclick="gallery.clearSearch()">
                            <i class="fas fa-times me-2"></i>Clear Search
                        </button>
                    </div>
                </div>
            </div>
            <div class="image-grid" id="search-grid"></div>
        `;
        
        if (this.searchResults.length > 0) {
            this.renderImages(this.searchResults, 'search', true);
        } else {
            this.showEmptyState('search', 'No results found', 'Try different search terms or browse categories below.');
        }
    }
    
    renderImages(images, category, replace = false) {
        let gridId;
        if (category === 'search') {
            gridId = 'search-grid';
        } else {
            // Map category to correct grid ID
            const gridMap = {
                'picture_frames': 'frames-grid',
                'shadow_boxes': 'boxes-grid',
                'jewelry_boxes': 'jewelry-grid',
                'display_cases': 'cases-grid'
            };
            gridId = gridMap[category] || `${category.split('_')[0]}-grid`;
        }
        const grid = document.getElementById(gridId);
        
        if (!grid) {
            console.error(`Grid not found for category: ${category}`);
            return;
        }
        
        if (replace) {
            grid.innerHTML = '';
        }
        
        if (images.length === 0 && replace) {
            this.showEmptyState(category);
            return;
        }
        
        images.forEach(image => {
            const imageCard = this.createImageCard(image);
            grid.appendChild(imageCard);
        });
    }
    
    createImageCard(imageData) {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.setAttribute('data-image-id', imageData.id);
        
        // Determine image source
        const imageUrl = imageData.local_image 
            ? `/images/${imageData.local_image}` 
            : imageData.image_url;
        
        // Platform badge styling
        const platformClass = `platform-${imageData.platform || 'blog'}`;
        
        // Category display name
        const categoryName = this.getCategoryDisplayName(imageData.category);
        
        card.innerHTML = `
            <img src="${imageUrl}" 
                 alt="${imageData.title || 'Shell craft project'}" 
                 loading="lazy"
                 onerror="this.src='data:image/svg+xml,<svg xmlns=\\"http://www.w3.org/2000/svg\\" width=\\"300\\" height=\\"250\\" viewBox=\\"0 0 300 250\\"><rect width=\\"300\\" height=\\"250\\" fill=\\"%23f8f9fa\\"/><text x=\\"150\\" y=\\"125\\" text-anchor=\\"middle\\" fill=\\"%236c757d\\" font-family=\\"Arial\\" font-size=\\"14\\">Image not available</text></svg>'">
            <div class="source-info">
                <i class="fas fa-external-link-alt me-1"></i>
                Click to view source
            </div>
            <div class="image-card-content">
                <h5 class="image-card-title">${imageData.title || 'Shell Craft Project'}</h5>
                <p class="image-card-description">${imageData.description || 'Beautiful handcrafted shell project'}</p>
                <div class="image-card-meta">
                    <span class="platform-badge ${platformClass}">
                        <i class="fas fa-${this.getPlatformIcon(imageData.platform)} me-1"></i>
                        ${imageData.platform || 'Source'}
                    </span>
                    <span class="badge bg-coastal-secondary">${categoryName}</span>
                </div>
            </div>
        `;
        
        // Add click handler for source linking
        card.addEventListener('click', () => this.handleImageClick(imageData));
        
        return card;
    }
    
    handleImageClick(imageData) {
        // Primary action: Open source URL
        if (imageData.source_url) {
            window.open(imageData.source_url, '_blank', 'noopener,noreferrer');
        }
        
        // Secondary action: Show modal with details
        this.showImageModal(imageData);
    }
    
    showImageModal(imageData) {
        const modal = document.getElementById('imageModal');
        if (!modal) return;
        
        // Populate modal content
        const modalImage = document.getElementById('modalImage');
        const modalTitle = document.getElementById('modalTitle');
        const modalDescription = document.getElementById('modalDescription');
        const modalPlatform = document.getElementById('modalPlatform');
        const modalCategory = document.getElementById('modalCategory');
        const modalSourceBtn = document.getElementById('modalSourceBtn');
        
        const imageUrl = imageData.local_image 
            ? `/images/${imageData.local_image}` 
            : imageData.image_url;
        
        modalImage.src = imageUrl;
        modalImage.alt = imageData.title || 'Shell craft project';
        modalTitle.textContent = imageData.title || 'Shell Craft Project';
        modalDescription.textContent = imageData.description || 'Beautiful handcrafted shell project';
        modalPlatform.textContent = imageData.platform || 'Source';
        modalCategory.textContent = this.getCategoryDisplayName(imageData.category);
        
        // Source button
        modalSourceBtn.onclick = () => {
            if (imageData.source_url) {
                window.open(imageData.source_url, '_blank', 'noopener,noreferrer');
            }
        };
        
        // Show modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    getCategoryDisplayName(category) {
        const displayNames = {
            'picture_frames': 'Picture Frames',
            'shadow_boxes': 'Shadow Boxes',
            'jewelry_boxes': 'Jewelry Boxes',
            'display_cases': 'Display Cases'
        };
        return displayNames[category] || category;
    }
    
    getPlatformIcon(platform) {
        const icons = {
            'pinterest': 'map-pin',
            'etsy': 'store',
            'blog': 'globe'
        };
        return icons[platform] || 'link';
    }
    
    showEmptyState(category, title = 'No items found', message = 'Click "Find New Crafts" to discover content.') {
        let gridId;
        if (category === 'search') {
            gridId = 'search-grid';
        } else {
            // Map category to correct grid ID
            const gridMap = {
                'picture_frames': 'frames-grid',
                'shadow_boxes': 'boxes-grid',
                'jewelry_boxes': 'jewelry-grid',
                'display_cases': 'cases-grid'
            };
            gridId = gridMap[category] || `${category.split('_')[0]}-grid`;
        }
        const grid = document.getElementById(gridId);
        
        if (!grid) return;
        
        grid.innerHTML = `
            <div class="empty-state col-12">
                <i class="fas fa-shell-icon"></i>
                <h3>${title}</h3>
                <p>${message}</p>
            </div>
        `;
    }
    
    showLoading(category, show) {
        // Map category to correct loading ID
        const loadingMap = {
            'picture_frames': 'frames-loading',
            'shadow_boxes': 'boxes-loading', 
            'jewelry_boxes': 'jewelry-loading',
            'display_cases': 'cases-loading'
        };
        const loadingId = loadingMap[category] || `${category.split('_')[0]}-loading`;
        const loadingElement = document.getElementById(loadingId);
        
        if (loadingElement) {
            loadingElement.style.display = show ? 'block' : 'none';
        }
    }
    
    showSearchLoading(show) {
        const searchBtn = document.getElementById('searchBtn');
        if (!searchBtn) return;
        
        if (show) {
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
            searchBtn.disabled = true;
        } else {
            searchBtn.innerHTML = 'Search';
            searchBtn.disabled = false;
        }
    }
    
    hideLoadMoreButton(category) {
        const button = document.querySelector(`[data-category="${category}"]`);
        if (button) {
            button.style.display = 'none';
        }
    }
    
    async scrapeNewContent() {
        const scrapeBtn = document.getElementById('scrapeBtn');
        if (!scrapeBtn) return;
        
        // Update button state
        const originalHTML = scrapeBtn.innerHTML;
        scrapeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Finding New Crafts...';
        scrapeBtn.disabled = true;
        
        try {
            const response = await fetch('/api/scrape?category=all&limit=5');
            const data = await response.json();
            
            if (data.success) {
                let totalNew = 0;
                Object.values(data.results).forEach(count => totalNew += count);
                
                if (totalNew > 0) {
                    this.showSuccess(`Found ${totalNew} new shell craft projects!`);
                    
                    // Refresh category counts and reload images
                    await this.updateCategoryCounts();
                    await this.loadInitialData();
                } else {
                    this.showSuccess('No new content found. Check back later!');
                }
            } else {
                this.showError('Failed to find new content: ' + data.error);
            }
        } catch (error) {
            console.error('Scraping error:', error);
            this.showError('Failed to find new content due to network error');
        } finally {
            // Restore button state
            scrapeBtn.innerHTML = originalHTML;
            scrapeBtn.disabled = false;
        }
    }
    
    showSearchLoading(show) {
        // You can add loading state UI here if needed
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            if (show) {
                searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
                searchBtn.disabled = true;
            } else {
                searchBtn.innerHTML = 'Search';
                searchBtn.disabled = false;
            }
        }
    }

    showError(message) {
        this.showToast('errorToast', message);
    }
    
    showSuccess(message) {
        this.showToast('successToast', message);
    }
    
    showToast(toastId, message) {
        const toast = document.getElementById(toastId);
        const toastBody = document.getElementById(toastId.replace('Toast', 'ToastBody'));
        
        if (toast && toastBody) {
            toastBody.textContent = message;
            const bootstrapToast = new bootstrap.Toast(toast);
            bootstrapToast.show();
        }
    }
}

// Initialize gallery when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gallery = new ShellGallery();
});

// Error handling for image loading failures
document.addEventListener('error', (e) => {
    if (e.target.tagName === 'IMG') {
        console.warn('Image failed to load:', e.target.src);
        // Fallback handled in HTML onerror attribute
    }
}, true);

// Performance optimization: Intersection Observer for lazy loading
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    });
    
    // Observe all images with data-src attribute
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    });
}
