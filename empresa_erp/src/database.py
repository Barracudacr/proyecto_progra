"""
Sistema de Base de Datos JSON para ERP Empresarial
================================================
Este módulo implementa un sistema de almacenamiento de datos usando archivos JSON
para обеспечить persistencia sin necesidad de bases de datos externas.
Soporta multitenancy (múltiples empresas) y autenticación.
"""

import json
import os
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class Database:
    """
    Clase principal para gestión de base de datos JSON.
    Implementa patrón Singleton para garantizar una única instancia.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.base_path = Path("data")
            self.base_path.mkdir(exist_ok=True)
            self.current_company = None
            self.current_user = None
            self.current_role = None
            self._initialized = True

    def _get_company_path(self, company_id: str = None) -> Path:
        """Obtiene la ruta de la carpeta de datos de una empresa."""
        company = company_id or self.current_company
        if not company:
            raise ValueError("No hay empresa seleccionada")
        path = self.base_path / f"company_{company}"
        path.mkdir(exist_ok=True)
        return path

    def _get_file_path(self, collection: str, company_id: str = None) -> Path:
        """Obtiene la ruta de un archivo de colección específico."""
        return self._get_company_path(company_id) / f"{collection}.json"

    def _load_collection(self, collection: str, company_id: str = None) -> List[Dict]:
        """Carga una colección desde archivo JSON."""
        file_path = self._get_file_path(collection, company_id)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_collection(self, collection: str, data: List[Dict], company_id: str = None):
        """Guarda una colección en archivo JSON."""
        file_path = self._get_file_path(collection, company_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def init_company(self, company_id: str):
        """Inicializa el contexto para una empresa específica."""
        self.current_company = company_id
        self._create_collections()

    def _create_collections(self):
        """Crea las colecciones iniciales para una empresa."""
        collections = ['users', 'employees', 'attendance', 'payroll', 'products',
                       'categories', 'suppliers', 'sales', 'purchases', 'invoices']
        for collection in collections:
            file_path = self._get_file_path(collection)
            if not file_path.exists():
                self._save_collection(collection, [])

    def select_company(self, company_id: str):
        """Selecciona la empresa activa para las operaciones."""
        self.current_company = company_id

    def create_company(self, name: str, cedula_juridica: str, address: str, phone: str, email: str) -> Dict:
        """
        Registra una nueva empresa en el sistema.
        Cada empresa tiene su propio espacio de datos aislado.
        """
        company_data = {
            'id': str(uuid.uuid4())[:8],
            'name': name,
            'cedula_juridica': cedula_juridica,
            'address': address,
            'phone': phone,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'active': True
        }

        companies = self._get_companies_list()
        if any(c['cedula_juridica'] == cedula_juridica for c in companies):
            raise ValueError("Ya existe una empresa con esta Cédula Jurídica")

        companies.append(company_data)
        self._save_companies_list(companies)

        self.init_company(company_data['id'])
        self._create_collections()

        return company_data

    def _get_companies_list(self) -> List[Dict]:
        """Obtiene la lista de todas las empresas."""
        meta_file = self.base_path / "companies.json"
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_companies_list(self, companies: List[Dict]):
        """Guarda la lista de empresas."""
        meta_file = self.base_path / "companies.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=4, ensure_ascii=False)

    def get_companies(self) -> List[Dict]:
        """Retorna todas las empresas registradas."""
        return self._get_companies_list()

    def hash_password(self, password: str) -> str:
        """Genera hash seguro de contraseña usando SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, password: str, role: str,
                    employee_id: str = None, full_name: str = "",
                    email: str = "") -> Dict:
        """Crea un nuevo usuario en el sistema."""
        users = self._load_collection('users')

        if any(u['username'] == username for u in users):
            raise ValueError("El nombre de usuario ya existe")

        valid_roles = ['admin', 'gerente', 'empleado']
        if role not in valid_roles:
            raise ValueError(f"Rol inválido. Debe ser uno de: {valid_roles}")

        user = {
            'id': str(uuid.uuid4())[:12],
            'username': username,
            'password_hash': self.hash_password(password),
            'role': role,
            'employee_id': employee_id,
            'full_name': full_name,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'active': True
        }

        users.append(user)
        self._save_collection('users', users)
        return user

    def authenticate(self, username: str, password: str, company_id: str = None) -> Optional[Dict]:
        """
        Autentica un usuario y retorna sus datos si las credenciales son válidas.
        Implementa control de empresa para multitenancy.
        """
        if company_id:
            self.select_company(company_id)

        users = self._load_collection('users')
        password_hash = self.hash_password(password)

        for user in users:
            if user['username'] == username and user['password_hash'] == password_hash:
                if user.get('active', True):
                    user['last_login'] = datetime.now().isoformat()
                    self._update_user(user['id'], {'last_login': user['last_login']})
                    self.current_user = user
                    self.current_role = user['role']
                    return user
        return None

    def _update_user(self, user_id: str, updates: Dict):
        """Actualiza datos de un usuario."""
        users = self._load_collection('users')
        for i, user in enumerate(users):
            if user['id'] == user_id:
                users[i].update(updates)
                break
        self._save_collection('users', users)

    def check_permission(self, required_role: str) -> bool:
        """Verifica si el usuario actual tiene el rol requerido."""
        role_hierarchy = {'admin': 3, 'gerente': 2, 'empleado': 1}
        user_level = role_hierarchy.get(self.current_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level

    def get_current_user(self) -> Optional[Dict]:
        """Retorna el usuario autenticado actualmente."""
        return self.current_user

    def CRUD(self, collection: str, operation: str, data: Dict = None,
             filters: Dict = None, record_id: str = None) -> any:
        """
        Sistema CRUD genérico para todas las colecciones.
        Operaciones: create, read, update, delete, list, find

        Args:
            collection: Nombre de la colección
            operation: Tipo de operación (create, read, update, delete, list, find)
            data: Datos para crear o actualizar
            filters: Criterios de filtrado para búsqueda
            record_id: ID del registro específico
        """
        if not self.current_company:
            raise ValueError("Debe seleccionar una empresa primero")

        items = self._load_collection(collection)

        if operation == 'list':
            return self._apply_filters(items, filters) if filters else items

        elif operation == 'find':
            return self._find_by_id(items, record_id) if record_id else None

        elif operation == 'create':
            if not data:
                raise ValueError("Se requieren datos para crear")
            data['id'] = str(uuid.uuid4())[:12]
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            items.append(data)
            self._save_collection(collection, items)
            return data

        elif operation == 'update':
            if not record_id:
                raise ValueError("Se requiere ID para actualizar")
            for i, item in enumerate(items):
                if item['id'] == record_id:
                    data['updated_at'] = datetime.now().isoformat()
                    items[i].update(data)
                    self._save_collection(collection, items)
                    return items[i]
            raise ValueError("Registro no encontrado")

        elif operation == 'delete':
            if not record_id:
                raise ValueError("Se requiere ID para eliminar")
            for i, item in enumerate(items):
                if item['id'] == record_id:
                    items.pop(i)
                    self._save_collection(collection, items)
                    return True
            raise ValueError("Registro no encontrado")

        return None

    def _find_by_id(self, items: List[Dict], record_id: str) -> Optional[Dict]:
        """Busca un registro por su ID."""
        for item in items:
            if item.get('id') == record_id:
                return item
        return None

    def _apply_filters(self, items: List[Dict], filters: Dict) -> List[Dict]:
        """Aplica filtros a una lista de elementos."""
        result = items
        for key, value in filters.items():
            if key == 'search':
                search = value.lower()
                result = [item for item in result
                         if search in str(item.get('name', '')).lower()
                         or search in str(item.get('description', '')).lower()
                         or search in str(item.get('id', '')).lower()]
            elif key == 'date_from':
                result = [item for item in result
                         if item.get('created_at', '') >= value]
            elif key == 'date_to':
                result = [item for item in result
                         if item.get('created_at', '') <= value]
            else:
                result = [item for item in result if item.get(key) == value]
        return result

    def backup_company(self, company_id: str = None, backup_path: str = None) -> str:
        """
        Crea una copia de seguridad de los datos de una empresa.
        Retorna la ruta del archivo de backup.
        """
        company = company_id or self.current_company
        if not company:
            raise ValueError("No hay empresa seleccionada")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(backup_path) if backup_path else self.base_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        backup_file = backup_dir / f"backup_{company}_{timestamp}.json"

        company_path = self.base_path / f"company_{company}"
        backup_data = {'metadata': {'company_id': company, 'timestamp': timestamp}}

        for json_file in company_path.glob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                backup_data[json_file.stem] = json.load(f)

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=4, ensure_ascii=False)

        return str(backup_file)

    def restore_company(self, backup_file: str):
        """Restaura datos de una empresa desde un backup."""
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        company_id = backup_data['metadata']['company_id']
        company_path = self.base_path / f"company_{company_id}"
        company_path.mkdir(exist_ok=True)

        for key, data in backup_data.items():
            if key != 'metadata':
                with open(company_path / f"{key}.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        return company_id

    def export_csv(self, collection: str, csv_path: str = None) -> str:
        """Exporta una colección a formato CSV."""
        import csv

        items = self._load_collection(collection)
        if not items:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = self.base_path / "exports"
        export_dir.mkdir(exist_ok=True)
        csv_file = export_dir / f"{collection}_{timestamp}.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)

        return str(csv_file)

    def import_csv(self, collection: str, csv_file: str):
        """Importa datos desde un archivo CSV."""
        import csv

        items = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            items = list(reader)

        if items:
            self._save_collection(collection, items)
        return len(items)


db = Database()
