# 🌐 Network Configuration System for DeliveryApp

This configuration system allows you to easily switch between different network environments (private, public WiFi, mobile hotspot) without manually editing settings files.

## 📋 Quick Start

### View Current Configuration
```powershell
python network_config.py status
```

### Switch Network Profiles
```powershell
# For home/office private networks
python network_config.py private

# For public WiFi (alternative ports to avoid restrictions)
python network_config.py public  

# For mobile phone hotspot
python network_config.py hotspot

# For phone access on home/office network (192.168.1.79:8081)
python network_config.py phone
```

### Smart Server Startup

#### Backend (Django)
```powershell
# Smart startup (auto-detects network configuration)
.\start-django-smart.ps1

# Or specify profile directly
.\start-django-smart.ps1 -Profile hotspot
```

#### Frontend (React)
```powershell
# Smart startup (auto-detects network configuration)
.\start-react-smart.ps1

# Or specify profile directly  
.\start-react-smart.ps1 -Profile private
```

## 🔧 Network Profiles

### 🏠 Private Network Profile
- **Use Case**: Home or office private network
- **Backend**: `127.0.0.1:8000` (localhost only)
- **Frontend**: `localhost:3000`
- **CORS**: Limited to localhost
- **Best For**: Local development, secure networks

### 🌍 Public Network Profile  
- **Use Case**: Public WiFi with port restrictions
- **Backend**: `0.0.0.0:8080` (alternative port)
- **Frontend**: `localhost:3001` (alternative port)
- **CORS**: Expanded host allowlist
- **Best For**: Coffee shops, libraries, public WiFi

### 📱 Hotspot Network Profile
- **Use Case**: Mobile phone hotspot
- **Backend**: `0.0.0.0:8000` (all interfaces)
- **Frontend**: `localhost:3000`
- **CORS**: Includes mobile IP ranges
- **Best For**: Mobile development, remote work

### 📱 Phone Network Profile  
- **Use Case**: Access from phone on home/office network
- **Backend**: `0.0.0.0:8081` (all interfaces, port 8081)
- **Frontend**: `localhost:3000` (API calls to `192.168.1.79:8081`)
- **CORS**: Optimized for phone access at `192.168.1.79`
- **Best For**: Phone app testing, cross-device development

## 📁 Configuration Files

### `network.config`
Main configuration file with all network profiles and settings:
```ini
[profile]
active=hotspot

[backend.hotspot]
HOST=0.0.0.0
PORT=8000
# ... other settings
```

### `network_config.py`
Python configuration manager:
- Reads `network.config` file
- Provides programmatic access to settings
- Handles profile switching
- Generates appropriate start commands

### `network_settings.py` (Django)
Django settings extension that automatically applies network configuration:
- Imports base Django settings
- Overlays network-specific settings
- Updates CORS, ALLOWED_HOSTS, JWT config
- Used by Django automatically when available

## 🚀 Smart Start Scripts

### `start-django-smart.ps1`
- Auto-detects network configuration
- Runs appropriate Django server command
- Handles virtual environment activation
- Falls back to hotspot mode if config unavailable

### `start-react-smart.ps1`
- Auto-detects network configuration
- Updates `.env` file with correct API URLs
- Sets appropriate port numbers
- Falls back to hotspot mode if config unavailable

## 🛠️ Manual Override

If you need to run servers manually with specific configurations:

```powershell
# Get the appropriate commands from config
python -c "from network_config import NetworkConfig; c = NetworkConfig(); print('Backend:', c.get_django_run_command()); print('Frontend:', c.get_react_start_command())"
```

## 🔄 Switching Networks Mid-Development

1. **Stop current servers** (Ctrl+C)
2. **Switch profile**: `python network_config.py <new-profile>`
3. **Restart servers**: `.\start-django-smart.ps1` and `.\start-react-smart.ps1`

## 📝 Adding New Network Profiles

Edit `network.config` and add new sections:
```ini
[backend.newprofile]
HOST=your.custom.host
PORT=8080
# ... other settings

[frontend.newprofile] 
PORT=3001
API_BASE_URL=http://your.custom.host:8080
# ... other settings
```

Then update the valid profiles list in `network_config.py` if needed.

## 🎯 Current Status

- **Active Profile**: `phone` (phone access on home/office network)
- **Backend**: Running on `http://0.0.0.0:8081/` (accessible at `http://192.168.1.79:8081/`)
- **Frontend**: Running on `http://localhost:3000/`
- **Database**: PostgreSQL on localhost (shared across all profiles)
- **JWT**: 15-minute access tokens, 7-day refresh tokens

---

*This configuration system ensures your DeliveryApp runs optimally on any network environment! 🚀*