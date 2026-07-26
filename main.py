import flet as ft
from supabase import create_client, Client

# --- CONFIGURAÇÃO INICIAL E VERSÃO ---
VERSAO_ATUAL_APP = "1.0.0"

SUPABASE_URL = "https://vccshrmzbubwzmfdgzqi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjY3Nocm16YnVid3ptZmRnenFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTcwMTQsImV4cCI6MjEwMDU3MzAxNH0.3RmDObR5_YfTTN87Yl7QwMEmTQh09JVRCakzGIfqHCE"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def main(page: ft.Page):
    page.title = "Flow"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121318"
    page.padding = 0
    page.vertical_alignment = "start"

    # Estado da aplicação
    usuario_atual = {
        "email": "",
        "nome": "",
        "celular": "",
        "genero": "Não informado",
        "foto_url": "",
    }

    # --- HELPER DE NAVEGAÇÃO SEGURA PARA DIALOGS ---
    def abrir_dialogo(dialog):
        try:
            page.dialog = dialog
            dialog.open = True
            page.update()
        except Exception as e:
            print(f"Erro ao abrir dialogo: {e}")

    def fechar_dialogo(dialog):
        try:
            dialog.open = False
            page.update()
        except Exception as e:
            print(f"Erro ao fechar dialogo: {e}")

    # --- VERIFICAÇÃO DE ATUALIZAÇÃO ---
    def verificar_atualizacao():
        try:
            res = (
                supabase.table("configuracoes")
                .select("*")
                .eq("id", 1)
                .execute()
            )
            if res.data:
                config = res.data[0]
                versao_remota = config.get("versao_apk")
                link_download = config.get("link_download")

                if versao_remota and versao_remota != VERSAO_ATUAL_APP:

                    def acao_fechar(e):
                        fechar_dialogo(dialog)

                    def abrir_download(e):
                        page.launch_url(link_download)

                    dialog = ft.AlertDialog(
                        title=ft.Text("🚀 Nova Atualização!"),
                        content=ft.Text(
                            f"A versão {versao_remota} está disponível. Deseja atualizar agora?"
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=acao_fechar),
                            ft.ElevatedButton(
                                "📥 Baixar Agora", on_click=abrir_download
                            ),
                        ],
                    )
                    abrir_dialogo(dialog)
        except Exception as err:
            print(f"Erro ao checar atualizações: {err}")

    # --- NAVEGAÇÃO & DRAWER ---
    def abrir_drawer(e=None):
        try:
            page.end_drawer.open = True
            page.update()
        except Exception as err:
            print(f"Erro ao abrir drawer: {err}")

    def fechar_drawer(e=None):
        try:
            page.end_drawer.open = False
            page.update()
        except Exception as err:
            print(f"Erro ao fechar drawer: {err}")

    def abrir_perfil(e):
        fechar_drawer()
        carregar_tela_perfil()

    def fazer_logout(e):
        fechar_drawer()
        usuario_atual.update(
            {
                "email": "",
                "nome": "",
                "celular": "",
                "genero": "Não informado",
                "foto_url": "",
            }
        )
        carregar_tela_login()

    # Painel Lateral
    page.end_drawer = ft.NavigationDrawer(
        bgcolor="#1E1F25",
        controls=[
            ft.Container(height=20),
            ft.ListTile(
                leading=ft.Icon("person", color="#42A5F5"),
                title=ft.Text(
                    "Meu Perfil",
                    color="#FFFFFF",
                    weight="bold",
                ),
                on_click=abrir_perfil,
            ),
            ft.Divider(color="#424242"),
            ft.Container(expand=True),
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon("logout", color="#EF5350"),
                            ft.Text("Sair", color="#EF5350"),
                        ],
                        alignment="center",
                    ),
                    style=ft.ButtonStyle(
                        bgcolor="#2A1215",
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=fazer_logout,
                ),
                padding=20,
            ),
        ],
    )

    # --- COMPONENTES REUTILIZÁVEIS ---
    def criar_header_app():
        foto_src = usuario_atual.get("foto_url")
        if foto_src:
            avatar_content = ft.CircleAvatar(
                foreground_image_url=foto_src, radius=20
            )
        else:
            inicial = (
                usuario_atual.get("nome", "U")[0].upper()
                if usuario_atual.get("nome")
                else "U"
            )
            avatar_content = ft.CircleAvatar(
                content=ft.Text(
                    inicial, color="#FFFFFF", weight="bold"
                ),
                bgcolor="#1E88E5",
                radius=20,
            )

        return ft.Container(
            padding=ft.padding.only(left=20, right=20, top=15, bottom=10),
            content=ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.Row(
                        [
                            ft.Icon(
                                "auto_awesome",
                                color="#42A5F5",
                                size=28,
                            ),
                            ft.Text(
                                "Flow",
                                size=24,
                                weight="bold",
                                color="#FFFFFF",
                            ),
                        ]
                    ),
                    ft.GestureDetector(
                        on_tap=abrir_drawer,
                        content=avatar_content,
                    ),
                ],
            ),
        )

    def criar_bottom_bar():
        return ft.Container(
            padding=ft.padding.only(bottom=20, left=15, right=15),
            content=ft.Row(
                alignment="center",
                vertical_alignment="center",
                controls=[
                    ft.Container(
                        bgcolor="#262832",
                        border_radius=30,
                        padding=ft.padding.symmetric(
                            horizontal=15, vertical=8
                        ),
                        content=ft.Row(
                            spacing=15,
                            controls=[
                                ft.IconButton(
                                    icon="home_rounded",
                                    icon_color="#FFFFFF",
                                    on_click=lambda _: carregar_home(),
                                ),
                                ft.IconButton(
                                    icon="chat_bubble_outline_rounded",
                                    icon_color="#BDBDBD",
                                    on_click=lambda _: None,
                                ),
                                ft.IconButton(
                                    icon="view_agenda_outlined",
                                    icon_color="#BDBDBD",
                                    on_click=lambda _: None,
                                ),
                                ft.IconButton(
                                    icon="more_horiz",
                                    icon_color="#BDBDBD",
                                    on_click=abrir_drawer,
                                ),
                            ],
                        ),
                    ),
                    ft.Container(width=10),
                    ft.Container(
                        bgcolor="#7B93FF",
                        border_radius=20,
                        width=56,
                        height=56,
                        content=ft.IconButton(
                            icon="add",
                            icon_color="#000000",
                            icon_size=28,
                            on_click=lambda _: None,
                        ),
                    ),
                ],
            ),
        )

    # --- TELA DE LOGIN ---
    def carregar_tela_login():
        page.controls.clear()

        email_input = ft.TextField(
            label="E-mail Corporativo",
            border_color="#2196F3",
            focused_border_color="#42A5F5",
            text_size=14,
        )
        senha_input = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            border_color="#616161",
            focused_border_color="#42A5F5",
            text_size=14,
        )

        def acao_login(e):
            if email_input.value:
                usuario_atual["email"] = email_input.value
                usuario_atual["nome"] = email_input.value.split("@")[0].capitalize()
                carregar_home()

        card_login = ft.Container(
            padding=25,
            bgcolor="#1E1F25",
            border_radius=16,
            width=360,
            content=ft.Column(
                horizontal_alignment="center",
                spacing=15,
                controls=[
                    ft.Icon(
                        "auto_awesome",
                        color="#42A5F5",
                        size=40,
                    ),
                    ft.Text(
                        "Flow",
                        size=28,
                        weight="bold",
                        color="#FFFFFF",
                    ),
                    ft.Container(height=10),
                    email_input,
                    senha_input,
                    ft.Container(height=5),
                    ft.ElevatedButton(
                        "Entrar no Sistema",
                        width=310,
                        height=48,
                        style=ft.ButtonStyle(
                            bgcolor="#1E88E5",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=acao_login,
                    ),
                    ft.TextButton(
                        "Não tem conta? Cadastre-se",
                        style=ft.ButtonStyle(color="#42A5F5"),
                        on_click=lambda _: carregar_tela_cadastro(),
                    ),
                ],
            ),
        )

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=card_login,
            )
        )
        page.update()

    # --- TELA DE CADASTRO ---
    def carregar_tela_cadastro():
        page.controls.clear()

        nome_input = ft.TextField(
            label="Nome Completo", border_color="#2196F3"
        )
        email_input = ft.TextField(
            label="E-mail Corporativo", border_color="#616161"
        )
        senha_input = ft.TextField(
            label="Senha", password=True, can_reveal_password=True
        )

        def acao_cadastrar(e):
            if email_input.value and nome_input.value:
                usuario_atual["email"] = email_input.value
                usuario_atual["nome"] = nome_input.value
                carregar_home()

        card_cadastro = ft.Container(
            padding=25,
            bgcolor="#1E1F25",
            border_radius=16,
            width=360,
            content=ft.Column(
                horizontal_alignment="center",
                spacing=15,
                controls=[
                    ft.Icon(
                        "auto_awesome",
                        color="#42A5F5",
                        size=40,
                    ),
                    ft.Text(
                        "Flow",
                        size=28,
                        weight="bold",
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        "Criar nova credencial de acesso",
                        size=12,
                        color="#BDBDBD",
                    ),
                    ft.Container(height=5),
                    nome_input,
                    email_input,
                    senha_input,
                    ft.Container(height=5),
                    ft.ElevatedButton(
                        "Entrar no Sistema",
                        width=310,
                        height=48,
                        style=ft.ButtonStyle(
                            bgcolor="#1E88E5",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=acao_cadastrar,
                    ),
                    ft.TextButton(
                        "Já possui conta? Faça o login.",
                        style=ft.ButtonStyle(color="#42A5F5"),
                        on_click=lambda _: carregar_tela_login(),
                    ),
                ],
            ),
        )

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=card_cadastro,
            )
        )
        page.update()

    # --- PAINEL PRINCIPAL (HOME) ---
    def carregar_home():
        page.controls.clear()

        card_faturamento = ft.Container(
            bgcolor="#1E1F25",
            padding=20,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Faturamento Total (Nuvem)",
                        color="#BDBDBD",
                        size=14,
                    ),
                    ft.Text(
                        "R$ 17.911,50",
                        color="#66BB6A",
                        size=28,
                        weight="bold",
                    ),
                ]
            ),
        )

        header_pagamentos = ft.Row(
            alignment="spaceBetween",
            controls=[
                ft.Row(
                    [
                        ft.Icon("description", color="#E0E0E0"),
                        ft.Text(
                            "Pagamentos",
                            size=18,
                            weight="bold",
                            color="#FFFFFF",
                        ),
                    ]
                ),
                ft.IconButton(
                    icon="refresh",
                    icon_color="#42A5F5",
                    on_click=lambda _: page.update(),
                ),
            ],
        )

        pagamentos_mock = [
            {
                "nome": "João Silva",
                "filial": "MATRIZ",
                "resp": "Victor",
                "valor": "R$ 1,500.50",
                "ok": True,
            },
            {
                "nome": "Maria Souza",
                "filial": "FILIAL-01",
                "resp": "Deidla",
                "valor": "R$ 850.00",
                "ok": True,
            },
            {
                "nome": "Carlos Santos",
                "filial": "FILIAL-11",
                "resp": "Loja 11",
                "valor": "R$ 420.00",
                "ok": False,
            },
            {
                "nome": "Empresa ABC",
                "filial": "MATRIZ",
                "resp": "Victor",
                "valor": "R$ 3,200.00",
                "ok": True,
            },
        ]

        cards_pagamento = []
        for item in pagamentos_mock:
            cards_pagamento.append(
                ft.Container(
                    bgcolor="#1E1F25",
                    padding=15,
                    border_radius=10,
                    content=ft.Row(
                        alignment="spaceBetween",
                        controls=[
                            ft.Row(
                                [
                                    ft.Icon(
                                        "check_circle"
                                        if item["ok"]
                                        else "access_time_filled",
                                        color="#66BB6A"
                                        if item["ok"]
                                        else "#FFC107",
                                        size=24,
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                item["nome"],
                                                weight="bold",
                                                color="#FFFFFF",
                                                size=15,
                                            ),
                                            ft.Text(
                                                f"Filial: {item['filial']} | Responsável: {item['resp']}",
                                                color="#BDBDBD",
                                                size=11,
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                            ft.Text(
                                item["valor"],
                                weight="bold",
                                color="#FFFFFF",
                                size=14,
                            ),
                        ],
                    ),
                )
            )

        conteudo_scroll = ft.Column(
            expand=True,
            scroll="auto",
            padding=ft.padding.symmetric(horizontal=20),
            spacing=15,
            controls=[
                card_faturamento,
                header_pagamentos,
                *cards_pagamento,
                ft.Container(height=80),
            ],
        )

        page.add(
            ft.Column(
                expand=True,
                controls=[
                    criar_header_app(),
                    conteudo_scroll,
                    criar_bottom_bar(),
                ],
            )
        )
        page.update()

    # --- TELA DE EDITAR PERFIL ---
    def carregar_tela_perfil():
        page.controls.clear()

        foto_input = ft.TextField(
            label="URL da Foto de Perfil",
            value=usuario_atual.get("foto_url", ""),
            border_color="#616161",
        )
        nome_input = ft.TextField(
            label="Nome Completo",
            value=usuario_atual.get("nome", ""),
            border_color="#616161",
        )
        celular_input = ft.TextField(
            label="Celular",
            value=usuario_atual.get("celular", ""),
            border_color="#616161",
        )
        genero_input = ft.Dropdown(
            label="Gênero",
            value=usuario_atual.get("genero", "Não informado"),
            options=[
                ft.dropdown.Option("Masculino"),
                ft.dropdown.Option("Feminino"),
                ft.dropdown.Option("Outro"),
                ft.dropdown.Option("Não informado"),
            ],
            border_color="#616161",
        )

        def salvar_perfil(e):
            usuario_atual["foto_url"] = foto_input.value
            usuario_atual["nome"] = nome_input.value
            usuario_atual["celular"] = celular_input.value
            usuario_atual["genero"] = genero_input.value

            try:
                supabase.table("perfis").upsert(
                    {
                        "email": usuario_atual["email"],
                        "nome": usuario_atual["nome"],
                        "celular": usuario_atual["celular"],
                        "genero": usuario_atual["genero"],
                        "foto_url": usuario_atual["foto_url"],
                    }
                ).execute()
            except Exception as err:
                print(f"Salvo localmente (Supabase error: {err})")

            carregar_home()

        header_perfil = ft.Container(
            padding=ft.padding.only(left=10, right=20, top=15, bottom=10),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon="arrow_back",
                        icon_color="#FFFFFF",
                        on_click=lambda _: carregar_home(),
                    ),
                    ft.Text(
                        "Editar Perfil",
                        size=20,
                        weight="bold",
                        color="#FFFFFF",
                    ),
                ]
            ),
        )

        form_perfil = ft.Column(
            expand=True,
            scroll="auto",
            padding=20,
            spacing=15,
            controls=[
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.CircleAvatar(
                        foreground_image_url=foto_input.value
                        if foto_input.value
                        else None,
                        content=ft.Icon("person", size=40)
                        if not foto_input.value
                        else None,
                        radius=45,
                        bgcolor="#1E88E5",
                    ),
                ),
                foto_input,
                nome_input,
                celular_input,
                genero_input,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Salvar informações",
                    width=400,
                    height=50,
                    style=ft.ButtonStyle(
                        bgcolor="#1E88E5",
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=salvar_perfil,
                ),
            ],
        )

        page.add(ft.Column(expand=True, controls=[header_perfil, form_perfil]))
        page.update()

    # --- INICIALIZAÇÃO DA APLICAÇÃO ---
    # Renderiza primeiro a interface
    carregar_tela_login()
    # Checa atualizações em segundo plano
    verificar_atualizacao()


ft.app(target=main)
