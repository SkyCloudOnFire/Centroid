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
                ''',
                'btn_2d_title': '🔷\n\n**2D Analysis**',
                'btn_2d_desc': 'Calculate centroids for 2D shapes',
                'btn_2d_list': '• Analytical formulas\n• Composite shapes\n• Coordinate input\n• Area calculation',
                'btn_3d_title': '🔶\n\n**3D Analysis**',
                'btn_3d_desc': 'Compute center of mass for 3D solids',
                'btn_3d_list': '• Cube, sphere, cylinder\n• Composite bodies\n• Volume calculation\n• 3D visualization',
                'btn_stl_title': '🔧\n\n**STL Import**',
                'btn_stl_desc': 'Import and analyze 3D mesh geometries',
                'btn_stl_list': '• Mesh processing\n• Volume integration\n• Centroid calculation\n• Mesh statistics'
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
                    5. **خروجی**: گزارش پی‌دی‌اف تولید کنید یا داده‌ها را خروجی بگیرید
                ''',
                'btn_2d_title': '🔷\n\n**تحلیل دوبعدی**',
                'btn_2d_desc': 'محاسبه مرکز سطح برای اشکال دوبعدی',
                'btn_2d_list': '• فرمول‌های تحلیلی\n• اشکال ترکیبی\n• ورود مختصات\n• محاسبه مساحت',
                'btn_3d_title': '🔶\n\n**تحلیل سه بعدی**',
                'btn_3d_desc': 'محاسبه مرکز جرم برای اجسام سه بعدی',
                'btn_3d_list': '• مکعب، کره، استوانه\n• اجسام ترکیبی\n• محاسبه حجم\n• نمایش سه بعدی',
                'btn_stl_title': '🔧\n\n**وارد کردن STL**',
                'btn_stl_desc': 'وارد کردن و تحلیل هندسه‌های مش سه بعدی',
                'btn_stl_list': '• پردازش مش\n• انتگرال‌گیری حجم\n• محاسبه مرکز سطح\n• آمار مش'
            }
        }
    
    def get_translations(self, language: str) -> dict:
        """Get translations for a language"""
        return self.translations.get(language, self.translations['English'])