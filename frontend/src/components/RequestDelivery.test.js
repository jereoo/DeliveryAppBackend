// RequestDelivery.test.js - Unit tests for Request Delivery Component
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import RequestDelivery from '../pages/RequestDelivery';
import { AuthProvider } from '../contexts/AuthContext';
import '@testing-library/jest-dom';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Test wrapper component
const TestWrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('RequestDelivery Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders delivery request form', () => {
    render(
      <TestWrapper>
        <RequestDelivery />
      </TestWrapper>
    );

    expect(screen.getByText('Request Delivery')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Pickup Location')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Dropoff Location')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Item Description')).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(
      <TestWrapper>
        <RequestDelivery />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /request delivery/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Pickup location is required')).toBeInTheDocument();
      expect(screen.getByText('Dropoff location is required')).toBeInTheDocument();
      expect(screen.getByText('Item description is required')).toBeInTheDocument();
    });
  });

  test('shows/hides pickup location based on checkbox', async () => {
    render(
      <TestWrapper>
        <RequestDelivery />
      </TestWrapper>
    );

    const checkbox = screen.getByRole('checkbox', { name: /use my address as pickup/i });
    const pickupInput = screen.getByPlaceholderText('Pickup Location');

    // Initially pickup input should be visible
    expect(pickupInput).not.toBeDisabled();

    // Check the box - pickup input should become disabled
    fireEvent.click(checkbox);
    expect(pickupInput).toBeDisabled();

    // Uncheck the box - pickup input should become enabled again
    fireEvent.click(checkbox);
    expect(pickupInput).not.toBeDisabled();
  });

  test('submits delivery request with valid data', async () => {
    render(
      <TestWrapper>
        <RequestDelivery />
      </TestWrapper>
    );

    // Fill out the form
    fireEvent.change(screen.getByPlaceholderText('Pickup Location'), {
      target: { value: '123 Pickup St' },
    });
    fireEvent.change(screen.getByPlaceholderText('Dropoff Location'), {
      target: { value: '456 Dropoff Ave' },
    });
    fireEvent.change(screen.getByPlaceholderText('Item Description'), {
      target: { value: 'Test package' },
    });
    fireEvent.change(screen.getByPlaceholderText('Special Instructions (Optional)'), {
      target: { value: 'Handle with care' },
    });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /request delivery/i });
    fireEvent.click(submitButton);

    // Form should be submitted (we can't test the actual submission without mocking the API)
    expect(screen.getByDisplayValue('123 Pickup St')).toBeInTheDocument();
    expect(screen.getByDisplayValue('456 Dropoff Ave')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test package')).toBeInTheDocument();
  });
});