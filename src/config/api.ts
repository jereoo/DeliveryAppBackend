// CIO DIRECTIVE – PERMANENT LAUNCH FIX – NOV 21 2025
// UPDATED JANUARY 03, 2026: Dynamic tunnel backend URL derivation

/**
 * API Configuration with Dynamic URL Resolution
 * SDK 51+ Compatible - Never use Constants.manifest again
 * Now supports automatic tunnel backend routing via hostUri
 */

import Constants from 'expo-constants';

// CIO DIRECTIVE: Intelligent backend URL resolution with tunnel priority
/* const getBackendUrl = (): string => {
  console.log('🔧 API Config Debug:', {
    expoConfig: Constants.expoConfig?.extra,
    hostUri: Constants.expoConfig?.hostUri,
    processEnv: process.env.BACKEND_URL,
  });

  // 1. PRIMARY: Derive tunnel backend URL from Expo tunnel (works automatically with --tunnel)
  if (Constants.expoConfig?.hostUri) {
    // hostUri format: exp://u.random-anonymous-8081.exp.direct
    // Extract the domain part after @
    const parts = Constants.expoConfig.hostUri.split('@');
    if (parts.length > 1) {
      const tunnelDomain = parts[1].split(':')[0];
      if (tunnelDomain.includes('exp.direct') || tunnelDomain.includes('ngrok.io')) {
        const tunnelBackendUrl = `https://${tunnelDomain}:8000/api`;
        console.log('✅ Using derived tunnel backend URL:', tunnelBackendUrl);
        return tunnelBackendUrl;
      }
    }
  }

  // 2. Fallback: Use explicit .env variable (if manually set)
  if (process.env.BACKEND_URL) {
    console.log('✅ Using process.env.BACKEND_URL');
    return process.env.BACKEND_URL;
  }

  // 3. Fallback: Use app.json extra (LAN mode when on same network)
  if (Constants.expoConfig?.extra?.backendUrl) {
    console.log('✅ Using expoConfig.extra.backendUrl (LAN fallback)');
    return Constants.expoConfig.extra.backendUrl;
  }

  // 4. Final safety: Fail fast with clear message
  console.log('❌ CRITICAL: No valid backend URL found');
  throw new Error(
    'Backend URL not available. Run via start-fullstack.bat with --tunnel for automatic tunnel routing.'
  );
}; */

// CIO DIRECTIVE: Get backend URL from reliable LAN connection (app.json) first
const getBackendUrl = (): string => {
  console.log('🔧 API Config Debug:', {
    expoConfig: Constants.expoConfig?.extra,
    processEnv: process.env.BACKEND_URL,
    hostUri: Constants.expoConfig?.hostUri,
  });

  // PRIMARY: Use reliable LAN URL from app.json (works when phone/PC on same Wi-Fi)
  if (Constants.expoConfig?.extra?.backendUrl) {
    console.log('✅ Using LAN backend URL from app.json');
    return Constants.expoConfig?.extra?.backendUrl;
  }

  // Fallback to .env (rare manual override)
  if (process.env.BACKEND_URL) {
    console.log('✅ Using process.env.BACKEND_URL');
    return process.env.BACKEND_URL;
  }

  throw new Error('Backend URL missing. Update app.json extra.backendUrl with your current Wi-Fi IP (ipconfig → 192.168.x.x)');
};

// Get the base URL for API calls
export const API_BASE_URL = getBackendUrl();

// Strip trailing slashes for clean concatenation
export const API_URL = API_BASE_URL.replace(/\/+$/, '');

// API endpoints (all relative to API_URL)
export const API_ENDPOINTS = {
  // Authentication
  TOKEN: `${API_URL}/token/`,
  TOKEN_REFRESH: `${API_URL}/token/refresh/`,

  // Health check
  HEALTH: `${API_URL}/health/`,

  // Address validation
  ADDRESS_VALIDATION: `${API_URL}/address-validation/validate/`,

  // Delivery management
  DELIVERIES: `${API_URL}/deliveries/`,
  REQUEST_DELIVERY: `${API_URL}/deliveries/request_delivery/`,

  // Customer management
  CUSTOMERS: `${API_URL}/customers/`,
  CUSTOMER_REGISTER: `${API_URL}/customers/register/`,
  CUSTOMER_ME: `${API_URL}/customers/me/`,
  CUSTOMER_DELIVERIES: `${API_URL}/customers/my_deliveries/`,

  // Driver management
  DRIVERS: `${API_URL}/drivers/`,
  DRIVER_REGISTER: `${API_URL}/drivers/register/`,

  // Vehicle management
  VEHICLES: `${API_URL}/vehicles/`,
};

// Health check function
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(API_ENDPOINTS.HEALTH, {
      method: 'GET',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

// Retained for compatibility (currently returns base URL)
export const discoverBackendUrl = async (): Promise<string> => {
  console.log('🔍 Dynamic discovery complete — using resolved URL');
  return API_BASE_URL;
};

// Axios-style config object
export const API_CONFIG = {
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// Debug information
export const getApiDebugInfo = () => {
  return {
    currentUrl: API_URL,
    expoConfigExtra: Constants.expoConfig?.extra,
    processEnv: process.env.BACKEND_URL,
    hostUri: Constants.expoConfig?.hostUri,
    isUsingTunnel: API_URL.includes('exp.direct') || API_URL.includes('ngrok.io'),
    isDevelopment: __DEV__,
  };
};

// Print debug info in development
if (__DEV__) {
  console.log('🔧 API Configuration Debug Info:', getApiDebugInfo());
}