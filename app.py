# =======================================================================
# PARTE 1: CONFIGURAÇÕES INICIAIS, MAPAS DE ARQUIVOS E BACKUP AUTOMÁTICO
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

# CORREÇÃO CRÍTICA LINUX: Ajustado estritamente para letras maiúsculas batendo com o GitHub (.CSV)
ARQUIVO_BD_CSV = "BD.csv"
ARQUIVO_ESCOLAS_CSV = "ESCOLAS.csv"
ARQUIVO_USER_CSV = "USER.CSV"
ARQUIVO_LOG_CSV = "LOG.csv"

# CONFIGURAÇÃO INTERNA E FIXA DA CONTA MASTER DO DIRETOR
USUARIO_MASTER = "ROBSON.TEIXEIRA@SEDUC.GO.GOV.BR"
SENHA_MASTER = "123"

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
        nome_backup = os.path.join(pasta_backup, f"BACKUP_BD_{data_atual}.csv")
        
        if not os.path.exists(nome_backup) and os.path.exists(ARQUIVO_BD_CSV):
            shutil.copy2(ARQUIVO_BD_CSV, nome_backup)
    except:
        pass

realizar_backup_automatico()



# =======================================================================
# PARTE 2: MOTORES DE AUDITORIA DE REDE E CARREGADORES DO BANCO DE DADOS
# =======================================================================

def registrar_log_auditoria(nome_funcionario, acao_realizada):
    try:
        nome_pc = socket.gethostname().upper()
        usuario_rede = getpass.getuser().upper()
        
        try:
            df_log = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python', on_bad_lines='skip')
        except:
            df_log = pd.DataFrame(columns=["DATA", "PC", "REDE", "USUÁRIO /NOME", "AÇÃO", "STATUS"])
            
        nova_linha_log = pd.DataFrame([{
            "DATA": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "PC": nome_pc,
            "REDE": usuario_rede,
            "USUÁRIO /NOME": str(nome_funcionario).upper().strip(),
            "AÇÃO": str(acao_realizada).upper().strip(),
            "STATUS": "ABERTO"
        }])
        
        df_log_atualizado = pd.concat([df_log, nova_linha_log], ignore_index=True)
        df_log_atualizado.to_csv(ARQUIVO_LOG_CSV, index=False, sep=",", encoding="utf-8-sig")
    except:
        pass

@strl.cache_data(ttl=600)
def carregar_dados_bd():
    try:
        # CORREÇÃO CRÍTICA: Ignora erros de linhas desalinhadas para não travar o app
        df = pd.read_csv(ARQUIVO_BD_CSV, sep=None, engine='python', on_bad_lines='skip')
        df = df.fillna("NÃO IDENTIFICADO")
        
        # Mapeia dinamicamente as colunas para evitar erros de acentuação
        colunas_disponiveis = list(df.columns)
        for col in colunas_disponiveis:
            df[col] = df[col].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        strl.error(f"ERRO CRÍTICO AO LER BANCO DE DADOS (BD.csv): {e}")
        return pd.DataFrame()

@strl.cache_data(ttl=600)
def carregar_lista_escolas():
    try:
        df = pd.read_csv(ARQUIVO_ESCOLAS_CSV, sep=None, engine='python', on_bad_lines='skip')
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

# Ativa o banco de dados principal de alta velocidade na memória cache baseado em CSV
df_dados = carregar_dados_bd()

# Desenha o cabeçalho identitário azul
strl.markdown(
    """
    <div style="background-color:#1e40af; padding:15px; border-radius:10px; margin-bottom:25px;">
        <h1 style="color:white; text-align:center; margin:0; font-family:sans-serif; font-size: 28px;">
            CONTROLE DE ALUNOS ESCOLAS EXTINTAS - CAEX (VERSÃO CSV)
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
            with strl.spinner("GRAVANDO NOVO USUÁRIO EM DISCO..."):
                try:
                    # 1. LER COM UTF-8-SIG PARA EXTERMINAR O CARACTERE OCULTO DO EXCEL
                    df_usuarios = pd.read_csv(ARQUIVO_USER_CSV, sep=";", engine='python', on_bad_lines='skip', encoding="utf-8-sig")
                    df_usuarios = df_usuarios.fillna("NÃO IDENTIFICADO")
                    df_usuarios.columns = [str(c).strip().upper() for c in df_usuarios.columns]
                    
                    colunas_user_reais = list(df_usuarios.columns)
                    col_user_real = next((c for c in colunas_user_reais if "USUÁRIO" in str(c) or "USUARIO" in str(c)), "USUÁRIO")
                    
                    # Verifica se o e-mail digitado já existe na base de dados
                    if (df_usuarios[col_user_real].astype(str).str.upper().str.strip() == c_user).any():
                        strl.warning("Este e-mail de usuário já está cadastrado no sistema!")
                    else:
                        fone_limpo = "".join([char for char in c_fone if char.isdigit()])
                        fone_formatado = c_fone.upper()
                        if len(fone_limpo) == 11:
                            fone_formatado = f"({fone_limpo[:2]}) {fone_limpo[2:7]}-{fone_limpo[7:]}"
                        elif len(fone_limpo) == 10:
                            fone_formatado = f"({fone_limpo[:2]}) {fone_limpo[2:6]}-{fone_limpo[6:]}"
                        
                        # 2. GRAVAÇÃO DIRETA E CIRÚRGICA EM MODO APPEND (TEXTO PURO EM DISCO)
                        # Abre o arquivo local no final e injeta a linha formatada com ponto e vírgula nativo
                        with open(ARQUIVO_USER_CSV, mode="a", encoding="utf-8-sig") as arquivo_txt:
                            # Adiciona uma quebra de linha de segurança e a linha de dados nova
                            arquivo_txt.write(f"\n{c_user};{c_pass};{c_nome};{fone_formatado};1")
                        
                        registrar_log_auditoria(c_nome, f"CRIOU CONTA PARA O EMAIL: {c_user}")
                        strl.success("✅ Usuário registrado com sucesso e eternizado em disco!")
                        strl.rerun()
                except Exception as erro_gravacao:
                    strl.error(f"Erro crítico ao registrar usuário no arquivo USER.csv: {erro_gravacao}")


# =======================================================================
# PARTE 4: FORMULÁRIOS REQUERIMENTO DE ELEVAÇÃO DE NÍVEL (CORRIGIDO)
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
                df_usuarios = pd.read_csv(ARQUIVO_USER_CSV, sep=None, engine='python')
                df_usuarios.columns = [str(c).strip().upper() for c in df_usuarios.columns]
                col_user_real = "USUÁRIO" if "USUÁRIO" in df_usuarios.columns else "USUARIO"
                
                validacao = (df_usuarios[col_user_real].astype(str).str.upper() == e_user) & (df_usuarios["SENHA"].astype(str) == e_pass)
                user_encontrado = df_usuarios[validacao]
                
                if not user_encontrado.empty:
                    nome_funcionario = str(user_encontrado.iloc[0]["NOME"]).upper()
                    nivel_alvo = e_nivel[:1]
                    
                    mensagem_log_formatada = f"PEDIDO_PENDENTE | NÍVEL SOLICITADO: {nivel_alvo} | JUSTIFICATIVA: {e_just.upper()}"
                    registrar_log_auditoria(nome_funcionario, mensagem_log_formatada)
                    
                    strl.success("✅ REQUERIMENTO PROTOCOLADO COM SUCESSO!")
                    strl.rerun()
                else:
                    strl.error("Credenciais inválidas. Verifique seu e-mail e senha atual.")
            except Exception as err_envio:
                strl.error(f"Erro ao processar requisição no banco de dados: {err_envio}")

# =======================================================================
# PARTE 5: INTERFACE GRÁFICA DE LOGIN, VALIDAÇÃO E MENUS DA BARRA LATERAL
# =======================================================================

if not strl.session_state["autenticado"]:
    strl.markdown("### 🔐 ACESSO RESTRITO - CONTROLE DE ACESSO")
    
    # Cria o formulário nativo que captura o clique da tecla ENTER automaticamente
    with strl.form("formulario_login_caex", clear_on_submit=False):
        col_input1, col_input2 = strl.columns(2)
        with col_input1:
            usuario_digitado = strl.text_input("E-MAIL DE USUÁRIO:", placeholder="EXEMPLO@EMAIL.COM")
        with col_input2:
            senha_digitada = strl.text_input("SENHA:", type="password", placeholder="DIGITE SUA SENHA RESTRITA")
            
        btn_entrar = strl.form_submit_button("🔓 ENTRAR NO SISTEMA", use_container_width=True)
        
    # Mantém os botões secundários fora do formulário para não dispararem no Enter por engano
    btn_l2, btn_l3 = strl.columns(2)
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
        elif u_clean == USUARIO_MASTER and s_clean == SENHA_MASTER:
            strl.session_state["autenticado"] = True
            strl.session_state["usuario_nome"] = "ROBSON TEIXEIRA"
            strl.session_state["usuario_nivel"] = "3 - ADMINISTRADOR MASTER (TOTAL)"
            strl.session_state["usuario_login"] = "3"
            registrar_log_auditoria("ROBSON TEIXEIRA", "REALIZOU LOGIN VIA CONTA MASTER INTERNA")
            strl.rerun()
        else:
            try:
                # Carrega a tabela de usuários a partir do arquivo USER.csv
                df_usuarios = pd.read_csv(ARQUIVO_USER_CSV, sep=None, engine='python', on_bad_lines='skip')
                df_usuarios = df_usuarios.fillna("NÃO IDENTIFICADO")
                
                # Normaliza todas as colunas para letras maiúsculas tirando espaços extras
                df_usuarios.columns = [str(c).strip().upper() for c in df_usuarios.columns]
                
                # Identifica as colunas dinamicamente para evitar o KeyError
                colunas_user_reais = list(df_usuarios.columns)
                col_user_real = next((c for c in colunas_user_reais if "USUÁRIO" in str(c) or "USUARIO" in str(c)), colunas_user_reais[0])
                col_nivel_real = next((c for c in colunas_user_reais if "NÍVEL" in str(c) or "NIVEL" in str(c)), colunas_user_reais[-1])
                col_nome_real = next((c for c in colunas_user_reais if "NOME" in str(c)), "NOME")
                col_senha_real = next((c for c in colunas_user_reais if "SENHA" in str(c)), "SENHA")
                
                filtro_user = (df_usuarios[col_user_real].astype(str).str.strip().str.upper() == u_clean) & \
                              (df_usuarios[col_senha_real].astype(str).str.strip() == s_clean)
                usuario_valido = df_usuarios[filtro_user]
                
                if not usuario_valido.empty:
                    # CORREÇÃO DEFINITIVA DE SINTAXE: Coleta o valor puro da primeira linha do vetor sem conflito de iloc
                    nome_real = str(usuario_valido[col_nome_real].values[0]).upper().strip()
                    nivel_acesso = str(usuario_valido[col_nivel_real].values[0]).strip()
                    
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

opcoes_menu_disponiveis = ["🏠 PAINEL INICIAL"]

if strl.session_state["usuario_login"] == "3":
    opcoes_menu_disponiveis.append("🛠️ C-PANEL")

if strl.session_state["usuario_login"] in ["1", "2"]:
    opcoes_menu_disponiveis.append("⚠️ ABRIR CHAMADO")

if strl.session_state["usuario_login"] in ["2", "3"]:
    opcoes_menu_disponiveis.append("📝 NOVAS PASTAS")

opcoes_menu_disponiveis.append("📥 EXPORTAR DADOS")

if "chamado_sucesso" in strl.session_state and strl.session_state["chamado_sucesso"] == True:
    strl.session_state["chave_menu"] = "🏠 PAINEL INICIAL"

if "chave_menu" not in strl.session_state:
    strl.session_state["chave_menu"] = "🏠 PAINEL INICIAL"

tela_selecionada = strl.sidebar.radio(
    "Selecione a operação desejada:", 
    opcoes_menu_disponiveis, 
    key="chave_menu"
)


# =======================================================================
# PARTE 6: PAINEL DE CONTROLE EXCLUSIVO MASTER - FLUXO 1 (🛠️ C-PANEL)
# =======================================================================

if tela_selecionada == "🛠️ C-PANEL":
    strl.markdown("## 🛠️ C-PANEL - CENTRAL DE CONTROLE DO ADMINISTRADOR")
    strl.markdown("Gerenciamento avançado de permissões de operadores, manutenção do sistema e atendimento de suporte.")
    
    if strl.session_state["usuario_login"] != "3":
        strl.error("⚠️ ACESSO NEGADO: Esta área é restrita à conta master da direção.")
        strl.stop()
        
    try:
        df_log_check = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python', on_bad_lines='skip')
        df_log_check.columns = [str(c).strip().upper() for c in df_log_check.columns]
        
        if "STATUS" not in df_log_check.columns:
            df_log_check["STATUS"] = "ABERTO"
            
        pedidos_pendentes = df_log_check[
            (df_log_check["AÇÃO"].str.contains("PEDIDO_PENDENTE", na=False)) &
            (df_log_check["STATUS"].astype(str).str.upper().str.strip() != "CONCLUÍDO")
        ].copy()
        
        if not pedidos_pendentes.empty:
            strl.markdown("#### 📋 FILA DE AVALIAÇÃO DE MUDANÇA DE NÍVEL")
            
            pedidos_pendentes["INDEX_REAL_EXCEL"] = pedidos_pendentes.index
            pedidos_unicos = pedidos_pendentes.drop_duplicates(subset=["USUÁRIO /NOME"], keep="last")
            
            for idx, linha_pedido in pedidos_unicos.iterrows():
                funcionario_pedinte = str(linha_pedido["USUÁRIO /NOME"]).upper().strip()
                detalhes_acao = str(linha_pedido["AÇÃO"])
                data_pedido = linha_pedido["DATA"]
                indice_original_excel = int(linha_pedido["INDEX_REAL_EXCEL"])
                
                partes_pedido = detalhes_acao.split("|")
                if len(partes_pedido) >= 3:
                    nivel_pedido = ""
                    justificativa_pedido = ""
                    
                    for item_ped in partes_pedido:
                        item_ped_up = item_ped.upper().strip()
                        if "NÍVEL SOLICITADO:" in item_ped_up:
                            nivel_pedido = item_ped_up.replace("NÍVEL SOLICITADO:", "").strip()
                        elif "JUSTIFICATIVA:" in item_ped_up:
                            justificativa_pedido = item_ped_up.replace("JUSTIFICATIVA:", "").strip()
                    
                    with strl.container(border=True):
                        strl.markdown(f"👤 **Funcionário:** {funcionario_pedinte} | 📅 **Solicitado em:** {data_pedido}")
                        strl.write(f"• **Nível Requerido:** NÍVEL {nivel_pedido}")
                        strl.write(f"• **Justificativa:** \"{justificativa_pedido}\"")
                        
                        col_btn1, col_btn2 = strl.columns([0.2, 0.8])
                        
                        if col_btn1.button(f"✅ Aprovar {funcionario_pedinte.split()}", key=f"aprov_cp_{idx}"):
                            with strl.spinner("Aplicando elevação de nível..."):
                                df_user_master = pd.read_csv(ARQUIVO_USER_CSV, sep=None, engine='python', on_bad_lines='skip')
                                df_user_master.columns = [str(c).strip().upper() for c in df_user_master.columns]
                                col_nivel_ref = "NÍVEL" if "NÍVEL" in df_user_master.columns else "NIVEL"
                                filtro_mudar = df_user_master["NOME"].astype(str).str.upper().str.strip() == funcionario_pedinte
                                
                                if filtro_mudar.any():
                                    df_user_master.loc[filtro_mudar, col_nivel_ref] = int(nivel_pedido)
                                    
                                    df_atualizar_log = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python', on_bad_lines='skip')
                                    df_atualizar_log.at[indice_original_excel, "STATUS"] = "CONCLUÍDO"
                                    
                                    df_user_master.to_csv(ARQUIVO_USER_CSV, index=False, sep=",", encoding="utf-8-sig")
                                    df_atualizar_log.to_csv(ARQUIVO_LOG_CSV, index=False, sep=",", encoding="utf-8-sig")
                                        
                                    registrar_log_auditoria("ROBSON TEIXEIRA", f"APROVOU VIA C-PANEL O FUNCIONÁRIO {funcionario_pedinte} PARA O NÍVEL {nivel_pedido}")
                                    strl.success(f"Solicitação concluída com sucesso!")
                                    strl.cache_data.clear()
                                    strl.rerun()
                                else:
                                    strl.error("Funcionário não localizado no arquivo USER.csv.")
                                    
                        if col_btn2.button(f"❌ Arquivar Pedido", key=f"recus_cp_{idx}"):
                            with strl.spinner("Arquivando solicitação..."):
                                df_atualizar_log = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python', on_bad_lines='skip')
                                df_atualizar_log.at[indice_original_excel, "STATUS"] = "CONCLUÍDO"
                                df_atualizar_log.to_csv(ARQUIVO_LOG_CSV, index=False, sep=",", encoding="utf-8-sig")
                                    
                                registrar_log_auditoria("ROBSON TEIXEIRA", f"ARQUIVOU VIA C-PANEL O PEDIDO DE {funcionario_pedinte}")
                                strl.cache_data.clear()
                                strl.rerun()
            strl.markdown("---")
    except Exception as e_cp_f1:
        strl.error(f"Erro na varredura do C-PANEL Fluxo 1: {e_cp_f1}")

# =======================================================================
# PARTE 7: CENTRAL DE ATENDIMENTO DE CHAMADOS DE SUPORTE (🛠️ C-PANEL)
# =======================================================================

    try:
        # Carrega o histórico técnico diretamente do arquivo LOG.csv
        df_log_check = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python')
        df_log_check.columns = [str(c).strip().upper() for c in df_log_check.columns]
        
        if "STATUS" not in df_log_check.columns:
            df_log_check["STATUS"] = "ABERTO"
        
        # Filtra os registros que contêm chamados de suporte técnicos pendentes
        chamados_abertos = df_log_check[
            (df_log_check["AÇÃO"].str.contains("CHAMADO_SUPORTE", na=False)) & 
            (df_log_check["STATUS"].astype(str).str.upper().str.strip() == "ABERTO")
        ].copy()
        
        strl.markdown("#### 🛠️ MURAL DE CHAMADOS TÉCNICOS E SITUAÇÕES ADVERSAS")
        if not chamados_abertos.empty:
            # CORREÇÃO CRÍTICA: Mapeia o índice numérico real da linha do arquivo CSV antes de filtrar duplicados
            chamados_abertos["INDEX_REAL_EXCEL"] = chamados_abertos.index
            chamados_unicos = chamados_abertos.drop_duplicates(subset=["DATA", "USUÁRIO /NOME"], keep="last")
            
            for idx_ch, linha_chamado in chamados_unicos.iterrows():
                operador_chamado = str(linha_chamado["USUÁRIO /NOME"]).upper().strip()
                texto_chamado = str(linha_chamado["AÇÃO"])
                data_chamado = linha_chamado["DATA"]
                indice_chamado_excel = int(linha_chamado["INDEX_REAL_EXCEL"])
                
                partes_ch = texto_chamado.split("|")
                if len(partes_ch) >= 5:
                    cat_ch, imp_ch, anexo_ch, detalhes_ch = "", "", "", ""
                    
                    for item in partes_ch:
                        item_up = item.upper().strip()
                        if "CATEGORIA:" in item_up:
                            cat_ch = item_up.replace("CATEGORIA:", "").strip()
                        elif "IMPACTO:" in item_up:
                            imp_ch = item_up.replace("IMPACTO:", "").strip()
                        elif "ANEXO:" in item_up:
                            anexo_ch = item.strip().split("ANEXO:")[-1].strip()
                        elif "DETALHES:" in item_up:
                            detalhes_ch = item_up.replace("DETALHES:", "").strip()
                    
                    with strl.container(border=True):
                        strl.error(f"🚨 **Chamado Técnico Ativo - {data_chamado}**")
                        strl.write(f"• **Operador Solicitante:** {operador_chamado}")
                        strl.write(f"• **Categoria Adversidade:** {cat_ch}")
                        strl.write(f"• **Nível de Impacto Relatado:** {imp_ch}")
                        strl.write(f"• **Relato da Situação:** \"{detalhes_ch}\"")
                        
                        if anexo_ch != "NENHUM ANEXO ENVIADO" and os.path.exists(anexo_ch):
                            with strl.expander("🖼️ CLIQUE AQUI PARA VER A CAPTURA DE TELA DO ERRO"):
                                strl.image(anexo_ch, caption=f"Evidência visual enviada por {operador_chamado}", use_container_width=True)
                        else:
                            strl.write("*• Evidência Visual:* Nenhum arquivo anexado a este ticket.")
                            
                        col_ch1, col_ch2 = strl.columns([0.2, 0.8])
                        
                        if col_ch1.button(f"🏁 Concluir Atendimento", key=f"Resolv_{idx_ch}"):
                            with strl.spinner("Dando baixa no chamado técnico..."):
                                df_planilha_log = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python')
                                
                                # Altera o status mirando cirurgicamente a linha original absoluta no CSV
                                df_planilha_log.at[indice_chamado_excel, "STATUS"] = "CONCLUÍDO"
                                
                                # Grava de volta no disco com codificação segura para Excel em português
                                df_planilha_log.to_csv(ARQUIVO_LOG_CSV, index=False, sep=",", encoding="utf-8-sig")
                                
                                registrar_log_auditoria("ROBSON TEIXEIRA", f"ENCERROU O ATENDIMENTO DO CHAMADO DE {operador_chamado} REGISTRADO EM {data_chamado}")
                                strl.toast("✅ Chamado arquivado com sucesso!", icon="🏁")
                                strl.cache_data.clear()
                                strl.rerun()
        else:
            strl.success("✅ Excelente! Nenhum chamado operacional pendente de suporte técnico.")
            
    except Exception as e_cp_global:
        strl.error(f"Erro na varredura analítica do C-PANEL Fluxo 2 (Mural de Chamados): {e_cp_global}")

# =======================================================================
# PARTE 8: 🏠 PAINEL INICIAL (Notificações Master, Busca e Estatísticas)
# =======================================================================

if tela_selecionada == "🏠 PAINEL INICIAL":
    if strl.session_state["usuario_login"] == "3":
        try:
            # Leitura direta do arquivo LOG.csv para garantir notificações em tempo real
            df_log_check = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python', on_bad_lines='skip')
            df_log_check.columns = [str(c).strip().upper() for c in df_log_check.columns]
            
            if "STATUS" not in df_log_check.columns:
                df_log_check["STATUS"] = "ABERTO"
            
            # Alerta Tipo 1: Pedidos de Promoção de Nível (Filtra apenas os pendentes de resolução)
            pedidos_pendentes = df_log_check[
                (df_log_check["AÇÃO"].str.contains("PEDIDO_PENDENTE", na=False)) &
                (df_log_check["STATUS"].astype(str).str.upper().str.strip() != "CONCLUÍDO")
            ]
            
            if not pedidos_pendentes.empty:
                pedidos_unicos = pedidos_pendentes.drop_duplicates(subset=["USUÁRIO /NOME"], keep="last")
                for idx, linha_pedido in pedidos_unicos.iterrows():
                    funcionario_pedinte = str(linha_pedido["USUÁRIO /NOME"]).upper().strip()
                    detalhes_acao = str(linha_pedido["AÇÃO"])
                    data_pedido = linha_pedido["DATA"]
                    
                    # Checagem dupla no banco USER.csv para evitar alertas fantasmas se já foi promovido
                    df_user_real = pd.read_csv(ARQUIVO_USER_CSV, sep=None, engine='python')
                    df_user_real.columns = [str(c).strip().upper() for c in df_user_real.columns]
                    filtro_liberado = df_user_real["NOME"].astype(str).str.upper().str.strip() == funcionario_pedinte
                    
                    partes_pedido = detalhes_acao.split("|")
                    nivel_pedido = "2"
                    for it_p in partes_pedido:
                        if "NÍVEL SOLICITADO:" in it_p.upper():
                            nivel_pedido = it_p.upper().replace("NÍVEL SOLICITADO:", "").strip()
                            
                    # Se o nível já consta como alterado na tabela, pula o card visual automaticamente
                    if filtro_liberado.any() and str(df_user_real.loc[filtro_liberado, "NÍVEL"].iloc[0]).strip() == str(nivel_pedido):
                        continue
                        
                    strl.warning(f"""
                        ⚠️ **MUDANÇA DE NÍVEL PENDENTE ({data_pedido})**  
                        O funcionário **{funcionario_pedinte}** solicitou promoção para o **NÍVEL {nivel_pedido}**.  
                        *Instruções: Para avaliar ou aprovar, acesse a aba '🛠️ C-PANEL' no menu lateral.*
                    """)
                        
            # Alerta Tipo 2: Chamados de Suporte Operacional (Filtra rigorosamente os que estão ABERTO)
            chamados_pendentes = df_log_check[
                (df_log_check["AÇÃO"].str.contains("CHAMADO_SUPORTE", na=False)) & 
                (df_log_check["STATUS"].astype(str).str.upper().str.strip() == "ABERTO")
            ]
                
            if not chamados_pendentes.empty:
                chamados_unicos = chamados_pendentes.drop_duplicates(subset=["DATA", "USUÁRIO /NOME"], keep="last")
                for idx_ch, linha_chamado in chamados_unicos.iterrows():
                    operador_pedinte = str(linha_chamado["USUÁRIO /NOME"]).upper().strip()
                    texto_acao = str(linha_chamado["AÇÃO"])
                    data_chamado = linha_chamado["DATA"]
                    partes_ch = texto_acao.split("|")
                    if len(partes_ch) >= 3:
                        cat_critica = ""
                        for it_c in partes_ch:
                            if "CATEGORIA:" in it_c.upper():
                                cat_critica = it_c.upper().replace("CATEGORIA:", "").strip()
                        strl.error(f"""
                            🚨 **NOVO CHAMADO DE SUPORTE OPERACIONAL DETECTADO ({data_chamado})**  
                            O operador **{operador_pedinte}** reportou uma situação adversa na categoria: **{cat_critica}**.  
                            *Instruções: Para ler o relatório do erro, abrir o anexo e encerrar o ticket, abra a aba '🛠️ C-PANEL'.*
                        """)
            
            # Desenha a linha divisória estrutural caso existam notificações pendentes ativas
            chamados_visiveis = df_log_check[(df_log_check["AÇÃO"].str.contains("CHAMADO_SUPORTE", na=False)) & (df_log_check["STATUS"] == "ABERTO")]
            if not pedidos_pendentes.empty or not chamados_visiveis.empty:
                strl.markdown("---")
        except:
            pass

    col_esquerda, col_direita = strl.columns([0.6, 0.4], gap="large")

    with col_esquerda:
        strl.markdown("### 🔍 BUSCA RÁPIDA DE ALUNOS")
        termo_busca = strl.text_input("Digite o Nome do Aluno (ou parte dele):", placeholder="[ DIGITE O NOME AQUI... ]")
        
        if termo_busca:
            termo_upper = termo_busca.strip().upper()
            
            # Mapeia dinamicamente os nomes reais das colunas no arquivo CSV de alunos
            colunas_reais_bd = list(df_dados.columns)
            col_aluno_real = next((c for c in colunas_reais_bd if "ALUNO" in str(c).upper()), colunas_reais_bd[0])
            col_escola_real = next((c for c in colunas_reais_bd if "ESCOLA" in str(c).upper() or "UNIDADE" in str(c).upper()), colunas_reais_bd[1])
            col_pasta_real = next((c for c in colunas_reais_bd if "PASTA" in str(c).upper() and "ARQUIVO" not in str(c).upper()), colunas_reais_bd[2])
            col_caixa_real = next((c for c in colunas_reais_bd if "ARQUIVO" in str(c).upper() or "CAIXA" in str(c).upper()), colunas_reais_bd[3])

            resultado_filtro = df_dados[df_dados[col_aluno_real].str.contains(termo_upper, na=False)].copy()
            
            strl.markdown("### 📋 RESULTADO DA BUSCA")
            if not resultado_filtro.empty:
                strl.success(f"BUSCA CONCLUÍDA! FORAM ENCONTRADOS {len(resultado_filtro)} REGISTROS.")
                
                tabela_exibicao = resultado_filtro[[col_aluno_real, col_escola_real, col_pasta_real, col_caixa_real]].copy()
                tabela_exibicao.columns = ["NOME DO ALUNO", "UNIDADE ESCOLAR", "Nº PASTA", "PASTA ARQUIVO"]
                tabela_ordenada = tabela_exibicao.sort_values(by="NOME DO ALUNO", ascending=True)
                
                strl.markdown("<small>💡 Dica: Selecione o aluno marcando a linha desejada na tabela abaixo para habilitar o botão de alteração.</small>", unsafe_allow_html=True)
                selecao = strl.dataframe(tabela_ordenada, width="stretch", hide_index=True, selection_mode="single-row", on_select="rerun")

# =======================================================================
# PARTE 9: 🏠 PAINEL INICIAL ( BUSCA, EDIÇÃO E EXCLUSÃO NO PAINEL INICIAL)
# =======================================================================
                if selecao and "selection" in selecao and selecao["selection"].get("rows"):
                    idx_linha_selecionada = selecao["selection"]["rows"][0] # CORREÇÃO: Pega o primeiro valor inteiro puro da seleção
                    
                    # Extrai os dados isolados da linha clicada na tabela ordenada
                    linha_tabela = tabela_ordenada.iloc[idx_linha_selecionada]
                    nome_aluno_selecionado = str(linha_tabela["NOME DO ALUNO"]).strip().upper()
                    escola_aluno_selecionado = str(linha_tabela["UNIDADE ESCOLAR"]).strip().upper()
                    pasta_aluno_selecionada = str(linha_tabela["Nº PASTA"]).strip().upper()
                    caixa_aluno_selecionada = str(linha_tabela["PASTA ARQUIVO"]).strip().upper()
                    
                    # Identifica dinamicamente os nomes das colunas reais no CSV
                    colunas_reais_bd = list(resultado_filtro.columns)
                    col_aluno_real = next((c for c in colunas_reais_bd if "ALUNO" in str(c).upper()), colunas_reais_bd[0])
                    col_escola_real = next((c for c in colunas_reais_bd if "ESCOLA" in str(c).upper() or "UNIDADE" in str(c).upper()), colunas_reais_bd[1])
                    col_pasta_real = next((c for c in colunas_reais_bd if "PASTA" in str(c).upper() and "ARQUIVO" not in str(c).upper()), colunas_reais_bd[2])
                    col_caixa_real = next((c for c in colunas_reais_bd if "ARQUIVO" in str(c).upper() or "CAIXA" in str(c).upper()), colunas_reais_bd[3])

                    # Localiza o registro exato cruzando TODAS as informações da linha clicada (seguro contra duplicados)
                    dados_originais_aluno = resultado_filtro[
                        (resultado_filtro[col_aluno_real].astype(str) == nome_aluno_selecionado) & 
                        (resultado_filtro[col_escola_real].astype(str) == escola_aluno_selecionado) &
                        (resultado_filtro[col_pasta_real].astype(str) == pasta_aluno_selecionada) &
                        (resultado_filtro[col_caixa_real].astype(str) == caixa_aluno_selecionada)
                    ]
                    
                    if not dados_originais_aluno.empty:
                        # CORREÇÃO CRÍTICA: Captura o número inteiro puro escalar do índice da linha do CSV
                        indice_real_excel = int(dados_originais_aluno.index[0])
                        aluno_row_data = dados_originais_aluno.iloc[0].to_dict() # CORREÇÃO CRÍTICA: Converte a linha pura para dicionário
                        
                        @strl.dialog("✏️ ALTERAR DADOS DO ALUNO")
                        def popup_editar_aluno(index_linha, dados_aluno):
                            strl.markdown(f"Alterando o cadastro de: **{dados_aluno[col_aluno_real]}**")
                            ed_nome = strl.text_input("Nome do Aluno:", value=dados_aluno[col_aluno_real])
                            ed_escola = strl.text_input("Unidade Escolar (Apenas Visualização):", value=dados_aluno[col_escola_real], disabled=True)
                            
                            ed_col1, ed_col2 = strl.columns(2)
                            with ed_col1:
                                ed_pasta = strl.text_input("Número da Pasta:", value=dados_aluno[col_pasta_real])
                            with ed_col2:
                                ed_caixa = strl.text_input("Caixa Arquivo:", value=dados_aluno[col_caixa_real])
                                
                            btn_gravar_edicao = strl.button("💾 Salvar Alterações")
                            if btn_gravar_edicao:
                                if ed_nome.strip() == "" or ed_pasta.strip() == "" or ed_caixa.strip() == "":
                                    strl.error("Nenhum campo pode ficar em branco.")
                                else:
                                    with strl.spinner("💾 ATUALIZANDO BANCO DE DADOS..."):
                                        try:
                                            # Carrega o arquivo físico do disco
                                            df_planilha = pd.read_csv(ARQUIVO_BD_CSV, sep=None, engine='python', on_bad_lines='skip')
                                            
                                            # Gravação cirúrgica usando o número inteiro puro do índice mapeado
                                            df_planilha.at[index_linha, col_aluno_real] = ed_nome.strip().upper()
                                            df_planilha.at[index_linha, col_pasta_real] = ed_pasta.strip().upper()
                                            df_planilha.at[index_linha, col_caixa_real] = ed_caixa.strip().upper()
                                            
                                            col_origem_real = next((c for c in df_planilha.columns if "ORIGEM" in str(c).upper()), None)
                                            if col_origem_real:
                                                df_planilha.at[index_linha, col_origem_real] = "EDIÇÃO_MANUAL_WEB"
                                            
                                            # Força a reescrita física e o fechamento do arquivo no HD virtual
                                            df_planilha.to_csv(ARQUIVO_BD_CSV, index=False, sep=",", encoding="utf-8-sig")
                                            
                                            registrar_log_auditoria(strl.session_state["usuario_nome"], f"ALTEROU CADASTRO DO ALUNO PARA: {ed_nome.strip().upper()}")
                                            strl.cache_data.clear() # Limpa a memória cache do Streamlit
                                            strl.success("Cadastro atualizado com sucesso!")
                                            strl.rerun()
                                        except Exception as err:
                                            strl.error(f"Erro ao salvar edição no arquivo BD.csv: {err}")

                        @strl.dialog("🗑️ CONFIRMAR EXCLUSÃO DE REGISTRO")
                        def popup_excluir_aluno(index_linha, dados_aluno):
                            strl.error(f"⚠️ ATENÇÃO: Você está prestes a deletar permanentemente o registro abaixo!")
                            strl.markdown(f"**Aluno:** {dados_aluno[col_aluno_real]}")
                            strl.markdown(f"**Escola:** {dados_aluno[col_escola_real]} | **Pasta:** {dados_aluno[col_pasta_real]}")
                            strl.write("Esta ação não poderá ser desfeita na interface web.")
                            
                            strl.markdown("---")
                            if strl.button("🚨 SIM, EXCLUIR DEFINITIVAMENTE", type="primary", use_container_width=True):
                                with strl.spinner("🗑️ REMOVENDO REGISTRO DO ACERVO..."):
                                    try:
                                        df_planilha = pd.read_csv(ARQUIVO_BD_CSV, sep=None, engine='python', on_bad_lines='skip')
                                        
                                        nome_deletado = dados_aluno[col_aluno_real]
                                        pasta_deletada = dados_aluno[col_pasta_real]
                                        escola_deletada = dados_aluno[col_escola_real]
                                        
                                        # Remove a linha fisicamente usando o índice inteiro puro
                                        df_planilha = df_planilha.drop(index=index_linha)
                                        df_planilha.to_csv(ARQUIVO_BD_CSV, index=False, sep=",", encoding="utf-8-sig")
                                        
                                        registrar_log_auditoria(
                                            strl.session_state["usuario_nome"], 
                                            f"EXCLUIU REGISTRO - ALUNO: {nome_deletado} | PASTA: {pasta_deletada} | ESCOLA: {escola_deletada}"
                                        )
                                        
                                        strl.cache_data.clear()
                                        strl.success("Registro removido com sucesso!")
                                        strl.rerun()
                                    except Exception as err:
                                        strl.error(f"Erro ao processar exclusão no arquivo BD.csv: {err}")
                        
                        strl.markdown("---")
                        if strl.session_state["usuario_login"] == "1":
                            strl.info("💡 OPERADOR NÍVEL 1 (CONSULTA): Seu perfil não possui permissões para alterar ou excluir registros do acervo.")
                        else:
                            btn_col1, btn_col2 = strl.columns(2)
                            with btn_col1:
                                if strl.button("✏️ ALTERAR DADOS DO ALUNO SELECIONADO", type="primary", use_container_width=True):
                                    popup_editar_aluno(indice_real_excel, aluno_row_data)
                            with btn_col2:
                                if strl.button("🗑️ EXCLUIR ALUNO SELECIONADO", type="secondary", use_container_width=True):
                                    popup_excluir_aluno(indice_real_excel, aluno_row_data)
            else:
                strl.warning("NENHUM ALUNO ENCONTRADO COM ESSE NOME.")

# =======================================================================
# PARTE 10: 📝 NOVAS PASTAS (FORMULÁRIO DO ALUNO + POP-UP DINÂMICO DE ESCOLA)
# =======================================================================

if tela_selecionada == "📝 NOVAS PASTAS":
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
                with strl.spinner("💾 GRAVANDO NOVA ESCOLA NO ACERVO..."):
                    try:
                        df_escolas = pd.read_csv(ARQUIVO_ESCOLAS_CSV, sep=None, engine='python', on_bad_lines='skip')
                        coluna_nome = df_escolas.columns
                        escola_final = p_nome.upper().strip()
                        
                        existe = (df_escolas[coluna_nome].astype(str).str.upper().str.strip() == escola_final).any()

                        if not existe:
                            nova_linha = pd.DataFrame([{
                                coluna_nome: escola_final, 
                                "Ano de Encerramento": p_ano.upper().strip(), 
                                "Endereço": p_endereco.upper().strip(), 
                                "Contato": p_contato.upper().strip()
                            }])
                            df_escolas = pd.concat([df_escolas, nova_linha], ignore_index=True)
                            df_escolas.to_csv(ARQUIVO_ESCOLAS_CSV, index=False, sep=",", encoding="utf-8-sig")
                            
                            strl.session_state["escola_selecionada_atual"] = escola_final
                            registrar_log_auditoria(strl.session_state["usuario_nome"], f"CADASTROU NOVA UNIDADE ESCOLAR: {escola_final}")
                            
                            strl.cache_data.clear()
                            strl.success(f"Escola '{escola_final}' cadastrada com sucesso!")
                            strl.rerun()
                        else:
                            strl.warning("Esta escola já consta cadastrada no sistema!")
                    except Exception as erro:
                        strl.error(f"Erro ao salvar escola no arquivo ESCOLAS.csv: {erro}")

    index_padrao = 0
    if "escola_selecionada_atual" in strl.session_state:
        if strl.session_state["escola_selecionada_atual"] in opcoes_escola:
            index_padrao = opcoes_escola.index(strl.session_state["escola_selecionada_atual"])

    escola_selecionada = strl.selectbox("1. Selecione a Unidade Escolar:", opcoes_escola, index=index_padrao, key="selectbox_cadastro_novas_pastas")

    if escola_selecionada == "➕ CADASTRAR NOVA ESCOLA":
        strl.session_state["escola_selecionada_atual"] = "--- SELECIONE ---"
        popup_cadastrar_escola()
        strl.stop()

    strl.sidebar.markdown("---") 
    strl.session_state["escola_selecionada_atual"] = escola_selecionada

    with strl.form("form_cadastro_aluno", clear_on_submit=True):
        nome_aluno = strl.text_input("2. Nome Completo do Aluno:", placeholder="DIGITE O NOME COMPLETO", key="campo_nome_aluno")
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
                with strl.spinner("⚡ GRAVANDO E PADRONIZANDO BANCO DE DADOS..."):
                    try:
                        df_bd_original = pd.read_csv(ARQUIVO_BD_CSV, sep=None, engine='python', on_bad_lines='skip')
                        
                        colunas_reais = list(df_bd_original.columns)
                        col_escola = next((c for c in colunas_reais if "ESCOLA" in str(c).upper() or "UNIDADE" in str(c).upper()), "UNIDADE ESCOLAR")
                        col_aluno = next((c for c in colunas_reais if "ALUNO" in str(c).upper()), "NOME DO ALUNO(A)")
                        col_pasta = next((c for c in colunas_reais if "PASTA" in str(c).upper() and "ARQUIVO" not in str(c).upper()), "Nº DA PASTA")
                        col_caixa = next((c for c in colunas_reais if "ARQUIVO" in str(c).upper() or "CAIXA" in str(c).upper()), "PASTA ARQUIVO")
                        col_origem = next((c for c in colunas_reais if "ORIGEM" in str(c).upper()), "ARQUIVO ORIGEM")

                        escola_f = escola_ativa.upper().strip()
                        nome_f = nome_aluno.upper().strip()
                        pasta_f = numero_pasta.upper().strip()
                        caixa_f = caixa_arquivo.upper().strip()
                        
                        # -----------------------------------------------------------------------
                        # TRAVA DE SEGURANÇA INTELIGENTE: Bloqueia apenas o mesmo ALUNO na mesma ESCOLA com a mesma PASTA
                        # -----------------------------------------------------------------------
                        filtro_duplicado_real = (df_bd_original[col_aluno].astype(str).str.upper().str.strip() == nome_f) & \
                                                (df_bd_original[col_escola].astype(str).str.upper().str.strip() == escola_f) & \
                                                (df_bd_original[col_pasta].astype(str).str.upper().str.strip() == pasta_f)
                        
                        if filtro_duplicado_real.any():
                            strl.error(f"❌ IMPOSSÍVEL SALVAR: O registro do aluno **{nome_f}** com a Pasta Nº **{pasta_f}** já consta cadastrado nesta instituição!")
                        else:
                            # Executa o salvamento legítimo liberando os números repetidos de outros alunos
                            nova_linha_aluno = pd.DataFrame([{
                                col_escola: escola_f, 
                                col_aluno: nome_f, 
                                col_pasta: pasta_f, 
                                col_caixa: caixa_f, 
                                col_origem: "CADASTRO_MANUAL"
                            }])
                            
                            df_consolidado = pd.concat([df_bd_original, nova_linha_aluno], ignore_index=True)
                            df_consolidado.to_csv(ARQUIVO_BD_CSV, index=False, sep=",", encoding="utf-8-sig")
                            
                            strl.cache_data.clear()
                            registrar_log_auditoria(strl.session_state["usuario_nome"], f"CADASTROU O ALUNO: {nome_f} NA PASTA: {pasta_f}")
                            
                            strl.session_state["escola_selecionada_atual"] = escola_ativa 
                            strl.success(f"✅ Cadastro realizado com sucesso e gravado em disco!\n\nAluno: {nome_f}\nEscola: {escola_f}")
                            strl.rerun()
                    except Exception as erro:
                        strl.error(f"Erro ao sincronizar gravação no arquivo BD.csv: {erro}")

    strl.components.v1.html(
        """
        <script>
            window.parent.document.querySelectorAll('input[placeholder="DIGITE O NOME COMPLETO"]').forEach(function(el) {
                setTimeout(function() { el.focus(); }, 100);
            });
        </script>
        """,
        height=0,
        width=0
    )

# =======================================================================
# PARTE 11: 📥 EXPORTAR DADOS (DOWNLOAD RESTRITO EM EXCEL DE A-Z)
# =======================================================================

if tela_selecionada == "📥 EXPORTAR DADOS":
    strl.markdown("## 📥 CENTRAL DE EXPORTAÇÃO DE DADOS")
    strl.markdown("Escolha abaixo se deseja baixar o acervo completo do sistema ou filtrar os registros de uma instituição específica.")

    import io

    # -----------------------------------------------------------------------
    # FLUXO 1: EXPORTAÇÃO COMPLETA DO BANCO DE DADOS GLOBAL (GERAL)
    # -----------------------------------------------------------------------
    with strl.container(border=True):
        strl.markdown("##### 🌎 EXPORTAÇÃO GLOBAL DO ACERVO")
        if not df_dados.empty:
            total_geral_linhas = len(df_dados)
            strl.write(f"Clique no botão abaixo para gerar uma planilha unificada contendo todos os **{total_geral_linhas:,}** registros salvos no sistema CAEX.".replace(",", "."))
            
            try:
                # Mapeamento dinâmico e inteligente para encontrar as colunas mesmo se mudarem de nome no CSV
                colunas_disponiveis = list(df_dados.columns)
                
                col_aluno = next((c for c in colunas_disponiveis if "ALUNO" in str(c).upper()), colunas_disponiveis[0])
                col_escola = next((c for c in colunas_disponiveis if "ESCOLA" in str(c).upper() or "UNIDADE" in str(c).upper()), colunas_disponiveis[1])
                col_pasta = next((c for c in colunas_disponiveis if "PASTA" in str(c).upper() and "ARQUIVO" not in str(c).upper()), colunas_disponiveis[2])
                col_caixa = next((c for c in colunas_disponiveis if "ARQUIVO" in str(c).upper() or "CAIXA" in str(c).upper()), colunas_disponiveis[3])

                # Extrai os dados usando as colunas identificadas dinamicamente
                df_geral_ordenado = df_dados[[col_aluno, col_escola, col_pasta, col_caixa]].copy()
                df_geral_ordenado.columns = ["NOME DO ALUNO", "UNIDADE ESCOLAR", "Nº PASTA", "PASTA ARQUIVO"]
                df_geral_ordenado = df_geral_ordenado.sort_values(by="NOME DO ALUNO", ascending=True)
                
                # Prepara o download em formato Excel na memória RAM
                output_geral = io.BytesIO()
                with pd.ExcelWriter(output_geral, engine='openpyxl') as writer_geral:
                    df_geral_ordenado.to_excel(writer_geral, sheet_name="ACERVO_TOTAL", index=False)
                dados_excel_geral = output_geral.getvalue()
                
                # Botão destacado para exportação global
                strl.download_button(
                    label=f"📥 EXPORTAR TODO O BANCO DE DADOS ({total_geral_linhas:,} REGISTROS)".replace(",", "."),
                    data=dados_excel_geral,
                    file_name="CAEX_ACERVO_TOTAL_COMPLETO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            except Exception as e_export_geral:
                strl.error(f"Erro ao preparar download do banco de dados geral: {e_export_geral}")
        else:
            strl.warning("O banco de dados de alunos (BD.csv) está vazio ou não pôde ser lido.")

    strl.markdown("<br>", unsafe_allow_html=True) # Espaçador visual estrutural

    # -----------------------------------------------------------------------
    # FLUXO 2: EXPORTAÇÃO FILTRADA POR UNIDADE ESCOLAR INDIVIDUAL
    # -----------------------------------------------------------------------
    with strl.container(border=True):
        strl.markdown("##### 🏫 EXPORTAÇÃO INDIVIDUAL POR ESCOLA")
        lista_escolas_exportar = carregar_lista_escolas()
        
        if lista_escolas_exportar:
            escola_alvo = strl.selectbox("Selecione a Escola que deseja exportar:", ["--- SELECIONE UMA ESCOLA ---"] + lista_escolas_exportar)
            
            if escola_alvo != "--- SELECIONE UMA ESCOLA ---":
                try:
                    colunas_disponiveis = list(df_dados.columns)
                    col_aluno = next((c for c in colunas_disponiveis if "ALUNO" in str(c).upper()), colunas_disponiveis[0])
                    col_escola = next((c for c in colunas_disponiveis if "ESCOLA" in str(c).upper() or "UNIDADE" in str(c).upper()), colunas_disponiveis[1])
                    col_pasta = next((c for c in colunas_disponiveis if "PASTA" in str(c).upper() and "ARQUIVO" not in str(c).upper()), colunas_disponiveis[2])
                    col_caixa = next((c for c in colunas_disponiveis if "ARQUIVO" in str(c).upper() or "CAIXA" in str(c).upper()), colunas_disponiveis[3])

                    alunos_filtrados = df_dados[df_dados[col_escola] == escola_alvo].copy()
                    relatorio_final = alunos_filtrados[[col_aluno, col_escola, col_pasta, col_caixa]].copy()
                    relatorio_final.columns = ["NOME DO ALUNO", "UNIDADE ESCOLAR", "Nº PASTA", "PASTA ARQUIVO"]
                    relatorio_final = relatorio_final.sort_values(by="NOME DO ALUNO", ascending=True)
                    
                    total_filtrado = len(relatorio_final)
                    strl.markdown(f"**Total de alunos localizados para esta instituição:** {total_filtrado} registros.")
                    
                    if total_filtrado > 0:
                        strl.dataframe(relatorio_final, width="stretch", hide_index=True)
                        
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
                    else:
                        strl.warning("Não existem alunos cadastrados para esta escola no momento.")
                except Exception as e_export:
                    strl.error(f"Erro ao gerar o arquivo de download por escola: {e_export}")

# =======================================================================
# PARTE 12: 🛠️ SUPORTE - ABRIR CHAMADO (EXCLUSIVO NÍVEL 1 E 2)
# =======================================================================

if tela_selecionada == "⚠️ ABRIR CHAMADO":
    strl.markdown("## ⚠️ CENTRAL DE SUPORTE - ABRIR CHAMADO")
    strl.markdown("Utilize este canal direto para reportar erros de sistema, inconsistências no banco de dados ou solicitar apoio técnico à administração master.")
    
    with strl.form("formulario_suporte_caex", clear_on_submit=True):
        strl.markdown("##### 📝 QUESTIONÁRIO DE IDENTIFICAÇÃO DO PROBLEMA")
        strl.text_input("Operador Solicitante (Identificação Automática):", value=strl.session_state["usuario_nome"], disabled=True)
        
        categoria_problema = strl.selectbox(
            "1. Qual é o tipo de situação adversa que você está enfrentando?",
            [
                "--- SELECIONE UMA OPÇÃO ---",
                "ERRO NA BUSCA (O aluno existe na folha física, mas não aparece na busca)",
                "ERRO AO SALVAR DADOS (O sistema trava ou mostra erro vermelho ao cadastrar nova pasta)",
                "INCONSISTÊNCIA NA PLANILHA (Nomes trocados, números de pastas errados ou duplicados)",
                "LENTIDÃO CRÍTICA (A tabela demora muito para carregar ou atualizar)",
                "OUTRO PROBLEMA TÉCNICO"
            ]
        )
        
        impacto_trabalho = strl.radio(
            "2. Qual o nível de impacto deste problema na sua rotina atual?",
            ["Baixo (Consigo trabalhar em outras pastas por enquanto)", "Médio (Está atrasando minhas metas do dia)", "Alto (Não consigo realizar nenhuma operação no sistema)"],
            horizontal=True
        )
        
        descricao_detalhada = strl.text_area(
            "3. Descreva detalhadamente como o problema acontece:",
            placeholder="Exemplo: Ao pesquisar o aluno 'MARIA DA SILVA', o sistema retornou o erro X na linha Y...",
            height=180
        )
        
        strl.markdown("##### 📸 ANEXAR EVIDÊNCIAS VISUAIS")
        strl.markdown("<small>💡 Dica: Tire um print da sua tela mostrando o erro e anexe abaixo. Limite máximo padrão do servidor: **200 MB** por arquivo.</small>", unsafe_allow_html=True)
        
        imagem_anexada = strl.file_uploader(
            "Selecione uma imagem de captura de tela (Formatos aceitos: PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False
        )
        
        submeter_chamado = strl.form_submit_button("🚀 ENVIAR CHAMADO PARA O MASTER")
        
        if submeter_chamado:
            if categoria_problema == "--- SELECIONE UMA OPÇÃO ---" or not descricao_detalhada.strip():
                strl.error("❌ ERRO: Você deve selecionar uma categoria válida e descrever o problema antes de enviar.")
            else:
                strl.session_state["chamado_sucesso"] = False
                
                with strl.spinner("Registrando seu chamado técnico no acervo..."):
                    try:
                        nome_arquivo_salvo = "NENHUM ANEXO ENVIADO"
                        if imagem_anexada is not None:
                            pasta_anexos = "ANEXOS_SUPORTE"
                            if not os.path.exists(pasta_anexos):
                                os.makedirs(pasta_anexos)
                            
                            timestamp_anexo = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
                            nome_arquivo_salvo = os.path.join(pasta_anexos, f"ERRO_{timestamp_anexo}_{imagem_anexada.name}")
                            
                            with open(nome_arquivo_salvo, "wb") as f_anexo:
                                f_anexo.write(imagem_anexada.getbuffer())
                        
                        mensagem_chamado_log = f"CHAMADO_SUPORTE | CATEGORIA: {categoria_problema} | IMPACTO: {impacto_trabalho.upper()} | ANEXO: {nome_arquivo_salvo} | DETALHES: {descricao_detalhada.upper().strip()}"
                        
                        df_log_atual = pd.read_csv(ARQUIVO_LOG_CSV, sep=None, engine='python')
                        
                        nome_pc = socket.gethostname().upper()
                        usuario_rede = getpass.getuser().upper()
                        
                        nova_linha_chamado = pd.DataFrame([{
                            "DATA": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "PC": nome_pc,
                            "REDE": usuario_rede,
                            "USUÁRIO /NOME": str(strl.session_state["usuario_nome"]).upper().strip(),
                            "AÇÃO": mensagem_chamado_log.upper().strip(),
                            "STATUS": "ABERTO"
                        }])
                        
                        df_log_novo = pd.concat([df_log_atual, nova_linha_chamado], ignore_index=True)
                        df_log_novo.to_csv(ARQUIVO_LOG_CSV, index=False, sep=",", encoding="utf-8-sig")
                        
                        strl.session_state["chamado_sucesso"] = True
                        strl.rerun()
                        
                    except Exception as e_chamado:
                        strl.error(f"Erro crítico ao processar o envio do chamado técnico no arquivo LOG.csv: {e_chamado}")

if "chamado_sucesso" in strl.session_state and strl.session_state["chamado_sucesso"] == True:
    strl.toast("✅ Chamado registrado com sucesso!", icon="📥")
    strl.session_state["chamado_sucesso"] = False
