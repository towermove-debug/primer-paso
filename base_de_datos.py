import sqlite3

class BaseDB:
    def __init__(self, db_name="stock.db"):
        self.db_name = db_name
        self.conexion = None
        self.cursor = None

    def conectar(self):
        self.conexion = sqlite3.connect(self.db_name)
        self.cursor = self.conexion.cursor()
        

    def obtener_columnas(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"PRAGMA table_info({self.tabla})")
        return [col[1] for col in self.cursor.fetchall()]

    def obtener_todos(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT * FROM {self.tabla}")
        return self.cursor.fetchall()
    
    

class Stock(BaseDB):
    def __init__(self):
        super().__init__()
        self.tabla = "stock"

    def crear_tablas(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cantidad INTEGER,
                producto TEXT,
                utilidad REAL,
                costo REAL,
                proveedor TEXT
            )
        ''')#bien 
        self.conexion.commit()

    def actualizar(self, producto, cantidad):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"UPDATE {self.tabla} SET cantidad = cantidad - ? WHERE producto = ?", (cantidad, producto))
        self.conexion.commit()
    def agregar_stock(self, cantidad, producto, utilidad, costo, proveedor):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (cantidad, producto, utilidad, costo, proveedor) VALUES (?, ?, ?, ?, ?)", (cantidad, producto, utilidad, costo, proveedor))
        self.conexion.commit()

    def eliminar_stock(self, producto):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"DELETE FROM {self.tabla} WHERE producto = ?", (producto,))
        self.conexion.commit()

    def modificar_stock(self, id_registro, cantidad, producto, utilidad, costo, proveedor):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f'''
            UPDATE {self.tabla} 
            SET cantidad = ?, producto = ?, utilidad = ?, costo = ?, proveedor = ? 
            WHERE id = ?
        ''', (cantidad, producto, utilidad, costo, proveedor, id_registro))
        self.conexion.commit()

class VentasDiarias(BaseDB):
    def __init__(self):
        super().__init__()
        self.tabla = "ventas"

    def crear_tablas(self):
        # Crear tabla ventas según lo solicitado
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cantidad INTEGER,
                producto TEXT,
                utilidad REAL,
                hora TIME DEFAULT (time('now', 'localtime'))
            )
        ''')
        self.conexion.commit()
    def agregar_venta(self, cantidad, producto, utilidad):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (cantidad, producto, utilidad) VALUES (?, ?, ?)", (cantidad, producto, utilidad))
        self.conexion.commit()

class Ventas(BaseDB):
    def __init__(self):
        super().__init__()
        self.tabla = "ventas_diarias"

    def crear_tablas(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cantidad INTEGER,
                producto TEXT,
                costo REAL,
                utilidad REAL,
                proveedor TEXT,
                fecha DATE DEFAULT (date('now', 'localtime')),
                 hora TIME DEFAULT (time('now', 'localtime'))
            )
        ''')
        self.conexion.commit()

    def agregar_venta(self, cantidad, producto, costo, utilidad, proveedor):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (cantidad, producto, costo, utilidad, proveedor) VALUES (?, ?, ?, ?, ?)", (cantidad, producto, costo, utilidad, proveedor))
        self.conexion.commit()
    

class proveedores(BaseDB):
    def __init__(self):
        super().__init__()
        self.tabla = "proveedores"

    def crear_tablas(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
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
        self.cursor.execute(f"DELETE FROM {self.tabla} WHERE nombre = ?", (nombre,))
        self.conexion.commit()
    def actualizar_provider(self, nombre, telefono, correo):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"UPDATE {self.tabla} SET telefono = ?, correo = ? WHERE nombre = ?", (telefono, correo, nombre))
        self.conexion.commit()


