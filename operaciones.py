from base_de_datos import *

class procesos:
    def __init__(self):
        self.db = {
            "stock": Stock(),
            "ventas": VentasDiarias(),
            "historial": Ventas(),
            "proveedores": proveedores()
        }
        self.db["stock"].conectar()
        self.db["ventas"].conectar()
        self.db["historial"].conectar()
        self.db["proveedores"].conectar()



    

    def agregar_tabla_stock(self, cantidad, producto, utilidad, costo, proveedor):
        self.db["stock"].agregar_stock(cantidad, producto, utilidad, costo, proveedor)

    def eliminar_tabla_stock(self, id_registro):
        self.db["stock"].eliminar_stock(id_registro)

    def modificar_tabla_stock(self, id_registro, cantidad, producto, utilidad, costo, proveedor):
        self.db["stock"].modificar_stock(id_registro, cantidad, producto, utilidad, costo, proveedor)

    def agregar_tabla_ventas(self, cantidad, producto, utilidad):
        self.db["ventas"].agregar_venta(cantidad, producto, utilidad)

    def agregar_tabla_historial(self, cantidad, producto, costo, utilidad, proveedor):
        self.db["historial"].agregar_venta(cantidad, producto, costo, utilidad, proveedor)

    def agregar_tabla_proveedores(self, nombre, telefono, correo):
        self.db["proveedores"].agregar_proveedor(nombre, telefono, correo)

    def eliminar_tabla_proveedores(self, nombre):
        self.db["proveedores"].eliminar_proveedor(nombre)

    def actualizar_tabla_proveedores(self, nombre, telefono, correo):
        self.db["proveedores"].actualizar_proveedor(nombre, telefono, correo)

    def actualizar_tabla_stock(self, producto, cantidad):
        self.db["stock"].actualizar(producto, cantidad) 

    def obtener_columnas(self, tabla):
        return self.db[tabla].obtener_columnas()

    def obtener_todos(self, tabla):
        return self.db[tabla].obtener_todos()


   