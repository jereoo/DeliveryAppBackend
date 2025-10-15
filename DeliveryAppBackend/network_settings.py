# Network-Aware Django Settings
# This file imports the base settings and applies network-specific configurations

from .settings import *
from pathlib import Path
import sys
import os

# Add the parent directory to sys.path to import network_config
current_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(current_dir))

try:
    from network_config import NetworkConfig
    
    # Load network configuration
    network_config = NetworkConfig()
    backend_config = network_config.get_backend_config()
    
    # Apply network-specific settings
    DEBUG = backend_config['DEBUG']
    ALLOWED_HOSTS = backend_config['ALLOWED_HOSTS']
    
    # Update CORS settings
    CORS_ALLOWED_ORIGINS = backend_config['CORS_ORIGINS']
    CORS_ALLOW_CREDENTIALS = True
    
    # JWT settings from config
    jwt_config = network_config.get_jwt_config()
    from datetime import timedelta
    
    SIMPLE_JWT.update({
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=jwt_config['ACCESS_TOKEN_LIFETIME_MINUTES']),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=jwt_config['REFRESH_TOKEN_LIFETIME_DAYS']),
        'ROTATE_REFRESH_TOKENS': jwt_config['ROTATE_REFRESH_TOKENS'],
        'BLACKLIST_AFTER_ROTATION': jwt_config['BLACKLIST_AFTER_ROTATION'],
    })
    
    # Database settings from config
    db_config = network_config.get_database_config()
    DATABASES['default'].update({
        'ENGINE': db_config['ENGINE'],
        'NAME': db_config['NAME'],
        'USER': db_config['USER'],
        'HOST': db_config['HOST'],
        'PORT': db_config['PORT'],
    })
    
    print(f"🌐 Loaded network profile: {network_config.active_profile}")
    print(f"📊 Backend will run on: {backend_config['HOST']}:{backend_config['PORT']}")
    
except (ImportError, FileNotFoundError) as e:
    print(f"⚠️  Network config not found, using default settings: {e}")
    # Fallback to current hotspot settings
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.79']
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://0.0.0.0:3000',
        'http://192.168.1.79:3000',
    ]