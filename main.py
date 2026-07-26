import os
import threading
import flet as ft
from supabase import create_client, Client

# --- TRATAMENTO SEGURO DE VARIÁVEIS DE AMBIENTE ---
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv(".env")
except Exception:
    pass

VERSAO_ATUAL_APP = "1.1.0"

SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://vccshrmzbubwzmfdgzqi.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjY3Nocm16YnVid3ptZmRnenFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTcwMTQsImV4cCI6MjEwMDU3MzAxNH0.3RmDObR5_YfTTN87Yl7QwMEmTQh09JVRCakzGIfqHCE"

supabase: Client = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Aviso Supabase: {e}")

usuario_atual = {
    "id": "",
    "email": "",
    "nome": "",
    "celular": "",
    "genero": "Não informado",
    "foto_url": "",
}

def carregar_dados_usuario(email_user: str):
    if not email_user:
        return
    usuario_atual["email"] = email_user
    usuario_atual["nome"] = email_user.split("@")[0].capitalize()

    if not supabase:
        return

    try:
        res = supabase.table("perfis").select("*").eq("email", email_user).execute()
        if res.data:
            perfil = res.data[0]
            usuario_atual.update({
                "email": perfil.get("email", email_user),
                "nome": perfil.get("nome") or email_user.split("@")[0].capitalize(),
                "celular": perfil.get("celular", ""),
                "genero": perfil.get("genero", "Não informado"),
                "foto_url": perfil.get("foto_url", ""),
            })
    except Exception as err:
        print(f"Erro ao buscar perfil: {err}")

def verificar_atualizacao(page: ft.Page):
    def checar():
        if not supabase:
            return
        try:
            res = supabase.table("configuracoes").select("versao_recente, url_download").eq("id", 1).execute()
            if res.data:
                config = res.data[0]
                versao_recente = config.get("versao_recente")
                url_download = config.get("url_download")
                
                if versao_recente and versao_recente != VERSAO_ATUAL_APP:
                    def baixar_atualizacao(e):
                        if url_download:
                            page.launch_url(url_download)

                    dialog_atualizacao = ft.AlertDialog(
                        title=ft.Text("Nova Atualização Disponível!"),
                        content=ft.Text(f"Uma nova versão ({versao_recente}) do Flow está disponível para download."),
                        actions=[
                            ft.TextButton("Depois", on_click=lambda _: setattr(dialog_atualizacao, "open", False) or page.update()),
                            ft.ElevatedButton("Atualizar Agora", bgcolor="#1E88E5", color="#FFFFFF", on_click=baixar_atualizacao),
                        ],
                    )
                    page.dialog = dialog_atualizacao
                    dialog_atualizacao.open = True
                    page.update()
        except Exception as err:
            print(f"Erro ao verificar atualização: {err}")

    # Executa em segundo plano para não congelar a interface (evita tela preta)
    threading.Thread(target=checar, daemon=True).start()

def buscar_dados_financeiros():
    if supabase:
        try:
            res = supabase.table("pagamentos").select("*").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception as err:
            print(f"Erro ao ler pagamentos da nuvem: {err}")

    return [
        {"nome": "João Silva", "filial": "MATRIZ", "resp": "Victor", "valor": 1500.50, "ok": True},
        {"nome": "Maria Souza", "filial": "FILIAL-01", "resp": "Deidla", "valor": 850.00, "ok": True},
        {"nome": "Carlos Santos", "filial": "FILIAL-11", "resp": "Loja 11", "valor": 420.00, "ok": False},
        {"nome": "Empresa ABC", "filial": "MATRIZ", "resp": "Victor", "valor": 3200.00, "ok": True},
    ]

def criar_header_app(page: ft.Page, abrir_drawer_func=None):
    foto_src = usuario_atual.get("foto_url")
    if foto_src:
        avatar_content = ft.CircleAvatar(foreground_image_src=foto_src, radius=20)
    else:
        inicial = usuario_atual.get("nome", "U")[0].upper() if usuario_atual.get("nome") else "U"
        avatar_content = ft.CircleAvatar(
            content=ft.Text(inicial, color="#FFFFFF", weight="bold"),
            bgcolor="#1E88E5",
            radius=20,
        )

    return ft.Container(
        padding=ft.padding.only(left=20, right=20, top=15, bottom=10),
        content=ft.Row(
            alignment="spaceBetween",
            controls=[
                ft.Row([
                    ft.Icon("auto_awesome", color="#42A5F5", size=28),
                    ft.Text("Flow", size=24, weight="bold"),
                ]),
                ft.GestureDetector(
                    on_tap=abrir_drawer_func if abrir_drawer_func else lambda _: page.go("/perfil"),
                    content=avatar_content,
                ),
            ],
        ),
    )

def criar_bottom_bar(page: ft.Page):
    is_dark = page.theme_mode == "dark"

    def alternar_tema(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        page.update()

    return ft.Container(
        padding=ft.padding.only(bottom=20, left=15, right=15),
        content=ft.Row(
            alignment="center",
            vertical_alignment="center",
            controls=[
                ft.Container(
                    bgcolor="#262832" if is_dark else "#E0E0E0",
                    border_radius=30,
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    content=ft.Row(
                        spacing=15,
                        controls=[
                            ft.IconButton(
                                icon="home_rounded",
                                icon_color="#FFFFFF" if is_dark else "#1A1A1A",
                                on_click=lambda _: page.go("/home"),
                            ),
                            ft.IconButton(
                                icon="person_outline",
                                icon_color="#BDBDBD" if is_dark else "#666666",
                                on_click=lambda _: page.go("/perfil"),
                            ),
                            ft.IconButton(
                                icon="light_mode" if is_dark else "dark_mode",
                                icon_color="#FFD54F" if is_dark else "#5C6BC0",
                                tooltip="Alternar Tema",
                                on_click=alternar_tema,
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

def login_view(page: ft.Page) -> ft.View:
    email_input = ft.TextField(label="E-mail Corporativo", border_color="#2196F3", text_size=14)
    senha_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, text_size=14)
    btn_entrar = ft.ElevatedButton("Entrar no Sistema", width=290, height=48, bgcolor="#1E88E5", color="#FFFFFF")

    def mostrar_snack(txt, erro=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(txt, color="#FFFFFF"),
            bgcolor="#EF5350" if erro else "#43A047",
            open=True,
        )
        page.update()

    def acao_login(e):
        if not email_input.value or not senha_input.value:
            mostrar_snack("Preencha e-mail e senha", erro=True)
            return
        usuario_atual["email"] = email_input.value
        usuario_atual["nome"] = email_input.value.split("@")[0].capitalize()
        page.client_storage.set("user_email", email_input.value)
        page.go("/home")

    btn_entrar.on_click = acao_login

    card_login = ft.Container(
        padding=25,
        bgcolor="#1E1F25" if page.theme_mode == "dark" else "#FFFFFF",
        border_radius=16,
        width=340,
        content=ft.Column(
            horizontal_alignment="center",
            spacing=15,
            tight=True,
            controls=[
                ft.Icon("auto_awesome", color="#42A5F5", size=40),
                ft.Text("Flow", size=28, weight="bold"),
                email_input,
                senha_input,
                btn_entrar,
            ],
        ),
    )
    return ft.View(route="/login", vertical_alignment="center", horizontal_alignment="center", controls=[card_login])

def cadastro_view(page: ft.Page) -> ft.View:
    nome_input = ft.TextField(label="Nome Completo", border_color="#2196F3")
    email_input = ft.TextField(label="E-mail", border_color="#616161")
    senha_input = ft.TextField(label="Senha", password=True, can_reveal_password=True)
    btn_cadastrar = ft.ElevatedButton("Criar Conta", width=290, height=48, bgcolor="#1E88E5", color="#FFFFFF")

    def acao_cadastrar(e):
        usuario_atual["email"] = email_input.value
        usuario_atual["nome"] = nome_input.value
        page.client_storage.set("user_email", email_input.value)
        page.go("/home")

    btn_cadastrar.on_click = acao_cadastrar

    card_cadastro = ft.Container(
        padding=25,
        bgcolor="#1E1F25" if page.theme_mode == "dark" else "#FFFFFF",
        border_radius=16,
        width=340,
        content=ft.Column(
            horizontal_alignment="center",
            spacing=15,
            tight=True,
            controls=[
                ft.Icon("auto_awesome", color="#42A5F5", size=40),
                ft.Text("Flow", size=28, weight="bold"),
                nome_input, email_input, senha_input, btn_cadastrar,
                ft.TextButton("Voltar ao Login", color="#42A5F5", on_click=lambda _: page.go("/login")),
            ],
        ),
    )
    return ft.View(route="/cadastro", vertical_alignment="center", horizontal_alignment="center", controls=[card_cadastro])

def home_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == "dark"

    drawer = ft.NavigationDrawer(
        bgcolor="#1E1F25" if is_dark else "#F5F5F5",
        controls=[
            ft.Container(height=20),
            ft.ListTile(
                leading=ft.Icon("person", color="#42A5F5"),
                title=ft.Text("Meu Perfil", weight="bold"),
                on_click=lambda _: (setattr(drawer, "open", False) or page.update(), page.go("/perfil")),
            ),
            ft.Divider(),
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([ft.Icon("logout", color="#EF5350"), ft.Text("Sair", color="#EF5350")], alignment="center"),
                    bgcolor="#2A1215" if is_dark else "#FFEBEE",
                    on_click=lambda _: (
                        page.client_storage.remove("user_email"),
                        usuario_atual.clear(),
                        page.go("/login")
                    ),
                ),
                padding=20,
            ),
        ],
    )

    lista_pagamentos = buscar_dados_financeiros()
    total_faturado = sum(p.get("valor", 0) for p in lista_pagamentos if isinstance(p.get("valor"), (int, float)))

    card_faturamento = ft.Container(
        bgcolor="#1E1F25" if is_dark else "#FFFFFF",
        padding=20,
        border_radius=12,
        content=ft.Column(
            controls=[
                ft.Text("Faturamento Total", size=14, color="#BDBDBD"),
                ft.Text(f"R$ {total_faturado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), color="#66BB6A", size=28, weight="bold"),
            ]
        ),
    )

    cards_pagamento = []
    for item in lista_pagamentos:
        ok = item.get("ok", True)
        valor_fmt = f"R$ {item['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        cards_pagamento.append(
            ft.Container(
                bgcolor="#1E1F25" if is_dark else "#FFFFFF",
                padding=15,
                border_radius=10,
                content=ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Row([
                            ft.Icon("check_circle" if ok else "access_time_filled", color="#66BB6A" if ok else "#FFC107", size=24),
                            ft.Column([
                                ft.Text(item.get("nome", "Cliente"), weight="bold", size=15),
                                ft.Text(f"Filial: {item.get('filial')} | Resp: {item.get('resp')}", size=11, color="#BDBDBD"),
                            ], spacing=2),
                        ]),
                        ft.Text(valor_fmt, weight="bold", size=14),
                    ],
                ),
            )
        )

    conteudo_scroll = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=20),
        content=ft.Column(
            scroll="auto",
            spacing=15,
            controls=[
                card_faturamento,
                ft.Text("Pagamentos", size=18, weight="bold"),
                *cards_pagamento,
                ft.Container(height=80),
            ],
        ),
    )

    return ft.View(
        route="/home",
        drawer=drawer,
        controls=[
            criar_header_app(page, lambda _: setattr(drawer, "open", True) or page.update()),
            conteudo_scroll,
            criar_bottom_bar(page),
        ],
    )

def perfil_view(page: ft.Page) -> ft.View:
    nome_input = ft.TextField(label="Nome", value=usuario_atual.get("nome", ""))
    celular_input = ft.TextField(label="Celular", value=usuario_atual.get("celular", ""))
    status_txt = ft.Text("", size=12, color="#42A5F5")

    file_picker = ft.FilePicker()

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            usuario_atual["foto_url"] = file_path
            status_txt.value = f"Arquivo selecionado: {e.files[0].name}"
            page.update()

    file_picker.on_result = on_file_picked
    page.overlay.append(file_picker)

    def salvar(e):
        usuario_atual["nome"] = nome_input.value
        usuario_atual["celular"] = celular_input.value
        page.go("/home")

    btn_enviar_foto = ft.ElevatedButton(
        "Enviar Nova Foto/Arquivo",
        icon="upload_file",
        on_click=lambda _: file_picker.pick_files(allow_multiple=False)
    )

    return ft.View(
        route="/perfil",
        controls=[
            ft.Row([
                ft.IconButton(icon="arrow_back", on_click=lambda _: page.go("/home")), 
                ft.Text("Perfil do Usuário", size=20, weight="bold")
            ]),
            ft.Container(
                padding=20, 
                content=ft.Column([
                    nome_input, 
                    celular_input, 
                    btn_enviar_foto,
                    status_txt,
                    ft.ElevatedButton("Salvar Alterações", bgcolor="#1E88E5", color="#FFFFFF", on_click=salvar)
                ], spacing=15)
            )
        ]
    )

def main(page: ft.Page):
    try:
        page.title = "Flow"
        page.theme_mode = "dark"
        page.padding = 0

        # Dispara a checagem em background para não travar a UI na inicialização
        verificar_atualizacao(page)

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
                page.views.append(perfil_view(page))
            page.update()

        def view_pop(view_event):
            page.views.pop()
            if page.views:
                top_view = page.views[-1]
                page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop
        page.go(page.route or "/")

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        page.clean()
        page.add(ft.ListView(expand=True, controls=[ft.Text("ERRO:", color="red"), ft.Text(err_msg, color="white")]))
        page.update()

ft.app(target=main)
