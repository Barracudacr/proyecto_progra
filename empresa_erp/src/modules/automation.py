"""
Módulo de Automatización
========================
Envío de correos automáticos, notificaciones y tareas programadas.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from src.database import db
from src.modules.finance import reports as finance_reports


class EmailConfig:
    """Configuración del servidor de correo."""

    def __init__(self):
        self.smtp_server = ""
        self.smtp_port = 587
        self.sender_email = ""
        self.sender_password = ""
        self.use_tls = True

    def configure(self, smtp_server: str, smtp_port: int, sender_email: str,
                 sender_password: str, use_tls: bool = True):
        """Configura los parámetros del servidor SMTP."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

    def save_config(self, filepath: str = "data/email_config.json"):
        """Guarda la configuración en un archivo JSON."""
        import json
        config_path = Path(filepath)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_email': self.sender_email,
            'use_tls': self.use_tls
        }

        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)

    def load_config(self, filepath: str = "data/email_config.json"):
        """Carga la configuración desde un archivo JSON."""
        import json
        config_path = Path(filepath)

        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.smtp_server = config.get('smtp_server', '')
                self.smtp_port = config.get('smtp_port', 587)
                self.sender_email = config.get('sender_email', '')
                self.use_tls = config.get('use_tls', True)
                return True
        return False


class EmailSender:
    """
    Clase para enviar correos electrónicos.
    Soporta HTML, archivos adjuntos y múltiples destinatarios.
    """

    def __init__(self):
        self.config = EmailConfig()

    def send_email(self, to_email: str, subject: str, body: str,
                  html_body: str = None, attachments: List[str] = None) -> bool:
        """
        Envía un correo electrónico.

        Args:
            to_email: Correo del destinatario
            subject: Asunto del correo
            body: Cuerpo del mensaje (texto plano)
            html_body: Cuerpo del mensaje (HTML)
            attachments: Lista de rutas de archivos adjuntos

        Returns:
            True si el correo fue enviado exitosamente
        """
        if not self.config.sender_email or not self.config.sender_password:
            print("Error: Configuración de correo no encontrada")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            msg.attach(MIMEText(body, 'plain'))

            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            if attachments:
                for filepath in attachments:
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                  f'attachment; filename= {Path(filepath).name}')
                    msg.attach(part)

            context = ssl.create_default_context()

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.ehlo()
                if self.config.use_tls:
                    server.starttls(context=context)
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False

    def send_mass_email(self, recipients: List[Dict], subject: str,
                       body_template: str, **template_vars) -> Dict:
        """
        Envía correos masivos a múltiples destinatarios.

        Args:
            recipients: Lista de diccionarios con 'email' y 'name'
            subject: Asunto del correo
            body_template: Plantilla del cuerpo (soporta format)
            **template_vars: Variables para la plantilla

        Returns:
            Dict con estadísticas de envío
        """
        results = {'sent': 0, 'failed': 0, 'errors': []}

        for recipient in recipients:
            try:
                personalized_body = body_template.format(
                    name=recipient.get('name', 'Usuario'),
                    **template_vars
                )

                if self.send_email(recipient['email'], subject, personalized_body):
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Falló envío a {recipient['email']}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error con {recipient['email']}: {str(e)}")

        return results


class NotificationSystem:
    """
    Sistema de notificaciones automáticas.
    Envía alertas por correo y genera reportes programados.
    """

    def __init__(self):
        self.email_sender = EmailSender()
        self.db = db

    def check_and_notify_low_stock(self) -> Dict:
        """
        Verifica productos con stock bajo y envía notificaciones.
        """
        from src.modules.inventory import products

        low_stock_products = products.get_low_stock_products()

        if not low_stock_products:
            return {'notified': False, 'count': 0}

        subject = "Alerta: Productos con Stock Bajo"

        body = f"""
Sistema ERP - Alerta de Inventario
===================================

Se han detectado {len(low_stock_products)} producto(s) con stock bajo:

"""

        for product in low_stock_products:
            body += f"- {product['name']}\n"
            body += f"  Stock actual: {product['stock']}\n"
            body += f"  Stock mínimo: {product['min_stock']}\n\n"

        body += """
Por favor, revise el inventario y realice los pedidos correspondientes.

Este es un mensaje automático del Sistema ERP.
        """

        employees = self.db.CRUD('employees', 'list', filters={'status': 'activo'})
        recipients = []

        for emp in employees:
            if emp.get('email'):
                recipients.append({
                    'email': emp.get('email'),
                    'name': f"{emp.get('first_name', '')} {emp.get('last_name', '')}"
                })

        if recipients:
            self.email_sender.send_mass_email(recipients, subject, body)

        return {'notified': True, 'count': len(low_stock_products), 'recipients': len(recipients)}

    def notify_payroll_day(self) -> Dict:
        """
        Envía notificación recordatorio de día de pago.
        """
        from src.modules.hr import payroll

        today = datetime.now()
        last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        if today.day == last_day.day:
            employees = self.db.CRUD('employees', 'list', filters={'status': 'activo'})

            subject = "Recordatorio: Día de Pago"

            body = f"""
Sistema ERP - Recordatorio de Nómina
====================================

Se acerca la fecha de pago de nómina.

Fecha: {today.strftime('%Y-%m-%d')}

Por favor, asegúrese de que todos los registros de asistencia estén actualizados.

Este es un mensaje automático del Sistema ERP.
            """

            recipients = []
            for emp in employees:
                if emp.get('email'):
                    recipients.append({
                        'email': emp.get('email'),
                        'name': f"{emp.get('first_name', '')} {emp.get('last_name', '')}"
                    })

            if recipients:
                self.email_sender.send_mass_email(recipients, subject, body)

            return {'notified': True, 'recipients': len(recipients)}

        return {'notified': False}

    def send_daily_summary(self, company_id: str) -> Dict:
        """
        Envía resumen diario de la empresa a los gerentes.
        """
        self.db.select_company(company_id)

        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        cash_flow = finance_reports.get_cash_flow(yesterday, today)

        subject = f"Resumen Diario - {today}"

        body = f"""
Sistema ERP - Resumen Diario
=============================

Empresa: {company_id}
Fecha: {today}

RESUMEN DE VENTAS
-----------------
Total de ventas: CRC {cash_flow['income']['total_sales']:,.2f}
Cantidad de transacciones: {cash_flow['income']['sales_count']}

RESUMEN DE GASTOS
-----------------
Total de compras: CRC {cash_flow['expenses']['total_purchases']:,.2f}
Total de nómina: CRC {cash_flow['expenses']['total_payroll']:,.2f}

FLUJO DE CAJA
-------------
Flujo de caja neto: CRC {cash_flow['cash_flow']:,.2f}

Este es un mensaje automático del Sistema ERP.
        """

        users = self.db.CRUD('users', 'list', filters={'role': 'gerente'})
        recipients = []

        for user in users:
            if user.get('email'):
                recipients.append({
                    'email': user['email'],
                    'name': user.get('full_name', user['username'])
                })

        if recipients:
            self.email_sender.send_mass_email(recipients, subject, body)

        return {'sent': True, 'recipients': len(recipients)}

    def send_weekly_report(self, company_id: str) -> Dict:
        """
        Envía reporte semanal completo a administradores.
        """
        self.db.select_company(company_id)

        today = datetime.now()
        week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')

        from src.modules.reports import reports

        dashboard = reports.generate_executive_dashboard()

        subject = f"Reporte Semanal - {today_str}"

        body = f"""
Sistema ERP - Reporte Semanal
==============================

Empresa: {company_id}
Período: {week_ago} al {today_str}
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%M')}

RESUMEN EJECUTIVO
-----------------

1. FINANZAS
   Ventas totales: CRC {dashboard['financial']['total_sales']:,.2f}
   Gastos totales: CRC {dashboard['financial']['total_expenses']:,.2f}
   Transacciones: {dashboard['financial']['sales_count']}
   Flujo de caja: CRC {dashboard['financial']['cash_flow']:,.2f}

2. INVENTARIO
   Productos activos: {dashboard['inventory']['total_products']}
   Valor total: CRC {dashboard['inventory']['total_value']:,.2f}
   Alertas de stock bajo: {dashboard['inventory']['low_stock_count']}

3. RECURSOS HUMANOS
   Empleados activos: {dashboard['hr']['total_employees']}
   Costo de nómina: CRC {dashboard['hr']['total_payroll']:,.2f}

ALERTAS PENDIENTES: {len(dashboard['alerts'])}

Este es un mensaje automático del Sistema ERP.
        """

        users = self.db.CRUD('users', 'list', filters={'role': 'admin'})
        recipients = []

        for user in users:
            if user.get('email'):
                recipients.append({
                    'email': user['email'],
                    'name': user.get('full_name', user['username'])
                })

        if recipients:
            self.email_sender.send_mass_email(recipients, subject, body)

        return {'sent': True, 'recipients': len(recipients)}


email_config = EmailConfig()
email_sender = EmailSender()
notifications = NotificationSystem()
