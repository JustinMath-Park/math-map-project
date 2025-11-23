/**
 * Application Configuration
 * Automatically detects environment (development/production)
 */

const Config = (() => {
  const ENV = {
    DEVELOPMENT: 'development',
    PRODUCTION: 'production',
  };

  // Detect environment
  const isLocalhost = window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '';

  const currentEnv = isLocalhost ? ENV.DEVELOPMENT : ENV.PRODUCTION;

  // Configuration by environment
  const config = {
    [ENV.DEVELOPMENT]: {
      API_BASE: 'http://localhost:5001',
      USE_LOCAL_DATA: true,
      DEBUG: true,
    },
    [ENV.PRODUCTION]: {
      API_BASE: '', // Will use relative paths or Firebase Functions
      USE_LOCAL_DATA: true, // Use bundled data in production
      DEBUG: false,
    },
  };

  const current = config[currentEnv];

  return {
    ENV: currentEnv,
    API_BASE: current.API_BASE,
    USE_LOCAL_DATA: current.USE_LOCAL_DATA,
    DEBUG: current.DEBUG,

    // Endpoints
    CURRICULUMS_ENDPOINT: current.USE_LOCAL_DATA ? './data/curriculums.json' : (current.API_BASE ? `${current.API_BASE}/curriculums` : './data/curriculums.json'),
    LECTURES_ENDPOINT: (id) => current.USE_LOCAL_DATA ? './data/lectures.json' : (current.API_BASE ? `${current.API_BASE}/lectures/${id}` : './data/lectures.json'),

    // Paths
    LOCAL_CURRICULUMS: './data/curriculums.json',
    LOCAL_LECTURES: './data/lectures.json',

    // App settings
    APP_VERSION: 'v0.3.3.07',
    APP_NAME: 'Mathiter Curriculum Navigator',

    log(...args) {
      if (this.DEBUG) {
        console.log('[Config]', ...args);
      }
    },

    warn(...args) {
      if (this.DEBUG) {
        console.warn('[Config]', ...args);
      }
    },
  };
})();

// Make it available globally
if (typeof window !== 'undefined') {
  window.Config = Config;
}

// Log current configuration
Config.log('Environment:', Config.ENV);
Config.log('API Base:', Config.API_BASE);
Config.log('Use Local Data:', Config.USE_LOCAL_DATA);
