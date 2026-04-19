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
        self.page.update()

    def update_view(self, view_name):
        # Limpiar contenido anterior
        self.main_content.controls.clear()
        self.form_container.visible = False
        
        # Titulo dinámico para el formulario
        self.form_title = ft.Text("DATOS DE ENTRADA", size=18, weight="bold", color=ft.Colors.BLUE_200)
        
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
                ft.Row([ft.TextField(label="Producto", expand=True), ft.TextField(label="Cantidad", width=100)]),
                ft.Row([ft.TextField(label="Costo", width=100), ft.TextField(label="Utilidad", width=100), ft.TextField(label="Proveedor", expand=True)]),
            ]
        elif view_name == "ventas":
            title_icon = ft.Icons.SHOPPING_CART
            actions = [
                self.create_button("AGREGAR VENTA", ft.Icons.ADD_SHOPPING_CART, ft.Colors.GREEN_600, on_click=lambda _: self.toggle_form("Nueva Venta")),
                self.create_button("BORRAR", ft.Icons.DELETE, ft.Colors.RED_600, on_click=lambda _: self.toggle_form("Anular Venta")),
            ]
            form_fields = [
                ft.Row([ft.TextField(label="Producto", expand=True), ft.TextField(label="Cantidad", width=100)]),
                ft.TextField(label="Utilidad (%)", width=150),
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