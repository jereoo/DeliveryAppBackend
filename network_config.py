#!/usr/bin/env python3
"""
Network Configuration Manager for DeliveryApp
Reads network.config file and applies appropriate settings
"""

import os
import configparser
from pathlib import Path

class NetworkConfig:
    def __init__(self, config_file='network.config'):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()
        
    def load_config(self):
        """Load configuration from network.config file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file {self.config_file} not found")
        
        self.config.read(self.config_file)
        
        # Read the active profile from the config
        try:
            self.active_profile = self.config['profile']['active']
        except KeyError:
            self.active_profile = 'private'  # default
    
    def get_backend_config(self):
        """Get backend configuration for active profile"""
        section = f'backend.{self.active_profile}'
        if section not in self.config:
            raise ValueError(f"Backend config for profile '{self.active_profile}' not found")
        
        return {
            'HOST': self.config[section]['host'],
            'PORT': int(self.config[section]['port']),
            'DEBUG': self.config[section].getboolean('debug'),
            'ALLOWED_HOSTS': self.config[section]['allowed_hosts'].split(','),
            'CORS_ORIGINS': self.config[section]['cors_origins'].split(','),
        }
    
    def get_frontend_config(self):
        """Get frontend configuration for active profile"""
        section = f'frontend.{self.active_profile}'
        if section not in self.config:
            raise ValueError(f"Frontend config for profile '{self.active_profile}' not found")
        
        return {
            'PORT': int(self.config[section]['port']),
            'API_BASE_URL': self.config[section]['api_base_url'],
            'PROXY_TARGET': self.config[section]['proxy_target'],
        }
    
    def get_database_config(self):
        """Get database configuration"""
        return {
            'ENGINE': self.config['database']['engine'],
            'NAME': self.config['database']['name'],
            'USER': self.config['database']['user'],
            'HOST': self.config['database']['host'],
            'PORT': int(self.config['database']['port']),
        }
    
    def get_jwt_config(self):
        """Get JWT configuration"""
        return {
            'ACCESS_TOKEN_LIFETIME_MINUTES': int(self.config['jwt']['access_token_lifetime_minutes']),
            'REFRESH_TOKEN_LIFETIME_DAYS': int(self.config['jwt']['refresh_token_lifetime_days']),
            'ROTATE_REFRESH_TOKENS': self.config['jwt'].getboolean('rotate_refresh_tokens'),
            'BLACKLIST_AFTER_ROTATION': self.config['jwt'].getboolean('blacklist_after_rotation'),
        }
    
    def set_active_profile(self, profile):
        """Change the active network profile"""
        valid_profiles = ['private', 'public', 'hotspot', 'phone']
        if profile not in valid_profiles:
            raise ValueError(f"Invalid profile. Must be one of: {valid_profiles}")
        
        # Update the active profile in config
        self.config['profile']['active'] = profile
        
        # Write back to file
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        
        self.active_profile = profile
        print(f"✅ Network profile changed to: {profile}")
    
    def get_django_run_command(self):
        """Get the appropriate Django runserver command"""
        backend_config = self.get_backend_config()
        host = backend_config['HOST']
        port = backend_config['PORT']
        return f"python manage.py runserver {host}:{port}"
    
    def get_react_start_command(self):
        """Get the appropriate React start command with port"""
        frontend_config = self.get_frontend_config()
        port = frontend_config['PORT']
        return f"PORT={port} npm start"
    
    def print_current_config(self):
        """Print the current configuration summary"""
        print(f"\n🌐 Current Network Profile: {self.active_profile.upper()}")
        print("=" * 50)
        
        backend = self.get_backend_config()
        frontend = self.get_frontend_config()
        
        print(f"📊 Backend Server: http://{backend['HOST']}:{backend['PORT']}/")
        print(f"⚛️  Frontend Server: http://localhost:{frontend['PORT']}/")
        print(f"🔗 API Base URL: {frontend['API_BASE_URL']}")
        print(f"🎯 CORS Origins: {', '.join(backend['CORS_ORIGINS'])}")
        
        print(f"\n🚀 Start Commands:")
        print(f"Backend:  {self.get_django_run_command()}")
        print(f"Frontend: {self.get_react_start_command()}")
        print()

def main():
    """CLI interface for network configuration management"""
    import sys
    
    config = NetworkConfig()
    
    if len(sys.argv) == 1:
        config.print_current_config()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['private', 'public', 'hotspot', 'phone']:
            config.set_active_profile(sys.argv[1])
            config.print_current_config()
        elif sys.argv[1] == 'status':
            config.print_current_config()
        else:
            print("Usage: python network_config.py [private|public|hotspot|phone|status]")
    else:
        print("Usage: python network_config.py [private|public|hotspot|phone|status]")

if __name__ == '__main__':
    main()