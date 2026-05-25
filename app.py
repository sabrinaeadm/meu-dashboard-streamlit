import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
# FUNÇÃO LEITURA E TRATAMENTO COM MAPEAMENTO INTELIGENTE
# =====================================================
@st.cache_data
def load_data():
    try:
        df_risco = pd.read_csv("Gestão de riscos e reclamações(respostas).csv", sep=";", encoding="utf-8")
        df_churn = pd.read_csv("Formulário de Solicitação de Cancelamento(Respostas).csv", sep=";", encoding="utf-8")
    except:
        df_risco = pd.read_excel("gestao.xlsx", engine="openpyxl")
        df_churn = pd.read_excel("churn.xlsx", engine="openpyxl")

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
    
    c_
