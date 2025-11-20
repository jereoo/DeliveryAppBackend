# DeliveryApp Debug Quick Reference

## 🔧 Common Issues & Solutions

### Django Server Won't Start

#### Issue: Server exits immediately
```bash
# Symptoms
python manage.py runserver 0.0.0.0:8081
# Server starts then exits with code 1
```

**Solution Checklist:**
1. ✅ Check virtual environment is activated
2. ✅ Verify all packages installed in venv
3. ✅ Check CORS configuration
4. ✅ Validate database connection
5. ✅ Review Django settings for errors

```bash
# Quick fixes
.\venv\Scripts\Activate.ps1
pip install django-cors-headers
python manage.py check
python manage.py showmigrations
```

### Mobile App Connection Issues

#### Issue: "Network request failed"
**Common Causes:**
- CORS not configured
- Server not running on correct IP/port
- Firewall blocking connections
- Authentication credentials incorrect

**Debug Steps:**
```bash
# 1. Verify server is running
curl http://127.0.0.1:8081/

# 2. Test authentication
curl -X POST http://127.0.0.1:8081/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. Check network accessibility
curl http://192.168.1.69:8081/api/

# 4. Run API test suite
pwsh -File tests/test-api-endpoints.ps1
```

### Database Issues

#### Issue: Migration conflicts
```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial
python manage.py makemigrations --empty delivery
python manage.py migrate
```

#### Issue: PostgreSQL connection errors
```bash
# Check PostgreSQL status
Get-Service postgresql*

# Test connection
python manage.py dbshell
```

## 🚀 Quick Start Commands

### Environment Setup
```powershell
# Navigate to project
cd C:\Users\360WEB\DeliveryAppBackend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Django server
python manage.py runserver 0.0.0.0:8081
```

### Mobile App Setup
```powershell
# Navigate to mobile project
cd C:\Users\360WEB\DeliveryAppMobile

# Start Expo development server
npm start
```

### Testing Suite
```powershell
# Run Django tests
python manage.py test

# Run API endpoint tests
pwsh -File tests/test-api-endpoints.ps1

# Check mobile app network config
# Verify enhanced_network_config.js settings
```

## 📋 System Requirements Checklist

### Backend Requirements
- [x] Python 3.13+
- [x] Django 5.2.5
- [x] PostgreSQL running
- [x] Virtual environment activated
- [x] CORS headers installed
- [x] Admin user created

### Mobile App Requirements  
- [x] Node.js + npm
- [x] Expo CLI
- [x] Mobile device or emulator
- [x] Network connectivity to backend
- [x] Correct API base URL configured

### Network Configuration
- [x] Django server on `0.0.0.0:8081`
- [x] Mobile app on `19000` (Expo default)
- [x] Firewall allows inbound traffic on 8081
- [x] CORS configured for cross-origin requests

## 🚨 Emergency Recovery

### Complete System Reset
```powershell
# 1. Kill all processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
taskkill /F /IM node.exe 2>$null

# 2. Restart PostgreSQL
Restart-Service postgresql*

# 3. Reset database (CAUTION: Deletes all data)
python manage.py flush --noinput
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email admin@test.com
python manage.py create_test_data

# 4. Restart services
python manage.py runserver 0.0.0.0:8081 &
cd ../DeliveryAppMobile && npm start
```

### Backup & Restore
```powershell
# Create database backup
pg_dump -U delivery_user -h localhost delivery_app > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Restore from backup
psql -U delivery_user -h localhost delivery_app < backup_20251108_190000.sql
```

---

**Last Updated:** November 8, 2025  
**For detailed technical analysis, see:** `DJANGO_SERVER_CONNECTION_DEBUG.md`