// Nuclear Biology Reviews - Main JavaScript
// Professional search functionality and interactive features

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Initialize search functionality
    initializeSearch();

    // Initialize smooth scrolling
    initializeSmoothScroll();

    // Initialize review cards animation
    initializeAnimations();

    // Initialize navigation highlighting
    initializeNavigation();

    console.log('Nuclear Biology Reviews app initialized successfully');
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.querySelector('.search-button');
    const reviewsGrid = document.getElementById('reviewsGrid');

    if (searchInput && reviewsGrid) {
        // Real-time search as user types
        searchInput.addEventListener('input', debounce(performSearch, 300));

        // Search on button click
        if (searchButton) {
            searchButton.addEventListener('click', performSearch);
        }

        // Search on Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const reviewsGrid = document.getElementById('reviewsGrid');
    const searchResults = document.getElementById('searchResults');

    if (!searchInput || !reviewsGrid) return;

    const searchTerm = searchInput.value.toLowerCase().trim();
    const reviewCards = reviewsGrid.querySelectorAll('.review-card');

    let visibleCount = 0;
    let matchingReviews = [];

    reviewCards.forEach(card => {
        const title = card.querySelector('h3 a').textContent.toLowerCase();
        const description = card.querySelector('.review-description').textContent.toLowerCase();
        const isVisible = searchTerm === '' || 
                         title.includes(searchTerm) || 
                         description.includes(searchTerm);

        if (isVisible) {
            card.style.display = 'block';
            card.classList.add('fade-in');
            visibleCount++;

            if (searchTerm !== '') {
                matchingReviews.push({
                    title: card.querySelector('h3 a').textContent,
                    url: card.querySelector('h3 a').href,
                    description: card.querySelector('.review-description').textContent
                });
            }
        } else {
            card.style.display = 'none';
            card.classList.remove('fade-in');
        }
    });

    // Update search results summary
    updateSearchResults(searchTerm, visibleCount, matchingReviews);

    // Scroll to results if search was performed
    if (searchTerm !== '') {
        document.getElementById('reviews').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function updateSearchResults(searchTerm, count, matches) {
    const searchResults = document.getElementById('searchResults');
    if (!searchResults) return;

    if (searchTerm === '') {
        searchResults.innerHTML = '';
        return;
    }

    let resultsHTML = `
        <div class="search-summary">
            <h3>Search Results</h3>
            <p>Found <strong>${count}</strong> reviews matching "<strong>${searchTerm}</strong>"</p>
        </div>
    `;

    if (matches.length > 0 && matches.length <= 10) {
        resultsHTML += '<div class="search-matches">';
        matches.slice(0, 10).forEach(match => {
            resultsHTML += `
                <div class="search-match">
                    <h4><a href="${match.url}">${highlightSearchTerm(match.title, searchTerm)}</a></h4>
                    <p>${highlightSearchTerm(match.description, searchTerm)}</p>
                </div>
            `;
        });
        resultsHTML += '</div>';
    }

    searchResults.innerHTML = resultsHTML;
}

function highlightSearchTerm(text, term) {
    if (!term) return text;

    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Debounce function to limit search frequency
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scrolling for navigation links
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animation on scroll for review cards
function initializeAnimations() {
    // Intersection Observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });

        // Observe all review cards
        document.querySelectorAll('.review-card').forEach(card => {
            observer.observe(card);
        });

        // Observe feature cards
        document.querySelectorAll('.feature').forEach(feature => {
            observer.observe(feature);
        });
    }
}

// Navigation highlighting based on scroll position
function initializeNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

    function updateActiveNavigation() {
        let currentSection = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (window.scrollY >= (sectionTop - 200)) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    }

    // Update on scroll
    window.addEventListener('scroll', debounce(updateActiveNavigation, 100));

    // Update on load
    updateActiveNavigation();
}

// Global search function (called by search button onclick)
function searchReviews() {
    performSearch();
}

// Utility function to clear search
function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
        performSearch();
    }
}

// Filter reviews by category (extensible for future use)
function filterReviews(category) {
    const reviewCards = document.querySelectorAll('.review-card');

    reviewCards.forEach(card => {
        const cardCategory = card.querySelector('.review-category');
        if (!category || category === 'all' || 
            (cardCategory && cardCategory.textContent.toLowerCase().includes(category.toLowerCase()))) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Analytics and tracking (placeholder for future implementation)
function trackEvent(category, action, label) {
    // Placeholder for analytics tracking
    console.log('Track:', category, action, label);

    // Example Google Analytics integration:
    // if (typeof gtag !== 'undefined') {
    //     gtag('event', action, {
    //         event_category: category,
    //         event_label: label
    //     });
    // }
}

// Error handling for missing elements
function safeQuerySelector(selector) {
    try {
        return document.querySelector(selector);
    } catch (error) {
        console.warn(`Element not found: ${selector}`);
        return null;
    }
}

// Keyboard accessibility improvements
document.addEventListener('keydown', function(e) {
    // ESC key to clear search
    if (e.key === 'Escape') {
        clearSearch();
    }

    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

// Responsive navigation menu (for future mobile menu implementation)
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('mobile-active');
    }
}

// Performance monitoring
function measurePerformance() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            const navigationTiming = performance.getEntriesByType('navigation')[0];
            console.log('Page Load Time:', navigationTiming.loadEventEnd - navigationTiming.loadEventStart, 'ms');

            // Track search performance
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const startTime = performance.now();
                    // Measure after search completes
                    setTimeout(() => {
                        const endTime = performance.now();
                        console.log('Search Time:', endTime - startTime, 'ms');
                    }, 0);
                });
            }
        });
    }
}

// Initialize performance monitoring in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    measurePerformance();
}

// Export functions for testing (if module system is available)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        performSearch,
        searchReviews,
        clearSearch,
        filterReviews,
        debounce,
        highlightSearchTerm
    };
}