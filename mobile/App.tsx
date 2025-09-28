import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Button, Alert, ScrollView, ActivityIndicator } from 'react-native';

interface DeliveryData {
  id: number;
  customer_name: string;
  pickup_location: string;
  dropoff_location: string;
  status: string;
}

export default function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [deliveries, setDeliveries] = useState<DeliveryData[]>([]);
  const [loading, setLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);

  const API_BASE = 'http://172.20.10.6:8081';

  const checkBackend = async () => {
    try {
      setLoading(true);
      console.log('Testing backend connection...');
      
      // Test the health check endpoint first
      const healthResponse = await fetch(`${API_BASE}/`);
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setBackendStatus(`✅ Backend Connected! ${healthData.message}`);
        return true;
      } else {
        setBackendStatus(`❌ Backend Error: ${healthResponse.status}`);
        return false;
      }
    } catch (error) {
      console.error('Connection error:', error);
      setBackendStatus(`❌ Connection Failed: ${error.message}`);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const authenticateUser = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'w3r3w0lf'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAuthToken(data.access);
        Alert.alert('Success!', 'Authentication successful!');
        return data.access;
      } else {
        Alert.alert('Login Failed', 'Invalid credentials');
        return null;
      }
    } catch (error) {
      Alert.alert('Error', `Authentication failed: ${error.message}`);
      return null;
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

      const response = await fetch(`${API_BASE}/api/deliveries/`, {
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
      } else {
        Alert.alert('Error', `Failed to load deliveries: ${response.status}`);
      }
    } catch (error) {
      Alert.alert('Error', `Failed to load deliveries: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testFullWorkflow = async () => {
    const isConnected = await checkBackend();
    if (isConnected) {
      const token = await authenticateUser();
      if (token) {
        await loadDeliveries(token);
      }
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>🚚 DeliveryApp Mobile</Text>
        <Text style={styles.subtitle}>Modern Expo SDK 51+ Compatible</Text>
        
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

        <View style={styles.buttonContainer}>
          <Button 
            title="🔄 Check Backend Connection" 
            onPress={checkBackend}
            disabled={loading}
          />
        </View>

        <View style={styles.buttonContainer}>
          <Button 
            title="🔐 Authenticate" 
            onPress={authenticateUser}
            disabled={loading}
          />
        </View>

        <View style={styles.buttonContainer}>
          <Button 
            title="📦 Load Deliveries" 
            onPress={() => loadDeliveries()}
            disabled={loading || !authToken}
          />
        </View>

        <View style={styles.buttonContainer}>
          <Button 
            title="🚀 Test Full Workflow" 
            onPress={testFullWorkflow}
            disabled={loading}
          />
        </View>

        {authToken && (
          <View style={styles.tokenContainer}>
            <Text style={styles.tokenLabel}>🔑 Authenticated</Text>
            <Text style={styles.tokenText}>Token: {authToken.substring(0, 20)}...</Text>
          </View>
        )}

        {deliveries.length > 0 && (
          <View style={styles.deliveriesContainer}>
            <Text style={styles.deliveriesTitle}>📋 Deliveries ({deliveries.length})</Text>
            {deliveries.slice(0, 5).map((delivery) => (
              <View key={delivery.id} style={styles.deliveryItem}>
                <Text style={styles.deliveryText}>
                  #{delivery.id} - {delivery.customer_name}
                </Text>
                <Text style={styles.deliverySubtext}>
                  From: {delivery.pickup_location}
                </Text>
                <Text style={styles.deliverySubtext}>
                  To: {delivery.dropoff_location}
                </Text>
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
          <Text style={styles.infoText}>Network: Mobile Hotspot</Text>
          <Text style={styles.infoText}>SDK: Expo 51+ Compatible</Text>
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
  tokenContainer: {
    marginTop: 15,
    padding: 15,
    backgroundColor: '#e7f3ff',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  tokenLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  tokenText: {
    fontSize: 12,
    fontFamily: 'monospace',
    color: '#666',
    marginTop: 5,
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