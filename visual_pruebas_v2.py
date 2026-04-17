import flet as ft
from base_de_datos import Stock, Ventas, VentasDiarias

# --- CONFIGURACIÓN Y ESTILOS ---
THEME_COLOR = "blue"
BG_COLOR = ft.Colors.BLUE_900  # Color más oscuro para el fondo de cabeceras
BORDER_COLOR = "blue900"
TEXT_COLOR = "white"

def main(page: ft.Page):
    """
    Función principal de la aplicación.
    Configura la página, inicializa la DB y construye la interfaz.
    """
    # Configuración de la ventana
    page.title = "Sistema de Gestión de Stock (Versión Oscura)"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # --- INICIALIZACIÓN DE BASE DE DATOS ---
    # Centralizamos las conexiones en un diccionario
    db = {
        "stock": Stock(),
        "ventas": Ventas(),
        "historial": VentasDiarias()
    }
    for d in db.values(): d.conectar()

    # --- ELEMENTOS DE ESTADO ---
    # Container dinámico para alternar entre formularios y tablas
    container_formulario = ft.Container()
    container_tabla = ft.Container(expand=True)
    
    # Store para el producto seleccionado en la sección de ventas
    seleccion = {"datos": None}

    # --- UTILIDADES ---
    def mostrar_notificacion(texto, color="blue"):
        """Muestra un mensaje SnackBar en la parte inferior."""
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # --- COMPONENTES ---

    def crear_buscador():
        """Genera el campo de búsqueda con lista de resultados dinámica."""
        txt_busqueda = ft.TextField(
            label="Buscar Producto", 
            expand=True, 
            border=ft.InputBorder.OUTLINE,
            hint_text="Escriba el nombre...",
            on_change=lambda e: actualizar_lista(e.control.value)
        )
        lista_res = ft.ListView(height=0, spacing=5)

        def actualizar_lista(texto):
            lista_res.controls.clear()
            if texto:
                resultados = db["stock"].buscar(texto)
                for prod in resultados:
                    def al_seleccionar(_, p=prod):
                        txt_busqueda.value = p[2]
                        lista_res.height = 0
                        on_product_click(p)

                    lista_res.controls.append(
                        ft.ListTile(
                            title=ft.Text(prod[2]),
                            subtitle=ft.Text(f"Stock: {prod[1]} | Precio: ${prod[4]}"),
                            on_click=al_seleccionar,
                            dense=True
                        )
                    )
                lista_res.height = min(len(resultados) * 50, 200)
            else:
                lista_res.height = 0
            page.update()

        return ft.Column([txt_busqueda, lista_res], spacing=0, expand=True), txt_busqueda

    def on_product_click(prod):
        """Manejador global para cuando se selecciona un producto del buscador."""
        seleccion["datos"] = prod
        # Forzamos la actualización de la info visual en el formulario de ventas
        actualizar_formulario_ventas(prod)

    def construir_datos_tabla(nombre):
        """Genera un DataTable basado en el nombre de la sección."""
        # Configuración de visualización por tabla
        config = {
            "stock": {"obj": db["stock"], "excluir": []},
            "ventas": {"obj": db["ventas"], "excluir": ["costo", "proveedor"]},
            "historial": {"obj": db["historial"], "excluir": []}
        }
        
        target = config[nombre]
        columnas_all = target["obj"].obtener_columnas()
        datos_all = target["obj"].obtener_todos()
        
        # Filtrado de columnas visuales
        indices = [i for i, col in enumerate(columnas_all) if col not in target["excluir"]]
        columnas_final = [columnas_all[i] for i in indices]

        # Cálculo de utilidad total (asumiendo que 'utilidad' está en las columnas)
        total_utilidad = 0
        if "utilidad" in columnas_all:
            idx_util = columnas_all.index("utilidad")
            total_utilidad = sum(float(fila[idx_util] or 0) for fila in datos_all)

        return ft.DataTable(
            expand=True,
            border=ft.Border.all(2, BORDER_COLOR),
            border_radius=10,
            column_spacing=50,
            heading_row_color=BG_COLOR,
            columns=[ft.DataColumn(ft.Text(col.upper(), weight="bold")) for col in columnas_final],
            rows=[
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(fila[i]))) for i in indices])
                for fila in datos_all
            ]
        ), total_utilidad

    def construir_formulario(nombre):
        """Construye el layout de control superior para cada sección."""
        if nombre == "stock":
            f_cant = ft.TextField(label="Cantidad", width=100)
            f_prod = ft.TextField(label="Producto", expand=True)
            f_util = ft.TextField(label="Utilidad", width=100)
            f_cost = ft.TextField(label="Costo", width=100)
            f_prov = ft.TextField(label="Proveedor", width=150)

            def agregar(_):
                if f_prod.value:
                    db["stock"].agregar(
                        int(f_cant.value or 0), f_prod.value, 
                        float(f_util.value or 0), float(f_cost.value or 0), f_prov.value
                    )
                    cargar_vistas("stock")
                    mostrar_notificacion("Producto añadido al inventario", "green")

            return ft.Column([
                ft.Text("GESTIÓN DE INVENTARIO", weight="bold", size=18),
                ft.Row([f_cant, f_prod, f_util, f_cost, f_prov, ft.ElevatedButton("AGREGAR", on_click=agregar, icon=ft.Icons.ADD, style=ft.ButtonStyle(bgcolor=BG_COLOR,shape=ft.RoundedRectangleBorder(radius=10)))])
            ])

        if nombre == "ventas":
            # Creamos los elementos que necesitan ser referenciados globalmente en esta vista
            f_cant = ft.TextField(label="Cant.", width=80, value="1")
            info_txt = ft.Text("Busque un producto para iniciar la venta...", italic=True, color="grey")
            buscador_col, txt_input = crear_buscador()

            def registrar(_):
                if not seleccion["datos"]: return
                try:
                    cant = int(f_cant.value or 0)
                    prod = seleccion["datos"]
                    
                    if cant > prod[1]:
                        return mostrar_notificacion("Error: Stock insuficiente", "red")

                    # Lógica de venta
                    db["ventas"].agregar(
                        cantidad=cant, producto=prod[2], utilidad=cant * prod[3],
                        costo=prod[4], proveedor=prod[5]
                    )
                    
                    # Actualización de Stock
                    db["stock"].actualizar(prod[0], prod[1]-cant, prod[2], prod[3], prod[4], prod[5])
                    
                    # Limpieza
                    seleccion["datos"] = None
                    cargar_vistas("ventas")
                    mostrar_notificacion(f"Venta registrada. Nuevo stock: {prod[1]-cant}", "green")
                except Exception as e:
                    mostrar_notificacion(f"Error: {e}", "red")

            # Función interna para actualizar el texto descriptivo
            def set_info(p):
                info_txt.value = f"SELECCIONADO: {p[2]} | STOCK DISPONIBLE: {p[1]} | COSTO: ${p[4]}"
                info_txt.color = "blue"
                page.update()

            # "Inyectamos" la referencia para que on_product_click pueda usarla
            nonlocal actualizar_formulario_ventas
            actualizar_formulario_ventas = set_info

            return ft.Column([
                ft.Text("REGISTRO DE VENTAS", weight="bold", size=18),
                ft.Row([f_cant, buscador_col, ft.ElevatedButton("REGISTRAR VENTA", on_click=registrar, icon=ft.Icons.SAVE, bgcolor="blue", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))], spacing=10),
                info_txt
            ])

        return ft.Text("HISTORIAL DE MOVIMIENTOS - SOLO LECTURA", weight="bold")

    # Referencia para actualización dinámica de la vista de ventas
    actualizar_formulario_ventas = lambda p: None

    def cargar_vistas(nombre):
        """Refresca los componentes de formulario y tabla de la página."""
        container_formulario.content = construir_formulario(nombre)
        
        tabla, total = construir_datos_tabla(nombre)
        
        # Lista de controles para la columna de la tabla
        controles = [tabla]
        
        # Solo mostramos la utilidad total en Ventas e Historial
        if nombre != "stock" and nombre != "historial":
            controles.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"UTILIDAD TOTAL: ", weight="bold", size=16),
                        ft.Text(f"${total:,.2f}", weight="bold", size=20, color="green" if total >= 0 else "red")
                    ], alignment=ft.MainAxisAlignment.END),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.05, "white"),
                    border_radius=5
                )
            )
        
        container_tabla.content = ft.Column(
            controles, 
            scroll=ft.ScrollMode.ADAPTIVE, expand=True
        )
        page.update()

    # --- ESTRUCTURA DE NAVEGACIÓN ---
    navegacion = ft.Row([
        ft.Button("STOCK", icon=ft.Icons.INVENTORY, on_click=lambda _: cargar_vistas("stock")),
        ft.Button("VENTAS", icon=ft.Icons.SHOPPING_CART, on_click=lambda _: cargar_vistas("ventas")),
        ft.Button("HISTORIAL", icon=ft.Icons.HISTORY, on_click=lambda _: cargar_vistas("historial")),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=25)

    # --- MONTAJE INICIAL ---
    page.add(
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.STORE_ROUNDED, size=40, color="blue"),
                ft.Text("SISTEMA DE STOCK V2", size=28, weight="bold", color="blue"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            margin=ft.Margin.only(bottom=10)
        ),
        navegacion,
        ft.Divider(height=2, color="grey300"),
        container_formulario,
        ft.Divider(height=2, color="grey300"),
        container_tabla
    )

    cargar_vistas("stock")

# Ejecución
ft.run(main)
