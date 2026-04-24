"""
Módulo de Generación de Reportes y Gráficos
============================================
Utiliza Matplotlib y Pandas para generar reportes visuales.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from src.database import db
from src.modules.finance import reports as finance_reports


class ReportGenerator:
    """
    Generador de reportes gráficos y tableros de control (Dashboards).
    """

    def __init__(self):
        self.db = db
        self.output_dir = Path("data/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_plot(self, filename: str) -> str:
        """Guarda el gráfico actual y retorna la ruta."""
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return str(filepath)

    def _prepare_financial_data(self, start_date: str, end_date: str) -> Dict:
        """Prepara datos para gráficos financieros."""
        cash_flow = finance_reports.get_cash_flow(start_date, end_date)
        return cash_flow

    def plot_sales_overview(self, start_date: str, end_date: str) -> str:
        """Genera gráfico de overview de ventas."""
        if not HAS_MATPLOTLIB:
            return "Matplotlib no disponible"

        cash_flow = self._prepare_financial_data(start_date, end_date)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Dashboard de Ventas y Finanzas', fontsize=16, fontweight='bold')

        sales = cash_flow.get('sales', [])
        if sales:
            sales_by_date = {}
            for sale in sales:
                date = sale['created_at'][:10]
                sales_by_date[date] = sales_by_date.get(date, 0) + sale['total']

            dates = sorted(sales_by_date.keys())
            amounts = [sales_by_date[d] for d in dates]

            axes[0, 0].bar(range(len(dates)), amounts, color='#3498db', alpha=0.7)
            axes[0, 0].set_title('Ventas por Día')
            axes[0, 0].set_xlabel('Fecha')
            axes[0, 0].set_ylabel('Monto (CRC)')
            axes[0, 0].tick_params(axis='x', rotation=45)

        income = cash_flow.get('income', {})
        expense = cash_flow.get('expenses', {})

        categories = ['Ingresos', 'Gastos']
        values = [income.get('total_sales', 0), expense.get('total_expenses', 0)]
        colors = ['#2ecc71', '#e74c3c']

        axes[0, 1].pie(values, labels=categories, colors=colors, autopct='%1.1f%%',
                       startangle=90, explode=(0.05, 0))
        axes[0, 1].set_title('Ingresos vs Gastos')

        labels = ['Ventas', 'Compras', 'Nómina']
        sizes = [income.get('total_sales', 0),
                expense.get('total_purchases', 0),
                expense.get('total_payroll', 0)]
        colors = ['#3498db', '#e74c3c', '#f39c12']

        axes[1, 0].bar(labels, sizes, color=colors, alpha=0.7)
        axes[1, 0].set_title('Desglose de Transacciones')
        axes[1, 0].set_ylabel('Monto (CRC)')
        for i, v in enumerate(sizes):
            axes[1, 0].text(i, v + 100, f'{v:,.0f}', ha='center')

        cash_flow_value = cash_flow.get('cash_flow', 0)
        labels = ['Flujo de Caja']
        values = [cash_flow_value]
        colors = ['#2ecc71' if cash_flow_value >= 0 else '#e74c3c']

        axes[1, 1].bar(labels, values, color=colors, alpha=0.7)
        axes[1, 1].set_title('Flujo de Caja Neto')
        axes[1, 1].set_ylabel('Monto (CRC)')
        axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        plt.tight_layout()
        return self._save_plot(f'sales_overview_{datetime.now().strftime("%Y%m%d")}.png')

    def plot_inventory_status(self) -> str:
        """Genera gráfico del estado del inventario."""
        if not HAS_MATPLOTLIB:
            return "Matplotlib no disponible"

        products = self.db.CRUD('products', 'list', filters={'status': 'activo'})

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Estado del Inventario', fontsize=16, fontweight='bold')

        low_stock = [p for p in products if p['stock'] <= p['min_stock']]
        normal_stock = [p for p in products if p['stock'] > p['min_stock']]

        labels = ['Stock Bajo', 'Stock Normal']
        sizes = [len(low_stock), len(normal_stock)]
        colors = ['#e74c3c', '#2ecc71']

        axes[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   startangle=90, explode=(0.05, 0))
        axes[0].set_title('Estado del Inventario')

        if products:
            top_products = sorted(products, key=lambda x: x['stock'], reverse=True)[:10]
            names = [p['name'][:15] for p in top_products]
            stocks = [p['stock'] for p in top_products]
            mins = [p['min_stock'] for p in top_products]

            x = range(len(names))
            width = 0.35

            axes[1].bar(x, stocks, width, label='Stock Actual', color='#3498db', alpha=0.7)
            axes[1].bar([i + width for i in x], mins, width, label='Stock Mínimo',
                      color='#e74c3c', alpha=0.7)
            axes[1].set_ylabel('Cantidad')
            axes[1].set_title('Top 10 Productos por Stock')
            axes[1].set_xticks([i + width / 2 for i in x])
            axes[1].set_xticklabels(names, rotation=45, ha='right')
            axes[1].legend()

        plt.tight_layout()
        return self._save_plot(f'inventory_status_{datetime.now().strftime("%Y%m%d")}.png')

    def plot_employee_stats(self) -> str:
        """Genera gráfico de estadísticas de empleados."""
        if not HAS_MATPLOTLIB:
            return "Matplotlib no disponible"

        employees = self.db.CRUD('employees', 'list', filters={'status': 'activo'})

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Estadísticas de Recursos Humanos', fontsize=16, fontweight='bold')

        departments = {}
        for emp in employees:
            dept = emp.get('department', 'Sin departamento')
            departments[dept] = departments.get(dept, 0) + 1

        axes[0, 0].pie(departments.values(), labels=departments.keys(),
                      autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Empleados por Departamento')

        payroll_total = sum(emp['salary'] for emp in employees)
        axes[0, 1].bar(['Total Nómina'], [payroll_total], color='#3498db', alpha=0.7)
        axes[0, 1].set_title('Costo Total de Nómina')
        axes[0, 1].set_ylabel('Monto (CRC)')
        axes[0, 1].text(0, payroll_total + 100, f'{payroll_total:,.0f}', ha='center')

        positions = {}
        for emp in employees:
            pos = emp.get('position', 'Sin puesto')
            positions[pos] = positions.get(pos, 0) + 1

        axes[1, 0].barh(list(positions.keys()), list(positions.values()),
                       color='#2ecc71', alpha=0.7)
        axes[1, 0].set_title('Empleados por Puesto')
        axes[1, 0].set_xlabel('Cantidad')

        salary_ranges = {'< 500': 0, '500-1000': 0, '1000-2000': 0, '> 2000': 0}
        for emp in employees:
            sal = emp['salary']
            if sal < 500:
                salary_ranges['< 500'] += 1
            elif sal < 1000:
                salary_ranges['500-1000'] += 1
            elif sal < 2000:
                salary_ranges['1000-2000'] += 1
            else:
                salary_ranges['> 2000'] += 1

        axes[1, 1].bar(salary_ranges.keys(), salary_ranges.values(),
                       color='#9b59b6', alpha=0.7)
        axes[1, 1].set_title('Distribución de Salarios')
        axes[1, 1].set_xlabel('Rango (CRC)')
        axes[1, 1].set_ylabel('Cantidad de Empleados')

        plt.tight_layout()
        return self._save_plot(f'employee_stats_{datetime.now().strftime("%Y%m%d")}.png')

    def plot_profit_loss(self, start_date: str, end_date: str) -> str:
        """Genera gráfico de pérdidas y ganancias."""
        if not HAS_MATPLOTLIB:
            return "Matplotlib no disponible"

        income_stmt = finance_reports.get_income_statement(start_date, end_date)

        fig, ax = plt.subplots(figsize=(12, 6))

        categories = ['Ingresos\nNetos', 'Costo de\nVentas', 'Utilidad\nBruta',
                     'Gastos\nOperativos', 'Utilidad\nNeta']
        values = [
            income_stmt['revenue']['net_revenue'],
            income_stmt['cost_of_sales'],
            income_stmt['gross_profit'],
            income_stmt['operating_expenses']['total'],
            income_stmt['net_profit']
        ]
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

        bars = ax.bar(categories, values, color=colors, alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=9)

        ax.set_title(f'Estado de Resultados ({start_date} - {end_date})',
                    fontsize=14, fontweight='bold')
        ax.set_ylabel('Monto (CRC)')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        if income_stmt['profit_margin'] > 0:
            ax.text(0.95, 0.95, f'Margen de Utilidad: {income_stmt["profit_margin"]:.1f}%',
                   transform=ax.transAxes, fontsize=12, verticalalignment='top',
                   horizontalalignment='right', bbox=dict(boxstyle='round',
                   facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        return self._save_plot(f'profit_loss_{datetime.now().strftime("%Y%m%d")}.png')

    def generate_executive_dashboard(self) -> Dict:
        """Genera un dashboard ejecutivo completo."""
        today = datetime.now()
        month_start = today.replace(day=1).strftime('%Y-%m-%d')
        month_end = today.strftime('%Y-%m-%d')

        cash_flow = finance_reports.get_cash_flow(month_start, month_end)
        inventory = self._get_inventory_summary()
        employees_data = self._get_employees_summary()
        alerts = self._get_pending_alerts()

        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'period': {'start': month_start, 'end': month_end},
            'financial': {
                'total_sales': cash_flow['income']['total_sales'],
                'total_expenses': cash_flow['expenses']['total_expenses'],
                'cash_flow': cash_flow['cash_flow'],
                'sales_count': cash_flow['income']['sales_count']
            },
            'inventory': inventory,
            'hr': employees_data,
            'alerts': alerts
        }

        return dashboard

    def _get_inventory_summary(self) -> Dict:
        """Resumen rápido del inventario."""
        products = self.db.CRUD('products', 'list', filters={'status': 'activo'})
        low_stock = [p for p in products if p['stock'] <= p['min_stock']]

        return {
            'total_products': len(products),
            'total_value': sum(p['cost'] * p['stock'] for p in products),
            'low_stock_count': len(low_stock),
            'low_stock_products': [{'name': p['name'], 'stock': p['stock'], 'min': p['min_stock']}
                                   for p in low_stock[:5]]
        }

    def _get_employees_summary(self) -> Dict:
        """Resumen rápido de empleados."""
        employees = self.db.CRUD('employees', 'list', filters={'status': 'activo'})

        return {
            'total_employees': len(employees),
            'total_payroll': sum(e['salary'] for e in employees),
            'by_department': self._count_by_field(employees, 'department')
        }

    def _count_by_field(self, items: List[Dict], field: str) -> Dict:
        """Cuenta elementos por campo."""
        counts = {}
        for item in items:
            value = item.get(field, 'N/A')
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _get_pending_alerts(self) -> List[Dict]:
        """Obtiene alertas pendientes."""
        alerts = self.db.CRUD('alerts', 'list',
                              filters={'status': 'pendiente'})
        return alerts[:10]

    def export_report_json(self, report_type: str, **kwargs) -> str:
        """Exporta un reporte a JSON."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if report_type == 'cash_flow':
            data = finance_reports.get_cash_flow(kwargs['start_date'], kwargs['end_date'])
        elif report_type == 'income_statement':
            data = finance_reports.get_income_statement(kwargs['start_date'], kwargs['end_date'])
        elif report_type == 'balance_sheet':
            data = finance_reports.get_balance_sheet()
        elif report_type == 'dashboard':
            data = self.generate_executive_dashboard()
        else:
            raise ValueError(f"Tipo de reporte desconocido: {report_type}")

        filepath = self.output_dir / f'{report_type}_{timestamp}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)

        return str(filepath)


reports = ReportGenerator()
