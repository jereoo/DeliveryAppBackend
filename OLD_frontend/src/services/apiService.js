import api from './api';

export const authService = {
  // Login
  login: async (username, password) => {
    const response = await api.post('/token/', { username, password });
    return response.data;
  },

  // Customer registration
  registerCustomer: async (customerData) => {
    const response = await api.post('/customers/register/', customerData);
    return response.data;
  },

  // Driver registration
  registerDriver: async (driverData) => {
    const response = await api.post('/drivers/register/', driverData);
    return response.data;
  },

  // Get current user profile
  getProfile: async () => {
    const response = await api.get('/customers/me/');
    return response.data;
  },

  // Logout
  logout: () => {
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  }
};

export const deliveryService = {
  // Request delivery
  requestDelivery: async (deliveryData) => {
    const response = await api.post('/deliveries/request_delivery/', deliveryData);
    return response.data;
  },

  // Get deliveries
  getDeliveries: async () => {
    const response = await api.get('/deliveries/');
    return response.data;
  },

  // Get customer deliveries
  getMyDeliveries: async () => {
    const response = await api.get('/customers/my_deliveries/');
    return response.data;
  }
};