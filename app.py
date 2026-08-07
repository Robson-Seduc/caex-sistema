# =======================================================================
# PARTE 1: CONFIGURAÇÕES INICIAIS, CACHE DE DADOS E BACKUP AUTOMÁTICO
# =======================================================================

import streamlit as strl
import pandas as pd
import shutil
from datetime import datetime
import os
import socket
import getpass

# Configuração estável da página do navegador (Título, Layout Amplo e Ícone)
strl.set_page_config(page_title="CAEX - Sistema Integrado", layout="wide", page_icon="icone.png")

# Nome exato do seu arquivo Excel no formato padrão corporativo do projeto
ARQUIVO_EXCEL = "Controle de Alunos Escolas Extintas - CAEX.xlsx"

# CONFIGURAÇÃO INTERNA E FIXA DA CONTA MASTER DO DIRETOR
USUARIO_MASTER = "ROBSON.TEIXEIRA@SEDUC.GO.GOV.BR"
SENHA_MASTER = "Rs52846917Lm*"

# -----------------------------------------------------------------------
# ENGINE DE SESSÃO NATIVA: Mantém as chaves de login salvas na memória local
# -----------------------------------------------------------------------
if "autenticado" not in strl.session_state:
    strl.session_state["autenticado"] = False
if "usuario_nome" not in strl.session_state:
    strl.session_state["usuario_nome"] = ""
if "usuario_nivel" not in strl.session_state:
    strl.session_state["usuario_nivel"] = ""
if "usuario_login" not in strl.session_state:
    strl.session_state["usuario_login"] = ""

# -----------------------------------------------------------------------
# ESCUDO AUTOMÁTICO DE SEGURANÇA: Rotina de cópia diária de salvaguarda
# -----------------------------------------------------------------------
def realizar_backup_automatico():
    try:
        pasta_backup = "BACKUP_DIARIO"
        if not os.path.exists(pasta_backup):
            os.makedirs(pasta_backup)
        
        data_atual = datetime.now().strftime("%d_%m_%Y")
        nome_backup = os.path.join(pasta_backup, f"BACKUP_CAEX_{data_atual}.xlsx")
        
        if not os.path.exists(nome_backup) and os.path.exists(ARQUIVO_EXCEL):
            shutil.copy2(ARQUIVO_EXCEL, nome_backup)
    except:
        pass

realizar_backup_automatico()

# =======================================================================
# PARTE 2: MOTORES DE AUDITORIA DE REDE E CARREGADORES DO BANCO DE DADOS
# =======================================================================

# -----------------------------------------------------------------------
# LIVRO DE AUDITORIA: Registra DATA, PC, REDE, NOME e AÇÃO no LOG do Excel
# -----------------------------------------------------------------------
def registrar_log_auditoria(nome_funcionario, acao_realizada):
    try:
        nome_pc = socket.gethostname().upper()
        usuario_rede = getpass.getuser().upper()
        
        try:
            df_log = pd.read_excel(ARQUIVO_EXCEL, sheet_name="LOG")
        except:
            df_log = pd.DataFrame(columns=["DATA", "PC", "REDE", "USUÁRIO /NOME", "AÇÃO"])
            
        nova_linha_log = pd.DataFrame([{
            "DATA": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "PC": nome_pc,
            "REDE": usuario_rede,
            "USUÁRIO /NOME": str(nome_funcionario).upper().strip(),
            "AÇÃO": str(acao_realizada).upper().strip()
        }])
        
        df_log_atualizado = pd.concat([df_log, nova_linha_log], ignore_index=True)
        with pd.ExcelWriter(ARQUIVO_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_log_atualizado.to_excel(writer, sheet_name="LOG", index=False)
    except:
        pass

# -----------------------------------------------------------------------
# ENGINE DE LEITURA DO ACERVO: Carrega as 27 mil linhas tratadas em CAIXA ALTA
# -----------------------------------------------------------------------
def carregar_dados_bd():
    try:
        df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="BD")
        df = df.fillna("NÃO IDENTIFICADO")
        for col in ["UNIDADE ESCOLAR", "NOME DO ALUNO(A)", "Nº DA PASTA", "PASTA ARQUIVO"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        strl.error(f"ERRO CRÍTICO AO LER BANCO DE DADOS (ABA BD): {e}")
        return pd.DataFrame()

def carregar_lista_escolas():
    try:
        df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="ESCOLAS")
        if not df.empty:
            colunas_maiusculas = [str(c).strip().upper() for c in df.columns]
            coluna_encontrada = None
            for nome_col_original, nome_col_up in zip(df.columns, colunas_maiusculas):
                if "ESCOLA" in nome_col_up or "UNIDADE" in nome_col_up:
                    coluna_encontrada = nome_col_original
                    break
            if coluna_encontrada:
                lista = df[coluna_encontrada].dropna().astype(str).str.strip().str.upper().unique()
                return sorted(list(lista))
        return []
    except:
        return []

# Ativa o banco de dados principal na memória
df_dados = carregar_dados_bd()

# Desenha o cabeçalho identitário azul
strl.markdown(
    """
    <div style="background-color:#1e40af; padding:15px; border-radius:10px; margin-bottom:25px;">
        <h1 style="color:white; text-align:center; margin:0; font-family:sans-serif; font-size: 28px;">
            CONTROLE DE ALUNOS ESCOLAS EXTINTAS - CAEX
        </h1>
    </div>
    """, 
    unsafe_allow_html=True
)

# =======================================================================
# PARTE 3: FORMULÁRIOS FLUTUANTES (POP-UPS) DA TELA DE LOGIN
# =======================================================================

@strl.dialog("📝 COMPLEMENTO DE CADASTRO - NOVO USUÁRIO")
def popup_solicitar_cadastro():
    strl.markdown("Insira os dados abaixo para criar uma conta de acesso. **O usuário deve ser o seu e-mail pessoal.**")
    c_user = strl.text_input("Defina o Usuário (Seu E-mail Pessoal):").strip().upper()
    c_pass = strl.text_input("Defina a Senha:", type="password").strip()
    c_nome = strl.text_input("Nome Completo:").strip().upper()
    c_fone = strl.text_input("Telefone / Contato:", placeholder="EX: 62933005329").strip()
    
    if strl.button("💾 Enviar Solicitação de Cadastro"):
        if not c_user or not c_pass or not c_nome:
            strl.error("❌ ERRO: OS CAMPOS USUÁRIO, SENHA E NOME SÃO OBRIGATÓRIOS!")
        elif "@" not in c_user or "." not in c_user:
            strl.error("❌ ERRO: O USUÁRIO DEVE SER OBRIGATORIAMENTE UM E-MAIL VÁLIDO!")
        else:
            with strl.spinner("GRAVANDO REQUISIÇÃO..."):
                try:
                    df_usuarios = pd.read_excel(ARQUIVO_EXCEL, sheet_name="USER")
                    df_usuarios.columns = [str(c).strip().upper() for c in df_usuarios.columns]
                    col_user_real = "USUÁRIO" if "USUÁRIO" in df_usuarios.columns else "USUARIO"
                    
                    if (df_usuarios[col_user_real].astype(str).str.upper() == c_user).any():
                        strl.warning("Este e-mail de usuário já está cadastrado no sistema!")
                    else:
                        fone_limpo = "".join([char for char in c_fone if char.isdigit()])
                        fone_formatado = c_fone.upper()
                        if len(fone_limpo) == 11:
                            fone_formatado = f"({fone_limpo[:2]}) {fone_limpo[2:7]}-{fone_limpo[7:]}"
                        elif len(fone_limpo) == 10:
                            fone_formatado = f"({fone_limpo[:2]}) {fone_limpo[2:6]}-{fone_limpo[6:]}"
                        
                        col_nivel_nome = "NÍVEL" if "NÍVEL" in df_usuarios.columns else "NIVEL"
                        col_user_nome = "USUÁRIO" if "USUÁRIO" in df_usuarios.columns else "USUARIO"
                        
                        nova_linha_user = pd.DataFrame([{
                            col_user_nome: c_user, "SENHA": c_pass, "NOME": c_nome, "FONE": fone_formatado, col_nivel_nome: "1"
                        }])
                        df_user_atualizado = pd.concat([df_usuarios, nova_linha_user], ignore_index=True)
                        with pd.ExcelWriter(ARQUIVO_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                            df_user_atualizado.to_excel(writer, sheet_name="USER", index=False)
                        
                        registrar_log_auditoria(c_nome, "CRIOU UMA NOVA CONTA DE ACESSO VIA E-MAIL PESSOAL (NÍVEL 1)")
                        strl.success("Conta criada com sucesso!")
                        strl.rerun()
                except Exception as e_c:
                    strl.error(f"Erro ao salvar cadastro: {e_c}")



# =======================================================================
# PARTE 3.1: FORMULÁRIOS REQUERIMENTO DE ELEVAÇÃO DE NÍVEL (CORRIGIDO)
# =======================================================================
@strl.dialog("📈 REQUERIMENTO DE ELEVAÇÃO DE NÍVEL")
def popup_pedir_elevacao():
    strl.markdown("Preencha os dados da conta atual. Sua justificativa será registrada no LOG do sistema para avaliação imediata do Administrador Master.")
    e_user = strl.text_input("Informe seu E-mail de Usuário:").strip().upper()
    e_pass = strl.text_input("Confirme sua Senha Atual:", type="password").strip()
    e_nivel = strl.selectbox("Selecione o Nível Desejado:", ["2 - EDITOR (CONSULTA, EDIÇÃO E INSERÇÃO)", "3 - ADMINISTRADOR (TOTAL)"])
    e_just = strl.text_area("Justificativa do Pedido de Promoção:")
    
    if strl.button("📥 Enviar Requerimento"):
        if not e_user or not e_pass or not e_just.strip():
            strl.error("Todos os campos de validação e justificativa são obrigatórios!")
        else:
            try:
                # Validação das credenciais do funcionário no Excel
                df_usuarios = pd.read_excel(ARQUIVO_EXCEL, sheet_name="USER")
                df_usuarios.columns = [str(c).strip().upper() for c in df_usuarios.columns]
                col_user_real = "USUÁRIO" if "USUÁRIO" in df_usuarios.columns else "USUARIO"
                
                validacao = (df_usuarios[col_user_real].astype(str).str.upper() == e_user) & (df_usuarios["SENHA"].astype(str) == e_pass)
                user_encontrado = df_usuarios[validacao]
                
                if not user_encontrado.empty:
                    nome_funcionario = str(user_encontrado.iloc[0]["NOME"]).upper()
                    nivel_alvo = e_nivel[:1]
                    
                    # Carimba a solicitação no LOG com uma tag padrão para o painel identificar depois
                    mensagem_log_formatada = f"PEDIDO_PENDENTE | NÍVEL SOLICITADO: {nivel_alvo} | JUSTIFICATIVA: {e_just.upper()}"
                    registrar_log_auditoria(nome_funcionario, mensagem_log_formatada)
                    
                    strl.success("✅ REQUERIMENTO PROTOCOLADO COM SUCESSO!")
                    strl.rerun()
                else:
                    strl.error("Credenciais inválidas. Verifique seu e-mail e senha atual.")
            except Exception as err_envio:
                strl.error(f"Erro ao processar requisição: {err_envio}")



# =======================================================================
# PARTE 3.2: PAINEL CENTRAL (BUSCA RÁPIDA, DASHBOARD E CENTRAL DE NOTIFICAÇÕES)
# =======================================================================
if tela_selecionada == "🔍 PAINEL CENTRAL":
    
    # -----------------------------------------------------------------------
    # CENTRAL DE ALERTAS MASTER: Mostra notificações se o usuário for o Robson (Nível 3)
    # -----------------------------------------------------------------------
    if strl.session_state["usuario_login"] == "3":
        try:
            df_log_check = pd.read_excel(ARQUIVO_EXCEL, sheet_name="LOG")
            df_log_check.columns = [str(c).strip().upper() for c in df_log_check.columns]
            
            # Filtra na tabela LOG se existem linhas contendo a tag de pedido pendente
            pedidos_pendentes = df_log_check[df_log_check["AÇÃO"].str.contains("PEDIDO_PENDENTE", na=False)]
            
            if not pedidos_pendentes.empty:
                for idx, linha_pedido in pedidos_pendentes.iterrows():
                    funcionario_pedinte = linha_pedido["USUÁRIO /NOME"]
                    detalhes_acao = str(linha_pedido["AÇÃO"])
                    data_pedido = linha_pedido["DATA"]
                    
                    # Processa o texto do log de forma segura usando split
                    partes_pedido = detalhes_acao.split("|")
                    if len(partes_pedido) >= 3:
                        nivel_pedido = partes_pedido[1].replace("NÍVEL SOLICITADO:", "").strip()
                        justificativa_pedido = partes_pedido[2].replace("JUSTIFICATIVA:", "").strip()
                        
                        # Renderiza o Card de Notificação Amarelo Alerta na sua tela principal
                        strl.warning(f"""
                            ⚠️ **SOLICITAÇÃO DE PROMOÇÃO DETECTADA ({data_pedido})**  
                            • **Funcionário:** {funcionario_pedinte}  
                            • **Nível Solicitado:** NÍVEL {nivel_pedido}  
                            • **Justificativa:** "{justificativa_pedido}"  
                            *Instruções: Para aprovar, abra a aba 'USER' do Excel, altere o nível deste funcionário e salve o arquivo.*
                        """)
        except:
            pass

    # Segue o fluxo normal das colunas de busca do Painel Central
    col_esquerda, col_direita = strl.columns([0.6, 0.4], gap="large")


# =======================================================================
# PARTE 4: INTERFACE GRÁFICA DE LOGIN, VALIDAÇÃO E MENUS DA BARRA LATERAL
# =======================================================================

if not strl.session_state["autenticado"]:
    strl.markdown("### 🔐 ACESSO RESTRITO - CONTROLE DE ACESSO")
    
    col_input1, col_input2 = strl.columns(2)
    with col_input1:
        usuario_digitado = strl.text_input("E-MAIL DE USUÁRIO:", placeholder="EXEMPLO@EMAIL.COM")
    with col_input2:
        senha_digitada = strl.text_input("SENHA:", type="password", placeholder="DIGITE SUA SENHA RESTRITA")
        
    btn_l1, btn_l2, btn_l3 = strl.columns(3)
    with btn_l1:
        btn_entrar = strl.button("🔓 ENTRAR NO SISTEMA", use_container_width=True)
    with btn_l2:
        if strl.button("📝 CADASTRAR NOVO USUÁRIO", use_container_width=True):
            popup_solicitar_cadastro()
    with btn_l3:
        if strl.button("📈 SOLICITAR ELEVAÇÃO DE NÍVEL", use_container_width=True):
            popup_pedir_elevacao()
    
    if btn_entrar:
        u_clean = usuario_digitado.strip().upper()
        s_clean = senha_digitada.strip()
        
        if u_clean == "" or s_clean == "":
            strl.error("❌ POR FAVOR, PREENCHA OS CAMPOS DE USUÁRIO E SENHA!")
        # 1. VALIDAÇÃO PRIORITÁRIA DA CONTA MASTER DO DIRETOR
        elif u_clean == USUARIO_MASTER and s_clean == SENHA_MASTER:
            strl.session_state["autenticado"] = True
            strl.session_state["usuario_nome"] = "ROBSON TEIXEIRA"
            strl.session_state["usuario_nivel"] = "3 - ADMINISTRADOR MASTER (TOTAL)"
            strl.session_state["usuario_login"] = "3"
            registrar_log_auditoria("ROBSON TEIXEIRA", "REALIZOU LOGIN VIA CONTA MASTER INTERNA")
            strl.rerun()
        # 2. VALIDAÇÃO DAS DEMAIS CONTAS ARMAZENADAS NA PLANILHA
        else:
            try:
                df_usuarios = pd.read_excel(ARQUIVO_EXCEL, sheet_name="USER")
                df_usuarios = df_usuarios.fillna("NÃO IDENTIFICADO")
                df_usuarios.columns = [str(c).strip().upper() for c in df_usuarios.columns]
                
                col_user_real = "USUÁRIO" if "USUÁRIO" in df_usuarios.columns else "USUARIO"
                col_nivel_real = "NÍVEL" if "NÍVEL" in df_usuarios.columns else "NIVEL"
                
                filtro_user = (df_usuarios[col_user_real].astype(str).str.strip().str.upper() == u_clean) & \
                              (df_usuarios["SENHA"].astype(str).str.strip() == s_clean)
                usuario_valido = df_usuarios[filtro_user]
                
                if not usuario_valido.empty:
                    nome_real = str(usuario_valido.iloc[0]["NOME"]).upper().strip()
                    nivel_acesso = str(usuario_valido.iloc[0][col_nivel_real]).strip()
                    
                    legendas_nivel = {"1": "1 - CONSULTA (RESTRITO)", "2": "2 - EDITOR (PROMOVIDO)", "3": "3 - ADMINISTRADOR (TOTAL)"}
                    nivel_legenda = legendas_nivel.get(nivel_acesso, f"{nivel_acesso} - DESCONHECIDO")
                    
                    strl.session_state["autenticado"] = True
                    strl.session_state["usuario_nome"] = nome_real
                    strl.session_state["usuario_nivel"] = nivel_legenda
                    strl.session_state["usuario_login"] = nivel_acesso
                    
                    registrar_log_auditoria(nome_real, f"REALIZOU LOGIN COM SUCESSO (NÍVEL {nivel_acesso})")
                    strl.rerun()
                else:
                    strl.error("❌ USUÁRIO OU SENHA INCORRETOS! ACESSO NEGADO.")
            except Exception as err_user:
                strl.error(f"❌ ERRO CRÍTICO AO ACESSAR TABELA DE USUÁRIOS: {err_user}")
    strl.stop()

# -----------------------------------------------------------------------
# INTERFACE LOGADA: Montagem dos Menus da Barra Lateral Cinza
# -----------------------------------------------------------------------
strl.sidebar.markdown(f"👤 **OPERADOR:** {strl.session_state['usuario_nome']}")
strl.sidebar.markdown(f"🏷️ **NÍVEL:** {strl.session_state['usuario_nivel']}")

if strl.session_state["usuario_login"] in ["1", "2"]:
    if strl.sidebar.button("📈 SOLICITAR MUDANÇA DE NÍVEL", use_container_width=True):
        popup_pedir_elevacao()

if strl.sidebar.button("🚪 SAIR DO SISTEMA", use_container_width=True):
    registrar_log_auditoria(strl.session_state["usuario_nome"], "LOGOU-SE PARA FORA DO SISTEMA (LOGOUT)")
    strl.session_state["autenticado"] = False
    strl.rerun()

strl.sidebar.markdown("---")
strl.sidebar.markdown("## 🧭 MENU CAEX")
opcoes_menu_disponiveis = ["🔍 PAINEL CENTRAL"]

if strl.session_state["usuario_login"] in ["2", "3"]:
    opcoes_menu_disponiveis.append("📝 NOVAS PASTAS")

opcoes_menu_disponiveis.append("📥 EXPORTAR DADOS")
tela_selecionada = strl.sidebar.radio("Selecione a operação desejada:", opcoes_menu_disponiveis)


# -----------------------------------------------------------------------
# PARTE 5: 🔍 PAINEL CENTRAL (Busca, Estatísticas de A-Z e Edição Restrita)
# -----------------------------------------------------------------------
if tela_selecionada == "🔍 PAINEL CENTRAL":
    col_esquerda, col_direita = strl.columns([0.6, 0.4], gap="large")

    with col_esquerda:
        strl.markdown("### 🔍 BUSCA RÁPIDA DE ALUNOS")
        termo_busca = strl.text_input("Digite o Nome do Aluno (ou parte dele):", placeholder="[ DIGITE O NOME AQUI... ]")
        
        if termo_busca:
            termo_upper = termo_busca.strip().upper()
            resultado_filtro = df_dados[df_dados["NOME DO ALUNO(A)"].str.contains(termo_upper, na=False)].copy()
            
            strl.markdown("### 📋 RESULTADO DA BUSCA")
            if not resultado_filtro.empty:
                strl.success(f"BUSCA CONCLUÍDA! FORAM ENCONTRADOS {len(resultado_filtro)} REGISTROS.")
                
                tabela_exibicao = resultado_filtro[["NOME DO ALUNO(A)", "UNIDADE ESCOLAR", "Nº DA PASTA", "PASTA ARQUIVO"]].copy()
                tabela_exibicao.columns = ["NOME DO ALUNO", "UNIDADE ESCOLAR", "Nº PASTA", "PASTA ARQUIVO"]
                tabela_ordenada = tabela_exibicao.sort_values(by="NOME DO ALUNO", ascending=True)
                
                strl.markdown("<small>💡 Dica: Selecione o aluno marcando a linha desejada na tabela abaixo para habilitar o botão de alteração.</small>", unsafe_allow_html=True)
                selecao = strl.dataframe(tabela_ordenada, width="stretch", hide_index=True, selection_mode="single-row", on_select="rerun")
                
                if selecao and "selection" in selecao and selecao["selection"].get("rows"):
                    idx_linha_selecionada = selecao["selection"]["rows"][0]
                    nome_aluno_selecionado = tabela_ordenada.iloc[idx_linha_selecionada]["NOME DO ALUNO"]
                    dados_originais_aluno = resultado_filtro[resultado_filtro["NOME DO ALUNO(A)"] == nome_aluno_selecionado]
                    
                    if not dados_originais_aluno.empty:
                        indice_real_excel = dados_originais_aluno.index[0]
                        aluno_row_data = dados_originais_aluno.iloc[0]
                        
                        @strl.dialog("✏️ ALTERAR DADOS DO ALUNO")
                        def popup_editar_aluno(index_linha, dados_aluno):
                            strl.markdown(f"Alterando o cadastro de: **{dados_aluno['NOME DO ALUNO(A)']}**")
                            ed_nome = strl.text_input("Nome do Aluno:", value=dados_aluno["NOME DO ALUNO(A)"])
                            ed_escola = strl.text_input("Unidade Escolar (Apenas Visualização):", value=dados_aluno["UNIDADE ESCOLAR"], disabled=True)
                            
                            ed_col1, ed_col2 = strl.columns(2)
                            with ed_col1:
                                ed_pasta = strl.text_input("Número da Pasta:", value=dados_aluno["Nº DA PASTA"])
                            with ed_col2:
                                ed_caixa = strl.text_input("Caixa Arquivo:", value=dados_aluno["PASTA ARQUIVO"])
                                
                            btn_gravar_edicao = strl.button("💾 Salvar Alterações")
                            if btn_gravar_edicao:
                                if ed_nome.strip() == "" or ed_pasta.strip() == "" or ed_caixa.strip() == "":
                                    strl.error("Nenhum campo pode ficar em branco.")
                                else:
                                    with strl.spinner("💾 ATUALIZANDO BANCO DE DADOS... POR FAVOR, AGUARDE..."):
                                        try:
                                            df_planilha = pd.read_excel(ARQUIVO_EXCEL, sheet_name="BD")
                                            df_planilha.at[index_linha, "NOME DO ALUNO(A)"] = ed_nome.strip().upper()
                                            df_planilha.at[index_linha, "Nº DA PASTA"] = ed_pasta.strip().upper()
                                            df_planilha.at[index_linha, "PASTA ARQUIVO"] = ed_caixa.strip().upper()
                                            df_planilha.at[index_linha, "ARQUIVO ORIGEM"] = "EDIÇÃO_MANUAL_WEB"
                                            
                                            with pd.ExcelWriter(ARQUIVO_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                                                df_planilha.to_excel(writer, sheet_name="BD", index=False)
                                                
                                            registrar_log_auditoria(strl.session_state["usuario_nome"], f"ALTEROU CADASTRO DO ALUNO PARA: {ed_nome.strip().upper()}")
                                            strl.cache_data.clear()
                                            strl.success("Cadastro atualizado com sucesso!")
                                            strl.rerun()
                                        except Exception as err:
                                            strl.error(f"Erro ao salvar edição: {err}")
                        
                        strl.markdown("---")
                        if strl.session_state["usuario_login"] == "1":
                            strl.info("💡 OPERADOR NÍVEL 1 (CONSULTA): Seu perfil não possui permissões para alterar registros do acervo.")
                        else:
                            if strl.button("✏️ ALTERAR DADOS DO ALUNO SELECIONADO", type="primary"):
                                popup_editar_aluno(indice_real_excel, aluno_row_data)
            else:
                strl.warning("NENHUM ALUNO ENCONTRADO COM ESSE NOME.")

    with col_direita:
        strl.markdown("### 📊 INDICADORES DO ARQUIVO")
        if not df_dados.empty:
            total_alunos = len(df_dados)
            total_escolas = df_dados["UNIDADE ESCOLAR"].nunique()
            
            card_col1, card_col2 = strl.columns(2)
            with card_col1:
                strl.metric(label="🏷️ TOTAL DE ALUNOS CADASTRADOS", value=f"{total_alunos:,}".replace(",", "."))
            with card_col2:
                strl.metric(label="🏫 ESCOLAS ATENDIDAS", value=total_escolas)
                
            strl.markdown("---")
            strl.markdown("##### 🏆 TOP 5 - MAIOR VOLUME DE ALUNOS")
            top_escolas = df_dados["UNIDADE ESCOLAR"].value_counts().head(5)
            for i, (escola, qtd) in enumerate(top_escolas.items(), 1):
                strl.write(f"**{i}. {escola}** ({qtd} alunos)")
        else:
            strl.error("DADOS INDISPONÍVEIS.")


# =======================================================================
# PARTE 6: 📝 NOVAS PASTAS (FORMULÁRIO DO ALUNO + POP-UP DINÂMICO DE ESCOLA)
# =======================================================================
elif tela_selecionada == "📝 NOVAS PASTAS":
    strl.markdown("## 📝 CADASTRO DE NOVAS PASTAS")
    lista_escolas = carregar_lista_escolas()
    opcoes_escola = ["--- SELECIONE ---", "➕ CADASTRAR NOVA ESCOLA"] + lista_escolas

    @strl.dialog("🏫 CADASTRO DE NOVA UNIDADE ESCOLAR")
    def popup_cadastrar_escola():
        strl.markdown("Esta escola será adicionada automaticamente à lista de escolas do acervo.")
        p_nome = strl.text_input("Nome da Escola:")
        p_endereco = strl.text_input("Endereço:")
        p_col1, p_col2 = strl.columns(2)
        with p_col1:
            p_ano = strl.text_input("Ano de Encerramento:", max_chars=4)
        with p_col2:
            p_contato = strl.text_input("Telefone / Contato", placeholder="(00) 0 0000-0000")
            
        btn_salvar_escola = strl.button("💾 Salvar Escola no Acervo")
        if btn_salvar_escola:
            if p_nome.strip() == "":
                strl.error("O nome da escola é obrigatório.")
            else:
                with strl.spinner("💾 GRAVANDO NOVA ESCOLA NO ACERVO... POR FAVOR, AGUARDE..."):
                    try:
                        df_escolas = pd.read_excel(ARQUIVO_EXCEL, sheet_name="ESCOLAS")
                        coluna_nome = df_escolas.columns[0]
                        escola_final = p_nome.upper().strip()
                        
                        # CORREÇÃO CRÍTICA DO BLOCO 6: Removido o termo 'school_final' para evitar travamento
                        existe = (df_escolas[coluna_nome].astype(str).str.upper().str.strip() == escola_final).any()

                        if not existe:
                            nova_linha = pd.DataFrame([{
                                coluna_nome: escola_final, 
                                "Ano de Encerramento": p_ano.upper().strip(), 
                                "Endereço": p_endereco.upper().strip(), 
                                "Contato": p_contato.upper().strip()
                            }])
                            df_escolas = pd.concat([df_escolas, nova_linha], ignore_index=True)
                            with pd.ExcelWriter(ARQUIVO_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                                df_escolas.to_excel(writer, sheet_name="ESCOLAS", index=False)
                            
                            strl.session_state["escola_selecionada_atual"] = escola_final
                            registrar_log_auditoria(strl.session_state["usuario_nome"], f"CADASTROU NOVA UNIDADE ESCOLAR: {escola_final}")
                            strl.cache_data.clear()
                            strl.success(f"Escola '{escola_final}' cadastrada com sucesso!")
                            strl.rerun()
                        else:
                            strl.warning("Esta escola já consta cadastrada no sistema!")
                    except Exception as erro:
                        strl.error(f"Erro ao salvar escola: {erro}")

    index_padrao = 0
    if "escola_selecionada_atual" in strl.session_state:
        if strl.session_state["escola_selecionada_atual"] in opcoes_escola:
            index_padrao = opcoes_escola.index(strl.session_state["escola_selecionada_atual"])

    escola_selecionada = strl.selectbox("1. Selecione a Unidade Escolar:", opcoes_escola, index=index_padrao)

    if escola_selecionada == "➕ CADASTRAR NOVA ESCOLA":
        strl.session_state["escola_selecionada_atual"] = "--- SELECIONE ---"
        popup_cadastrar_escola()
        strl.stop()

    strl.session_state["escola_selecionada_atual"] = escola_selecionada

    with strl.form("form_cadastro_aluno", clear_on_submit=True):
        nome_aluno = strl.text_input("2. Nome Completo do Aluno:", placeholder="DIGITE O NOME COMPLETO")
        col1, col2 = strl.columns(2)
        with col1:
            numero_pasta = strl.text_input("3. Número da Pasta")
        with col2:
            caixa_arquivo = strl.text_input("4. Caixa Arquivo")

        salvar = strl.form_submit_button("💾 SALVAR CADASTRO")

        if salvar:
            escola_ativa = strl.session_state.get("escola_selecionada_atual", "--- SELECIONE ---")
            
            if escola_ativa in ["--- SELECIONE ---", "➕ CADASTRAR NOVA ESCOLA"]:
                strl.error("Por favor, selecione uma Unidade Escolar válida na listagem superior.")
            elif nome_aluno.strip() == "" or numero_pasta.strip() == "" or caixa_arquivo.strip() == "":
                strl.error("Todos os campos do aluno são obrigatórios.")
            else:
                with strl.spinner("📝 PROCESSANDO BANCO DE DADOS E GRAVANDO ALUNO... POR FAVOR, AGUARDE..."):
                    try:
                        df_bd = pd.read_excel(ARQUIVO_EXCEL, sheet_name="BD")
                        nova_linha_aluno = pd.DataFrame([{
                            "UNIDADE ESCOLAR": escola_ativa.upper().strip(), 
                            "NOME DO ALUNO(A)": nome_aluno.upper().strip(), 
                            "Nº DA PASTA": numero_pasta.upper().strip(), 
                            "PASTA ARQUIVO": caixa_arquivo.upper().strip(), 
                            "ARQUIVO ORIGEM": "CADASTRO_MANUAL"
                        }])
                        df_bd = pd.concat([df_bd, nova_linha_aluno], ignore_index=True)
                        with pd.ExcelWriter(ARQUIVO_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                            df_bd.to_excel(writer, sheet_name="BD", index=False)

                        strl.session_state["escola_selecionada_atual"] = "--- SELECIONE ---"
                        registrar_log_auditoria(strl.session_state["usuario_nome"], f"CADASTROU O ALUNO: {nome_aluno.upper().strip()} NA PASTA: {numero_pasta.upper().strip()}")
                        strl.cache_data.clear()
                        strl.success(f"Cadastro realizado com sucesso!\n\nAluno: {nome_aluno.upper()}\nEscola: {escola_ativa.upper()}")
                        strl.rerun()
                    except Exception as erro:
                        strl.error(f"Erro ao gravar os dados do aluno:\n\n{erro}")




# =======================================================================
# PARTE 7: 📥 EXPORTAR DADOS (DOWNLOAD RESTRITO EM EXCEL DE A-Z)
# =======================================================================
elif tela_selecionada == "📥 EXPORTAR DADOS":
    strl.markdown("## 📥 EXPORTAR DADOS POR ESCOLA")
    strl.markdown("Selecione uma instituição abaixo para gerar e baixar a planilha contendo a listagem completa de alunos.")

    lista_escolas_exportar = carregar_lista_escolas()
    if lista_escolas_exportar:
        escola_alvo = strl.selectbox("Selecione a Escola que deseja exportar:", ["--- SELECIONE UMA ESCOLA ---"] + lista_escolas_exportar)
        
        if escola_alvo != "--- SELECIONE UMA ESCOLA ---":
            alunos_filtrados = df_dados[df_dados["UNIDADE ESCOLAR"] == escola_alvo].copy()
            relatorio_final = alunos_filtrados[["NOME DO ALUNO(A)", "UNIDADE ESCOLAR", "Nº DA PASTA", "PASTA ARQUIVO"]].copy()
            relatorio_final.columns = ["NOME DO ALUNO", "UNIDADE ESCOLAR", "Nº PASTA", "PASTA ARQUIVO"]
            relatorio_final = relatorio_final.sort_values(by="NOME DO ALUNO", ascending=True)
            
            total_filtrado = len(relatorio_final)
            strl.markdown(f"**Total de alunos localizados para esta instituição:** {total_filtrado} registros.")
            
            if total_filtrado > 0:
                strl.dataframe(relatorio_final, width="stretch", hide_index=True)
                try:
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        relatorio_final.to_excel(writer, sheet_name="ALUNOS", index=False)
                    dados_excel_binario = output.getvalue()
                    
                    nome_arquivo_baixado = f"ALUNOS_{escola_alvo.replace(' ', '_')}.xlsx"
                    strl.download_button(
                        label=f"📥 BAIXAR PLANILHA EXCEL ({total_filtrado} ALUNOS)",
                        data=dados_excel_binario,
                        file_name=nome_arquivo_baixado,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e_export:
                    strl.error(f"Erro ao gerar o arquivo de download: {e_export}")
            else:
                strl.warning("Não existem alunos cadastrados para esta escola no momento.")



