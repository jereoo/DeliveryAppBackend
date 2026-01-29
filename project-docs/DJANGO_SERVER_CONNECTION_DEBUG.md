# Django Server Connection Issues - Debug Log

**Date:** November 8, 2025  
**Issues:** 
1. Django server starting but immediately exiting when accessed by mobile app
2. Mobile app unable to connect to Django backend  
**Status:** ✅ **BOTH RESOLVED**  
**Total Debug Time:** 2 hours

## Problem 1: Django Server Exit on First Request

### Symptoms
- Django server starts successfully with message: `Starting development server at http://0.0.0.0:8081/`
- Server immediately exits (code 1) when any HTTP request is made to it
- Mobile app logs show `Network request failed` errors
- API test scripts fail with connection refused errors
- No error messages in Django server output before exit

### Mobile App Error Logs (Initial)
```
LOG  Testing endpoint: http://localhost:8081/api/
LOG  Failed to connect to Auto-detected: [TypeError: Network request failed]
LOG  Testing endpoint: http://192.168.1.77:8081/api/
LOG  Attempting login to: http://192.168.1.69:8081/api/token/
ERROR Login network error: [TypeError: Network request failed]
```

### Django Server Behavior
```
PS C:\Users\360WEB\DeliveryAppBackend> python manage.py runserver 0.0.0.0:8081
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
November 08, 2025 - 18:51:39
Django version 5.2.5, using settings 'DeliveryAppBackend.settings'
Starting development server at http://0.0.0.0:8081/
Quit the server with CTRL-BREAK.
Command exited with code 1  # ← Server exits immediately when accessed
```

## Root Cause Analysis

### Primary Issue: Missing CORS Configuration
1. **django-cors-headers not installed in virtual environment**
   - Package was installed globally but not in the project's venv
   - Django couldn't import `corsheaders` module
   - Server silently failed on first request due to missing middleware

2. **CORS middleware disabled in settings**
   - `corsheaders` was commented out in `INSTALLED_APPS`
   - `CorsMiddleware` was commented out in `MIDDLEWARE`
   - No CORS headers sent to mobile app requests

3. **Incorrect admin credentials in test scripts**
   - Test scripts used password `"w3r3w0lf"`
   - Admin user was created with password `"admin123"`
   - Authentication failed before CORS issue could be identified

## Resolution Steps

### 1. Install django-cors-headers in Virtual Environment
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install CORS package
pip install django-cors-headers
```

### 2. Enable CORS in Django Settings
```python
# In DeliveryAppBackend/settings.py
INSTALLED_APPS = [
    # ...existing apps...
    'corsheaders',  # Re-enabled for mobile app
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Re-enabled for mobile app
    # ...existing middleware...
]

# CORS settings for mobile app
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://192.168.1.69:8081",
    "http://192.168.1.77:8081",
    "http://192.168.1.68:19000",  # Expo dev server
    # ...other origins...
]
```

### 3. Fix Authentication Credentials
```powershell
# In test-api-endpoints.ps1
$authData = @{
    username = "admin"
    password = "admin123"  # Changed from "w3r3w0lf"
} | ConvertTo-Json
```

### 4. Server Startup Sequence
```bash
# Navigate to project directory
cd C:\Users\360WEB\DeliveryAppBackend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server with network access
python manage.py runserver 0.0.0.0:8081
```

## Final Working Configuration

### Server Status
```
PS C:\Users\360WEB\DeliveryAppBackend> python manage.py runserver 0.0.0.0:8081
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
November 08, 2025 - 19:02:07
Django version 5.2.5, using settings 'DeliveryAppBackend.settings'
Starting development server at http://0.0.0.0:8081/
Quit the server with CTRL-BREAK.
```

### Mobile App Connectivity
- ✅ Server accessible on `http://0.0.0.0:8081/`
- ✅ CORS headers properly configured
- ✅ JWT authentication endpoints working
- ✅ API endpoints accessible from mobile devices

## Lessons Learned

### 1. Virtual Environment Management
- Always install packages in the correct virtual environment
- Verify package installation with `pip list` in activated venv
- Global Python installations don't affect venv

### 2. CORS Configuration for Mobile Apps
- Mobile apps require explicit CORS configuration
- `CORS_ALLOW_ALL_ORIGINS = True` useful for development
- Production should use specific allowed origins

### 3. Error Debugging Techniques
- Django server exits silently on import errors
- Use `--verbosity=3` flag for detailed server output
- Check terminal output immediately after server exit

### 4. Network Binding
- Use `0.0.0.0:port` to allow external connections
- `127.0.0.1:port` only allows localhost connections
- Mobile devices need network IP access

## Problem 2: Mobile App Connection Failure (After Server Fix)

### Symptoms
- Django server running correctly on `0.0.0.0:8081`
- CORS properly configured
- Mobile app still shows "Network request failed"
- Login attempts fail with network errors

### Error Logs (After CORS Fix)
```
LOG  Testing endpoint: http://192.168.1.69:8081/api/
LOG  Failed to connect to Auto-detected: [TypeError: Network request failed]
ERROR Login network error: [TypeError: Network request failed]
```

### Root Cause: Incorrect IP Address in Mobile App
**File:** `DeliveryAppMobile/App.tsx`, Line 1607

**Problem:**
- Mobile app hardcoded to `http://192.168.1.69:8081`
- Computer's actual IP was `192.168.1.68` (DHCP changed IP)
- Connection failed because wrong IP address

**How to Verify:**
```powershell
# Check current computer IP
ipconfig | findstr "IPv4"
# Result: IPv4 Address. . . . . . . . . . . : 192.168.1.68

# Verify server is listening
netstat -ano | findstr ":8081"
# Result: TCP    0.0.0.0:8081    0.0.0.0:0    LISTENING    31376
```

### Solution: Update Mobile App IP Address
**File:** `DeliveryAppMobile/App.tsx`
```typescript
// BEFORE (Line 1607):
const [API_BASE, setApiBase] = useState('http://192.168.1.69:8081');

// AFTER:
const [API_BASE, setApiBase] = useState('http://192.168.1.68:8081');
const [currentNetwork, setCurrentNetwork] = useState('Django Backend (192.168.1.68)');
```

Also updated `NETWORK_ENDPOINTS` fallback array:
```typescript
const NETWORK_ENDPOINTS = [
  { url: API_BASE, name: 'Auto-detected' },
  { url: 'http://192.168.1.68:8081', name: 'Current Backend IP' },  // Updated
  { url: 'http://192.168.1.77:8081', name: 'Alternative IP' },
  // ... other fallbacks
];
```

### Result
✅ Mobile app successfully connected to Django backend  
✅ Admin login working correctly  
✅ All API endpoints accessible

## Prevention Strategies

1. **Environment Verification Script**
   ```bash
   # Check if CORS is properly installed
   python -c "import corsheaders; print('CORS available')"
   ```

2. **IP Address Management**
   - **Option 1:** Set static IP on development machine
   - **Option 2:** Add "Check Backend" button in mobile app to auto-detect IP
   - **Option 3:** Use multiple fallback IPs in `NETWORK_ENDPOINTS` array
   - **Option 4:** Use hostname instead of IP (if router supports mDNS)

3. **Quick IP Verification**
   ```powershell
   # Create helper script: check-ip.ps1
   $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi").IPAddress
   Write-Host "Current IP: $ip"
   Write-Host "Update App.tsx line 1607 if needed"
   ```

4. **Settings Validation**
   - Ensure CORS middleware is enabled
   - Verify ALLOWED_HOSTS includes development IPs
   - Test API endpoints before mobile app development

5. **Credential Management**
   - Use consistent admin credentials across all test scripts
   - Document default development credentials
   - Consider using environment variables for passwords

## Related Files Modified

**Backend:**
- `DeliveryAppBackend/settings.py` - CORS configuration
- `tests/test-api-endpoints.ps1` - Admin credentials
- Virtual environment - django-cors-headers installation

**Mobile App:**
- `DeliveryAppMobile/App.tsx` - Line 1607: Updated API_BASE IP address
- `DeliveryAppMobile/App.tsx` - Lines 1610-1616: Updated NETWORK_ENDPOINTS

## Testing Commands

```bash
# Test server health
curl http://127.0.0.1:8081/

# Test authentication
curl -X POST http://127.0.0.1:8081/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Run API test suite
pwsh -File tests/test-api-endpoints.ps1

# Check current IP address
ipconfig | findstr "IPv4"

# Verify Django is listening on all interfaces
netstat -ano | findstr ":8081"
```

## Quick Reference for Future Debugging

### When Mobile App Shows "Network request failed":

1. **Check Django server is running:**
   ```powershell
   netstat -ano | findstr ":8081"
   # Should show: TCP    0.0.0.0:8081    0.0.0.0:0    LISTENING
   ```

2. **Verify computer's IP address:**
   ```powershell
   ipconfig | findstr "IPv4"
   # Compare with App.tsx line 1607
   ```

3. **Test backend from browser:**
   ```
   http://<YOUR_IP>:8081/api/
   # Should return 401 Unauthorized (expected for auth endpoints)
   ```

4. **Update mobile app if IP changed:**
   - Edit `DeliveryAppMobile/App.tsx` line 1607
   - Update `API_BASE` to correct IP
   - Restart Expo server

---

**Resolution Time:** ~2 hours  
**Impact:** Mobile app can now successfully connect to Django backend  
**Next Steps:** Monitor mobile app connectivity and implement error logging