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
    
    # Captura exata da coluna S ('Status')
    if 'Status' in df_risco.columns:
        df_risco.rename(columns={'Status': 'Status_Standard'}, inplace=True)
    else:
        c_status_risco = next((c for c in df_risco.columns if 'status' in c.lower()), None)
        if c_status_risco: df_risco.rename(columns={c_status_risco: 'Status_Standard'}, inplace=True)

    # Tratamento de Datas - Risco
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
    
    # Localização inteligente do Nome do Grupo
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

    # Tratamento de Datas - Churn
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
    df_risco, df_churn = load_data()

    # ABAS ATUALIZADAS
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
            
        with rf4:
            area_risco_opcoes = sorted(df_risco['Area_Standard'].dropna().astype(str).unique()) if 'Area_Standard' in df_risco.columns else []
            filtro_area_risco = st.multiselect("Área Responsável", area_risco_opcoes)

        # Filtros Inteligentes (Vazios por padrão = Mostra Tudo)
        risco_filtrado = df_risco.copy()
        if filtro_status_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Status_Standard'].isin(filtro_status_risco)]
        if filtro_ano_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Ano'].isin(filtro_ano_risco)]
        if filtro_mes_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Mês'].isin(filtro_mes_risco)]
        if filtro_area_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Area_Standard'].astype(str).isin(filtro_area_risco)]

        st.divider()

        # KPIs NO TOPO
        total_casos = len(risco_filtrado)
        aging_medio = risco_filtrado['Aging_Standard'].mean() if 'Aging_Standard' in risco_filtrado.columns else 0
        risco_medio = risco_filtrado['Grau Numérico'].mean() if 'Grau Numérico' in risco_filtrado.columns else 0
        try:
            area_critica = risco_filtrado['Area_Standard'].mode()[0] if not risco_filtrado.empty else "N/A"
        except:
            area_critica = "N/A"

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total de Casos", f"{total_casos}")
        kpi2.metric("Aging Médio (Dias)", f"{aging_medio:.1f}" if pd.notnull(aging_medio) else "0")
        kpi3.metric("Risco Médio", f"{risco_medio:.1f}" if pd.notnull(risco_medio) else "0")
        kpi4.metric("Área Crítica (Moda)", str(area_critica))

        st.divider()

        # VISUAIS
        g1, g2 = st.columns([1, 2])
        with g1:
            st.markdown("##### 🌡️ Termômetro de Risco (Médio)")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risco_medio if pd.notnull(risco_medio) else 0,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 5], 'tickwidth': 1},
                    'bar': {'color': "darkred"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightgreen"},
                        {'range': [2, 3.5], 'color': "gold"},
                        {'range': [3.5, 5], 'color': "salmon"}
                    ]
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with g2:
            st.markdown("##### 📊 Riscos por Área")
            if 'Area_Standard' in risco_filtrado.columns:
                df_area = risco_filtrado['Area_Standard'].value_counts().reset_index()
                df_area.columns = ['Área', 'Quantidade']
                fig_bar = px.bar(df_area, x='Área', y='Quantidade', text_auto=True, color='Quantidade', color_continuous_scale='Reds')
                fig_bar.update_layout(height=280, xaxis_title="", yaxis_title="Casos", showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig_bar, use_container_width=True)

        # TABELA DE DETALHES
        st.markdown("##### 📋 Detalhamento dos Casos")
        colunas_tabela_risco = {
            'Empresa_Standard': 'Empresa',
            'Aging_Standard': 'Dias Parados (Aging)',
            'Area_Standard': 'Área Responsável',
            'Grau_Standard': 'Impacto (Risco Original)',
            'Status_Standard': 'Status (Coluna S)'
        }
        cols_existentes = [c for c in colunas_tabela_risco.keys() if c in risco_filtrado.columns]
        df_risco_view = risco_filtrado[cols_existentes].rename(columns=colunas_tabela_risco)
        st.dataframe(df_risco_view, use_container_width=True, hide_index=True)


    # =====================================================
    # ABA 2: SOLICITAÇÕES ENTRANTES CHURN/CANCELAMENTOS
    # =====================================================
    with tab2:
        st.subheader("Análise de Churn e Cancelamentos")

        st.markdown("##### 🔎 Filtros de Churn")
        cf1, cf2, cf3, cf4 = st.columns(4)

        with cf1:
            franquias = sorted(df_churn["Franquia_Standard"].dropna().astype(str).unique()) if 'Franquia_Standard' in df_churn.columns else []
            filtro_franquia = st.multiselect("Franquia", franquias)

        with cf2:
            ano_churn_opcoes = sorted(df_churn['Ano'].unique()) if 'Ano' in df_churn.columns else []
            filtro_ano_churn = st.multiselect("Ano", ano_churn_opcoes)

        with cf3:
            mes_churn_opcoes = sorted(df_churn['Mês'].unique()) if 'Mês' in df_churn.columns else []
            filtro_mes_churn = st.multiselect("Mês", mes_churn_opcoes)

        with cf4:
            status_churn = sorted(df_churn["Status_Standard"].dropna().astype(str).unique()) if 'Status_Standard' in df_churn.columns else []
            filtro_status_churn = st.multiselect("Status", status_churn)

        # Filtros Inteligentes Churn
        churn_filtrado = df_churn.copy()
        if 'Franquia_Standard'
