$content = Get-Content App.tsx -Raw

# Replace the network configuration section
$content = $content -replace 
'(?s)  // Network detection.*?const NETWORK_ENDPOINTS = \[.*?\];',
@"
  // Enhanced Network Configuration with Auto-Detection
  const NetworkConfig = {
    // Environment detection
    isDevelopment: true, // Set to false for production
    
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
  };"@

# Replace API_BASE initialization
$content = $content -replace 
'  const \[API_BASE, setApiBase\] = useState\(NETWORK_ENDPOINTS\[0\]\.url\);',
'  const [API_BASE, setApiBase] = useState(NetworkConfig.development.fallbackEndpoints[0].url);'

$content | Set-Content App.tsx
Write-Host "✅ Network configuration updated successfully!"
