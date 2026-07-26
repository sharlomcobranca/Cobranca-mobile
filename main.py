import flet as ft
import traceback

def main(page: ft.Page):
    try:
        # Configuração inicial da página
        page.title = "Flow"
        page.theme_mode = "dark"
        
        # Teste de interface básica protegida
        page.add(
            ft.View(
                controls=[
                    ft.AppBar(title=ft.Text("Flow - Inicialização"), bgcolor=ft.colors.BLUE_900),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            horizontal_alignment="center",
                            alignment="center",
                            controls=[
                                ft.Icon("check_circle", color="green", size=60),
                                ft.Text("Aplicação carregada com sucesso!", size=20, weight="bold"),
                            ]
                        )
                    )
                ]
            )
        )
        page.update()
        
    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)
        page.clean()
        page.add(
            ft.ListView(
                expand=True,
                controls=[
                    ft.Text("ERRO CRÍTICO NO APP:", color="red", weight="bold", size=20),
                    ft.Text(err_msg, color="white", size=12)
                ]
            )
        )
        page.update()

ft.app(target=main)
