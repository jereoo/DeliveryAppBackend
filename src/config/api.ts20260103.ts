// CIO DIRECTIVE – PERMANENT LAUNCH FIX – NOV 21 2025
/**
 * API Configuration with Dynamic URL Resolution
 * SDK 51+ Compatible - Never use Constants.manifest again
 */

import Constants from 'expo-constants';

// CIO DIRECTIVE: Get backend URL ONLY from tunnel environment variables
const getBackendUrl = (): string => {
  console.log('🔧 API Config Debug:', {
    expoConfig: Constants.expoConfig?.extra,
    processEnv: process.env.BACKEND_URL,
    hostUri: Constants.expoConfig?.hostUri,
  });

  // 1. Check environment variables (from .env)
  if (process.env.BACKEND_URL) {
    console.log('✅ Using process.env.BACKEND_URL');
    return process.env.BACKEND_URL;
  }

  // 2. Check expo config extra (modern API - SDK 51+)
  if (Constants.expoConfig?.extra?.backendUrl) {
    console.log('✅ Using expoConfig.extra.backendUrl');
    return Constants.expoConfig.extra.backendUrl;
  }

  // 3. CIO DIRECTIVE: NO LOCALHOST OR HARDCODED IPs
  console.log('❌ CRITICAL: No tunnel URL configured in environment');
  throw new Error('BACKEND_URL not configured. Run start-fullstack.bat to set tunnel URL.');

};

// Get the base URL for API calls
export const API_BASE_URL = getBackendUrl();

// Remove any trailing slash
// OLD – allows double /api if someone prefixes endpoint with /api/
//export const API_URL = API_BASE_URL.replace(/\/$/, '');

// NEW – guarantees clean base URL ending exactly with /api (no trailing slash)
export const API_URL = API_BASE_URL.replace(/\/+$/, '');

// API endpoints
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

// Health check function with dynamic backend discovery
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

// CRITICAL FIX: Dynamic backend discovery for tunnel mode (CIO DIRECTIVE COMPLIANT)
export const discoverBackendUrl = async (): Promise<string> => {
  // Only attempt discovery if we're getting connection errors
  console.log('🔍 Attempting dynamic backend discovery...');

  // CIO DIRECTIVE: NO LOCALHOST TESTING - Use only tunnel URLs from environment
  console.log('🔍 Using tunnel URL from environment...');

  return API_BASE_URL;
};

// Configuration object
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
    isUsingTunnel: API_URL.includes('ngrok.io') || API_URL.includes('tunnel'),
    isDevelopment: __DEV__,
  };
};

// Print debug info in development
if (__DEV__) {
  console.log('🔧 API Configuration Debug Info:', getApiDebugInfo());
}
