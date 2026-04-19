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

   



    #paraq los gastos filtrar y separar productos y proveedores 
    #yy ara reposicion hacer sistema de agregado de productos nuevos 

    def agregar_tabla_stock(self, cantidad, producto, utilidad, costo, proveedor):
        proveedor_selecionado=self.db["proveedores"].obtener_nombre(proveedor)
        self.db["stock"].agregar_stock(cantidad, producto, utilidad, costo, proveedor_selecionado)

    def eliminar_tabla_stock(self, id_registro,producto):
        self.db["stock"].eliminar_stock(id_registro,producto)

    def modificar_tabla_stock(self, id_registro, cantidad, producto, utilidad, costo, proveedor):
        proveedor_selecionado=self.db["proveedores"].obtener_nombre(proveedor)
        self.db["stock"].modificar_stock(id_registro, cantidad, producto, utilidad, costo, proveedor_selecionado)

    def agregar_ventas(self, cantidad, producto, utilidad):#vender diaria 
        cantidad_previa = self.db["stock"].obtener_cantidad(id_registro,producto)
        cantidad_restante = cantidad_previa - cantidad
        self.db["stock"].actualizar(producto, cantidad_restante)
        #multilpicar cantidad por utilidad para obtener la utilidad total
        utilidad_total = cantidad * utilidad
        self.db["ventas"].agregar_venta_diaria(id_registro,cantidad, producto, utilidad_total)


    def agregar_historial(self):
        #de stock debo obntener id,costo,proveedor
       id_producto,costo,proveedores= self.db["stock"].obtener_todo_historial()
       #de ventas debo obtener cantidad producto,utilidad,hora
       cantidad,producto,utilidad,hora= self.db["ventas"].obtener_todo()

    def menores_20(self):
        #para la tabla de escasos un filtro de elementos menores a 20
        registros_escasos = self.db["stock"].obtener_cantidad_menores_20()
        for i in range(len(registros_escasos)):
            print(f"Cantidad: {registros_escasos[i][0]}, Producto: {registros_escasos[i][1]}, Proveedor: {registros_escasos[i][2]}")
        #agregarse en la tabla de escasos de visual 

      


