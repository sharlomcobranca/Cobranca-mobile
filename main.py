import flet as ft

def main(page: ft.Page):
    page.title = "Teste Flow"
    page.theme_mode = "dark"
    
    page.add(
        ft.View(
            controls=[
                ft.AppBar(title=ft.Text("Teste de Inicialização"), bgcolor=ft.colors.BLUE_900),
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment="center",
                        alignment="center",
                        controls=[
                            ft.Icon("check_circle", color="green", size=60),
                            ft.Text("O Flet abriu com sucesso!", size=20, weight="bold"),
                            ft.ElevatedButton("Testar Clique", on_click=lambda _: print("Clicado!"))
                        ]
                    )
                )
            ]
        )
    )
    page.update()

ft.app(target=main)
