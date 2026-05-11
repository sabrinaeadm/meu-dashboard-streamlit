import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Executivo",
    layout="wide"
)

st.title("📊 Dashboard Executivo - Whirlpool")

# ==========================================
# CARREGAMENTO DOS DADOS
# ==========================================
@st.cache_data
def load_data():

    file_risco = "gestao.xlsx"
    file_churn = "churn.xlsx"

    df_risco = pd.read_excel(file_risco, engine="openpyxl")
    df_churn = pd.read_excel(file_churn, engine="openpyxl")

    return df_risco, df_churn


try:

    df_risco, df_churn = load_data()

    # ==========================================
    # ABAS
    # ==========================================
    tab1, tab2 = st.tabs(
        ["⚠️ Gestão de Risco", "📉 Churn"]
    )

    # ==========================================
    # ABA GESTÃO DE RISCO
    # ==========================================
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

        # ==========================
        # KPIs
        # ==========================
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total de Casos",
            len(risco_view)
        )

        if "Cliente" in risco_view.columns:
            c2.metric(
                "Clientes Impactados",
                risco_view["Cliente"].nunique()
            )

        if "Área" in risco_view.columns:
            c3.metric(
                "Áreas Envolvidas",
                risco_view["Área"].nunique()
            )

        st.divider()

        # ==========================
        # GRÁFICOS
        # ==========================
        col1, col2 = st.columns(2)

        # Gráfico Área Reclamada
        with col1:

            st.markdown("### 📌 Riscos por Área")

            if "Área" in risco_view.columns:

                grafico_area = (
                    risco_view["Área"]
                    .value_counts()
                )

                st.bar_chart(grafico_area)

        # Gráfico Status
        with col2:

            st.markdown("### 📌 Status das Tratativas")

            if "Status" in risco_view.columns:

                grafico_status = (
                    risco_view["Status"]
                    .value_counts()
                )

                st.bar_chart(grafico_status)

        st.divider()

        st.markdown("### 📋 Base Completa")

        st.dataframe(
            risco_view,
            use_container_width=True
        )

    # ==========================================
    # ABA CHURN
    # ==========================================
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

        # ==========================================
        # GRÁFICOS CHURN
        # ==========================================
        col3, col4 = st.columns(2)

        # Motivos
        with col3:

            st.markdown("### 📌 Motivos de Cancelamento")

            if "Motivo" in churn_view.columns:

                grafico_motivo = (
                    churn_view["Motivo"]
                    .value_counts()
                    .head(10)
                )

                st.bar_chart(grafico_motivo)

        # Franquia
        with col4:

            st.markdown("### 📌 Churn por Franquia")

            if "Franquia" in churn_view.columns:

                grafico_franquia = (
                    churn_view["Franquia"]
                    .value_counts()
                    .head(10)
                )

                st.bar_chart(grafico_franquia)

        st.divider()

        st.markdown("### 📋 Base Completa")

        st.dataframe(
            churn_view,
            use_container_width=True
        )

except Exception as e:

    st.error("Erro ao executar aplicação")

    st.write(e)
