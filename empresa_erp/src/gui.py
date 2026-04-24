"""
Interfaz Gr�fica del Sistema ERP
================================
Aplicaci�n de escritorio usando Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Optional
import uuid

from src.database import db
from src.modules.auth import auth
from src.modules.hr import employees, payroll, attendance
from src.modules.inventory import products, categories, suppliers
from src.modules.finance import sales, purchases, invoices, reports as finance_reports
from src.modules.reports import reports as report_generator
from src.modules.automation import notifications, email_config


class ERPApplication:
    """Aplicaci�n principal del ERP."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EnterpriseERP - Sistema de Gesti�n Empresarial")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)

        self.current_company = None
        self.current_user = None

        self._setup_styles()
        self._create_widgets()
        self._show_login_screen()

    def _setup_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10), padding=10)
        style.configure('Menu.TButton', font=('Arial', 11), padding=15)

    def _create_widgets(self):
        """Crea los widgets principales."""
        self.main_container = tk.Frame(self.root, bg='#f0f0f0')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.login_frame = None
        self.dashboard_frame = None
        self.content_frame = None

    def _clear_frame(self, frame):
        """Limpia todos los widgets de un frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    def _show_login_screen(self):
        """Muestra la pantalla de inicio de sesi�n."""
        self._clear_frame(self.main_container)

        login_container = tk.Frame(self.main_container, bg='#ffffff',
                                  bd=2, relief=tk.RAISED)
        login_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title = ttk.Label(login_container, text="EnterpriseERP",
                         style='Title.TLabel')
        title.pack(pady=20, padx=50)

        subtitle = ttk.Label(login_container,
                           text="Sistema de Gesti�n Empresarial")
        subtitle.pack(pady=(0, 30))

        ttk.Label(login_container, text="Empresa:").pack(pady=5)
        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(login_container,
                                         textvariable=self.company_var,
                                         state='readonly', width=30)
        self.company_combo.pack(pady=5)
        self._load_companies()

        ttk.Label(login_container, text="Usuario:").pack(pady=5)
        self.username_entry = ttk.Entry(login_container, width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(login_container, text="Contrase�a:").pack(pady=5)
        self.password_entry = ttk.Entry(login_container, show="*", width=30)
        self.password_entry.pack(pady=5)

        ttk.Button(login_container, text="Iniciar Sesi�n",
                  style='Action.TButton',
                  command=self._do_login).pack(pady=20)

        ttk.Button(login_container, text="Registrar Nueva Empresa",
                  command=self._show_register_company).pack(pady=(0, 10))

        self.username_entry.bind('<Return>', lambda e: self._do_login())
        self.password_entry.bind('<Return>', lambda e: self._do_login())

    def _load_companies(self):
        """Carga la lista de empresas en el combobox."""
        companies = db.get_companies()
        self.company_combo['values'] = [c['name'] for c in companies]
        if companies:
            self.company_combo.current(0)

    def _show_register_company(self):
        """Muestra el formulario de registro de empresa."""
        register_win = tk.Toplevel(self.root)
        register_win.title("Registrar Nueva Empresa")
        register_win.geometry("400x500")
        register_win.transient(self.root)
        register_win.grab_set()

        fields = ['name', 'cedula_juridica', 'address', 'phone', 'email']
        entries = {}

        ttk.Label(register_win, text="Datos de la Empresa",
                 style='Header.TLabel').pack(pady=10)

        field_labels = {
            'name': 'Nombre de la Empresa',
            'cedula_juridica': 'C�dula Jur�dica',
            'address': 'Direcci�n',
            'phone': 'Tel�fono',
            'email': 'Correo Electr�nico'
        }

        for field in fields:
            ttk.Label(register_win, text=field_labels.get(field, field.capitalize())+":").pack(pady=3)
            entries[field] = ttk.Entry(register_win, width=40)
            entries[field].pack(pady=3)

        ttk.Separator(register_win).pack(fill='x', pady=15)

        ttk.Label(register_win, text="Datos del Administrador",
                 style='Header.TLabel').pack(pady=5)

        admin_fields = ['admin_name', 'admin_username', 'admin_email']
        for field in admin_fields:
            ttk.Label(register_win, text=f"{field.replace('admin_', '').capitalize()}:").pack(pady=3)
            entries[field] = ttk.Entry(register_win, width=40)
            entries[field].pack(pady=3)

        ttk.Label(register_win, text="Contrase�a:").pack(pady=3)
        entries['admin_password'] = ttk.Entry(register_win, show="*", width=40)
        entries['admin_password'].pack(pady=3)

        def do_register():
            try:
                data = {k: v.get() for k, v in entries.items()}
                auth.register_admin(data)

                messagebox.showinfo("�xito", "Empresa registrada correctamente")
                register_win.destroy()
                self._load_companies()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(register_win, text="Registrar",
                  style='Action.TButton',
                  command=do_register).pack(pady=20)

    def _do_login(self):
        """Procesa el inicio de sesi�n."""
        company_name = self.company_var.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not all([company_name, username, password]):
            messagebox.showerror("Error", "Complete todos los campos")
            return

        companies = db.get_companies()
        company = next((c for c in companies if c['name'] == company_name), None)

        if not company:
            messagebox.showerror("Error", "Empresa no encontrada")
            return

        user = auth.login(company['id'], username, password)

        if user:
            self.current_company = company
            self.current_user = user
            self._show_dashboard()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def _show_dashboard(self):
        """Muestra el dashboard principal."""
        self._clear_frame(self.main_container)

        top_frame = tk.Frame(self.main_container, bg='#2c3e50', height=60)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        title = tk.Label(top_frame, text="EnterpriseERP",
                        font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        title.pack(side=tk.LEFT, padx=20)

        company_label = tk.Label(top_frame,
                                text=f"{self.current_company['name']} | {self.current_user['username']} ({self.current_user['role']})",
                                bg='#2c3e50', fg='white')
        company_label.pack(side=tk.RIGHT, padx=20)

        menu_frame = tk.Frame(self.main_container, bg='#34495e', width=200)
        menu_frame.pack(fill=tk.Y, side=tk.LEFT)
        menu_frame.pack_propagate(False)

        buttons = [
            ("Dashboard", self._show_main_dashboard),
            ("Empleados", self._show_employees),
            ("N�mina", self._show_payroll),
            ("Asistencia", self._show_attendance),
            ("Inventario", self._show_inventory),
            ("Productos", self._show_products),
            ("Ventas", self._show_sales),
            ("Compras", self._show_purchases),
            ("Reportes", self._show_reports),
            ("Cerrar Sesi�n", self._logout)
        ]

        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, command=command,
                           bg='#34495e', fg='white', relief='flat',
                           font=('Arial', 10), anchor='w', padx=20, pady=10)
            btn.pack(fill=tk.X, pady=1)

        self.content_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self._show_main_dashboard()

    def _logout(self):
        """Cierra la sesi�n."""
        auth.logout()
        self.current_company = None
        self.current_user = None
        self._show_login_screen()

    def _show_main_dashboard(self):
        """Muestra el dashboard principal."""
        self._clear_frame(self.content_frame)

        db.select_company(self.current_company['id'])
        dashboard = report_generator.generate_executive_dashboard()

        total_sales = 0.0
        total_expenses = 0.0
        cash_flow = 0.0

        try:
            sales_list = sales.list_sales()
            for s in sales_list:
                if s.get('status') == 'completada':
                    total_sales += s.get('total', 0)
        except:
            pass

        try:
            purchases_list = purchases.list_purchases()
            for p in purchases_list:
                if p.get('status') == 'recibida':
                    total_expenses += p.get('total', 0)
        except:
            pass

        try:
            emp_list = employees.list_employees()
            total_expenses += sum(e.get('salary', 0) for e in emp_list if e.get('status') == 'activo')
        except:
            pass

        try:
            movements = db.CRUD('inventory_movements', 'list')
            for m in movements:
                if m.get('type') == 'entrada':
                    pass
                elif m.get('type') == 'salida':
                    prod = products.get_product(product_id=m.get('product_id'))
                    if prod:
                        total_expenses += prod.get('cost', 0) * m.get('quantity', 0)
        except:
            pass

        try:
            reposiciones = db.CRUD('costs', 'list')
            for r in reposiciones:
                total_expenses += r.get('total_cost', 0)
        except:
            pass

        cash_flow = total_sales - total_expenses

        header = tk.Label(self.content_frame, text="Dashboard Ejecutivo",
                         font=('Arial', 18, 'bold'), bg='#f0f0f0')
        header.pack(pady=10)

        cards_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        cards_frame.pack(pady=20)

        cards = [
            ("Ventas", f"CRC {total_sales:,.2f}", '#3498db'),
            ("Gastos", f"CRC {total_expenses:,.2f}", '#e74c3c'),
            ("Flujo de Caja", f"CRC {cash_flow:,.2f}", '#2ecc71'),
            ("Productos", str(dashboard['inventory']['total_products']), '#9b59b6'),
            ("Empleados", str(dashboard['hr']['total_employees']), '#f39c12'),
            ("Alertas", str(len(dashboard['alerts'])), '#e67e22')
        ]

        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(cards_frame, bg=color, width=180, height=100)
            card.grid(row=0, column=i, padx=10, pady=10)
            card.pack_propagate(False)

            tk.Label(card, text=title, bg=color, fg='white',
                    font=('Arial', 10)).pack(pady=(15, 5))
            tk.Label(card, text=value, bg=color, fg='white',
                    font=('Arial', 14, 'bold')).pack()

        self._show_beautiful_alerts(dashboard['alerts'])

    def _show_beautiful_alerts(self, alerts):
        """Muestra alertas con estilo visual attractive usando tkinter."""
        alerts_container = tk.Frame(self.content_frame, bg='#f0f0f0')
        alerts_container.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        header_label = tk.Label(alerts_container, text="Alertas del Sistema",
                           font=('Arial', 14, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        header_label.pack(pady=(0, 15))

        if not alerts or len(alerts) == 0:
            no_alerts_frame = tk.Frame(alerts_container, bg='#ffffff', bd=2, relief=tk.RAISED)
            no_alerts_frame.pack(fill=tk.X, pady=10)

            tk.Label(no_alerts_frame, text="No hay alertas pendientes",
                   font=('Arial', 11), bg='#ffffff', fg='#27ae60',
                   padx=40, pady=20).pack()
            return

        for i, alert in enumerate(alerts[:8]):
            alert_type = alert.get('type', 'general')
            product_name = alert.get('product_name', 'Producto')
            alert_id = alert.get('id')

            btn_command = lambda a_id=alert_id: self._resolve_alert(a_id)

            if alert_type == 'low_stock':
                color_bg = '#ffebee'
                color_border = '#e74c3c'
                title = 'Stock Bajo'
                message = f'{product_name}: Stock actual {alert.get("current_stock", 0)} (minimo: {alert.get("min_stock", 0)})'
            else:
                color_bg = '#fff3e0'
                color_border = '#f39c12'
                title = 'Notificacion'
                message = str(alert)

            alert_frame = tk.Frame(alerts_container, bg=color_border, bd=0)
            alert_frame.pack(fill=tk.X, pady=6)

            inner_frame = tk.Frame(alert_frame, bg=color_bg, bd=1, relief=tk.FLAT)
            inner_frame.pack(fill=tk.X, padx=2, pady=2)

            text_frame = tk.Frame(inner_frame, bg=color_bg)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)

            tk.Label(text_frame, text=title,
                   font=('Arial', 10, 'bold'), bg=color_bg, fg='#c0392b').pack(anchor='w')

            tk.Label(text_frame, text=message,
                   font=('Arial', 9), bg=color_bg, fg='#2c3e50').pack(anchor='w')

            btn_frame = tk.Frame(inner_frame, bg=color_bg)
            btn_frame.pack(side=tk.RIGHT, padx=10)

            ttk.Button(btn_frame, text="Resolver",
                     command=btn_command).pack()

    def _resolve_alert(self, alert_id):
        """Marca una alerta como resuelta."""
        try:
            db.CRUD('alerts', 'update',
                   data={'status': 'resuelta', 'resolved_at': datetime.now().isoformat()},
                   record_id=alert_id)
            messagebox.showinfo("Exito", "Alerta marcada como resuelta")
            self._show_main_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_employees(self):
        """Muestra la gesti�n de empleados."""
        self._clear_frame(self.content_frame)

        header = tk.Label(self.content_frame, text="Gestion de Empleados",
                         font=('Arial', 18, 'bold'), bg='#f0f0f0')
        header.pack(pady=10)

        btn_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        if auth.has_role('gerente') or auth.has_permission('*'):
            ttk.Button(btn_frame, text="+ Nuevo Empleado",
                      command=self._add_employee).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('ID', 'Nombre', 'Departamento', 'Puesto', 'Salario', 'Estado')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.employees_tree = tree
        self.employees_data = []

        try:
            emp_list = employees.list_employees()
            self.employees_data = emp_list

            for i, emp in enumerate(emp_list):
                tree.insert('', tk.END, values=(
                    emp['id'],
                    f"{emp['first_name']} {emp['last_name']}",
                    emp.get('department', ''),
                    emp.get('position', ''),
                    f"CRC {emp['salary']:.2f}",
                    emp.get('status', 'activo')
                ), tags=('emp', str(i)))

            if auth.has_role('gerente') or auth.has_permission('*'):
                tree.tag_bind('emp', '<Double-Button-1>', self._on_employee_action)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_employee_action(self, event):
        item_id = self.employees_tree.selection()
        if not item_id:
            return
        item = self.employees_tree.item(item_id)
        values = item['values']
        if not values:
            return
        emp_id = values[0]
        emp = next((e for e in self.employees_data if e['id'] == emp_id), None)
        if emp:
            self._eliminar_empleado(emp)

    def _eliminar_empleado(self, emp):
        confirm = messagebox.askyesno("Confirmar",
            f"Esta seguro de eliminar al empleado {emp.get('first_name')} {emp.get('last_name')}?")
        if confirm:
            try:
                employees.delete_employee(emp['id'])
                messagebox.showinfo("Exito", "Empleado eliminado")
                self._show_employees()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _add_employee(self):
        """Formulario para agregar empleado."""
        win = tk.Toplevel(self.root)
        win.title("Nuevo Empleado")
        win.geometry("400x600")
        win.transient(self.root)
        win.grab_set()

        fields = ['first_name', 'last_name', 'document_number', 'email',
                  'phone', 'department', 'position', 'salary']
        entries = {}

        for i, field in enumerate(fields):
            ttk.Label(win, text=f"{field.replace('_', ' ').capitalize()}:").grid(
                row=i, column=0, sticky='w', padx=10, pady=5)
            entries[field] = ttk.Entry(win, width=30)
            entries[field].grid(row=i, column=1, padx=10, pady=5)

        def save():
            try:
                data = {k: v.get() for k, v in entries.items()}
                employees.create_employee(data)
                messagebox.showinfo("�xito", "Empleado creado")
                win.destroy()
                self._show_employees()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Guardar", command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=20)

    def _show_payroll(self):
        """Muestra la gesti�n de n�mina."""
        self._clear_frame(self.content_frame)

        header = tk.Label(self.content_frame, text="Gesti�n de N�mina",
                         font=('Arial', 18, 'bold'), bg='#f0f0f0')
        header.pack(pady=10)

        if auth.has_role('gerente') or auth.has_permission('*'):
            ttk.Button(self.content_frame, text="Generar N�mina",
                      command=self._generate_payroll).pack(pady=10)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('ID', 'Empleado', 'Per�odo', 'Salario Base', 'Deducciones', 'Neto')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        try:
            history = payroll.get_payroll_history()
            for entry in history:
                details = entry.get('details', {})
                tree.insert('', tk.END, values=(
                    entry['id'],
                    details.get('employee_name', ''),
                    entry.get('period', ''),
                    f"CRC {details.get('base_salary', 0):.2f}",
                    f"CRC {details.get('deductions', {}).get('total', 0):.2f}",
                    f"CRC {details.get('net_salary', 0):.2f}"
                ))
        except Exception as e:
            tk.Label(self.content_frame, text=str(e), fg='red').pack()

    def _generate_payroll(self):
        """Genera la n�mina mensual."""
        try:
            payroll.generate_payroll('mensual')
            messagebox.showinfo("�xito", "N�mina generada")
            self._show_payroll()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_attendance(self):
        """Muestra el control de asistencia."""
        self._clear_frame(self.content_frame)

        header = tk.Label(self.content_frame, text="Control de Asistencia",
                         font=('Arial', 18, 'bold'), bg='#f0f0f0')
        header.pack(pady=10)

        btn_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        info_label = tk.Label(btn_frame,
                           text="Empleado actual: " + self.current_user.get('username', 'Unknown'),
                           font=('Arial', 10), bg='#f0f0f0')
        info_label.pack(pady=5)

        ttk.Button(btn_frame, text="Marcar Entrada",
                   command=self._check_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Marcar Salida",
                   command=self._check_out).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('Fecha', 'Entrada', 'Salida', 'Horas', 'Estado')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        today = datetime.now().strftime('%Y-%m-%d')
        month_start = datetime.now().strftime('%Y-01-01')

        try:
            employee_id = self.current_user.get('employee_id')
            if not employee_id:
                all_records = db.CRUD('attendance', 'list', filters={})
            else:
                all_records = db.CRUD('attendance', 'list', filters={'employee_id': employee_id})

            month_records = [r for r in all_records
                         if r.get('date', '').startswith(datetime.now().strftime('%Y-'))]

            if not month_records and employee_id:
                month_records = db.CRUD('attendance', 'list', filters={})

            for rec in month_records:
                if rec.get('date', '').startswith(datetime.now().strftime('%Y-%m-')):
                    entry_time = rec.get('entry_time', '-')
                    exit_time = rec.get('exit_time', '-')
                    hours = rec.get('hours_worked', 0)
                    state = rec.get('status', 'completo')
                    tree.insert('', tk.END, values=(
                        rec.get('date', ''), entry_time, exit_time, f"{hours:.1f}", state
                    ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _check_in(self):
        """Registrar entrada."""
        try:
            employee_id = self.current_user.get('employee_id')
            if not employee_id:
                messagebox.showwarning("Advertencia", "Usuario sin empleado asociado")
                return
            today = datetime.now().strftime('%Y-%m-%d')
            existing = db.CRUD('attendance', 'list', filters={
                'employee_id': employee_id, 'date': today
            })
            if existing:
                messagebox.showinfo("Info", "Ya hay registro para hoy")
                return
            db.CRUD('attendance', 'create', data={
                'employee_id': employee_id,
                'date': today,
                'entry_time': datetime.now().strftime('%H:%M:%S'),
                'status': 'presente'
            })
            messagebox.showinfo("Exito", "Entrada registrada")
            self._show_attendance()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _check_out(self):
        """Registrar salida."""
        try:
            employee_id = self.current_user.get('employee_id')
            if not employee_id:
                messagebox.showwarning("Advertencia", "Usuario sin empleado asociado")
                return
            today = datetime.now().strftime('%Y-%m-%d')
            records = db.CRUD('attendance', 'list', filters={
                'employee_id': employee_id, 'date': today
            })
            if not records:
                messagebox.showwarning("Advertencia", "No hay entrada registrada hoy")
                return
            record = records[0]
            entry = datetime.strptime(record['entry_time'], '%H:%M:%S')
            exit_time = datetime.now()
            hours = (exit_time - entry).seconds / 3600
            db.CRUD('attendance', 'update', record_id=record['id'], data={
                'exit_time': exit_time.strftime('%H:%M:%S'),
                'hours_worked': hours,
                'status': 'completo'
            })
            messagebox.showinfo("Exito", "Salida registrada")
            self._show_attendance()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_reports(self):
        """Muestra informes."""
        self._clear_frame(self.content_frame)
        header = tk.Label(self.content_frame, text="Informes",
                         font=('Arial', 18, 'bold'), bg='#f0f0f0')
        header.pack(pady=10)
        ttk.Label(self.content_frame, text="Modulo de informes en desarrollo",
                 font=('Arial', 12)).pack(pady=20)
