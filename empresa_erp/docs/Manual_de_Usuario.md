# Manual de Usuario - EnterpriseERP

## Sistema de Gestión Empresarial

**Versión:** 1.0.0

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Módulos del Sistema](#módulos-del-sistema)
4. [Operaciones Comunes](#operaciones-comunes)
5. [Reportes y Exportación](#reportes-y-exportación)
6. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

### ¿Qué es EnterpriseERP?

EnterpriseERP es un sistema integral de gestión empresarial que le permite administrar de manera centralizada todos los aspectos de su empresa:

- **Recursos Humanos:** Gestión de empleados, nómina y asistencia
- **Inventario:** Control de productos y stock
- **Finanzas:** Ventas, compras y facturación
- **Reportes:** Análisis y estadísticas en tiempo real

### Requisitos del Sistema

- Computadora con Windows, macOS o Linux
- Python 3.8 o superior instalado
- 4 GB de memoria RAM mínimo
- 100 MB de espacio en disco

---

## Primeros Pasos

### 1.1 Iniciar la Aplicación

1. Abra una terminal o símbolo del sistema
2. Navegue hasta la carpeta del programa
3. Ejecute:
   ```
   python main.py
   ```

### 1.2 Primera Configuración

Si es la primera vez que usa el sistema:

1. Haga clic en **"Registrar Nueva Empresa"**
2. Complete los datos de su empresa:
   - Nombre de la empresa
   - RIF/NIT
   - Dirección
   - Teléfono
   - Correo electrónico
3. Configure el usuario administrador
4. Haga clic en **"Registrar"**

### 1.3 Iniciar Sesión

1. Seleccione su empresa del menú desplegable
2. Ingrese su nombre de usuario
3. Ingrese su contraseña
4. Haga clic en **"Iniciar Sesión"**

---

## Módulos del Sistema

### 2.1 Dashboard

El dashboard es la pantalla principal que muestra un resumen ejecutivo de su empresa.

**¿Qué información muestra?**

- Ventas del período actual
- Gastos registrados
- Flujo de caja neto
- Cantidad de productos
- Total de empleados
- Alertas pendientes

**Recomendación:** Consulte el dashboard diariamente para tener una visión general del estado de su empresa.

---

### 2.2 Gestión de Empleados

Este módulo le permite administrar todo lo relacionado con su personal.

#### Agregar un Nuevo Empleado

1. Vaya al menú **Empleados**
2. Haga clic en **"+ Nuevo Empleado"**
3. Complete los campos:
   - Nombres y Apellidos
   - Número de documento
   - Correo electrónico
   - Teléfono
   - Departamento
   - Puesto
   - Salario base
4. Haga clic en **"Guardar"**

#### Editar Información de un Empleado

1. En la lista de empleados, seleccione el empleado
2. Modifique los campos necesarios
3. Guarde los cambios

#### Desactivar un Empleado

1. Seleccione el empleado de la lista
2. Elimine el registro (cambiará a estado "inactivo")

---

### 2.3 Nómina

Este módulo calcula y gestiona los salarios de los empleados.

#### Generar Nómina Mensual

1. Vaya al menú **Nómina**
2. Haga clic en **"Generar Nómina"**
3. El sistema calculará automáticamente:
   - Salario bruto
   - Deducciones (impuestos, seguro social)
   - Bonificaciones
   - **Salario neto a pagar**

#### Ver Historial de Nómina

1. En la pantalla de nómina, observe la tabla con todos los registros
2. Cada fila muestra:
   - Período
   - Empleado
   - Salario base
   - Deducciones
   - Monto neto

---

### 2.4 Asistencia

Control de entrada y salida del personal.

#### Marcar Entrada

1. Vaya al menú **Asistencia**
2. Haga clic en **"Marcar Entrada"**
3. El sistema registrará la hora actual

#### Marcar Salida

1. Vaya al menú **Asistencia**
2. Haga clic en **"Marcar Salida"**
3. El sistema calculará las horas trabajadas

#### Solicitar Vacaciones

*Función disponible para todos los empleados*

1. Acceda a la opción de vacaciones
2. Seleccione las fechas
3. Ingrese el motivo
4. Envíe la solicitud

---

### 2.5 Inventario

Gestión de productos y control de stock.

#### Agregar un Producto

1. Vaya al menú **Inventario**
2. Haga clic en **"+ Nuevo Producto"**
3. Complete la información:
   - Nombre del producto
   - SKU (código interno)
   - Categoría
   - Costo de compra
   - Precio de venta
   - Stock actual
   - Stock mínimo (para alertas)
   - Ubicación en almacén
4. Haga clic en **"Guardar"**

#### Registrar Entrada de Mercancía

1. Seleccione el producto
2. Ingrese la cantidad a agregar
3. Indique la referencia (orden de compra, factura)
4. Agregue notas si es necesario
5. Confirme la entrada

#### Registrar Salida de Mercancía

1. Seleccione el producto
2. Ingrese la cantidad a retirar
3. Indique la referencia (venta, devolución)
4. Confirme la salida

#### Alertas de Stock Bajo

El sistema automáticamente detecta cuando un producto está por debajo del stock mínimo y genera una alerta en el dashboard.

---

### 2.6 Ventas

Registro y gestión de transacciones de venta.

#### Registrar una Venta

1. Vaya al menú **Ventas**
2. Haga clic en **"+ Nueva Venta"**
3. Complete los datos del cliente:
   - Nombre/Razón social
   - RIF/CI
4. Agregue productos:
   - Seleccione el producto
   - Ingrese la cantidad
   - Haga clic en "Agregar"
5. Repita para cada producto
6. Haga clic en **"Procesar Venta"**

**Nota:** El sistema automáticamente:
- Descuenta el stock
- Calcula impuestos (IVA 16%)
- Genera el total

#### Generar Factura

Después de cada venta, el sistema genera automáticamente una factura en formato PDF.

La factura incluye:
- Número de factura
- Datos del cliente
- Detalle de productos
- Subtotal, IVA y Total
- Forma de pago

#### Cancelar una Venta

1. Seleccione la venta de la lista
2. Elija la opción "Cancelar"
3. Ingrese el motivo de cancelación
4. El sistema revertirá automáticamente el stock

---

### 2.7 Compras

Registro de compras a proveedores.

#### Registrar una Compra

1. Vaya al menú **Compras**
2. Complete los datos:
   - Proveedor
   - Productos adquiridos
   - Costos
3. El sistema actualizará automáticamente el stock

#### Marcar Compra como Pagada

1. Seleccione la compra
2. Actualice el estado de pago
3. Ingrese la referencia del pago

---

## Operaciones Comunes

### 3.1 Búsqueda de Registros

**Empleados:**
- Busque por nombre
- Filtre por departamento
- Filtre por puesto

**Productos:**
- Busque por nombre
- Busque por SKU
- Filtre por categoría

**Ventas:**
- Filtre por fecha
- Filtre por estado
- Busque por número de factura

### 3.2 Exportar Datos

El sistema permite exportar datos a formato CSV:

1. Vaya al módulo deseado
2. Use la opción de exportar (disponible según permisos)
3. El archivo se guardará en `data/exports/`

### 3.3 Realizar Copias de Seguridad

**Crear Respaldo:**

El administrador puede crear copias de seguridad desde el menú de configuración.

**Restaurar Datos:**

1. Acceda a la opción de restaurar
2. Seleccione el archivo de respaldo
3. Confirme la restauración

---

## Reportes y Exportación

### 4.1 Reportes Disponibles

#### Reporte de Ventas
Muestra:
- Total de ventas del período
- Ingresos por método de pago
- Promedio por transacción

#### Estado de Resultados
Muestra:
- Ingresos netos
- Costos de venta
- Gastos operativos
- Utilidad bruta y neta
- Margen de rentabilidad

#### Flujo de Caja
Muestra:
- Entradas (ventas)
- Salidas (compras, nómina)
- Saldo neto

#### Reporte de Inventario
Muestra:
- Valor total del inventario
- Productos con stock bajo
- Valorización de productos

#### Reporte de RRHH
Muestra:
- Total de empleados
- Distribución por departamento
- Costo de nómina

### 4.2 Dashboard Visual

El sistema genera gráficos automáticamente:

- Gráfico de ventas por día
- Gráfico de ingresos vs gastos
- Gráfico de estado del inventario
- Gráfico de distribución de empleados

---

## Solución de Problemas

### 5.1 Problemas de Acceso

**No puedo iniciar sesión:**
- Verifique que el nombre de usuario y contraseña sean correctos
- Asegúrese de seleccionar la empresa correcta
- Si olvidó su contraseña, contacte al administrador

**El sistema me deniega el acceso a una función:**
- Consulte con el administrador sobre sus permisos
- Es posible que su rol no tenga acceso a esa función

### 5.2 Problemas con Datos

**Un producto no aparece en el inventario:**
- Verifique que el producto esté activo
- Use la función de búsqueda
- Filtre por la categoría correspondiente

**El stock no se actualiza:**
- Verifique que no haya procesos concurrentes
- Reinicie la aplicación

### 5.3 Problemas Técnicos

**La aplicación no inicia:**
- Verifique que Python esté instalado: `python --version`
- Asegúrese de estar en el directorio correcto
- Verifique que los archivos no estén corruptos

**Error al generar PDF:**
- Verifique que tenga permisos de escritura
- Asegúrese de tener espacio en disco

---

## Glosario

| Término | Definición |
|---------|------------|
| **SKU** | Código único de identificación de producto |
| **RIF** | Registro de Información Fiscal |
| **IVA** | Impuesto al Valor Agregado (16%) |
| **RBAC** | Control de Acceso Basado en Roles |
| **Multitenancy** | Capacidad de servir múltiples empresas |
| **CRUD** | Crear, Leer, Actualizar, Eliminar |

---

## Contacto y Soporte

Para soporte técnico o consultas:

- Correo: soporte@enterpriseerp.com
- Documentación: docs/ folder

---

**EnterpriseERP** - Simplificando la gestión empresarial.

© 2026 EnterpriseERP. Todos los derechos reservados.
