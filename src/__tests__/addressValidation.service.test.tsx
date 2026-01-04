/**
 * Address Validation Service Tests - CIO COMPLIANCE
 * Testing core validation functionality with proper mocking
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { addressValidationService } from '../services/addressValidation';
// Jest/TypeScript: declare global for test context
declare var global: any;

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage');
const mockAsyncStorage = AsyncStorage as jest.Mocked<typeof AsyncStorage>;

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('AddressValidationService', () => {
  const mockToken = 'mock-jwt-token';

  beforeEach(() => {
    jest.clearAllMocks();
    mockAsyncStorage.getItem.mockResolvedValue(mockToken);

    // Mock successful response by default
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: 1,
        validation_status: 'valid',
        confidence_score: 0.95,
        latitude: 40.7128,
        longitude: -74.0060,
        formatted_address: '123 Main St, New York, NY 10001, USA',
        original_address: '123 Main St',
        validation_source: 'google_maps',
        is_valid: true,
        created_at: new Date().toISOString(),
      }),
    } as Response);
  });

  describe('Authentication', () => {
    it('throws error when no token is available', async () => {
      mockAsyncStorage.getItem.mockResolvedValue(null);

      await expect(
        addressValidationService.validateAddress({ address: '123 Main St' })
      ).rejects.toThrow('No authentication token found');
    });

    it('includes authorization header when token is available', async () => {
      await addressValidationService.validateAddress({ address: '123 Main St' });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/address-validation/validate/'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`,
          }),
        })
      );
    });
  });

  describe('Address Validation', () => {
    it('makes correct API call with address and country hint', async () => {
      const request = { address: '123 Main Street', country_hint: 'US' as const };

      await addressValidationService.validateAddress(request);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/address-validation/validate/'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            address: '123 Main Street',
            country_hint: 'US',
          }),
        })
      );
    });

    it('defaults country hint to US when not provided', async () => {
      await addressValidationService.validateAddress({ address: '123 Main Street' });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({
            address: '123 Main Street',
            country_hint: 'US',
          }),
        })
      );
    });

    it('returns parsed validation response', async () => {
      const result = await addressValidationService.validateAddress({ address: '123 Main St' });

      expect(result).toMatchObject({
        validation_status: 'valid',
        confidence_score: 0.95,
        formatted_address: '123 Main St, New York, NY 10001, USA',
      });
    });
  });

  describe('Address Validation with Badge', () => {
    it('returns validation result with appropriate badge for valid address', async () => {
      const { result, badge } = await addressValidationService.validateAddressWithBadge('123 Main St');

      expect(result.validation_status).toBe('valid');
      expect(badge.text).toBe('Valid Address');
      expect(badge.icon).toBe('✓');
      expect(badge.color).toBe('#10B981');
    });
  });

  describe('Address Formatting', () => {
    it('returns formatted address when available', () => {
      const response = {
        id: 1,
        validation_status: 'valid' as const,
        formatted_address: '123 Main St, New York, NY 10001, USA',
        confidence_score: 0.95,
        original_address: '123 Main St',
        validation_source: 'google_maps',
        is_valid: true,
        created_at: new Date().toISOString(),
      };

      const formatted = addressValidationService.formatAddressForDisplay(response);

      expect(formatted).toBe('123 Main St, New York, NY 10001, USA');
    });

    it('returns original address when formatted address not available', () => {
      const response = {
        id: 1,
        validation_status: 'valid' as const,
        formatted_address: '',
        confidence_score: 0.95,
        original_address: '123 Main St',
        validation_source: 'google_maps',
        is_valid: true,
        created_at: new Date().toISOString(),
      };

      const formatted = addressValidationService.formatAddressForDisplay(response);

      expect(formatted).toBe('123 Main St');
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(
        addressValidationService.validateAddress({ address: '123 Main St' })
      ).rejects.toThrow('Network error');
    });

    it('handles API errors with proper error messages', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid address format' }),
      } as Response);

      await expect(
        addressValidationService.validateAddress({ address: '123 Main St' })
      ).rejects.toThrow('Invalid address format');
    });
  });
});
