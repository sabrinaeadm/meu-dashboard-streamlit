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
    initial_sidebar_state="collapsed" # Menu lateral escondido por padrão
)

# Estilização CSS para forçar textos escuros se o usuário estiver em tema claro
# e garantir um visual limpo.
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        color: #0A2342;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Executivo")
st.markdown("Acompanhamento de Riscos e Churn para tomada de decisão estratégica.")

# =====================================================
# PALETA DE CORES EXECUTIVA (Navy/Dark Blue)
# =====================================================
COLOR_NAVY_DEEP = "#0A2342"
COLOR_NAVY_MED = "#153B6D"
COLOR_NAVY_LIGHT = "#3664A3"
# Escala de azuis para gráficos
BLUE_SCALE = [COLOR_NAVY_DEEP, COLOR_NAVY_MED, COLOR_NAVY_LIGHT, "#5C85BB", "#89A7D3"]

# =====================================================
# MENU LATERAL: UPLOAD COM MEMÓRIA PERSISTENTE
# =====================================================
with st.sidebar.expander("⚙️ Atualizar Bases de Dados", expanded=False):
    st.markdown("<small>Carregue novas bases aqui. Elas ficarão salvas no sistema mesmo se você atualizar a página (F5).</small>", unsafe_allow_html=True)
    
    up_risco = st.file_uploader("1. Gestão de Riscos", type=['csv', 'xlsx'])
    up_churn = st.file_uploader("2. Churn/Cancelamentos", type=['csv', 'xlsx'])

    # Salva os arquivos no disco do servidor para não sumirem no F5
    if up_risco:
        with open("risco_temporario.csv", "wb") as f:
            f.write(up_risco.getbuffer())
        st.success("✅ Base de Riscos salva no sistema!")
        
    if up_churn:
        with open("churn_temporario.csv", "wb") as f:
            f.write(up_churn.getbuffer())
        st.success("✅ Base de Churn salva no sistema!")

    st.divider()
    
    # Botão para deletar as bases quando o usuário quiser
    if st.button("🗑️ Limpar Bases Salvas"):
        if os.path.exists("risco_temporario.csv"):
            os.remove("risco_temporario.csv")
        if os.path.exists("churn_temporario.csv"):
            os.remove("churn_temporario.csv")
        st.success("Bases limpas com sucesso!")
        st.rerun()

# =====================================================
# FUNÇÃO LEITURA E TRATAMENTO (SEM CACHE PARA ATUALIZAR NA HORA)
# =====================================================
def load_data():
    df_risco = pd.DataFrame()
    df_churn = pd.DataFrame()
    
    # --- CARREGAR GESTÃO DE RISCOS (Ordem de Prioridade) ---
    if os.path.exists("risco_temporario.csv"):
        try: df_risco = pd.read_csv("risco_temporario.csv", sep=";", encoding="utf-8")
        except: df_risco = pd.read_excel("risco_temporario.csv")
    elif os.path.exists("risco.csv"):
        df_risco = pd.read_csv("risco.csv", sep=";", encoding="utf-8")
    elif os.path.exists("Gestão de riscos e reclamações(respostas).csv"):
        df_risco = pd.read_csv("Gestão de riscos e reclamações(respostas).csv", sep=";", encoding="utf-8")

    # --- CARREGAR CHURN (Ordem de Prioridade) ---
    if os.path.exists("churn_temporario.csv"):
        try: df_churn = pd.read_csv("churn_temporario.csv", sep=";", encoding="utf-8")
        except: df_churn = pd.read_excel("churn_temporario.csv")
    elif os.path.exists("churn.csv"):
        df_churn = pd.read_csv("churn.csv", sep=";", encoding="utf-8")
    elif os.path.exists("Formulário de Solicitação de Cancelamento(Respostas).csv"):
        df_churn = pd.read_csv("Formulário de Solicitação de Cancelamento(Respostas).csv", sep=";", encoding="utf-8")

    # Se estiver tudo vazio, retorna para avisar o usuário
    if df_risco.empty or df_churn.empty:
        return df_risco, df_churn

    # --- LIMPEZA E PADRONIZAÇÃO ---
    df_risco.columns = df_risco.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)
    df_churn.columns = df_churn.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)

    # -------------------------------------------------
    # BLINDAGEM - GESTÃO DE RISCO
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
    # BLINDAGEM - CHURN
    # -------------------------------------------------
    c_franquia_churn = next((c for c in df_churn.columns if 'franquia' in c.lower()), None)
    if c_franquia_churn: df_churn.rename(columns={c_franquia_churn: 'Franquia_Standard'}, inplace=True)
    
    c_motivo_churn = next((c for c in df_churn.columns if 'motivo' in c.lower() and 'principal' in c.lower()), None)
    if c_motivo_churn: df_churn.rename(columns={c_motivo_churn: 'Motivo_Standard'}, inplace=True)
    
    c_grupo_churn = next((c for c in df_churn.columns if 'nome' in c.lower() and 'grupo' in c.lower()), None)
    if not c_grupo_churn: c_grupo_churn = next((c for c in df_churn.columns if 'grupo' in c.lower() and 'quantidade' not in c.lower()), None)
    if not c_grupo_churn: c_grupo_churn = next((c for c in df_churn.columns if 'empresa' in c.lower() and 'cnpj' not in c.lower()), None)
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

    # Força as colunas numéricas a serem números
    if 'Qtd_Cancelamentos_Standard' in df_churn.columns:
        df_churn['Qtd_Cancelamentos_Standard'] = pd.to_numeric(df_churn['Qtd_Cancelamentos_Standard'], errors='coerce').fillna(0)
    if 'Qtd_Revertidos_Standard' in df_churn.columns:
        df_churn['Qtd_Revertidos_Standard'] = pd.to_numeric(df_churn['Qtd_Revertidos_Standard'], errors='coerce').fillna(0)

    return df_risco, df_churn

# =====================================================
# EXECUÇÃO DO APP
# =====================================================
try:
    df_risco, df_churn = load_data()

    if df_risco.empty or df_churn.empty:
        st.warning("⚠️ O Dashboard está aguardando os dados.")
        st.info("👉 **Abra o menu lateral (clicando na setinha > no canto superior esquerdo)** e arraste os seus arquivos de Excel/CSV para visualizar o painel. Eles ficarão salvos!")
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
            filtro_status_risco = st.multiselect("Status da Tratativa", status_risco_opcoes)
        with rf2:
            ano_risco_opcoes = sorted(df_risco['Ano'].unique()) if 'Ano' in df_risco.columns else []
            filtro_ano_risco = st.multiselect("Ano do Evento", ano_risco_opcoes)
        with rf3:
            mes_risco_opcoes = sorted(df_risco['Mês'].unique()) if 'Mês' in df_risco.columns else []
            filtro_mes_risco = st.multiselect("Mês do Evento", mes_risco_opcoes)
        with rf4:
            area_risco_opcoes = sorted(df_risco['Area_Standard'].dropna().astype(str).unique()) if 'Area_Standard' in df_risco.columns else []
            filtro_area_risco = st.multiselect("Área Responsável", area_risco_opcoes)

        risco_filtrado = df_risco.copy()
        if filtro_status_risco: risco_filtrado = risco_filtrado[risco_filtrado['Status_Standard'].isin(filtro_status_risco)]
        if filtro_ano_risco: risco_filtrado = risco_filtrado[risco_filtrado['Ano'].isin(filtro_ano_risco)]
        if filtro_mes_risco: risco_filtrado = risco_filtrado[risco_filtrado['Mês'].isin(filtro_mes_risco)]
        if filtro_area_risco: risco_filtrado = risco_filtrado[risco_filtrado['Area_Standard'].astype(str).isin(filtro_area_risco)]

        st.divider()

        total_casos = len(risco_filtrado)
        aging_medio = risco_filtrado['Aging_Standard'].mean() if 'Aging_Standard' in risco_filtrado.columns else 0
        risco_medio = risco_filtrado['Grau Numérico'].mean() if 'Grau Numérico' in risco_filtrado.columns else 0
        try: area_critica = risco_filtrado['Area_Standard'].mode()[0] if not risco_filtrado.empty else "N/A"
        except: area_critica = "N/A"

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total de Casos", f"{total_casos}")
        kpi2.metric("Aging Médio (Dias)", f"{aging_medio:.1f}" if pd.notnull(aging_medio) else "0")
        kpi3.metric("Risco Médio", f"{risco_medio:.1f}" if pd.notnull(risco_medio) else "0")
        kpi4.metric("Área Crítica (Moda)", str(area_critica))

        st.divider()

        g1, g2 = st.columns([1, 2])
        with g1:
            st.markdown("##### 🌡️ Termômetro de Risco (Médio)")
            # AJUSTE: Cores intensas e ponteiro preto
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risco_medio if pd.notnull(risco_medio) else 0,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 5], 'tickwidth': 1, 'tickcolor': "black"},
                    'bar': {'color': "black", 'thickness': 0.25}, # Marcador interno PRETO
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 2], 'color': "#008000"},   # VERDE INTENSO
                        {'range': [2, 3.5], 'color': "#FFD700"}, # AMARELO OURO INTENSO
                        {'range': [3.5, 5], 'color': "#FF0000"}  # VERMELHO VIVO INTENSO
                    ],
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gauge, use_container_width=True)

        with g2:
            st.markdown("##### 📊 Riscos por Área")
            if 'Area_Standard' in risco_filtrado.columns:
                df_area = risco_filtrado['Area_Standard'].value_counts().reset_index()
                df_area.columns = ['Área', 'Quantidade']
                # AJUSTE: Gráfico em tons de Azul Escuro
                fig_bar = px.bar(df_area, x='Área', y='Quantidade', text_auto=True, color='Quantidade', color_continuous_scale=BLUE_SCALE)
                fig_bar.update_layout(height=280, xaxis_title="", yaxis_title="Casos", showlegend=False, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)

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

        churn_filtrado = df_churn.copy()
        
        if 'Franquia_Standard' in churn_filtrado.columns and filtro_franquia:
            churn_filtrado = churn_filtrado[churn_filtrado["Franquia_Standard"].astype(str).isin(filtro_franquia)]
        if filtro_ano_churn:
            churn_filtrado = churn_filtrado[churn_filtrado["Ano"].isin(filtro_ano_churn)]
        if filtro_mes_churn:
            churn_filtrado = churn_filtrado[churn_filtrado["Mês"].isin(filtro_mes_churn)]
        if 'Status_Standard' in churn_filtrado.columns and filtro_status_churn:
            churn_filtrado = churn_filtrado[churn_filtrado["Status_Standard"].astype(str).isin(filtro_status_churn)]

        st.divider()

        total_solicitacoes = len(churn_filtrado)
        total_cancelamentos = churn_filtrado['Qtd_Cancelamentos_Standard'].sum() if 'Qtd_Cancelamentos_Standard' in churn_filtrado.columns else 0
        total_revertidos = churn_filtrado['Qtd_Revertidos_Standard'].sum() if 'Qtd_Revertidos_Standard' in churn_filtrado.columns else 0

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("Total de Solicitações", f"{total_solicitacoes}")
        kc2.metric("Qtd. Contratos Cancelados", f"{total_cancelamentos:.0f}")
        kc3.metric("Qtd. Contratos Revertidos", f"{total_revertidos:.0f}")

        st.divider()

        cg1, cg2 = st.columns(2)
        with cg1:
            st.markdown("##### 📌 Cancelamentos por Franquia")
            if 'Franquia_Standard' in churn_filtrado.columns:
                df_franq = churn_filtrado['Franquia_Standard'].value_counts().reset_index()
                df_franq.columns = ['Franquia', 'Cancelamentos']
                # AJUSTE: Gráfico em tons de Azul Escuro
                fig_franq = px.bar(df_franq.head(10), x='Cancelamentos', y='Franquia', orientation='h', text_auto=True, color='Cancelamentos', color_continuous_scale=BLUE_SCALE)
                fig_franq.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=320, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_franq, use_container_width=True)

        with cg2:
            st.markdown("##### 📌 Motivo Principal do Cancelamento")
            if 'Motivo_Standard' in churn_filtrado.columns:
                df_motivo = churn_filtrado['Motivo_Standard'].value_counts().reset_index()
                df_motivo.columns = ['Motivo', 'Quantidade']
                # AJUSTE: Gráfico de Rosca usando a paleta Azul Escuro
                fig_motivo = px.pie(df_motivo.head(7), values='Quantidade', names='Motivo', hole=0.4, color_discrete_sequence=BLUE_SCALE)
                fig_motivo.update_layout(height=320, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_motivo, use_container_width=True)

        st.divider()

        st.markdown("##### 🏢 Empresas com Solicitação (Detalhamento)")
        colunas_tabela_churn = {
            'Grupo_Standard': 'Nome do Grupo / Empresa',
            'CNPJ_Standard': 'CNPJ',
            'Franquia_Standard': 'Franquia',
            'Motivo_Standard': 'Motivo Principal',
            'Qtd_Cancelamentos_Standard': 'Qtd. Cancelamentos',
            'Qtd_Revertidos_Standard': 'Quantidade de Revertidos',
            'Status_Standard': 'Status'
        }
        cols_existentes_churn = [c for c in colunas_tabela_churn.keys() if c in churn_filtrado.columns]
        df_churn_view = churn_filtrado[cols_existentes_churn].rename(columns=colunas_tabela_churn)
        st.dataframe(df_churn_view, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Ocorreu um erro interno ao gerar os gráficos. Verifique o formato do arquivo.")
    st.exception(e)
