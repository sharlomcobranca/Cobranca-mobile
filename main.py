import os
from pathlib import Path
import flet as ft
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CRIAÇÃO AUTOMÁTICA DO ARQUIVO .ENV (CASO NÃO EXISTA) ---
env_path = Path(".env")
if not env_path.exists():
    conteudo_env_padrao = (
        'SUPABASE_URL="https://vccshrmzbubwzmfdgzqi.supabase.co"\n'
        'SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjY3Nocm16YnVid3ptZmRnenFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTcwMTQsImV4cCI6MjEwMDU3MzAxNH0.3RmDObR5_YfTTN87Yl7QwMEmTQh09JVRCakzGIfqHCE"\n'
    )
    env_path.write_text(conteudo_env_padrao, encoding="utf-8")
    print("✨ Arquivo .env criado automaticamente com as chaves padrão!")

# --- CARREGAMENTO DE VARIÁVEIS DE AMBIENTE ---
load_dotenv()

VERSAO_ATUAL_APP = "1.0.0"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def main(page: ft.Page):
    page.title = "Flow"
    page.theme_mode = "dark"
    page.bgcolor = "#121318"
    page.padding = 0

    # Estado global do usuário logado
    usuario_atual = {
        "id": "",
        "email": "",
        "nome": "",
        "celular": "",
        "genero": "Não informado",
        "foto_url": "",
    }

    # --- HELPER DE NOTIFICAÇÕES (SNACKBAR) ---
    def mostrar_mensagem(texto: str, erro: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(texto, color="#FFFFFF"),
            bgcolor="#EF5350" if erro else "#43A047",
            open=True,
        )
        page.snack_bar = snack
        page.update()

    # --- HELPER DE ESTADO DE CARREGAMENTO NOS BOTÕES ---
    def alternar_loading(btn: ft.ElevatedButton, carregando: bool, texto_padrao: str):
        btn.disabled = carregando
        if carregando:
            btn.content = ft.ProgressRing(
                width=20, height=20, stroke_width=2, color="#FFFFFF"
            )
        else:
            btn.content = None
            btn.text = texto_padrao
        page.update()

    # --- HELPER DE DIÁLOGOS ---
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

    # --- DIÁLOGO DE RECUPERAÇÃO DE SENHA ---
    def abrir_dialogo_esqueci_senha(e=None):
        rec_email = ft.TextField(
            label="E-mail Cadastrado", border_color="#2196F3"
        )

        def enviar_reset(evt):
            if not rec_email.value:
                rec_email.error_text = "Informe o e-mail"
                page.update()
                return

            try:
                supabase.auth.reset_password_for_email(rec_email.value)
                fechar_dialogo(dialog_rec)
                mostrar_mensagem("Link de redefinição enviado para seu e-mail!")
            except Exception as err:
                mostrar_mensagem(f"Erro ao enviar: {err}", erro=True)

        dialog_rec = ft.AlertDialog(
            title=ft.Text("Recuperar Senha"),
            content=ft.Column(
                [
                    ft.Text(
                        "Digite seu e-mail para receber as instruções de redefinição:",
                        size=13,
                        color="#BDBDBD",
                    ),
                    rec_email,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=lambda _: fechar_dialogo(dialog_rec)
                ),
                ft.ElevatedButton(
                    "Enviar E-mail",
                    bgcolor="#1E88E5",
                    color="#FFFFFF",
                    on_click=enviar_reset,
                ),
            ],
        )
        abrir_dialogo(dialog_rec)

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
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        usuario_atual.update(
            {
                "id": "",
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
                title=ft.Text("Meu Perfil", color="#FFFFFF", weight="bold"),
                on_click=abrir_perfil,
            ),
            ft.Divider(color="#424242"),
            ft.Container(height=20),
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon("logout", color="#EF5350"),
                            ft.Text("Sair", color="#EF5350"),
                        ],
                        alignment="center",
                    ),
                    bgcolor="#2A1215",
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
                foreground_image_src=foto_src, radius=20
            )
        else:
            inicial = (
                usuario_atual.get("nome", "U")[0].upper()
                if usuario_atual.get("nome")
                else "U"
            )
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
                    ft.Row(
                        [
                            ft.Icon("auto_awesome", color="#42A5F5", size=28),
                            ft.Text(
                                "Flow", size=24, weight="bold", color="#FFFFFF"
                            ),
                        ]
                    ),
                    ft.GestureDetector(
                        on_tap=abrir_drawer, content=avatar_content
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

    # --- BUSCAR DADOS DO BANCO ---
    def carregar_dados_usuario(email_user):
        try:
            res = (
                supabase.table("perfis")
                .select("*")
                .eq("email", email_user)
                .execute()
            )
            if res.data:
                perfil = res.data[0]
                usuario_atual.update(
                    {
                        "email": perfil.get("email", email_user),
                        "nome": perfil.get("nome")
                        or email_user.split("@")[0].capitalize(),
                        "celular": perfil.get("celular", ""),
                        "genero": perfil.get("genero", "Não informado"),
                        "foto_url": perfil.get("foto_url", ""),
                    }
                )
            else:
                usuario_atual["email"] = email_user
                usuario_atual["nome"] = email_user.split("@")[0].capitalize()
        except Exception as err:
            print(f"Erro ao buscar perfil: {err}")
            usuario_atual["email"] = email_user
            usuario_atual["nome"] = email_user.split("@")[0].capitalize()

    def buscar_dados_financeiros():
        try:
            res = supabase.table("pagamentos").select("*").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception as err:
            print(f"Lendo pagamentos locais / fallback: {err}")

        # Fallback Mock
        return [
            {
                "nome": "João Silva",
                "filial": "MATRIZ",
                "resp": "Victor",
                "valor": 1500.50,
                "ok": True,
            },
            {
                "nome": "Maria Souza",
                "filial": "FILIAL-01",
                "resp": "Deidla",
                "valor": 850.00,
                "ok": True,
            },
            {
                "nome": "Carlos Santos",
                "filial": "FILIAL-11",
                "resp": "Loja 11",
                "valor": 420.00,
                "ok": False,
            },
            {
                "nome": "Empresa ABC",
                "filial": "MATRIZ",
                "resp": "Victor",
                "valor": 3200.00,
                "ok": True,
            },
        ]

    # --- TELA DE LOGIN ---
    def carregar_tela_login():
        page.controls.clear()
        page.vertical_alignment = "center"
        page.horizontal_alignment = "center"

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

        btn_entrar = ft.ElevatedButton(
            "Entrar no Sistema",
            width=290,
            height=48,
            bgcolor="#1E88E5",
            color="#FFFFFF",
        )

        def acao_login(e):
            email_input.error_text = None
            senha_input.error_text = None

            valido = True
            if not email_input.value:
                email_input.error_text = "Informe o e-mail"
                valido = False
            if not senha_input.value:
                senha_input.error_text = "Informe a senha"
                valido = False

            if not valido:
                page.update()
                return

            alternar_loading(btn_entrar, True, "Entrar no Sistema")

            try:
                res = supabase.auth.sign_in_with_password(
                    {
                        "email": email_input.value,
                        "password": senha_input.value,
                    }
                )
                if res.user:
                    carregar_dados_usuario(res.user.email)
                    mostrar_mensagem("Login realizado com sucesso!")
                    carregar_home()
            except Exception as err:
                erro_str = str(err)
                if (
                    "Invalid login credentials" in erro_str
                    or "invalid_credentials" in erro_str
                ):
                    mostrar_mensagem("E-mail ou senha incorretos.", erro=True)
                    alternar_loading(btn_entrar, False, "Entrar no Sistema")
                else:
                    usuario_atual["email"] = email_input.value
                    usuario_atual["nome"] = (
                        email_input.value.split("@")[0].capitalize()
                    )
                    mostrar_mensagem("Acesso iniciado localmente.")
                    carregar_home()

        btn_entrar.on_click = acao_login

        card_login = ft.Container(
            padding=25,
            bgcolor="#1E1F25",
            border_radius=16,
            width=340,
            content=ft.Column(
                horizontal_alignment="center",
                spacing=15,
                tight=True,
                controls=[
                    ft.Icon("auto_awesome", color="#42A5F5", size=40),
                    ft.Text("Flow", size=28, weight="bold", color="#FFFFFF"),
                    ft.Container(height=5),
                    email_input,
                    senha_input,
                    ft.Row(
                        [
                            ft.TextButton(
                                "Esqueceu a senha?",
                                color="#BDBDBD",
                                on_click=abrir_dialogo_esqueci_senha,
                            )
                        ],
                        alignment="end",
                    ),
                    ft.Container(height=5),
                    btn_entrar,
                    ft.TextButton(
                        "Não tem conta? Cadastre-se",
                        color="#42A5F5",
                        on_click=lambda _: carregar_tela_cadastro(),
                    ),
                ],
            ),
        )

        page.add(card_login)
        page.update()

    # --- TELA DE CADASTRO ---
    def carregar_tela_cadastro():
        page.controls.clear()
        page.vertical_alignment = "center"
        page.horizontal_alignment = "center"

        nome_input = ft.TextField(
            label="Nome Completo", border_color="#2196F3"
        )
        email_input = ft.TextField(
            label="E-mail Corporativo", border_color="#616161"
        )
        senha_input = ft.TextField(
            label="Senha", password=True, can_reveal_password=True
        )

        btn_cadastrar = ft.ElevatedButton(
            "Criar Conta",
            width=290,
            height=48,
            bgcolor="#1E88E5",
            color="#FFFFFF",
        )

        def acao_cadastrar(e):
            nome_input.error_text = None
            email_input.error_text = None
            senha_input.error_text = None

            valido = True
            if not nome_input.value:
                nome_input.error_text = "Informe seu nome"
                valido = False
            if not email_input.value:
                email_input.error_text = "Informe o e-mail"
                valido = False
            if not senha_input.value:
                senha_input.error_text = "Informe a senha"
                valido = False

            if not valido:
                page.update()
                return

            alternar_loading(btn_cadastrar, True, "Criar Conta")

            try:
                res = supabase.auth.sign_up(
                    {
                        "email": email_input.value,
                        "password": senha_input.value,
                        "options": {"data": {"nome": nome_input.value}},
                    }
                )
                usuario_atual["email"] = email_input.value
                usuario_atual["nome"] = nome_input.value

                try:
                    supabase.table("perfis").upsert(
                        {
                            "email": email_input.value,
                            "nome": nome_input.value,
                        }
                    ).execute()
                except Exception:
                    pass

                mostrar_mensagem("Conta criada com sucesso!")
                carregar_home()
            except Exception as err:
                mostrar_mensagem(f"Erro no cadastro: {err}", erro=True)
                alternar_loading(btn_cadastrar, False, "Criar Conta")

        btn_cadastrar.on_click = acao_cadastrar

        card_cadastro = ft.Container(
            padding=25,
            bgcolor="#1E1F25",
            border_radius=16,
            width=340,
            content=ft.Column(
                horizontal_alignment="center",
                spacing=15,
                tight=True,
                controls=[
                    ft.Icon("auto_awesome", color="#42A5F5", size=40),
                    ft.Text("Flow", size=28, weight="bold", color="#FFFFFF"),
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
                    btn_cadastrar,
                    ft.TextButton(
                        "Já possui conta? Faça o login.",
                        color="#42A5F5",
                        on_click=lambda _: carregar_tela_login(),
                    ),
                ],
            ),
        )

        page.add(card_cadastro)
        page.update()

    # --- PAINEL PRINCIPAL (HOME) ---
    def carregar_home():
        page.controls.clear()
        page.vertical_alignment = "start"
        page.horizontal_alignment = "start"

        lista_pagamentos = buscar_dados_financeiros()

        total_faturado = 0.0
        for item in lista_pagamentos:
            val = item.get("valor", 0)
            if isinstance(val, (int, float)):
                total_faturado += val
            elif isinstance(val, str):
                try:
                    total_faturado += float(
                        val.replace("R$", "")
                        .replace(".", "")
                        .replace(",", ".")
                        .strip()
                    )
                except ValueError:
                    pass

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
                        f"R$ {total_faturado:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", "."),
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
                    on_click=lambda _: carregar_home(),
                ),
            ],
        )

        cards_pagamento = []
        for item in lista_pagamentos:
            ok = item.get("ok", True)
            valor_fmt = (
                f"R$ {item['valor']:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if isinstance(item["valor"], (int, float))
                else str(item["valor"])
            )

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
                                        "check_circle" if ok else "access_time_filled",
                                        color="#66BB6A" if ok else "#FFC107",
                                        size=24,
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                item.get("nome", "Cliente"),
                                                weight="bold",
                                                color="#FFFFFF",
                                                size=15,
                                            ),
                                            ft.Text(
                                                f"Filial: {item.get('filial', 'MATRIZ')} | Responsável: {item.get('resp', 'N/A')}",
                                                color="#BDBDBD",
                                                size=11,
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                            ft.Text(
                                valor_fmt,
                                weight="bold",
                                color="#FFFFFF",
                                size=14,
                            ),
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
                    header_pagamentos,
                    *cards_pagamento,
                    ft.Container(height=80),
                ],
            ),
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
        page.vertical_alignment = "start"
        page.horizontal_alignment = "start"

        avatar_preview = ft.CircleAvatar(
            foreground_image_src=usuario_atual.get("foto_url")
            if usuario_atual.get("foto_url")
            else None,
            content=ft.Icon("person", size=40)
            if not usuario_atual.get("foto_url")
            else None,
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
            border_color="#616161",
            on_change=atualizar_preview_foto,
        )

        def ao_selecionar_arquivo(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                arquivo = e.files[0]
                try:
                    nome_arquivo = f"avatar_{usuario_atual.get('email', 'user').replace('@', '_')}.jpg"

                    with open(arquivo.path, "rb") as f:
                        file_bytes = f.read()

                    supabase.storage.from_("avatars").upload(
                        path=nome_arquivo,
                        file=file_bytes,
                        file_options={"upsert": "true"},
                    )

                    public_url = supabase.storage.from_("avatars").get_public_url(
                        nome_arquivo
                    )

                    foto_input.value = public_url
                    avatar_preview.foreground_image_src = public_url
                    avatar_preview.content = None
                    mostrar_mensagem("Foto enviada para o servidor com sucesso!")
                    page.update()
                except Exception as err:
                    mostrar_mensagem(
                        f"Erro ao enviar arquivo (Verifique o bucket 'avatars'): {err}",
                        erro=True,
                    )

        file_picker = ft.FilePicker(on_result=ao_selecionar_arquivo)
        page.overlay.append(file_picker)

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

        btn_salvar_perfil = ft.ElevatedButton(
            "Salvar Informações",
            width=400,
            height=50,
            bgcolor="#1E88E5",
            color="#FFFFFF",
        )

        def salvar_perfil(e):
            alternar_loading(btn_salvar_perfil, True, "Salvar Informações")

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
                mostrar_mensagem("Perfil atualizado no Supabase com sucesso!")
            except Exception:
                mostrar_mensagem("Perfil salvo localmente.")

            carregar_home()

        btn_salvar_perfil.on_click = salvar_perfil

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

        form_perfil = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(
                scroll="auto",
                spacing=15,
                controls=[
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=avatar_preview,
                    ),
                    ft.OutlinedButton(
                        "📷 Upload de Foto do Aparelho",
                        icon="upload_file",
                        on_click=lambda _: file_picker.pick_files(
                            allow_multiple=False,
                            file_type=ft.FilePickerFileType.IMAGE,
                        ),
                    ),
                    foto_input,
                    nome_input,
                    celular_input,
                    genero_input,
                    ft.Container(height=10),
                    btn_salvar_perfil,
                ],
            ),
        )

        page.add(ft.Column(expand=True, controls=[header_perfil, form_perfil]))
        page.update()

    # --- INICIALIZAÇÃO DA APLICAÇÃO ---
    carregar_tela_login()
    verificar_atualizacao()


ft.app(target=main)
