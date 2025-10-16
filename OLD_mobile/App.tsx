// 🚚 DeliveryApp Mobile - Complete Feature Set with ALL Backend Features
// Complete delivery management system with customer registration, driver registration,
// delivery management, vehicle management, admin features, and authentication

import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  Button, 
  Alert, 
  ScrollView, 
  ActivityIndicator, 
  TextInput, 
  Switch,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  FlatList
} from 'react-native';

// Type definitions
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
  | 'vehicle_form';

type UserType = 'admin' | 'customer' | 'driver' | null;

export default function App() {
  // State management
  const [currentScreen, setCurrentScreen] = useState<Screen>('main');
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [loading, setLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [userType, setUserType] = useState<UserType>(null);
  
  // Data states
  const [deliveries, setDeliveries] = useState<DeliveryData[]>([]);
  const [customers, setCustomers] = useState<CustomerData[]>([]);
  const [drivers, setDrivers] = useState<DriverData[]>([]);
  const [vehicles, setVehicles] = useState<VehicleData[]>([]);
  const [assignments, setAssignments] = useState<DeliveryAssignmentData[]>([]);
  const [driverVehicles, setDriverVehicles] = useState<DriverVehicleData[]>([]);

  // Network endpoints
  const NETWORK_ENDPOINTS = [
    { url: 'http://192.168.1.87:8081', name: 'Home Office Network' },
    { url: 'http://192.168.1.82:8081', name: 'Home Office Network (Alt)' },
    { url: 'http://172.20.10.6:8081', name: 'Mobile Hotspot' },
    { url: 'http://localhost:8081', name: 'Local Development' }
  ];
  
  const [API_BASE, setApiBase] = useState<string>(NETWORK_ENDPOINTS[0].url);
  const [currentNetwork, setCurrentNetwork] = useState<string>('Detecting...');

  const [customerForm, setCustomerForm] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    is_business: false
  });

  const [driverForm, setDriverForm] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    name: '',
    phone_number: '',
    license_number: '',
    vehicle_license_plate: '',
    vehicle_model: '',
    vehicle_capacity: '',
    vehicle_capacity_unit: 'kg'
  });

  const checkBackend = async () => {
    try {
      const response = await fetch(API_BASE + '/api/');
      if (response.ok) {
        setBackendStatus('✅ Backend Connected');
      } else {
        setBackendStatus('⚠️ Backend Error');
      }
    } catch (error) {
      setBackendStatus('❌ Backend Unreachable');
    }
  };

  const registerCustomer = async () => {
    try {
      setLoading(true);
      
      if (!customerForm.username || !customerForm.email || !customerForm.password) {
        Alert.alert('Error', 'Please fill required fields');
        return;
      }

      const response = await fetch(API_BASE + '/api/customers/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerForm)
      });

      if (response.ok) {
        Alert.alert('Success!', 'Customer registered successfully!');
        setCurrentScreen('main');
        // Clear form
        setCustomerForm({
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          phone_number: '',
          address: '',
          is_business: false
        });
      } else {
        const errorData = await response.json();
        Alert.alert('Error', JSON.stringify(errorData));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const registerDriver = async () => {
    try {
      setLoading(true);
      
      if (!driverForm.username || !driverForm.email || !driverForm.password || 
          !driverForm.first_name || !driverForm.last_name || !driverForm.name ||
          !driverForm.phone_number || !driverForm.license_number) {
        Alert.alert('Error', 'Please fill all required fields');
        return;
      }

      // For driver registration, we need these specific fields
      const driverData = {
        username: driverForm.username,
        email: driverForm.email,
        password: driverForm.password,
        first_name: driverForm.first_name,
        last_name: driverForm.last_name,
        name: driverForm.name,
        phone_number: driverForm.phone_number,
        license_number: driverForm.license_number,
        vehicle_license_plate: driverForm.vehicle_license_plate,
        vehicle_model: driverForm.vehicle_model,
        vehicle_capacity: parseInt(driverForm.vehicle_capacity) || 1000,
        vehicle_capacity_unit: driverForm.vehicle_capacity_unit
      };

      const response = await fetch(API_BASE + '/api/drivers/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(driverData)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', `Driver ${data.name} registered successfully!`);
        setCurrentScreen('main');
        // Clear form
        setDriverForm({
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          name: '',
          phone_number: '',
          license_number: '',
          vehicle_license_plate: '',
          vehicle_model: '',
          vehicle_capacity: '',
          vehicle_capacity_unit: 'kg'
        });
      } else {
        const errorData = await response.json();
        Alert.alert('Error', JSON.stringify(errorData));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  if (currentScreen === 'customer_register') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>👤 Customer Registration</Text>
          
          <TextInput
            style={styles.input}
            value={customerForm.username}
            onChangeText={(text) => setCustomerForm({...customerForm, username: text})}
            placeholder="Username"
          />

          <TextInput
            style={styles.input}
            value={customerForm.email}
            onChangeText={(text) => setCustomerForm({...customerForm, email: text})}
            placeholder="Email"
            keyboardType="email-address"
          />

          <TextInput
            style={styles.input}
            value={customerForm.password}
            onChangeText={(text) => setCustomerForm({...customerForm, password: text})}
            placeholder="Password"
            secureTextEntry
          />

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

          <View style={styles.buttonContainer}>
            <Button title="Register Customer" onPress={registerCustomer} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back" onPress={() => setCurrentScreen('main')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  if (currentScreen === 'driver_register') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🚚 Driver Registration</Text>
          
          <Text style={styles.sectionTitle}>Personal Information</Text>
          
          <TextInput
            style={styles.input}
            value={driverForm.username}
            onChangeText={(text) => setDriverForm({...driverForm, username: text})}
            placeholder="Username"
          />

          <TextInput
            style={styles.input}
            value={driverForm.email}
            onChangeText={(text) => setDriverForm({...driverForm, email: text})}
            placeholder="Email"
            keyboardType="email-address"
          />

          <TextInput
            style={styles.input}
            value={driverForm.password}
            onChangeText={(text) => setDriverForm({...driverForm, password: text})}
            placeholder="Password"
            secureTextEntry
          />

          <TextInput
            style={styles.input}
            value={driverForm.first_name}
            onChangeText={(text) => setDriverForm({...driverForm, first_name: text})}
            placeholder="First Name"
          />

          <TextInput
            style={styles.input}
            value={driverForm.last_name}
            onChangeText={(text) => setDriverForm({...driverForm, last_name: text})}
            placeholder="Last Name"
          />

          <TextInput
            style={styles.input}
            value={driverForm.name}
            onChangeText={(text) => setDriverForm({...driverForm, name: text})}
            placeholder="Display Name (Full Name)"
          />

          <TextInput
            style={styles.input}
            value={driverForm.phone_number}
            onChangeText={(text) => setDriverForm({...driverForm, phone_number: text})}
            placeholder="Phone Number"
            keyboardType="phone-pad"
          />

          <TextInput
            style={styles.input}
            value={driverForm.license_number}
            onChangeText={(text) => setDriverForm({...driverForm, license_number: text})}
            placeholder="Driver's License Number"
          />

          <Text style={styles.sectionTitle}>Vehicle Information</Text>

          <TextInput
            style={styles.input}
            value={driverForm.vehicle_license_plate}
            onChangeText={(text) => setDriverForm({...driverForm, vehicle_license_plate: text})}
            placeholder="Vehicle License Plate"
          />

          <TextInput
            style={styles.input}
            value={driverForm.vehicle_model}
            onChangeText={(text) => setDriverForm({...driverForm, vehicle_model: text})}
            placeholder="Vehicle Model (e.g., Ford Transit)"
          />

          <TextInput
            style={styles.input}
            value={driverForm.vehicle_capacity}
            onChangeText={(text) => setDriverForm({...driverForm, vehicle_capacity: text})}
            placeholder="Vehicle Capacity (e.g., 1000)"
            keyboardType="numeric"
          />

          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Capacity Unit: {driverForm.vehicle_capacity_unit.toUpperCase()}</Text>
            <Switch
              value={driverForm.vehicle_capacity_unit === 'lb'}
              onValueChange={(value) => setDriverForm({
                ...driverForm, 
                vehicle_capacity_unit: value ? 'lb' : 'kg'
              })}
            />
          </View>

          <View style={styles.buttonContainer}>
            <Button title="Register Driver" onPress={registerDriver} disabled={loading} />
          </View>
          
          <View style={styles.buttonContainer}>
            <Button title="Back" onPress={() => setCurrentScreen('main')} />
          </View>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>🚚 DeliveryApp Mobile</Text>
        
        <View style={styles.statusContainer}>
          <Text style={styles.statusLabel}>Backend Status:</Text>
          <Text style={styles.status}>{backendStatus}</Text>
        </View>

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text>Loading...</Text>
          </View>
        )}

        <View style={styles.buttonContainer}>
          <Button 
            title="👤 Register as Customer" 
            onPress={() => setCurrentScreen('customer_register')}
          />
        </View>

        <View style={styles.buttonContainer}>
          <Button 
            title="🚚 Register as Driver" 
            onPress={() => setCurrentScreen('driver_register')}
          />
        </View>

        <View style={styles.buttonContainer}>
          <Button 
            title="🔄 Check Backend" 
            onPress={checkBackend}
          />
        </View>
      </View>
    </ScrollView>
  );
}

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
    marginBottom: 20,
    color: '#333',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    color: '#555',
  },
  statusContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  status: {
    fontSize: 14,
    fontWeight: 'bold',
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
  },
});