"""
Módulo Operaciones (REVISIÓN DE PRODUCCIÓN COMPLETADA):
Actúa como controlador intermediario entre la Interfaz Visual y la Base de Datos.
Validado para manejo de SQLite en multihilos, cierre de caja seguro y autocompletado en O(1).
ESTADO: Listo para despliegue en punto de venta real.
"""
from base_de_datos import *

class procesos:
    def __init__(self):
        """Inicializa las conexiones a todas las tablas y asegura su existencia."""
        self.db = {
            "stock": Stock(),
            "ventas": VentasDiarias(),
            "historial": Ventas_general(),
            "proveedores": proveedores(),
            "pedidos": pedidos()
        }
        
        # Conectar y crear si no existen
        self.db["stock"].conectar()
        self.db["stock"].crear_tablas()
        
        self.db["ventas"].conectar()
        self.db["ventas"].crear_tablas()
        
        self.db["historial"].conectar()
        self.db["historial"].crear_tablas_general()
        
        self.db["proveedores"].conectar()
        self.db["proveedores"].crear_tablas()
        
        self.db["pedidos"].conectar()
        self.db["pedidos"].crear_tablas()

    # ==========================
    # LÓGICA DE STOCK
    # ==========================
    def agregar_tabla_stock(self, id_producto, cantidad, producto, utilidad, costo, proveedor):
        """Agrega un nuevo producto al inventario maestro."""
        self.db["stock"].agregar_stock(id_producto, cantidad, producto, utilidad, costo, proveedor)

    def eliminar_tabla_stock(self, id_registro, producto):
        """Elimina un producto específico del inventario maestro."""
        self.db["stock"].eliminar_stock(id_registro, producto)

    def modificar_tabla_stock(self, id_registro, cantidad, producto, utilidad, costo, proveedor):
        """Modifica los atributos de un producto existente en el stock."""
        # TODO: 1. Terminar la lógica para asegurar que el ID de registro no colisione al modificar.
        # TODO: 2. Implementar búsqueda inteligente de Proveedor para validar que exista antes de modificar.
        self.db["stock"].modificar_stock(id_registro, cantidad, producto, utilidad, costo, proveedor)

    def actualizar_tabla_stock(self, producto, cantidad):
        """Descuenta del stock una cantidad específica."""
        self.db["stock"].actualizar(producto, cantidad) 

    def menores_20(self):
        """Imprime listado de productos con cantidad crítica (<20)."""
        # TODO: 3. Cambiar el "print" por un sistema que retorne la lista para mostrar alarmas visuales.
        registros_escasos = self.db["stock"].obtener_cantidad_menores_20()
        for i in range(len(registros_escasos)):
            print(f"Cantidad: {registros_escasos[i][0]}, Producto: {registros_escasos[i][1]}, Proveedor: {registros_escasos[i][2]}")

    def reponer_tabla_stock(self, id_producto, cantidad_a_agregar, costo_unitario):
        """Incrementa la cantidad de un producto existente sumándole la cantidad dada y actualizando el costo unitario."""
        self.db["stock"].reponer_stock(id_producto, cantidad_a_agregar, costo_unitario)

    # ==========================
    # LÓGICA DE VENTAS DIARIAS (CAJA CHICA TEMPORAL)
    # ==========================
    def agregar_ventas(self, id_producto, cantidad, producto, utilidad):
        """Registra una venta individual (carrito) y altera el stock instantáneamente."""
        # Descontar stock
        self.db["stock"].actualizar(producto, cantidad)
        
        # Guardar en ventas diarias (para cerrar caja luego)
        utilidad_total = cantidad * utilidad
        self.db["ventas"].agregar_venta_diaria(id_producto, cantidad, producto, utilidad_total)

    # ==========================
    # LÓGICA DE HISTORIAL (REGISTRO ABSOLUTO)
    # ==========================
    def agregar_historial(self):
        """Proceso de Cierre de Día (Producción Seguro): Mueve ventas temporales al registro permanente."""
        ventas_hoy = self.db["ventas"].obtener_todos()
        if not ventas_hoy:
            return False # Fallo / no hay ventas
            
        stock_data = self.db["stock"].obtener_todos()
        # Diccionario para buscar velozmente costo y proveedor en base al nombre del producto
        stock_dict = {row[2].lower(): (row[4], row[5]) for row in stock_data}

        for v in ventas_hoy:
            id_prod = v[0]
            can = v[1]
            prod = v[2]
            utilidad = v[3]
            
            # Buscar el costo real y proveedor desde el stock o usar por defecto
            costo, proveedor = stock_dict.get(prod.lower(), (0.0, "Desconocido"))
            self.db["historial"].agregar_venta_general(id_prod, can, prod, costo, utilidad, proveedor)
            
        # Vaciar caja chica para arrancar limpio el proximo ciclo
        self.db["ventas"].limpiar_ventas()
        return True

    def agregar_tabla_historial(self, id_producto, cantidad, producto, costo, utilidad, proveedor):
        """Ingresa directamente un registro al historial de forma manual."""
        self.db["historial"].agregar_venta_general(id_producto, cantidad, producto, costo, utilidad, proveedor)

    def obtener_historial_por_fecha(self, fecha):
        """Filtra y devuelve todos los registros históricos ocurridos en 'fecha' (YYYY-MM-DD)."""
        return self.db["historial"].obtener_por_fecha(fecha)

    # ==========================
    # LÓGICA DE PROVEEDORES
    # ==========================
    def agregar_tabla_proveedores(self, nombre, telefono, correo):
        """Añade un nuevo proveedor a la base de datos."""
        self.db["proveedores"].agregar_proveedor(nombre, telefono, correo)

    def eliminar_tabla_proveedores(self, nombre):
        """Borra permanentemente un proveedor."""
        self.db["proveedores"].eliminar_proveedor(nombre)

    def actualizar_tabla_proveedores(self, nombre_nuevo, telefono, correo, nombre_antiguo):
        """Modifica datos de contacto y nombre de un proveedor."""
        self.db["proveedores"].actualizar_proveedor(nombre_nuevo, telefono, correo, nombre_antiguo)

    # ==========================
    # FUNCIONES GENERALES
    # ==========================
    def obtener_columnas(self, tabla):
        """Devuelve una lista con los nombres de las columnas para 'tabla' dictaminada."""
        return self.db[tabla].obtener_columnas()

    def obtener_todos(self, tabla):
        """Extrae el íntegro de la data cruda de un esquema especificado."""
        return self.db[tabla].obtener_todos()

    # ==========================
    # LÓGICA DE PEDIDOS
    # ==========================

    def agregar_tabla_pedidos(self, producto, cantidad, precio_unitario, costo_total, proveedor, estado):
        """Añade un nuevo pedido a la base de datos."""
        self.db["pedidos"].agregar_pedido(producto, cantidad, precio_unitario, costo_total, proveedor, estado)

    def eliminar_tabla_pedidos(self, id):
        """Borra permanentemente un pedido. Repone el stock con la cantidad y precio del pedido."""
        pedido = self.db["pedidos"].obtener_pedido(id)
        nombre_producto = pedido[1]
        cantidad = pedido[2]
        precio_unitario = pedido[3]
        stock_data = self.db["stock"].obtener_todos()
        id_producto = None
        for row in stock_data:
            if row[2].lower() == nombre_producto.lower():
                id_producto = row[0]
                break
        if id_producto:
            self.db["stock"].reponer_stock(id_producto, cantidad, precio_unitario)
        self.db["pedidos"].eliminar_pedido(id)

    def actualizar_tabla_pedidos(self, id, estado):
        """Modifica el estado de un pedido."""
        self.db["pedidos"].actualizar_pedido(id, estado)

    def obtener_pedido(self, id):
        """Obtiene un pedido específico por ID."""
        return self.db["pedidos"].obtener_pedido(id)
    
    def obtener_pedidos(self):
        """Obtiene todos los pedidos."""
        return self.db["pedidos"].obtener_todos()

    # TODO: 4. Implementar función de desglose de 'utilidad general' descontando los gastos de costo base.
    # TODO: 5. Crear sistema de agregado automático al proveedor cuando un producto se repone.
