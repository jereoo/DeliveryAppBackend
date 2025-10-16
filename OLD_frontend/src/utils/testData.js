// testData.js - Mock test data for unit tests
export const mockCustomers = [
  {
    id: 1,
    username: 'customer1',
    email: 'customer1@example.com',
    first_name: 'John',
    last_name: 'Doe',
    phone_number: '555-0001',
    address: '123 Main St, City, State',
    is_business: false,
    company_name: null,
    preferred_pickup_address: null,
  },
  {
    id: 2,
    username: 'business1',
    email: 'contact@business1.com',
    first_name: 'Jane',
    last_name: 'Smith',
    phone_number: '555-0002',
    address: '456 Business Ave, City, State',
    is_business: true,
    company_name: 'ABC Corporation',
    preferred_pickup_address: '789 Warehouse St',
  },
  {
    id: 3,
    username: 'customer3',
    email: 'customer3@example.com',
    first_name: 'Bob',
    last_name: 'Johnson',
    phone_number: '555-0003',
    address: '321 Oak Dr, City, State',
    is_business: false,
    company_name: null,
    preferred_pickup_address: '111 Pickup Point',
  },
];

export const mockDrivers = [
  {
    id: 1,
    username: 'driver1',
    email: 'driver1@example.com',
    name: 'Alice Williams',
    phone_number: '555-1001',
    license_number: 'DL123456',
    active: true,
    current_vehicle: 'Toyota Camry',
    current_vehicle_plate: 'ABC123',
  },
  {
    id: 2,
    username: 'driver2',
    email: 'driver2@example.com',
    name: 'Mike Davis',
    phone_number: '555-1002',
    license_number: 'DL789012',
    active: true,
    current_vehicle: 'Honda Civic',
    current_vehicle_plate: 'XYZ789',
  },
];

export const mockVehicles = [
  {
    id: 1,
    license_plate: 'ABC123',
    model: 'Toyota Camry',
    capacity: 1500,
    capacity_unit: 'kg',
    capacity_display: '1500 kg',
    active: true,
  },
  {
    id: 2,
    license_plate: 'XYZ789',
    model: 'Honda Civic',
    capacity: 1200,
    capacity_unit: 'kg',
    capacity_display: '1200 kg',
    active: true,
  },
  {
    id: 3,
    license_plate: 'DEF456',
    model: 'Ford Transit',
    capacity: 3000,
    capacity_unit: 'lb',
    capacity_display: '3000 lb',
    active: true,
  },
];

export const mockDeliveries = [
  {
    id: 1,
    customer: 1,
    customer_name: 'John Doe',
    customer_email: 'customer1@example.com',
    customer_phone: '555-0001',
    pickup_location: '123 Main St, City, State',
    dropoff_location: '456 Oak Ave, City, State',
    same_pickup_as_customer: true,
    use_preferred_pickup: false,
    same_dropoff_as_customer: false,
    item_description: 'Small package',
    status: 'Pending',
    delivery_date: '2025-09-27',
    delivery_time: '14:00:00',
    special_instructions: 'Ring doorbell twice',
    estimated_cost: 15.50,
    created_at: '2025-09-26T10:30:00Z',
    updated_at: '2025-09-26T10:30:00Z',
  },
  {
    id: 2,
    customer: 2,
    customer_name: 'Jane Smith',
    customer_email: 'contact@business1.com',
    customer_phone: '555-0002',
    pickup_location: '789 Warehouse St',
    dropoff_location: '321 Client Blvd, City, State',
    same_pickup_as_customer: false,
    use_preferred_pickup: true,
    same_dropoff_as_customer: false,
    item_description: 'Business documents',
    status: 'En Route',
    delivery_date: '2025-09-26',
    delivery_time: '16:30:00',
    special_instructions: 'Deliver to reception',
    estimated_cost: 25.00,
    created_at: '2025-09-26T09:15:00Z',
    updated_at: '2025-09-26T11:45:00Z',
  },
  {
    id: 3,
    customer: 1,
    customer_name: 'John Doe',
    customer_email: 'customer1@example.com',
    customer_phone: '555-0001',
    pickup_location: '123 Main St, City, State',
    dropoff_location: '987 Destination Dr, City, State',
    same_pickup_as_customer: true,
    use_preferred_pickup: false,
    same_dropoff_as_customer: false,
    item_description: 'Electronics',
    status: 'Completed',
    delivery_date: '2025-09-25',
    delivery_time: '10:00:00',
    special_instructions: 'Fragile - handle with care',
    estimated_cost: 35.75,
    created_at: '2025-09-25T08:00:00Z',
    updated_at: '2025-09-25T10:30:00Z',
  },
];

export const mockDeliveryAssignments = [
  {
    id: 1,
    delivery: 1,
    driver: 1,
    vehicle: 1,
    assigned_at: '2025-09-26T10:35:00Z',
    estimated_completion: '2025-09-27T15:00:00Z',
  },
  {
    id: 2,
    delivery: 2,
    driver: 2,
    vehicle: 2,
    assigned_at: '2025-09-26T09:20:00Z',
    estimated_completion: '2025-09-26T17:30:00Z',
  },
];

export const mockAuthTokens = {
  access: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_access_token',
  refresh: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_refresh_token',
};

export const mockRegistrationData = {
  customer: {
    username: 'newcustomer',
    email: 'newcustomer@example.com',
    password: 'securepass123',
    first_name: 'New',
    last_name: 'Customer',
    phone_number: '555-9999',
    address: '999 New St, City, State',
    is_business: false,
  },
  businessCustomer: {
    username: 'newbusiness',
    email: 'contact@newbusiness.com',
    password: 'businesspass123',
    first_name: 'Business',
    last_name: 'Owner',
    phone_number: '555-8888',
    address: '888 Business Blvd, City, State',
    is_business: true,
    company_name: 'New Business LLC',
    preferred_pickup_address: '777 Pickup Hub',
  },
  driver: {
    username: 'newdriver',
    email: 'newdriver@example.com',
    password: 'driverpass123',
    first_name: 'New',
    last_name: 'Driver',
    name: 'New Driver',
    phone_number: '555-7777',
    license_number: 'DL999888',
    vehicle_license_plate: 'NEW123',
    vehicle_model: 'Nissan Altima',
    vehicle_capacity: 1400,
    vehicle_capacity_unit: 'kg',
  },
};

export const mockApiResponses = {
  loginSuccess: {
    access: mockAuthTokens.access,
    refresh: mockAuthTokens.refresh,
    user: {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    },
  },
  customerRegistrationSuccess: {
    message: 'Customer registered successfully',
    customer: mockCustomers[0],
  },
  driverRegistrationSuccess: {
    message: 'Driver registered successfully',
    driver_id: 1,
    name: 'New Driver',
    vehicle_assigned: true,
  },
  deliveryRequestSuccess: {
    id: 4,
    customer: 1,
    pickup_location: '123 Test St',
    dropoff_location: '456 Test Ave',
    item_description: 'Test item',
    status: 'Pending',
    created_at: '2025-09-26T12:00:00Z',
  },
};

// Validation helpers for test data
export const validateCustomerData = (customer) => {
  const required = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address'];
  return required.every(field => customer[field] && customer[field].trim() !== '');
};

export const validateDriverData = (driver) => {
  const required = ['username', 'email', 'name', 'phone_number', 'license_number'];
  return required.every(field => driver[field] && driver[field].trim() !== '');
};

export const validateDeliveryData = (delivery) => {
  const required = ['pickup_location', 'dropoff_location', 'item_description'];
  return required.every(field => delivery[field] && delivery[field].trim() !== '');
};

export const validateEmailFormat = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhoneFormat = (phone) => {
  const phoneRegex = /^\d{3}-\d{4}$/;
  return phoneRegex.test(phone);
};

// Status constants
export const DELIVERY_STATUSES = ['Pending', 'En Route', 'Completed', 'Cancelled'];
export const VEHICLE_CAPACITY_UNITS = ['kg', 'lb'];

export default {
  mockCustomers,
  mockDrivers,
  mockVehicles,
  mockDeliveries,
  mockDeliveryAssignments,
  mockAuthTokens,
  mockRegistrationData,
  mockApiResponses,
  validateCustomerData,
  validateDriverData,
  validateDeliveryData,
  validateEmailFormat,
  validatePhoneFormat,
  DELIVERY_STATUSES,
  VEHICLE_CAPACITY_UNITS,
};