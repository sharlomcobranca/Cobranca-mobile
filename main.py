import flet as ft
from supabase import create_client, Client

# ==============================================================================
# 🎨 PALETA DE CORES PREMIUM (DARK MODE ELEGANTE)
# ==============================================================================
APP_NAME = "Flow"
VERSAO_ATUAL_APP = "1.0.0"

C_BG_PRIMARY    = "#1A1A1A"  # Fundo principal
C_CARD          = "#25272C"  # Cards
C_BLUE_PRIMARY  = "#1F6FEB"  # Azul principal
C_BLUE_HOVER    = "#2979FF"  # Azul destaque
C_SUCCESS       = "#2ECC71"  # Verde sucesso
C_WARNING      = "#F4B400"  # Amarelo alerta
C_ERROR        = "#EF4444"  # Vermelho erro
C_TEXT_MAIN     = "#F3F3F3"  # Texto principal
C_TEXT_MUTED    = "#B9BEC7"  # Texto secundário
C_BORDER        = "#353942"  # Bordas

SUPABASE_URL = "https://vccshrmzbubwzmfdgzqi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjY3Nocm16YnVid3ptZmRnenFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTcwMTQsImV4cCI6MjEwMDU3MzAxNH0.3RmDObR5_YfTTN87Yl7QwMEmTQh09JVRCakzGIfqHCE"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None


def main(page: ft.Page):
    page.title = f"{APP_NAME} Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = C_BG_PRIMARY
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    def checar_atualizacao():
        if not supabase:
            return
        try:
            res = supabase.table("configuracoes").select("versao_apk, link_download").eq("id", 1).execute()
            if res.data:
                config = res.data[0]
                versao_nuvem = config.get("versao_apk")
                link_download = config.get("link_download")

                if versao_nuvem and versao_nuvem != VERSAO_ATUAL_APP:
                    dlg_atualizacao = ft.AlertDialog(
                        bgcolor=C_CARD,
                        title=ft.Text("🚀 Nova Atualização!", color=C_TEXT_MAIN, weight=ft.FontWeight.BOLD),
                        content=ft.Text(f"A versão {versao_nuvem} está disponível.", color=C_TEXT_MUTED),
                        actions=[
                            ft.ElevatedButton(
                                "📥 Baixar Agora",
                                on_click=lambda e: page.launch_url(link_download),
                                style=ft.ButtonStyle(bgcolor=C_BLUE_PRIMARY, color=C_TEXT_MAIN)
                            )
                        ],
                    )
                    page.dialog = dlg_atualizacao
                    dlg_atualizacao.open = True
                    page.update()
        except Exception:
            pass

    # --------------------------------------------------------------------------
    # 🔐 TELA DE LOGIN / CADASTRO
    # --------------------------------------------------------------------------
    is_cadastro = False

    def alternar_modo(e):
        nonlocal is_cadastro
        is_cadastro = not is_cadastro
        
        container_nome.visible = is_cadastro
        container_filial.visible = is_cadastro
        btn_acao.text = "✨ Criar Conta" if is_cadastro else "🔑 Entrar no Sistema"
        btn_alternar.text = "Já tem uma conta? Faça Login" if is_cadastro else "Não tem conta? Cadastre-se"
        lbl_subtitulo.value = "Criar nova credencial de acesso" if is_cadastro else "Painel Gestor Mobile"
        lbl_erro.value = ""
        page.update()

    def processar_autenticacao(e):
        email = ent_email.value.strip()
        senha = ent_senha.value.strip()
        nome = ent_nome.value.strip()
        filial = drop_filial.value

        if not email or not senha or (is_cadastro and not nome):
            lbl_erro.color = C_ERROR
            lbl_erro.value = "Preencha todos os campos obrigatórios!"
            page.update()
            return

        if not supabase:
            lbl_erro.color = C_ERROR
            lbl_erro.value = "Erro na conexão com a nuvem."
            page.update()
            return

        btn_acao.disabled = True
        lbl_erro.color = C_TEXT_MUTED
        lbl_erro.value = "Processando..."
        page.update()

        try:
            if is_cadastro:
                auth_res = supabase.auth.sign_up({"email": email, "password": senha})
                user_id = auth_res.user.id if auth_res.user else None

                if user_id:
                    nivel_usuario = "matriz" if filial == "MATRIZ" else "operador"
                    supabase.table("perfis").insert({
                        "id": user_id,
                        "email": email,
                        "nome": nome,
                        "nivel": nivel_usuario,
                        "filial_id": filial
                    }).execute()

                lbl_erro.color = C_SUCCESS
                lbl_erro.value = "Conta criada com sucesso! Faça login."
                alternar_modo(None)
            else:
                auth_res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                user_id = auth_res.user.id if auth_res.user else None

                if user_id:
                    perfil_res = supabase.table("perfis").select("*").eq("id", user_id).execute()
                    if perfil_res.data and len(perfil_res.data) > 0:
                        abrir_painel_principal(perfil_res.data[0])
                    else:
                        # Se não achou na tabela 'perfis', cria um objeto temporário com o email do auth
                        abrir_painel_principal({
                            "id": user_id,
                            "email": email,
                            "nome": email.split("@")[0].capitalize(),
                            "nivel": "matriz",
                            "filial_id": "MATRIZ"
                        })
                else:
                    lbl_erro.color = C_ERROR
                    lbl_erro.value = "Falha ao autenticar usuário."

        except Exception as ex:
            lbl_erro.color = C_ERROR
            lbl_erro.value = f"Erro: {str(ex)}"
        
        btn_acao.disabled = False
        page.update()

    # Campos
    ent_nome = ft.TextField(label="Nome Completo", width=300, border_color=C_BORDER, color=C_TEXT_MAIN, focused_border_color=C_BLUE_PRIMARY)
    container_nome = ft.Container(content=ent_nome, visible=False)

    drop_filial = ft.Dropdown(
        label="Filial de Acesso", width=300, border_color=C_BORDER, color=C_TEXT_MAIN, focused_border_color=C_BLUE_PRIMARY, value="MATRIZ",
        options=[
            ft.dropdown.Option("MATRIZ", "👑 Matriz Central"),
            ft.dropdown.Option("FILIAL-01", "🏬 Filial 01"),
            ft.dropdown.Option("FILIAL-02", "🏬 Filial 02"),
            ft.dropdown.Option("FILIAL-11", "🏬 Filial 11"),
        ]
    )
    container_filial = ft.Container(content=drop_filial, visible=False)

    ent_email = ft.TextField(label="E-mail Corporativo", width=300, border_color=C_BORDER, color=C_TEXT_MAIN, focused_border_color=C_BLUE_PRIMARY)
    ent_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300, border_color=C_BORDER, color=C_TEXT_MAIN, focused_border_color=C_BLUE_PRIMARY)
    
    lbl_erro = ft.Text("", color=C_ERROR, size=12)
    lbl_subtitulo = ft.Text("Painel Gestor Mobile", size=12, color=C_TEXT_MUTED)

    btn_acao = ft.ElevatedButton(
        "🔑 Entrar no Sistema", on_click=processar_autenticacao,
        style=ft.ButtonStyle(bgcolor=C_BLUE_PRIMARY, color=C_TEXT_MAIN, shape=ft.RoundedRectangleBorder(radius=8)), width=300
    )

    btn_alternar = ft.TextButton("Não tem conta? Cadastre-se", on_click=alternar_modo, style=ft.ButtonStyle(color=C_BLUE_HOVER))

    card_login = ft.Card(
        elevation=4,
        content=ft.Container(
            bgcolor=C_CARD, border_radius=8,
            content=ft.Column([
                ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=44, color=C_BLUE_PRIMARY),
                ft.Text(APP_NAME, size=24, weight=ft.FontWeight.BOLD, color=C_TEXT_MAIN),
                lbl_subtitulo,
                ft.Container(height=10),
                container_nome,
                ent_email,
                ent_senha,
                container_filial,
                lbl_erro,
                btn_acao,
                btn_alternar
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=25
        )
    )

    def reiniciar_tela_login(e=None):
        page.clean()
        page.add(card_login)
        page.update()

    # --------------------------------------------------------------------------
    # 2. PAINEL PRINCIPAL
    # --------------------------------------------------------------------------
    def abrir_painel_principal(usuario):
        try:
            email_bruto = usuario.get("email") or "Usuario"
            nome_usuario = usuario.get("nome") or email_bruto.split("@")[0].capitalize()
            nivel_usuario = usuario.get("nivel", "matriz")
            filial_usuario = usuario.get("filial_id", "MATRIZ")

            lbl_total = ft.Text("R$ 0,00", size=26, weight=ft.FontWeight.BOLD, color=C_SUCCESS)
            list_view = ft.ListView(spacing=10, padding=10)

            def carregar_dados(e=None):
                list_view.controls.clear()
                if not supabase:
                    list_view.controls.append(ft.Text("Sem conexão com o banco.", color=C_ERROR))
                    page.update()
                    return
                try:
                    query = supabase.table("pagamentos_processados").select("*")
                    if nivel_usuario == "operador":
                        query = query.eq("filial_id", filial_usuario)

                    res = query.execute()
                    dados = res.data or []

                    total = sum(float(item.get("valor_pagamento", 0) or 0) for item in dados)
                    lbl_total.value = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    if not dados:
                        list_view.controls.append(ft.Text("Nenhum registro de pagamento encontrado.", color=C_TEXT_MUTED))
                    else:
                        for row in dados:
                            status = row.get("status_whatsapp", "Pendente")
                            status_icon = ft.Icons.CHECK_CIRCLE_ROUNDED if status == "Enviado" else ft.Icons.SCHEDULE_ROUNDED
                            status_color = C_SUCCESS if status == "Enviado" else C_WARNING
                            valor = float(row.get("valor_pagamento", 0) or 0)

                            list_view.controls.append(
                                ft.Card(
                                    elevation=2,
                                    content=ft.Container(
                                        bgcolor=C_CARD, border_radius=8,
                                        content=ft.ListTile(
                                            leading=ft.Icon(status_icon, color=status_color),
                                            title=ft.Text(f"{row.get('cliente', 'Cliente')}", color=C_TEXT_MAIN, weight=ft.FontWeight.W_600),
                                            subtitle=ft.Text(
                                                f"Filial: {row.get('filial_id', 'N/A')} | Responsável: {row.get('responsavel', 'N/A')}",
                                                color=C_TEXT_MUTED, size=11
                                            ),
                                            trailing=ft.Text(f"R$ {valor:,.2f}", weight=ft.FontWeight.BOLD, color=C_TEXT_MAIN)
                                        )
                                    )
                                )
                            )
                except Exception as ex:
                    list_view.controls.append(ft.Text(f"Erro ao carregar lista: {str(ex)}", color=C_ERROR))
                page.update()

            page.clean()
            page.add(
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=20, color=C_BLUE_PRIMARY),
                        ft.Text(APP_NAME, size=20, weight=ft.FontWeight.BOLD, color=C_TEXT_MAIN),
                    ]),
                    ft.Text(f"[{nome_usuario}]", size=12, color=C_BLUE_HOVER, weight=ft.FontWeight.W_600)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=C_BORDER),
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor=C_CARD, border_radius=8,
                        content=ft.Column([
                            ft.Text("Faturamento Total (Nuvem)", size=12, color=C_TEXT_MUTED),
                            lbl_total
                        ]), padding=20
                    )
                ),
                ft.Row([
                    ft.Text("📑 Histórico Recente", size=16, weight=ft.FontWeight.BOLD, color=C_TEXT_MAIN),
                    ft.IconButton(icon=ft.Icons.REFRESH, icon_color=C_BLUE_PRIMARY, on_click=carregar_dados)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(content=list_view, height=350),
                ft.ElevatedButton("Sair", on_click=reiniciar_tela_login, style=ft.ButtonStyle(bgcolor=C_BORDER, color=C_TEXT_MAIN))
            )
            carregar_dados()

        except Exception as err:
            page.clean()
            page.add(
                ft.Text("Ocorreu um erro ao abrir o painel:", color=C_ERROR, weight=ft.FontWeight.BOLD),
                ft.Text(str(err), color=C_TEXT_MAIN),
                ft.ElevatedButton("Voltar para o Login", on_click=reiniciar_tela_login)
            )
            page.update()

    page.add(card_login)
    checar_atualizacao()


ft.app(target=main)
