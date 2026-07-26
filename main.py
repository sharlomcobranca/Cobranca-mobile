import os
import flet as ft
from supabase import create_client, Client

# --- TRATAMENTO SEGURO DE VARIÁVEIS DE AMBIENTE ---
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv(".env")
except Exception:
    pass

VERSAO_ATUAL_APP = "1.0.0"

# Busca do ambiente com fallback seguro para evitar tela preta no APK
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://vccshrmzbubwzmfdgzqi.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjY3Nocm16YnVid3ptZmRnenFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTcwMTQsImV4cCI6MjEwMDU3MzAxNH0.3RmDObR5_YfTTN87Yl7QwMEmTQh09JVRCakzGIfqHCE"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Aviso Supabase: {e}")
    supabase = None

# --- ESTADO GLOBAL DO USUÁRIO ---
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


def buscar_dados_financeiros():
    if supabase:
        try:
            res = supabase.table("pagamentos").select("*").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception as err:
            print(f"Erro ao ler pagamentos da nuvem: {err}")

    # Fallback local
    return [
        {"nome": "João Silva", "filial": "MATRIZ", "resp": "Victor", "valor": 1500.50, "ok": True},
        {"nome": "Maria Souza", "filial": "FILIAL-01", "resp": "Deidla", "valor": 850.00, "ok": True},
        {"nome": "Carlos Santos", "filial": "FILIAL-11", "resp": "Loja 11", "valor": 420.00, "ok": False},
        {"nome": "Empresa ABC", "filial": "MATRIZ", "resp": "Victor", "valor": 3200.00, "ok": True},
    ]


# --- COMPONENTES REUTILIZÁVEIS ---
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
                                tooltip="Alternar Tema Escuro/Claro",
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


# --- TELAS (VIEWS) ---

def login_view(page: ft.Page) -> ft.View:
    email_input = ft.TextField(label="E-mail Corporativo", border_color="#2196F3", text_size=14)
    senha_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, text_size=14)
    btn_entrar = ft.ElevatedButton("Entrar no Sistema", width=290, height=48, bgcolor="#1E88E5", color="#FFFFFF")

    def mostrar_snack(txt, erro=False):
        snack = ft.SnackBar(
            content=ft.Text(txt, color="#FFFFFF"),
            bgcolor="#EF5350" if erro else "#43A047",
            open=True,
        )
        page.snack_bar = snack
        page.update()

    def abrir_esqueci_senha(e):
        rec_email = ft.TextField(label="E-mail Cadastrado", border_color="#2196F3")

        def enviar_reset(evt):
            if not rec_email.value:
                rec_email.error_text = "Informe o e-mail"
                page.update()
                return
            try:
                if supabase:
                    supabase.auth.reset_password_for_email(rec_email.value)
                dialog_rec.open = False
                page.update()
                mostrar_snack("Link enviado para seu e-mail!")
            except Exception as err:
                mostrar_snack(f"Erro: {err}", erro=True)

        dialog_rec = ft.AlertDialog(
            title=ft.Text("Recuperar Senha"),
            content=ft.Column(
                [
                    ft.Text("Digite seu e-mail para redefinir a senha:", size=13),
                    rec_email,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(dialog_rec, "open", False) or page.update()),
                ft.ElevatedButton("Enviar E-mail", bgcolor="#1E88E5", color="#FFFFFF", on_click=enviar_reset),
            ],
        )
        page.dialog = dialog_rec
        dialog_rec.open = True
        page.update()

    def acao_login(e):
        email_input.error_text = None
        senha_input.error_text = None

        if not email_input.value or not senha_input.value:
            if not email_input.value:
                email_input.error_text = "Informe o e-mail"
            if not senha_input.value:
                senha_input.error_text = "Informe a senha"
            page.update()
            return

        btn_entrar.disabled = True
        btn_entrar.content = ft.ProgressRing(width=20, height=20, stroke_width=2, color="#FFFFFF")
        page.update()

        try:
            if supabase:
                res = supabase.auth.sign_in_with_password({
                    "email": email_input.value,
                    "password": senha_input.value,
                })
                if res.user:
                    carregar_dados_usuario(res.user.email)
                    page.client_storage.set("user_email", res.user.email)
                    mostrar_snack("Login realizado!")
                    page.go("/home")
                    return

            usuario_atual["email"] = email_input.value
            usuario_atual["nome"] = email_input.value.split("@")[0].capitalize()
            page.client_storage.set("user_email", email_input.value)
            mostrar_snack("Acesso local iniciado.")
            page.go("/home")
        except Exception as err:
            if "Invalid login credentials" in str(err):
                mostrar_snack("E-mail ou senha incorretos.", erro=True)
            else:
                usuario_atual["email"] = email_input.value
                usuario_atual["nome"] = email_input.value.split("@")[0].capitalize()
                page.client_storage.set("user_email", email_input.value)
                mostrar_snack("Acesso local iniciado.")
                page.go("/home")
        finally:
            btn_entrar.disabled = False
            btn_entrar.content = None
            btn_entrar.text = "Entrar no Sistema"
            page.update()

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
                ft.Row(
                    [ft.TextButton("Esqueceu a senha?", color="#BDBDBD", on_click=abrir_esqueci_senha)],
                    alignment="end",
                ),
                btn_entrar,
                ft.TextButton("Não tem conta? Cadastre-se", color="#42A5F5", on_click=lambda _: page.go("/cadastro")),
            ],
        ),
    )

    return ft.View(
        route="/login",
        vertical_alignment="center",
        horizontal_alignment="center",
        controls=[card_login],
    )


def cadastro_view(page: ft.Page) -> ft.View:
    nome_input = ft.TextField(label="Nome Completo", border_color="#2196F3")
    email_input = ft.TextField(label="E-mail Corporativo", border_color="#616161")
    senha_input = ft.TextField(label="Senha", password=True, can_reveal_password=True)
    btn_cadastrar = ft.ElevatedButton("Criar Conta", width=290, height=48, bgcolor="#1E88E5", color="#FFFFFF")

    def mostrar_snack(txt, erro=False):
        snack = ft.SnackBar(
            content=ft.Text(txt, color="#FFFFFF"),
            bgcolor="#EF5350" if erro else "#43A047",
            open=True,
        )
        page.snack_bar = snack
        page.update()

    def acao_cadastrar(e):
        if not nome_input.value or not email_input.value or not senha_input.value:
            mostrar_snack("Preencha todos os campos!", erro=True)
            return

        try:
            if supabase:
                supabase.auth.sign_up({
                    "email": email_input.value,
                    "password": senha_input.value,
                    "options": {"data": {"nome": nome_input.value}},
                })
                try:
                    supabase.table("perfis").upsert({
                        "email": email_input.value,
                        "nome": nome_input.value,
                    }).execute()
                except Exception:
                    pass

            usuario_atual["email"] = email_input.value
            usuario_atual["nome"] = nome_input.value
            page.client_storage.set("user_email", email_input.value)
            mostrar_snack("Conta criada com sucesso!")
            page.go("/home")
        except Exception as err:
            mostrar_snack(f"Erro no cadastro: {err}", erro=True)

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
                ft.Text("Criar nova credencial", size=12, color="#BDBDBD"),
                nome_input,
                email_input,
                senha_input,
                btn_cadastrar,
                ft.TextButton("Já possui conta? Faça o login.", color="#42A5F5", on_click=lambda _: page.go("/login")),
            ],
        ),
    )

    return ft.View(
        route="/cadastro",
        vertical_alignment="center",
        horizontal_alignment="center",
        controls=[card_cadastro],
    )


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
            ft.Container(height=20),
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([ft.Icon("logout", color="#EF5350"), ft.Text("Sair", color="#EF5350")], alignment="center"),
                    bgcolor="#2A1215" if is_dark else "#FFEBEE",
                    on_click=lambda _: fazer_logout(),
                ),
                padding=20,
            ),
        ],
    )

    def abrir_drawer(e=None):
        drawer.open = True
        page.update()

    def fazer_logout():
        drawer.open = False
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        page.client_storage.remove("user_email")
        usuario_atual.clear()
        page.go("/login")

    def checar_atualizacoes():
        if not supabase:
            return
        try:
            res = supabase.table("configuracoes").select("*").eq("id", 1).execute()
            if res.data:
                config = res.data[0]
                remota = config.get("versao_apk")
                link = config.get("link_download")
                if remota and remota != VERSAO_ATUAL_APP:
                    dialog = ft.AlertDialog(
                        title=ft.Text("🚀 Nova Atualização!"),
                        content=ft.Text(f"Versão {remota} disponível."),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda _: setattr(dialog, "open", False) or page.update()),
                            ft.ElevatedButton("Baixar Agora", on_click=lambda _: page.launch_url(link)),
                        ],
                    )
                    page.dialog = dialog
                    dialog.open = True
                    page.update()
        except Exception as err:
            print(f"Checagem de atualização ignorada: {err}")

    checar_atualizacoes()

    lista_pagamentos = buscar_dados_financeiros()
    total_faturado = sum(p.get("valor", 0) for p in lista_pagamentos if isinstance(p.get("valor"), (int, float)))

    card_faturamento = ft.Container(
        bgcolor="#1E1F25" if is_dark else "#FFFFFF",
        padding=20,
        border_radius=12,
        content=ft.Column(
            controls=[
                ft.Text("Faturamento Total", size=14, color="#BDBDBD"),
                ft.Text(
                    f"R$ {total_faturado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    color="#66BB6A",
                    size=28,
                    weight="bold",
                ),
            ]
        ),
    )

    cards_pagamento = []
    for item in lista_pagamentos:
        ok = item.get("ok", True)
        valor_fmt = (
            f"R$ {item['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if isinstance(item.get("valor"), (int, float))
            else str(item.get("valor", 0))
        )

        cards_pagamento.append(
            ft.Container(
                bgcolor="#1E1F25" if is_dark else "#FFFFFF",
                padding=15,
                border_radius=10,
                content=ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Row([
                            ft.Icon(
                                "check_circle" if ok else "access_time_filled",
                                color="#66BB6A" if ok else "#FFC107",
                                size=24,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(item.get("nome", "Cliente"), weight="bold", size=15),
                                    ft.Text(
                                        f"Filial: {item.get('filial', 'MATRIZ')} | Responsável: {item.get('resp', 'N/A')}",
                                        size=11,
                                        color="#BDBDBD",
                                    ),
                                ],
                            ),
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
                ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Text("Pagamentos", size=18, weight="bold"),
                        ft.IconButton(icon="refresh", icon_color="#42A5F5", on_click=lambda _: page.go("/home")),
                    ],
                ),
                *cards_pagamento,
                ft.Container(height=80),
            ],
        ),
    )

    return ft.View(
        route="/home",
        drawer=drawer,
        controls=[
            criar_header_app(page, abrir_drawer),
            conteudo_scroll,
            criar_bottom_bar(page),
        ],
    )


def perfil_view(page: ft.Page, file_picker: ft.FilePicker) -> ft.View:
    avatar_preview = ft.CircleAvatar(
        foreground_image_src=usuario_atual.get("foto_url") or None,
        content=ft.Icon("person", size=40) if not usuario_atual.get("foto_url") else None,
        radius=45,
        bgcolor="#1E88E5",
    )

    def atualizar_preview_foto(e):
        url = (e.control.value or "").strip()
        if url:
            avatar_preview.foreground_image_src = url
            avatar_preview.content = None
        else:
            avatar_preview.foreground_image_src = None
            avatar_preview.content = ft.Icon("person", size=40)
        avatar_preview.update()

    foto_input = ft.TextField(
        label="URL da Foto de Perfil",
        value=usuario_atual.get("foto_url", ""),
        on_change=atualizar_preview_foto,
    )
    nome_input = ft.TextField(label="Nome Completo", value=usuario_atual.get("nome", ""))
    celular_input = ft.TextField(label="Celular", value=usuario_atual.get("celular", ""))
    genero_input = ft.Dropdown(
        label="Gênero",
        value=usuario_atual.get("genero", "Não informado"),
        options=[
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Feminino"),
            ft.dropdown.Option("Outro"),
            ft.dropdown.Option("Não informado"),
        ],
    )

    def ao_selecionar_arquivo(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            arquivo = e.files[0]
            try:
                nome_arq = f"avatar_{usuario_atual.get('email', 'user').replace('@', '_')}.jpg"
                if supabase:
                    with open(arquivo.path, "rb") as f:
                        file_bytes = f.read()

                    supabase.storage.from_("avatars").upload(
                        path=nome_arq, file=file_bytes, file_options={"upsert": "true"}
                    )
                    public_url = supabase.storage.from_("avatars").get_public_url(nome_arq)
                    foto_input.value = public_url
                    avatar_preview.foreground_image_src = public_url
                    avatar_preview.content = None

                snack = ft.SnackBar(content=ft.Text("Foto alterada com sucesso!"), bgcolor="#43A047", open=True)
                page.snack_bar = snack
                page.update()
            except Exception as err:
                snack = ft.SnackBar(content=ft.Text(f"Erro no upload: {err}"), bgcolor="#EF5350", open=True)
                page.snack_bar = snack
                page.update()

    file_picker.on_result = ao_selecionar_arquivo

    btn_salvar = ft.ElevatedButton("Salvar Informações", width=400, height=50, bgcolor="#1E88E5", color="#FFFFFF")

    def salvar_perfil(e):
        usuario_atual["foto_url"] = foto_input.value
        usuario_atual["nome"] = nome_input.value
        usuario_atual["celular"] = celular_input.value
        usuario_atual["genero"] = genero_input.value

        if supabase:
            try:
                supabase.table("perfis").upsert({
                    "email": usuario_atual["email"],
                    "nome": usuario_atual["nome"],
                    "celular": usuario_atual["celular"],
                    "genero": usuario_atual["genero"],
                    "foto_url": usuario_atual["foto_url"],
                }).execute()
            except Exception:
                pass

        page.go("/home")

    btn_salvar.on_click = salvar_perfil

    header_perfil = ft.Container(
        padding=ft.padding.only(left=10, right=20, top=15, bottom=10),
        content=ft.Row(controls=[
            ft.IconButton(icon="arrow_back", on_click=lambda _: page.go("/home")),
            ft.Text("Editar Perfil", size=20, weight="bold"),
        ]),
    )

    form_perfil = ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            scroll="auto",
            spacing=15,
            controls=[
                ft.Container(alignment=ft.Alignment(0, 0), content=avatar_preview),
                ft.OutlinedButton(
                    "📷 Abrir Galeria do Celular",
                    icon="upload_file",
                    on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.IMAGE),
                ),
                foto_input,
                nome_input,
                celular_input,
                genero_input,
                ft.Container(height=10),
                btn_salvar,
            ],
        ),
    )

    return ft.View(route="/perfil", controls=[header_perfil, form_perfil])


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


ft.app(target=main)
