# 📋 DeliveryApp Quick Start Checklist

## 🚀 **Daily Development Startup**

### **Start Both Servers:**
```powershell
cd C:\Users\360WEB\DeliveryAppBackend
.\start-all-simple.ps1
```

### **Or Start Individually:**
```powershell
# Backend only:
.\start-backend-simple.ps1

# Mobile only (from DeliveryAppMobile directory):  
.\start-mobile-simple.ps1
```

### **Check System Status:**
```powershell
.\check-status.ps1
```

---

## 🧪 **Testing Checklist**

### **Customer Testing:**
- [ ] Register new customer (`POST /api/customers/register/`)
- [ ] Login with customer credentials (`POST /api/token/`)  
- [ ] Create delivery request (`POST /api/deliveries/request_delivery/`)
- [ ] View delivery history (`GET /api/customers/my_deliveries/`)

### **Driver Testing:**  
- [ ] Register new driver with full name (`POST /api/drivers/register/`)
- [ ] Test vehicle assignment during registration
- [ ] Verify driver-vehicle relationship created

### **Test Accounts Available:**
```
Username: sarah.williams.1, Password: testpass123
Username: john.jack, Password: testpass123 (real registration)
Username: chris.davis.5, Password: testpass123 (business)
```

---

## 🔧 **Key API Endpoints**

### **Customer Endpoints:**
```
POST /api/customers/register/     # Registration (no auth)
GET  /api/customers/me/          # Current customer profile
GET  /api/customers/my_deliveries/ # Customer's delivery history
```

### **Authentication:**
```
POST /api/token/                 # Login (get JWT tokens)
POST /api/token/refresh/         # Refresh access token
```

### **Delivery Endpoints:**
```
POST /api/deliveries/request_delivery/ # Create delivery (customer)
GET  /api/deliveries/            # View deliveries (filtered by user)
```

### **Driver Endpoints:**
```
POST /api/drivers/register/      # Driver registration (no auth)  
GET  /api/drivers/              # List drivers
POST /api/drivers/{id}/assign_vehicle/ # Assign vehicle
```

---

## 🛠 **Quick Fixes Reference**

### **Network Issues:**
- Check IP in settings: `ALLOWED_HOSTS = ['*']` for development
- Verify mobile app endpoint: `http://192.168.1.85:8081`
- Check Norton firewall: ports 8081, 19000, 19001

### **Database Issues:**
```powershell
# Reset test data:
python manage.py create_test_data --clear --customers 10 --drivers 10

# Check database contents:
.\verify-test-data.ps1
```

### **Driver Registration Issues:**
- ✅ **FIXED:** API now accepts `full_name` field  
- Mobile can send either `full_name` OR `first_name`+`last_name`
- Auto-splits: "Mike Johnson" → first:"Mike", last:"Johnson"

---

## 📱 **Mobile App Testing Steps**

### **1. Customer Flow:**
1. Open mobile app (scan QR code)
2. Register new customer with valid email
3. Login with new credentials  
4. Create delivery request
5. Check "same pickup as customer" checkbox
6. Submit and verify success

### **2. Driver Flow:**
1. Navigate to driver registration  
2. Fill full name field (e.g., "Mike Smith")
3. Add phone, license number
4. Add vehicle details (plate, model, capacity)
5. Submit registration
6. Verify success (no more "first/last name" error)

---

## 🔍 **Troubleshooting**

### **Common Issues & Solutions:**

**"Network Error during registration"**
- ✅ Check Django server running on :8081
- ✅ Verify ALLOWED_HOSTS setting  
- ✅ Check mobile app endpoint URL

**"Username already exists"**  
- ✅ Use unique usernames for testing
- ✅ Check existing users in database

**"requires first and last name"**
- ✅ **FIXED!** Use updated API that accepts `full_name`

**Mobile app won't connect**
- ✅ Check Norton firewall settings
- ✅ Verify IP address (may change with DHCP)  
- ✅ Restart Expo server if needed

### **Quick Commands:**
```powershell
# Kill all processes and restart:
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue  
.\start-all-simple.ps1

# Check what's running:
Get-Process | Where-Object {$_.ProcessName -eq "python"}
Get-Process | Where-Object {$_.ProcessName -eq "node"}

# Database quick check:
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DeliveryAppBackend.settings')
django.setup()
from delivery.models import Customer, Driver
print(f'Customers: {Customer.objects.count()}, Drivers: {Driver.objects.count()}')
"
```

---

## ✅ **Success Indicators**

### **System is Working When:**
- [ ] Django server responds at `http://192.168.1.85:8081/api/`
- [ ] Expo shows QR code for mobile connection
- [ ] Mobile app loads and shows registration/login screens
- [ ] Customer registration completes successfully  
- [ ] Driver registration accepts full name without errors
- [ ] Database operations save data properly

### **Ready for Production When:**
- [ ] All test cases pass consistently
- [ ] Error handling works properly  
- [ ] Performance is acceptable (< 500ms API responses)
- [ ] Security settings reviewed (JWT, CORS, etc.)
- [ ] Documentation complete and up-to-date

---

*Last Updated: October 23, 2025*  
*Status: ✅ All systems operational*