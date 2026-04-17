"""
base_de_datos.py
────────────────
Módulo de acceso a datos para la aplicación de stock/ventas.

Estructura:
  - BaseDatos : clase base con lógica compartida (conectar, desconectar, obtener).
  - Stock     : ABM de productos en inventario.
  - Ventas    : registro de ventas (acumula si el producto ya existe).
  - VentasDiarias : copia diaria de ventas para historial.

Todas las tablas viven en el archivo 'stock.db' (SQLite).
"""

import sqlite3
from datetime import datetime


# ──────────────────────────────────────────────
#  Clase base: lógica compartida de conexión
# ──────────────────────────────────────────────
class BaseDatos:
    """
    Clase base que encapsula la conexión a SQLite.
    Cada subclase solo necesita definir su SQL de creación de tabla
    y sus métodos de negocio.
    """

    # Cada subclase sobreescribe esto con su CREATE TABLE
    _sql_crear_tabla = ""

    def conectar(self):
        """Abre la conexión a 'stock.db' y crea la tabla si no existe."""
        try:
            self.conexion = sqlite3.connect("stock.db")
            self.cursor = self.conexion.cursor()
            if self._sql_crear_tabla:
                self.cursor.execute(self._sql_crear_tabla)
                self.conexion.commit()
        except Exception as ex:
            print(f"Error al conectar con la base de datos: {ex}")

    def desconectar(self):
        """Cierra la conexión de forma segura."""
        if hasattr(self, "conexion") and self.conexion:
            self.conexion.close()

    def obtener_todos(self):
        """Devuelve todas las filas de la tabla asociada."""
        self.cursor.execute(f"SELECT * FROM {self._nombre_tabla}")
        return self.cursor.fetchall()

    def obtener_columnas(self):
        """Devuelve la lista de nombres de columnas de la tabla."""
        self.cursor.execute(f"SELECT * FROM {self._nombre_tabla} LIMIT 0")
        return [desc[0] for desc in self.cursor.description]


# ──────────────────────────────────────────────
#  Stock – inventario de productos
# ──────────────────────────────────────────────
class Stock(BaseDatos):
    """
    Maneja la tabla 'stock' con los campos:
      id, cantidad, producto, utilidad, costo, proveedor.
    """

    _nombre_tabla = "stock"
    _sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS stock (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            cantidad  INTEGER,
            producto  TEXT,
            utilidad  REAL,
            costo     REAL,
            proveedor TEXT
        )
    """

    def agregar(self, cantidad, producto, utilidad, costo, proveedor):
        """Inserta un nuevo producto en el inventario."""
        self.cursor.execute(
            "INSERT INTO stock (cantidad, producto, utilidad, costo, proveedor) VALUES (?, ?, ?, ?, ?)",
            (cantidad, producto, utilidad, costo, proveedor),
        )
        self.conexion.commit()

    def eliminar(self, id_producto):
        """Elimina un producto por su ID."""
        self.cursor.execute("DELETE FROM stock WHERE id = ?", (id_producto,))
        self.conexion.commit()

    def actualizar(self, id_producto, cantidad, producto, utilidad, costo, proveedor):
        """Actualiza todos los campos de un producto dado su ID."""
        self.cursor.execute(
            "UPDATE stock SET cantidad=?, producto=?, utilidad=?, costo=?, proveedor=? WHERE id=?",
            (cantidad, producto, utilidad, costo, proveedor, id_producto),
        )
        self.conexion.commit()

    def buscar(self, texto):
        """Busca productos cuyo nombre contenga 'texto' (búsqueda parcial)."""
        self.cursor.execute(
            "SELECT * FROM stock WHERE producto LIKE ?", (f"%{texto}%",)
        )
        return self.cursor.fetchall()


# ──────────────────────────────────────────────
#  Ventas – registro de ventas del día
# ──────────────────────────────────────────────
class Ventas(BaseDatos):
    """
    Maneja la tabla 'ventas'.
    - utilidad = precio_unitario × cantidad (se acumula si el producto ya existe).
    La fecha y hora se generan automáticamente al insertar.
    """

    _nombre_tabla = "ventas"
    _sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS ventas (
            id       INTEGER PRIMARY KEY,
            cantidad INTEGER,
            producto TEXT,
            utilidad REAL DEFAULT 0,
            fecha    DATE DEFAULT (date('now', 'localtime')),
            hora     TIME DEFAULT (time('now', 'localtime'))
        )
    """

    def agregar(self, cantidad, producto, utilidad=0.0):
        """
        Registra una venta.
        - Si el producto ya existe, acumula cantidad y utilidad.
        - Si no existe, crea un registro nuevo.
        """
        self.cursor.execute(
            "SELECT id, cantidad, utilidad FROM ventas WHERE producto = ?",
            (producto,),
        )
        registro = self.cursor.fetchone()

        if registro:
            self.cursor.execute(
                "UPDATE ventas SET cantidad=?, utilidad=? WHERE id=?",
                (registro[1] + cantidad, (registro[2] or 0) + utilidad, registro[0]),
            )
        else:
            self.cursor.execute(
                "INSERT INTO ventas (cantidad, producto, utilidad) VALUES (?, ?, ?)",
                (cantidad, producto, utilidad),
            )
        self.conexion.commit()


# ──────────────────────────────────────────────
#  Ventas Diarias – historial consolidado
# ──────────────────────────────────────────────
class VentasDiarias(BaseDatos):
    """
    Maneja la tabla 'ventas_diarias'.
    Se usa para copiar las ventas del día actual desde la tabla 'ventas'
    como registro histórico permanente.
    """

    _nombre_tabla = "ventas_diarias"
    _sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS ventas_diarias (
            id        INTEGER PRIMARY KEY,
            cantidad  INTEGER,
            producto  TEXT,
            utilidad  REAL,
            costo     REAL,
            proveedor TEXT,
            fecha     TEXT,
            hora      TEXT
        )
    """

    def importar_ventas_hoy(self):
        """
        Copia todos los registros de 'ventas' cuya fecha sea hoy
        hacia la tabla 'ventas_diarias'.
        """
        hoy = datetime.now().strftime("%Y-%m-%d")
        try:
            self.cursor.execute(
                """
                INSERT INTO ventas_diarias (cantidad, producto, utilidad, costo, proveedor, fecha, hora)
                SELECT cantidad, producto, utilidad, costo, proveedor, fecha, hora
                FROM ventas
                WHERE fecha = ?
                """,
                (hoy,),
            )
            self.conexion.commit()
            print(f"Ventas del {hoy} importadas correctamente a ventas_diarias.")
        except Exception as ex:
            print(f"Error al importar ventas: {ex}")
