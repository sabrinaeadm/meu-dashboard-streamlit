import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Dashboard de Gestão", layout="wide")

st.title("📊 Dashboard Executivo")

# Função para carregar os dados tratando erros de CSV brasileiro
@st.cache_data
def load_data():
    # O encoding='latin1' e sep=None fazem o pandas descobrir se é vírgula ou ponto e vírgula sozinho
    risco_df = pd.read_csv("gestao_risco.csv", sep=None, engine='python', encoding="latin1")
    churn_df = pd.read_csv("churn.csv", sep=None, engine='python', encoding="latin1")
    return risco_df, churn_df

try:
    df_risco, df_churn = load_data()

    # Criação das Abas
    tab_risco, tab_churn = st.tabs(["⚠️ Gestão de Risco", "📉 Análise de Churn"])

    with tab_risco:
        st.header("Visão de Gestão de Risco")
        # Colunas ajustadas para o que você pediu inicialmente
        colunas_risco = ["cliente", "area reclamada", "sla", "temperatura do cliente", "status"]
        
        # Filtra apenas as colunas que realmente existem no arquivo para não dar erro
        colunas_existentes = [c for c in colunas_risco if c in df_risco.columns]
        st.dataframe(df_risco[colunas_existentes], use_container_width=True)

    with tab_churn:
        st.header("Visão de Churn")
        
        # Métricas principais baseadas no seu print
        c1, c2, c3 = st.columns(3)
        
        if "Quantidade de cancelamentos" in df_churn.columns:
            cancelados = df_churn["Quantidade de cancelamentos"].sum()
            c1.metric("Total de Cancelamentos", f"{cancelados}")
            
        if "Quantidade de revertidos" in df_churn.columns:
            revertidos = df_churn["Quantidade de revertidos"].sum()
            c2.metric("Revertidos", f"{revertidos}")

        st.divider()
        
        # Mostra a tabela de Churn com os nomes exatos do seu print
        st.subheader("Detalhamento por Empresa")
        st.dataframe(df_churn, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar os dados. Verifique se os arquivos CSV estão corretos.")
    st.info(f"Detalhe do erro: {e}")
