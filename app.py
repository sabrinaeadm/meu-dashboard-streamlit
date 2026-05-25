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
# FUNÇÃO LEITURA E TRATAMENTO
# =====================================================
@st.cache_data
def load_data():
    try:
        df_risco = pd.read_csv("Gestão de riscos e reclamações(respostas).csv", sep=";", encoding="utf-8")
        df_churn = pd.read_csv("Formulário de Solicitação de Cancelamento(Respostas).csv", sep=";", encoding="utf-8")
    except:
        df_risco = pd.read_excel("gestao.xlsx", engine="openpyxl")
        df_churn = pd.read_excel("churn.xlsx", engine="openpyxl")

    # Limpeza de colunas (Remove quebras de linha e espaços)
    df_risco.columns = df_risco.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)
    df_churn.columns = df_churn.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)

    # TRATAMENTOS - RISCO
    if 'Data da Reclamação/Evento Original (Início do Risco)' in df_risco.columns:
        df_risco['Data Base'] = pd.to_datetime(df_risco['Data da Reclamação/Evento Original (Início do Risco)'], format='%d/%m/%Y', errors='coerce')
        df_risco['Ano'] = df_risco['Data Base'].dt.year.fillna(0).astype(int).astype(str).replace('0', 'N/A')
        df_risco['Mês'] = df_risco['Data Base'].dt.month.fillna(0).astype(int).astype(str).replace('0', 'N/A')
    
    # Extrair número do Grau de Risco (Ex: "2 - Médio" -> 2.0)
    col_risco = 'Grau de Risco Atual (Impacto Potencial: 5 = Perda Iminente)'
    if col_risco in df_risco.columns:
        df_risco['Grau Numérico'] = df_risco[col_risco].astype(str).str.extract(r'(\d+)').astype(float)
    
    # TRATAMENTOS - CHURN
    if 'Data da Solicitação' in df_churn.columns:
        df_churn['Data Base'] = pd.to_datetime(df_churn['Data da Solicitação'], format='%d/%m/%Y', errors='coerce')
        df_churn['Ano'] = df_churn['Data Base'].dt.year.fillna(0).astype(int).astype(str).replace('0', 'N/A')
        df_churn['Mês'] = df_churn['Data Base'].dt.month.fillna(0).astype(int).astype(str).replace('0', 'N/A')

    if 'Franquia' not in df_churn.columns and 'Franquia\n' in df_churn.columns:
        df_churn.rename(columns={'Franquia\n': 'Franquia'}, inplace=True)

    return df_risco, df_churn

# =====================================================
# INÍCIO DA APLICAÇÃO
# =====================================================
try:
    df_risco, df_churn = load_data()

    # =====================================================
    # ABAS (Nome da Aba 2 Atualizado conforme solicitado)
    # =====================================================
    tab1, tab2 = st.tabs([
        "⚠️ Gestão de Risco", 
        "📉 Solicitações Entrantes Churn/Cancelamentos"
    ])

    # =====================================================
    # ABA 1: GESTÃO DE RISCO
    # =====================================================
    with tab1:
        st.subheader("Painel de Gestão de Risco e Reclamações")

        # 1. FILTROS (Limpos por padrão)
        st.markdown("##### 🔎 Filtros de Risco")
        rf1, rf2, rf3 = st.columns(3)
        
        with rf1:
            # Puxando a informação diretamente da coluna S ("Status")
            status_risco_opcoes = sorted(df_risco['Status'].dropna().unique())
            filtro_status_risco = st.multiselect("Status da Tratativa (Coluna S)", status_risco_opcoes)
        with rf2:
            ano_risco_opcoes = sorted(df_risco['Ano'].unique())
            filtro_ano_risco = st.multiselect("Ano do Evento", ano_risco_opcoes)
        with rf3:
            mes_risco_opcoes = sorted(df_risco['Mês'].unique())
            filtro_mes_risco = st.multiselect("Mês do Evento", mes_risco_opcoes)

        # Aplicar Filtros Risco (Se não selecionar nada, mostra tudo)
        risco_filtrado = df_risco.copy()
        if filtro_status_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Status'].isin(filtro_status_risco)]
        if filtro_ano_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Ano'].isin(filtro_ano_risco)]
        if filtro_mes_risco:
            risco_filtrado = risco_filtrado[risco_filtrado['Mês'].isin(filtro_mes_risco)]

        st.divider()

        # 2. KPIs NO TOPO
        col_aging = 'Dias em aberto'
        col_area = 'Área Primária Reclamada/Causadora do Risco'

        total_casos = len(risco_filtrado)
        aging_medio = risco_filtrado[col_aging].mean() if col_aging in risco_filtrado.columns else 0
        risco_medio = risco_filtrado['Grau Numérico'].mean() if 'Grau Numérico' in risco_filtrado.columns else 0
        
        try:
            area_critica = risco_filtrado[col_area].mode()[0] if not risco_filtrado.empty else "N/A"
        except:
            area_critica = "N/A"

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total de Casos", f"{total_casos}")
        kpi2.metric("Aging Médio (Dias)", f"{aging_medio:.1f}" if pd.notnull(aging_medio) else "0")
        kpi3.metric("Risco Médio", f"{risco_medio:.1f}" if pd.notnull(risco_medio) else "0")
        kpi4.metric("Área Crítica (Moda)", str(area_critica))

        st.divider()

        # 3. TERMÔMETRO E GRÁFICO DE BARRAS
        g1, g2 = st.columns([1, 2])

        with g1:
            st.markdown("##### 🌡️ Termômetro de Risco (Médio)")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risco_medio if pd.notnull(risco_medio) else 0,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Nível de Risco (1 a 5)", 'font': {'size': 16}},
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
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with g2:
            st.markdown("##### 📊 Riscos por Área")
            if col_area in risco_filtrado.columns:
                df_area = risco_filtrado[col_area].value_counts().reset_index()
                df_area.columns = ['Área', 'Quantidade']
                fig_bar = px.bar(df_area, x='Área', y='Quantidade', text_auto=True, color='Quantidade', color_continuous_scale='Reds')
                fig_bar.update_layout(height=300, xaxis_title="", yaxis_title="Casos", showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_bar, use_container_width=True)

        # 4. TABELA DE DETALHES
        st.markdown("##### 📋 Detalhamento dos Casos")
        colunas_tabela_risco = {
            'Empresa (Obrigatório)': 'Empresa',
            'Dias em aberto': 'Dias Parados (Aging)',
            'Área Primária Reclamada/Causadora do Risco': 'Área Responsável',
            'Grau de Risco Atual (Impacto Potencial: 5 = Perda Iminente)': 'Impacto (Risco Original)',
            'Status': 'Status (Coluna S)'
        }
        
        cols_existentes = [c for c in colunas_tabela_risco.keys() if c in risco_filtrado.columns]
        df_risco_view = risco_filtrado[cols_existentes].rename(columns=colunas_tabela_risco)
        st.dataframe(df_risco_view, use_container_width=True, hide_index=True)


    # =====================================================
    # ABA 2: SOLICITAÇÕES ENTRANTES CHURN/CANCELAMENTOS
    # =====================================================
    with tab2:
        st.subheader("Análise de Churn e Cancelamentos")

        # 1. FILTROS (Limpos por padrão)
        st.markdown("##### 🔎 Filtros de Churn")
        cf1, cf2, cf3, cf4 = st.columns(4)

        with cf1:
            if 'Franquia' in df_churn.columns:
                franquias = sorted(df_churn["Franquia"].dropna().astype(str).unique())
                filtro_franquia = st.multiselect("Franquia", franquias)
            else:
                filtro_franquia = []

        with cf2:
            ano_churn_opcoes = sorted(df_churn['Ano'].unique())
            filtro_ano_churn = st.multiselect("Ano", ano_churn_opcoes)

        with cf3:
            mes_churn_opcoes = sorted(df_churn['Mês'].unique())
            filtro_mes_churn = st.multiselect("Mês", mes_churn_opcoes)

        with cf4:
            if 'Status' in df_churn.columns:
                status_churn = sorted(df_churn["Status"].dropna().astype(str).unique())
                filtro_status_churn = st.multiselect("Status", status_churn)
            else:
                filtro_status_churn = []

        # Aplicação dos filtros (Se não selecionar nada, mostra tudo)
        churn_filtrado = df_churn.copy()
        if 'Franquia' in churn_filtrado.columns and filtro_franquia:
            churn_filtrado = churn_filtrado[churn_filtrado["Franquia"].astype(str).isin(filtro_franquia)]
        if filtro_ano_churn:
            churn_filtrado = churn_filtrado[churn_filtrado["Ano"].isin(filtro_ano_churn)]
        if filtro_mes_churn:
            churn_filtrado = churn_filtrado[churn_filtrado["Mês"].isin(filtro_mes_churn)]
        if 'Status' in churn_filtrado.columns and filtro_status_churn:
            churn_filtrado = churn_filtrado[churn_filtrado["Status"].astype(str).isin(filtro_status_churn)]

        st.divider()

        # 2. GRÁFICOS
        cg1, cg2 = st.columns(2)

        with cg1:
            st.markdown("##### 📌 Cancelamentos por Franquia")
            if 'Franquia' in churn_filtrado.columns:
                df_franq = churn_filtrado['Franquia'].value_counts().reset_index()
                df_franq.columns = ['Franquia', 'Cancelamentos']
                fig_franq = px.bar(df_franq.head(10), x='Cancelamentos', y='Franquia', orientation='h', text_auto=True, color='Cancelamentos', color_continuous_scale='Blues')
                fig_franq.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=350, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_franq, use_container_width=True)

        with cg2:
            st.markdown("##### 📌 Motivo Principal do Cancelamento")
            col_motivo = "Motivo Principal do Cancelamento"
            if col_motivo in churn_filtrado.columns:
                df_motivo = churn_filtrado[col_motivo].value_counts().reset_index()
                df_motivo.columns = ['Motivo', 'Quantidade']
                fig_motivo = px.pie(df_motivo.head(7), values='Quantidade', names='Motivo', hole=0.4)
                fig_motivo.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_motivo, use_container_width=True)

        st.divider()

        # 3. TABELA DE EMPRESAS ATUALIZADA
        st.markdown("##### 🏢 Empresas com Solicitação (Detalhamento)")
        
        colunas_tabela_churn = {
            'Nome do Grupo': 'Nome do Grupo / Empresa',
            'CNPJ da Empresa': 'CNPJ',
            'Franquia': 'Franquia',
            'Motivo Principal do Cancelamento': 'Motivo Principal',
            'Quantidade Total de Cancelamentos Solicitados': 'Qtd. Cancelamentos',
            'Quant. Revertido': 'Quantidade de Revertidos',
            'Status': 'Status'
        }
        
        cols_existentes_churn = [c for c in colunas_tabela_churn.keys() if c in churn_filtrado.columns]
        df_churn_view = churn_filtrado[cols_existentes_churn].rename(columns=colunas_tabela_churn)
        st.dataframe(df_churn_view, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Erro ao executar a aplicação. Certifique-se de que as planilhas/CSVs estão na mesma pasta do código.")
    st.exception(e)
