"""
Módulo de Gestión de Inventarios
================================
Control completo de productos, stock y movimientos de inventario.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from src.database import db
from src.modules.auth import auth


class CategoryManager:
    """Gestor de categorías de productos."""

    def __init__(self):
        self.db = db

    def create_category(self, data: Dict) -> Dict:
        """Crea una nueva categoría."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para crear categorías")

        category = {
            'id': str(uuid.uuid4())[:12],
            'name': data['name'],
            'description': data.get('description', ''),
            'parent_id': data.get('parent_id'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        return self.db.CRUD('categories', 'create', data=category)

    def list_categories(self, parent_id: str = None) -> List[Dict]:
        """Lista categorías, opcionalmente filtradas por padre."""
        filters = {}
        if parent_id:
            filters['parent_id'] = parent_id

        return self.db.CRUD('categories', 'list', filters=filters)

    def update_category(self, category_id: str, updates: Dict) -> Dict:
        """Actualiza una categoría."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para actualizar categorías")

        return self.db.CRUD('categories', 'update', data=updates, record_id=category_id)

    def delete_category(self, category_id: str) -> bool:
        """Elimina una categoría."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para eliminar categorías")

        return self.db.CRUD('categories', 'delete', record_id=category_id)


class SupplierManager:
    """Gestor de proveedores."""

    def __init__(self):
        self.db = db

    def create_supplier(self, data: Dict) -> Dict:
        """Registra un nuevo proveedor."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para registrar proveedores")

        supplier = {
            'id': str(uuid.uuid4())[:12],
            'name': data['name'],
            'contact_person': data.get('contact_person', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'cedula_juridica': data.get('cedula_juridica', ''),
            'payment_terms': data.get('payment_terms', 'contado'),
            'rating': data.get('rating', 5),
            'status': 'activo',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        return self.db.CRUD('suppliers', 'create', data=supplier)

    def list_suppliers(self, filters: Dict = None) -> List[Dict]:
        """Lista proveedores con filtros."""
        return self.db.CRUD('suppliers', 'list', filters=filters)

    def update_supplier(self, supplier_id: str, updates: Dict) -> Dict:
        """Actualiza datos de un proveedor."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para actualizar proveedores")

        return self.db.CRUD('suppliers', 'update', data=updates, record_id=supplier_id)

    def delete_supplier(self, supplier_id: str) -> bool:
        """Desactiva un proveedor."""
        return self.db.CRUD('suppliers', 'update',
                          data={'status': 'inactivo'},
                          record_id=supplier_id)


class ProductManager:
    """
    Gestor de productos e inventario.
    Maneja stock en tiempo real, alertas y categorización.
    """

    def __init__(self):
        self.db = db

    def create_product(self, data: Dict) -> Dict:
        """Crea un nuevo producto en el inventario."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para crear productos")

        if data.get('sku'):
            existing = self.db.CRUD('products', 'list', filters={'sku': data['sku']})
            if existing:
                raise ValueError("Ya existe un producto con este SKU")

        product = {
            'id': str(uuid.uuid4())[:12],
            'sku': data.get('sku', str(uuid.uuid4())[:8].upper()),
            'name': data['name'],
            'description': data.get('description', ''),
            'category_id': data.get('category_id'),
            'supplier_id': data.get('supplier_id'),
            'cost': float(data.get('cost', 0)),
            'price': float(data.get('price', 0)),
            'stock': int(data.get('stock', 0)),
            'min_stock': int(data.get('min_stock', 10)),
            'max_stock': int(data.get('max_stock', 100)),
            'unit': data.get('unit', 'unidad'),
            'location': data.get('location', ''),
            'barcode': data.get('barcode', ''),
            'image': data.get('image', ''),
            'status': 'activo',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self._create_initial_movement(product['id'], 'entrada', product['stock'],
                                       'Stock inicial', 'inventario_inicial')

        return self.db.CRUD('products', 'create', data=product)

    def _create_initial_movement(self, product_id: str, movement_type: str,
                                 quantity: int, notes: str, reference: str):
        """Crea el movimiento inicial de inventario."""
        movement = {
            'id': str(uuid.uuid4())[:12],
            'product_id': product_id,
            'type': movement_type,
            'quantity': quantity,
            'notes': notes,
            'reference': reference,
            'created_by': auth.get_session()['user_id'] if auth.get_session() else 'system',
            'created_at': datetime.now().isoformat()
        }
        self.db.CRUD('inventory_movements', 'create', data=movement)

    def list_products(self, filters: Dict = None) -> List[Dict]:
        """Lista productos con filtros."""
        return self.db.CRUD('products', 'list', filters=filters)

    def get_product(self, product_id: str = None, sku: str = None) -> Optional[Dict]:
        """Obtiene un producto por ID o SKU."""
        if product_id:
            return self.db.CRUD('products', 'find', record_id=product_id)

        if sku:
            products = self.db.CRUD('products', 'list', filters={'sku': sku})
            return products[0] if products else None

        return None

    def update_product(self, product_id: str, updates: Dict) -> Dict:
        """Actualiza datos de un producto."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para actualizar productos")

        return self.db.CRUD('products', 'update', data=updates, record_id=product_id)

    def delete_product(self, product_id: str) -> bool:
        """Desactiva un producto."""
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para eliminar productos")

        return self.db.CRUD('products', 'update',
                          data={'status': 'inactivo'},
                          record_id=product_id)

    def stock_entry(self, product_id: str, quantity: int, notes: str = '',
                   reference: str = '') -> Dict:
        """
        Registra entrada de mercancía al inventario.
        """
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para entradas de inventario")

        product = self.get_product(product_id)
        if not product:
            raise ValueError("Producto no encontrado")

        new_stock = product['stock'] + quantity

        self.db.CRUD('products', 'update',
                    data={'stock': new_stock},
                    record_id=product_id)

        movement = {
            'id': str(uuid.uuid4())[:12],
            'product_id': product_id,
            'type': 'entrada',
            'quantity': quantity,
            'stock_before': product['stock'],
            'stock_after': new_stock,
            'notes': notes,
            'reference': reference,
            'created_by': auth.get_session()['user_id'],
            'created_at': datetime.now().isoformat()
        }

        self.db.CRUD('inventory_movements', 'create', data=movement)

        self._check_low_stock(product_id, new_stock, product['min_stock'])

        return movement

    def stock_output(self, product_id: str, quantity: int, notes: str = '',
                    reference: str = '') -> Dict:
        """
        Registra salida de mercancía del inventario.
        """
        if not auth.has_permission('*') and not auth.has_role('gerente'):
            raise PermissionError("No tiene permiso para salidas de inventario")

        product = self.get_product(product_id)
        if not product:
            raise ValueError("Producto no encontrado")

        if product['stock'] < quantity:
            raise ValueError(f"Stock insuficiente. Disponible: {product['stock']}")

        new_stock = product['stock'] - quantity

        self.db.CRUD('products', 'update',
                    data={'stock': new_stock},
                    record_id=product_id)

        movement = {
            'id': str(uuid.uuid4())[:12],
            'product_id': product_id,
            'type': 'salida',
            'quantity': quantity,
            'stock_before': product['stock'],
            'stock_after': new_stock,
            'notes': notes,
            'reference': reference,
            'created_by': auth.get_session()['user_id'],
            'created_at': datetime.now().isoformat()
        }

        self.db.CRUD('inventory_movements', 'create', data=movement)

        self._check_low_stock(product_id, new_stock, product['min_stock'])

        return movement

    def _check_low_stock(self, product_id: str, current_stock: int, min_stock: int):
        """Verifica si el stock está por debajo del mínimo y genera alerta."""
        if current_stock <= min_stock:
            self._create_low_stock_alert(product_id, current_stock, min_stock)

    def _create_low_stock_alert(self, product_id: str, current_stock: int, min_stock: int):
        """Crea una alerta de stock bajo."""
        product = self.get_product(product_id)
        alert = {
            'id': str(uuid.uuid4())[:12],
            'type': 'low_stock',
            'product_id': product_id,
            'product_name': product['name'] if product else 'Desconocido',
            'current_stock': current_stock,
            'min_stock': min_stock,
            'status': 'pendiente',
            'created_at': datetime.now().isoformat()
        }
        self.db.CRUD('alerts', 'create', data=alert)

    def get_low_stock_products(self) -> List[Dict]:
        """Retorna productos con stock bajo el mínimo."""
        products = self.db.CRUD('products', 'list', filters={'status': 'activo'})
        return [p for p in products if p['stock'] <= p['min_stock']]

    def get_stock_alerts(self) -> List[Dict]:
        """Retorna alertas de stock pendientes."""
        return self.db.CRUD('alerts', 'list', filters={'type': 'low_stock', 'status': 'pendiente'})

    def acknowledge_alert(self, alert_id: str) -> Dict:
        """Marca una alerta como vista."""
        return self.db.CRUD('alerts', 'update',
                           data={'status': 'atendida'},
                           record_id=alert_id)

    def get_movements(self, product_id: str = None, start_date: str = None,
                     end_date: str = None) -> List[Dict]:
        """Obtiene historial de movimientos de inventario."""
        filters = {}
        if product_id:
            filters['product_id'] = product_id
        if start_date:
            filters['date_from'] = start_date
        if end_date:
            filters['date_to'] = end_date

        return self.db.CRUD('inventory_movements', 'list', filters=filters)

    def get_inventory_valuation(self) -> Dict:
        """Calcula el valor total del inventario."""
        products = self.db.CRUD('products', 'list', filters={'status': 'activo'})

        total_cost = sum(p['cost'] * p['stock'] for p in products)
        total_retail = sum(p['price'] * p['stock'] for p in products)

        return {
            'total_products': len(products),
            'total_units': sum(p['stock'] for p in products),
            'total_cost_value': total_cost,
            'total_retail_value': total_retail,
            'potential_profit': total_retail - total_cost,
            'products': products
        }

    def search_products(self, query: str) -> List[Dict]:
        """Busca productos por nombre, SKU o descripción."""
        return self.db.CRUD('products', 'list', filters={'search': query})


categories = CategoryManager()
suppliers = SupplierManager()
products = ProductManager()
