// 🚚 DeliveryApp Mobile - Complete Feature Set
// Copy this content to C:\Users\360WEB\DeliveryAppMobile\App.tsx

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
  TouchableOpacity,
  Switch
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

  const checkBackend = async () => {
    try {
      setLoading(true);
      console.log('Testing backend connection...');
      setBackendStatus('🔍 Auto-detecting network...');
      
      for (const endpoint of NETWORK_ENDPOINTS) {
        try {
          console.log(`Trying ${endpoint.name}: ${endpoint.url}`);
          const healthResponse = await fetch(`${endpoint.url}/`);
          
          if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            setApiBase(endpoint.url);
            setCurrentNetwork(endpoint.name);
            setBackendStatus(`✅ Connected via ${endpoint.name}! ${healthData.message}`);
            return true;
          }
        } catch (networkError) {
          console.log(`${endpoint.name} failed:`, networkError);
          continue;
        }
      }
      
      setBackendStatus('❌ No networks available. Check WiFi/hotspot connection.');
      setCurrentNetwork('None Available');
      return false;
    } catch (error: any) {
      console.error('Connection error:', error);
      setBackendStatus(`❌ Connection Failed: ${error.message}`);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const authenticateUser = async (credentials?: { username: string; password: string }) => {
    try {
      setLoading(true);
      const creds = credentials || { username: 'admin', password: 'w3r3w0lf' };
      
      const response = await fetch(`${API_BASE}/api/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(creds)
      });

      if (response.ok) {
        const data = await response.json();
        setAuthToken(data.access);
        
        // Determine user type based on credentials
        if (creds.username === 'admin') {
          setUserType('admin');
        } else {
          setUserType('customer'); // Default for now
        }
        
        Alert.alert('Success!', 'Authentication successful!');
        setCurrentScreen('main');
        return data.access;
      } else {
        Alert.alert('Login Failed', 'Invalid credentials');
        return null;
      }
    } catch (error: any) {
      Alert.alert('Error', `Authentication failed: ${error.message}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const registerCustomer = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE}/api/customers/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', 'Customer registration successful! You can now login.');
        setCurrentScreen('login');
        // Reset form
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
        Alert.alert('Registration Failed', JSON.stringify(errorData));
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
      
      const response = await fetch(`${API_BASE}/api/drivers/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(driverForm)
      });

      if (response.ok) {
        const data = await response.json();
        Alert.alert('Success!', 'Driver registration successful! You can now login.');
        setCurrentScreen('login');
        // Reset form
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
    } catch (error: any) {
      Alert.alert('Error', `Registration failed: ${error.message}`);
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
        Alert.alert('Success!', 'Delivery request submitted successfully!');
        setCurrentScreen('main');
        // Reset form
        setDeliveryForm({
          pickup_location: '',
          dropoff_location: '',
          item_description: '',
          same_pickup_as_customer: false,
          use_preferred_pickup: false
        });
        // Reload deliveries
        loadDeliveries();
      } else {
        const errorData = await response.json();
        Alert.alert('Request Failed', JSON.stringify(errorData));
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

  // Main Screen
  if (currentScreen === 'main') {
    return (
      <ScrollView style={styles.container}>
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
                  onPress={() => authenticateUser()}
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
                  title="📦 View Deliveries" 
                  onPress={() => loadDeliveries()}
                />
              </View>

              {userType === 'customer' && (
                <View style={styles.buttonContainer}>
                  <Button 
                    title="📋 Request Delivery" 
                    onPress={() => setCurrentScreen('delivery_request')}
                  />
                </View>
              )}

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
              title="🔄 Check Connection" 
              onPress={checkBackend}
              disabled={loading}
            />
          </View>

          {deliveries.length > 0 && (
            <View style={styles.deliveriesContainer}>
              <Text style={styles.deliveriesTitle}>📋 Deliveries ({deliveries.length})</Text>
              {deliveries.slice(0, 5).map((delivery: DeliveryData) => (
                <View key={delivery.id} style={styles.deliveryItem}>
                  <Text style={styles.deliveryText}>
                    #{delivery.id} {delivery.customer_name ? `- ${delivery.customer_name}` : ''}
                  </Text>
                  <Text style={styles.deliverySubtext}>
                    From: {delivery.pickup_location}
                  </Text>
                  <Text style={styles.deliverySubtext}>
                    To: {delivery.dropoff_location}
                  </Text>
                  {delivery.item_description && (
                    <Text style={styles.deliverySubtext}>
                      Item: {delivery.item_description}
                    </Text>
                  )}
                  <Text style={[styles.deliveryStatus, 
                    delivery.status === 'Completed' ? styles.statusCompleted : styles.statusPending
                  ]}>
                    Status: {delivery.status}
                  </Text>
                </View>
              ))}
            </View>
          )}

          <View style={styles.infoContainer}>
            <Text style={styles.infoTitle}>📱 Connection Info</Text>
            <Text style={styles.infoText}>API URL: {API_BASE}</Text>
            <Text style={styles.infoText}>Network: {currentNetwork}</Text>
            <Text style={styles.infoText}>User Type: {userType || 'Not logged in'}</Text>
          </View>
        </View>
      </ScrollView>
    );
  }

  // Login Screen
  if (currentScreen === 'login') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🔐 Login</Text>
          
          <View style={styles.formContainer}>
            <Text style={styles.label}>Username:</Text>
            <TextInput
              style={styles.input}
              value={loginForm.username}
              onChangeText={(text) => setLoginForm({...loginForm, username: text})}
              placeholder="Enter username"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Password:</Text>
            <TextInput
              style={styles.input}
              value={loginForm.password}
              onChangeText={(text) => setLoginForm({...loginForm, password: text})}
              placeholder="Enter password"
              secureTextEntry
            />

            <View style={styles.buttonContainer}>
              <Button
                title="Login"
                onPress={() => authenticateUser(loginForm)}
                disabled={loading || !loginForm.username || !loginForm.password}
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
    );
  }

  // Customer Registration Screen
  if (currentScreen === 'customer_register') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>📝 Customer Registration</Text>
          
          <View style={styles.formContainer}>
            <Text style={styles.label}>Username:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.username}
              onChangeText={(text) => setCustomerForm({...customerForm, username: text})}
              placeholder="Choose username"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Email:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.email}
              onChangeText={(text) => setCustomerForm({...customerForm, email: text})}
              placeholder="your@email.com"
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Password:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.password}
              onChangeText={(text) => setCustomerForm({...customerForm, password: text})}
              placeholder="Choose password"
              secureTextEntry
            />

            <Text style={styles.label}>First Name:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.first_name}
              onChangeText={(text) => setCustomerForm({...customerForm, first_name: text})}
              placeholder="First name"
            />

            <Text style={styles.label}>Last Name:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.last_name}
              onChangeText={(text) => setCustomerForm({...customerForm, last_name: text})}
              placeholder="Last name"
            />

            <Text style={styles.label}>Phone Number:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.phone_number}
              onChangeText={(text) => setCustomerForm({...customerForm, phone_number: text})}
              placeholder="Phone number"
              keyboardType="phone-pad"
            />

            <Text style={styles.label}>Address:</Text>
            <TextInput
              style={styles.input}
              value={customerForm.address}
              onChangeText={(text) => setCustomerForm({...customerForm, address: text})}
              placeholder="Your address"
              multiline
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
                  style={styles.input}
                  value={customerForm.company_name}
                  onChangeText={(text) => setCustomerForm({...customerForm, company_name: text})}
                  placeholder="Company name"
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
    );
  }

  // Driver Registration Screen
  if (currentScreen === 'driver_register') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🚚 Driver Registration</Text>
          
          <View style={styles.formContainer}>
            <Text style={styles.label}>Username:</Text>
            <TextInput
              style={styles.input}
              value={driverForm.username}
              onChangeText={(text) => setDriverForm({...driverForm, username: text})}
              placeholder="Choose username"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Email:</Text>
            <TextInput
              style={styles.input}
              value={driverForm.email}
              onChangeText={(text) => setDriverForm({...driverForm, email: text})}
              placeholder="your@email.com"
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Password:</Text>
            <TextInput
              style={styles.input}
              value={driverForm.password}
              onChangeText={(text) => setDriverForm({...driverForm, password: text})}
              placeholder="Choose password"
              secureTextEntry
            />

            <Text style={styles.label}>Full Name:</Text>
            <TextInput
              style={styles.input}
              value={driverForm.name}
              onChangeText={(text) => setDriverForm({...driverForm, name: text})}
              placeholder="Full name"
            />

            <Text style={styles.label}>Phone Number:</Text>
            <TextInput
              style={styles.input}
              value={driverForm.phone_number}
              onChangeText={(text) => setDriverForm({...driverForm, phone_number: text})}
              placeholder="Phone number"
              keyboardType="phone-pad"
            />

            <Text style={styles.label}>License Number:</Text>
            <TextInput
              style={styles.input}
              value={driverForm.license_number}
              onChangeText={(text) => setDriverForm({...driverForm, license_number: text})}
              placeholder="Driver's license number"
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
    );
  }

  // Delivery Request Screen
  if (currentScreen === 'delivery_request') {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>📋 Request Delivery</Text>
          
          <View style={styles.formContainer}>
            <Text style={styles.label}>Pickup Location:</Text>
            <TextInput
              style={styles.input}
              value={deliveryForm.pickup_location}
              onChangeText={(text) => setDeliveryForm({...deliveryForm, pickup_location: text})}
              placeholder="Pickup address"
              multiline
            />

            <Text style={styles.label}>Dropoff Location:</Text>
            <TextInput
              style={styles.input}
              value={deliveryForm.dropoff_location}
              onChangeText={(text) => setDeliveryForm({...deliveryForm, dropoff_location: text})}
              placeholder="Delivery address"
              multiline
            />

            <Text style={styles.label}>Item Description:</Text>
            <TextInput
              style={styles.input}
              value={deliveryForm.item_description}
              onChangeText={(text) => setDeliveryForm({...deliveryForm, item_description: text})}
              placeholder="What needs to be delivered?"
              multiline
            />

            <View style={styles.switchContainer}>
              <Text style={styles.label}>Use my address as pickup:</Text>
              <Switch
                value={deliveryForm.same_pickup_as_customer}
                onValueChange={(value) => setDeliveryForm({...deliveryForm, same_pickup_as_customer: value})}
              />
            </View>

            <View style={styles.switchContainer}>
              <Text style={styles.label}>Use preferred pickup address:</Text>
              <Switch
                value={deliveryForm.use_preferred_pickup}
                onValueChange={(value) => setDeliveryForm({...deliveryForm, use_preferred_pickup: value})}
              />
            </View>

            <View style={styles.buttonContainer}>
              <Button
                title="Request Delivery"
                onPress={requestDelivery}
                disabled={loading || !deliveryForm.dropoff_location || !deliveryForm.item_description}
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
    );
  }

  return null;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
    paddingTop: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 5,
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  status: {
    fontSize: 14,
    fontWeight: '500',
  },
  success: {
    color: '#28a745',
  },
  error: {
    color: '#dc3545',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 15,
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
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginVertical: 10,
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