# modules/utils/language.py
"""Language management with translations"""

import json


class LanguageManager:
    """Manage translations and language switching"""
    
    def __init__(self):
        self.translations = {
            'English': {
                'title': 'Center of Mass & Centroid Analysis System',
                'subtitle': '2D and 3D Geometry Analysis Platform',
                'welcome': 'Welcome to COM Analysis System',
                '2d_analysis': '2D Analysis',
                '3d_analysis': '3D Analysis',
                'stl_import': 'STL Import',
                'report_generator': 'Report Generator',
                'settings': 'Settings',
                'calculate': 'Calculate',
                'reset': 'Reset',
                'export_pdf': 'Export PDF',
                'export_csv': 'Export CSV'
            },
            'Persian': {
                'title': 'سیستم تحلیل مرکز جرم و مرکز سطح',
                'subtitle': 'پلتفرم تحلیل هندسه دوبعدی و سه بعدی',
                'welcome': 'به سیستم تحلیل مرکز جرم خوش آمدید',
                '2d_analysis': 'تحلیل دوبعدی',
                '3d_analysis': 'تحلیل سه بعدی',
                'stl_import': 'وارد کردن فایل STL',
                'report_generator': 'تولید گزارش',
                'settings': 'تنظیمات',
                'calculate': 'محاسبه',
                'reset': 'بازنشانی',
                'export_pdf': 'خروجی PDF',
                'export_csv': 'خروجی CSV'
            }
        }
    
    def get_translations(self, language: str) -> dict:
        """Get translations for a language"""
        return self.translations.get(language, self.translations['English'])