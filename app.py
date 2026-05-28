import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# =====================================================
# CONFIGURAÇÃO DA PÁGINA (Expandida e Clean)
# =====================================================
st.set_page_config(
    page_title="Monitor de Cancelamentos",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Injeção de CSS: Paleta Clara, Cartões com Sombra e Layout de Impressão (PDF)
estilo_reporte = """
<style>
    /* Fundo da aplicação claro (cinza/gelo) para destacar os cartões brancos */
    .stApp { background-color: #F4F7FB !important; }
    
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px; /* Limita a largura para o print ficar perfeito */
    }
    
    /* Tipografia global */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #1E293B !important;
    }
    
    /* Estilo dos Cartões KPI (Idêntico ao Print) */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .kpi-value {
        font-size: 42px;
        font-weight: 800;
        color: #0033A0;
        line-height: 1.1;
        margin-bottom: 5px;
    }
    
    .kpi-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-subtext {
        font-size: 12px;
        margin-top: 10px;
        display: flex;
        gap: 10px;
    }
    
    .pill-blue { background-color: #E0E7FF; color: #1D4ED8; padding: 4px 8px; border-radius: 4px; font-weight: 600;}
    .pill-orange { background-color: #FFEDD5; color: #C2410C; padding: 4px 8px; border-radius: 4px; font-weight: 600;}
    .pill-green { background-color: #DCFCE7; color: #15803D; padding: 4px 8px; border-radius: 4px; font-weight: 600;}

    /* Configuração para gerar o PDF (Ctrl+P) perfeito */
    @media print {
        .stSidebar { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { display: none !important; }
        div[data-testid="stToolbar"] { display: none !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        /* Força fundo branco na impressão */
        .stApp, .kpi-card { background-color: #FFFFFF !important; box-shadow: none !important; border: 1px solid #E2E8F0 !important;}
    }
</style>
"""
st.markdown(estilo_reporte, unsafe_allow_html=True)

# =====================================================
# MENU LATERAL
# =====================================================
with st.sidebar:
    st.markdown("### ⚙️ Administração")
    st.markdown("<small>Atualize as bases para o reporte diário.</small>", unsafe_allow_html=True)
    
    up_risco = st.file_uploader("1. Base de Riscos", type=['csv', 'xlsx'])
    up_churn = st.file_uploader("2. Base de Churn", type=['csv', 'xlsx'])

    if up_risco:
        with open("risco_temporario.csv", "wb") as f: f.write(up_risco.getbuffer())
        st.success("Base de Riscos salva!")
        
    if up_churn:
        with open("churn_temporario.csv", "wb") as f: f.write(up_churn.getbuffer())
        st.success("Base de Churn salva!")

    st.divider()
    if st.button("🗑️ Limpar Bases", use_container_width=True):
        if os.path.exists("risco_temporario.csv"): os.remove("risco_temporario.csv")
        if os.path.exists("churn_temporario.csv"): os.remove("churn_temporario.csv")
        st.rerun()
        
    st.info("💡 **Dica de Reporte:** Para exportar este painel, pressione `Ctrl + P` e escolha **Salvar como PDF**. O layout foi otimizado para isso!")

# =====================================================
# FUNÇÃO LEITURA E TRATAMENTO
# =====================================================
@st.cache_data
def load_data():
    df_risco = pd.DataFrame()
    df_churn = pd.DataFrame()
    
    # --- CARREGAR GESTÃO DE RISCOS ---
    if os.path.exists("risco_temporario.csv"):
        try: df_risco = pd.read_csv("risco_temporario.csv", sep=";", encoding="utf-8")
        except: df_risco = pd.read_excel("risco_temporario.csv")

    # --- CARREGAR CHURN ---
    if os.path.exists("churn_temporario.csv"):
        try: df_churn = pd.read_csv("churn_temporario.csv", sep=";", encoding="utf-8")
        except: df_churn = pd.read_excel("churn_temporario.csv")

    # --- LIMPEZA BÁSICA ---
    if not df_risco.empty:
        df_risco.columns = df_risco.columns.str.strip().str.replace("\n", "").str.replace("\r", "")
        # Adicione aqui os renomeios do risco conforme código anterior se precisar
        c_status_risco = next((c for c in df_risco.columns if 'status' in c.lower()), None)
        if c_status_risco: df_risco.rename(columns={c_status_risco: 'Status_Standard'}, inplace=True)

    if not df_churn.empty:
        df_churn.columns = df_churn.columns.str.strip().str.replace("\n", "").str.replace("\r", "")
        c_franquia_churn = next((c for c in df_churn.columns if 'franquia' in c.lower()), None)
        if c_franquia_churn: df_churn.rename(columns={c_franquia_churn: 'Franquia_Standard'}, inplace=True)
        
        c_grupo_churn = next((c for c in df_churn.columns if 'nome' in c.lower() and 'grupo' in c.lower()), None)
        if not c_grupo_churn: c_grupo_churn = next((c for c in df_churn.columns if 'empresa' in c.lower()), None)
        if c_grupo_churn: df_churn.rename(columns={c_grupo_churn: 'Grupo_Standard'}, inplace=True)
        
        c_qtd_canc = next((c for c in df_churn.columns if 'quantidade' in c.lower() and 'cancelamento' in c.lower()), None)
        if c_qtd_canc: df_churn.rename(columns={c_qtd_canc: 'Qtd_Cancelamentos_Standard'}, inplace=True)
        
        c_status_churn = next((c for c in df_churn.columns if 'status' in c.lower()), None)
        if c_status_churn: df_churn.rename(columns={c_status_churn: 'Status_Standard'}, inplace=True)

        c_data_churn = next((c for c in df_churn.columns if 'data' in c.lower()), None)
        if c_data_churn:
            df_churn['Data Base'] = pd.to_datetime(df_churn[c_data_churn], format='%d/%m/%Y', errors='coerce')
            df_churn['Data_Standard'] = df_churn['Data Base'].dt.strftime('%d/%m/%Y').fillna('N/A')

        if 'Qtd_Cancelamentos_Standard' in df_churn.columns:
            df_churn['Qtd_Cancelamentos_Standard'] = pd.to_numeric(df_churn['Qtd_Cancelamentos_Standard'], errors='coerce').fillna(1) # Default 1 se vazio
        
        # Cria colunas de backup caso não existam no CSV, para não quebrar a tela
        if 'Status_Standard' not in df_churn.columns: df_churn['Status_Standard'] = 'Pendente'
        if 'Grupo_Standard' not in df_churn.columns: df_churn['Grupo_Standard'] = 'Empresa N/A'
        if 'Franquia_Standard' not in df_churn.columns: df_churn['Franquia_Standard'] = 'Matriz'

    return df_risco, df_churn

def format_status(val):
    """Adiciona Emojis aos status para simular a bolinha colorida do design"""
    val_str = str(val).lower()
    if 'autorizado' in val_str or 'concluído' in val_str or 'ok' in val_str or 'aprovado' in val_str: 
        return f"🟢 {val}"
    elif 'pendente' in val_str or 'aguardando' in val_str or 'análise' in val_str: 
        return f"🟠 {val}"
    elif 'revertido' in val_str or 'retido' in val_str:
        return f"🔵 {val}"
    return f"⚪ {val}"

# =====================================================
# EXECUÇÃO DO APP
# =====================================================
try:
    df_risco, df_churn = load_data()

    tab1, tab2 = st.tabs(["📉 MONITOR DE CANCELAMENTOS", "⚠️ GESTÃO DE RISCO"])

    with tab1:
        if df_churn.empty:
            st.warning("⚠️ Faça o upload da base de **Churn** no menu lateral para visualizar o reporte.")
        else:
            # CABEÇALHO DO REPORTE
            hoje = datetime.now().strftime('%d/%m/%Y')
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 3px solid #0033A0; padding-bottom: 10px; margin-bottom: 20px;">
                <h1 style="color: #0033A0; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -1px;">MONITOR DE CANCELAMENTOS</h1>
                <div style="color: #64748B; font-size: 16px; font-weight: 500;">Reporte Diário • {hoje}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- FILTRO INVISÍVEL NA IMPRESSÃO ---
            st.markdown("<div style='margin-bottom: 10px; color:#64748B; font-size: 12px;'>Filtros de visualização (Ocultos ao exportar PDF)</div>", unsafe_allow_html=True)
            cf1, cf2 = st.columns(2)
            with cf1:
                datas = sorted(df_churn["Data_Standard"].unique(), reverse=True)
                filtro_data = st.multiselect("Filtrar Data Específica", datas, default=datas[0] if datas else None)
            
            churn_filtrado = df_churn[df_churn["Data_Standard"].isin(filtro_data)] if filtro_data else df_churn.copy()

            # --- CÁLCULOS DOS KPIS ---
            total_contratos = int(churn_filtrado['Qtd_Cancelamentos_Standard'].sum()) if 'Qtd_Cancelamentos_Standard' in churn_filtrado.columns else len(churn_filtrado)
            grupos_impactados = churn_filtrado['Grupo_Standard'].nunique()
            
            # Conta status para o painel de autorização
            status_counts = churn_filtrado['Status_Standard'].str.lower().value_counts()
            
            # Agrupa lógicas (Ajuste as palavras conforme o que vem no seu CSV)
            autorizados = status_counts[status_counts.index.str.contains('autorizado|aprovado|concluído|ok', na=False)].sum()
            pendentes = status_counts[status_counts.index.str.contains('pendente|aguardando|análise', na=False)].sum()
            
            total_tratados = autorizados + pendentes
            taxa_auth = int((autorizados / total_tratados * 100) if total_tratados > 0 else 0)
            taxa_pend = 100 - taxa_auth if total_tratados > 0 else 0

            # --- RENDERIZAÇÃO DOS CARTÕES HTML ---
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_contratos:02d}</div>
                    <div class="kpi-label">CONTRATOS SOLICITADOS</div>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{grupos_impactados:02d}</div>
                    <div class="kpi-label">GRUPOS IMPACTADOS</div>
                </div>
                """, unsafe_allow_html=True)
                
            with c3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color: #0033A0;">{taxa_auth}%</div>
                    <div class="kpi-label" style="margin-bottom:8px;">TAXA DE AUTORIZAÇÃO</div>
                    <div class="kpi-subtext">
                        <span class="pill-blue">{autorizados} Autorizados ({taxa_auth}%)</span>
                        <span class="pill-orange">{pendentes} Pendentes ({taxa_pend}%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- SEÇÃO INFERIOR: GRÁFICOS E TABELA ---
            col_esq, col_dir = st.columns([1, 1.8])

            with col_esq:
                st.markdown("<h4 style='color:#0033A0; margin-bottom:15px; font-size:18px;'>📑 Impacto por Franquia</h4>", unsafe_allow_html=True)
                
                df_franq = churn_filtrado.groupby('Franquia_Standard')['Qtd_Cancelamentos_Standard'].sum().reset_index()
                df_franq = df_franq.sort_values(by='Qtd_Cancelamentos_Standard', ascending=False).head(5)
                
                # Gráfico de Barras Minimalista simulando o Print
                fig_bar = px.bar(df_franq, x='Qtd_Cancelamentos_Standard', y='Franquia_Standard', orientation='h', text='Qtd_Cancelamentos_Standard')
                fig_bar.update_traces(marker_color='#0033A0', textposition='outside', textfont_size=12)
                fig_bar.update_layout(
                    height=280, 
                    margin=dict(l=0, r=20, t=0, b=0),
                    plot_bgcolor='white',
                    xaxis=dict(showgrid=False, showticklabels=False, title=""),
                    yaxis=dict(showgrid=False, title="", tickfont=dict(size=13, color="#1E293B"), categoryorder='total ascending')
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
                
                # Legenda inferior idêntica ao print
                st.markdown("""
                <div style="margin-top: 10px;">
                    <h4 style='color:#0033A0; font-size:16px; margin-bottom:8px;'>ℹ️ Próximas Ações</h4>
                    <div style="font-size: 13px; color: #64748B; line-height: 1.6;">
                        <span style="color:#15803D;">●</span> <b>Autorizado:</b> Agendar OS de Retirada<br>
                        <span style="color:#C2410C;">●</span> <b>Pendente:</b> Aguardando Avaliação
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_dir:
                st.markdown("<h4 style='color:#0033A0; margin-bottom:15px; font-size:18px;'>🗂️ Detalhe por Empresa do Dia</h4>", unsafe_allow_html=True)
                
                df_detalhe = churn_filtrado.copy()
                df_detalhe['Status_Display'] = df_detalhe['Status_Standard'].apply(format_status)
                
                cols_view = ['Grupo_Standard', 'Franquia_Standard', 'Qtd_Cancelamentos_Standard', 'Status_Display']
                df_view = df_detalhe[cols_view].rename(columns={
                    'Grupo_Standard': 'EMPRESA / GRUPO',
                    'Franquia_Standard': 'FRANQUIA',
                    'Qtd_Cancelamentos_Standard': 'CONTR.',
                    'Status_Display': 'STATUS'
                }).head(15) # Limita para caber no print da tela
                
                # Exibição usando o dataframe nativo otimizado para o tema light
                st.dataframe(
                    df_view, 
                    use_container_width=True, 
                    hide_index=True,
                    height=360
                )

    # Mantive a aba de Risco intacta caso precise depois
    with tab2:
        st.info("Aba de Risco preservada. Retorne ao Monitor de Cancelamentos para visualização do reporte.")

except Exception as e:
    st.error("Erro ao gerar o painel. Verifique o formato dos dados enviados.")
    st.exception(e)
