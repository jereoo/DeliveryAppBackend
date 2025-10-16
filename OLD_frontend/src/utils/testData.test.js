// testData.test.js - Unit tests for test data validation
import {
  mockCustomers,
  mockDrivers,
  mockVehicles,
  mockDeliveries,
  mockRegistrationData,
  validateCustomerData,
  validateDriverData,
  validateDeliveryData,
  validateEmailFormat,
  validatePhoneFormat,
  DELIVERY_STATUSES,
  VEHICLE_CAPACITY_UNITS,
} from '../utils/testData';

describe('Test Data Validation', () => {
  describe('Mock Data Structure', () => {
    test('customers have required fields', () => {
      mockCustomers.forEach(customer => {
        expect(customer).toHaveProperty('id');
        expect(customer).toHaveProperty('username');
        expect(customer).toHaveProperty('email');
        expect(customer).toHaveProperty('first_name');
        expect(customer).toHaveProperty('last_name');
        expect(customer).toHaveProperty('phone_number');
        expect(customer).toHaveProperty('address');
        expect(customer).toHaveProperty('is_business');
      });
    });

    test('drivers have required fields', () => {
      mockDrivers.forEach(driver => {
        expect(driver).toHaveProperty('id');
        expect(driver).toHaveProperty('username');
        expect(driver).toHaveProperty('email');
        expect(driver).toHaveProperty('name');
        expect(driver).toHaveProperty('phone_number');
        expect(driver).toHaveProperty('license_number');
        expect(driver).toHaveProperty('active');
      });
    });

    test('vehicles have required fields', () => {
      mockVehicles.forEach(vehicle => {
        expect(vehicle).toHaveProperty('id');
        expect(vehicle).toHaveProperty('license_plate');
        expect(vehicle).toHaveProperty('model');
        expect(vehicle).toHaveProperty('capacity');
        expect(vehicle).toHaveProperty('capacity_unit');
        expect(vehicle).toHaveProperty('active');
      });
    });

    test('deliveries have required fields', () => {
      mockDeliveries.forEach(delivery => {
        expect(delivery).toHaveProperty('id');
        expect(delivery).toHaveProperty('customer');
        expect(delivery).toHaveProperty('pickup_location');
        expect(delivery).toHaveProperty('dropoff_location');
        expect(delivery).toHaveProperty('item_description');
        expect(delivery).toHaveProperty('status');
      });
    });
  });

  describe('Data Validation Functions', () => {
    test('validateCustomerData - valid data', () => {
      const validCustomer = {
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe',
        phone_number: '555-1234',
        address: '123 Main St',
      };

      expect(validateCustomerData(validCustomer)).toBe(true);
    });

    test('validateCustomerData - missing fields', () => {
      const invalidCustomer = {
        username: 'testuser',
        email: 'test@example.com',
        // missing required fields
      };

      expect(validateCustomerData(invalidCustomer)).toBe(false);
    });

    test('validateCustomerData - empty fields', () => {
      const invalidCustomer = {
        username: '',
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe',
        phone_number: '555-1234',
        address: '123 Main St',
      };

      expect(validateCustomerData(invalidCustomer)).toBe(false);
    });

    test('validateDriverData - valid data', () => {
      const validDriver = {
        username: 'driver123',
        email: 'driver@example.com',
        name: 'John Driver',
        phone_number: '555-5678',
        license_number: 'DL123456',
      };

      expect(validateDriverData(validDriver)).toBe(true);
    });

    test('validateDriverData - missing fields', () => {
      const invalidDriver = {
        username: 'driver123',
        email: 'driver@example.com',
        // missing required fields
      };

      expect(validateDriverData(invalidDriver)).toBe(false);
    });

    test('validateDeliveryData - valid data', () => {
      const validDelivery = {
        pickup_location: '123 Pickup St',
        dropoff_location: '456 Dropoff Ave',
        item_description: 'Test package',
      };

      expect(validateDeliveryData(validDelivery)).toBe(true);
    });

    test('validateDeliveryData - missing fields', () => {
      const invalidDelivery = {
        pickup_location: '123 Pickup St',
        // missing required fields
      };

      expect(validateDeliveryData(invalidDelivery)).toBe(false);
    });

    test('validateEmailFormat - valid emails', () => {
      const validEmails = [
        'test@example.com',
        'user@domain.co.uk',
        'name.surname@company.org',
        'user123@test-domain.com',
      ];

      validEmails.forEach(email => {
        expect(validateEmailFormat(email)).toBe(true);
      });
    });

    test('validateEmailFormat - invalid emails', () => {
      const invalidEmails = [
        'invalid-email',
        'user@',
        '@domain.com',
        'user@domain',
        'user space@domain.com',
        '',
      ];

      invalidEmails.forEach(email => {
        expect(validateEmailFormat(email)).toBe(false);
      });
    });

    test('validatePhoneFormat - valid phones', () => {
      const validPhones = [
        '555-1234',
        '123-4567',
        '999-0000',
      ];

      validPhones.forEach(phone => {
        expect(validatePhoneFormat(phone)).toBe(true);
      });
    });

    test('validatePhoneFormat - invalid phones', () => {
      const invalidPhones = [
        '5551234',
        '555-12345',
        '55-1234',
        '555-abc4',
        '',
        '555 1234',
      ];

      invalidPhones.forEach(phone => {
        expect(validatePhoneFormat(phone)).toBe(false);
      });
    });
  });

  describe('Constants Validation', () => {
    test('DELIVERY_STATUSES contains expected values', () => {
      expect(DELIVERY_STATUSES).toContain('Pending');
      expect(DELIVERY_STATUSES).toContain('En Route');
      expect(DELIVERY_STATUSES).toContain('Completed');
      expect(DELIVERY_STATUSES).toContain('Cancelled');
      expect(DELIVERY_STATUSES).toHaveLength(4);
    });

    test('VEHICLE_CAPACITY_UNITS contains expected values', () => {
      expect(VEHICLE_CAPACITY_UNITS).toContain('kg');
      expect(VEHICLE_CAPACITY_UNITS).toContain('lb');
      expect(VEHICLE_CAPACITY_UNITS).toHaveLength(2);
    });

    test('all mock deliveries have valid statuses', () => {
      mockDeliveries.forEach(delivery => {
        expect(DELIVERY_STATUSES).toContain(delivery.status);
      });
    });

    test('all mock vehicles have valid capacity units', () => {
      mockVehicles.forEach(vehicle => {
        expect(VEHICLE_CAPACITY_UNITS).toContain(vehicle.capacity_unit);
      });
    });
  });

  describe('Registration Data Validation', () => {
    test('customer registration data is valid', () => {
      expect(validateCustomerData(mockRegistrationData.customer)).toBe(true);
      expect(validateEmailFormat(mockRegistrationData.customer.email)).toBe(true);
      expect(validatePhoneFormat(mockRegistrationData.customer.phone_number)).toBe(true);
    });

    test('business customer registration data is valid', () => {
      expect(validateCustomerData(mockRegistrationData.businessCustomer)).toBe(true);
      expect(validateEmailFormat(mockRegistrationData.businessCustomer.email)).toBe(true);
      expect(validatePhoneFormat(mockRegistrationData.businessCustomer.phone_number)).toBe(true);
      expect(mockRegistrationData.businessCustomer.is_business).toBe(true);
      expect(mockRegistrationData.businessCustomer.company_name).toBeTruthy();
    });

    test('driver registration data is valid', () => {
      expect(validateDriverData(mockRegistrationData.driver)).toBe(true);
      expect(validateEmailFormat(mockRegistrationData.driver.email)).toBe(true);
      expect(validatePhoneFormat(mockRegistrationData.driver.phone_number)).toBe(true);
      expect(VEHICLE_CAPACITY_UNITS).toContain(mockRegistrationData.driver.vehicle_capacity_unit);
    });
  });

  describe('Cross-Reference Data Integrity', () => {
    test('delivery customer references exist in customers', () => {
      const customerIds = mockCustomers.map(c => c.id);
      mockDeliveries.forEach(delivery => {
        expect(customerIds).toContain(delivery.customer);
      });
    });

    test('customer emails are unique', () => {
      const emails = mockCustomers.map(c => c.email);
      const uniqueEmails = [...new Set(emails)];
      expect(emails.length).toBe(uniqueEmails.length);
    });

    test('driver emails are unique', () => {
      const emails = mockDrivers.map(d => d.email);
      const uniqueEmails = [...new Set(emails)];
      expect(emails.length).toBe(uniqueEmails.length);
    });

    test('vehicle license plates are unique', () => {
      const plates = mockVehicles.map(v => v.license_plate);
      const uniquePlates = [...new Set(plates)];
      expect(plates.length).toBe(uniquePlates.length);
    });

    test('vehicle capacities are positive numbers', () => {
      mockVehicles.forEach(vehicle => {
        expect(typeof vehicle.capacity).toBe('number');
        expect(vehicle.capacity).toBeGreaterThan(0);
      });
    });
  });
});