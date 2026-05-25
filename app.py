import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Dashboard Executivo - Whirlpool",
    layout="wide",
    initial_sidebar_state="collapsed" # <--- Deixa a barra escondida por padrão!
)

st.title("📊 Dashboard Executivo")
st.markdown("Acompanhamento de Riscos e Churn para tomada de decisão estratégica.")

# =====================================================
# MENU LATERAL: PLANO B (UPLOAD MANUAL ELEGANTI)
# =====================================================
# Cria uma "sanfona" (expander) fechada por padrão
with st.sidebar.expander("⚙️ Inserir Dados Manualmente", expanded=False):
    st.markdown("<small>Use apenas se o painel não carregar automaticamente.</small>", unsafe_allow_html=True)
    up_risco = st.file_uploader("1. Gestão de Riscos", type=['csv', 'xlsx'])
    up_churn = st.file_uploader("2. Churn/Cancelamentos", type=['csv', 'xlsx'])

# =====================================================
# FUNÇÃO LEITURA E TRATAMENTO COM MAPEAMENTO INTELIGENTE
# =====================================================
@st.cache_data
def load_data(file_risco, file_churn):
    df_risco = pd.DataFrame()
    df_churn = pd.DataFrame()
    
    # Nomes padrão esperados no GitHub
    caminho_risco = "Gestão de riscos e reclamações(respostas).csv"
    caminho_churn = "Formulário de Solicitação de Cancelamento(Respostas).csv"
    
    # 1. Tenta carregar o arquivo do Risco
    if file_risco is not None:
        if file_risco.name.endswith('.csv'):
            df_risco = pd.read_csv(file_risco, sep=";", encoding="utf-8")
        else:
            df_risco = pd.read_excel(file_risco)
    elif os.path.exists(caminho_risco):
        df_risco = pd.read_csv(caminho_risco, sep=";", encoding="utf-8")

    # 2. Tenta carregar o arquivo de Churn
    if file_churn is not None:
        if file_churn.name.endswith('.csv'):
            df_churn = pd.read_csv(file_churn, sep=";", encoding="utf-8")
        else:
            df_churn = pd.read_excel(file_churn)
    elif os.path.exists(caminho_churn):
        df_churn = pd.read_csv(caminho_churn, sep=";", encoding="utf-8")

    if df_risco.empty or df_churn.empty:
        return df_risco, df_churn

    # Limpeza inicial de quebras de linha e espaços nas colunas
    df_risco.columns = df_risco.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)
    df_churn.columns = df_churn.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)

    # -------------------------------------------------
    # BLINDAGEM AUTOMÁTICA DE COLUNAS - GESTÃO DE RISCO
    # -------------------------------------------------
    c_empresa_risco = next((c for c in df_risco.columns if 'empresa' in c.lower() or 'cliente' in c.lower()), None)
    if c_empresa_risco: df_risco.rename(columns={c_empresa_risco: 'Empresa_Standard'}, inplace=True)
    
    c_aging_risco = next((c for c in df_risco.columns if 'dias' in c.lower() and ('aberto' in c.lower() or 'parados' in c.lower()) or 'aging' in c.lower()), None)
    if c_aging_risco: df_risco.rename(columns={c_aging_risco: 'Aging_Standard'}, inplace=True)
    
    c_area_risco = next((c for c in df_risco.columns if 'área' in c.lower() or 'area' in c.lower()), None)
    if c_area_risco: df_risco.rename(columns={c_area_risco: 'Area_Standard'}, inplace=True)
    
    c_grau_risco = next((c for c in df_risco.columns if 'grau' in c.lower() or 'risco' in c.lower() and 'atual' in c.lower()), None)
    if c_grau_risco: df_risco.rename(columns={c_grau_risco: 'Grau_Standard'}, inplace=True)
    
    if 'Status' in df_risco.columns:
        df_risco.rename(columns={'Status': 'Status_Standard'}, inplace=True)
    else:
        c_status_risco = next((c for c in df_risco.columns if 'status' in c.lower()), None)
        if c_status_risco: df_risco.rename(columns={c_status_risco: 'Status_Standard'}, inplace=True)

    c_data_risco = next((c for c in df_risco.columns if 'data' in c.lower() and ('reclama' in c.lower() or 'risco' in c.lower() or 'original' in c.lower())), None)
    if c_data_risco:
        df_risco['Data Base'] = pd.to_datetime(df_risco[c_data_risco], format='%d/%m/%Y', errors='coerce')
        df_risco['Ano'] = df_risco['Data Base'].dt.year.fillna(0).astype(int).astype(str).replace('0', 'N/A')
        df_risco['Mês'] = df_risco['Data Base'].dt.month.fillna(0).astype(int).astype(str).replace('0', 'N/A')
    
    if 'Grau_Standard' in df_risco.columns:
        df_risco['Grau Numérico'] = df_risco['Grau_Standard'].astype(str).str.extract(r'(\d+)').astype(float)

    # -------------------------------------------------
    # BLINDAGEM AUTOMÁTICA DE COLUNAS - CHURN
    # -------------------------------------------------
    c_franquia_churn = next((c for c in df_churn.columns if 'franquia' in c.lower()), None)
    if c_franquia_churn: df_churn.rename(columns={c_franquia_churn: 'Franquia_Standard'}, inplace=True)
    
    c_motivo_churn = next((c for c in df_churn.columns if 'motivo' in c.lower() and 'principal' in c.lower()), None)
    if c_motivo_churn: df_churn.rename(columns={c_motivo_churn: 'Motivo_Standard'}, inplace=True)
    
    c_grupo_churn = next((c for c in df_churn.columns if 'nome' in c.lower() and 'grupo' in c.lower()), None)
    if not c_grupo_churn:
        c_grupo_churn = next((c for c in df_churn.columns if 'grupo' in c.lower() and 'quantidade' not in c.lower()), None)
    if not c_grupo_churn:
        c_grupo_churn = next((c for c in df_churn.columns if 'empresa' in c.lower() and 'cnpj' not in c.lower()), None)
    if c_grupo_churn: df_churn.rename(columns={c_grupo_churn: 'Grupo_Standard'}, inplace=True)
    
    c_cnpj_churn = next((c for c in df_churn.columns if 'cnpj' in c.lower()), None)
    if c_cnpj_churn: df_churn.rename(columns={c_cnpj_churn: 'CNPJ_Standard'}, inplace=True)
    
    c_qtd_canc = next((c for c in df_churn.columns if 'quantidade' in c.lower() and 'cancelamento' in c.lower()), None)
    if c_qtd_canc: df_churn.rename(columns={c_qtd_canc: 'Qtd_Cancelamentos_Standard'}, inplace=True)
    
    c_qtd_rev = next((c for c in df_churn.columns if 'revertido' in c.lower() or 'rev' in c.lower()), None)
    if c_qtd_rev: df_churn.rename(columns={c_qtd_rev: 'Qtd_Revertidos_Standard'}, inplace=True)
    
    if 'Status' in df_churn.columns:
        df_churn.rename(columns={'Status': 'Status_Standard'}, inplace=True)
    else:
        c_status_churn = next((c for c in df_churn.columns if 'status' in c.lower()), None)
        if c_status_churn: df_churn.rename(columns={c_status_churn: 'Status_Standard'}, inplace=True)

    c_data_churn = next((c for c in df_churn.columns if 'data' in c.lower() and 'solicita' in c.lower()), None)
    if c_data_churn:
        df_churn['Data Base'] = pd.to_datetime(df_churn[c_data_churn], format='%d/%m/%Y', errors='coerce')
        df_churn['Ano'] = df_churn['Data Base'].dt.year.fillna(0).astype(int).astype(str).replace('0', 'N/A')
        df_churn['Mês'] = df_churn['Data Base'].dt.month.fillna(0).astype(int).astype(str).replace('0', 'N/A')

    return df_risco, df_churn

# =====================================================
# EXECUÇÃO DO APP
# =====================================================
try:
    df_risco, df_churn = load_data(up_risco, up_churn)

    if df_risco.empty or df_churn.empty:
        st.warning("⚠️ Os arquivos de dados originais não foram encontrados.")
        st.info("👉 **Abra o menu lateral (clicando na setinha > no canto superior esquerdo)** e arraste os seus arquivos de Excel/CSV para visualizar o dashboard!")
        st.stop()

    tab1, tab2 = st.tabs([
        "⚠️ Gestão de Risco", 
        "📉 Solicitações Entrantes Churn/Cancelamentos"
    ])

    # =====================================================
    # ABA 1: GESTÃO DE RISCO
    # =====================================================
    with tab1:
        st.subheader("Painel de Gestão de Risco e Reclamações")

        st.markdown("##### 🔎 Filtros de Risco")
        rf1, rf2, rf3, rf4 = st.columns(4)
        
        with rf1:
            status_risco_opcoes = sorted(df_risco['Status_Standard'].dropna().unique()) if 'Status_Standard' in df_risco.columns else []
            filtro_status_risco = st.multiselect("Status da Tratativa (Coluna S)", status_risco_opcoes)
        
        with rf2:
            ano_risco_opcoes = sorted(df_risco['Ano'].unique()) if 'Ano' in df_risco.columns else []
            filtro_ano_risco = st.multiselect("Ano do Evento", ano_risco_opcoes)
        
        with rf3:
            mes_risco_opcoes = sorted(df_risco['Mês'].unique()) if 'Mês' in df_risco.columns else []
            filtro_mes_risco = st.multiselect("Mês do Evento", mes_risco_opcoes)
