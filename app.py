import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Dashboard de Gestão", layout="wide")

st.title("📊 Dashboard Executivo")

# Carregamento dos dados (Substitua pelos nomes dos seus arquivos)
@st.cache_data
def load_data():
    risco_df = pd.read_csv("gestao_risco.csv")
    churn_df = pd.read_csv("churn.csv")
    return risco_df, churn_df

try:
    df_risco, df_churn = load_data()

    # Criação das Abas
    tab_risco, tab_churn = st.tabs(["⚠️ Gestão de Risco", "📉 Análise de Churn"])

    with tab_risco:
        st.header("Visão de Gestão de Risco")
        # Colunas solicitadas: Área, SLA, Temperatura, Cliente e Status
        colunas_risco = ["cliente", "area_reclamada", "sla", "temperatura", "status"]
        st.dataframe(df_risco[colunas_risco], use_container_width=True)
        
        # Exemplo de métrica rápida
        st.metric("Clientes em Risco Crítico", len(df_risco[df_risco['temperatura'] == 'Alta']))

    with tab_churn:
        st.header("Visão de Churn")
        # Colunas solicitadas: Empresa, Qtd Grupo, Cancelamentos, Revertidos, Churn/Franquia, Motivos, %
        st.subheader("Indicadores Gerais")
        
        # Exemplo de exibição de métricas calculadas
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Cancelamentos", df_churn["cancelamentos"].sum())
        c2.metric("Revertidos", df_churn["revertidos"].sum())
        
        st.divider()
        st.dataframe(df_churn, use_container_width=True)

except FileNotFoundError:
    st.error("Certifique-se de que os arquivos 'gestao_risco.csv' e 'churn.csv' estão na mesma pasta do código.")
