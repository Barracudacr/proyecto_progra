# 🐍 EnterpriseERP

### Sistema de Gestión Empresarial Integral

*Potenciando empresas con tecnología Python*

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-100%25-blue?style=for-the-badge" alt="Python 100%">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange?style=for-the-badge" alt="Version 1.0">
</p>

---

## 📋 Tabla de Contenidos

- [Acerca de](#-acerca-de)
- [Características](#-características)
- [Primeros Pasos](#-primeros-pasos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Módulos del Sistema](#-módulos-del-sistema)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Tecnologías](#-tecnologías)
- [Documentación](#-documentación)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## 🔍 Acerca de

EnterpriseERP es un sistema de planificación de recursos empresariales (ERP) desarrollado **100% en Python**, diseñado para centralizar y optimizar la gestión de empresas de cualquier tamaño.

### ¿Por qué EnterpriseERP?

| Ventaja | Descripción |
|---------|-------------|
| 💯 **100% Python** | Sin dependencias externas costosas |
| 🚀 **Implementación Rápida** | Listo en minutos, no en meses |
| 💰 **Bajo Costo** | Sin licencias, sin mensualidades |
| 🔒 **Seguro** | Control de acceso y respaldos automáticos |
| 📊 **Reportes Visuales** | Dashboard y gráficos en tiempo real |
| 🏢 **Multiempresa** | Soporta múltiples empresas |

---

## ✨ Características

### Módulos Principales

| Módulo | Descripción |
|--------|-------------|
| **RRHH** | Gestión de empleados, nómina y asistencia |
| **Inventario** | Control de productos, stock y alertas |
| **Finanzas** | Ventas, compras y facturación |
| **Reportes** | Dashboard ejecutivo y exportación de datos |
| **Automatización** | Notificaciones por correo electrónico |

### Funcionalidades Avanzadas

- ✅ Sistema de autenticación con roles (Admin, Gerente, Empleado)
- ✅ Multitenancy: Aislamiento total de datos por empresa
- ✅ CRUD completo para todas las entidades
- ✅ Cálculo automático de nómina con deducciones
- ✅ Control de stock con alertas de reabastecimiento
- ✅ Generación de facturas en PDF
- ✅ Reportes financieros con gráficos
- ✅ Exportación a CSV y JSON
- ✅ Copias de seguridad automáticas
- ✅ Interfaz gráfica intuitiva

---

## 🚀 Primeros Pasos

### Requisitos

- Python 3.8 o superior
- Sistema operativo: Windows, macOS, Linux

### Instalación

```bash
# 1. Clonar o descargar el proyecto
cd empresa_erp

# 2. (Opcional) Instalar dependencias avanzadas
pip install reportlab matplotlib numpy pandas

# 3. Iniciar la aplicación
python main.py
```

### Datos de Demostración

```bash
# Generar datos de prueba
python main.py --init
```

**Credenciales de prueba:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 📁 Estructura del Proyecto

```
empresa_erp/
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias opcionales
├── README.md                  # Este archivo
│
├── src/
│   ├── __init__.py           # Paquete principal
│   ├── database.py           # Sistema de base de datos
│   ├── gui.py                # Interfaz gráfica
│   │
│   └── modules/
│       ├── __init__.py       # Módulos
│       ├── auth.py           # Autenticación
│       ├── hr.py             # Recursos Humanos
│       ├── inventory.py      # Inventario
│       ├── finance.py        # Finanzas
│       ├── reports.py        # Reportes
│       └── automation.py     # Automatización
│
├── data/                     # Datos de la aplicación
│   ├── companies.json
│   └── company_*/
│
├── docs/                     # Documentación
│   ├── Documentacion_Tecnica.md
│   └── Manual_de_Usuario.md
│
└── brand/                    # Identidad corporativa
    ├── Brand_Book.md
    └── Marketing_Kit.md
```

---

## 🧩 Módulos del Sistema

### 1. Autenticación (`auth.py`)

```python
from src.modules.auth import auth

# Registrar empresa
auth.register_admin({
    'name': 'Mi Empresa C.A.',
    'admin_username': 'admin',
    'admin_password': 'password123'
})

# Iniciar sesión
session = auth.login(company_id, 'admin', 'password123')

# Verificar permisos
if auth.has_permission('read_inventory'):
    print("Acceso concedido")
```

### 2. Recursos Humanos (`hr.py`)

```python
from src.modules.hr import employees, payroll, attendance

# Gestionar empleados
emp = employees.create_employee({
    'first_name': 'Juan',
    'last_name': 'Pérez',
    'department': 'Ventas',
    'salary': 800
})

# Calcular nómina
nomina = payroll.calculate_net_salary(emp['id'])

# Marcar asistencia
attendance.check_in(emp['id'])
attendance.check_out(emp['id'])
```

### 3. Inventario (`inventory.py`)

```python
from src.modules.inventory import products

# Crear producto
prod = products.create_product({
    'name': 'Laptop HP',
    'sku': 'LAP001',
    'cost': 450,
    'price': 650,
    'stock': 10,
    'min_stock': 5
})

# Movimientos de stock
products.stock_entry(prod['id'], quantity=20)
products.stock_output(prod['id'], quantity=5)

# Verificar stock bajo
low_stock = products.get_low_stock_products()
```

### 4. Finanzas (`finance.py`)

```python
from src.modules.finance import sales, invoices, reports

# Registrar venta
sale = sales.create_sale({
    'customer_name': 'Cliente Ejemplo',
    'items': [
        {'product_id': 'prod123', 'quantity': 2}
    ]
})

# Generar factura
pdf_path = invoices.generate_invoice(sale['id'])

# Reportes financieros
cash_flow = reports.get_cash_flow('2026-04-01', '2026-04-30')
income_stmt = reports.get_income_statement('2026-04-01', '2026-04-30')
```

### 5. Reportes (`reports.py`)

```python
from src.modules.reports import reports

# Generar dashboard
dashboard = reports.generate_executive_dashboard()

# Gráficos
reports.plot_sales_overview('2026-04-01', '2026-04-30')
reports.plot_inventory_status()
reports.plot_employee_stats()

# Exportar a JSON
reports.export_report_json('cash_flow', start_date='2026-04-01', end_date='2026-04-30')
```

---

## 📸 Capturas de Pantalla

### Pantalla de Login
```
┌────────────────────────────────────────────┐
│                                            │
│              EnterpriseERP                 │
│     Sistema de Gestión Empresarial         │
│                                            │
│  Empresa: [Empresa Demo C.A.     ▼]        │
│  Usuario: [___________________]           │
│  Contraseña: [___________________]         │
│                                            │
│        [Iniciar Sesión]                   │
│                                            │
│   [Registrar Nueva Empresa]                │
│                                            │
└────────────────────────────────────────────┘
```

### Dashboard Ejecutivo
```
┌────────────────────────────────────────────────────────────────┐
│ EnterpriseERP          Empresa Demo | admin (admin) [Cerrar]   │
├─────────┬──────────────────────────────────────────────────────┤
│         │                                                      │
│Dashboard│  Dashboard Ejecutivo                                  │
│Empleados│                                                      │
│Nómina   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│Asistencia│ │ Ventas │ │ Gastos │ │ Flujo  │ │ Prods  │       │
│Inventario│ │125,000 │ │ 89,500 │ │ 35,500 │ │   48   │       │
│Ventas   │ └────────┘ └────────┘ └────────┘ └────────┘       │
│Compras  │                                                      │
│Reportes │  Alertas Recientes                                   │
│         │  • Laptop HP 15": Stock bajo (3/5)                  │
│         │  • Resma de Papel: Reponer inventario               │
└─────────┴──────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Lenguaje** | Python 3.8+ | Desarrollo principal |
| **Base de Datos** | JSON | Almacenamiento de datos |
| **GUI** | Tkinter | Interfaz gráfica |
| **Gráficos** | Matplotlib | Visualización de datos |
| **PDF** | ReportLab | Generación de facturas |
| **Email** | smtplib | Notificaciones automáticas |

### Sin Dependencias Externas

El sistema funciona **100% con bibliotecas estándar de Python**:

```python
# Bibliotecas estándar utilizadas
import json          # Almacenamiento de datos
import csv           # Exportación de datos
import hashlib       # Seguridad de contraseñas
import uuid          # Generación de IDs únicos
import datetime      # Manejo de fechas
import tkinter       # Interfaz gráfica
import smtplib       # Envío de correos
import ssl           # Seguridad de conexión
import pathlib       # Manejo de rutas
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [Documentación Técnica](docs/Documentacion_Tecnica.md) | Especificaciones técnicas completas |
| [Manual de Usuario](docs/Manual_de_Usuario.md) | Guía paso a paso para usuarios |
| [Brand Book](brand/Brand_Book.md) | Identidad visual y directrices |
| [Marketing Kit](brand/Marketing_Kit.md) | Materiales promocionales |

---

## 🤝 Contribución

¡Contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -m 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📬 Contacto

- **Website:** [www.enterpriseerp.com](https://www.enterpriseerp.com)
- **Email:** info@enterpriseerp.com
- **GitHub:** [github.com/enterpriseerp](https://github.com/enterpriseerp)

---

<p align="center">
  <strong>EnterpriseERP</strong> - Simplificando la gestión empresarial
  <br>
  Construido con ❤️ y Python
</p>
