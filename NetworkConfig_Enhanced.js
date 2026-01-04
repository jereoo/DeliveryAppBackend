// 🚀 Enhanced Network Configuration for DeliveryApp Mobile
// This file contains the smart auto-detection system for development environments
// 
// IMPLEMENTATION GUIDE:
// 1. Replace the NETWORK_ENDPOINTS section in App.tsx with this configuration
// 2. Replace the checkBackend() function with checkBackendSmart()
// 3. Update the useEffect to call the new function

// =============================================================================
// ENHANCED NETWORK CONFIGURATION
// =============================================================================

const NetworkConfig = {
  // Environment detection - automatically switches between dev and production
  isDevelopment: true, // Change to false for production builds

  // Development Configuration - Auto-detection with fallbacks
  development: {
    autoDetect: true,
    scanTimeout: 2000,          // 2 seconds per network scan
    maxConcurrentScans: 3,      // Scan 3 IPs at once for speed
    commonPorts: [8081, 8080, 3000, 8000, 5000],

    // Primary endpoints (in priority order)
    ENDPOINTS: [
      'http://192.168.1.85:8000',  // Current server IP (from Django startup)
      'http://127.0.0.1:8000',     // Localhost 
      'http://localhost:8000',  // Alternative mobile IP
    ],    // IP ranges to auto-scan
    scanRanges: [
      { base: '192.168.1.', start: 80, end: 90, name: 'Home Network Range' },
      { base: '192.168.0.', start: 1, end: 10, name: 'Alt Home Range' },
      { base: '10.0.0.', start: 1, end: 20, name: 'Corporate Range' },
      { base: '172.20.10.', start: 1, end: 20, name: 'Hotspot Range' }
    ]
  },

  // Production Configuration - Static, reliable URLs
  production: {
    baseURL: 'https://api.deliveryapp.com',
    fallbackURL: 'https://api-backup.deliveryapp.com',
    healthCheckURL: 'https://status.deliveryapp.com',
    autoDetect: false,
    useHTTPS: true
  }
};

// =============================================================================
// SMART NETWORK DETECTION FUNCTIONS
// =============================================================================

// Get current device IP (optional enhancement)
const getCurrentDeviceIP = async () => {
  try {
    const response = await fetch('https://api.ipify.org?format=json', {
      timeout: 3000
    });
    const data = await response.json();
    return data.ip;
  } catch {
    return null;
  }
};

// Parallel network scanning for speed
const scanLocalNetworkParallel = async () => {
  const { scanRanges, commonPorts, scanTimeout } = NetworkConfig.development;
  const promises = [];

  for (const range of scanRanges) {
    for (let i = range.start; i <= range.end; i++) {
      for (const port of commonPorts) {
        const testURL = `http://${range.base}${i}:${port}`;

        promises.push(
          testEndpoint(testURL, scanTimeout).then(result =>
            result ? {
              url: testURL,
              name: `Auto-detected (${range.name})`
            } : null
          )
        );

        // Limit concurrent requests to avoid overwhelming network
        if (promises.length >= NetworkConfig.development.maxConcurrentScans) {
          const results = await Promise.allSettled(promises);
          const found = results.find(r => r.status === 'fulfilled' && r.value);
          if (found) return found.value;
          promises.length = 0; // Clear array
        }
      }
    }
  }

  // Check remaining promises
  if (promises.length > 0) {
    const results = await Promise.allSettled(promises);
    const found = results.find(r => r.status === 'fulfilled' && r.value);
    if (found) return found.value;
  }

  return null;
};

// Test individual endpoint with timeout
const testEndpoint = async (url, timeout) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(`${url}/api/`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      }
    });

    clearTimeout(timeoutId);

    // Accept both 200 (success) and 401 (unauthorized but server exists)
    return response.status === 200 || response.status === 401;
  } catch (e) {
    return false;
  }
};

// =============================================================================
// MAIN DETECTION FUNCTION - Replace checkBackend() with this
// =============================================================================

const checkBackendSmart = async () => {
  setBackendStatus('🔍 Smart network detection...');
  setCurrentNetwork('Scanning...');

  try {
    if (NetworkConfig.isDevelopment) {
      console.log('🔧 Development mode: Starting smart network detection');

      // Phase 1: Try parallel auto-detection (fastest)
      if (NetworkConfig.development.autoDetect) {
        setBackendStatus('🚀 Auto-scanning network ranges...');
        const detected = await scanLocalNetworkParallel();

        if (detected) {
          setApiBase(detected.url);
          setCurrentNetwork(detected.name);
          setBackendStatus(`✅ Auto-detected: ${detected.name}`);
          console.log(`🎯 Auto-detected backend: ${detected.url}`);
          return;
        }
      }

      // Phase 2: Try predefined endpoints (fallback)
      setBackendStatus('🔄 Checking known endpoints...');
      const sortedEndpoints = NetworkConfig.development.fallbackEndpoints
        .sort((a, b) => a.priority - b.priority);

      for (const endpoint of sortedEndpoints) {
        try {
          const isValid = await testEndpoint(endpoint.url, 3000);

          if (isValid) {
            setApiBase(endpoint.url);
            setCurrentNetwork(endpoint.name);
            setBackendStatus(`✅ Connected: ${endpoint.name}`);
            console.log(`🎯 Connected to: ${endpoint.url}`);
            return;
          }
        } catch (error) {
          console.log(`❌ Failed: ${endpoint.url}`, error.message);
          continue;
        }
      }

      // Phase 3: No backend found
      setBackendStatus('❌ No backend found in development');
      setCurrentNetwork('None');
      console.log('💥 No backend server found. Please start Django server.');

    } else {
      // Production mode
      console.log('🏭 Production mode: Using static URLs');
      setBackendStatus('🔄 Connecting to production...');

      try {
        // Try main production URL
        const isValid = await testEndpoint(NetworkConfig.production.baseURL, 5000);
        if (isValid) {
          setApiBase(NetworkConfig.production.baseURL);
          setCurrentNetwork('Production Server');
          setBackendStatus('✅ Connected to Production');
          return;
        }

        // Try fallback URL
        const isFallbackValid = await testEndpoint(NetworkConfig.production.fallbackURL, 5000);
        if (isFallbackValid) {
          setApiBase(NetworkConfig.production.fallbackURL);
          setCurrentNetwork('Production Server (Backup)');
          setBackendStatus('✅ Connected to Backup Server');
          return;
        }

        setBackendStatus('❌ Production servers unavailable');
        setCurrentNetwork('Offline');

      } catch (error) {
        setBackendStatus('❌ Production connection failed');
        setCurrentNetwork('Error');
      }
    }

  } catch (error) {
    setBackendStatus('❌ Network detection failed');
    setCurrentNetwork('Error');
    console.error('Network detection error:', error);
  }
};

// =============================================================================
// USAGE INSTRUCTIONS
// =============================================================================

/*
TO IMPLEMENT THIS ENHANCED NETWORK SYSTEM:

1. REPLACE this section in App.tsx:
   ```
   // Network detection
   const NETWORK_ENDPOINTS = [
     { url: 'http://localhost:8000', name: 'Home Office Network' },
     // ... etc
   ];
   ```
   
   WITH:
   ```
   // Enhanced Network Configuration with Auto-Detection
   const NetworkConfig = { ... }; // (copy from above)
   ```

2. REPLACE this line:
   ```
   const [API_BASE, setApiBase] = useState(NETWORK_ENDPOINTS[0].url);
   ```
   
   WITH:
   ```
   const [API_BASE, setApiBase] = useState(
     NetworkConfig.development.fallbackEndpoints[0].url
   );
   ```

3. REPLACE the checkBackend function:
   ```
   const checkBackend = async () => { ... };
   ```
   
   WITH:
   ```
   const checkBackendSmart = async () => { ... }; // (copy from above)
   ```

4. UPDATE the useEffect call:
   ```
   checkBackend(); → checkBackendSmart();
   ```

5. UPDATE button handlers:
   ```
   onPress={checkBackend} → onPress={checkBackendSmart}
   ```

BENEFITS:
✅ Automatic IP detection - no more manual updates needed
✅ Handles IP changes in development environments  
✅ Smart fallback system with priority ordering
✅ Parallel scanning for faster detection
✅ Production/development environment switching
✅ Comprehensive error handling and logging
✅ Future-proof for deployment scenarios

*/

export default NetworkConfig;
