// 🚚 DeliveryApp Mobile - Fixed Keyboard & Form Navigation
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
  Keyboard
} from 'react-native';

interface DeliveryData {
  id: number;
  customer_name?: string;
  pickup_location: string;
  dropoff_location: string;
  status: string;
  item_description?: string;
}

interface CustomerData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  address: string;
  company_name?: string;
  is_business: boolean;
}

interface DriverData {
  username: string;
  email: string;
  password: string;
  name: string;
  phone_number: string;
  license_number: string;
  vehicle_id?: number;
}

interface DeliveryRequest {
  pickup_location: string;
  dropoff_location: string;
  item_description: string;
  same_pickup_as_customer: boolean;
  use_preferred_pickup: boolean;
}

type Screen = 'main' | 'customer_register' | 'driver_register' | 'delivery_request' | 'login';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('main');
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [deliveries, setDeliveries] = useState<DeliveryData[]>([]);
  const [loading, setLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [currentNetwork, setCurrentNetwork] = useState<string>('Detecting...');
  const [userType, setUserType] = useState<'admin' | 'customer' | 'driver' | null>(null);

  // Refs for form navigation
  const scrollViewRef = useRef<ScrollView>(null);
  const customerFormRefs = {
    username: useRef<TextInput>(null),
    email: useRef<TextInput>(null),
    password: useRef<TextInput>(null),
    first_name: useRef<TextInput>(null),
    last_name: useRef<TextInput>(null),
    phone_number: useRef<TextInput>(null),
    address: useRef<TextInput>(null),
    company_name: useRef<TextInput>(null),
  };

  const driverFormRefs = {
    username: useRef<TextInput>(null),
    email: useRef<TextInput>(null),
    password: useRef<TextInput>(null),
    name: useRef<TextInput>(null),
    phone_number: useRef<TextInput>(null),
    license_number: useRef<TextInput>(null),
  };

  // Network endpoints to try
  const NETWORK_ENDPOINTS = [
    { url: 'http://192.168.1.87:8081', name: 'Home Office Network' },
    { url: 'http://192.168.1.82:8081', name: 'Home Office Network (Alt)' },
    { url: 'http://172.20.10.6:8081', name: 'Mobile Hotspot' }
  ];
  
  const [API_BASE, setApiBase] = useState<string>(NETWORK_ENDPOINTS[0].url);

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
    is_business: false
  });

  const [driverForm, setDriverForm] = useState<DriverData>({
    username: '',
    email: '',
    password: '',
    name: '',
    phone_number: '',
    license_number: ''
  });

  const [deliveryForm, setDeliveryForm] = useState<DeliveryRequest>({
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

  // Auto-detect network endpoint
  const checkBackend = async () => {
    for (const endpoint of NETWORK_ENDPOINTS) {
      try {
        const response = await fetch(`${endpoint.url}/api/`, {
          method: 'GET',
          timeout: 3000
        });
        
        if (response.ok) {
          setApiBase(endpoint.url);
          setCurrentNetwork(endpoint.name);
          setBackendStatus(`✅ Connected to ${endpoint.name}`);
          return;
        }
      } catch (error) {
        continue;
      }
    }
    setBackendStatus('❌ Backend unreachable');
  };

  const registerCustomer = async () => {
    try {
      setLoading(true);
      
      // Validate required fields
      if (!customerForm.username || !customerForm.email || !customerForm.password || 
          !customerForm.first_name || !customerForm.last_name || !customerForm.phone_number || 
          !customerForm.address) {
        Alert.alert('Error', 'Please fill in all required fields');
        return;
      }

      const response = await fetch(`${API_BASE}/api/customers/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', `Customer ${data.first_name} registered successfully! You can now login.`);
        setCurrentScreen('login');
        // Clear form
        setCustomerForm({
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          phone_number: '',
          address: '',
          company_name: '',
          is_business: false
        });
      } else {
        const errorData = await response.json();
        const errorMessage = typeof errorData === 'object' 
          ? Object.values(errorData).flat().join(', ') 
          : 'Registration failed';
        Alert.alert('Registration Failed', errorMessage);
      }
    } catch (error: any) {
      Alert.alert('Error', `Registration failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const registerDriver = async () => {
    try {
      setLoading(true);
      
      // Validate required fields
      if (!driverForm.username || !driverForm.email || !driverForm.password || 
          !driverForm.name || !driverForm.phone_number || !driverForm.license_number) {
        Alert.alert('Error', 'Please fill in all required fields');
        return;
      }

      const response = await fetch(`${API_BASE}/api/drivers/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(driverForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', `Driver ${data.name} registered successfully! You can now login.`);
        setCurrentScreen('login');
        // Clear form
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
        const errorMessage = typeof errorData === 'object' 
          ? Object.values(errorData).flat().join(', ') 
          : 'Registration failed';
        Alert.alert('Registration Failed', errorMessage);
      }
    } catch (error: any) {
      Alert.alert('Error', `Registration failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      setLoading(true);
      
      if (!loginForm.username || !loginForm.password) {
        Alert.alert('Error', 'Please enter username and password');
        return;
      }

      const response = await fetch(`${API_BASE}/api/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginForm)
      });

      if (response.ok) {
        const data = await response.json();
        setAuthToken(data.access);
        
        // Determine user type
        if (loginForm.username === 'admin') {
          setUserType('admin');
        } else {
          setUserType('customer'); // Default to customer
        }
        
        Alert.alert('Success!', 'Logged in successfully!');
        setCurrentScreen('main');
        setLoginForm({ username: '', password: '' });
      } else {
        Alert.alert('Login Failed', 'Invalid credentials');
      }
    } catch (error: any) {
      Alert.alert('Error', `Login failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const requestDelivery = async () => {
    try {
      setLoading(true);
      
      if (!authToken) {
        Alert.alert('Error', 'Please login first');
        return;
      }

      if (!deliveryForm.pickup_location || !deliveryForm.dropoff_location || !deliveryForm.item_description) {
        Alert.alert('Error', 'Please fill in all required fields');
        return;
      }

      const response = await fetch(`${API_BASE}/api/deliveries/request_delivery/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deliveryForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', `Delivery request submitted! ID: ${data.id}`);
        setCurrentScreen('main');
        // Clear form
        setDeliveryForm({
          pickup_location: '',
          dropoff_location: '',
          item_description: '',
          same_pickup_as_customer: false,
          use_preferred_pickup: false
        });
      } else {
        const errorData = await response.json();
        Alert.alert('Request Failed', errorData.detail || 'Failed to submit delivery request');
      }
    } catch (error: any) {
      Alert.alert('Error', `Request failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadDeliveries = async (token?: string) => {
    try {
      setLoading(true);
      const accessToken = token || authToken;
      
      if (!accessToken) {
        Alert.alert('Error', 'Please authenticate first');
        return;
      }

      const endpoint = userType === 'admin' ? 'deliveries' : 'deliveries';
      const response = await fetch(`${API_BASE}/api/${endpoint}/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        const deliveryList = data.results || data || [];
        setDeliveries(deliveryList);
        Alert.alert('Success!', `Loaded ${deliveryList.length} deliveries`);
      } else if (response.status === 401) {
        Alert.alert('Error', 'Authentication required or expired');
        setAuthToken(null);
        setUserType(null);
      } else {
        Alert.alert('Error', `Failed to load deliveries: ${response.status}`);
      }
    } catch (error: any) {
      Alert.alert('Error', `Failed to load deliveries: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setAuthToken(null);
    setUserType(null);
    setCurrentScreen('main');
    Alert.alert('Success', 'Logged out successfully');
  };

  useEffect(() => {
    checkBackend();
  }, []);

  // Scroll to input when focused
  const scrollToInput = (inputRef: React.RefObject<TextInput>) => {
    setTimeout(() => {
      inputRef.current?.measure((fx, fy, width, height, px, py) => {
        scrollViewRef.current?.scrollTo({
          y: py - 100, // Offset to ensure field is visible above keyboard
          animated: true
        });
      });
    }, 100);
  };

  // Main Screen
  if (currentScreen === 'main') {
    return (
      <ScrollView style={styles.container} ref={scrollViewRef}>
        <View style={styles.content}>
          <Text style={styles.title}>🚚 DeliveryApp Mobile</Text>
          <Text style={styles.subtitle}>Complete Feature Set</Text>
          
          <View style={styles.statusContainer}>
            <Text style={styles.statusLabel}>Backend Status:</Text>
            <Text style={[styles.status, backendStatus.includes('✅') ? styles.success : styles.error]}>
              {backendStatus}
            </Text>
          </View>

          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text>Loading...</Text>
            </View>
          )}

          {!authToken ? (
            <>
              <View style={styles.buttonContainer}>
                <Button 
                  title="👤 Login" 
                  onPress={() => setCurrentScreen('login')}
                />
              </View>
              
              <View style={styles.buttonContainer}>
                <Button 
                  title="📝 Register as Customer" 
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
                  title="🔐 Admin Login" 
                  onPress={() => {
                    setLoginForm({ username: 'admin', password: 'w3r3w0lf' });
                    setCurrentScreen('login');
                  }}
                />
              </View>
            </>
          ) : (
            <>
              <View style={styles.userInfo}>
                <Text style={styles.userInfoText}>
                  Logged in as: {userType?.toUpperCase()}
                </Text>
              </View>

              <View style={styles.buttonContainer}>
                <Button 
                  title="📦 Request Delivery" 
                  onPress={() => setCurrentScreen('delivery_request')}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button 
                  title="📋 Load Deliveries" 
                  onPress={() => loadDeliveries()}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button 
                  title="🚪 Logout" 
                  onPress={logout}
                />
              </View>
            </>
          )}

          <View style={styles.buttonContainer}>
            <Button 
              title="🔄 Check Backend" 
              onPress={checkBackend}
            />
          </View>

          {deliveries.length > 0 && (
            <View style={styles.deliveriesContainer}>
              <Text style={styles.deliveriesTitle}>Recent Deliveries:</Text>
              {deliveries.slice(0, 5).map((delivery) => (
                <View key={delivery.id} style={styles.deliveryItem}>
                  <Text style={styles.deliveryText}>
                    ID: {delivery.id} | {delivery.customer_name || 'Customer'}
                  </Text>
                  <Text style={styles.deliverySubtext}>
                    📍 {delivery.pickup_location} → {delivery.dropoff_location}
                  </Text>
                  <Text style={[
                    styles.deliveryStatus,
                    delivery.status === 'Completed' ? styles.statusCompleted : styles.statusPending
                  ]}>
                    Status: {delivery.status}
                  </Text>
                </View>
              ))}
            </View>
          )}

          <View style={styles.infoContainer}>
            <Text style={styles.infoTitle}>📱 Mobile App Features:</Text>
            <Text style={styles.infoText}>✅ Customer Registration</Text>
            <Text style={styles.infoText}>✅ Driver Registration</Text>
            <Text style={styles.infoText}>✅ User Authentication</Text>
            <Text style={styles.infoText}>✅ Delivery Requests</Text>
            <Text style={styles.infoText}>✅ Network Auto-Detection</Text>
            <Text style={styles.infoText}>✅ Enhanced Form Navigation</Text>
          </View>
        </View>
      </ScrollView>
    );
  }

  // Customer Registration Screen
  if (currentScreen === 'customer_register') {
    return (
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          ref={scrollViewRef}
          style={styles.container}
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            <Text style={styles.title}>📝 Customer Registration</Text>
            
            <View style={styles.formContainer}>
              <Text style={styles.label}>Username:</Text>
              <TextInput
                ref={customerFormRefs.username}
                style={styles.input}
                value={customerForm.username}
                onChangeText={(text) => setCustomerForm({...customerForm, username: text})}
                placeholder="Choose username"
                autoCapitalize="none"
                returnKeyType="next"
                onSubmitEditing={() => customerFormRefs.email.current?.focus()}
                onFocus={() => scrollToInput(customerFormRefs.username)}
              />

              <Text style={styles.label}>Email:</Text>
              <TextInput
                ref={customerFormRefs.email}
                style={styles.input}
                value={customerForm.email}
                onChangeText={(text) => setCustomerForm({...customerForm, email: text})}
                placeholder="your@email.com"
                keyboardType="email-address"
                autoCapitalize="none"
                returnKeyType="next"
                onSubmitEditing={() => customerFormRefs.password.current?.focus()}
                onFocus={() => scrollToInput(customerFormRefs.email)}
              />

              <Text style={styles.label}>Password:</Text>
              <TextInput
                ref={customerFormRefs.password}
                style={styles.input}
                value={customerForm.password}
                onChangeText={(text) => setCustomerForm({...customerForm, password: text})}
                placeholder="Choose password"
                secureTextEntry
                returnKeyType="next"
                onSubmitEditing={() => customerFormRefs.first_name.current?.focus()}
                onFocus={() => scrollToInput(customerFormRefs.password)}
              />

              <Text style={styles.label}>First Name:</Text>
              <TextInput
                ref={customerFormRefs.first_name}
                style={styles.input}
                value={customerForm.first_name}
                onChangeText={(text) => setCustomerForm({...customerForm, first_name: text})}
                placeholder="First name"
                returnKeyType="next"
                onSubmitEditing={() => customerFormRefs.last_name.current?.focus()}
                onFocus={() => scrollToInput(customerFormRefs.first_name)}
              />

              <Text style={styles.label}>Last Name:</Text>
              <TextInput
                ref={customerFormRefs.last_name}
                style={styles.input}
                value={customerForm.last_name}
                onChangeText={(text) => setCustomerForm({...customerForm, last_name: text})}
                placeholder="Last name"
                returnKeyType="next"
                onSubmitEditing={() => customerFormRefs.phone_number.current?.focus()}
                onFocus={() => scrollToInput(customerFormRefs.last_name)}
              />

              <Text style={styles.label}>Phone Number:</Text>
              <TextInput
                ref={customerFormRefs.phone_number}
                style={styles.input}
                value={customerForm.phone_number}
                onChangeText={(text) => setCustomerForm({...customerForm, phone_number: text})}
                placeholder="Phone number"
                keyboardType="phone-pad"
                returnKeyType="next"
                onSubmitEditing={() => customerFormRefs.address.current?.focus()}
                onFocus={() => scrollToInput(customerFormRefs.phone_number)}
              />

              <Text style={styles.label}>Address:</Text>
              <TextInput
                ref={customerFormRefs.address}
                style={[styles.input, styles.multilineInput]}
                value={customerForm.address}
                onChangeText={(text) => setCustomerForm({...customerForm, address: text})}
                placeholder="Your full address"
                multiline
                numberOfLines={3}
                returnKeyType="done"
                onFocus={() => scrollToInput(customerFormRefs.address)}
                onSubmitEditing={() => Keyboard.dismiss()}
              />

              <View style={styles.switchContainer}>
                <Text style={styles.label}>Business Customer:</Text>
                <Switch
                  value={customerForm.is_business}
                  onValueChange={(value) => setCustomerForm({...customerForm, is_business: value})}
                />
              </View>

              {customerForm.is_business && (
                <>
                  <Text style={styles.label}>Company Name:</Text>
                  <TextInput
                    ref={customerFormRefs.company_name}
                    style={styles.input}
                    value={customerForm.company_name}
                    onChangeText={(text) => setCustomerForm({...customerForm, company_name: text})}
                    placeholder="Company name"
                    returnKeyType="done"
                    onFocus={() => scrollToInput(customerFormRefs.company_name)}
                  />
                </>
              )}

              <View style={styles.buttonContainer}>
                <Button
                  title="Register Customer"
                  onPress={registerCustomer}
                  disabled={loading}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button
                  title="Back"
                  onPress={() => setCurrentScreen('main')}
                />
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Driver Registration Screen
  if (currentScreen === 'driver_register') {
    return (
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          ref={scrollViewRef}
          style={styles.container}
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            <Text style={styles.title}>🚚 Driver Registration</Text>
            
            <View style={styles.formContainer}>
              <Text style={styles.label}>Username:</Text>
              <TextInput
                ref={driverFormRefs.username}
                style={styles.input}
                value={driverForm.username}
                onChangeText={(text) => setDriverForm({...driverForm, username: text})}
                placeholder="Choose username"
                autoCapitalize="none"
                returnKeyType="next"
                onSubmitEditing={() => driverFormRefs.email.current?.focus()}
                onFocus={() => scrollToInput(driverFormRefs.username)}
              />

              <Text style={styles.label}>Email:</Text>
              <TextInput
                ref={driverFormRefs.email}
                style={styles.input}
                value={driverForm.email}
                onChangeText={(text) => setDriverForm({...driverForm, email: text})}
                placeholder="your@email.com"
                keyboardType="email-address"
                autoCapitalize="none"
                returnKeyType="next"
                onSubmitEditing={() => driverFormRefs.password.current?.focus()}
                onFocus={() => scrollToInput(driverFormRefs.email)}
              />

              <Text style={styles.label}>Password:</Text>
              <TextInput
                ref={driverFormRefs.password}
                style={styles.input}
                value={driverForm.password}
                onChangeText={(text) => setDriverForm({...driverForm, password: text})}
                placeholder="Choose password"
                secureTextEntry
                returnKeyType="next"
                onSubmitEditing={() => driverFormRefs.name.current?.focus()}
                onFocus={() => scrollToInput(driverFormRefs.password)}
              />

              <Text style={styles.label}>Full Name:</Text>
              <TextInput
                ref={driverFormRefs.name}
                style={styles.input}
                value={driverForm.name}
                onChangeText={(text) => setDriverForm({...driverForm, name: text})}
                placeholder="Your full name"
                returnKeyType="next"
                onSubmitEditing={() => driverFormRefs.phone_number.current?.focus()}
                onFocus={() => scrollToInput(driverFormRefs.name)}
              />

              <Text style={styles.label}>Phone Number:</Text>
              <TextInput
                ref={driverFormRefs.phone_number}
                style={styles.input}
                value={driverForm.phone_number}
                onChangeText={(text) => setDriverForm({...driverForm, phone_number: text})}
                placeholder="Phone number"
                keyboardType="phone-pad"
                returnKeyType="next"
                onSubmitEditing={() => driverFormRefs.license_number.current?.focus()}
                onFocus={() => scrollToInput(driverFormRefs.phone_number)}
              />

              <Text style={styles.label}>License Number:</Text>
              <TextInput
                ref={driverFormRefs.license_number}
                style={styles.input}
                value={driverForm.license_number}
                onChangeText={(text) => setDriverForm({...driverForm, license_number: text})}
                placeholder="Driver license number"
                returnKeyType="done"
                onFocus={() => scrollToInput(driverFormRefs.license_number)}
                onSubmitEditing={() => Keyboard.dismiss()}
              />

              <View style={styles.buttonContainer}>
                <Button
                  title="Register Driver"
                  onPress={registerDriver}
                  disabled={loading}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button
                  title="Back"
                  onPress={() => setCurrentScreen('main')}
                />
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Login Screen
  if (currentScreen === 'login') {
    return (
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          ref={scrollViewRef}
          style={styles.container}
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            <Text style={styles.title}>👤 Login</Text>
            
            <View style={styles.formContainer}>
              <Text style={styles.label}>Username:</Text>
              <TextInput
                style={styles.input}
                value={loginForm.username}
                onChangeText={(text) => setLoginForm({...loginForm, username: text})}
                placeholder="Enter username"
                autoCapitalize="none"
                returnKeyType="next"
              />

              <Text style={styles.label}>Password:</Text>
              <TextInput
                style={styles.input}
                value={loginForm.password}
                onChangeText={(text) => setLoginForm({...loginForm, password: text})}
                placeholder="Enter password"
                secureTextEntry
                returnKeyType="done"
                onSubmitEditing={login}
              />

              <View style={styles.buttonContainer}>
                <Button
                  title="Login"
                  onPress={login}
                  disabled={loading}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button
                  title="Back"
                  onPress={() => setCurrentScreen('main')}
                />
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  // Delivery Request Screen
  if (currentScreen === 'delivery_request') {
    return (
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          ref={scrollViewRef}
          style={styles.container}
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            <Text style={styles.title}>📦 Request Delivery</Text>
            
            <View style={styles.formContainer}>
              <Text style={styles.label}>Pickup Location:</Text>
              <TextInput
                style={[styles.input, styles.multilineInput]}
                value={deliveryForm.pickup_location}
                onChangeText={(text) => setDeliveryForm({...deliveryForm, pickup_location: text})}
                placeholder="Where to pick up from?"
                multiline
                numberOfLines={2}
                returnKeyType="next"
              />

              <Text style={styles.label}>Dropoff Location:</Text>
              <TextInput
                style={[styles.input, styles.multilineInput]}
                value={deliveryForm.dropoff_location}
                onChangeText={(text) => setDeliveryForm({...deliveryForm, dropoff_location: text})}
                placeholder="Where to deliver to?"
                multiline
                numberOfLines={2}
                returnKeyType="next"
              />

              <Text style={styles.label}>Item Description:</Text>
              <TextInput
                style={[styles.input, styles.multilineInput]}
                value={deliveryForm.item_description}
                onChangeText={(text) => setDeliveryForm({...deliveryForm, item_description: text})}
                placeholder="What are you sending?"
                multiline
                numberOfLines={3}
                returnKeyType="done"
                onSubmitEditing={() => Keyboard.dismiss()}
              />

              <View style={styles.switchContainer}>
                <Text style={styles.label}>Same pickup as customer address:</Text>
                <Switch
                  value={deliveryForm.same_pickup_as_customer}
                  onValueChange={(value) => setDeliveryForm({...deliveryForm, same_pickup_as_customer: value})}
                />
              </View>

              <View style={styles.switchContainer}>
                <Text style={styles.label}>Use preferred pickup location:</Text>
                <Switch
                  value={deliveryForm.use_preferred_pickup}
                  onValueChange={(value) => setDeliveryForm({...deliveryForm, use_preferred_pickup: value})}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button
                  title="Submit Delivery Request"
                  onPress={requestDelivery}
                  disabled={loading}
                />
              </View>

              <View style={styles.buttonContainer}>
                <Button
                  title="Back"
                  onPress={() => setCurrentScreen('main')}
                />
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    );
  }

  return null;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 50, // Extra padding for keyboard
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
    fontStyle: 'italic',
  },
  statusContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
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
  },
  success: {
    color: '#28a745',
  },
  error: {
    color: '#dc3545',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  buttonContainer: {
    marginVertical: 8,
  },
  userInfo: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#e7f3ff',
    borderRadius: 8,
    alignItems: 'center',
  },
  userInfoText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  formContainer: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 8,
    elevation: 2,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
    marginTop: 10,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
    marginBottom: 5,
  },
  multilineInput: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginVertical: 10,
    paddingHorizontal: 5,
  },
  deliveriesContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    elevation: 2,
  },
  deliveriesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  deliveryItem: {
    padding: 12,
    marginBottom: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  deliveryText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  deliverySubtext: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  deliveryStatus: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 5,
  },
  statusCompleted: {
    color: '#28a745',
  },
  statusPending: {
    color: '#ffc107',
  },
  infoContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#fff3cd',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#856404',
  },
  infoText: {
    fontSize: 14,
    color: '#856404',
    fontFamily: 'monospace',
  },
});