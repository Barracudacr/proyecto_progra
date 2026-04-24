"""
EnterpriseERP - Sistema de Gestión Empresarial
==============================================

Paquete principal del sistema ERP empresarial.
Construido 100% en Python puro.
"""

__version__ = "1.0.0"
__author__ = "EnterpriseERP Team"
__license__ = "MIT"

from src.database import db
from src.modules.auth import auth
from src.modules.hr import employees, payroll, attendance
from src.modules.inventory import products, categories, suppliers
from src.modules.finance import sales, purchases, invoices, reports
from src.modules.reports import reports as report_generator
from src.modules.automation import email_sender, notifications, email_config
