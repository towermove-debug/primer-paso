import flet as ft
from operaciones import *

class ReposicionApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Reposición de Productos Escasos"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0f172a"
        self.page.window_width = 900
        self.page.window_height = 600

        self.ops = procesos()
        self.productos_escasos = self.obtener_escasos()

        self.setup_ui()

    def obtener_escasos(self):
        todos = self.ops.obtener_todos("stock")
        return [item for item in todos if item[1] < 20]

    def setup_ui(self):
        self.page.clean()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("PRODUCTOS CON STOCK CRÍTICO", size=24, weight="bold", color=ft.Colors.ORANGE_400),
                    ft.Text("Cantidad menor a 20 unidades", size=14, color=ft.Colors.GREY_400),
                    ft.Divider(),
                    self.crear_tabla_escasos(),
                    ft.Divider(),
                    self.crear_formulario_reposicion(),
                ], scroll=ft.ScrollMode.AUTO),
                padding=20,
                bgcolor="#1e293b",
                border_radius=10,
                expand=True
            )
        )

    def crear_tabla_escasos(self):
        if not self.productos_escasos:
            return ft.Text("No hay productos escasos", color=ft.Colors.GREEN_400)

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight="bold")),
                ft.DataColumn(ft.Text("CANTIDAD", weight="bold", color=ft.Colors.RED_300)),
                ft.DataColumn(ft.Text("PRODUCTO", weight="bold")),
                ft.DataColumn(ft.Text("UTILIDAD", weight="bold")),
                ft.DataColumn(ft.Text("COSTO", weight="bold")),
                ft.DataColumn(ft.Text("PROVEEDOR", weight="bold")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(cell))) for cell in row
                ]) for row in self.productos_escasos
            ],
            heading_row_color=ft.Colors.RED_900,
            border=ft.Border.all(1, ft.Colors.ORANGE_700),
            border_radius=10
        )

    def crear_formulario_reposicion(self):
        self.id_input = ft.TextField(label="ID del Producto", width=200)
        self.cantidad_input = ft.TextField(label="Cantidad a agregar", width=200)

        return ft.Container(
            content=ft.Column([
                ft.Text("REPONER PRODUCTO", size=18, weight="bold", color=ft.Colors.BLUE_300),
                ft.Row([self.id_input, self.cantidad_input]),
                ft.Row([
                    ft.FilledButton(
                        "REPONER",
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        bgcolor=ft.Colors.GREEN_700,
                        on_click=self.reponer
                    ),
                ])
            ], spacing=15),
            padding=15,
            bgcolor="#0f172a",
            border_radius=10
        )

    def reponer(self, e):
        try:
            id_producto = self.id_input.value
            cantidad = int(self.cantidad_input.value)

            if not id_producto or not cantidad:
                self.page.snack_bar = ft.SnackBar(ft.Text("Complete todos los campos"))
                self.page.update()
                return

            self.ops.reponer_tabla_stock(id_producto, cantidad)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Producto {id_producto} reponido con +{cantidad} unidades"),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.update()
            self.setup_ui()

        except ValueError:
            self.page.snack_bar = ft.SnackBar(ft.Text("Cantidad debe ser un número"), bgcolor=ft.Colors.RED_700)
            self.page.update()

def main(page: ft.Page):
    ReposicionApp(page)

if __name__ == "__main__":
    ft.app(target=main)