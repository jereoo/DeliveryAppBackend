# 📱 DeliveryApp with Expo - Quick Setup Guide

## 🎯 **Perfect! Expo Makes This Super Easy**

Since you have Expo on your phone, you can quickly create a React Native app that connects to your DeliveryApp backend.

## 🚀 **Quick Start with Expo**

### **Step 1: Create Expo Project**
```bash
# In a new directory (not in your current project)
npx create-expo-app DeliveryAppMobile
cd DeliveryAppMobile
```

### **Step 2: Install Required Dependencies**
```bash
npm install axios @react-navigation/native @react-navigation/stack
npx expo install react-native-screens react-native-safe-area-context
```

### **Step 3: Configure API Connection**
Create `config/api.js`:
```javascript
// config/api.js
export const API_CONFIG = {
  // Your computer's IP on the same network
  BASE_URL: 'http://192.168.1.79:8081',
  ENDPOINTS: {
    LOGIN: '/api/token/',
    REGISTER: '/api/customers/register/',
    DELIVERIES: '/api/deliveries/',
    REQUEST_DELIVERY: '/api/deliveries/request_delivery/',
    CUSTOMERS: '/api/customers/',
  }
};
```

## 📱 **Sample Expo App Components**

### **API Service (services/api.js)**
```javascript
import axios from 'axios';
import { API_CONFIG } from '../config/api';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.token = null;
  }

  setAuthToken(token) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  async login(username, password) {
    try {
      const response = await this.client.post(API_CONFIG.ENDPOINTS.LOGIN, {
        username,
        password,
      });
      
      if (response.data.access) {
        this.setAuthToken(response.data.access);
        return {
          success: true,
          token: response.data.access,
          refreshToken: response.data.refresh,
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  }

  async registerCustomer(customerData) {
    try {
      const response = await this.client.post(API_CONFIG.ENDPOINTS.REGISTER, customerData);
      return {
        success: true,
        customer: response.data,
      };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        error: error.response?.data || 'Registration failed',
      };
    }
  }

  async getDeliveries() {
    try {
      const response = await this.client.get(API_CONFIG.ENDPOINTS.DELIVERIES);
      return {
        success: true,
        deliveries: response.data.results || response.data,
      };
    } catch (error) {
      console.error('Get deliveries error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch deliveries',
      };
    }
  }

  async requestDelivery(deliveryData) {
    try {
      const response = await this.client.post(API_CONFIG.ENDPOINTS.REQUEST_DELIVERY, deliveryData);
      return {
        success: true,
        delivery: response.data,
      };
    } catch (error) {
      console.error('Request delivery error:', error);
      return {
        success: false,
        error: error.response?.data || 'Failed to request delivery',
      };
    }
  }
}

export default new ApiService();
```

### **Login Screen (screens/LoginScreen.js)**
```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import ApiService from '../services/api';

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    const result = await ApiService.login(username, password);
    setLoading(false);

    if (result.success) {
      Alert.alert('Success', 'Login successful!');
      navigation.navigate('Dashboard');
    } else {
      Alert.alert('Login Failed', result.error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>DeliveryApp Login</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={handleLogin}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? 'Logging in...' : 'Login'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.linkButton}
        onPress={() => navigation.navigate('Register')}
      >
        <Text style={styles.linkText}>Don't have an account? Register</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
  },
  input: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkButton: {
    marginTop: 15,
  },
  linkText: {
    color: '#007AFF',
    textAlign: 'center',
  },
});
```

### **Customer Registration Screen (screens/RegisterScreen.js)**
```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  Switch,
} from 'react-native';
import ApiService from '../services/api';

export default function RegisterScreen({ navigation }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    is_business: false,
    company_name: '',
  });
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    // Basic validation
    if (!formData.username || !formData.email || !formData.password) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    setLoading(true);
    const result = await ApiService.registerCustomer(formData);
    setLoading(false);

    if (result.success) {
      Alert.alert(
        'Success', 
        'Registration successful! You can now login.',
        [{ text: 'OK', onPress: () => navigation.navigate('Login') }]
      );
    } else {
      Alert.alert('Registration Failed', JSON.stringify(result.error));
    }
  };

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Register Customer</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Username *"
        value={formData.username}
        onChangeText={(value) => updateField('username', value)}
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Email *"
        value={formData.email}
        onChangeText={(value) => updateField('email', value)}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Password *"
        value={formData.password}
        onChangeText={(value) => updateField('password', value)}
        secureTextEntry
      />
      
      <TextInput
        style={styles.input}
        placeholder="First Name"
        value={formData.first_name}
        onChangeText={(value) => updateField('first_name', value)}
      />
      
      <TextInput
        style={styles.input}
        placeholder="Last Name"
        value={formData.last_name}
        onChangeText={(value) => updateField('last_name', value)}
      />
      
      <TextInput
        style={styles.input}
        placeholder="Phone Number"
        value={formData.phone_number}
        onChangeText={(value) => updateField('phone_number', value)}
        keyboardType="phone-pad"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Address"
        value={formData.address}
        onChangeText={(value) => updateField('address', value)}
        multiline
      />
      
      <View style={styles.switchContainer}>
        <Text style={styles.switchLabel}>Business Customer</Text>
        <Switch
          value={formData.is_business}
          onValueChange={(value) => updateField('is_business', value)}
        />
      </View>
      
      {formData.is_business && (
        <TextInput
          style={styles.input}
          placeholder="Company Name"
          value={formData.company_name}
          onChangeText={(value) => updateField('company_name', value)}
        />
      )}
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={handleRegister}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? 'Registering...' : 'Register'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.linkButton}
        onPress={() => navigation.navigate('Login')}
      >
        <Text style={styles.linkText}>Already have an account? Login</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
  },
  input: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  switchLabel: {
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkButton: {
    marginTop: 15,
    marginBottom: 30,
  },
  linkText: {
    color: '#007AFF',
    textAlign: 'center',
  },
});
```

## 🚀 **How to Use with Expo**

### **Step 1: Make sure your Django server is running**
```bash
# On your computer
python network_config.py phone
python manage.py runserver 0.0.0.0:8081
```

### **Step 2: Create the Expo app**
```bash
npx create-expo-app DeliveryAppMobile
cd DeliveryAppMobile
# Copy the code above into the appropriate files
```

### **Step 3: Update the IP address**
In `config/api.js`, make sure the IP matches your computer:
```javascript
BASE_URL: 'http://192.168.1.79:8081',  // Your computer's IP
```

### **Step 4: Run with Expo**
```bash
npx expo start
```

### **Step 5: Scan QR code with Expo app on your phone**
- Open Expo app on your phone
- Scan the QR code shown in terminal
- Your React Native app will load!

## 🎯 **Test Credentials**
Use these to test the login:
- **Username**: `admin`
- **Password**: `w3r3w0lf`

## ✨ **What You'll Have**
- ✅ Native mobile app running on your phone
- ✅ Real-time connection to your Django backend
- ✅ Customer registration and login
- ✅ Delivery request functionality
- ✅ Live reload during development

Your backend is **already configured** for this - just create the Expo app and start coding! 📱🚀