/**
 * AddressAutocomplete Component Tests - CIO COMPLIANCE
 * Basic testing for address validation UI component
 */

import { render } from '@testing-library/react-native';
import React from 'react';
import AddressAutocomplete, { AddressAutocompleteProps } from '../components/AddressAutocomplete';

// Mock the address validation service
jest.mock('../services/addressValidation', () => ({
  addressValidationService: {
    validateAddressWithBadge: jest.fn(),
    formatAddressForDisplay: jest.fn(),
  },
}));

// Mock lodash debounce to make tests synchronous
jest.mock('lodash', () => ({
  debounce: (fn: any) => {
    fn.cancel = jest.fn();
    return fn;
  },
}));

describe('AddressAutocomplete Component', () => {
  const defaultProps: AddressAutocompleteProps = {
    onAddressSelected: jest.fn(),
    onValidationStatusChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders with default props', () => {
      const { getByPlaceholderText } = render(<AddressAutocomplete {...defaultProps} />);
      expect(getByPlaceholderText('Enter address...')).toBeTruthy();
    });

    it('renders with custom placeholder', () => {
      const customPlaceholder = 'Enter your delivery address';
      const { getByPlaceholderText } = render(
        <AddressAutocomplete {...defaultProps} placeholder={customPlaceholder} />
      );
      expect(getByPlaceholderText(customPlaceholder)).toBeTruthy();
    });

    it('renders with initial value', () => {
      const initialValue = '123 Main Street';
      const { getByDisplayValue } = render(
        <AddressAutocomplete {...defaultProps} initialValue={initialValue} />
      );
      expect(getByDisplayValue(initialValue)).toBeTruthy();
    });
  });
});