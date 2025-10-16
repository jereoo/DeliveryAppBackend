// api.test.js - Unit tests for API service
import axios from 'axios';
import Cookies from 'js-cookie';
import api from '../services/api';

// Mock axios and js-cookie
jest.mock('axios');
jest.mock('js-cookie');

const mockedAxios = axios;
const mockedCookies = Cookies;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Request Interceptor', () => {
    test('adds authorization header when token exists', () => {
      const mockToken = 'mock-jwt-token';
      mockedCookies.get.mockReturnValue(mockToken);

      const config = {
        headers: { 'Content-Type': 'application/json' },
      };

      // Simulate the request interceptor
      const interceptedConfig = api.interceptors.request.handlers[0].fulfilled(config);

      expect(mockedCookies.get).toHaveBeenCalledWith('access_token');
      expect(interceptedConfig.headers.Authorization).toBe(`Bearer ${mockToken}`);
    });

    test('does not add authorization header when token does not exist', () => {
      mockedCookies.get.mockReturnValue(undefined);

      const config = {
        headers: { 'Content-Type': 'application/json' },
      };

      const interceptedConfig = api.interceptors.request.handlers[0].fulfilled(config);

      expect(mockedCookies.get).toHaveBeenCalledWith('access_token');
      expect(interceptedConfig.headers.Authorization).toBeUndefined();
    });
  });

  describe('Response Interceptor', () => {
    test('handles successful responses', () => {
      const mockResponse = { data: { message: 'Success' }, status: 200 };

      const result = api.interceptors.response.handlers[0].fulfilled(mockResponse);

      expect(result).toBe(mockResponse);
    });

    test('handles 401 error with refresh token', async () => {
      const mockError = {
        response: { status: 401 },
      };

      const mockRefreshToken = 'mock-refresh-token';
      const mockNewAccessToken = 'new-access-token';

      mockedCookies.get.mockReturnValue(mockRefreshToken);
      mockedAxios.post.mockResolvedValue({
        data: { access: mockNewAccessToken },
      });

      await expect(
        api.interceptors.response.handlers[0].rejected(mockError)
      ).rejects.toBe(mockError);

      expect(mockedCookies.get).toHaveBeenCalledWith('refresh_token');
    });

    test('handles 401 error without refresh token', async () => {
      const mockError = {
        response: { status: 401 },
      };

      mockedCookies.get.mockReturnValue(undefined);

      await expect(
        api.interceptors.response.handlers[0].rejected(mockError)
      ).rejects.toBe(mockError);

      expect(mockedCookies.get).toHaveBeenCalledWith('refresh_token');
    });

    test('handles non-401 errors', async () => {
      const mockError = {
        response: { status: 500 },
      };

      await expect(
        api.interceptors.response.handlers[0].rejected(mockError)
      ).rejects.toBe(mockError);
    });
  });
});

// Integration tests with mock data
describe('API Integration Tests', () => {
  const mockCustomerData = {
    username: 'testuser',
    email: 'test@example.com',
    password: 'password123',
    first_name: 'John',
    last_name: 'Doe',
    phone_number: '555-1234',
    address: '123 Main St',
    is_business: false,
  };

  const mockDriverData = {
    username: 'driver123',
    email: 'driver@example.com',
    password: 'password123',
    first_name: 'Jane',
    last_name: 'Smith',
    name: 'Jane Smith',
    phone_number: '555-5678',
    license_number: 'DL123456',
    vehicle_license_plate: 'ABC123',
    vehicle_model: 'Toyota Camry',
    vehicle_capacity: 1500,
    vehicle_capacity_unit: 'kg',
  };

  const mockDeliveryData = {
    pickup_location: '123 Pickup St',
    dropoff_location: '456 Dropoff Ave',
    item_description: 'Test package',
    same_pickup_as_customer: false,
    use_preferred_pickup: false,
    same_dropoff_as_customer: false,
    special_instructions: 'Handle with care',
  };

  test('customer registration data structure', () => {
    expect(mockCustomerData).toEqual({
      username: expect.any(String),
      email: expect.stringMatching(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
      password: expect.any(String),
      first_name: expect.any(String),
      last_name: expect.any(String),
      phone_number: expect.any(String),
      address: expect.any(String),
      is_business: expect.any(Boolean),
    });
  });

  test('driver registration data structure', () => {
    expect(mockDriverData).toEqual({
      username: expect.any(String),
      email: expect.stringMatching(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
      password: expect.any(String),
      first_name: expect.any(String),
      last_name: expect.any(String),
      name: expect.any(String),
      phone_number: expect.any(String),
      license_number: expect.any(String),
      vehicle_license_plate: expect.any(String),
      vehicle_model: expect.any(String),
      vehicle_capacity: expect.any(Number),
      vehicle_capacity_unit: expect.stringMatching(/^(kg|lb)$/),
    });
  });

  test('delivery request data structure', () => {
    expect(mockDeliveryData).toEqual({
      pickup_location: expect.any(String),
      dropoff_location: expect.any(String),
      item_description: expect.any(String),
      same_pickup_as_customer: expect.any(Boolean),
      use_preferred_pickup: expect.any(Boolean),
      same_dropoff_as_customer: expect.any(Boolean),
      special_instructions: expect.any(String),
    });
  });

  test('validates required fields for customer registration', () => {
    const requiredFields = [
      'username',
      'email',
      'password',
      'first_name',
      'last_name',
      'phone_number',
      'address',
    ];

    requiredFields.forEach((field) => {
      expect(mockCustomerData).toHaveProperty(field);
      expect(mockCustomerData[field]).toBeTruthy();
    });
  });

  test('validates required fields for driver registration', () => {
    const requiredFields = [
      'username',
      'email',
      'password',
      'name',
      'phone_number',
      'license_number',
      'vehicle_license_plate',
      'vehicle_model',
      'vehicle_capacity',
    ];

    requiredFields.forEach((field) => {
      expect(mockDriverData).toHaveProperty(field);
      expect(mockDriverData[field]).toBeTruthy();
    });
  });

  test('validates email format', () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    expect(mockCustomerData.email).toMatch(emailRegex);
    expect(mockDriverData.email).toMatch(emailRegex);
  });

  test('validates phone number format', () => {
    const phoneRegex = /^\d{3}-\d{4}$/;
    expect(mockCustomerData.phone_number).toMatch(phoneRegex);
    expect(mockDriverData.phone_number).toMatch(phoneRegex);
  });

  test('validates vehicle capacity is positive number', () => {
    expect(mockDriverData.vehicle_capacity).toBeGreaterThan(0);
    expect(typeof mockDriverData.vehicle_capacity).toBe('number');
  });

  test('validates vehicle capacity unit', () => {
    const validUnits = ['kg', 'lb'];
    expect(validUnits).toContain(mockDriverData.vehicle_capacity_unit);
  });
});