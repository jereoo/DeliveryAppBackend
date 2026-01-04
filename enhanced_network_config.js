import * as FileSystem from 'expo-file-system';

// Enhanced Network Configuration with Auto-Detection
const NetworkConfig = {
  // Environment detection
  isDevelopment: __DEV__ || process.env.NODE_ENV === 'development',

  // Development: Auto-detect + fallbacks
  development: {
    autoDetect: true,
    scanTimeout: 2000,
    commonPorts: [8000, 8080, 3000],
    fallbackEndpoints: [
      { url: 'http://localhost:8000', name: 'Current Network IP' },
      { url: 'http://localhost:8000', name: 'Home Office Network' },
      { url: 'http://localhost:8000', name: 'Home Office Network (Alt)' },
      { url: 'http://localhost:8000', name: 'Router Default' },
      { url: 'http://localhost:8000', name: 'Mobile Hotspot' },
      { url: 'http://localhost:8000', name: 'Localhost' }
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

  const ipRanges = [
    '192.168.1.',
    '192.168.0.',
    '10.0.0.',
    '172.20.10.'
  ];

  for (const baseIP of ipRanges) {
    for (let i = 1; i <= 20; i++) {
      for (const port of commonPorts) {
        try {
          const testURL = `http://${baseIP}${i}:${port}`;
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), scanTimeout);

          const response = await fetch(`${testURL}/api/`, {
            method: 'GET',
            signal: controller.signal
          });

          clearTimeout(timeoutId);

          if (response.status === 401 || response.status === 200) {
            return {
              url: testURL,
              name: `Auto-detected (${baseIP}${i}:${port})`
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
      const detected = await scanLocalNetwork();

      if (detected) {
        setApiBase(detected.url);
        setCurrentNetwork(detected.name);
        setBackendStatus(`✅ Auto-detected: ${detected.url}`);
        return;
      }

      for (const endpoint of NetworkConfig.development.fallbackEndpoints) {
        try {
          const response = await fetch(`${endpoint.url}/api/`, {
            method: 'GET',
            timeout: 3000
          });

          if (response.status === 401 || response.status === 200) {
            setApiBase(endpoint.url);
            setCurrentNetwork(endpoint.name);
            setBackendStatus(`✅ Connected: ${endpoint.url}`);
            return;
          }
        } catch (error) {
          continue;
        }
      }
    } else {
      try {
        const response = await fetch(`${NetworkConfig.production.baseURL}/api/`);
        if (response.status === 401 || response.status === 200) {
          setApiBase(NetworkConfig.production.baseURL);
          setCurrentNetwork('Production Server');
          setBackendStatus('✅ Connected to Production');
          return;
        }
      } catch {
        const response = await fetch(`${NetworkConfig.production.fallbackURL}/api/`);
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

// Enhanced backend detection with dynamic IP auto-detection
const initializeBackendConnection = async () => {
  try {
    const detected = await scanLocalNetwork();
    if (detected) {
      API_BASE_URL = detected.url; // Dynamically set the backend URL
      console.log(`Connected to backend at ${API_BASE_URL}`);
    } else {
      console.error("Failed to detect backend server.");
    }
  } catch (error) {
    console.error("Error during backend detection:", error);
  }
};

// Call this function during app initialization
initializeBackendConnection();

// Error logging functionality
const logErrorToFile = async (errorMessage) => {
  const logFilePath = `${FileSystem.documentDirectory}ERR/error_log.txt`;
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${errorMessage}\n`;

  try {
    await FileSystem.writeAsStringAsync(logFilePath, logMessage, { append: true });
    console.log("Error logged to file:", logFilePath);
  } catch (err) {
    console.error("Failed to log error to file:", err);
  }
};

// Example usage in an API call
const fetchData = async () => {
  try {
    const response = await fetch(API_BASE_URL + "endpoint");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    logErrorToFile(error.message);
    throw error;
  }
};
