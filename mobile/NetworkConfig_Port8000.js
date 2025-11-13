// Network Configuration Update for DeliveryApp Mobile
// Updates primary endpoints to use port 8000 (current working Django server)

const CONFIG = {
  // Primary endpoints (in priority order) - UPDATED FOR PORT 8000
  ENDPOINTS: [
    'http://192.168.1.77:8000',  // Current working server IP
    'http://127.0.0.1:8000',     // Localhost 
    'http://192.168.1.79:8000',  // Alternative IP on port 8000
    'http://192.168.1.77:8081',  // Fallback to original port
    'http://192.168.1.79:8081',  // Alternative mobile IP
  ],

  // Connection settings
  TIMEOUT: 5000,      // 5 second timeout for endpoint tests
  RETRY_DELAY: 1000,  // 1 second between retries
  MAX_RETRIES: 2,     // Maximum retry attempts

  // API paths
  PATHS: {
    AUTH: '/api/token/',
    REFRESH: '/api/token/refresh/',
    DELIVERIES: '/api/deliveries/',
    CUSTOMERS: '/api/customers/',
    DRIVERS: '/api/drivers/',
    VEHICLES: '/api/vehicles/',
    ASSIGNMENTS: '/api/assignments/',
    DRIVER_VEHICLES: '/api/driver-vehicles/',
  }
};

class NetworkManager {
  constructor() {
    this.baseURL = null;
    this.isChecking = false;
  }

  // Test endpoint connectivity
  async testEndpoint(endpoint) {
    try {
      console.log(`🔗 Testing endpoint: ${endpoint}`);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);

      const response = await fetch(`${endpoint}/api/deliveries/`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 401 || response.status === 200) {
        // 401 = Auth required (server is working)
        // 200 = Success (if no auth required)
        console.log(`✅ Endpoint accessible: ${endpoint}`);
        return true;
      }

      console.log(`⚠️ Endpoint returned ${response.status}: ${endpoint}`);
      return false;

    } catch (error) {
      console.log(`❌ Endpoint failed: ${endpoint} - ${error.message}`);
      return false;
    }
  }

  // Find the best working endpoint
  async detectBestEndpoint() {
    if (this.isChecking) {
      console.log('🔄 Endpoint detection already in progress...');
      return this.baseURL;
    }

    this.isChecking = true;
    console.log('🌐 Starting endpoint detection...');

    try {
      for (const endpoint of CONFIG.ENDPOINTS) {
        const isWorking = await this.testEndpoint(endpoint);
        if (isWorking) {
          this.baseURL = endpoint;
          console.log(`🎯 Selected endpoint: ${endpoint}`);
          return endpoint;
        }
      }

      // No endpoints working
      console.error('❌ No working endpoints found!');
      this.baseURL = CONFIG.ENDPOINTS[0]; // Use first as fallback
      return this.baseURL;

    } finally {
      this.isChecking = false;
    }
  }

  // Get current base URL (with auto-detection)
  async getBaseURL() {
    if (!this.baseURL) {
      await this.detectBestEndpoint();
    }
    return this.baseURL;
  }

  // Build full API URL
  async buildURL(path) {
    const baseURL = await this.getBaseURL();
    return `${baseURL}${path}`;
  }

  // Force refresh endpoint detection
  async refreshEndpoints() {
    console.log('🔄 Forcing endpoint refresh...');
    this.baseURL = null;
    return await this.detectBestEndpoint();
  }

  // Get current status
  getStatus() {
    return {
      currentEndpoint: this.baseURL,
      isChecking: this.isChecking,
      availableEndpoints: CONFIG.ENDPOINTS,
    };
  }
}

// Global network manager instance
const networkManager = new NetworkManager();

// Enhanced API helper with automatic retry and endpoint switching
export const apiRequest = async (path, options = {}) => {
  let lastError;

  for (let attempt = 0; attempt <= CONFIG.MAX_RETRIES; attempt++) {
    try {
      const baseURL = await networkManager.getBaseURL();
      const url = `${baseURL}${path}`;

      console.log(`📡 API Request [Attempt ${attempt + 1}]: ${options.method || 'GET'} ${url}`);

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ API Success: ${options.method || 'GET'} ${path}`);
      return { success: true, data };

    } catch (error) {
      lastError = error;
      console.log(`❌ API Error [Attempt ${attempt + 1}]: ${error.message}`);

      if (attempt < CONFIG.MAX_RETRIES) {
        console.log(`⏳ Retrying in ${CONFIG.RETRY_DELAY}ms...`);
        await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY));

        // Try refreshing endpoints on network errors
        if (error.message.includes('Network') || error.message.includes('fetch')) {
          await networkManager.refreshEndpoints();
        }
      }
    }
  }

  console.error(`💥 API Failed after ${CONFIG.MAX_RETRIES + 1} attempts:`, lastError);
  return {
    success: false,
    error: lastError?.message || 'Network request failed',
    details: lastError
  };
};

// Export everything
export { CONFIG, networkManager };
export default { apiRequest, networkManager, CONFIG };