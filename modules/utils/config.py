# modules/utils/config.py
"""Configuration management"""

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self):
        self.config = {
            'units': 'mm',
            'precision': 3,
            'theme': 'light',
            'language': 'English',
            'show_grid': True,
            'show_axes': True,
            'marker_size': 10
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value