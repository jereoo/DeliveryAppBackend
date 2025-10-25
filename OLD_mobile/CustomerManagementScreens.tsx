// 🛠️ Customer Management CRUD Screens
// Complete CREATE, READ, UPDATE, DELETE operations for admin users

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
  FlatList,
  KeyboardAvoidingView,
  Platform
} from 'react-native';

// ========================================
// CUSTOMER CREATE SCREEN
// ========================================
export const CustomerCreateScreen = ({ 
  authToken, 
  API_BASE, 
  setCurrentScreen, 
  loadData,
  styles 
}) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: 'temppass123', // Default password
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    preferred_pickup_address: '',
    is_business: false,
    company_name: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) newErrors.username = 'Username is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
    if (!formData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    
    if (formData.is_business && !formData.company_name.trim()) {
      newErrors.company_name = 'Company name is required for business customers';
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const createCustomer = async () => {
    if (!validateForm()) {
      Alert.alert('Validation Error', 'Please fix the errors in the form');
      return;
    }

    setLoading(true);
    
    try {
      // First create the User account
      const userResponse = await fetch(`${API_BASE}/auth/users/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          first_name: formData.first_name,
          last_name: formData.last_name,
        }),
      });

      if (!userResponse.ok) {
        const errorData = await userResponse.json();
        throw new Error(`User creation failed: ${JSON.stringify(errorData)}`);
      }

      const userData = await userResponse.json();

      // Then create the Customer profile
      const customerResponse = await fetch(`${API_BASE}/customers/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user: userData.id,
          phone_number: formData.phone_number,
          address: formData.address,
          preferred_pickup_address: formData.preferred_pickup_address,
          is_business: formData.is_business,
          company_name: formData.company_name,
        }),
      });

      if (!customerResponse.ok) {
        const errorData = await customerResponse.json();
        throw new Error(`Customer creation failed: ${JSON.stringify(errorData)}`);
      }

      Alert.alert('Success', 'Customer created successfully!');
      await loadData(); // Refresh customer list
      setCurrentScreen('admin_customers');
      
    } catch (error) {
      console.error('Customer creation error:', error);
      Alert.alert('Error', `Failed to create customer: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.content}>
        <Text style={styles.title}>➕ Add New Customer</Text>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Username *</Text>
          <TextInput
            placeholder="Enter username"
            value={formData.username}
            onChangeText={(text) => setFormData({...formData, username: text.toLowerCase()})}
            style={[styles.input, errors.username && styles.inputError]}
            autoCapitalize="none"
          />
          {errors.username && <Text style={styles.errorText}>{errors.username}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Email *</Text>
          <TextInput
            placeholder="Enter email address"
            value={formData.email}
            onChangeText={(text) => setFormData({...formData, email: text.toLowerCase()})}
            style={[styles.input, errors.email && styles.inputError]}
            keyboardType="email-address"
            autoCapitalize="none"
          />
          {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>First Name *</Text>
          <TextInput
            placeholder="Enter first name"
            value={formData.first_name}
            onChangeText={(text) => setFormData({...formData, first_name: text})}
            style={[styles.input, errors.first_name && styles.inputError]}
          />
          {errors.first_name && <Text style={styles.errorText}>{errors.first_name}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Last Name *</Text>
          <TextInput
            placeholder="Enter last name"
            value={formData.last_name}
            onChangeText={(text) => setFormData({...formData, last_name: text})}
            style={[styles.input, errors.last_name && styles.inputError]}
          />
          {errors.last_name && <Text style={styles.errorText}>{errors.last_name}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Phone Number *</Text>
          <TextInput
            placeholder="Enter phone number"
            value={formData.phone_number}
            onChangeText={(text) => setFormData({...formData, phone_number: text})}
            style={[styles.input, errors.phone_number && styles.inputError]}
            keyboardType="phone-pad"
          />
          {errors.phone_number && <Text style={styles.errorText}>{errors.phone_number}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Address *</Text>
          <TextInput
            placeholder="Enter full address"
            value={formData.address}
            onChangeText={(text) => setFormData({...formData, address: text})}
            style={[styles.textArea, errors.address && styles.inputError]}
            multiline
            numberOfLines={3}
          />
          {errors.address && <Text style={styles.errorText}>{errors.address}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Preferred Pickup Address (Optional)</Text>
          <TextInput
            placeholder="Enter preferred pickup address"
            value={formData.preferred_pickup_address}
            onChangeText={(text) => setFormData({...formData, preferred_pickup_address: text})}
            style={styles.textArea}
            multiline
            numberOfLines={3}
          />
        </View>

        <View style={styles.switchContainer}>
          <Text style={styles.label}>Business Customer:</Text>
          <Switch
            value={formData.is_business}
            onValueChange={(value) => setFormData({...formData, is_business: value})}
          />
        </View>

        {formData.is_business && (
          <View style={styles.formGroup}>
            <Text style={styles.label}>Company Name *</Text>
            <TextInput
              placeholder="Enter company name"
              value={formData.company_name}
              onChangeText={(text) => setFormData({...formData, company_name: text})}
              style={[styles.input, errors.company_name && styles.inputError]}
            />
            {errors.company_name && <Text style={styles.errorText}>{errors.company_name}</Text>}
          </View>
        )}

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={[styles.primaryButton, loading && styles.buttonDisabled]} 
            onPress={createCustomer}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <Text style={styles.buttonText}>Create Customer</Text>
            )}
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={() => setCurrentScreen('admin_customers')}
            disabled={loading}
          >
            <Text style={styles.secondaryButtonText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

// ========================================
// CUSTOMER EDIT SCREEN
// ========================================
export const CustomerEditScreen = ({ 
  customerId, 
  authToken, 
  API_BASE, 
  setCurrentScreen, 
  loadData,
  styles 
}) => {
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadCustomer();
  }, []);

  const loadCustomer = async () => {
    try {
      const response = await fetch(`${API_BASE}/customers/${customerId}/`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load customer');
      }
      
      const customer = await response.json();
      setFormData({
        first_name: customer.user?.first_name || '',
        last_name: customer.user?.last_name || '',
        email: customer.user?.email || '',
        phone_number: customer.phone_number || '',
        address: customer.address || '',
        preferred_pickup_address: customer.preferred_pickup_address || '',
        is_business: customer.is_business || false,
        company_name: customer.company_name || '',
      });
      setLoading(false);
    } catch (error) {
      console.error('Load customer error:', error);
      Alert.alert('Error', 'Failed to load customer details');
      setCurrentScreen('admin_customers');
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.first_name?.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name?.trim()) newErrors.last_name = 'Last name is required';
    if (!formData.email?.trim()) newErrors.email = 'Email is required';
    if (!formData.phone_number?.trim()) newErrors.phone_number = 'Phone number is required';
    if (!formData.address?.trim()) newErrors.address = 'Address is required';
    
    if (formData.is_business && !formData.company_name?.trim()) {
      newErrors.company_name = 'Company name is required for business customers';
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const updateCustomer = async () => {
    if (!validateForm()) {
      Alert.alert('Validation Error', 'Please fix the errors in the form');
      return;
    }

    setSaving(true);
    
    try {
      // Update customer profile
      const customerResponse = await fetch(`${API_BASE}/customers/${customerId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone_number: formData.phone_number,
          address: formData.address,
          preferred_pickup_address: formData.preferred_pickup_address,
          is_business: formData.is_business,
          company_name: formData.company_name,
        }),
      });

      if (!customerResponse.ok) {
        const errorData = await customerResponse.json();
        throw new Error(`Customer update failed: ${JSON.stringify(errorData)}`);
      }

      Alert.alert('Success', 'Customer updated successfully!');
      await loadData(); // Refresh customer list
      setCurrentScreen('admin_customers');
      
    } catch (error) {
      console.error('Customer update error:', error);
      Alert.alert('Error', `Failed to update customer: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading customer details...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.content}>
        <Text style={styles.title}>✏️ Edit Customer</Text>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>First Name *</Text>
          <TextInput
            placeholder="Enter first name"
            value={formData.first_name}
            onChangeText={(text) => setFormData({...formData, first_name: text})}
            style={[styles.input, errors.first_name && styles.inputError]}
          />
          {errors.first_name && <Text style={styles.errorText}>{errors.first_name}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Last Name *</Text>
          <TextInput
            placeholder="Enter last name"
            value={formData.last_name}
            onChangeText={(text) => setFormData({...formData, last_name: text})}
            style={[styles.input, errors.last_name && styles.inputError]}
          />
          {errors.last_name && <Text style={styles.errorText}>{errors.last_name}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Email * (Read Only)</Text>
          <TextInput
            value={formData.email}
            style={[styles.input, styles.readOnlyInput]}
            editable={false}
          />
          <Text style={styles.helpText}>Email cannot be changed after creation</Text>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Phone Number *</Text>
          <TextInput
            placeholder="Enter phone number"
            value={formData.phone_number}
            onChangeText={(text) => setFormData({...formData, phone_number: text})}
            style={[styles.input, errors.phone_number && styles.inputError]}
            keyboardType="phone-pad"
          />
          {errors.phone_number && <Text style={styles.errorText}>{errors.phone_number}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Address *</Text>
          <TextInput
            placeholder="Enter full address"
            value={formData.address}
            onChangeText={(text) => setFormData({...formData, address: text})}
            style={[styles.textArea, errors.address && styles.inputError]}
            multiline
            numberOfLines={3}
          />
          {errors.address && <Text style={styles.errorText}>{errors.address}</Text>}
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Preferred Pickup Address (Optional)</Text>
          <TextInput
            placeholder="Enter preferred pickup address"
            value={formData.preferred_pickup_address}
            onChangeText={(text) => setFormData({...formData, preferred_pickup_address: text})}
            style={styles.textArea}
            multiline
            numberOfLines={3}
          />
        </View>

        <View style={styles.switchContainer}>
          <Text style={styles.label}>Business Customer:</Text>
          <Switch
            value={formData.is_business}
            onValueChange={(value) => setFormData({...formData, is_business: value})}
          />
        </View>

        {formData.is_business && (
          <View style={styles.formGroup}>
            <Text style={styles.label}>Company Name *</Text>
            <TextInput
              placeholder="Enter company name"
              value={formData.company_name}
              onChangeText={(text) => setFormData({...formData, company_name: text})}
              style={[styles.input, errors.company_name && styles.inputError]}
            />
            {errors.company_name && <Text style={styles.errorText}>{errors.company_name}</Text>}
          </View>
        )}

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={[styles.primaryButton, saving && styles.buttonDisabled]} 
            onPress={updateCustomer}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <Text style={styles.buttonText}>Update Customer</Text>
            )}
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={() => setCurrentScreen('admin_customers')}
            disabled={saving}
          >
            <Text style={styles.secondaryButtonText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

// ========================================
// CUSTOMER DELETE SCREEN
// ========================================
export const CustomerDeleteScreen = ({ 
  customerId, 
  customerName, 
  authToken, 
  API_BASE, 
  setCurrentScreen, 
  loadData,
  styles 
}) => {
  const [deleting, setDeleting] = useState(false);

  const deleteCustomer = async () => {
    Alert.alert(
      'Confirm Delete',
      `Are you sure you want to delete customer "${customerName}"?\n\nThis action cannot be undone and will remove all associated data.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: performDelete,
        },
      ]
    );
  };

  const performDelete = async () => {
    setDeleting(true);
    
    try {
      const response = await fetch(`${API_BASE}/customers/${customerId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      if (response.ok) {
        Alert.alert('Success', 'Customer deleted successfully');
        await loadData(); // Refresh customer list
        setCurrentScreen('admin_customers');
      } else {
        const errorData = await response.json();
        throw new Error(`Delete failed: ${JSON.stringify(errorData)}`);
      }
    } catch (error) {
      console.error('Customer deletion error:', error);
      Alert.alert('Error', `Failed to delete customer: ${error.message}`);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>🗑️ Delete Customer</Text>
        
        <View style={styles.warningContainer}>
          <Text style={styles.warningIcon}>⚠️</Text>
          <Text style={styles.warningTitle}>Warning</Text>
          <Text style={styles.warningText}>
            You are about to permanently delete customer "{customerName}".
          </Text>
          <Text style={styles.warningText}>
            This will also remove:
          </Text>
          <Text style={styles.warningBullet}>• All delivery history</Text>
          <Text style={styles.warningBullet}>• Customer profile data</Text>
          <Text style={styles.warningBullet}>• User account information</Text>
          <Text style={styles.warningText}>
            This action cannot be undone.
          </Text>
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={[styles.dangerButton, deleting && styles.buttonDisabled]} 
            onPress={deleteCustomer}
            disabled={deleting}
          >
            {deleting ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <Text style={styles.buttonText}>Delete Customer</Text>
            )}
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={() => setCurrentScreen('admin_customers')}
            disabled={deleting}
          >
            <Text style={styles.secondaryButtonText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

// ========================================
// CUSTOMER DETAIL SCREEN
// ========================================
export const CustomerDetailScreen = ({ 
  customerId, 
  authToken, 
  API_BASE, 
  setCurrentScreen, 
  styles 
}) => {
  const [customer, setCustomer] = useState(null);
  const [customerDeliveries, setCustomerDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomerDetails();
  }, []);

  const loadCustomerDetails = async () => {
    try {
      // Load customer details
      const customerResponse = await fetch(`${API_BASE}/customers/${customerId}/`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
      });
      
      if (!customerResponse.ok) {
        throw new Error('Failed to load customer details');
      }
      
      const customerData = await customerResponse.json();
      setCustomer(customerData);

      // Load customer's deliveries
      const deliveriesResponse = await fetch(
        `${API_BASE}/deliveries/?customer=${customerId}`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
        }
      );
      
      if (deliveriesResponse.ok) {
        const deliveriesData = await deliveriesResponse.json();
        setCustomerDeliveries(deliveriesData.results || []);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Load customer details error:', error);
      Alert.alert('Error', 'Failed to load customer details');
      setCurrentScreen('admin_customers');
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading customer details...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>👤 Customer Details</Text>
        
        <View style={styles.detailCard}>
          <Text style={styles.detailCardTitle}>Personal Information</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Name:</Text>
            <Text style={styles.detailValue}>
              {customer.user?.first_name} {customer.user?.last_name}
            </Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Email:</Text>
            <Text style={styles.detailValue}>{customer.user?.email}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Phone:</Text>
            <Text style={styles.detailValue}>{customer.phone_number}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Customer Type:</Text>
            <Text style={styles.detailValue}>
              {customer.is_business ? '🏢 Business' : '👤 Individual'}
            </Text>
          </View>
          
          {customer.is_business && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Company:</Text>
              <Text style={styles.detailValue}>{customer.company_name}</Text>
            </View>
          )}
        </View>

        <View style={styles.detailCard}>
          <Text style={styles.detailCardTitle}>Address Information</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Primary Address:</Text>
            <Text style={styles.detailValue}>{customer.address}</Text>
          </View>
          
          {customer.preferred_pickup_address && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Preferred Pickup:</Text>
              <Text style={styles.detailValue}>{customer.preferred_pickup_address}</Text>
            </View>
          )}
        </View>

        <View style={styles.detailCard}>
          <Text style={styles.detailCardTitle}>
            Delivery History ({customerDeliveries.length})
          </Text>
          
          {customerDeliveries.length === 0 ? (
            <Text style={styles.emptyText}>No deliveries found</Text>
          ) : (
            customerDeliveries.map((delivery) => (
              <View key={delivery.id} style={styles.deliveryItem}>
                <Text style={styles.deliveryTitle}>📦 Delivery #{delivery.id}</Text>
                <Text style={styles.deliveryDetail}>From: {delivery.pickup_location}</Text>
                <Text style={styles.deliveryDetail}>To: {delivery.dropoff_location}</Text>
                <Text style={styles.deliveryDetail}>Status: {delivery.status}</Text>
                <Text style={styles.deliveryDetail}>
                  Created: {new Date(delivery.created_at).toLocaleDateString()}
                </Text>
                {delivery.item_description && (
                  <Text style={styles.deliveryDetail}>Items: {delivery.item_description}</Text>
                )}
              </View>
            ))
          )}
        </View>
        
        <View style={styles.actionButtonsContainer}>
          <TouchableOpacity 
            style={styles.primaryButton}
            onPress={() => setCurrentScreen(`customer_edit_${customerId}`)} 
          >
            <Text style={styles.buttonText}>✏️ Edit Customer</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.dangerButton}
            onPress={() => setCurrentScreen(`customer_delete_${customerId}`)} 
          >
            <Text style={styles.buttonText}>🗑️ Delete Customer</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.secondaryButton}
            onPress={() => setCurrentScreen('admin_customers')} 
          >
            <Text style={styles.secondaryButtonText}>← Back to List</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};