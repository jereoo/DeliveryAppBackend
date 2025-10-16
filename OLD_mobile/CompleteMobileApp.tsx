// 🚚 DeliveryApp Mobile - Complete Feature Set with ALL Backend Features
// Copy this content to C:\Users\360WEB\DeliveryAppMobile\App.tsx

import React, { useState, useEffect, useRef } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  Button, 
  Alert, 
  ScrollView, 
  ActivityIndicator, 
  TextInput, 
  TouchableOpacity,
  Switch,
  KeyboardAvoidingView,
  Platform,
  Modal,
  FlatList
} from 'react-native';

// ========================================
// TYPE DEFINITIONS
// ========================================

interface CustomerData {
  id?: number;
  username: string;
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  address: string;
  company_name?: string;
  is_business: boolean;
  preferred_pickup_address?: string;
}

interface DriverData {
  id?: number;
  username: string;
  email: string;
  password?: string;
  name: string;
  phone_number: string;
  license_number: string;
  active?: boolean;
  current_vehicle?: number;
  current_vehicle_plate?: string;
}

interface VehicleData {
  id?: number;
  license_plate: string;
  model: string;
  capacity: number;
  capacity_unit?: string;
  active?: boolean;
}

interface DeliveryData {
  id?: number;
  customer_name?: string;
  pickup_location: string;
  dropoff_location: string;
  status: string;
  item_description?: string;
  delivery_date?: string;
  delivery_time?: string;
  same_pickup_as_customer?: boolean;
  use_preferred_pickup?: boolean;
  customer?: number;
}

interface DeliveryAssignmentData {
  id?: number;
  delivery: number;
  driver: number;
  vehicle: number;
  assigned_at?: string;
  driver_name?: string;
  vehicle_license_plate?: string;
  customer_name?: string;
}

interface DriverVehicleData {
  id?: number;
  driver: number;
  vehicle: number;
  assigned_from: string;
  assigned_to?: string;
  driver_name?: string;
  vehicle_license_plate?: string;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
}

type Screen = 
  | 'main' 
  | 'login' 
  | 'customer_register' 
  | 'driver_register'
  | 'dashboard'
  | 'delivery_request'
  | 'my_deliveries'
  | 'admin_customers'
  | 'admin_drivers' 
  | 'admin_vehicles'
  | 'admin_deliveries'
  | 'admin_assignments'
  | 'admin_driver_vehicles'
  | 'vehicle_form'
  | 'driver_vehicle_assign'
  | 'delivery_detail';

type UserType = 'admin' | 'customer' | 'driver' | null;

// ========================================
// MAIN COMPONENT
// ========================================

export default function App() {
  // ========================================
  // STATE MANAGEMENT
  // ========================================
  
  const [currentScreen, setCurrentScreen] = useState<Screen>('main');
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [loading, setLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [userType, setUserType] = useState<UserType>(null);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  
  // Data states
  const [deliveries, setDeliveries] = useState<DeliveryData[]>([]);
  const [customers, setCustomers] = useState<CustomerData[]>([]);
  const [drivers, setDrivers] = useState<DriverData[]>([]);
  const [vehicles, setVehicles] = useState<VehicleData[]>([]);
  const [assignments, setAssignments] = useState<DeliveryAssignmentData[]>([]);
  const [driverVehicles, setDriverVehicles] = useState<DriverVehicleData[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  // Network detection
  const NETWORK_ENDPOINTS = [
    { url: 'http://192.168.1.87:8081', name: 'Home Office Network' },
    { url: 'http://192.168.1.82:8081', name: 'Home Office Network (Alt)' },
    { url: 'http://172.20.10.6:8081', name: 'Mobile Hotspot' },
    { url: 'http://localhost:8081', name: 'Local Development' }
  ];
  
  const [API_BASE, setApiBase] = useState<string>(NETWORK_ENDPOINTS[0].url);
  const [currentNetwork, setCurrentNetwork] = useState<string>('Detecting...');

  // Form states
  const [customerForm, setCustomerForm] = useState<CustomerData>({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    company_name: '',
    is_business: false,
    preferred_pickup_address: ''
  });

  const [driverForm, setDriverForm] = useState<DriverData>({
    username: '',
    email: '',
    password: '',
    name: '',
    phone_number: '',
    license_number: ''
  });

  const [vehicleForm, setVehicleForm] = useState<VehicleData>({
    license_plate: '',
    model: '',
    capacity: 1000,
    capacity_unit: 'kg'
  });

  const [deliveryForm, setDeliveryForm] = useState<DeliveryData>({
    pickup_location: '',
    dropoff_location: '',
    item_description: '',
    same_pickup_as_customer: false,
    use_preferred_pickup: false
  });

  const [loginForm, setLoginForm] = useState({
    username: '',
    password: ''
  });

  // ========================================
  // NETWORK & BACKEND FUNCTIONS
  // ========================================

  const checkBackend = async () => {
    for (const endpoint of NETWORK_ENDPOINTS) {
      try {
        const response = await fetch(`${endpoint.url}/api/`, {
          method: 'GET'
        });
        
        if (response.ok) {
          setApiBase(endpoint.url);
          setCurrentNetwork(endpoint.name);
          setBackendStatus(`✅ Connected to ${endpoint.name}`);
          return;
        }
      } catch (error) {
        // Continue to next endpoint
      }
    }
    
    setBackendStatus('❌ No backend connection found');
    setCurrentNetwork('None');
  };

  const makeAuthenticatedRequest = async (endpoint: string, options: RequestInit = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
      ...options.headers
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Token expired, logout
      handleLogout();
      throw new Error('Authentication expired');
    }

    return response;
  };

  // ========================================
  // AUTHENTICATION FUNCTIONS
  // ========================================

  const handleLogin = async () => {
    try {
      setLoading(true);
      
      if (!loginForm.username || !loginForm.password) {
        Alert.alert('Error', 'Please enter username and password');
        return;
      }

      const response = await fetch(`${API_BASE}/api/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });

      if (response.ok) {
        const data = await response.json();
        setAuthToken(data.access);
        
        // Determine user type by trying different endpoints
        await determineUserType(data.access);
        
        setCurrentScreen('dashboard');
        setLoginForm({ username: '', password: '' });
        Alert.alert('Success!', 'Logged in successfully!');
      } else {
        const errorData = await response.json();
        Alert.alert('Login Failed', errorData.detail || 'Invalid credentials');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const determineUserType = async (token: string) => {
    try {
      // Try customer profile first
      const customerResponse = await fetch(`${API_BASE}/api/customers/me/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (customerResponse.ok) {
        setUserType('customer');
        return;
      }

      // Check if user is admin by trying to access admin endpoints
      const driversResponse = await fetch(`${API_BASE}/api/drivers/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (driversResponse.ok) {
        setUserType('admin');
        return;
      }

      // Default to driver if no other type matches
      setUserType('driver');
    } catch (error) {
      setUserType('customer'); // Default fallback
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    setUserType(null);
    setCurrentUser(null);
    setCurrentScreen('main');
    // Clear all data
    setDeliveries([]);
    setCustomers([]);
    setDrivers([]);
    setVehicles([]);
    setAssignments([]);
    setDriverVehicles([]);
  };

  // ========================================
  // REGISTRATION FUNCTIONS
  // ========================================

  const registerCustomer = async () => {
    try {
      setLoading(true);
      
      if (!customerForm.username || !customerForm.email || !customerForm.password) {
        Alert.alert('Error', 'Please fill required fields');
        return;
      }

      const response = await fetch(`${API_BASE}/api/customers/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerForm)
      });

      if (response.ok) {
        Alert.alert('Success!', 'Customer registered successfully! You can now login.');
        setCurrentScreen('login');
        setCustomerForm({
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          phone_number: '',
          address: '',
          company_name: '',
          is_business: false,
          preferred_pickup_address: ''
        });
      } else {
        const errorData = await response.json();
        Alert.alert('Registration Failed', JSON.stringify(errorData));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const registerDriver = async () => {
    try {
      setLoading(true);
      
      if (!driverForm.username || !driverForm.email || !driverForm.password || 
          !driverForm.name || !driverForm.phone_number || !driverForm.license_number) {
        Alert.alert('Error', 'Please fill all required fields');
        return;
      }

      const response = await fetch(`${API_BASE}/api/drivers/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(driverForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', `Driver ${data.name} registered successfully! You can now login.`);
        setCurrentScreen('login');
        setDriverForm({
          username: '',
          email: '',
          password: '',
          name: '',
          phone_number: '',
          license_number: ''
        });
      } else {
        const errorData = await response.json();
        Alert.alert('Registration Failed', JSON.stringify(errorData));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // ========================================
  // DELIVERY FUNCTIONS
  // ========================================

  const requestDelivery = async () => {
    try {
      setLoading(true);
      
      if (!deliveryForm.pickup_location || !deliveryForm.dropoff_location) {
        Alert.alert('Error', 'Please fill pickup and dropoff locations');
        return;
      }

      const response = await makeAuthenticatedRequest('/api/deliveries/request_delivery/', {
        method: 'POST',
        body: JSON.stringify(deliveryForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', `Delivery request #${data.id} created successfully!`);
        setCurrentScreen('dashboard');
        setDeliveryForm({
          pickup_location: '',
          dropoff_location: '',
          item_description: '',
          same_pickup_as_customer: false,
          use_preferred_pickup: false
        });
        // Refresh deliveries
        await fetchMyDeliveries();
      } else {
        const errorData = await response.json();
        Alert.alert('Request Failed', JSON.stringify(errorData));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyDeliveries = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/customers/my_deliveries/');
      if (response.ok) {
        const data = await response.json();
        setDeliveries(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    }
  };

  const fetchAllDeliveries = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/deliveries/');
      if (response.ok) {
        const data = await response.json();
        setDeliveries(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching all deliveries:', error);
    }
  };

  // ========================================
  // ADMIN DATA FUNCTIONS
  // ========================================

  const fetchCustomers = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/customers/');
      if (response.ok) {
        const data = await response.json();
        setCustomers(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const fetchDrivers = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/drivers/');
      if (response.ok) {
        const data = await response.json();
        setDrivers(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching drivers:', error);
    }
  };

  const fetchVehicles = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/vehicles/');
      if (response.ok) {
        const data = await response.json();
        setVehicles(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching vehicles:', error);
    }
  };

  const fetchAssignments = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/assignments/');
      if (response.ok) {
        const data = await response.json();
        setAssignments(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
    }
  };

  const fetchDriverVehicles = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/driver-vehicles/');
      if (response.ok) {
        const data = await response.json();
        setDriverVehicles(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching driver vehicles:', error);
    }
  };

  // ========================================
  // VEHICLE MANAGEMENT FUNCTIONS
  // ========================================

  const createVehicle = async () => {
    try {
      setLoading(true);
      
      if (!vehicleForm.license_plate || !vehicleForm.model || !vehicleForm.capacity) {
        Alert.alert('Error', 'Please fill all required fields');
        return;
      }

      const response = await makeAuthenticatedRequest('/api/vehicles/', {
        method: 'POST',
        body: JSON.stringify(vehicleForm)
      });

      if (response.ok) {
        Alert.alert('Success!', 'Vehicle created successfully!');
        setCurrentScreen('admin_vehicles');
        setVehicleForm({
          license_plate: '',
          model: '',
          capacity: 1000,
          capacity_unit: 'kg'
        });
        await fetchVehicles();
      } else {
        const errorData = await response.json();
        Alert.alert('Creation Failed', JSON.stringify(errorData));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // ========================================
  // INITIALIZATION
  // ========================================

  useEffect(() => {
    checkBackend();
  }, []);

  useEffect(() => {
    if (authToken && userType === 'customer') {
      fetchMyDeliveries();
    } else if (authToken && userType === 'admin') {
      fetchAllDeliveries();
      fetchCustomers();
      fetchDrivers();
      fetchVehicles();
      fetchAssignments();
      fetchDriverVehicles();
    }
  }, [authToken, userType]);

  // ========================================
  // SCREEN COMPONENTS
  // ========================================

  // Main/Landing Screen
  if (currentScreen === 'main') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🚚 DeliveryApp Mobile</Text>
          <Text style={styles.subtitle}>Complete Delivery Management System</Text>
          
          <View style={styles.statusContainer}>
            <Text style={styles.statusLabel}>Backend Status:</Text>
            <Text style={styles.status}>{backendStatus}</Text>
            <Text style={styles.networkLabel}>Network: {currentNetwork}</Text>
          </View>

          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text>Loading...</Text>
            </View>
          )}

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔐 Authentication</Text>
            <View style={styles.buttonContainer}>
              <Button title="🔑 Login" onPress={() => setCurrentScreen('login')} />
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📝 Registration</Text>
            <View style={styles.buttonContainer}>
              <Button title="👤 Register as Customer" onPress={() => setCurrentScreen('customer_register')} />
            </View>
            <View style={styles.buttonContainer}>
              <Button title="🚚 Register as Driver" onPress={() => setCurrentScreen('driver_register')} />
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔧 System</Text>
            <View style={styles.buttonContainer}>
              <Button title="🔄 Check Backend Connection" onPress={checkBackend} />
            </View>
          </View>
        </View>
      </ScrollView>
    );
  }

  // Login Screen
  if (currentScreen === 'login') {
    return (
      <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.content}>
          <Text style={styles.title}>🔑 Login</Text>
          
          <TextInput
            style={styles.input}
            value={loginForm.username}
            onChangeText={(text) => setLoginForm({...loginForm, username: text})}
            placeholder="Username"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            value={loginForm.password}
            onChangeText={(text) => setLoginForm({...loginForm, password: text})}
            placeholder="Password"
            secureTextEntry
          />

          <View style={styles.buttonContainer}>
            <Button title="Login" onPress={handleLogin} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back" onPress={() => setCurrentScreen('main')} />
          </View>

          <View style={styles.section}>
            <Text style={styles.infoText}>
              Need an account? Go back and register as a customer or driver first.
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Customer Registration Screen
  if (currentScreen === 'customer_register') {
    return (
      <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.content}>
          <Text style={styles.title}>👤 Customer Registration</Text>
          
          <Text style={styles.sectionTitle}>Account Information</Text>
          <TextInput
            style={styles.input}
            value={customerForm.username}
            onChangeText={(text) => setCustomerForm({...customerForm, username: text})}
            placeholder="Username *"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            value={customerForm.email}
            onChangeText={(text) => setCustomerForm({...customerForm, email: text})}
            placeholder="Email *"
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            value={customerForm.password}
            onChangeText={(text) => setCustomerForm({...customerForm, password: text})}
            placeholder="Password *"
            secureTextEntry
          />

          <Text style={styles.sectionTitle}>Personal Information</Text>
          <TextInput
            style={styles.input}
            value={customerForm.first_name}
            onChangeText={(text) => setCustomerForm({...customerForm, first_name: text})}
            placeholder="First Name"
          />

          <TextInput
            style={styles.input}
            value={customerForm.last_name}
            onChangeText={(text) => setCustomerForm({...customerForm, last_name: text})}
            placeholder="Last Name"
          />

          <TextInput
            style={styles.input}
            value={customerForm.phone_number}
            onChangeText={(text) => setCustomerForm({...customerForm, phone_number: text})}
            placeholder="Phone Number"
            keyboardType="phone-pad"
          />

          <TextInput
            style={[styles.input, styles.multilineInput]}
            value={customerForm.address}
            onChangeText={(text) => setCustomerForm({...customerForm, address: text})}
            placeholder="Address"
            multiline
            numberOfLines={3}
          />

          <Text style={styles.sectionTitle}>Business Customer</Text>
          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Is Business Customer</Text>
            <Switch
              value={customerForm.is_business}
              onValueChange={(value) => setCustomerForm({...customerForm, is_business: value})}
            />
          </View>

          {customerForm.is_business && (
            <TextInput
              style={styles.input}
              value={customerForm.company_name}
              onChangeText={(text) => setCustomerForm({...customerForm, company_name: text})}
              placeholder="Company Name"
            />
          )}

          <TextInput
            style={[styles.input, styles.multilineInput]}
            value={customerForm.preferred_pickup_address}
            onChangeText={(text) => setCustomerForm({...customerForm, preferred_pickup_address: text})}
            placeholder="Preferred Pickup Address (Optional)"
            multiline
            numberOfLines={2}
          />

          <View style={styles.buttonContainer}>
            <Button title="Register Customer" onPress={registerCustomer} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back" onPress={() => setCurrentScreen('main')} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Driver Registration Screen
  if (currentScreen === 'driver_register') {
    return (
      <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.content}>
          <Text style={styles.title}>🚚 Driver Registration</Text>
          
          <Text style={styles.sectionTitle}>Account Information</Text>
          <TextInput
            style={styles.input}
            value={driverForm.username}
            onChangeText={(text) => setDriverForm({...driverForm, username: text})}
            placeholder="Username *"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            value={driverForm.email}
            onChangeText={(text) => setDriverForm({...driverForm, email: text})}
            placeholder="Email *"
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            value={driverForm.password}
            onChangeText={(text) => setDriverForm({...driverForm, password: text})}
            placeholder="Password *"
            secureTextEntry
          />

          <Text style={styles.sectionTitle}>Driver Information</Text>
          <TextInput
            style={styles.input}
            value={driverForm.name}
            onChangeText={(text) => setDriverForm({...driverForm, name: text})}
            placeholder="Full Name *"
          />

          <TextInput
            style={styles.input}
            value={driverForm.phone_number}
            onChangeText={(text) => setDriverForm({...driverForm, phone_number: text})}
            placeholder="Phone Number *"
            keyboardType="phone-pad"
          />

          <TextInput
            style={styles.input}
            value={driverForm.license_number}
            onChangeText={(text) => setDriverForm({...driverForm, license_number: text})}
            placeholder="Driver License Number *"
          />

          <View style={styles.buttonContainer}>
            <Button title="Register Driver" onPress={registerDriver} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back" onPress={() => setCurrentScreen('main')} />
          </View>

          <View style={styles.section}>
            <Text style={styles.infoText}>
              Note: Vehicle assignment can be done by administrators after registration.
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Dashboard Screen (Post-Login)
  if (currentScreen === 'dashboard') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>📊 Dashboard</Text>
          <Text style={styles.subtitle}>Welcome, {userType?.toUpperCase()} User!</Text>
          
          <View style={styles.statusContainer}>
            <Text style={styles.statusLabel}>Status: Logged In</Text>
            <Text style={styles.networkLabel}>User Type: {userType}</Text>
          </View>

          {/* Customer Dashboard */}
          {userType === 'customer' && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📦 Customer Services</Text>
              <View style={styles.buttonContainer}>
                <Button title="📋 Request Delivery" onPress={() => setCurrentScreen('delivery_request')} />
              </View>
              <View style={styles.buttonContainer}>
                <Button title="📃 My Deliveries" onPress={() => setCurrentScreen('my_deliveries')} />
              </View>
            </View>
          )}

          {/* Driver Dashboard */}
          {userType === 'driver' && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>🚚 Driver Services</Text>
              <View style={styles.buttonContainer}>
                <Button title="📦 My Assignments" onPress={() => setCurrentScreen('my_deliveries')} />
              </View>
              <Text style={styles.infoText}>
                Driver-specific features are managed through the admin interface.
              </Text>
            </View>
          )}

          {/* Admin Dashboard */}
          {userType === 'admin' && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>⚙️ Admin Management</Text>
              <View style={styles.buttonContainer}>
                <Button title="👥 Manage Customers" onPress={() => setCurrentScreen('admin_customers')} />
              </View>
              <View style={styles.buttonContainer}>
                <Button title="🚚 Manage Drivers" onPress={() => setCurrentScreen('admin_drivers')} />
              </View>
              <View style={styles.buttonContainer}>
                <Button title="🚐 Manage Vehicles" onPress={() => setCurrentScreen('admin_vehicles')} />
              </View>
              <View style={styles.buttonContainer}>
                <Button title="📦 Manage Deliveries" onPress={() => setCurrentScreen('admin_deliveries')} />
              </View>
              <View style={styles.buttonContainer}>
                <Button title="🔗 Delivery Assignments" onPress={() => setCurrentScreen('admin_assignments')} />
              </View>
              <View style={styles.buttonContainer}>
                <Button title="🔧 Driver-Vehicle Assignments" onPress={() => setCurrentScreen('admin_driver_vehicles')} />
              </View>
            </View>
          )}

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔧 Account</Text>
            <View style={styles.buttonContainer}>
              <Button title="🚪 Logout" onPress={handleLogout} color="#FF3B30" />
            </View>
          </View>
        </View>
      </ScrollView>
    );
  }

  // Delivery Request Screen (Customer)
  if (currentScreen === 'delivery_request') {
    return (
      <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.content}>
          <Text style={styles.title}>📋 Request Delivery</Text>
          
          <Text style={styles.sectionTitle}>Pickup & Delivery</Text>
          
          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Use my address as pickup</Text>
            <Switch
              value={deliveryForm.same_pickup_as_customer || false}
              onValueChange={(value) => setDeliveryForm({...deliveryForm, same_pickup_as_customer: value})}
            />
          </View>

          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Use preferred pickup address</Text>
            <Switch
              value={deliveryForm.use_preferred_pickup || false}
              onValueChange={(value) => setDeliveryForm({...deliveryForm, use_preferred_pickup: value})}
            />
          </View>

          {!deliveryForm.same_pickup_as_customer && !deliveryForm.use_preferred_pickup && (
            <TextInput
              style={[styles.input, styles.multilineInput]}
              value={deliveryForm.pickup_location}
              onChangeText={(text) => setDeliveryForm({...deliveryForm, pickup_location: text})}
              placeholder="Pickup Location *"
              multiline
              numberOfLines={3}
            />
          )}

          <TextInput
            style={[styles.input, styles.multilineInput]}
            value={deliveryForm.dropoff_location}
            onChangeText={(text) => setDeliveryForm({...deliveryForm, dropoff_location: text})}
            placeholder="Dropoff Location *"
            multiline
            numberOfLines={3}
          />

          <Text style={styles.sectionTitle}>Item Details</Text>
          <TextInput
            style={[styles.input, styles.multilineInput]}
            value={deliveryForm.item_description}
            onChangeText={(text) => setDeliveryForm({...deliveryForm, item_description: text})}
            placeholder="Item Description"
            multiline
            numberOfLines={4}
          />

          <View style={styles.buttonContainer}>
            <Button title="📋 Request Delivery" onPress={requestDelivery} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // My Deliveries Screen
  if (currentScreen === 'my_deliveries') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>📃 My Deliveries</Text>
          
          {deliveries.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No deliveries found.</Text>
            </View>
          ) : (
            <FlatList
              data={deliveries}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>Delivery #{item.id}</Text>
                  <Text style={styles.listItemText}>From: {item.pickup_location}</Text>
                  <Text style={styles.listItemText}>To: {item.dropoff_location}</Text>
                  <Text style={[styles.listItemText, styles.statusText]}>Status: {item.status}</Text>
                  {item.item_description && (
                    <Text style={styles.listItemText}>Item: {item.item_description}</Text>
                  )}
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={userType === 'customer' ? fetchMyDeliveries : fetchAllDeliveries} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Admin Customers Screen
  if (currentScreen === 'admin_customers') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>👥 Manage Customers</Text>
          
          {customers.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No customers found.</Text>
            </View>
          ) : (
            <FlatList
              data={customers}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>{item.first_name} {item.last_name}</Text>
                  <Text style={styles.listItemText}>Username: {item.username}</Text>
                  <Text style={styles.listItemText}>Email: {item.email}</Text>
                  <Text style={styles.listItemText}>Phone: {item.phone_number}</Text>
                  {item.is_business && (
                    <Text style={styles.listItemText}>Company: {item.company_name}</Text>
                  )}
                  <Text style={styles.listItemText}>Address: {item.address}</Text>
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={fetchCustomers} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Admin Drivers Screen
  if (currentScreen === 'admin_drivers') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🚚 Manage Drivers</Text>
          
          {drivers.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No drivers found.</Text>
            </View>
          ) : (
            <FlatList
              data={drivers}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>{item.name}</Text>
                  <Text style={styles.listItemText}>License: {item.license_number}</Text>
                  <Text style={styles.listItemText}>Phone: {item.phone_number}</Text>
                  <Text style={styles.listItemText}>Status: {item.active ? 'Active' : 'Inactive'}</Text>
                  {item.current_vehicle_plate && (
                    <Text style={styles.listItemText}>Vehicle: {item.current_vehicle_plate}</Text>
                  )}
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={fetchDrivers} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Admin Vehicles Screen
  if (currentScreen === 'admin_vehicles') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🚐 Manage Vehicles</Text>
          
          {vehicles.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No vehicles found.</Text>
            </View>
          ) : (
            <FlatList
              data={vehicles}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>{item.license_plate}</Text>
                  <Text style={styles.listItemText}>Model: {item.model}</Text>
                  <Text style={styles.listItemText}>Capacity: {item.capacity} {item.capacity_unit || 'kg'}</Text>
                  <Text style={styles.listItemText}>Status: {item.active ? 'Active' : 'Inactive'}</Text>
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="➕ Add Vehicle" onPress={() => setCurrentScreen('vehicle_form')} />
          </View>

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={fetchVehicles} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Vehicle Form Screen
  if (currentScreen === 'vehicle_form') {
    return (
      <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.content}>
          <Text style={styles.title}>➕ Add Vehicle</Text>
          
          <TextInput
            style={styles.input}
            value={vehicleForm.license_plate}
            onChangeText={(text) => setVehicleForm({...vehicleForm, license_plate: text})}
            placeholder="License Plate *"
            autoCapitalize="characters"
          />

          <TextInput
            style={styles.input}
            value={vehicleForm.model}
            onChangeText={(text) => setVehicleForm({...vehicleForm, model: text})}
            placeholder="Vehicle Model *"
          />

          <TextInput
            style={styles.input}
            value={vehicleForm.capacity.toString()}
            onChangeText={(text) => setVehicleForm({...vehicleForm, capacity: parseInt(text) || 0})}
            placeholder="Capacity *"
            keyboardType="numeric"
          />

          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Capacity Unit: {vehicleForm.capacity_unit?.toUpperCase()}</Text>
            <Switch
              value={vehicleForm.capacity_unit === 'lb'}
              onValueChange={(value) => setVehicleForm({
                ...vehicleForm, 
                capacity_unit: value ? 'lb' : 'kg'
              })}
            />
          </View>

          <View style={styles.buttonContainer}>
            <Button title="Create Vehicle" onPress={createVehicle} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Cancel" onPress={() => setCurrentScreen('admin_vehicles')} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Admin Deliveries Screen
  if (currentScreen === 'admin_deliveries') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>📦 Manage Deliveries</Text>
          
          {deliveries.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No deliveries found.</Text>
            </View>
          ) : (
            <FlatList
              data={deliveries}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>Delivery #{item.id}</Text>
                  <Text style={styles.listItemText}>Customer: {item.customer_name}</Text>
                  <Text style={styles.listItemText}>From: {item.pickup_location}</Text>
                  <Text style={styles.listItemText}>To: {item.dropoff_location}</Text>
                  <Text style={[styles.listItemText, styles.statusText]}>Status: {item.status}</Text>
                  {item.item_description && (
                    <Text style={styles.listItemText}>Item: {item.item_description}</Text>
                  )}
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={fetchAllDeliveries} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Admin Assignments Screen
  if (currentScreen === 'admin_assignments') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🔗 Delivery Assignments</Text>
          
          {assignments.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No delivery assignments found.</Text>
            </View>
          ) : (
            <FlatList
              data={assignments}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>Assignment #{item.id}</Text>
                  <Text style={styles.listItemText}>Delivery: #{item.delivery}</Text>
                  <Text style={styles.listItemText}>Driver: {item.driver_name || `ID: ${item.driver}`}</Text>
                  <Text style={styles.listItemText}>Vehicle: {item.vehicle_license_plate || `ID: ${item.vehicle}`}</Text>
                  <Text style={styles.listItemText}>Customer: {item.customer_name}</Text>
                  {item.assigned_at && (
                    <Text style={styles.listItemText}>Assigned: {new Date(item.assigned_at).toLocaleDateString()}</Text>
                  )}
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={fetchAssignments} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Admin Driver-Vehicle Assignments Screen
  if (currentScreen === 'admin_driver_vehicles') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🔧 Driver-Vehicle Assignments</Text>
          
          {driverVehicles.length === 0 ? (
            <View style={styles.section}>
              <Text style={styles.infoText}>No driver-vehicle assignments found.</Text>
            </View>
          ) : (
            <FlatList
              data={driverVehicles}
              keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
              renderItem={({ item }) => (
                <View style={styles.listItem}>
                  <Text style={styles.listItemTitle}>Assignment #{item.id}</Text>
                  <Text style={styles.listItemText}>Driver: {item.driver_name || `ID: ${item.driver}`}</Text>
                  <Text style={styles.listItemText}>Vehicle: {item.vehicle_license_plate || `ID: ${item.vehicle}`}</Text>
                  <Text style={styles.listItemText}>From: {item.assigned_from}</Text>
                  {item.assigned_to && (
                    <Text style={styles.listItemText}>To: {item.assigned_to}</Text>
                  )}
                  {!item.assigned_to && (
                    <Text style={[styles.listItemText, styles.statusText]}>Status: Active</Text>
                  )}
                </View>
              )}
              scrollEnabled={false}
            />
          )}

          <View style={styles.buttonContainer}>
            <Button title="🔄 Refresh" onPress={fetchDriverVehicles} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  // Default fallback
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>DeliveryApp Mobile</Text>
        <Text style={styles.infoText}>Unknown screen: {currentScreen}</Text>
        <Button title="Go to Main" onPress={() => setCurrentScreen('main')} />
      </View>
    </View>
  );
}

// ========================================
// STYLES
// ========================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    color: '#555',
  },
  section: {
    marginVertical: 15,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statusContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  status: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  networkLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  buttonContainer: {
    marginVertical: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
    marginBottom: 10,
  },
  multilineInput: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 15,
    marginBottom: 10,
  },
  switchLabel: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    fontStyle: 'italic',
    marginVertical: 10,
  },
  listItem: {
    backgroundColor: '#f9f9f9',
    padding: 15,
    marginVertical: 5,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  listItemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  listItemText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  statusText: {
    fontWeight: 'bold',
    color: '#007AFF',
  },
});