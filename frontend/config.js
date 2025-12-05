// Frontend configuration - handles backend URL dynamically
// This allows the frontend to be deployed separately from the backend

// Get backend URL from localStorage (set by loader.html) or use default
function getBackendUrl() {
    // For production: Use the backend URL set by loader
    const storedBackendUrl = localStorage.getItem('backendUrl');
    
    // For development: Check if we're running locally
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1';
    
    if (isDevelopment) {
        // Local development - backend on same server
        return window.location.origin;
    }
    
    if (storedBackendUrl) {
        // Production - use stored backend URL
        return storedBackendUrl;
    }
    
    // Fallback - same origin (works if frontend/backend are together)
    return window.location.origin;
}

// Export for use in other files
window.APP_CONFIG = {
    backendUrl: getBackendUrl(),
    
    // Helper method to build API URLs
    apiUrl: function(endpoint) {
        // Remove leading slash if present to avoid double slashes
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
        return `${this.backendUrl}/${cleanEndpoint}`;
    }
};

// Log configuration on load (helpful for debugging)
console.log('🔧 App Configuration:', {
    backendUrl: window.APP_CONFIG.backendUrl,
    environment: window.location.hostname === 'localhost' ? 'development' : 'production'
});
