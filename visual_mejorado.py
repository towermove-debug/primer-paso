import flet as ft
from operaciones import procesos

class VisualApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sistema de Gestión "
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0f172a"
        self.page.padding = 20
        self.page.window_width = 1200
        self.page.window_height = 800
        
        # Inicializar procesos (base de datos)
        try:
            self.ops = procesos() 
        except Exception as e:
            print(f"Error al conectar DB: {e}")
            self.ops = None

        # Contenedores para formularios (mockups visuales)
        self.form_container = ft.Container(visible=False, padding=20, bgcolor="#1e293b", border_radius=10)
        
        # Contenedor para tablas
        self.table_container = ft.Container(padding=10, bgcolor="#1e293b", border_radius=10, expand=True)

        # Contenedor principal para el contenido dinámico con scroll
        self.main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20
        )

        self.setup_ui()

    def create_button(self, text, icon, color=None, on_click=None):
        return ft.ElevatedButton(
            text,
            icon=icon,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=color if color else ft.Colors.BLUE_700,
                padding=ft.padding.symmetric(horizontal=15, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation={"hovered": 5, "": 1},
            ),
            on_click=on_click
        )

    def create_data_table(self, table_name):
        if not self.ops:
            return ft.Text("Error: Base de datos no conectada", color=ft.Colors.RED_400)
        
        try:
            # Obtener datos reales
            if table_name == "escasos":
                # Lógica especial para escasos (ejemplo: stock < 10)
                todos = self.ops.obtener_todos("stock")
                data = [item for item in todos if item[0] < 10] # Asumiendo cantidad en índice 0
                cols = self.ops.obtener_columnas("stock")
            else:
                data = self.ops.obtener_todos(table_name)
                cols = self.ops.obtener_columnas(table_name)

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
            return ft.Text(f"Error cargando tabla {table_name}: {e}", color=ft.Colors.RED_400)

    def toggle_form(self, title, e=None):
        if e: # Si es llamado por un botón de cerrar o toggle genérico
            if self.form_container.visible:
                self.form_container.visible = False
            else:
                # Si se abre sin título previo (no debería pasar con los nuevos botones)
                self.form_title.value = title if title else "DATOS DE ENTRADA"
                self.form_container.visible = True
        else: # Llamada programática con título
            self.form_title.value = title.upper()
            self.form_container.visible = True
            if title =="Agregar Stock":
                self.form_title.color = ft.Colors.GREEN_400
            elif title =="Agregar Venta":
                self.form_title.color = ft.Colors.GREEN_600
            elif title =="Agregar Proveedor":
                self.form_title.color = ft.Colors.GREEN_600
            elif title =="Borrar Registro":
                self.form_title.color = ft.Colors.RED_600
            elif title =="Eliminar Venta":
                self.form_title.color = ft.Colors.RED_600
            elif title =="Eliminar Proveedor":
                self.form_title.color = ft.Colors.RED_600
            elif title =="Modificar Stock":
                self.form_title.color = ft.Colors.YELLOW_600
            elif title =="Modificar Venta":
                self.form_title.color = ft.Colors.YELLOW_600
            elif title =="Modificar Proveedor":
                self.form_title.color = ft.Colors.YELLOW_600
            
        self.page.update()

    def on_producto_change(self, e):
        text = e.control.value.lower()
        self.similarity_list.controls.clear()
        
        if not text:
            self.similarity_container.visible = False
            self.page.update()
            return
            
        try:
            stock_data = self.ops.obtener_todos("stock")
            productos_db = [row[2] for row in stock_data if row[2]]
        except Exception as err:
            print(f"Error al obtener productos: {err}")
            productos_db = []
            
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
                ft.Container(
                    ft.Text("Producto no encontrado", color=ft.Colors.RED_400, italic=True),
                    padding=10
                )
            )
            self.similarity_container.visible = True
            
        self.page.update()

    def select_producto(self, nombre, text_field):
        text_field.value = nombre.title()
        self.similarity_container.visible = False
        
        try:
            stock_data = self.ops.obtener_todos("stock")
            for row in stock_data:
                if row[2].lower() == nombre.lower():
                    if hasattr(self, 'cantidad_input'):
                        self.cantidad_input.value = str(row[1])
                    if hasattr(self, 'costo_input'):
                        self.costo_input.value = str(row[4])
                    if hasattr(self, 'utilidad_input'):
                        self.utilidad_input.value = str(row[3])
                    if hasattr(self, 'proveedor_input'):
                        self.proveedor_input.value = str(row[5])
                    break
        except Exception as e:
            print(f"Error autocompletando datos: {e}")
            
        self.page.update()

    def on_proveedor_change(self, e):
        text = e.control.value.lower()
        self.prov_similarity_list.controls.clear()
        
        if not text:
            self.prov_similarity_container.visible = False
            self.page.update()
            return
            
        try:
            prov_data = self.ops.obtener_todos("proveedores")
            proveedores_db = [row[1] for row in prov_data if row[1]]
        except Exception as err:
            print(f"Error al obtener proveedores: {err}")
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
                ft.Container(
                    ft.Text("Proveedor no encontrado", color=ft.Colors.RED_400, italic=True),
                    padding=10
                )
            )
            self.prov_similarity_container.visible = True
            
        self.page.update()

    def select_proveedor(self, nombre, text_field):
        text_field.value = nombre.title()
        self.prov_similarity_container.visible = False
        self.page.update()


    def update_view(self, view_name):
        # Limpiar contenido anterior
        self.main_content.controls.clear()
        self.form_container.visible = False
        
        # Titulo dinámico para el formulario
        self.form_title = ft.Text("DATOS DE ENTRADA", size=18, weight="bold", color=ft.Colors.BLUE_200)
        
        # Componentes para similitudes de productos
        self.similarity_list = ft.ListView(spacing=0)
        self.similarity_container = ft.Container(
            content=self.similarity_list,
            visible=False,
            bgcolor="#334155",
            border_radius=5,
            height=120,
        )
        self.producto_input = ft.TextField(
            label="Producto", 
            expand=True,
            on_change=self.on_producto_change
        )
        producto_col = ft.Column([self.producto_input, self.similarity_container], expand=True, spacing=5)
        
        self.cantidad_input = ft.TextField(label="Cantidad", width=100)
        self.costo_input = ft.TextField(label="Costo", width=100)
        self.utilidad_input = ft.TextField(label="Utilidad", width=100)
        
        self.prov_similarity_list = ft.ListView(spacing=0)
        self.prov_similarity_container = ft.Container(
            content=self.prov_similarity_list,
            visible=False,
            bgcolor="#334155",
            border_radius=5,
            height=120,
        )
        self.proveedor_input = ft.TextField(
            label="Proveedor", 
            expand=True,
            on_change=self.on_proveedor_change
        )
        proveedor_col = ft.Column([self.proveedor_input, self.prov_similarity_container], expand=True, spacing=5)
        
        # Definir botones de acción según sección
        actions = []
        form_fields = []
        title_icon = ft.Icons.DASHBOARD
        
        if view_name == "stock":
            title_icon = ft.Icons.INVENTORY
            actions = [
                self.create_button("AGREGAR", ft.Icons.ADD_CIRCLE, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Agregar Stock")),
                self.create_button("MODIFICAR", ft.Icons.EDIT, ft.Colors.ORANGE_700, on_click=lambda _: self.toggle_form("Modificar Stock")),
                self.create_button("BORRAR", ft.Icons.DELETE, ft.Colors.RED_600, on_click=lambda _: self.toggle_form("Borrar Registro")),
            ]
            form_fields = [
                ft.Row([producto_col, self.cantidad_input], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Row([self.costo_input, self.utilidad_input, proveedor_col], vertical_alignment=ft.CrossAxisAlignment.START),
            ]
        elif view_name == "ventas":
            title_icon = ft.Icons.SHOPPING_CART
            actions = [
                self.create_button("AGREGAR VENTA", ft.Icons.ADD_SHOPPING_CART, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Nueva Venta")),
                self.create_button("BORRAR", ft.Icons.DELETE, ft.Colors.RED_600, on_click=lambda _: self.toggle_form("Anular Venta")),
            ]
            form_fields = [
                ft.Row([producto_col, self.cantidad_input], vertical_alignment=ft.CrossAxisAlignment.START),
            ]
        elif view_name == "registro":
            title_icon = ft.Icons.HISTORY
            actions = [
                ft.TextField(label="Buscar registro...", width=300, prefix_icon=ft.Icons.SEARCH),
                self.create_button("BUSCAR", ft.Icons.FILTER_LIST, ft.Colors.BLUE_700),
            ]
            view_name = "historial" # Mapeo de nombre de tabla
        elif view_name == "proveedores":
            title_icon = ft.Icons.PEOPLE
            actions = [
                self.create_button("AGREGAR PROVEEDOR", ft.Icons.PERSON_ADD, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Nuevo Proveedor")),
                self.create_button("BORRAR", ft.Icons.DELETE, ft.Colors.RED_600, on_click=lambda _: self.toggle_form("Eliminar Proveedor")),
            ]
            form_fields = [
                ft.TextField(label="Nombre del Proveedor"),
                ft.Row([ft.TextField(label="Teléfono", expand=True), ft.TextField(label="Correo", expand=True)]),
            ]
        elif view_name == "escasos":
            title_icon = ft.Icons.WARNING
            actions = [
                self.create_button("REFRESCAR", ft.Icons.REFRESH, ft.Colors.AMBER_800, on_click=lambda _: self.update_view("escasos")),
            ]

        # Configurar Formulario si hay campos
        if form_fields:
            self.form_container.content = ft.Column([
                self.form_title,
                *form_fields,
                ft.Row([
                    self.create_button("CONFIRMAR ACCIÓN", ft.Icons.CHECK, ft.Colors.GREEN_700),
                    self.create_button("CERRAR", ft.Icons.CLOSE, ft.Colors.RED_700, on_click=lambda _: self.toggle_form("")),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15)

        # Poblar Tabla
        self.table_container.content = self.create_data_table(view_name)

        # Construir Vista
        self.main_content.controls.extend([
            ft.Row([
                ft.Text(f"GESTIÓN DE {view_name.replace('historial', 'REGISTRO').upper()}", size=24, weight="bold"),
                ft.Icon(title_icon, color=ft.Colors.BLUE_400, size=30)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=10, color=ft.Colors.BLUE_GREY_800),
            ft.Row(actions, spacing=15, wrap=True),
            self.form_container,
            ft.Text("LISTADO DE REGISTROS", size=14, weight="bold", color=ft.Colors.GREY_500),
            ft.Row([self.table_container], scroll=ft.ScrollMode.AUTO), 
        ])
        
        self.page.update()

    def setup_ui(self):
        # Barra de Navegación Superior
        menu_row = ft.Row(
            controls=[
                self.create_button("STOCK", ft.Icons.INVENTORY, on_click=lambda _: self.update_view("stock")),
                self.create_button("VENTAS", ft.Icons.SHOPPING_CART, on_click=lambda _: self.update_view("ventas")),
                self.create_button("REGISTRO", ft.Icons.HISTORY, on_click=lambda _: self.update_view("registro")),
                self.create_button("PROVEEDORES", ft.Icons.PEOPLE, on_click=lambda _: self.update_view("proveedores")),
                self.create_button("ESCASOS", ft.Icons.WARNING, ft.Colors.AMBER_800, on_click=lambda _: self.update_view("escasos")),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True
        )

        # Header de la App
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.BLUE_400, size=32),
                    ft.Text("SISTEMA DE GESTIÓN", size=28, weight="w900", color=ft.Colors.BLUE_400),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                menu_row,
            ]),
            padding=ft.padding.only(bottom=20)
        )

        # Layout Principal
        self.page.add(
            ft.Column([
                header,
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_900),
                self.main_content
            ], expand=True)
        )

def main(page: ft.Page):
    VisualApp(page)

if __name__ == "__main__":
    ft.app(target=main)