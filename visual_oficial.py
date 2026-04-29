import flet as ft
import datetime
from operaciones import *

class VisualApp:
    """Clase principal de la UI del Sistema de Gestión construida con Flet."""

    def __init__(self, page: ft.Page):
        # ---------------------------------------------
        # Configuración Inicial de la Ventana
        # ---------------------------------------------
        self.page = page
        self.page.title = "Sistema de Gestión Maestría"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0f172a"
        self.page.padding = 20
        self.page.window_width = 1200
        self.page.window_height = 800
        
        # ---------------------------------------------
        # Conexión con Controlador Lógico (Base de Datos)
        # ---------------------------------------------
        try:
            self.ops = procesos() 
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            self.ops = None

        # ---------------------------------------------
        # Declaración de Contenedores Globales
        # ---------------------------------------------
        self.form_container = ft.Container(visible=False, padding=20, bgcolor="#1e293b", border_radius=10)
        
        # Estado y contenedor del carrito de compras temporal
        self.carrito_items = []
        self.cart_container = ft.Container(visible=False, padding=20, bgcolor="#1e293b", border_radius=10)
        
        # Contenedor para renderizar tablas dinámicas (Stock, Historial, etc)
        self.table_container = ft.Container(padding=10, bgcolor="#1e293b", border_radius=10, expand=True)

        # Contenedor padre general con soporte a desplazamiento (Scroll)
        self.main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20
        )

        # Tracking de selección para modificaciones (Proveedores)
        self.selected_prov_name = None

        # Lanzar la UI estructurada superior
        self.setup_ui()

    # ==========================================
    # CREADORES DE COMPONENTES VISUALES
    # ==========================================
    def create_button(self, text, icon, color=None, on_click=None):
        """Generador estándar para botones consistentes del sistema."""
        return ft.FilledButton(
            text,
            icon=icon,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=color if color else ft.Colors.BLUE_700,
                padding=ft.Padding(15, 12, 15, 12),
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation={"hovered": 5, "": 1},
            ),
            on_click=on_click
        )

    def create_data_table(self, table_name):
        """Consume datos del backend y los serializa en una ft.DataTable estilizada."""
        if not self.ops:
            return ft.Text("Error crítico: Base de datos inaccesible", color=ft.Colors.RED_400)
        
        try:
            # 1. Traer data cruda filtrando el caso específico
            if table_name == "escasos":
                todos = self.ops.obtener_todos("stock")
                data = [item for item in todos if item[1] < 20] # item[1] corresponde a 'cantidad'
                cols = self.ops.obtener_columnas("stock")
                
            elif hasattr(self, 'filtro_historial_fecha') and self.filtro_historial_fecha and table_name == "historial":
                data = self.ops.obtener_historial_por_fecha(self.filtro_historial_fecha)
                cols = self.ops.obtener_columnas("historial")
                
            else:
                # Comportamiento general (Stock completo, Ventas, Proveedores)
                data = self.ops.obtener_todos(table_name)
                cols = self.ops.obtener_columnas(table_name)

            # 2. Dibujar estructura de Data Table
            return ft.DataTable(
                columns=[ft.DataColumn(ft.Text(col.upper(), weight="bold", color=ft.Colors.BLUE_200)) for col in cols],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                    for row in data
                ],
                heading_row_color=ft.Colors.BLUE_GREY_900,
                border=ft.Border.all(1, ft.Colors.BLUE_GREY_800),
                border_radius=10,
                vertical_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_800),
            )
        except Exception as e:
            return ft.Text(f"Error renderizando reporte de {table_name}: {e}", color=ft.Colors.RED_400)

    # ==========================================
    # MANEJADORES DE UI (COMPORTAMIENTOS DINÁMICOS)
    # ==========================================
    def limpiar_campos_formulario(self):
        """Clears all form input fields."""
        self.id_producto_input.value = ""
        self.producto_input.value = ""
        self.cantidad_input.value = ""
        self.costo_input.value = ""
        self.utilidad_input.value = ""
        self.proveedor_input.value = ""
        # Campos de proveedores
        if hasattr(self, 'prov_nombre_input'): self.prov_nombre_input.value = ""
        if hasattr(self, 'prov_tel_input'): self.prov_tel_input.value = ""
        if hasattr(self, 'prov_correo_input'): self.prov_correo_input.value = ""
        self.selected_prov_name = None
        self.page.update()


    def toggle_form(self, title, e=None):
        """Oculta o muestra el panel de formularios superior, coloreando y titulando dinámicamente."""
        if e is None:
            # Click desde un botón "cerrar" u ocultamiento
            if self.form_container.visible:
                self.limpiar_campos_formulario()
                self.form_container.visible = False
            else:
                self.form_title.value = title if title else "DATOS DE ENTRADA"
                self.form_container.visible = True
                # Colorear títulos para intuición (Verde = Agrega, Rojo = Borra, Amarillo = Modifica)
                if "Agregar" in title or "Nuevo" in title or "Nueva" in title:
                    self.form_title.color = ft.Colors.GREEN_400
                elif "Eliminar" in title or "Borrar" in title or "Anular" in title:
                    self.form_title.color = ft.Colors.RED_600
                elif "Modificar" in title:
                    self.form_title.color = ft.Colors.YELLOW_600
                else:
                    self.form_title.color = ft.Colors.WHITE
        else:  
            # Invocación directa con objetivo (ej: "Agregar Stock")
            self.form_title.value = title.upper()
            self.form_container.visible = True
            
            # Colorear títulos para intuición (Verde = Agrega, Rojo = Borra, Amarillo = Modifica)
            if "Agregar" in title or "Nuevo" in title or "Nueva" in title:
                self.form_title.color = ft.Colors.GREEN_400
            elif "Eliminar" in title or "Borrar" in title or "Anular" in title:
                self.form_title.color = ft.Colors.RED_600
            elif "Modificar" in title:
                self.form_title.color = ft.Colors.YELLOW_600
            else:
                self.form_title.color = ft.Colors.WHITE

        self.page.update()
    
       

    # --- AUTOCOMPLETADO INTELIGENTE (BÚSQUEDAS) ---
    def on_producto_change(self, e):
        """Manejador: busca en tiempo real en la DB productos similares a lo que se teclea."""
        text = e.control.value.lower()
        self.similarity_list.controls.clear()
        
        if not text:
            self.similarity_container.visible = False
            self.page.update()
            return
            
        try:
            stock_data = self.ops.obtener_todos("stock")
            # Extraer sólo string de nombres no vacíos, asumiendo índice 2 es 'producto'
            productos_db = [row[2] for row in stock_data if row[2] is not None]
        except Exception:
            productos_db = []
            
        # Filtrado de coincidencias puras
        coincidencias = [p for p in productos_db if text in p.lower()]
        
        if coincidencias:
            for p in coincidencias:
                self.similarity_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(p.title()),
                        hover_color=ft.Colors.BLUE_GREY_700,
                        on_click=lambda ev, prod=p: self.select_producto(prod, e.control)
                    )
                )
            self.similarity_container.visible = True
        else:
            self.similarity_list.controls.append(
                ft.Container(ft.Text("Producto no encontrado", color=ft.Colors.RED_400, italic=True), padding=10)
            )
            self.similarity_container.visible = True
            
        self.page.update()

    def select_producto(self, nombre, text_field):
        """Disparado al hacer clic en un producto recomendado; pre-rellena todos los cuadros de texto relativos."""
        text_field.value = nombre.title()
        self.similarity_container.visible = False
        
        try:
            stock_data = self.ops.obtener_todos("stock")
            for row in stock_data:
                # row structure: id_producto=0, cantidad=1, producto=2, utilidad=3, costo=4, proveedor=5
                if row[2] and row[2].strip().lower() == nombre.strip().lower():
                    if hasattr(self, 'id_producto_input'):
                        self.id_producto_input.value = str(row[0])
                    if hasattr(self, 'cantidad_input'):
                        # En ventas dejamos cantidad vacía para el usuario, en otros cargamos el stock actual
                        self.cantidad_input.value = "" if self.form_title.value == "NUEVA VENTA" else str(row[1])
                    if hasattr(self, 'costo_input'):
                        self.costo_input.value = str(row[4])
                    if hasattr(self, 'utilidad_input'):
                        self.utilidad_input.value = str(row[3])
                    if hasattr(self, 'proveedor_input'):
                        self.proveedor_input.value = str(row[5])
                    break
        except Exception as e:
            print(f"Error autocompletando métricas de {nombre}: {e}")
            
        self.page.update()

    def on_proveedor_change(self, e):
        """Manejador similar al de productos pero para el input de proveedores."""
        text = e.control.value.lower()
        self.prov_similarity_list.controls.clear()
        
        if not text:
            self.prov_similarity_container.visible = False
            self.page.update()
            return
            
        try:
            prov_data = self.ops.obtener_todos("proveedores")
            proveedores_db = [row[1] for row in prov_data if row[1]] # index 1 es nombre
        except Exception:
            proveedores_db = []
            
        coincidencias = [p for p in proveedores_db if text in p.lower()]
        
        if coincidencias:
            for p in coincidencias:
                self.prov_similarity_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(p.title()),
                        hover_color=ft.Colors.BLUE_GREY_700,
                        on_click=lambda ev, prov=p: self.select_proveedor(prov, e.control)
                    )
                )
            self.prov_similarity_container.visible = True
        else:
            self.prov_similarity_list.controls.append(
                ft.Container(ft.Text("Proveedor no encontrado", color=ft.Colors.RED_400, italic=True), padding=10)
            )
            self.prov_similarity_container.visible = True
            
        self.page.update()

    def select_proveedor(self, nombre, text_field):
        """Consolida la visual de autocompletado en el text field deseado."""
        text_field.value = nombre # Usamos el nombre exacto de la DB para evitar fallos de case-sensitivity
        self.selected_prov_name = nombre # Guardamos el nombre original para modificaciones
        self.prov_similarity_container.visible = False
        
        # Si estamos en la vista de proveedores, cargamos los datos de contacto automáticamente
        try:
            prov_data = self.ops.obtener_todos("proveedores")
            for row in prov_data:
                # row index 1 es nombre, 2 tel, 3 correo
                if row[1] and row[1].strip().lower() == nombre.strip().lower():
                    if hasattr(self, 'prov_tel_input'):
                        self.prov_tel_input.value = str(row[2])
                    if hasattr(self, 'prov_correo_input'):
                        self.prov_correo_input.value = str(row[3])
                    break
        except Exception as e:
            print(f"Error cargando datos del proveedor {nombre}: {e}")
            
        self.page.update()

    # ==========================================
    # CREADOR MAESTRO DE VISTAS (ENRUTADOR VISUAL)
    # ==========================================
    def update_view(self, view_name):
        """Inyecta los elementos funcionales dependiendo de la rama que elija el usuario visualizar."""
        # Limpieza previa del lienzo
        self.main_content.controls.clear()
        self.form_container.visible = False
        self.selected_prov_name = None
        
        # Base titulo dinámico
        self.form_title = ft.Text("DATOS DE ENTRADA", size=18, weight="bold", color=ft.Colors.BLUE_200)
        
        # -----------------------------------------------
        # 1. Definición Global de Campos (Inputs)
        # -----------------------------------------------
        self.id_producto_input = ft.TextField(
            label="Código (ID / Barras)", width=180, icon=ft.Icons.QR_CODE_SCANNER
        )
        
        # Contenedor especial con autocompletador para producto
        self.similarity_list = ft.ListView(spacing=0)
        self.similarity_container = ft.Container(
            content=self.similarity_list, visible=False, bgcolor="#334155", border_radius=5, height=120
        )
        self.producto_input = ft.TextField(label="Producto", expand=True, on_change=self.on_producto_change)
        producto_col = ft.Column([self.producto_input, self.similarity_container], expand=True, spacing=5)
        
        # Finanzas e inventario
        self.cantidad_input = ft.TextField(label="Cantidad", width=100)
        self.costo_input = ft.TextField(label="Costo", width=100)
        self.utilidad_input = ft.TextField(label="Precio/Utilidad", width=100)
        
        # Contenedor especial con autocompletador para proveedores
        self.prov_similarity_list = ft.ListView(spacing=0)
        self.prov_similarity_container = ft.Container(
            content=self.prov_similarity_list, visible=False, bgcolor="#334155", border_radius=5, height=120
        )
        self.proveedor_input = ft.TextField(label="Proveedor", expand=True, on_change=self.on_proveedor_change)
        proveedor_col = ft.Column([self.proveedor_input, self.prov_similarity_container], expand=True, spacing=5)
        
        # Campos específicos para proveedores con autocompletado
        self.prov_nombre_input = ft.TextField(label="Nombre Oficial del Proveedor", on_change=self.on_proveedor_change)
        self.prov_tel_input = ft.TextField(label="Teléfono", expand=True)
        self.prov_correo_input = ft.TextField(label="Correo Electrónico", expand=True)
        
        # Reset de filtros ajenos
        if view_name not in ["registro", "historial"]:
            self.filtro_historial_fecha = None
            
        # Configurables según el "Routing" / Menú clickeado
        actions = []
        extras_ui = []
        form_fields = []
        title_icon = ft.Icons.DASHBOARD
        
        # -----------------------------------------------
        # 2. Configuración Lógica de Cada Vista Privada
        # -----------------------------------------------

        # VISTA STOCK MAESTRO
        if view_name == "stock":
            title_icon = ft.Icons.INVENTORY
            actions = [
                self.create_button("AGREGAR", ft.Icons.ADD_CIRCLE, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Agregar Stock")),
                self.create_button("MODIFICAR", ft.Icons.EDIT, ft.Colors.ORANGE_700, on_click=lambda _: self.toggle_form("Modificar Stock")),
                self.create_button("BORRAR", ft.Icons.DELETE, ft.Colors.RED_600, on_click=lambda _: self.toggle_form("Eliminar Stock")),
            ]
            form_fields = [
                ft.Row([self.id_producto_input, producto_col, self.cantidad_input], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Row([self.costo_input, self.utilidad_input, proveedor_col], vertical_alignment=ft.CrossAxisAlignment.START),
            ]

        # VISTA VENTAS Y CAJA DIARIA
        elif view_name == "ventas":
            title_icon = ft.Icons.SHOPPING_CART
            actions = [
                self.create_button("NUEVO PEDIDO", ft.Icons.ADD_SHOPPING_CART, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Nueva Venta")),
            ]
            form_fields = [
                ft.Row([self.id_producto_input, producto_col, self.cantidad_input], vertical_alignment=ft.CrossAxisAlignment.START),
            ]
            
            # A) Metricas Diarias
            try:
                ventas_hoy = self.ops.obtener_todos("ventas") # tabla temporal
                qty_ventas = len(ventas_hoy)
                total_ventas = sum([v[3] for v in ventas_hoy]) if ventas_hoy else 0.0
            except:
                qty_ventas = 0; total_ventas = 0.0
                
            extras_ui.append(
                ft.Container(
                    ft.Row([
                        ft.Text(f"VENTAS HOY: {qty_ventas}", color=ft.Colors.BLUE_300, weight="bold", size=18),
                        ft.Text(f"TOTAL ACUMULADO: ${total_ventas:.2f}", color=ft.Colors.GREEN_400, weight="bold", size=18),
                        self.create_button("CERRAR Y GUARDAR DÍA", ft.Icons.SAVE, ft.Colors.ORANGE_800, on_click=self.cerrar_dia)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15, bgcolor="#1e293b", border_radius=10, margin=ft.Margin(0, 0, 0, 10)
                )
            )
            
            # B) Grilla de Carrito
            if self.carrito_items:
                total_pedido = sum(i['subtotal'] for i in self.carrito_items)
                cart_rows = [
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item['id_producto'])),
                        ft.DataCell(ft.Text(str(item['cantidad']))),
                        ft.DataCell(ft.Text(item['producto'])),
                        ft.DataCell(ft.Text(f"${item['precio']:.2f}")),
                        ft.DataCell(ft.Text(f"${item['subtotal']:.2f}")),
                        ft.DataCell(ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_400, on_click=lambda ev, cur_idx=idx: self.eliminar_del_carrito(cur_idx)))
                    ]) for idx, item in enumerate(self.carrito_items)
                ]
                
                self.cart_container.content = ft.Column([
                    ft.Text("PEDIDO ACTUAL (CARRITO EN CUBIERTA)", size=18, weight="bold", color=ft.Colors.GREEN_300),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("CODIGO")), ft.DataColumn(ft.Text("CANT.")),
                            ft.DataColumn(ft.Text("PRODUCTO")), ft.DataColumn(ft.Text("PRECIO")),
                            ft.DataColumn(ft.Text("SUBTOTAL")), ft.DataColumn(ft.Text("ACCIÓN")),
                        ],
                        rows=cart_rows, border=ft.Border.all(1, ft.Colors.BLUE_GREY_800), border_radius=5
                    ),
                    ft.Row([
                        ft.Text(f"TOTAL A PAGAR: ${total_pedido:.2f}", size=22, weight="bold", color=ft.Colors.YELLOW_400),
                        self.create_button("FINALIZAR PAGO Y ENTREGAR", ft.Icons.PAYMENTS, ft.Colors.GREEN_800, on_click=self.finalizar_venta)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
                self.cart_container.visible = True
            else:
                self.cart_container.visible = False

        # VISTA DE REGISTRO HISTÓRICO
        elif view_name in ["registro", "historial"]:
            title_icon = ft.Icons.HISTORY
            
            self.fecha_input = ft.TextField(
                label="Fecha Limitante (YYYY-MM-DD)", 
                width=220, 
                value=self.filtro_historial_fecha if hasattr(self, 'filtro_historial_fecha') and self.filtro_historial_fecha else datetime.date.today().strftime('%Y-%m-%d')
            )
            
            actions = [
                self.fecha_input,
                self.create_button("FILTRAR POR DÍA", ft.Icons.FILTER_LIST, ft.Colors.BLUE_700, on_click=self.filtrar_historial),
                self.create_button("VACIAR FILTRO Y VER TODOS", ft.Icons.LIST, ft.Colors.GREY_600, on_click=lambda _: self.limpiar_filtro_historial()),
                
            ]
            view_name = "historial"

        # VISTA DE PROVEEDORES Y CONTACTOS
        elif view_name == "proveedores":
            title_icon = ft.Icons.PEOPLE
            actions = [
                self.create_button("AGREGAR ALIANZA", ft.Icons.PERSON_ADD, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Nuevo Proveedor")),
                self.create_button("MODIFICAR", ft.Icons.EDIT, ft.Colors.ORANGE_700, on_click=lambda _: self.toggle_form("Modificar Proveedor")),
                self.create_button("BORRAR", ft.Icons.DELETE, ft.Colors.RED_600, on_click=lambda _: self.toggle_form("Eliminar Proveedor")),
            ]
            
            # Columna con buscador para el nombre
            prov_name_col = ft.Column([self.prov_nombre_input, self.prov_similarity_container], spacing=5)
            
            form_fields = [
                prov_name_col,
                ft.Row([self.prov_tel_input, self.prov_correo_input]),
            ]

        # VISTA DE ALARMAS Y ESCASEZ
        elif view_name == "escasos":
            title_icon = ft.Icons.WARNING
            actions = [
                self.create_button("REPONER", ft.Icons.ADD_SHOPPING_CART, ft.Colors.GREEN_700, on_click=self.abrir_reposicion),
            ]

        # -----------------------------------------------
        # 3. Empaquetado Final de Contenedores de Formulario y Visores
        # -----------------------------------------------
        if form_fields:
            self.form_container.content = ft.Column([
                self.form_title,
                *form_fields,
                ft.Row([
                    self.create_button("CONFIRMAR ACCIÓN", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_700, on_click=self.procesar_accion),
                    self.create_button("DESCARTAR", ft.Icons.CANCEL, ft.Colors.RED_700, on_click=lambda _: self.toggle_form("")),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15)

        self.table_container.content = self.create_data_table(view_name)

        # -----------------------------------------------
        # 4. Acople Principal de Pantalla
        # -----------------------------------------------
        self.main_content.controls.extend([
            ft.Row([
                ft.Text(f"PANEL: {view_name.replace('historial', 'REGISTRO DE OPERACIONES').upper()}", size=24, weight="bold"),
                ft.Icon(title_icon, color=ft.Colors.BLUE_400, size=30)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=10, color=ft.Colors.BLUE_GREY_800),
            *extras_ui,
            ft.Row(actions, spacing=15, wrap=True),
            self.form_container,
            self.cart_container,
            ft.Text("SALIDA DE DATOS TABULARES", size=14, weight="bold", color=ft.Colors.GREY_500),
            ft.Row([self.table_container], scroll=ft.ScrollMode.AUTO), 
        ])
        
        self.page.update()

    # ==========================================
    # LOGICAS EMPRESARIALES ACTIVAS (ON-CLICKS)
    # ==========================================
    def procesar_accion(self, e):
        """Intérprete general de acciones de control desde formularios emergentes (Insert, Updates, Deletes)."""
        titulo_accion = self.form_title.value.upper() if self.form_title.value else ""
        
        try:
            # FLUJO STOCK MAESTRO
            if titulo_accion == "AGREGAR STOCK":
                id_prod = self.id_producto_input.value
                can = int(self.cantidad_input.value) if self.cantidad_input.value else 0
                prod = self.producto_input.value
                util = float(self.utilidad_input.value.replace(",", ".")) if self.utilidad_input.value else 0.0
                costo = float(self.costo_input.value.replace(",", ".")) if self.costo_input.value else 0.0
                prov = self.proveedor_input.value
                
                self.ops.agregar_tabla_stock(id_prod, can, prod, util, costo, prov)
                self.page.snack_bar = ft.SnackBar(ft.Text("Transacción exitosa: Lote de inventario agregado!"), bgcolor=ft.Colors.GREEN_700)
                self.page.snack_bar.open = True
                self.update_view("stock")

            elif titulo_accion == "MODIFICAR STOCK":
                id_prod = self.id_producto_input.value
                can = int(self.cantidad_input.value) if self.cantidad_input.value else 0
                prod = self.producto_input.value
                util = float(self.utilidad_input.value.replace(",", ".")) if self.utilidad_input.value else 0.0
                costo = float(self.costo_input.value.replace(",", ".")) if self.costo_input.value else 0.0
                prov = self.proveedor_input.value
                
                # En esta UI, usamos el ID que está en el campo (o 0 si no se usa ID para búsqueda)
                self.ops.modificar_tabla_stock(id_prod, can, prod, util, costo, prov)
                self.page.snack_bar = ft.SnackBar(ft.Text("Éxito: Producto actualizado en base de datos."), bgcolor=ft.Colors.ORANGE_700)
                self.page.snack_bar.open = True
                self.update_view("stock")

            elif titulo_accion == "ELIMINAR STOCK":
                prod = self.producto_input.value
                # Se descarta ID ficticio "0" en esta version simple de UI
                self.ops.eliminar_tabla_stock(0, prod)
                self.page.snack_bar = ft.SnackBar(ft.Text("Transacción exitosa: Ítem purgado del sistema."), bgcolor=ft.Colors.GREEN_700)
                self.page.snack_bar.open = True
                self.update_view("stock")

            # FLUJO PROVEEDORES
            elif titulo_accion == "NUEVO PROVEEDOR":
                nombre = self.prov_nombre_input.value.strip() if self.prov_nombre_input.value else ""
                tel = self.prov_tel_input.value
                correo = self.prov_correo_input.value
                
                if not nombre:
                    raise ValueError("El nombre del proveedor es obligatorio.")
                
                self.ops.agregar_tabla_proveedores(nombre, tel, correo)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Alianza con {nombre} registrada exitosamente!"), bgcolor=ft.Colors.GREEN_700)
                self.page.snack_bar.open = True
                self.update_view("proveedores")

            elif titulo_accion == "MODIFICAR PROVEEDOR":
                nombre_nuevo = self.prov_nombre_input.value.strip() if self.prov_nombre_input.value else ""
                tel = self.prov_tel_input.value
                correo = self.prov_correo_input.value
                
                if not nombre_nuevo:
                    raise ValueError("Seleccione un proveedor para modificar.")
                
                # Si no hay selección previa, asumimos que el nombre actual es el que se quiere modificar
                nombre_antiguo = self.selected_prov_name if self.selected_prov_name else nombre_nuevo
                
                self.ops.actualizar_tabla_proveedores(nombre_nuevo, tel, correo, nombre_antiguo)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Datos de {nombre_nuevo} actualizados correctamente."), bgcolor=ft.Colors.ORANGE_700)
                self.page.snack_bar.open = True
                self.selected_prov_name = None
                self.update_view("proveedores")

            elif titulo_accion == "ELIMINAR PROVEEDOR":
                nombre = self.prov_nombre_input.value.strip() if self.prov_nombre_input.value else ""
                if not nombre:
                    raise ValueError("Indique el nombre del proveedor a eliminar.")
                    
                self.ops.eliminar_tabla_proveedores(nombre)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Proveedor {nombre} eliminado del registro."), bgcolor=ft.Colors.RED_700)
                self.page.snack_bar.open = True
                self.update_view("proveedores")

            # FLUJO VENTAS DE CAJA
            elif titulo_accion == "NUEVA VENTA":
                id_prod = self.id_producto_input.value
                can = int(self.cantidad_input.value) if self.cantidad_input.value else 0
                prod = self.producto_input.value
                util = float(self.utilidad_input.value.replace(",", ".")) if self.utilidad_input.value else 0.0
                
                # Aislamiento temporal hasta que pague
                self.carrito_items.append({
                    "id_producto": id_prod, "cantidad": can, "producto": prod,
                    "precio": util, "subtotal": can * util
                })
                
                self.page.snack_bar = ft.SnackBar(ft.Text(f"[{can}X] {prod} acoplado a la lista."), bgcolor=ft.Colors.BLUE_700)
                self.page.snack_bar.open = True
                
                # Reseteos de agilidad
                self.id_producto_input.value = ""
                self.cantidad_input.value = ""
                self.producto_input.value = ""
                self.update_view("ventas")

        except ValueError as ve:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Validación: {ve}"), bgcolor=ft.Colors.RED_700)
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error Genérico Interno: {ex}"), bgcolor=ft.Colors.RED_900)
            self.page.snack_bar.open = True
            self.page.update()

    def eliminar_del_carrito(self, index):
        """Descarta mercancía temporalmente asignada a un cliente sin pasarlo por caja."""
        if 0 <= index < len(self.carrito_items):
            self.carrito_items.pop(index)
            self.page.snack_bar = ft.SnackBar(ft.Text("Descartado de la compra en curso"), bgcolor=ft.Colors.ORANGE_700)
            self.page.snack_bar.open = True
            self.update_view("ventas")

    def finalizar_venta(self, e):
        """Dispara en ráfaga todas las ventas contenidas en el pedido y descuenta el stock en BD oficial."""
        try:
            for item in self.carrito_items:
                self.ops.agregar_ventas(item['id_producto'], item['cantidad'], item['producto'], item['precio'])
            
            self.carrito_items.clear()
            self.page.snack_bar = ft.SnackBar(ft.Text("¡TICKET GENERADO! Stocks alterados correspondientemente."), bgcolor=ft.Colors.GREEN_700)
            self.page.snack_bar.open = True
            
            self.form_container.visible = False
            self.update_view("ventas")
            
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error crítico asentando cajas: {ex}"), bgcolor=ft.Colors.RED_700)
            self.page.snack_bar.open = True
            self.page.update()

    def cerrar_dia(self, e):
        """Consolida las ventas individuales del día enviándolas al fichero imborrable histórico."""
        res = self.ops.agregar_historial()
        if res:
            self.page.snack_bar = ft.SnackBar(ft.Text("Z-Cierre exitoso. Bitácoras generadas y enviadas al Registro."), bgcolor=ft.Colors.GREEN_700)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Sistema detecta 0 movimientos de capital, no se guardó historial."), bgcolor=ft.Colors.ORANGE_700)
        self.page.snack_bar.open = True
        self.update_view("ventas")

    def filtrar_historial(self, e):
        """Refresca la red de memoria buscando específicamente en una fecha designada."""
        self.filtro_historial_fecha = self.fecha_input.value
        self.update_view("registro")

    def limpiar_filtro_historial(self):
        """Desaparece el filtro temporal y reinyecta 100% registros contables a la UI."""
        self.filtro_historial_fecha = None
        self.update_view("registro")

    def abrir_reposicion(self, e):
        """Abre la ventana de reposición de productos escasos."""
        import subprocess
        import sys
        subprocess.Popen([sys.executable, "escasos_reposicion.py"])

  

    # ==========================================
    # CABLEADO INICIAL DEL ENTORNO APP MAESTRA
    # ==========================================
    def setup_ui(self):
        """Enmarca la decoración header base y botones primordiales que persisten en la aplicación."""
        menu_row = ft.Row(
            controls=[
                self.create_button("MAESTRO DE STOCK", ft.Icons.INVENTORY, on_click=lambda _: self.update_view("stock")),
                self.create_button("CAJA Y VENTAS", ft.Icons.SHOPPING_CART, on_click=lambda _: self.update_view("ventas")),
                self.create_button("BITÁCORA HISTÓRICA", ft.Icons.HISTORY, ft.Colors.BLUE_GREY_700, on_click=lambda _: self.update_view("registro")),
                self.create_button("ALIANZAS CORPORATIVAS", ft.Icons.PEOPLE, on_click=lambda _: self.update_view("proveedores")),
                self.create_button("INVENTARIO EN RIESGO", ft.Icons.WARNING, ft.Colors.AMBER_800, on_click=lambda _: self.update_view("escasos")),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True
        )

        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.BLUE_400, size=42),
                    ft.Text("ERP MANAGEMENT SYS", size=32, weight="w900", color=ft.Colors.BLUE_400),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                menu_row,
            ]),
            padding=ft.Padding(0, 0, 0, 20)
        )

        self.page.add(
            ft.Column([
                header,
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_900),
                self.main_content
            ], expand=True)
        )


def main(page: ft.Page):
    """Instancia del entry-point para el framework de UI flet."""
    VisualApp(page)

if __name__ == "__main__":
    ft.run(main)