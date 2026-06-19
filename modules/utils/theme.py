# modules/utils/theme.py
"""Theme management"""

class ThemeManager:
    """Manage UI themes"""
    
    THEMES = {
        'light': {
            'background': '#ffffff',
            'text': '#0e1117',
            'primary': '#667eea',
            'card_bg': '#f0f2f6'
        },
        'dark': {
            'background': '#0e1117',
            'text': '#fafafa',
            'primary': '#667eea',
            'card_bg': '#262730'
        }
    }
    
    def get_theme(self, theme_name: str) -> dict:
        """Get theme colors"""
        return self.THEMES.get(theme_name.lower(), self.THEMES['light'])