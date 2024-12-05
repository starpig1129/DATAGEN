// API Configuration
const config = {
    // Dynamically get the base URL from the current window location
    apiBaseUrl: `${window.location.protocol}//${window.location.host}`,
};

// Expose config globally
window.apiConfig = config;
