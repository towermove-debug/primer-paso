import sqlite3
import datetime

# Puedes editar esta base de datos. No hay conflicto de permisos.

class BaseDB:
    """Clase base de datos primaria de la cual heredan todas las tablas."""
    
    def __init__(self, db_name="stock.db"):
        self.db_name = db_name
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Abre la conexión hacia SQLite local y genera el cursor.
        [PRODUCCIÓN] check_same_thread=False es vital para Flet, ya que maneja eventos en múltiples hilos."""
        self.conexion = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conexion.cursor()
        
    def obtener_columnas(self):
        """Introspecta la tabla usando el PRAGMA de SQLite para devolver los nombres de las columnas."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"PRAGMA table_info({self.tabla})")
        return [col[1] for col in self.cursor.fetchall()]

    def obtener_todos(self):
        """Selecciona de forma universal todas las filas y columnas de la tabla indicada."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT * FROM {self.tabla}")
        return self.cursor.fetchall()


class Stock(BaseDB):
    """
    Gestiona la tabla 'stock', que funje de inventario maestro.
    Almacena artículos con sus datos monetarios, proveedor y código universal.
    """
    def __init__(self):
        super().__init__()
        self.tabla = "stock"

    def crear_tablas(self):
        """Asegura la creación de la tabla principal de inventario si no existe."""
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id_producto TEXT,
                cantidad INTEGER,
                producto TEXT,
                utilidad REAL,
                costo REAL,
                proveedor TEXT
            )
        ''') 
        self.conexion.commit()

    def obtener_cantidad_menores_20(self):
        """Retorna artículos en situación crítica de escasez (cantidad debajo de 20)."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT cantidad, producto, proveedor FROM {self.tabla} WHERE cantidad < 20")
        return self.cursor.fetchall()

    def actualizar(self, producto, cantidad):
        """Sustrae lógicamente una cantidad dada del stock pre-existente, basado en el nombre (case-insensitive)."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"UPDATE {self.tabla} SET cantidad = cantidad - ? WHERE LOWER(producto) = LOWER(?)", (cantidad, producto))
        self.conexion.commit()

    def agregar_stock(self, id_producto, cantidad, producto, utilidad, costo, proveedor):
        """Realiza una inserción para depositar un bien nuevo en caja."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (id_producto, cantidad, producto, utilidad, costo, proveedor) VALUES (?, ?, ?, ?, ?, ?)", 
                            (id_producto, cantidad, producto, utilidad, costo, proveedor))
        self.conexion.commit()

    def reponer_stock(self, id_producto, cantidad_a_agregar,costo_unitario):
        """Incrementa la cantidad de un producto existente sumándole la cantidad dada. y actualizando el precio unitario"""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"UPDATE {self.tabla} SET cantidad = cantidad + ?, costo = ? WHERE id_producto = ?", (cantidad_a_agregar, costo_unitario, id_producto))
        self.conexion.commit()

    def eliminar_stock(self, id_registro, producto):
        """Elimina un producto (o su rama) usando case-insensitive."""
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f"DELETE FROM {self.tabla} WHERE LOWER(producto) = LOWER(?)", (producto,))
            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al eliminar el stock: {e}")

    def modificar_stock(self, id_registro, cantidad, producto, utilidad, costo, proveedor):
        """Reemplaza la meta-data de una entrada del inventario maestro."""
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f'''
            UPDATE {self.tabla} 
            SET cantidad = ?, producto = ?, utilidad = ?, costo = ?, proveedor = ? 
            WHERE id_producto = ?
        ''', (cantidad, producto, utilidad, costo, proveedor, id_registro))
            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al modificar el stock: {e}")

    def obtener_cantidad(self, producto):
        """Consulta y extrae la cantidad disponible de un producto particular."""
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f"SELECT cantidad FROM {self.tabla} WHERE LOWER(producto) = LOWER(?)", (producto,))
            resultado = self.cursor.fetchone()
            return resultado[0] if resultado else 0
        except sqlite3.Error as e:
            print(f"Error al obtener la cantidad: {e}")
            return 0


class VentasDiarias(BaseDB):
    """
    Tabla temporal transaccional que representa el flujo de caja del día actual.
    Suele llamarse a esta tabla 'ventas'.
    """
    def __init__(self):
        super().__init__()
        self.tabla = "ventas"

    def crear_tablas(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id_producto TEXT,
                cantidad INTEGER,
                producto TEXT,
                utilidad REAL,
                hora TIME DEFAULT (time('now', 'localtime'))
            )
        ''')
        self.conexion.commit()

    def agregar_venta_diaria(self, id_producto, cantidad, producto, utilidad):
        """Imputa una venta fugaz dentro de la caja temporal para contabilización corta."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (id_producto, cantidad, producto, utilidad) VALUES (?, ?, ?, ?)", 
                            (id_producto, cantidad, producto, utilidad))
        self.conexion.commit()
        
    def limpiar_ventas(self):
        """Trunca la tabla dejando la caja vacía limpia para un nuevo día/turno."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"DELETE FROM {self.tabla}")
        self.conexion.commit()


class Ventas_general(BaseDB):
    """
    Tabla Histórica General perpetua ('ventas_diarias') o mejor dicho Registros de operaciones.
    Consolida absolutamente toda la actividad de ventas cruzada con costos.
    """
    def __init__(self):
        super().__init__()
        self.tabla = "ventas_diarias"

    def crear_tablas_general(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id_producto TEXT,
                cantidad INTEGER,
                producto TEXT,
                costo REAL,
                utilidad REAL,
                proveedor TEXT,
                hora TEXT,
                fecha DATE DEFAULT (date('now', 'localtime'))
            )
        ''')
        self.conexion.commit()

    def agregar_venta_general(self, id_producto, cantidad, producto, costo, utilidad, proveedor):
        """Plasma un registro contable sellándolo automáticamente con hora y fecha de servidor real local."""
        if not self.cursor:
            self.conectar()
            
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        
        self.cursor.execute(f'''
            INSERT INTO {self.tabla} (id_producto, cantidad, producto, costo, utilidad, proveedor, hora, fecha) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_producto, cantidad, producto, costo, utilidad, proveedor, hora_actual, fecha_actual))
        self.conexion.commit()
        
    def obtener_por_fecha(self, fecha):
        """Consulta especial usando parámetros de fecha YYYY-MM-DD para obtener la bitácora requerida."""
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT * FROM {self.tabla} WHERE fecha = ?", (fecha,))
        return self.cursor.fetchall()


class proveedores(BaseDB):
    """
    Administra la agenda de Entidades Suplidoras / Proveedores de la Empresa comercial.
    """
    def __init__(self):
        super().__init__()
        self.tabla = "proveedores"

    def crear_tablas(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                telefono TEXT,
                correo TEXT
            )
        ''')
        self.conexion.commit()

    def agregar_proveedor(self, nombre, telefono, correo):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (nombre, telefono, correo) VALUES (?, ?, ?)", (nombre, telefono, correo))
        self.conexion.commit()

    def eliminar_proveedor(self, nombre):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"DELETE FROM {self.tabla} WHERE LOWER(nombre) = LOWER(?)", (nombre,))
        self.conexion.commit()

    def actualizar_proveedor(self, nombre_nuevo, telefono, correo, nombre_antiguo):
        if not self.cursor:
            self.conectar()
        try:
            # 1. Actualizar la tabla de proveedores (incluyendo el nombre si cambió)
            self.cursor.execute(f"UPDATE {self.tabla} SET nombre = ?, telefono = ?, correo = ? WHERE LOWER(nombre) = LOWER(?)", 
                                (nombre_nuevo, telefono, correo, nombre_antiguo))
            
            # 2. Si el nombre cambió, debemos actualizarlo también en la tabla de stock para mantener la integridad
            if nombre_nuevo.lower() != nombre_antiguo.lower():
                self.cursor.execute("UPDATE stock SET proveedor = ? WHERE LOWER(proveedor) = LOWER(?)", (nombre_nuevo, nombre_antiguo))
            
            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al actualizar el proveedor: {e}")
            self.conexion.rollback()

class pedidos(BaseDB):
    """
    Administra la agenda de Entidades Suplidoras / Proveedores de la Empresa comercial.
    """
    def __init__(self):
        super().__init__()
        self.tabla = "pedidos"

    def crear_tablas(self):
        # columnas: id (autoincrement), id_producto, producto, cantidad, precio_unitario, costo_total, proveedor, estado, fecha_creacion
        # (estado: "GENERADO", "PEDIDO", "ENTREGADO")
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                costo_total REAL,
                proveedor TEXT,
                estado TEXT,
                fecha_creacion DATE DEFAULT (DATE('now'))
            )
        ''')
        self.conexion.commit()

    def agregar_pedido(self, producto, cantidad, precio_unitario, costo_total, proveedor, estado):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (producto, cantidad, precio_unitario, costo_total, proveedor, estado) VALUES (?, ?, ?, ?, ?, ?)", (producto, cantidad, precio_unitario, costo_total, proveedor, estado))
        self.conexion.commit()

    def eliminar_pedido(self, id):
        if not self.cursor:
            self.conectar()
        
        self.cursor.execute(f"DELETE FROM {self.tabla} WHERE id = ?", (id,))
        self.conexion.commit()


    def actualizar_pedido(self, id, estado):
        estados = ["GENERADO", "PEDIDO", "ENTREGADO"]
        if estado not in estados:
            return False
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"UPDATE {self.tabla} SET estado = ? WHERE id = ?", (estado, id))
        self.conexion.commit()

    def obtener_pedido(self, id):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT * FROM {self.tabla} WHERE id = ?", (id,))
        return self.cursor.fetchone()
