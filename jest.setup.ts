// CIO DIRECTIVE: Jest setup for mobile testing compliance
import '@testing-library/jest-native/extend-expect';
import 'react-native-gesture-handler/jestSetup';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

// Mock Expo modules
jest.mock('expo-constants', () => ({
  manifest: {
    extra: {
      backendUrl: 'http://localhost:8000/api'
    },
    hostUri: 'localhost:19000'
  }
}));

// Mock fetch globally
global.fetch = jest.fn();

// Mock console methods to reduce test noise
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn(),
  log: jest.fn(),
};

// Setup test environment
beforeEach(() => {
  jest.clearAllMocks();
});

afterEach(() => {
  jest.restoreAllMocks();
});

// Increase timeout for CI
jest.setTimeout(30000);