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
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Executivo")
st.markdown("Acompanhamento de Riscos e Churn para tomada de decisão estratégica.")

# =====================================================
# MENU LATERAL: PLANO B (UPLOAD MANUAL)
# =====================================================
st.sidebar.markdown("### 📂 Inserir Dados")
st.sidebar.markdown("Se o painel estiver em branco, carregue os ficheiros manualmente aqui:")
up_risco = st.sidebar.file_uploader("1. Gestão de Riscos (CSV ou Excel)", type=['csv', 'xlsx'])
up_churn = st.sidebar.file_uploader("2. Churn/Cancelamentos (CSV ou Excel)", type=['csv', 'xlsx'])

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
    
    # 1. Tenta carregar o ficheiro do Risco
    if file_risco is not None:
        if file_risco.name.endswith('.csv'):
            df_risco = pd.read_csv(file_risco, sep=";", encoding="utf-8")
        else:
            df_risco = pd.read_excel(file_risco)
    elif os.path.exists(caminho_risco):
        df_risco = pd.read_csv(caminho_risco, sep=";", encoding="utf-8")

    # 2. Tenta carregar o ficheiro de Churn
    if file_churn is not None:
        if file_churn.name.endswith('.csv'):
            df_churn = pd.read_csv(file_churn, sep=";", encoding="utf-8")
        else:
            df_churn = pd.read_excel(file_churn)
    elif os.path.exists(caminho_churn):
        df_churn = pd.read_csv(caminho_churn, sep=";", encoding="utf-8")

    # Se estiverem vazios, devolve já para mostrar o aviso no ecrã principal
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

    c_data_risco = next((c for c in df_risco.columns if 'data' in c.lower() and ('reclama' in c.lower() or '
