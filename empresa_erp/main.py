#!/usr/bin/env python3
"""
EnterpriseERP - Punto de Entrada Principal
============================================

Sistema de Gestión Empresarial Integral
Construido 100% en Python - Sin dependencias externas

Uso:
    python main.py              - Iniciar aplicación gráfica
    python main.py --cli        - Iniciar interfaz de línea de comandos
    python main.py --init       - Inicializar base de datos de demo
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import db
from src.modules.auth import auth
from src.gui import ERPApplication


def init_demo_data():
    """Inicializa datos de demostración."""
    print("=" * 60)
    print("EnterpriseERP - Inicializando Datos de Demostración")
    print("=" * 60)

    demo_company = {
        'name': 'Empresa Demo S.A.',
        'cedula_juridica': '3-101-123456',
        'address': 'San José, Costa Rica',
        'phone': '+506 2222-3333',
        'email': 'info@empresademo.cr',
        'admin_name': 'Administrador',
        'admin_username': 'admin',
        'admin_password': 'admin123',
        'admin_email': 'admin@empresademo.cr'
    }

    print("\n[1/4] Creando empresa de demostración...")
    try:
        result = auth.register_admin(demo_company)
        print(f"    ✓ Empresa '{demo_company['name']}' creada")
        print(f"    ✓ Usuario admin: {demo_company['admin_username']}")
        print(f"    ✓ Contraseña: {demo_company['admin_password']}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return

    company_id = result['company']['id']
    db.select_company(company_id)

    print("\n[2/4] Agregando empleados de demostración...")
    from src.modules.hr import employees

    demo_employees = [
        {'first_name': 'Juan', 'last_name': 'Pérez', 'document_number': '1-2345-6789',
         'email': 'juan.perez@empresa.com', 'department': 'Ventas', 'position': 'Vendedor', 'salary': 800000},
        {'first_name': 'María', 'last_name': 'García', 'document_number': '2-3456-7890',
         'email': 'maria.garcia@empresa.com', 'department': 'Administración', 'position': 'Contador', 'salary': 1200000},
        {'first_name': 'Carlos', 'last_name': 'Rodríguez', 'document_number': '3-4567-8901',
         'email': 'carlos.rodriguez@empresa.com', 'department': 'Almacén', 'position': 'Almacenista', 'salary': 600000},
        {'first_name': 'Ana', 'last_name': 'Martínez', 'document_number': '4-5678-9012',
         'email': 'ana.martinez@empresa.com', 'department': 'Ventas', 'position': 'Gerente de Ventas', 'salary': 1500000},
        {'first_name': 'Luis', 'last_name': 'Hernández', 'document_number': '5-6789-0123',
         'email': 'luis.hernandez@empresa.com', 'department': 'Recursos Humanos', 'position': 'Gerente RRHH', 'salary': 1400000}
    ]

    for emp_data in demo_employees:
        try:
            emp = employees.create_employee(emp_data)
            auth.create_user(
                username=emp_data['first_name'].lower(),
                password='demo123',
                role='empleado',
                employee_id=emp['id'],
                full_name=f"{emp_data['first_name']} {emp_data['last_name']}",
                email=emp_data['email']
            )
            print(f"    ✓ {emp_data['first_name']} {emp_data['last_name']}")
        except Exception as e:
            print(f"    ✗ Error con {emp_data['first_name']}: {e}")

    print("\n[3/4] Agregando productos de demostración...")
    from src.modules.inventory import products, categories

    cat1 = categories.create_category({'name': 'Electrónica'})
    cat2 = categories.create_category({'name': 'Oficina'})
    cat3 = categories.create_category({'name': 'Papelería'})

    demo_products = [
        {'name': 'Laptop HP 15"', 'sku': 'LAP001', 'cost': 450, 'price': 650, 'stock': 15, 'min_stock': 5, 'category_id': cat1['id']},
        {'name': 'Mouse Inalámbrico', 'sku': 'MOU001', 'cost': 8, 'price': 15, 'stock': 50, 'min_stock': 10, 'category_id': cat1['id']},
        {'name': 'Teclado USB', 'sku': 'TEC001', 'cost': 12, 'price': 22, 'stock': 35, 'min_stock': 8, 'category_id': cat1['id']},
        {'name': 'Monitor 24"', 'sku': 'MON001', 'cost': 180, 'price': 280, 'stock': 8, 'min_stock': 5, 'category_id': cat1['id']},
        {'name': 'Escritorio Ejecutivo', 'sku': 'ESCR001', 'cost': 200, 'price': 350, 'stock': 3, 'min_stock': 2, 'category_id': cat2['id']},
        {'name': 'Silla Ergonómica', 'sku': 'SIL001', 'cost': 120, 'price': 200, 'stock': 10, 'min_stock': 3, 'category_id': cat2['id']},
        {'name': 'Resma de Papel A4', 'sku': 'PAP001', 'cost': 4, 'price': 8, 'stock': 100, 'min_stock': 20, 'category_id': cat3['id']},
        {'name': 'Bolígrafo Pack x10', 'sku': 'BOL001', 'cost': 2, 'price': 5, 'stock': 200, 'min_stock': 30, 'category_id': cat3['id']},
        {'name': 'Grapadora', 'sku': 'GRA001', 'cost': 5, 'price': 12, 'stock': 25, 'min_stock': 5, 'category_id': cat3['id']},
        {'name': 'Calculadora Científica', 'sku': 'CAL001', 'cost': 15, 'price': 30, 'stock': 3, 'min_stock': 5, 'category_id': cat1['id']}
    ]

    for prod_data in demo_products:
        try:
            products.create_product(prod_data)
            print(f"    ✓ {prod_data['name']}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    print("\n[4/4] Agregando usuario gerente...")
    try:
        auth.create_user(
            username='gerente',
            password='gerente123',
            role='gerente',
            full_name='Roberto Silva',
            email='gerente@empresa.com'
        )
        print("    ✓ Usuario gerente creado (gerente/gerente123)")
    except Exception as e:
        print(f"    ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("✓ Datos de demostración inicializados correctamente")
    print("=" * 60)
    print("\nPuede iniciar sesión con:")
    print("  Usuario: admin")
    print("  Contraseña: admin123")
    print("=" * 60)


def run_gui():
    """Ejecuta la aplicación gráfica."""
    print("Iniciando EnterpriseERP en modo gráfico...")
    app = ERPApplication()
    app.run()


def run_cli():
    """Ejecuta la interfaz de línea de comandos."""
    print("=" * 60)
    print("EnterpriseERP - Modo Consola")
    print("=" * 60)
    print("\nSeleccione una opción:")
    print("1. Iniciar sesión")
    print("2. Registrar nueva empresa")
    print("3. Salir")

    choice = input("\nOpción: ")

    if choice == "1":
        company_name = input("Empresa: ")
        username = input("Usuario: ")
        password = input("Contraseña: ")

        companies = db.get_companies()
        company = next((c for c in companies if c['name'] == company_name), None)

        if company:
            user = auth.login(company['id'], username, password)
            if user:
                print(f"\n✓ Bienvenido, {user['username']} ({user['role']})")
                print("Use la interfaz gráfica para continuar.")
            else:
                print("\n✗ Credenciales incorrectas")
        else:
            print("\n✗ Empresa no encontrada")

    elif choice == "2":
        print("\nRegistro de nueva empresa...")
        name = input("Nombre de la empresa: ")
        rif = input("RIF: ")
        admin_user = input("Usuario administrador: ")
        admin_pass = input("Contraseña: ")

        try:
            auth.register_admin({
                'name': name,
                'rif': rif,
                'address': '',
                'phone': '',
                'email': '',
                'admin_name': 'Administrador',
                'admin_username': admin_user,
                'admin_password': admin_pass,
                'admin_email': ''
            })
            print("\n✓ Empresa registrada correctamente")
        except Exception as e:
            print(f"\n✗ Error: {e}")

    else:
        print("\n¡Hasta luego!")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='EnterpriseERP - Sistema de Gestión Empresarial')
    parser.add_argument('--cli', action='store_true', help='Modo línea de comandos')
    parser.add_argument('--init', action='store_true', help='Inicializar datos de demostración')
    parser.add_argument('--gui', action='store_true', help='Modo gráfico (default)')

    args = parser.parse_args()

    if args.init:
        init_demo_data()
        return

    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
