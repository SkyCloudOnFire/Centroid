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
                'export_csv': 'Export CSV',
                'quick_start_guide': 'Quick Start Guide',
                'quick_start_steps': '''
                    1. **Choose Analysis Type**: Select 2D or 3D analysis from the sidebar
                    2. **Input Geometry**: Enter dimensions or import files
                    3. **Calculate**: Click calculate to get results
                    4. **Visualize**: Interact with real-time 3D visualization
                    5. **Export**: Generate PDF reports or export data
                '''
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
                'export_csv': 'خروجی CSV',
                'quick_start_guide': 'راهنمای شروع سریع',
                'quick_start_steps': '''
                    1. **نوع تحلیل را انتخاب کنید**: تحلیل دوبعدی یا سه بعدی را از نوار کناری انتخاب کنید
                    2. **ورود هندسه**: ابعاد را وارد کنید یا فایل وارد کنید
                    3. **محاسبه**: روی محاسبه کلیک کنید تا نتایج را ببینید
                    4. **نمایش تصویری**: با نمایش سه بعدی تعاملی کار کنید
                    5. **خروجی**: گزارش PDF تولید کنید یا داده‌ها را خروجی بگیرید
                '''
            }
        }
    
    def get_translations(self, language: str) -> dict:
        """Get translations for a language"""
        return self.translations.get(language, self.translations['English'])