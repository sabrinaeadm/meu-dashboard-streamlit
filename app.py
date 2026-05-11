import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Dashboard Executivo",
    layout="wide"
)

st.title("📊 Dashboard Executivo - Culligan")


# =========================
# CARREGAMENTO DOS DADOS
# =========================
@st.cache_data
def load_data():

    file_risco = "gestao.xlsx"
    file_churn = "churn.xlsx"

    # LEITURA DOS EXCELS
    df_risco = pd.read_excel(file_risco, engine="openpyxl")
    df_churn = pd.read_excel(file_churn, engine="openpyxl")

    return df_risco, df_churn


try:

    df_risco, df_churn = load_data()

    # ABAS
    tab1, tab2 = st.tabs(
        ["⚠️ Gestão de Risco", "📉 Churn"]
    )

    # ==================================================
    # ABA RISCO
    # ==================================================
    with tab1:

        st.subheader("Gestão de Risco")

        mapping_risco = {
            "Empresa (Obrigatório)": "Cliente",
            "Área Primária Reclamada/Causadora do Risco": "Área",
            "Urgência de Resolução (Em comparação com outros casos, qual a prioridade?)": "Urgência",
            "Grau de Risco Atual (Impacto Potencial: 5 = Perda Iminente)": "Temperatura",
            "Status Atual da Tratativa": "Status"
        }

        colunas_risco = [
            c for c in mapping_risco.keys()
            if c in df_risco.columns
        ]

        risco_view = df_risco[colunas_risco].rename(
            columns=mapping_risco
        )

        st.dataframe(
            risco_view,
            use_container_width=True
        )

    # ==================================================
    # ABA CHURN
    # ==================================================
    with tab2:

        st.subheader("Análise de Churn")

        c1, c2, c3 = st.columns(3)

        total_cancelamentos = df_churn[
            "Quantidade Total de Cancelamentos Solicitados"
        ].sum()

        total_revertidos = df_churn[
            "Quant. Revertido"
        ].sum()

        percentual = 0

        if total_cancelamentos > 0:
            percentual = (
                total_revertidos / total_cancelamentos
            ) * 100

        c1.metric(
            "Cancelamentos",
            int(total_cancelamentos)
        )

        c2.metric(
            "Revertidos",
            int(total_revertidos)
        )

        c3.metric(
            "% Reversão",
            f"{percentual:.2f}%"
        )

        st.divider()

        mapping_churn = {
            "Nome da Empresa": "Empresa",
            "Quantidade Total de Contratos do Grupo": "Qtd Grupo",
            "Quantidade Total de Cancelamentos Solicitados": "Cancelamentos",
            "Quant. Revertido": "Revertidos",
            "Franquia": "Franquia",
            "Motivo Principal do Cancelamento": "Motivo",
            "Status": "Status"
        }

        colunas_churn = [
            c for c in mapping_churn.keys()
            if c in df_churn.columns
        ]

        churn_view = df_churn[colunas_churn].rename(
            columns=mapping_churn
        )

        st.dataframe(
            churn_view,
            use_container_width=True
        )

except Exception as e:

    st.error("Erro ao executar aplicação")

    st.write(e)
