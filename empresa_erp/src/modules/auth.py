"""
Módulo de Autenticación y Gestión de Usuarios
=============================================
Sistema completo de autenticación con roles y permisos.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from src.database import db


class AuthSystem:
    """
    Sistema de autenticación con soporte para múltiples roles.
    Implementa el patrón de control de acceso basado en roles (RBAC).
    """

    ROLES = {
        'admin': {
            'level': 3,
            'permissions': ['*']
        },
        'gerente': {
            'level': 2,
            'permissions': [
                'read_employees', 'read_payroll', 'read_inventory',
                'write_inventory', 'read_finances', 'read_reports',
                'write_sales', 'write_purchases'
            ]
        },
        'empleado': {
            'level': 1,
            'permissions': [
                'read_own_profile', 'read_own_payroll',
                'write_own_attendance'
            ]
        }
    }

    def __init__(self):
        self.db = db
        self.current_session = None

    def register_admin(self, company_data: Dict) -> Dict:
        """Registra una nueva empresa con el primer usuario administrador."""
        company = self.db.create_company(
            name=company_data['name'],
            cedula_juridica=company_data['cedula_juridica'],
            address=company_data['address'],
            phone=company_data['phone'],
            email=company_data['email']
        )

        admin = self.db.create_user(
            username=company_data['admin_username'],
            password=company_data['admin_password'],
            role='admin',
            full_name=company_data['admin_name'],
            email=company_data['admin_email']
        )

        return {'company': company, 'admin': admin}

    def login(self, company_id: str, username: str, password: str) -> Optional[Dict]:
        """
        Autentica un usuario en el sistema.
        Retorna los datos del usuario si es exitoso, None si falla.
        """
        user = self.db.authenticate(username, password, company_id)

        if user:
            self.current_session = {
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'company_id': company_id,
                'login_time': datetime.now().isoformat(),
                'permissions': self.ROLES.get(user['role'], {}).get('permissions', [])
            }
            return self.current_session

        return None

    def logout(self):
        """Cierra la sesión actual."""
        self.current_session = None
        self.db.current_user = None
        self.db.current_role = None

    def has_permission(self, permission: str) -> bool:
        """Verifica si el usuario actual tiene un permiso específico."""
        if not self.current_session:
            return False

        permissions = self.current_session.get('permissions', [])
        return '*' in permissions or permission in permissions

    def has_role(self, role: str) -> bool:
        """Verifica si el usuario tiene el rol especificado o superior."""
        if not self.current_session:
            return False

        user_level = self.ROLES.get(self.current_session['role'], {}).get('level', 0)
        required_level = self.ROLES.get(role, {}).get('level', 0)

        return user_level >= required_level

    def create_user(self, user_data: Dict) -> Dict:
        """Crea un nuevo usuario (requiere permiso de admin)."""
        if not self.has_permission('*'):
            if not self.has_role('admin'):
                raise PermissionError("Solo administradores pueden crear usuarios")

        return self.db.create_user(
            username=user_data['username'],
            password=user_data['password'],
            role=user_data['role'],
            employee_id=user_data.get('employee_id'),
            full_name=user_data.get('full_name', ''),
            email=user_data.get('email', '')
        )

    def list_users(self, filters: Dict = None) -> List[Dict]:
        """Lista usuarios con filtros opcionales."""
        if not self.has_permission('*'):
            if not self.has_role('admin'):
                raise PermissionError("Solo administradores pueden listar usuarios")

        return self.db.CRUD('users', 'list', filters=filters)

    def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Actualiza datos de un usuario."""
        if not self.has_permission('*'):
            if self.current_session['user_id'] != user_id:
                if not self.has_role('admin'):
                    raise PermissionError("No tiene permiso para actualizar este usuario")

        if 'password' in updates:
            updates['password_hash'] = self.db.hash_password(updates.pop('password'))

        return self.db.CRUD('users', 'update', data=updates, record_id=user_id)

    def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario del sistema."""
        if not self.has_permission('*'):
            if not self.has_role('admin'):
                raise PermissionError("Solo administradores pueden eliminar usuarios")

        if self.current_session['user_id'] == user_id:
            raise ValueError("No puede eliminarse a sí mismo")

        return self.db.CRUD('users', 'delete', record_id=user_id)

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Permite a un usuario cambiar su contraseña."""
        if self.current_session['user_id'] != user_id:
            if not self.has_role('admin'):
                raise PermissionError("No puede cambiar la contraseña de otro usuario")

        user = self.db.CRUD('users', 'find', record_id=user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        if self.db.hash_password(old_password) != user['password_hash']:
            raise ValueError("Contraseña actual incorrecta")

        self.db.CRUD('users', 'update', data={'password': new_password}, record_id=user_id)
        return True

    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Resetea la contraseña de un usuario (solo admin)."""
        if not self.has_role('admin'):
            raise PermissionError("Solo administradores pueden resetear contraseñas")

        self.db.CRUD('users', 'update', data={'password': new_password}, record_id=user_id)
        return True

    def get_session(self) -> Optional[Dict]:
        """Retorna la sesión actual."""
        return self.current_session

    def is_authenticated(self) -> bool:
        """Verifica si hay una sesión activa."""
        return self.current_session is not None


auth = AuthSystem()
