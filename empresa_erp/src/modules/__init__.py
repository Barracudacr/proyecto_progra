"""
Módulos del Sistema ERP Empresarial
====================================
Paquete que contiene todos los módulos funcionales del sistema.
"""

from src.modules.auth import auth, AuthSystem
from src.modules.hr import employees, payroll, attendance
from src.modules.inventory import products, categories, suppliers
from src.modules.finance import sales, purchases, invoices, reports
from src.modules.reports import reports as report_generator
from src.modules.automation import email_sender, notifications, email_config

__all__ = [
    'auth',
    'AuthSystem',
    'employees',
    'payroll',
    'attendance',
    'products',
    'categories',
    'suppliers',
    'sales',
    'purchases',
    'invoices',
    'reports',
    'report_generator',
    'email_sender',
    'notifications',
    'email_config'
]
