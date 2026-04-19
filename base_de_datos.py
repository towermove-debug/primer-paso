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
    def obtener_cantidad_menores_20(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT cantidad,producto,proveedor FROM {self.tabla} WHERE cantidad < 20")
        return self.cursor.fetchall()

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

    def eliminar_stock(self, id_registro,producto):
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f"DELETE FROM {self.tabla} WHERE id = ? AND producto = ?", (id_registro,producto))
            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al eliminar el stock: {e}")

    def modificar_stock(self, id_registro, cantidad, producto, utilidad, costo, proveedor):
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f'''
            UPDATE {self.tabla} 
            SET cantidad = ?, producto = ?, utilidad = ?, costo = ?, proveedor = ? 
            WHERE id = ?
        ''', (cantidad, producto, utilidad, costo, proveedor, id_registro))
            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al modificar el stock: {e}")
    def obtener_cantidad(self,id_registro, producto):
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f"SELECT cantidad FROM {self.tabla} WHERE id = ? AND producto = ?", (id_registro, producto))
            return self.cursor.fetchone()[0], self.cursor.fetchone()[1]
        except sqlite3.Error as e:
            print(f"Error al obtener la cantidad: {e}")
    def obtener_todo_historial(self,id_registro,costo,proveedor):
        if not self.cursor:
            self.conectar()
        try:
            self.cursor.execute(f"SELECT id_registro,costo,proveedor FROM {self.tabla} WHERE id = ? AND costo = ? AND proveedor = ?", (id_registro, costo, proveedor))
            return self.cursor.fetchone()[0], self.cursor.fetchone()[1], self.cursor.fetchone()[2]
        except sqlite3.Error as e:
            print(f"Error al obtener la cantidad: {e}")


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
    def agregar_venta_diaria(self,id_registro, cantidad, producto, utilidad):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"INSERT INTO {self.tabla} (id_registro, cantidad, producto, utilidad) VALUES (?, ?, ?, ?)", (id_registro, cantidad, producto, utilidad))
        self.conexion.commit()

    def obtener_columnas_utilidad_total(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT utilidad FROM {self.tabla}")
        return self.cursor.fetchall()
    def obtener_columnas_cantidad(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT cantidad FROM {self.tabla}")
        return self.cursor.fetchall()
    def obtener_columnas_producto(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT producto FROM {self.tabla}")
        return self.cursor.fetchall()
    def obtener_columnas_id(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT id FROM {self.tabla}")
        return self.cursor.fetchall()
    def obtener_columnas_hora(self,producto):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT hora FROM {self.tabla} WHERE producto = ?", (producto,))

        return self.cursor.fetchall()
    def obtener_todo(self):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"SELECT * FROM {self.tabla}")
        return self.cursor.fetchall()

class Ventas_general(BaseDB):
    def __init__(self):
        super().__init__()
        self.tabla = "ventas_diarias"

    def crear_tablas_general(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cantidad INTEGER,
                producto TEXT UNIQUE,
                costo REAL,
                utilidad REAL,
                proveedor TEXT,
                hora TEXT,
                fecha DATE DEFAULT (date('now', 'localtime'))
            )
        ''')
        self.conexion.commit()

    def agregar_venta_general(self, cantidad, producto, costo, utilidad, proveedor):
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
        self.cursor.execute(f"DELETE FROM {self.tabla} WHERE nombre = ?", (nombre,))
        self.conexion.commit()
    def actualizar_provider(self, nombre, telefono, correo):
        if not self.cursor:
            self.conectar()
        self.cursor.execute(f"UPDATE {self.tabla} SET telefono = ?, correo = ? WHERE nombre = ?", (telefono, correo, nombre))
        self.conexion.commit()


