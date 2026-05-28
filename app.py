import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================
# CONFIGURAÇÃO DA PÁGINA (Expandida)
# =====================================================
st.set_page_config(
    page_title="Dashboard Executivo",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Injeção de CSS: Paleta Clara, Cartões Brancos (SUPERCOMPACTOS) e PDF
estilo_minimalista = """
<style>
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fundo da aplicação claro (gelo) */
    .stApp { background-color: #F4F7FB !important; }
    
    /* Reduzir margens superiores da página */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Tipografia e Cor Global */
    html, body, [class*="css"] {
        font-size: 12px !important; 
        color: #1E293B !important;
    }
    
    /* Estilizar abas */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px; 
        white-space: pre-wrap;
        background-color: transparent;
        color: #0033A0;
        font-weight: 600;
        font-size: 13px; 
    }

    /* Estilo dos Cartões - AJUSTADOS PARA SEREM MUITO MENORES E MAIS COMPACTOS */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 6px; 
        padding: 6px 10px; 
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); 
        border: 1px solid #E2E8F0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 90%; 
        margin: 0 auto; 
    }
    .kpi-val { 
        font-size: 22px; 
        font-weight: 800; 
        color: #0033A0; 
        line-height: 1.0; 
        margin-bottom: 0px; 
    } 
    .kpi-label { 
        font-size: 10px; 
        font-weight: 600; 
        color: #64748B; 
        text-transform: uppercase; 
        letter-spacing: 0.3px; 
    } 
    .kpi-sub { 
        font-size: 10px; 
        margin-top: 2px; 
        font-weight: 600; 
    } 
    .kpi-sub span {
        padding: 2px 4px; 
        font-size: 10px; 
    }
    
    /* Regras para exportação perfeita em PDF (Ctrl + P) */
    @media print {
        .stSidebar { display: none !important; }
        header { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { display: none !important; }
        .stApp { background-color: #FFFFFF !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        /* Ocultar barra de busca na impressão */
        div[data-testid="stTextInput"] { display: none !important; }
    }
</style>
"""
st.markdown(estilo_minimalista, unsafe_allow_html=True)

# =====================================================
# PALETA DE CORES EXECUTIVA
# =====================================================
BLUE_SCALE = ["#0033A0", "#153B6D", "#3664A3", "#5C85BB", "#89A7D3"]

# =====================================================
# MENU LATERAL: ATUALIZAÇÃO DE BASE
# =====================================================
with st.sidebar:
    st.markdown("### ⚙️ Administração de Dados")
    st.markdown("<small>Carregue os arquivos CSV/XLSX para atualizar os painéis.</small>", unsafe_allow_html=True)
    
    up_risco = st.file_uploader("1. Base de Riscos", type=['csv', 'xlsx'])
    up_churn = st.file_uploader("2. Base de Churn", type=['csv', 'xlsx'])

    if up_risco:
        with open("risco_temporario.csv", "wb") as f:
            f.write(up_risco.getbuffer())
        st.success("Base de Riscos salva!")
        
    if up_churn:
        with open("churn_temporario.csv", "wb") as f:
            f.write(up_churn.getbuffer())
        st.success("Base de Churn salva!")

    st.divider()
    
    if st.button("🗑️ Limpar Bases Salvas", use_container_width=True):
        if os.path.exists("risco_temporario.csv"): os.remove("risco_temporario.csv")
        if os.path.exists("churn_temporario.csv"): os.remove("churn_temporario.csv")
        st.rerun()
        
    st.info("💡 **Dica:** Para gerar o reporte, feche os filtros e aperte `Ctrl + P` para salvar como PDF limpo.")

# =====================================================
# FUNÇÃO LEITURA E TRATAMENTO
# =====================================================
def load_data():
    df_risco = pd.DataFrame()
    df_churn = pd.DataFrame()
    
    if os.path.exists("risco_temporario.csv"):
        try: df_risco = pd.read_csv("risco_temporario.csv", sep=";", encoding="utf-8")
        except: df_risco = pd.read_excel("risco_temporario.csv")
    elif os.path.exists("risco.csv"):
        df_risco = pd.read_csv("risco.csv", sep=";", encoding="utf-8")

    if os.path.exists("churn_temporario.csv"):
        try: df_churn = pd.read_csv("churn_temporario.csv", sep=";", encoding="utf-8")
        except: df_churn = pd.read_excel("churn_temporario.csv")
    elif os.path.exists("churn.csv"):
        df_churn = pd.read_csv("churn.csv", sep=";", encoding="utf-8")

    if not df_risco.empty:
        df_risco.columns = df_risco.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)
        c_empresa_risco = next((c for c in df_risco.columns if 'empresa' in c.lower() or 'cliente' in c.lower()), None)
        if c_empresa_risco: df_risco.rename(columns={c_empresa_risco: 'Empresa_Standard'}, inplace=True)
        c_aging_risco = next((c for c in df_risco.columns if 'dias' in c.lower() and ('aberto' in c.lower() or 'parados' in c.lower()) or 'aging' in c.lower()), None)
        if c_aging_risco: df_risco.rename(columns={c_aging_risco: 'Aging_Standard'}, inplace=True)
        c_area_risco = next((c for c in df_risco.columns if 'área' in c.lower() or 'area' in c.lower()), None)
        if c_area_risco: df_risco.rename(columns={c_area_risco: 'Area_Standard'}, inplace=True)
        c_grau_risco = next((c for c in df_risco.columns if 'grau' in c.lower() or 'risco' in c.lower() and 'atual' in c.lower()), None)
        if c_grau_risco: df_risco.rename(columns={c_grau_risco: 'Grau_Standard'}, inplace=True)
        
        if 'Status' in df_risco.columns: df_risco.rename(columns={'Status': 'Status_Standard'}, inplace=True)
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

    if not df_churn.empty:
        df_churn.columns = df_churn.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False)
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
        
        if 'Status' in df_churn.columns: df_churn.rename(columns={'Status': 'Status_Standard'}, inplace=True)
        else:
            c_status_churn = next((c for c in df_churn.columns if 'status' in c.lower()), None)
            if c_status_churn: df_churn.rename(columns={c_status_churn: 'Status_Standard'}, inplace=True)

        c_data_churn = next((c for c in df_churn.columns if 'data' in c.lower() and 'solicita' in c.lower()), None)
        if c_data_churn:
            df_churn['Data Base'] = pd.to_datetime(df_churn[c_data_churn], format='%d/%m/%Y', errors='coerce')
            df_churn['Ano'] = df_churn['Data Base'].dt.year.fillna(0).astype(int).astype(str).replace('0', 'N/A')
            df_churn['Mês'] = df_churn['Data Base'].dt.month.fillna(0).astype(int).astype(str).replace('0', 'N/A')
            df_churn['Data_Standard'] = df_churn['Data Base'].dt.strftime('%d/%m/%Y').fillna('N/A').replace('NaT', 'N/A')

        if 'Qtd_Cancelamentos_Standard' in df_churn.columns:
            df_churn['Qtd_Cancelamentos_Standard'] = pd.to_numeric(df_churn['Qtd_Cancelamentos_Standard'], errors='coerce').fillna(0)
        if 'Qtd_Revertidos_Standard' in df_churn.columns:
            df_churn['Qtd_Revertidos_Standard'] = pd.to_numeric(df_churn['Qtd_Revertidos_Standard'], errors='coerce').fillna(0)

    return df_risco, df_churn

def safe_pct(part, whole):
    return (part / whole * 100) if whole > 0 else 0

# =====================================================
# EXECUÇÃO DO APP
# =====================================================
try:
    df_risco, df_churn = load_data()

    tab1, tab2 = st.tabs([
        "GESTÃO DE RISCOS", 
        "CHURN E CANCELAMENTOS"
    ])

    # =====================================================
    # ABA 1: GESTÃO DE RISCO 
    # =====================================================
    with tab1:
        if df_risco.empty:
            st.warning("⚠️ Faça o upload da base de **Gestão de Riscos** no menu lateral esquerdo para visualizar este painel.")
        else:
            st.markdown("<p style='color:#64748B; font-weight:bold; margin-bottom:-10px;'>FILTROS GLOBAIS</p>", unsafe_allow_html=True)
            rf1, rf2, rf3, rf4 = st.columns(4)
            
            with rf1:
                status_risco_opcoes = sorted(df_risco['Status_Standard'].dropna().unique()) if 'Status_Standard' in df_risco.columns else []
                filtro_status_risco = st.multiselect("Status da Tratativa", status_risco_opcoes)
            with rf2:
                ano_risco_opcoes = sorted(df_risco['Ano'].unique()) if 'Ano' in df_risco.columns else []
                filtro_ano_risco = st.multiselect("Ano", ano_risco_opcoes)
            with rf3:
                mes_risco_opcoes = sorted(df_risco['Mês'].unique()) if 'Mês' in df_risco.columns else []
                filtro_mes_risco = st.multiselect("Mês", mes_risco_opcoes)
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
            pct_casos = safe_pct(total_casos, len(df_risco))
            aging_medio = risco_filtrado['Aging_Standard'].mean() if 'Aging_Standard' in risco_filtrado.columns else 0
            aging_medio_total = df_risco['Aging_Standard'].mean() if 'Aging_Standard' in df_risco.columns else 1
            pct_aging = safe_pct(aging_medio, aging_medio_total)
            risco_medio = risco_filtrado['Grau Numérico'].mean() if 'Grau Numérico' in risco_filtrado.columns else 0
            pct_risco = safe_pct(risco_medio, 5.0) 
            
            try: 
                area_critica = risco_filtrado['Area_Standard'].mode()[0] if not risco_filtrado.empty else "N/A"
                qtd_area_critica = len(risco_filtrado[risco_filtrado['Area_Standard'] == area_critica])
                pct_area = safe_pct(qtd_area_critica, total_casos)
            except: 
                area_critica = "N/A"
                pct_area = 0

            kr1, kr2, kr3, kr4 = st.columns(4)
            kr1.markdown(f'<div class="kpi-card"><div class="kpi-val">{total_casos}</div><div class="kpi-label">Total de Casos</div></div>', unsafe_allow_html=True)
            kr2.markdown(f'<div class="kpi-card"><div class="kpi-val">{aging_medio:.1f}</div><div class="kpi-label">Aging Médio (Dias)</div></div>', unsafe_allow_html=True)
            kr3.markdown(f'<div class="kpi-card"><div class="kpi-val">{risco_medio:.1f}</div><div class="kpi-label">Risco Médio</div></div>', unsafe_allow_html=True)
            kr4.markdown(f'<div class="kpi-card"><div class="kpi-val" style="font-size:20px;">{area_critica}</div><div class="kpi-label">Área Crítica</div></div>', unsafe_allow_html=True)

            st.divider()

            g1, g2 = st.columns([1, 2])
            with g1:
                st.markdown("<p style='color:#0033A0; font-weight:bold;'>Termômetro de Risco Médio</p>", unsafe_allow_html=True)
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = risco_medio if pd.notnull(risco_medio) else 0,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [None, 5], 'tickwidth': 1, 'tickcolor': "#0A2342"},
                        'bar': {'color': "#0033A0", 'thickness': 0.25}, 
                        'bgcolor': "white",
                        'borderwidth': 1,
                        'bordercolor': "#E2E8F0",
                        'steps': [{'range': [0, 2], 'color': "#89A7D3"}, {'range': [2, 3.5], 'color': "#3664A3"}, {'range': [3.5, 5], 'color': "#0A2342"}],
                    }
                ))
                fig_gauge.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_gauge, use_container_width=True)

            with g2:
                st.markdown("<p style='color:#0033A0; font-weight:bold;'>Distribuição de Casos por Área</p>", unsafe_allow_html=True)
                if 'Area_Standard' in risco_filtrado.columns:
                    df_area = risco_filtrado['Area_Standard'].value_counts().reset_index()
                    df_area.columns = ['Área', 'Quantidade']
                    fig_area = px.pie(df_area, values='Quantidade', names='Área', hole=0.6, color_discrete_sequence=BLUE_SCALE)
                    fig_area.update_traces(textinfo='value+percent', textposition='inside')
                    fig_area.update_layout(height=220, showlegend=True, margin=dict(l=0, r=0, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_area, use_container_width=True)

            st.markdown("<p style='color:#0033A0; font-weight:bold;'>Detalhamento Executivo</p>", unsafe_allow_html=True)
            colunas_tabela_risco = {'Empresa_Standard': 'Empresa', 'Aging_Standard': 'Dias Parados', 'Area_Standard': 'Área Responsável', 'Grau_Standard': 'Impacto', 'Status_Standard': 'Status'}
            cols_existentes = [c for c in colunas_tabela_risco.keys() if c in risco_filtrado.columns]
            df_risco_view = risco_filtrado[cols_existentes].rename(columns=colunas_tabela_risco)
            st.dataframe(df_risco_view, use_container_width=True, hide_index=True)


    # =====================================================
    # ABA 2: CHURN E CANCELAMENTOS
    # =====================================================
    with tab2:
        if df_churn.empty:
            st.warning("⚠️ Faça o upload da base de **Churn/Cancelamentos** no menu lateral esquerdo para visualizar este painel.")
        else:
            st.markdown("<p style='color:#64748B; font-weight:bold; margin-bottom:-10px;'>FILTROS GLOBAIS</p>", unsafe_allow_html=True)
            cf1, cf2, cf3, cf4, cf5 = st.columns(5)

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
            with cf5:
                data_churn_opcoes = sorted(df_churn["Data_Standard"].dropna().unique()) if 'Data_Standard' in df_churn.columns else []
                filtro_data_churn = st.multiselect("Data da Solicitação", data_churn_opcoes)

            churn_filtrado = df_churn.copy()
            
            if 'Franquia_Standard' in churn_filtrado.columns and filtro_franquia:
                churn_filtrado = churn_filtrado[churn_filtrado["Franquia_Standard"].astype(str).isin(filtro_franquia)]
            if filtro_ano_churn: churn_filtrado = churn_filtrado[churn_filtrado["Ano"].isin(filtro_ano_churn)]
            if filtro_mes_churn: churn_filtrado = churn_filtrado[churn_filtrado["Mês"].isin(filtro_mes_churn)]
            if 'Status_Standard' in churn_filtrado.columns and filtro_status_churn:
                churn_filtrado = churn_filtrado[churn_filtrado["Status_Standard"].astype(str).isin(filtro_status_churn)]
            if 'Data_Standard' in churn_filtrado.columns and filtro_data_churn:
                churn_filtrado = churn_filtrado[churn_filtrado["Data_Standard"].isin(filtro_data_churn)]

            st.divider()

            total_solicitacoes = len(churn_filtrado)
            total_cancelamentos = churn_filtrado['Qtd_Cancelamentos_Standard'].sum() if 'Qtd_Cancelamentos_Standard' in churn_filtrado.columns else 0
            total_revertidos = churn_filtrado['Qtd_Revertidos_Standard'].sum() if 'Qtd_Revertidos_Standard' in churn_filtrado.columns else 0
            total_contratos_filtrados = total_cancelamentos + total_revertidos
            pct_rev = safe_pct(total_revertidos, total_contratos_filtrados)

            kc1, kc2, kc3 = st.columns(3)
            
            kc1.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{total_solicitacoes:02d}</div>
                <div class="kpi-label">VOLUME DE SOLICITAÇÕES</div>
            </div>
            """, unsafe_allow_html=True)
            
            kc2.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{total_cancelamentos:02.0f}</div>
                <div class="kpi-label">CONTRATOS CANCELADOS</div>
            </div>
            """, unsafe_allow_html=True)
            
            kc3.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{total_revertidos:02.0f}</div>
                <div class="kpi-label">CONTRATOS REVERTIDOS</div>
                <div class="kpi-sub"><span style="background:#E0E7FF; color:#1D4ED8; border-radius:4px;">{pct_rev:.1f}% Taxa de Reversão</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            col_esq, col_dir = st.columns([1, 1.6])
            
            with col_esq:
                st.markdown("<p style='color:#0033A0; font-weight:bold; font-size:16px;'>📉 Impacto por Franquia</p>", unsafe_allow_html=True)
                if 'Franquia_Standard' in churn_filtrado.columns:
                    df_franq = churn_filtrado['Franquia_Standard'].value_counts().reset_index()
                    df_franq.columns = ['Franquia', 'Cancelamentos']
                    fig_franq = px.bar(df_franq.head(6), x='Cancelamentos', y='Franquia', orientation='h', text_auto=True, color='Cancelamentos', color_continuous_scale=BLUE_SCALE)
                    fig_franq.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False, showlegend=False, height=220, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_franq, use_container_width=True)

                st.markdown("<p style='color:#0033A0; font-weight:bold; font-size:16px; margin-top:10px;'>🎯 Motivadores Principais</p>", unsafe_allow_html=True)
                if 'Motivo_Standard' in churn_filtrado.columns:
                    df_motivo = churn_filtrado['Motivo_Standard'].value_counts().reset_index()
                    df_motivo.columns = ['Motivo', 'Quantidade']
                    fig_motivo = px.pie(df_motivo.head(5), values='Quantidade', names='Motivo', hole=0.6, color_discrete_sequence=BLUE_SCALE)
                    fig_motivo.update_traces(textinfo='value+percent', textposition='inside')
                    fig_motivo.update_layout(height=220, margin=dict(l=0, r=0, t=0, b=0), showlegend=True, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_motivo, use_container_width=True)

            with col_dir:
                # Topo da tabela dividido para o título e a barra de busca
                c_topo1, c_topo2 = st.columns([1, 1])
                with c_topo1:
                    st.markdown("<p style='color:#0033A0; font-weight:bold; font-size:16px; padding-top:8px;'>🗂️ Detalhe por Empresa</p>", unsafe_allow_html=True)
                with c_topo2:
                    busca_cliente = st.text_input("Buscar Cliente", placeholder="🔍 Digite CNPJ ou Empresa...", label_visibility="collapsed")
                
                # Lógica da busca
                if busca_cliente:
                    # Filtra a tabela visual onde o CNPJ ou Nome contiverem o texto da busca
                    filtro_tabela = churn_filtrado[
                        churn_filtrado['Grupo_Standard'].astype(str).str.contains(busca_cliente, case=False, na=False) |
                        churn_filtrado['CNPJ_Standard'].astype(str).str.contains(busca_cliente, case=False, na=False)
                    ]
                else:
                    filtro_tabela = churn_filtrado
                
                colunas_tabela_churn = {
                    'Grupo_Standard': 'Empresa / Grupo',
                    'CNPJ_Standard': 'CNPJ',
                    'Franquia_Standard': 'Franquia',
                    'Motivo_Standard': 'Motivo Principal',
                    'Qtd_Cancelamentos_Standard': 'Cancelamentos',
                    'Qtd_Revertidos_Standard': 'Reversões',
                    'Status_Standard': 'Status'
                }
                cols_existentes_churn = [c for c in colunas_tabela_churn.keys() if c in filtro_tabela.columns]
                df_churn_view = filtro_tabela[cols_existentes_churn].rename(columns=colunas_tabela_churn)
                
                st.dataframe(df_churn_view, use_container_width=True, hide_index=True, height=480)

except Exception as e:
    st.error("Erro interno ao gerar visualizações. Por favor, cheque a integridade da sua base de dados.")
    st.exception(e)
