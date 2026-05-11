import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Dashboard de Gestão", layout="wide")

st.title("📊 Dashboard Executivo - Whirlpool")

# Função para carregar os dados tratando o formato de exportação do Excel/Google Sheets
@st.cache_data
def load_data():
    # Nomes dos arquivos
    file_risco = "gestao.xlsx"
    file_churn = "churn.xlsx"
    
    # Leitura dos arquivos
    risco_df = pd.read_csv(file_risco, sep=None, engine='python', encoding="latin1")
    churn_df = pd.read_csv(file_churn, sep=None, engine='python', encoding="latin1")
    
    return risco_df, churn_df

try:
    df_risco, df_churn = load_data()

    # Criação das abas
    tab_risco, tab_churn = st.tabs(["⚠️ Gestão de Risco", "📉 Análise de Churn"])

    # =========================
    # ABA GESTÃO DE RISCO
    # =========================
    with tab_risco:
        st.header("Visão de Gestão de Risco")
        
        mapping_risco = {
            "Empresa (Obrigatório)": "Cliente",
            "Área Primária Reclamada/Causadora do Risco": "Área Reclamada",
            "Urgência de Resolução (Em comparação com outros casos, qual a prioridade?)": "SLA/Urgência",
            "Grau de Risco Atual (Impacto Potencial: 5 = Perda Iminente)": "Temperatura",
            "Status Atual da Tratativa": "Status"
        }

        df_risco_view = df_risco[list(mapping_risco.keys())].rename(columns=mapping_risco)

        st.dataframe(df_risco_view, use_container_width=True)

    # =========================
    # ABA CHURN
    # =========================
    with tab_churn:
        st.header("Visão de Churn")
        
        c1, c2, c3 = st.columns(3)

        total_cancelados = df_churn["Quantidade Total de Cancelamentos Solicitados"].sum()
        total_revertidos = df_churn["Quant. Revertido"].sum()

        c1.metric("Total de Cancelamentos", f"{total_cancelados}")
        c2.metric("Total Revertidos", f"{total_revertidos}")

        if total_cancelados > 0:
            perc = (total_revertidos / total_cancelados) * 100
            c3.metric("% Reversão", f"{perc:.2f}%")

        st.divider()

        mapping_churn = {
            "Nome da Empresa": "Empresa",
            "Quantidade Total de Contratos do Grupo": "Qtd Grupo",
            "Quantidade Total de Cancelamentos Solicitados": "Cancelamentos",
            "Quant. Revertido": "Revertidos",
            "Franquia\n": "Churn por Franquia",
            "Motivo Principal do Cancelamento\n": "Motivos",
            "Status": "Status Final"
        }

        st.subheader("Detalhamento de Churn por Empresa")

        df_churn_view = df_churn[list(mapping_churn.keys())].rename(columns=mapping_churn)

        st.dataframe(df_churn_view, use_container_width=True)

except Exception as e:
    st.error("Erro ao carregar os dados. Verifique se os arquivos estão corretos.")
    st.info(
        "Garanta que os arquivos estejam na mesma pasta do app.py com os nomes:\n"
        "1. gestao.xlsx\n"
        "2. churn.xlsx"
    )

    st.divider()
    st.write("Detalhe técnico do erro:", e)
