# 📱 Mobile CRUD Manual Testing Guide

**Status**: Ready for Physical Device Testing  
**Backend**: http://192.168.1.85:8081  
**Mobile App**: C:\Users\360WEB\DeliveryAppMobile  

## 🚀 **QUICK START - MANUAL TESTING**

### **Step 1: Start Backend Server**
```powershell
# Terminal 1: Start Backend
cd C:\Users\360WEB\DeliveryAppBackend
.\start-backend-simple.ps1
```
✅ **Expected**: Backend running at http://192.168.1.85:8081

### **Step 2: Start Mobile App**
```powershell
# Terminal 2: Start Mobile App
cd C:\Users\360WEB\DeliveryAppMobile
npx expo start
```
✅ **Expected**: QR code displayed for device scanning

### **Step 3: Connect Physical Device**
1. **Install Expo Go**: Download from App Store (iOS) or Google Play (Android)
2. **Scan QR Code**: Point phone camera at terminal QR code
3. **Open in Expo Go**: App should load automatically

---

## ✅ **MANUAL TESTING CHECKLIST**

### 🔗 **1. CONNECTIVITY TESTING**
- [ ] **App Loads**: Mobile app opens without crashes
- [ ] **Network Detection**: App shows "Current Network (Auto-detected)" as first option
- [ ] **Backend Connection**: App successfully connects to backend (192.168.1.85:8081)
- [ ] **Status Indicator**: Connection status shows "Connected" or similar positive indicator

**✅ Expected Behavior**: App automatically selects correct network endpoint and establishes connection

---

### 👤 **2. CUSTOMER REGISTRATION TESTING**

#### **Test Case 2.1: New Customer Registration**
- [ ] **Navigate to Registration**: Find and tap customer registration option
- [ ] **Fill Registration Form**:
  - Username: `manual_test_[your_name]`
  - Email: `[your_name]@test.com`
  - Password: `testpass123`
  - First Name: `[Your First Name]`
  - Last Name: `[Your Last Name]`
  - Phone: `+1234567890`
  - Address: `123 Test Street, Test City`
- [ ] **Submit Registration**: Tap submit/register button
- [ ] **Success Response**: Registration succeeds, customer ID received
- [ ] **Auto-redirect**: App redirects to login or main screen

**✅ Expected Behavior**: Registration creates account, returns customer ID, allows immediate login

#### **Test Case 2.2: Validation Testing**
- [ ] **Empty Fields**: Try submitting with empty required fields → should show validation errors
- [ ] **Invalid Email**: Try `invalid-email` → should show email format error
- [ ] **Short Password**: Try `123` → should show password length error
- [ ] **Duplicate Username**: Try existing username → should show "username exists" error

**✅ Expected Behavior**: Form validation prevents invalid submissions with clear error messages

---

### 🔐 **3. AUTHENTICATION TESTING**

#### **Test Case 3.1: Login with New Account**
- [ ] **Navigate to Login**: Find and tap login option
- [ ] **Enter Credentials**: Use username/password from registration
- [ ] **Submit Login**: Tap login button
- [ ] **Success Response**: Login succeeds, JWT token received
- [ ] **Access Granted**: App shows authenticated user interface

**✅ Expected Behavior**: Login works with newly created account, proper authentication state

#### **Test Case 3.2: Invalid Login Testing**
- [ ] **Wrong Password**: Try correct username + wrong password → should show error
- [ ] **Wrong Username**: Try non-existent username → should show error
- [ ] **Empty Fields**: Try submitting empty fields → should show validation

**✅ Expected Behavior**: Failed logins show appropriate error messages without crashing

---

### 📖 **4. CUSTOMER PROFILE READ TESTING**

#### **Test Case 4.1: View Own Profile**
- [ ] **Navigate to Profile**: Find "My Profile" or similar option
- [ ] **Profile Loads**: Your customer data displays correctly
- [ ] **Data Accuracy**: All fields match registration data:
  - ✅ Name: Should show your first/last name
  - ✅ Email: Should show your email address
  - ✅ Phone: Should show your phone number
  - ✅ Address: Should show your address
- [ ] **UI Formatting**: Data displays properly formatted and readable

**✅ Expected Behavior**: Profile shows your own data accurately with good formatting

---

### ✏️ **5. CUSTOMER PROFILE UPDATE TESTING**

#### **Test Case 5.1: Edit Profile Information**
- [ ] **Navigate to Edit**: Find "Edit Profile" button/option
- [ ] **Modify Fields**: Change some profile information:
  - Phone: `+9876543210`
  - Address: `456 Updated Avenue, New City`
- [ ] **Save Changes**: Tap save/update button
- [ ] **Success Confirmation**: App shows update success message
- [ ] **Immediate Reflection**: Changes appear immediately in profile view
- [ ] **Persistence**: Close and reopen profile → changes should persist

**✅ Expected Behavior**: Updates save correctly and persist across app sessions

#### **Test Case 5.2: Update Validation**
- [ ] **Invalid Phone**: Try invalid phone format → should show validation error
- [ ] **Empty Required Field**: Clear required field → should prevent save
- [ ] **Cancel Changes**: Make changes then cancel → should revert to original values

**✅ Expected Behavior**: Validation prevents invalid updates, cancel works properly

---

### 🗑️ **6. CUSTOMER ACCOUNT DELETE TESTING**

#### **Test Case 6.1: Account Deletion**
- [ ] **Navigate to Delete**: Find account deletion option (often in settings)
- [ ] **Confirmation Dialog**: App should show deletion confirmation
- [ ] **Confirm Deletion**: Proceed with account deletion
- [ ] **Success Response**: Deletion succeeds
- [ ] **Auto-logout**: App logs out and returns to welcome/login screen
- [ ] **Account Verification**: Try logging in with deleted account → should fail

**✅ Expected Behavior**: Account deletes successfully, immediate logout, login no longer works

#### **Test Case 6.2: Deletion Safety**
- [ ] **Cancel Option**: Deletion dialog should have cancel option
- [ ] **Cancel Works**: Canceling should NOT delete account
- [ ] **Clear Warning**: Warning message should clearly explain deletion is permanent

**✅ Expected Behavior**: Safe deletion with clear warnings and cancel option

---

### 🔄 **7. NAVIGATION & UX TESTING**

#### **Test Case 7.1: App Navigation**
- [ ] **Menu Structure**: Navigation is logical and intuitive
- [ ] **Back Buttons**: Back navigation works consistently
- [ ] **Screen Transitions**: Smooth transitions between screens
- [ ] **Loading States**: Loading indicators show during API calls
- [ ] **Error Handling**: Network errors display user-friendly messages

**✅ Expected Behavior**: Smooth, intuitive navigation with proper feedback

#### **Test Case 7.2: Mobile-Specific UX**
- [ ] **Touch Targets**: Buttons are easy to tap (not too small)
- [ ] **Keyboard Behavior**: Virtual keyboard doesn't cover form fields
- [ ] **Screen Orientation**: Works in both portrait and landscape (if supported)
- [ ] **Scrolling**: Smooth scrolling on forms and lists
- [ ] **Visual Design**: Readable text, good contrast, professional appearance

**✅ Expected Behavior**: Mobile-optimized interface that's easy to use on touchscreen

---

## 🚨 **COMMON ISSUES & TROUBLESHOOTING**

### **Connection Issues**
- **Problem**: "Network Error" or "Connection Failed"
- **Solution**: 
  1. Check backend is running: http://192.168.1.85:8081/admin/
  2. Verify phone and computer on same Wi-Fi network
  3. Try network refresh in mobile app

### **Registration Issues**
- **Problem**: "Registration Failed" 
- **Solution**:
  1. Try different username (must be unique)
  2. Check email format (must include @)
  3. Ensure password is 8+ characters

### **App Crashes**
- **Problem**: App closes unexpectedly
- **Solution**:
  1. Shake device → "Reload" to restart app
  2. Check Expo Go app is latest version
  3. Restart backend server if needed

### **QR Code Issues**
- **Problem**: QR code won't scan
- **Solution**:
  1. Ensure good lighting when scanning
  2. Try typing the URL manually in Expo Go
  3. Make sure Expo server is running (npx expo start)

---

## 📊 **TEST RESULTS TRACKING**

### **Record Your Results**:
```
📝 MANUAL TEST RESULTS:
====================
Date: [Date]
Device: [iOS/Android] 
App Version: [Expo version]

✅ PASSED TESTS:
- [ ] Connectivity
- [ ] Registration  
- [ ] Authentication
- [ ] Profile Read
- [ ] Profile Update
- [ ] Account Delete
- [ ] Navigation/UX

❌ FAILED TESTS:
- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]

📱 DEVICE-SPECIFIC NOTES:
- Performance: [Smooth/Lag]
- UI Appearance: [Good/Issues]
- Touch Response: [Responsive/Slow]

🔧 ISSUES FOUND:
1. [Describe any bugs or usability issues]
2. [Screenshots if helpful]
3. [Steps to reproduce problems]
```

---

## 🎯 **SUCCESS CRITERIA**

### **✅ PASS Criteria**: 
- All 6 main test categories (Connectivity, Registration, Auth, Read, Update, Delete) work correctly
- No app crashes during normal usage
- UI is usable and responsive on mobile device
- Data persists correctly between sessions

### **🚀 READY FOR NEXT PHASE**:
Once manual testing passes, we'll proceed with:
1. **Driver CRUD Screens**: Following same pattern as Customer CRUD
2. **Vehicle CRUD Screens**: Management interface for vehicles
3. **Delivery Request Interface**: Customer delivery functionality

---

## 💡 **TESTING TIPS**

1. **Take Screenshots**: Document any issues for debugging
2. **Test Edge Cases**: Try unusual inputs, rapid tapping, etc.
3. **Network Variations**: Test with strong/weak Wi-Fi, mobile data if available
4. **Multiple Accounts**: Create 2-3 test accounts to verify isolation
5. **Real Usage**: Use the app as a real customer would

**Remember**: We have 100% automated test success, so most issues (if any) will likely be UI/UX related rather than core functionality problems.

🎉 **You're ready to start manual testing! Good luck!** 🎉