// CustomerRegister.test.js - Unit tests for Customer Registration Component
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import CustomerRegister from '../pages/CustomerRegister';
import { AuthProvider } from '../contexts/AuthContext';
import '@testing-library/jest-dom';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
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

describe('CustomerRegister Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders customer registration form', () => {
    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    expect(screen.getByText('Register as Customer')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('First Name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Last Name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Phone Number')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Address')).toBeInTheDocument();
  });

  test('shows business-specific fields when business checkbox is checked', async () => {
    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    const businessCheckbox = screen.getByRole('checkbox', { name: /business customer/i });
    fireEvent.click(businessCheckbox);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Company Name')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Preferred Pickup Address (Optional)')).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument();
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });

  test('validates email format', async () => {
    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    const emailInput = screen.getByPlaceholderText('Email address');
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email')).toBeInTheDocument();
    });
  });

  test('validates password length', async () => {
    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    const passwordInput = screen.getByPlaceholderText('Password');
    fireEvent.change(passwordInput, { target: { value: '123' } });
    
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
    });
  });

  test('toggles password visibility', () => {
    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    const passwordInput = screen.getByPlaceholderText('Password');
    const toggleButton = screen.getByRole('button', { name: /toggle password visibility/i });

    // Initially password should be hidden
    expect(passwordInput.type).toBe('password');

    // Click to show password
    fireEvent.click(toggleButton);
    expect(passwordInput.type).toBe('text');

    // Click to hide password again
    fireEvent.click(toggleButton);
    expect(passwordInput.type).toBe('password');
  });

  test('submits form with valid data', async () => {
    const mockRegisterCustomer = jest.fn().mockResolvedValue({ success: true });

    // Mock the useAuth hook
    jest.doMock('../contexts/AuthContext', () => ({
      useAuth: () => ({
        registerCustomer: mockRegisterCustomer,
      }),
    }));

    render(
      <TestWrapper>
        <CustomerRegister />
      </TestWrapper>
    );

    // Fill out the form
    fireEvent.change(screen.getByPlaceholderText('Username'), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByPlaceholderText('Email address'), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });
    fireEvent.change(screen.getByPlaceholderText('First Name'), {
      target: { value: 'John' },
    });
    fireEvent.change(screen.getByPlaceholderText('Last Name'), {
      target: { value: 'Doe' },
    });
    fireEvent.change(screen.getByPlaceholderText('Phone Number'), {
      target: { value: '555-1234' },
    });
    fireEvent.change(screen.getByPlaceholderText('Address'), {
      target: { value: '123 Main St' },
    });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockRegisterCustomer).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        first_name: 'John',
        last_name: 'Doe',
        phone_number: '555-1234',
        address: '123 Main St',
        is_business: false,
      });
    });
  });
});

export default CustomerRegister;