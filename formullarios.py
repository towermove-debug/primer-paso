import flet as ft

def main(page: ft.Page):
    page.title = "Formulario Simple"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Referencias a los campos
    txt_campo1 = ft.TextField(label="Campo 1")
    txt_campo2 = ft.TextField(label="Campo 2")
    txt_campo3 = ft.TextField(label="Campo 3")

    def toggle_form(e):
        form_container.visible = not form_container.visible
        btn_action.text = "Cerrar" if form_container.visible else "Abrir Formulario"
        page.update()

    def guardar_datos(e):
        # Aquí iría el código para guardar en la base de datos
        print(f"Guardando: {txt_campo1.value}, {txt_campo2.value}, {txt_campo3.value}")
        
        # Limpiar los campos
        txt_campo1.value = ""
        txt_campo2.value = ""
        txt_campo3.value = ""
        
        # Opcional: Cerrar el formulario tras guardar
        toggle_form(None)
        
        page.update()

    def create_modern_button(text, icon, color=None, on_click=None):
        return ft.ElevatedButton(
            text,
            icon=icon,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=color if color else ft.Colors.BLUE_700,
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation={"hovered": 10, "": 1},
            ),
            on_click=on_click
        )


    # Botón principal
    btn_action = create_modern_button(
        "Abrir Formulario",
        ft.Icons.UPCOMING,
        ft.Colors.INDIGO,
        on_click=toggle_form
    )

    # El formulario
    form_container = ft.Container(
        content=ft.Column([
            ft.Text("DATOS DEL FORMULARIO", size=18, weight="bold"),
            txt_campo1,
            txt_campo2,
            txt_campo3,
            ft.Row(
                [
                    create_modern_button("Guardar", ft.Icons.SAVE, ft.Colors.GREEN_700, on_click=guardar_datos),
                    ft.TextButton("Cancelar", on_click=toggle_form, style=ft.ButtonStyle(color=ft.Colors.RED_400))
                ],
                alignment=ft.MainAxisAlignment.END
            )
        ], spacing=15),
        padding=20,
        bgcolor="#1e293b",
        border_radius=12,
        visible=False,
        width=400,
    )


    page.add(
        ft.Text("Mi Formulario Moderno", size=28, weight="bold", color=ft.Colors.BLUE_400),
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        btn_action,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        form_container
    )


if __name__ == "__main__":
    ft.app(target=main)
