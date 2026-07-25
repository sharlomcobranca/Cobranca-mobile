import flet as ft
from supabase import create_client, Client

# ==============================================================================
# 📌 CONFIGURAÇÕES DO SISTEMA E SUPABASE
# ==============================================================================
VERSAO_ATUAL_APP = "1.0.0"

SUPABASE_URL = "https://vccshrmzbubwzmfdgzqi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjY3Nocm16YnVid3ptZmRnenFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTcwMTQsImV4cCI6MjEwMDU3MzAxNH0.3RmDObR5_YfTTN87Yl7QwMEmTQh09JVRCakzGIfqHCE"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None


def main(page: ft.Page):
    page.title = "Cobrança PRO Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # --------------------------------------------------------------------------
    # 🔔 VERIFICADOR DE ATUALIZAÇÃO AUTOMÁTICA
    # --------------------------------------------------------------------------
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
                        title=ft.Text("🚀 Nova Atualização!"),
                        content=ft.Text(f"A versão {versao_nuvem} já está disponível.\nClique abaixo para baixar."),
                        actions=[
                            ft.ElevatedButton(
                                "📥 Baixar Agora",
                                on_click=lambda e: page.launch_url(link_download),
                                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
                            )
                        ],
                    )
                    page.dialog = dlg_atualizacao
                    dlg_atualizacao.open = True
                    page.update()
        except Exception:
            pass

    # --------------------------------------------------------------------------
    # 1. TELA DE LOGIN
    # --------------------------------------------------------------------------
    def tentar_login(e):
        email = ent_email.value.strip()
        senha = ent_senha.value.strip()

        if not email or not senha:
            lbl_erro.value = "Preencha e-mail e senha!"
            page.update()
            return

        if not supabase:
            lbl_erro.value = "Erro na conexão com o Supabase."
            page.update()
            return

        btn_login.disabled = True
        lbl_erro.value = "Conectando..."
        page.update()

        try:
            # Autenticação na nuvem
            auth_res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            user_id = auth_res.user.id

            # Busca o nível e a filial do usuário
            perfil_res = supabase.table("perfis").select("*").eq("id", user_id).execute()
            
            if perfil_res.data:
                usuario = perfil_res.data[0]
                abrir_painel_principal(usuario)
            else:
                lbl_erro.value = "Perfil não cadastrado na tabela 'perfis'."
                btn_login.disabled = False
                page.update()

        except Exception as ex:
            # MOSTRA O ERRO EXATO RETORNADO PELO SUPABASE
            lbl_erro.value = f"Erro: {str(ex)}"
            btn_login.disabled = False
            page.update()

    ent_email = ft.TextField(label="E-mail Corporativo", width=300)
    ent_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    lbl_erro = ft.Text("", color=ft.Colors.RED_400, size=12)
    btn_login = ft.ElevatedButton(
        "🔑 Entrar no Sistema",
        on_click=tentar_login,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
        width=300
    )

    card_login = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SMART_TOY_ROUNDED, size=48, color=ft.Colors.BLUE_400),
                ft.Text("Cobrança PRO", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Painel Gestor Mobile", size=12, color=ft.Colors.GREY_400),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ent_email,
                ent_senha,
                lbl_erro,
                btn_login
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30
        )
    )

    # --------------------------------------------------------------------------
    # 2. PAINEL PRINCIPAL
    # --------------------------------------------------------------------------
    def abrir_painel_principal(usuario):
        page.clean()

        lbl_total = ft.Text("R$ 0,00", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        list_view = ft.ListView(expand=True, spacing=10, padding=10)

        def carregar_dados(e=None):
            list_view.controls.clear()
            try:
                query = supabase.table("pagamentos_processados").select("*")
                
                # Se for Operador, filtra apenas a filial dele
                if usuario["nivel"] == "operador":
                    query = query.eq("filial_id", usuario["filial_id"])

                res = query.execute()
                dados = res.data

                # Calcula total
                total = sum(item.get("valor_pagamento", 0) for item in dados)
                lbl_total.value = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                # Popula histórico
                if not dados:
                    list_view.controls.append(ft.Text("Nenhum registro encontrado.", color=ft.Colors.GREY_400))
                else:
                    for row in dados:
                        status = row.get("status_whatsapp", "Pendente")
                        status_icon = ft.Icons.CHECK_CIRCLE if status == "Enviado" else ft.Icons.ACCESS_TIME_FILLED
                        status_color = ft.Colors.GREEN_400 if status == "Enviado" else ft.Colors.AMBER_400

                        list_view.controls.append(
                            ft.Card(
                                content=ft.ListTile(
                                    leading=ft.Icon(status_icon, color=status_color),
                                    title=ft.Text(f"{row.get('cliente', 'Cliente')}"),
                                    subtitle=ft.Text(f"Filial: {row.get('filial_id')} | Responsável: {row.get('responsavel', 'N/A')}"),
                                    trailing=ft.Text(f"R$ {row.get('valor_pagamento', 0):,.2f}", weight=ft.FontWeight.BOLD)
                                )
                            )
                        )
            except Exception as ex:
                list_view.controls.append(ft.Text(f"Erro ao buscar dados: {ex}", color=ft.Colors.RED_400))
            page.update()

        nivel_str = f"👑 Matriz" if usuario['nivel'] == 'matriz' else f"🏬 {usuario['filial_id']}"

        page.add(
            ft.Row([
                ft.Text("🤖 Cobrança PRO", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"[{nivel_str}]", size=12, color=ft.Colors.BLUE_300)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Faturamento Total (Nuvem)", size=12, color=ft.Colors.GREY_300),
                        lbl_total
                    ]),
                    padding=20
                )
            ),
            ft.Row([
                ft.Text("📑 Histórico Recente", size=16, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.Icons.REFRESH, on_click=carregar_dados)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(content=list_view, height=380)
        )
        carregar_dados()

    page.add(card_login)
    
    # Executa verificação ao abrir o app
    checar_atualizacao()


ft.app(target=main)
