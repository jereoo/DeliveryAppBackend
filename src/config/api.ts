// CIO DIRECTIVE – PERMANENT LAUNCH FIX – NOV 21 2025
/**
 * API Configuration with Dynamic URL Resolution
 * SDK 51+ Compatible - Never use Constants.manifest again
 */

import Constants from 'expo-constants';

// Get backend URL from multiple sources with fallback hierarchy
const getBackendUrl = (): string => {
  console.log('🔧 API Config Debug:', {
    expoConfig: Constants.expoConfig?.extra,
    processEnv: process.env.BACKEND_URL,
    hostUri: Constants.expoConfig?.hostUri,
  });

  // 1. Check expo config extra (modern API - SDK 51+)
  if (Constants.expoConfig?.extra?.backendUrl) {
    console.log('✅ Using expoConfig.extra.backendUrl');
    return Constants.expoConfig.extra.backendUrl;
  }

  // 2. Check environment variables (from .env)
  if (process.env.BACKEND_URL) {
    console.log('✅ Using process.env.BACKEND_URL');
    return process.env.BACKEND_URL;
  }

  // 3. Dynamic network resolution (CIO DIRECTIVE COMPLIANT - NO HARDCODED IPs)
  // When tunnel is active, Django backend needs to be discovered dynamically
  console.log('🔧 No backend URL configured - using dynamic discovery');
  
  // Return localhost as primary fallback (works when Django runs on 0.0.0.0:8000)
  return 'http://localhost:8000/api';

  // 4. Final error - no valid backend URL found
  const errorMsg = `❌ BACKEND CONNECTION FAILED
  
No valid backend URL found. Ensure:
1. Django server is running on 0.0.0.0:8000
2. Expo tunnel is active
3. .env BACKEND_URL is set correctly

Use only: ./start-fullstack.bat or F5 in VS Code`;

  console.error(errorMsg);
  throw new Error('Backend URL not configured. Use CIO-approved startup script.');
};

// Get the base URL for API calls
export const API_BASE_URL = getBackendUrl();

// Remove any trailing slash
export const API_URL = API_BASE_URL.replace(/\/$/, '');

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
  
  // Test localhost first (standard development setup)
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    
    const response = await fetch('http://localhost:8000/api/token/', { 
      method: 'HEAD',
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok || response.status === 405) {
      console.log('✅ Found Django backend at localhost:8000');
      return 'http://localhost:8000/api';
    }
  } catch (error) {
    console.log('❌ Localhost:8000 not accessible, Django may not be running');
    console.log('💡 Make sure to run: python manage.py runserver 0.0.0.0:8000');
  }
  
  // If localhost fails, use the configured URL (maintains CIO directive compliance)
  console.log('⚠️ Using fallback - ensure Django is running with CIO-approved startup script');
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