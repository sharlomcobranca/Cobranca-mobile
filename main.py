# --- APLICAÇÃO PRINCIPAL ---
def main(page: ft.Page):
    try:
        page.title = "Flow"
        page.theme_mode = "dark"
        page.padding = 0

        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)

        def route_change(route_event):
            page.views.clear()

            email_salvo = page.client_storage.get("user_email")
            if email_salvo:
                carregar_dados_usuario(email_salvo)

            if page.route == "/login" or page.route == "/":
                if email_salvo:
                    page.route = "/home"
                    page.views.append(home_view(page))
                else:
                    page.views.append(login_view(page))
            elif page.route == "/cadastro":
                page.views.append(cadastro_view(page))
            elif page.route == "/home":
                page.views.append(home_view(page))
            elif page.route == "/perfil":
                page.views.append(perfil_view(page, file_picker))

            page.update()

        def view_pop(view_event):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop

        page.go(page.route or "/")
        
    except Exception as e:
        # Se ocorrer qualquer erro crítico na inicialização, mostra na tela em vez de ficar preto
        page.clean()
        page.add(
            ft.View(
                controls=[
                    ft.AppBar(title=ft.Text("Erro Crítico de Inicialização"), bgcolor=ft.colors.RED_900),
                    ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Ocorreu um erro ao iniciar o app:", weight="bold", color="red"),
                            ft.Text(str(e), size=12, selectable=True)
                        ])
                    )
                ]
            )
        )
        page.update()
