// Enhanced Network Configuration with Auto-Detection
const NetworkConfig = {
  // Environment detection
  isDevelopment: __DEV__ || process.env.NODE_ENV === 'development',
  
  // Development: Auto-detect + fallbacks
  development: {
    autoDetect: true,
    scanTimeout: 2000,
    commonPorts: [8081, 8080, 3000, 8000],
    fallbackEndpoints: [
      { url: 'http://192.168.1.85:8081', name: 'Current Network IP' },
      { url: 'http://192.168.1.87:8081', name: 'Home Office Network' },
      { url: 'http://192.168.1.82:8081', name: 'Home Office Network (Alt)' },
      { url: 'http://10.0.0.1:8081', name: 'Router Default' },
      { url: 'http://172.20.10.6:8081', name: 'Mobile Hotspot' },
      { url: 'http://localhost:8081', name: 'Localhost' }
    ]
  },
  
  // Production: Static URLs
  production: {
    baseURL: 'https://api.deliveryapp.com',
    fallbackURL: 'https://api-backup.deliveryapp.com',
    autoDetect: false
  }
};

// Auto-detect network IP from device
const getCurrentDeviceIP = async () => {
  try {
    // Method 1: Try to get IP from a network info service
    const response = await fetch('https://api.ipify.org?format=json', { timeout: 3000 });
    const data = await response.json();
    return data.ip;
  } catch {
    return null;
  }
};

// Smart network scanning for development
const scanLocalNetwork = async () => {
  const { commonPorts, scanTimeout } = NetworkConfig.development;
  
  // Get base IP ranges to scan
  const ipRanges = [
    '192.168.1.',   // Most common home network
    '192.168.0.',   // Alternative home network
    '10.0.0.',      // Some routers
    '172.20.10.'    // Mobile hotspot range
  ];
  
  for (const baseIP of ipRanges) {
    for (let i = 1; i <= 20; i++) { // Scan first 20 IPs (most common)
      for (const port of commonPorts) {
        try {
          const testURL = http://:;
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), scanTimeout);
          
          const response = await fetch(${testURL}/api/, {
            method: 'GET',
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (response.status === 401 || response.status === 200) {
            return { 
              url: testURL, 
              name: Auto-detected (:) 
            };
          }
        } catch (e) {
          // Continue scanning
        }
      }
    }
  }
  return null;
};

// Enhanced backend detection
const checkBackendSmart = async () => {
  setBackendStatus('🔍 Auto-detecting network...');
  setCurrentNetwork('Scanning...');
  
  try {
    if (NetworkConfig.isDevelopment) {
      // Development: Try auto-detection first
      const detected = await scanLocalNetwork();
      
      if (detected) {
        setApiBase(detected.url);
        setCurrentNetwork(detected.name);
        setBackendStatus(✅ Auto-detected: );
        return;
      }
      
      // Fallback to predefined endpoints
      for (const endpoint of NetworkConfig.development.fallbackEndpoints) {
        try {
          const response = await fetch(${endpoint.url}/api/, {
            method: 'GET',
            timeout: 3000
          });
          
          if (response.status === 401 || response.status === 200) {
            setApiBase(endpoint.url);
            setCurrentNetwork(endpoint.name);
            setBackendStatus(✅ Connected: );
            return;
          }
        } catch (error) {
          continue;
        }
      }
    } else {
      // Production: Use static URLs
      try {
        const response = await fetch(${NetworkConfig.production.baseURL}/api/);
        if (response.status === 401 || response.status === 200) {
          setApiBase(NetworkConfig.production.baseURL);
          setCurrentNetwork('Production Server');
          setBackendStatus('✅ Connected to Production');
          return;
        }
      } catch {
        // Try fallback
        const response = await fetch(${NetworkConfig.production.fallbackURL}/api/);
        if (response.status === 401 || response.status === 200) {
          setApiBase(NetworkConfig.production.fallbackURL);
          setCurrentNetwork('Production Server (Backup)');
          setBackendStatus('✅ Connected to Backup');
          return;
        }
      }
    }
    
    setBackendStatus('❌ No backend found');
    setCurrentNetwork('None');
  } catch (error) {
    setBackendStatus('❌ Network error');
    setCurrentNetwork('Error');
  }
};
