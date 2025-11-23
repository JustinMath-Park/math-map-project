const CONFIG = {
    VERSION: 'v1.0.9', // App Version
    API_BASE_URL: 'http://localhost:5001', // Default to local backend for dev
    TEST_LENGTH: 3
};

// Auto-detect backend URL based on environment
if (window.location.hostname.includes('firebaseapp.com') || window.location.hostname.includes('web.app')) {
    CONFIG.API_BASE_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';
}
