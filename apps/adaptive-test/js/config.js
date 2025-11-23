const CONFIG = {
    VERSION: 'v1.0.9', // App Version
    // Auto-detect environment
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:5001'
        : 'https://mathiter-backend-1093137562151.us-central1.run.app', // Production Backend URL
    TEST_LENGTH: 3
};

// Auto-detect backend URL based on environment
if (window.location.hostname.includes('firebaseapp.com') || window.location.hostname.includes('web.app')) {
    CONFIG.API_BASE_URL = 'https://mathiter-backend-1093137562151.us-central1.run.app';
}
