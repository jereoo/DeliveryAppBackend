// ENFORCED BY CIO DIRECTIVE – CORRECT DIRECTORY – NOV 20 2025
/**
 * Address Autocomplete Component with Google Places Integration
 * Real-time address validation with confidence badges
 */

import { debounce } from 'lodash';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from 'react-native';
import { AddressValidationResponse, addressValidationService } from '../services/addressValidation';

export interface AddressAutocompleteProps {
  placeholder?: string;
  initialValue?: string;
  countryHint?: 'US' | 'CA';
  onAddressSelected: (address: AddressValidationResponse) => void;
  onValidationStatusChange: (isValid: boolean, confidence: number) => void;
  style?: any;
  editable?: boolean;
  required?: boolean;
}

interface ValidationBadge {
  icon: string;
  text: string;
  color: string;
  confidence: string;
}

const AddressAutocomplete: React.FC<AddressAutocompleteProps> = ({
  placeholder = 'Enter address...',
  initialValue = '',
  countryHint = 'US',
  onAddressSelected,
  onValidationStatusChange,
  style,
  editable = true,
  required = false,
}) => {
  const [inputValue, setInputValue] = useState<string>(initialValue);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [validationResult, setValidationResult] = useState<AddressValidationResponse | null>(null);
  const [validationBadge, setValidationBadge] = useState<ValidationBadge | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFocused, setIsFocused] = useState<boolean>(false);

  // Debounced validation function
  const debouncedValidation = useCallback(
    debounce(async (address: string) => {
      if (!address.trim() || address.length < 10) {
        setValidationResult(null);
        setValidationBadge(null);
        setError(null);
        onValidationStatusChange(false, 0);
        return;
      }

      setIsValidating(true);
      setError(null);

      try {
        const { result, badge } = await addressValidationService.validateAddressWithBadge(
          address,
          countryHint
        );

        setValidationResult(result);
        setValidationBadge(badge);

        const isValid = result.validation_status === 'valid';
        onValidationStatusChange(isValid, result.confidence_score);

        if (isValid || result.validation_status === 'partial') {
          onAddressSelected(result);
        }
      } catch (err) {
        console.error('Address validation error:', err);
        setError(err instanceof Error ? err.message : 'Validation failed');
        setValidationResult(null);
        setValidationBadge(null);
        onValidationStatusChange(false, 0);
      } finally {
        setIsValidating(false);
      }
    }, 800),
    [countryHint, onAddressSelected, onValidationStatusChange]
  );

  // Effect to validate address when input changes
  useEffect(() => {
    if (inputValue !== initialValue) {
      debouncedValidation(inputValue);
    }
  }, [inputValue, debouncedValidation, initialValue]);

  // Handle text input change
  const handleInputChange = (text: string) => {
    setInputValue(text);
  };

  // Handle focus
  const handleFocus = () => {
    setIsFocused(true);
  };

  // Handle blur
  const handleBlur = () => {
    setIsFocused(false);
  };

  // Handle manual validation trigger
  const handleValidateNow = () => {
    if (inputValue.trim()) {
      debouncedValidation.cancel();
      debouncedValidation(inputValue);
    }
  };

  // Render validation badge
  const renderValidationBadge = () => {
    if (isValidating) {
      return (
        <View style={styles.validationBadge}>
          <ActivityIndicator size="small" color="#6B7280" />
          <Text style={styles.validatingText}>Validating...</Text>
        </View>
      );
    }

    if (validationBadge) {
      return (
        <View style={[styles.validationBadge, { backgroundColor: validationBadge.color + '20' }]}>
          <Text style={[styles.badgeIcon, { color: validationBadge.color }]}>
            {validationBadge.icon}
          </Text>
          <View style={styles.badgeTextContainer}>
            <Text style={[styles.badgeText, { color: validationBadge.color }]}>
              {validationBadge.text}
            </Text>
            <Text style={styles.confidenceText}>
              {validationBadge.confidence}
            </Text>
          </View>
        </View>
      );
    }

    if (error) {
      return (
        <View style={[styles.validationBadge, styles.errorBadge]}>
          <Text style={styles.errorIcon}>⚠</Text>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      );
    }

    return null;
  };

  // Format display address
  const getDisplayAddress = () => {
    if (validationResult) {
      return addressValidationService.formatAddressForDisplay(validationResult);
    }
    return inputValue;
  };

  return (
    <View style={[style]}>
      {/* Address Input */}
      <View style={styles.inputContainer}>
        <TextInput
          style={[
            styles.textInput,
            isFocused && styles.textInputFocused,
            error && styles.textInputError,
            validationResult?.validation_status === 'valid' && styles.textInputValid,
          ]}
          placeholder={placeholder}
          value={inputValue}
          onChangeText={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          editable={editable}
          multiline
          numberOfLines={2}
          autoCapitalize="words"
          autoCorrect={false}
          returnKeyType="done"
        />

        {/* Validation Button */}
        {inputValue.length > 0 && (
          <TouchableOpacity
            style={styles.validateButton}
            onPress={handleValidateNow}
            disabled={isValidating}
          >
            <Text style={styles.validateButtonText}>
              {isValidating ? '...' : '✓'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Required Field Indicator */}
      {required && (
        <Text style={styles.requiredText}>* Required field</Text>
      )}

      {/* Validation Badge */}
      {renderValidationBadge()}

      {/* Formatted Address Display */}
      {validationResult && (
        <View style={styles.formattedAddressContainer}>
          <Text style={styles.formattedAddressLabel}>Formatted Address:</Text>
          <Text style={styles.formattedAddressText}>
            {getDisplayAddress()}
          </Text>

          {/* Address Components */}
          {validationResult.latitude && validationResult.longitude && (
            <Text style={styles.coordinatesText}>
              📍 {validationResult.latitude.toFixed(6)}, {validationResult.longitude.toFixed(6)}
            </Text>
          )}
        </View>
      )}

      {/* Country Hint Display */}
      <Text style={styles.countryHint}>
        Validating for: {countryHint === 'US' ? 'United States' : 'Canada'}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    position: 'relative',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF',
    minHeight: 50,
    textAlignVertical: 'top',
  },
  textInputFocused: {
    borderColor: '#3B82F6',
    shadowColor: '#3B82F6',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  textInputError: {
    borderColor: '#EF4444',
  },
  textInputValid: {
    borderColor: '#10B981',
  },
  validateButton: {
    position: 'absolute',
    right: 8,
    top: 8,
    backgroundColor: '#F3F4F6',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
    minWidth: 30,
    alignItems: 'center',
  },
  validateButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  requiredText: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 4,
    fontStyle: 'italic',
  },
  validationBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginTop: 8,
    backgroundColor: '#F9FAFB',
  },
  badgeIcon: {
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  badgeTextContainer: {
    flex: 1,
  },
  badgeText: {
    fontSize: 14,
    fontWeight: '600',
  },
  confidenceText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  validatingText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
  },
  errorBadge: {
    backgroundColor: '#FEF2F2',
  },
  errorIcon: {
    fontSize: 16,
    color: '#EF4444',
    marginRight: 8,
  },
  errorText: {
    fontSize: 14,
    color: '#EF4444',
    flex: 1,
  },
  formattedAddressContainer: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#F9FAFB',
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#10B981',
  },
  formattedAddressLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  formattedAddressText: {
    fontSize: 14,
    color: '#111827',
    lineHeight: 20,
  },
  coordinatesText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
    fontFamily: 'monospace',
  },
  countryHint: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
    textAlign: 'right',
  },
});

export default AddressAutocomplete;