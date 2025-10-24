# 🛠️ Stage 1 CRUD Implementation Plan

## Immediate Action: Complete Mobile CRUD Operations

### **Phase 1: Admin Customer Management (START HERE)**

#### **1. Customer CRUD Screens**
```tsx
// File: CustomerManagementScreens.tsx
// Location: OLD_mobile/components/admin/

// CREATE: Add New Customer
const CustomerCreateScreen = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    preferred_pickup_address: '',
    is_business: false,
    company_name: ''
  });

  const createCustomer = async () => {
    try {
      const response = await fetch(`${API_BASE}/customers/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      // Handle success/error
    } catch (error) {
      Alert.alert('Error', 'Failed to create customer');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Add New Customer</Text>
      
      <TextInput
        placeholder="Username"
        value={formData.username}
        onChangeText={(text) => setFormData({...formData, username: text})}
        style={styles.input}
      />
      
      <TextInput
        placeholder="Email"
        value={formData.email}
        onChangeText={(text) => setFormData({...formData, email: text})}
        style={styles.input}
      />
      
      <TextInput
        placeholder="First Name"
        value={formData.first_name}
        onChangeText={(text) => setFormData({...formData, first_name: text})}
        style={styles.input}
      />
      
      <TextInput
        placeholder="Last Name"
        value={formData.last_name}
        onChangeText={(text) => setFormData({...formData, last_name: text})}
        style={styles.input}
      />
      
      <TextInput
        placeholder="Phone Number"
        value={formData.phone_number}
        onChangeText={(text) => setFormData({...formData, phone_number: text})}
        style={styles.input}
      />
      
      <TextInput
        placeholder="Address"
        value={formData.address}
        onChangeText={(text) => setFormData({...formData, address: text})}
        style={styles.input}
        multiline
      />
      
      <View style={styles.switchContainer}>
        <Text>Business Customer:</Text>
        <Switch
          value={formData.is_business}
          onValueChange={(value) => setFormData({...formData, is_business: value})}
        />
      </View>
      
      {formData.is_business && (
        <TextInput
          placeholder="Company Name"
          value={formData.company_name}
          onChangeText={(text) => setFormData({...formData, company_name: text})}
          style={styles.input}
        />
      )}
      
      <View style={styles.buttonContainer}>
        <Button title="Create Customer" onPress={createCustomer} />
        <Button title="Cancel" onPress={() => setCurrentScreen('admin_customers')} color="red" />
      </View>
    </ScrollView>
  );
};

// UPDATE: Edit Existing Customer
const CustomerEditScreen = ({ customerId }) => {
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);

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
      const customer = await response.json();
      setFormData(customer);
      setLoading(false);
    } catch (error) {
      Alert.alert('Error', 'Failed to load customer');
    }
  };

  const updateCustomer = async () => {
    try {
      const response = await fetch(`${API_BASE}/customers/${customerId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        Alert.alert('Success', 'Customer updated successfully');
        setCurrentScreen('admin_customers');
      } else {
        Alert.alert('Error', 'Failed to update customer');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to update customer');
    }
  };

  if (loading) {
    return <ActivityIndicator size="large" style={styles.loading} />;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Edit Customer</Text>
      
      {/* Same form fields as create, but pre-populated */}
      <TextInput
        placeholder="First Name"
        value={formData.first_name}
        onChangeText={(text) => setFormData({...formData, first_name: text})}
        style={styles.input}
      />
      
      {/* ... other fields ... */}
      
      <View style={styles.buttonContainer}>
        <Button title="Update Customer" onPress={updateCustomer} />
        <Button title="Cancel" onPress={() => setCurrentScreen('admin_customers')} color="red" />
      </View>
    </ScrollView>
  );
};

// DELETE: Remove Customer
const CustomerDeleteScreen = ({ customerId, customerName }) => {
  const deleteCustomer = async () => {
    Alert.alert(
      'Confirm Delete',
      `Are you sure you want to delete customer "${customerName}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetch(`${API_BASE}/customers/${customerId}/`, {
                method: 'DELETE',
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
              
              if (response.ok) {
                Alert.alert('Success', 'Customer deleted successfully');
                setCurrentScreen('admin_customers');
                loadData(); // Refresh customer list
              } else {
                Alert.alert('Error', 'Failed to delete customer');
              }
            } catch (error) {
              Alert.alert('Error', 'Failed to delete customer');
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Delete Customer</Text>
      <Text style={styles.warningText}>
        This will permanently delete the customer and all associated data.
      </Text>
      
      <View style={styles.buttonContainer}>
        <Button title="Delete Customer" onPress={deleteCustomer} color="red" />
        <Button title="Cancel" onPress={() => setCurrentScreen('admin_customers')} />
      </View>
    </View>
  );
};

// ENHANCED READ: Customer Detail View
const CustomerDetailScreen = ({ customerId }) => {
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
      const customerData = await customerResponse.json();
      setCustomer(customerData);

      // Load customer's deliveries
      const deliveriesResponse = await fetch(
        `${API_BASE}/deliveries/?customer=${customerId}`,
        {
          headers: { 'Authorization': `Bearer ${authToken}` },
        }
      );
      const deliveriesData = await deliveriesResponse.json();
      setCustomerDeliveries(deliveriesData.results || []);
      
      setLoading(false);
    } catch (error) {
      Alert.alert('Error', 'Failed to load customer details');
    }
  };

  if (loading) {
    return <ActivityIndicator size="large" style={styles.loading} />;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Customer Details</Text>
      
      <View style={styles.detailContainer}>
        <Text style={styles.detailLabel}>Name:</Text>
        <Text style={styles.detailValue}>
          {customer.user?.first_name} {customer.user?.last_name}
        </Text>
      </View>
      
      <View style={styles.detailContainer}>
        <Text style={styles.detailLabel}>Email:</Text>
        <Text style={styles.detailValue}>{customer.user?.email}</Text>
      </View>
      
      <View style={styles.detailContainer}>
        <Text style={styles.detailLabel}>Phone:</Text>
        <Text style={styles.detailValue}>{customer.phone_number}</Text>
      </View>
      
      <View style={styles.detailContainer}>
        <Text style={styles.detailLabel}>Address:</Text>
        <Text style={styles.detailValue}>{customer.address}</Text>
      </View>
      
      <View style={styles.detailContainer}>
        <Text style={styles.detailLabel}>Type:</Text>
        <Text style={styles.detailValue}>
          {customer.is_business ? 'Business' : 'Individual'}
        </Text>
      </View>
      
      {customer.is_business && (
        <View style={styles.detailContainer}>
          <Text style={styles.detailLabel}>Company:</Text>
          <Text style={styles.detailValue}>{customer.company_name}</Text>
        </View>
      )}
      
      <Text style={styles.sectionTitle}>Recent Deliveries ({customerDeliveries.length})</Text>
      
      {customerDeliveries.map((delivery) => (
        <View key={delivery.id} style={styles.deliveryItem}>
          <Text style={styles.deliveryTitle}>Delivery #{delivery.id}</Text>
          <Text>From: {delivery.pickup_location}</Text>
          <Text>To: {delivery.dropoff_location}</Text>
          <Text>Status: {delivery.status}</Text>
          <Text>Created: {new Date(delivery.created_at).toLocaleDateString()}</Text>
        </View>
      ))}
      
      <View style={styles.actionButtonsContainer}>
        <Button 
          title="Edit Customer" 
          onPress={() => setCurrentScreen(`customer_edit_${customerId}`)} 
        />
        <Button 
          title="Delete Customer" 
          onPress={() => setCurrentScreen(`customer_delete_${customerId}`)} 
          color="red" 
        />
        <Button 
          title="Back to List" 
          onPress={() => setCurrentScreen('admin_customers')} 
        />
      </View>
    </ScrollView>
  );
};

export {
  CustomerCreateScreen,
  CustomerEditScreen,
  CustomerDeleteScreen,
  CustomerDetailScreen
};
```

#### **2. Enhanced Customer List Screen**
```tsx
// Enhanced admin_customers screen with CRUD actions
const AdminCustomersScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>👥 Manage Customers</Text>
      
      <View style={styles.actionBar}>
        <Button 
          title="+ Add New Customer" 
          onPress={() => setCurrentScreen('customer_create')} 
        />
        <Button 
          title="🔄 Refresh" 
          onPress={loadData} 
        />
      </View>
      
      {customers.length === 0 ? (
        <Text style={styles.infoText}>No customers found</Text>
      ) : (
        <FlatList
          data={customers}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View style={styles.customerItem}>
              <TouchableOpacity 
                onPress={() => setCurrentScreen(`customer_detail_${item.id}`)}
                style={styles.customerInfo}
              >
                <Text style={styles.customerName}>
                  👤 {item.user?.first_name} {item.user?.last_name}
                </Text>
                <Text>Email: {item.user?.email}</Text>
                <Text>Phone: {item.phone_number}</Text>
                <Text>Type: {item.is_business ? 'Business' : 'Individual'}</Text>
              </TouchableOpacity>
              
              <View style={styles.customerActions}>
                <TouchableOpacity 
                  onPress={() => setCurrentScreen(`customer_edit_${item.id}`)}
                  style={styles.editButton}
                >
                  <Text style={styles.buttonText}>✏️ Edit</Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  onPress={() => setCurrentScreen(`customer_delete_${item.id}`)}
                  style={styles.deleteButton}
                >
                  <Text style={styles.buttonText}>🗑️ Delete</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}
          ListFooterComponent={() => (
            <View style={styles.buttonContainer}>
              <Button title="Back to Dashboard" onPress={() => setCurrentScreen('dashboard')} />
            </View>
          )}
        />
      )}
    </View>
  );
};
```

---

## **Implementation Strategy**

### **Step 1: Start with Customer CRUD (Most Critical)**
1. Create CustomerManagementScreens.tsx component file
2. Implement CREATE, UPDATE, DELETE, and detailed READ functionality
3. Add proper form validation and error handling
4. Test all CRUD operations thoroughly

### **Step 2: Replicate for Drivers**
1. Create DriverManagementScreens.tsx
2. Implement driver-specific fields (license, vehicle assignment)
3. Add driver status management

### **Step 3: Vehicle Management**
1. Create VehicleManagementScreens.tsx
2. Implement capacity, model, license plate management
3. Add vehicle assignment tracking

### **Step 4: Delivery Management**
1. Create DeliveryManagementScreens.tsx
2. Implement status updates, driver assignment
3. Add delivery tracking and management

### **Step 5: Integration & Testing**
1. Update main App.tsx with new screen routing
2. Test complete admin workflow
3. Add customer and driver self-management screens

---

**NEXT ACTION**: Implement Customer CRUD screens as the foundation for complete admin management functionality.