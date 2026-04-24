# Documentación Técnica - EnterpriseERP

## Sistema de Gestión Empresarial Integral

**Versión:** 1.0.0
**Fecha:** 2026
**Tecnología:** Python 100% Puro

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Base de Datos](#base-de-datos)
6. [Autenticación y Control de Acceso](#autenticación-y-control-de-acceso)
7. [API Reference](#api-reference)
8. [Instalación](#instalación)
9. [Configuración](#configuración)
10. [Diagramas](#diagramas)

---

## Introducción

### 1.1 Propósito del Sistema

EnterpriseERP es un sistema de planificación de recursos empresariales (ERP) desarrollado íntegramente en Python, diseñado para centralizar y optimizar la gestión de empresas de cualquier tamaño.

### 1.2 Características Principales

- **100% Python:** Sin dependencias externas para el núcleo del sistema
- **Multitenancy:** Soporte para múltiples empresas en una sola instalación
- **Interfaz Gráfica:** Aplicación de escritorio con Tkinter
- **Sistema de Roles:** Control de acceso granular basado en roles (RBAC)
- **Reportes Visuales:** Generación de gráficos y dashboards
- **Facturación:** Generación de facturas en PDF
- **Notificaciones:** Sistema de alertas por correo electrónico

### 1.3 Requisitos del Sistema

- Python 3.8 o superior
- Sistema operativo: Windows, macOS, Linux
- RAM mínima: 4 GB
- Espacio en disco: 100 MB

---

## Arquitectura del Sistema

### 2.1 Patrón de Diseño

El sistema utiliza una arquitectura **monolítica modular** con las siguientes características:

```
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE PRESENTACIÓN                     │
│                    (Interfaz Gráfica GUI)                    │
├─────────────────────────────────────────────────────────────┤
│                       CAPA DE SERVICIOS                      │
│  ┌──────────┬───────────┬──────────┬───────────┬──────────┐  │
│  │   RRHH  │ Inventario│ Finanzas │ Reportes  │Automación│  │
│  └──────────┴───────────┴──────────┴───────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      CAPA DE DATOS                          │
│                    (JSON Database Layer)                     │
├─────────────────────────────────────────────────────────────┤
│                    SISTEMA DE ARCHIVOS                       │
│                 (Almacenamiento JSON/CSV)                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes Principales

| Componente | Descripción | Responsabilidad |
|------------|-------------|-----------------|
| `database.py` | Capa de datos | Persistencia y CRUD genérico |
| `auth.py` | Autenticación | Login, logout, control de sesiones |
| `hr.py` | Recursos Humanos | Empleados, nómina, asistencia |
| `inventory.py` | Inventario | Productos, stock, categorías |
| `finance.py` | Finanzas | Ventas, compras, reportes |
| `reports.py` | Reportes | Gráficos y dashboards |
| `automation.py` | Automatización | Correos y notificaciones |
| `gui.py` | Interfaz | Aplicación Tkinter |

---

## Estructura del Proyecto

```
empresa_erp/
├── main.py                    # Punto de entrada
├── src/
│   ├── __init__.py           # Paquete principal
│   ├── database.py           # Sistema de base de datos
│   ├── gui.py                # Interfaz gráfica
│   └── modules/
│       ├── __init__.py       # Módulos del sistema
│       ├── auth.py           # Autenticación
│       ├── hr.py             # Recursos Humanos
│       ├── inventory.py      # Inventario
│       ├── finance.py        # Finanzas
│       ├── reports.py        # Reportes
│       └── automation.py     # Automatización
├── data/                      # Datos de la aplicación
│   ├── companies.json         # Metadatos de empresas
│   ├── company_XXXXX/         # Datos de cada empresa
│   │   ├── users.json
│   │   ├── employees.json
│   │   ├── products.json
│   │   └── ...
│   ├── reports/              # Reportes generados
│   └── exports/              # Exportaciones CSV/PDF
├── docs/                     # Documentación
└── brand/                    # Identidad corporativa
```

---

## Módulos del Sistema

### 4.1 Módulo de Base de Datos (`database.py`)

#### Clase: `Database`

Sistema de persistencia basado en archivos JSON con soporte para multitenancy.

**Métodos Principales:**

```python
# Gestión de empresas
create_company(name, rif, address, phone, email) -> Dict
get_companies() -> List[Dict]
init_company(company_id: str)
select_company(company_id: str)

# CRUD Genérico
CRUD(collection, operation, data, filters, record_id)

# backup y restore
backup_company(company_id) -> str
restore_company(backup_file) -> str

# Exportación
export_csv(collection) -> str
import_csv(collection, csv_file) -> int
```

**Colecciones Disponibles:**

| Colección | Descripción |
|-----------|-------------|
| `users` | Usuarios del sistema |
| `employees` | Datos de empleados |
| `attendance` | Registros de asistencia |
| `payroll` | Nóminas calculadas |
| `products` | Catálogo de productos |
| `categories` | Categorías de productos |
| `suppliers` | Proveedores |
| `sales` | Registro de ventas |
| `purchases` | Registro de compras |
| `invoices` | Facturas generadas |

---

### 4.2 Módulo de Autenticación (`auth.py`)

#### Clase: `AuthSystem`

Sistema de control de acceso basado en roles (RBAC).

**Roles Disponibles:**

| Rol | Nivel | Permisos |
|-----|-------|----------|
| `admin` | 3 | Acceso total al sistema |
| `gerente` | 2 | Ventas, compras, inventario, reportes |
| `empleado` | 1 | Solo nómina propia y asistencia |

**Ejemplo de Uso:**

```python
from src.modules.auth import auth

# Registrar empresa con admin
auth.register_admin({
    'name': 'Mi Empresa C.A.',
    'rif': 'J-12345678-9',
    'admin_username': 'admin',
    'admin_password': 'password123'
})

# Iniciar sesión
session = auth.login(company_id, 'admin', 'password123')

# Verificar permisos
if auth.has_permission('read_inventory'):
    # Acceso concedido
    pass
```

---

### 4.3 Módulo de Recursos Humanos (`hr.py`)

#### Clases:

- `EmployeeManager`: Gestión de empleados
- `PayrollManager`: Cálculo de nóminas
- `AttendanceManager`: Control de asistencia

**Gestión de Empleados:**

```python
from src.modules.hr import employees

# Crear empleado
emp = employees.create_employee({
    'first_name': 'Juan',
    'last_name': 'Pérez',
    'document_number': 'V-12345678',
    'department': 'Ventas',
    'position': 'Vendedor',
    'salary': 800.00
})

# Listar empleados
all_employees = employees.list_employees()

# Buscar por nombre
results = employees.search_employees('Juan')
```

**Cálculo de Nómina:**

```python
from src.modules.hr import payroll

# Calcular salario neto
nomina = payroll.calculate_net_salary(
    employee_id='emp123',
    period='mensual',
    bonuses=100.00,
    commissions=50.00,
    overtime_hours=10
)

# Generar nómina del período
payroll_records = payroll.generate_payroll(
    period='mensual',
    department='Ventas'
)
```

**Control de Asistencia:**

```python
from src.modules.hr import attendance

# Registrar entrada
attendance.check_in(employee_id='emp123')

# Registrar salida
attendance.check_out(employee_id='emp123', notes='Cierre de jornada')

# Solicitar vacaciones
attendance.request_vacation(employee_id='emp123', data={
    'start_date': '2026-05-01',
    'end_date': '2026-05-07',
    'reason': 'Vacaciones anuales'
})

# Reporte de asistencia
report = attendance.get_attendance_report(
    start_date='2026-04-01',
    end_date='2026-04-30'
)
```

---

### 4.4 Módulo de Inventario (`inventory.py`)

#### Clases:

- `CategoryManager`: Categorías de productos
- `SupplierManager`: Gestión de proveedores
- `ProductManager`: Control de inventario

**Gestión de Productos:**

```python
from src.modules.inventory import products, categories, suppliers

# Crear categoría
cat = categories.create_category({
    'name': 'Electrónica',
    'description': 'Productos electrónicos'
})

# Crear proveedor
sup = suppliers.create_supplier({
    'name': 'Distribuidora ABC',
    'email': 'ventas@abc.com',
    'phone': '+58 212 555-1234'
})

# Crear producto
prod = products.create_product({
    'name': 'Laptop HP 15"',
    'sku': 'LAP-HP-001',
    'category_id': cat['id'],
    'supplier_id': sup['id'],
    'cost': 450.00,
    'price': 650.00,
    'stock': 10,
    'min_stock': 5
})

# Entrada de mercancía
products.stock_entry(
    product_id=prod['id'],
    quantity=20,
    notes='Reabastecimiento',
    reference='OC-2026-001'
)

# Salida de mercancía
products.stock_output(
    product_id=prod['id'],
    quantity=5,
    notes='Venta',
    reference='F-2026-001'
)

# Verificar stock bajo
low_stock = products.get_low_stock_products()

# Valoración del inventario
valuation = products.get_inventory_valuation()
```

---

### 4.5 Módulo de Finanzas (`finance.py`)

#### Clases:

- `SalesManager`: Gestión de ventas
- `PurchasesManager`: Gestión de compras
- `InvoiceGenerator`: Generación de facturas
- `FinanceReports`: Reportes financieros

**Gestión de Ventas:**

```python
from src.modules.finance import sales, invoices

# Crear venta
sale = sales.create_sale({
    'customer_name': 'Cliente Ejemplo',
    'customer_rif': 'V-98765432-1',
    'items': [
        {'product_id': 'prod123', 'quantity': 2},
        {'product_id': 'prod456', 'quantity': 1}
    ],
    'payment_method': 'efectivo'
})

# Generar factura PDF
pdf_path = invoices.generate_invoice(sale['id'])

# Listar ventas
all_sales = sales.list_sales()

# Cancelar venta
sales.cancel_sale(sale_id='sale123', reason='Cliente solicitante')
```

**Reportes Financieros:**

```python
from src.modules.finance import reports

# Flujo de caja
cash_flow = reports.get_cash_flow('2026-04-01', '2026-04-30')

# Estado de resultados
income_stmt = reports.get_income_statement('2026-04-01', '2026-04-30')

# Balance general
balance = reports.get_balance_sheet()

# Resumen de ventas
summary = reports.get_sales_summary()
```

---

### 4.6 Módulo de Reportes (`reports.py`)

#### Clase: `ReportGenerator`

Generación de gráficos y dashboards visuales.

**Gráficos Disponibles:**

```python
from src.modules.reports import reports

# Dashboard de ventas
sales_chart = reports.plot_sales_overview('2026-04-01', '2026-04-30')

# Estado del inventario
inventory_chart = reports.plot_inventory_status()

# Estadísticas de empleados
hr_chart = reports.plot_employee_stats()

# Estado de resultados
profit_chart = reports.plot_profit_loss('2026-04-01', '2026-04-30')

# Dashboard ejecutivo
dashboard = reports.generate_executive_dashboard()

# Exportar a JSON
json_report = reports.export_report_json('cash_flow', start_date='2026-04-01', end_date='2026-04-30')
```

---

### 4.7 Módulo de Automatización (`automation.py`)

#### Clases:

- `EmailConfig`: Configuración SMTP
- `EmailSender`: Envío de correos
- `NotificationSystem`: Sistema de notificaciones

**Configuración de Correo:**

```python
from src.modules.automation import email_config, email_sender

# Configurar servidor SMTP
email_config.configure(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    sender_email='tu-correo@gmail.com',
    sender_password='tu-password',
    use_tls=True
)

# Guardar configuración
email_config.save_config()

# Enviar correo individual
email_sender.send_email(
    to_email='destinatario@ejemplo.com',
    subject='Asunto del correo',
    body='Contenido del mensaje',
    html_body='<p>Contenido HTML</p>'
)

# Envío masivo
email_sender.send_mass_email(
    recipients=[
        {'email': 'user1@ejemplo.com', 'name': 'Usuario 1'},
        {'email': 'user2@ejemplo.com', 'name': 'Usuario 2'}
    ],
    subject='Correo masivo',
    body_template='Hola {name}, este es un mensaje de prueba.'
)
```

---

## Base de Datos

### 5.1 Modelo de Datos

#### Empresas
```json
{
  "id": "abc12345",
  "name": "Empresa Demo C.A.",
  "rif": "J-12345678-9",
  "address": "Dirección de la empresa",
  "phone": "+58 212 123-4567",
  "email": "info@empresa.com",
  "created_at": "2026-04-17T10:00:00",
  "active": true
}
```

#### Usuarios
```json
{
  "id": "user001",
  "username": "admin",
  "password_hash": "sha256_hash",
  "role": "admin",
  "employee_id": "emp001",
  "full_name": "Administrador",
  "email": "admin@empresa.com",
  "created_at": "2026-04-17T10:00:00",
  "last_login": null,
  "active": true
}
```

#### Empleados
```json
{
  "id": "emp001",
  "first_name": "Juan",
  "last_name": "Pérez",
  "document_type": "DNI",
  "document_number": "V-12345678",
  "email": "juan@empresa.com",
  "department": "Ventas",
  "position": "Vendedor",
  "hire_date": "2026-01-15",
  "salary": 800.00,
  "status": "activo"
}
```

#### Productos
```json
{
  "id": "prod001",
  "sku": "LAP001",
  "name": "Laptop HP 15\"",
  "category_id": "cat001",
  "cost": 450.00,
  "price": 650.00,
  "stock": 15,
  "min_stock": 5,
  "status": "activo"
}
```

---

## Autenticación y Control de Acceso

### 6.1 Sistema RBAC

El sistema implementa Control de Acceso Basado en Roles (Role-Based Access Control):

```
        ┌─────────┐
        │  ADMIN  │ ◄─── Acceso total
        └────┬────┘
             │
        ┌────┴────┐
        │ GERENTE │ ◄─── Lectura/Escritura operativa
        └────┬────┘
             │
        ┌────┴────┐
        │EMPLEADO │ ◄─── Solo datos propios
        └─────────┘
```

### 6.2 Permisos por Rol

| Recurso | Admin | Gerente | Empleado |
|---------|-------|--------|----------|
| Usuarios | CRUD | - | - |
| Empleados | CRUD | CRUD | R (propio) |
| Nómina | CRUD | R | R (propia) |
| Asistencia | CRUD | CRUD | RU (propia) |
| Inventario | CRUD | CRUD | R |
| Ventas | CRUD | CRUD | - |
| Compras | CRUD | CRUD | - |
| Reportes | CRUD | R | R (limitado) |

---

## API Reference

### Métodos Comunes

#### Database.CRUD()

```python
# Crear registro
db.CRUD('collection', 'create', data={'key': 'value'})

# Leer registros
db.CRUD('collection', 'list', filters={'status': 'activo'})

# Leer un registro
db.CRUD('collection', 'find', record_id='id123')

# Actualizar registro
db.CRUD('collection', 'update', data={'key': 'new_value'}, record_id='id123')

# Eliminar registro
db.CRUD('collection', 'delete', record_id='id123')
```

---

## Instalación

### Requisitos Previos
- Python 3.8 o superior

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd empresa_erp
```

2. **Verificar Python**
```bash
python --version
```

3. **Iniciar la aplicación**
```bash
python main.py
```

4. **Inicializar datos de demostración (opcional)**
```bash
python main.py --init
```

---

## Configuración

### 7.1 Configuración de Correo

Editar `src/modules/automation.py` o usar el método `email_config.configure()`.

### 7.2 Estructura de Datos

Los datos se almacenan en la carpeta `data/` con el siguiente formato:
- `data/companies.json` - Metadatos de empresas
- `data/company_{id}/` - Datos individuales por empresa

### 7.3 Respaldo

```python
from src.database import db

# Crear respaldo
backup_path = db.backup_company(company_id)

# Restaurar desde respaldo
db.restore_company(backup_path)
```

---

## Diagramas

### Diagrama de Casos de Uso

```
┌─────────────────────────────────────────────────────────────┐
│                    Sistema EnterpriseERP                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐                                                │
│  │ Admin   │                                                │
│  └───┬─────┘                                                │
│      │                                                      │
│  ┌───┴───────────────────────┐                              │
│  │                           │                              │
│  ├─ Gestionar Usuarios       │                              │
│  ├─ Gestionar Empleados      │                              │
│  ├─ Gestionar Inventario     │                              │
│  ├─ Gestionar Ventas         │                              │
│  ├─ Gestionar Compras        │                              │
│  ├─ Ver Reportes             │                              │
│  ├─ Configurar Sistema       │                              │
│  └───────────────────────────┘                              │
│                                                              │
│  ┌─────────┐                                                │
│  │ Gerente │                                                │
│  └───┬─────┘                                                │
│      │                                                      │
│  ┌───┴───────────────────────┐                              │
│  │                           │                              │
│  ├─ Ver Empleados            │                              │
│  ├─ Procesar Nómina          │                              │
│  ├─ Control Asistencia       │                              │
│  ├─ Gestionar Inventario     │                              │
│  ├─ Registrar Ventas         │                              │
│  ├─ Registrar Compras        │                              │
│  └─ Ver Reportes             │                              │
│                                                              │
│  ┌─────────┐                                                │
│  │Empleado │                                                │
│  └───┬─────┘                                                │
│      │                                                      │
│  ┌───┴───────────────────────┐                              │
│  │                           │                              │
│  ├─ Ver Mi Perfil            │                              │
│  ├─ Ver Mi Nómina           │                              │
│  ├─ Marcar Asistencia       │                              │
│  └─ Solicitar Vacaciones     │                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Licencia

Este proyecto es software libre bajo la licencia MIT.

---

**EnterpriseERP** - Potenciando empresas con tecnología Python.
