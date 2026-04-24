"""
Módulo de Contabilidad y Finanzas
=================================
Gestión de ventas, compras, facturación y reportes financieros.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from src.database import db
from src.modules.auth import auth
from src.modules.inventory import products


class SalesManager:
    """Gestor de ventas y transacciones."""

    def __init__(self):
        self.db = db

    def create_sale(self, data: Dict) -> Dict:
        """
        Registra una nueva venta.
        Actualiza el inventario de forma automática.
        """
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para registrar ventas")

        sale_items = data.get('items', [])
        subtotal = 0
        processed_items = []

        for item in sale_items:
            product = products.get_product(product_id=item['product_id'])
            if not product:
                raise ValueError(f"Producto {item['product_id']} no encontrado")

            if product['stock'] < item['quantity']:
                raise ValueError(f"Stock insuficiente para {product['name']}")

            item_total = product['price'] * item['quantity']
            subtotal += item_total

            products.stock_output(
                product_id=item['product_id'],
                quantity=item['quantity'],
                notes=f"Venta #{data.get('invoice_number', 'N/A')}",
                reference=data.get('invoice_number', '')
            )

            processed_items.append({
                'product_id': item['product_id'],
                'product_name': product['name'],
                'quantity': item['quantity'],
                'unit_price': product['price'],
                'total': item_total
            })

        tax_rate = 0.16
        tax = subtotal * tax_rate
        total = subtotal + tax

        sale = {
            'id': str(uuid.uuid4())[:12],
            'invoice_number': data.get('invoice_number', self._generate_invoice_number()),
            'customer_name': data.get('customer_name', 'Consumidor Final'),
            'customer_cedula': data.get('customer_cedula', ''),
            'customer_address': data.get('customer_address', ''),
            'items': processed_items,
            'subtotal': subtotal,
            'tax': tax,
            'tax_rate': tax_rate,
            'total': total,
            'payment_method': data.get('payment_method', 'efectivo'),
            'payment_status': 'completada',
            'notes': data.get('notes', ''),
            'created_by': auth.get_session()['user_id'],
            'created_at': datetime.now().isoformat(),
            'status': 'completada'
        }

        return self.db.CRUD('sales', 'create', data=sale)

    def _generate_invoice_number(self) -> str:
        """Genera un número de factura único."""
        date = datetime.now().strftime('%Y%m%d')
        return f"F{date}-{str(uuid.uuid4())[:6].upper()}"

    def list_sales(self, filters: Dict = None) -> List[Dict]:
        """Lista ventas con filtros."""
        return self.db.CRUD('sales', 'list', filters=filters)

    def get_sale(self, sale_id: str) -> Optional[Dict]:
        """Obtiene detalles de una venta."""
        return self.db.CRUD('sales', 'find', record_id=sale_id)

    def cancel_sale(self, sale_id: str, reason: str = '') -> Dict:
        """Cancela una venta y revierte el inventario."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para cancelar ventas")

        sale = self.get_sale(sale_id)
        if not sale:
            raise ValueError("Venta no encontrada")

        if sale['status'] == 'cancelada':
            raise ValueError("La venta ya está cancelada")

        for item in sale['items']:
            products.stock_entry(
                product_id=item['product_id'],
                quantity=item['quantity'],
                notes=f"Reversión de venta cancelada #{sale['invoice_number']}",
                reference=sale['invoice_number']
            )

        return self.db.CRUD('sales', 'update',
                           data={
                               'status': 'cancelada',
                               'cancel_reason': reason,
                               'cancelled_at': datetime.now().isoformat(),
                               'cancelled_by': auth.get_session()['user_id']
                           },
                           record_id=sale_id)


class PurchasesManager:
    """Gestor de compras a proveedores."""

    def __init__(self):
        self.db = db

    def create_purchase(self, data: Dict) -> Dict:
        """
        Registra una nueva compra.
        Actualiza el inventario de forma automática.
        """
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para registrar compras")

        purchase_items = data.get('items', [])
        subtotal = 0
        processed_items = []

        for item in purchase_items:
            product = products.get_product(product_id=item['product_id'])
            if not product:
                raise ValueError(f"Producto {item['product_id']} no encontrado")

            item_total = item['unit_cost'] * item['quantity']
            subtotal += item_total

            products.stock_entry(
                product_id=item['product_id'],
                quantity=item['quantity'],
                notes=f"Compra a proveedor",
                reference=data.get('purchase_order', '')
            )

            if item.get('update_cost'):
                products.update_product(
                    item['product_id'],
                    {'cost': item['unit_cost']}
                )

            processed_items.append({
                'product_id': item['product_id'],
                'product_name': product['name'],
                'quantity': item['quantity'],
                'unit_cost': item['unit_cost'],
                'total': item_total
            })

        purchase = {
            'id': str(uuid.uuid4())[:12],
            'purchase_order': data.get('purchase_order', self._generate_po_number()),
            'supplier_id': data.get('supplier_id'),
            'supplier_name': data.get('supplier_name', ''),
            'items': processed_items,
            'subtotal': subtotal,
            'tax': subtotal * 0.16,
            'total': subtotal * 1.16,
            'payment_status': 'pendiente',
            'payment_method': data.get('payment_method', 'credito'),
            'due_date': data.get('due_date', ''),
            'notes': data.get('notes', ''),
            'created_by': auth.get_session()['user_id'],
            'created_at': datetime.now().isoformat(),
            'status': 'recibida'
        }

        return self.db.CRUD('purchases', 'create', data=purchase)

    def _generate_po_number(self) -> str:
        """Genera un número de orden de compra único."""
        date = datetime.now().strftime('%Y%m%d')
        return f"OC{date}-{str(uuid.uuid4())[:6].upper()}"

    def list_purchases(self, filters: Dict = None) -> List[Dict]:
        """Lista compras con filtros."""
        return self.db.CRUD('purchases', 'list', filters=filters)

    def get_purchase(self, purchase_id: str) -> Optional[Dict]:
        """Obtiene detalles de una compra."""
        return self.db.CRUD('purchases', 'find', record_id=purchase_id)

    def mark_as_paid(self, purchase_id: str, payment_data: Dict) -> Dict:
        """Marca una compra como pagada."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para actualizar compras")

        return self.db.CRUD('purchases', 'update',
                           data={
                               'payment_status': 'pagada',
                               'payment_date': datetime.now().isoformat(),
                               'payment_reference': payment_data.get('reference', '')
                           },
                           record_id=purchase_id)


class InvoiceGenerator:
    """
    Generador de facturas PDF.
    Utiliza ReportLab para crear documentos profesionales.
    """

    def __init__(self):
        self.db = db

    def generate_invoice(self, sale_id: str, output_path: str = None) -> str:
        """Genera una factura PDF para una venta."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
        except ImportError:
            print("Advertencia: ReportLab no está instalado. Se generará factura en texto plano.")
            return self._generate_text_invoice(sale_id, output_path)

        sale = self.db.CRUD('sales', 'find', record_id=sale_id)
        if not sale:
            raise ValueError("Venta no encontrada")

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data/exports/factura_{sale['invoice_number']}_{timestamp}.pdf"

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        header_data = [
            [Paragraph("<b>FACTURA</b>", styles['Title']),
             Paragraph(f"<b>N° {sale['invoice_number']}</b><br/>"
                      f"Fecha: {sale['created_at'][:10]}", styles['Normal'])]
        ]
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))

        customer_info = f"""
        <b>Cliente:</b> {sale['customer_name']}<br/>
        <b>Cédula:</b> {sale.get('customer_cedula', '')}<br/>
        <b>Dirección:</b> {sale['customer_address']}
        """
        elements.append(Paragraph(customer_info, styles['Normal']))
        elements.append(Spacer(1, 20))

        items_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Total']]
        for item in sale['items']:
            items_data.append([
                item['product_name'],
                str(item['quantity']),
                f"CRC {item['unit_price']:.2f}",
                f"CRC {item['total']:.2f}"
            ])

        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 20))

        totals_data = [
            ['Subtotal:', f"CRC {sale['subtotal']:.2f}"],
            ['IVA (16%):', f"CRC {sale['tax']:.2f}"],
            ['TOTAL:', f"CRC {sale['total']:.2f}"]
        ]
        totals_table = Table(totals_data, colWidths=[6*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
        ]))
        elements.append(totals_table)

        doc.build(elements)
        return output_path

    def _generate_text_invoice(self, sale_id: str, output_path: str = None) -> str:
        """Genera factura en formato texto plano."""
        sale = self.db.CRUD('sales', 'find', record_id=sale_id)
        if not sale:
            raise ValueError("Venta no encontrada")

        invoice_text = f"""
{'='*60}
                    FACTURA
              N° {sale['invoice_number']}
{'='*60}

Fecha: {sale['created_at'][:10]}

Cliente: {sale['customer_name']}
Cédula: {sale.get('customer_cedula', '')}
Dirección: {sale['customer_address']}

{'='*60}
PRODUCTO              CANT    PRECIO      TOTAL
{'-'*60}
"""

        for item in sale['items']:
            invoice_text += f"{item['product_name']:<20} {item['quantity']:>4} "
            invoice_text += f"{item['unit_price']:>10.2f} {item['total']:>10.2f}\n"

        invoice_text += f"""
{'-'*60}
Subtotal:                         CRC {sale['subtotal']:.2f}
IVA (16%):                        CRC {sale['tax']:.2f}
{'-'*60}
TOTAL:                            CRC {sale['total']:.2f}
{'='*60}

Forma de Pago: {sale['payment_method']}
Estado: {sale['payment_status']}

¡Gracias por su compra!
{'='*60}
"""

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data/exports/factura_{sale['invoice_number']}_{timestamp}.txt"

        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(invoice_text)

        return output_path


class FinanceReports:
    """Generador de reportes financieros."""

    def __init__(self):
        self.db = db

    def get_cash_flow(self, start_date: str, end_date: str) -> Dict:
        """
        Calcula el flujo de caja para un período.
        """
        sales = self.db.CRUD('sales', 'list',
                            filters={'date_from': start_date, 'date_to': end_date})
        purchases = self.db.CRUD('purchases', 'list',
                                 filters={'date_from': start_date, 'date_to': end_date})

        total_sales = sum(s['total'] for s in sales if s['status'] == 'completada')
        total_purchases = sum(p['total'] for p in purchases if p['status'] == 'recibida')

        payroll = self.db.CRUD('payroll', 'list',
                               filters={'date_from': start_date, 'date_to': end_date})
        total_payroll = sum(p['details']['net_salary'] for p in payroll
                           if p['status'] == 'pagado')

        return {
            'period': {'start': start_date, 'end': end_date},
            'income': {
                'total_sales': total_sales,
                'sales_count': len([s for s in sales if s['status'] == 'completada'])
            },
            'expenses': {
                'total_purchases': total_purchases,
                'total_payroll': total_payroll,
                'total_expenses': total_purchases + total_payroll
            },
            'cash_flow': total_sales - (total_purchases + total_payroll),
            'sales': sales,
            'purchases': purchases
        }

    def get_income_statement(self, start_date: str, end_date: str) -> Dict:
        """
        Genera estado de pérdidas y ganancias.
        """
        sales = self.db.CRUD('sales', 'list',
                            filters={'date_from': start_date, 'date_to': end_date})
        purchases = self.db.CRUD('purchases', 'list',
                                 filters={'date_from': start_date, 'date_to': end_date})

        completed_sales = [s for s in sales if s['status'] == 'completada']
        total_revenue = sum(s['total'] for s in completed_sales)
        total_sales_tax = sum(s['tax'] for s in completed_sales)
        net_revenue = total_revenue - total_sales_tax

        total_cost_sales = sum(s['subtotal'] for s in completed_sales)
        gross_profit = net_revenue - total_cost_sales

        payroll = self.db.CRUD('payroll', 'list',
                               filters={'date_from': start_date, 'date_to': end_date})
        total_payroll_expense = sum(p['details']['net_salary'] for p in payroll
                                    if p['status'] == 'pagado')

        operating_expenses = total_payroll_expense

        net_profit = gross_profit - operating_expenses

        return {
            'period': {'start': start_date, 'end': end_date},
            'revenue': {
                'gross_revenue': total_revenue,
                'sales_tax': total_sales_tax,
                'net_revenue': net_revenue
            },
            'cost_of_sales': total_cost_sales,
            'gross_profit': gross_profit,
            'operating_expenses': {
                'payroll': total_payroll_expense,
                'total': operating_expenses
            },
            'net_profit': net_profit,
            'profit_margin': (net_profit / net_revenue * 100) if net_revenue > 0 else 0
        }

    def get_balance_sheet(self) -> Dict:
        """
        Genera balance general simplificado.
        """
        products = self.db.CRUD('products', 'list', filters={'status': 'activo'})
        inventory_value = sum(p['cost'] * p['stock'] for p in products)

        employees = self.db.CRUD('employees', 'list', filters={'status': 'activo'})
        pending_payroll = sum(emp['salary'] for emp in employees)

        accounts_receivable = 0
        sales = self.db.CRUD('sales', 'list')
        for sale in sales:
            if sale['payment_status'] == 'completada' and sale['status'] != 'cancelada':
                accounts_receivable += sale['total']

        assets = {
            'current_assets': {
                'cash': 0,
                'accounts_receivable': accounts_receivable,
                'inventory': inventory_value,
                'total_current': accounts_receivable + inventory_value
            },
            'total_assets': accounts_receivable + inventory_value
        }

        liabilities = {
            'current_liabilities': {
                'accounts_payable': 0,
                'payroll_liability': pending_payroll,
                'taxes_payable': 0,
                'total_current': pending_payroll
            },
            'total_liabilities': pending_payroll
        }

        equity = assets['total_assets'] - liabilities['total_liabilities']

        return {
            'generated_at': datetime.now().isoformat(),
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'balance_check': assets['total_assets'] == (liabilities['total_liabilities'] + equity)
        }

    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Resumen de ventas."""
        filters = {}
        if start_date:
            filters['date_from'] = start_date
        if end_date:
            filters['date_to'] = end_date

        sales = self.db.CRUD('sales', 'list', filters=filters)
        completed_sales = [s for s in sales if s['status'] == 'completada']

        return {
            'total_sales': len(completed_sales),
            'total_revenue': sum(s['total'] for s in completed_sales),
            'average_sale': sum(s['total'] for s in completed_sales) / len(completed_sales) if completed_sales else 0,
            'sales_by_payment': {
                'efectivo': sum(s['total'] for s in completed_sales if s['payment_method'] == 'efectivo'),
                'tarjeta': sum(s['total'] for s in completed_sales if s['payment_method'] == 'tarjeta'),
                'transferencia': sum(s['total'] for s in completed_sales if s['payment_method'] == 'transferencia')
            }
        }


sales = SalesManager()
purchases = PurchasesManager()
invoices = InvoiceGenerator()
reports = FinanceReports()
