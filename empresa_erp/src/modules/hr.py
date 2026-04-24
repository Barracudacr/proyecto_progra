"""
Módulo de Recursos Humanos (RRHH)
================================
Gestión completa de empleados, nóminas y asistencia.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.database import db
from src.modules.auth import auth


class EmployeeManager:
    """Gestor de empleados de la empresa."""

    def __init__(self):
        self.db = db

    def create_employee(self, data: Dict) -> Dict:
        """Crea un nuevo registro de empleado."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para crear empleados")

        employee = {
            'id': str(uuid.uuid4())[:12],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'document_type': data.get('document_type', 'DNI'),
            'document_number': data['document_number'],
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'birth_date': data.get('birth_date', ''),
            'gender': data.get('gender', ''),
            'department': data.get('department', ''),
            'position': data.get('position', ''),
            'hire_date': data.get('hire_date', datetime.now().strftime('%Y-%m-%d')),
            'salary': float(data.get('salary', 0)),
            'employee_type': data.get('employee_type', 'tiempo_completo'),
            'bank_account': data.get('bank_account', ''),
            'emergency_contact': data.get('emergency_contact', {}),
            'status': 'activo',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        return self.db.CRUD('employees', 'create', data=employee)

    def list_employees(self, filters: Dict = None) -> List[Dict]:
        """Lista empleados con filtros."""
        employees = self.db.CRUD('employees', 'list', filters=filters)

        if not auth.has_permission('*'):
            user = auth.get_session()
            if user['role'] == 'empleado':
                user_data = self.db.CRUD('users', 'find', record_id=user['user_id'])
                employee_id = user_data.get('employee_id')
                employees = [e for e in employees if e['id'] == employee_id]

        return employees

    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Obtiene datos de un empleado específico."""
        employee = self.db.CRUD('employees', 'find', record_id=employee_id)

        if not employee:
            return None

        if not auth.has_permission('*'):
            user = auth.get_session()
            if user['role'] == 'empleado':
                user_data = self.db.CRUD('users', 'find', record_id=user['user_id'])
                if user_data.get('employee_id') != employee_id:
                    raise PermissionError("No tiene acceso a este empleado")

        return employee

    def update_employee(self, employee_id: str, updates: Dict) -> Dict:
        """Actualiza datos de un empleado."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para actualizar empleados")

        return self.db.CRUD('employees', 'update', data=updates, record_id=employee_id)

    def delete_employee(self, employee_id: str) -> bool:
        """Desactiva un empleado (soft delete)."""
        if not auth.has_permission('*'):
            if not auth.has_role('admin'):
                raise PermissionError("Solo administradores pueden eliminar empleados")

        return self.db.CRUD('employees', 'update',
                           data={'status': 'inactivo', 'deleted_at': datetime.now().isoformat()},
                           record_id=employee_id)

    def search_employees(self, query: str) -> List[Dict]:
        """Busca empleados por nombre o documento."""
        return self.db.CRUD('employees', 'list',
                          filters={'search': query})

    def get_departments(self) -> List[str]:
        """Retorna lista de departamentos únicos."""
        employees = self.db.CRUD('employees', 'list')
        return list(set(e.get('department', '') for e in employees if e.get('department')))

    def get_positions(self) -> List[str]:
        """Retorna lista de puestos únicos."""
        employees = self.db.CRUD('employees', 'list')
        return list(set(e.get('position', '') for e in employees if e.get('position')))


class PayrollManager:
    """
    Gestor de nóminas y cálculo de salarios.
    Calcula salario neto considerando impuestos, deducciones y bonificaciones.
    """

    TAX_RATES = {
        'isr': 0.10,
        'seguro_social': 0.04,
        'seguro_educativo': 0.02,
        'paro_paro': 0.01
    }

    def __init__(self):
        self.db = db
        self.employee_mgr = EmployeeManager()

    def calculate_gross_salary(self, base_salary: float, bonuses: float = 0,
                              commissions: float = 0, overtime_hours: float = 0,
                              hourly_rate: float = 0) -> float:
        """
        Calcula el salario bruto incluyendo todos los conceptos.
        """
        overtime_pay = overtime_hours * hourly_rate * 1.5
        return base_salary + bonuses + commissions + overtime_pay

    def calculate_deductions(self, gross_salary: float) -> Dict:
        """
        Calcula todas las deducciones legales obligatorias.
        """
        deductions = {}
        deductions['isr'] = gross_salary * self.TAX_RATES['isr']
        deductions['seguro_social'] = gross_salary * self.TAX_RATES['seguro_social']
        deductions['seguro_educativo'] = gross_salary * self.TAX_RATES['seguro_educativo']
        deductions['paro_paro'] = gross_salary * self.TAX_RATES['paro_paro']
        deductions['total'] = sum(deductions.values())

        return deductions

    def calculate_net_salary(self, employee_id: str, period: str = 'mensual',
                            bonuses: float = 0, commissions: float = 0,
                            overtime_hours: float = 0) -> Dict:
        """
        Calcula el salario neto completo de un empleado.
        """
        employee = self.employee_mgr.get_employee(employee_id)
        if not employee:
            raise ValueError("Empleado no encontrado")

        base_salary = employee['salary']
        hourly_rate = base_salary / 160

        gross_salary = self.calculate_gross_salary(
            base_salary, bonuses, commissions, overtime_hours, hourly_rate
        )

        deductions = self.calculate_deductions(gross_salary)
        net_salary = gross_salary - deductions['total']

        return {
            'employee_id': employee_id,
            'employee_name': f"{employee['first_name']} {employee['last_name']}",
            'period': period,
            'base_salary': base_salary,
            'bonuses': bonuses,
            'commissions': commissions,
            'overtime_hours': overtime_hours,
            'overtime_pay': overtime_hours * hourly_rate * 1.5,
            'gross_salary': gross_salary,
            'deductions': deductions,
            'net_salary': net_salary,
            'calculated_at': datetime.now().isoformat()
        }

    def generate_payroll(self, period: str, department: str = None) -> List[Dict]:
        """
        Genera la nómina completa para un período.
        """
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para generar nóminas")

        filters = {'status': 'activo'}
        if department:
            filters['department'] = department

        employees = self.employee_mgr.list_employees(filters)
        payroll = []

        for emp in employees:
            payroll_entry = self.calculate_net_salary(emp['id'], period)
            payroll.append(payroll_entry)

            self.db.CRUD('payroll', 'create', data={
                'id': str(uuid.uuid4())[:12],
                'employee_id': emp['id'],
                'period': period,
                'details': payroll_entry,
                'status': 'calculado',
                'created_at': datetime.now().isoformat()
            })

        return payroll

    def pay_employee(self, payroll_id: str, payment_data: Dict) -> Dict:
        """Registra el pago de una nómina."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para registrar pagos")

        payroll_entry = self.db.CRUD('payroll', 'find', record_id=payroll_id)
        if not payroll_entry:
            raise ValueError("Entrada de nómina no encontrada")

        payment = {
            'id': str(uuid.uuid4())[:12],
            'payroll_id': payroll_id,
            'amount': payment_data['amount'],
            'payment_method': payment_data.get('payment_method', 'transferencia'),
            'reference': payment_data.get('reference', ''),
            'paid_at': datetime.now().isoformat(),
            'paid_by': auth.get_session()['user_id']
        }

        self.db.CRUD('payroll', 'update',
                    data={'status': 'pagado', 'payment': payment},
                    record_id=payroll_id)

        return payment

    def get_payroll_history(self, employee_id: str = None) -> List[Dict]:
        """Obtiene historial de nóminas."""
        filters = {}
        if employee_id:
            filters['employee_id'] = employee_id

        if not auth.has_permission('*'):
            user = auth.get_session()
            if user['role'] == 'empleado':
                user_data = self.db.CRUD('users', 'find', record_id=user['user_id'])
                filters['employee_id'] = user_data.get('employee_id')

        return self.db.CRUD('payroll', 'list', filters=filters)


class AttendanceManager:
    """Gestor de asistencia y control de horario."""

    def __init__(self):
        self.db = db

    def check_in(self, employee_id: str) -> Dict:
        """Registra entrada de un empleado."""
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now()

        existing = self.db.CRUD('attendance', 'list',
                               filters={'employee_id': employee_id, 'date': today})

        if existing:
            raise ValueError("Ya se registró la entrada hoy")

        record = {
            'employee_id': employee_id,
            'date': today,
            'check_in': current_time.strftime('%H:%M:%S'),
            'check_in_datetime': current_time.isoformat(),
            'status': 'presente',
            'created_at': datetime.now().isoformat()
        }

        return self.db.CRUD('attendance', 'create', data=record)

    def check_out(self, employee_id: str, notes: str = '') -> Dict:
        """Registra salida de un empleado."""
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now()

        records = self.db.CRUD('attendance', 'list',
                              filters={'employee_id': employee_id, 'date': today})

        if not records:
            raise ValueError("No hay registro de entrada para hoy")

        record = records[0]
        if record.get('check_out'):
            raise ValueError("Ya se registró la salida hoy")

        check_in_time = datetime.fromisoformat(record['check_in_datetime'])
        hours_worked = (current_time - check_in_time).total_seconds() / 3600

        return self.db.CRUD('attendance', 'update',
                           data={
                               'check_out': current_time.strftime('%H:%M:%S'),
                               'check_out_datetime': current_time.isoformat(),
                               'hours_worked': round(hours_worked, 2),
                               'notes': notes
                           },
                           record_id=record['id'])

    def request_vacation(self, employee_id: str, data: Dict) -> Dict:
        """Registra solicitud de vacaciones."""
        vacation = {
            'id': str(uuid.uuid4())[:12],
            'employee_id': employee_id,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'days_requested': data.get('days_requested', 0),
            'reason': data.get('reason', ''),
            'status': 'pendiente',
            'created_at': datetime.now().isoformat()
        }

        return self.db.CRUD('attendance', 'create', data=vacation)

    def approve_vacation(self, vacation_id: str) -> Dict:
        """Aprueba una solicitud de vacaciones."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para aprobar vacaciones")

        return self.db.CRUD('attendance', 'update',
                           data={
                               'status': 'aprobada',
                               'approved_at': datetime.now().isoformat(),
                               'approved_by': auth.get_session()['user_id']
                           },
                           record_id=vacation_id)

    def get_attendance_report(self, start_date: str, end_date: str,
                             employee_id: str = None) -> List[Dict]:
        """Genera reporte de asistencia para un período."""
        filters = {'date_from': start_date, 'date_to': end_date}
        if employee_id:
            filters['employee_id'] = employee_id

        records = self.db.CRUD('attendance', 'list', filters=filters)

        if not auth.has_permission('*'):
            user = auth.get_session()
            if user['role'] == 'empleado':
                user_data = self.db.CRUD('users', 'find', record_id=user['user_id'])
                records = [r for r in records
                          if r.get('employee_id') == user_data.get('employee_id')]

        return records

    def get_monthly_summary(self, employee_id: str, year: int, month: int) -> Dict:
        """Obtiene resumen mensual de asistencia."""
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"

        records = self.db.CRUD('attendance', 'list',
                              filters={'employee_id': employee_id,
                                      'date_from': start_date,
                                      'date_to': end_date})

        attendance_records = [r for r in records if 'check_in' in r]
        total_hours = sum(r.get('hours_worked', 0) for r in attendance_records)
        days_present = len(attendance_records)

        return {
            'employee_id': employee_id,
            'year': year,
            'month': month,
            'days_present': days_present,
            'total_hours': total_hours,
            'average_hours': round(total_hours / days_present, 2) if days_present > 0 else 0,
            'records': attendance_records
        }


employees = EmployeeManager()
payroll = PayrollManager()
attendance = AttendanceManager()
