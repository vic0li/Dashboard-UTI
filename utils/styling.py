
import streamlit as st

def aplicar_estilo():
    st.markdown(
        """
        <style>
        :root{
            --bg:#EEF4F8;
            --surface:#FFFFFF;
            --surface-soft:#F7FAFC;
            --nav:#0F3553;
            --nav-2:#164B6A;
            --ink:#0D2A45;
            --ink-soft:#3F5F78;
            --muted:#6F8798;
            --border:#D8E4EC;
            --accent:#1F6EA5;
            --accent-soft:#EAF4FA;
            --cyan:#48A9D6;
            --success:#159A7A;
            --danger:#E5484D;
            --warning:#F4A62A;
            --purple:#8257D8;
        }

        html, body, [class*="css"]{
            font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }

        html{
            font-size: 20px !important;
        }

        .stApp{
            background:
                radial-gradient(circle at 0% 0%, rgba(92,165,205,.12), transparent 26%),
                linear-gradient(180deg,#F6FAFD 0%, var(--bg) 100%) !important;
            color:var(--ink)!important;
        }

        .main .block-container{
            max-width: 1540px !important;
            padding: 1.2rem 1.4rem 3rem !important;
        }

        header[data-testid="stHeader"]{
            background: rgba(246,250,253,.94)!important;
            border-bottom:1px solid var(--border)!important;
            backdrop-filter: blur(10px);
        }

        #MainMenu{visibility:hidden;}
        footer{visibility:hidden;}

        /* REMOVE COMPLETELY THE NATIVE STREAMLIT SIDEBAR */
        section[data-testid="stSidebar"]{
            display:none !important;
            width:0 !important;
            min-width:0 !important;
            max-width:0 !important;
        }

        [data-testid="stSidebarCollapsedControl"],
        button[data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarExpandButton"]{
            display:none !important;
        }

        /* Let main content use the full viewport width */
        [data-testid="stAppViewContainer"] > .main{
            margin-left:0 !important;
        }


        /* GLOBAL TYPOGRAPHY */
        h1{
            font-size:48px!important;
            line-height:1.1!important;
            font-weight:800!important;
            letter-spacing:-.035em!important;
            color:var(--ink)!important;
        }
        h2{
            font-size:40px!important;
            line-height:1.2!important;
            font-weight:800!important;
            color:var(--ink)!important;
        }
        h3{
            font-size:28px!important;
            line-height:1.25!important;
            font-weight:750!important;
            color:var(--ink)!important;
        }
        p, .stMarkdown, label, span{
            font-size:18px;
        }
        div[data-testid="stCaptionContainer"] p{
            font-size:17px!important;
            color:var(--muted)!important;
            line-height:1.55!important;
        }

        /* TOP PRODUCT BAR */
        .product-bar{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:24px;
            background:rgba(255,255,255,.98);
            border:1px solid var(--border);
            border-radius:14px;
            padding:14px 18px;
            margin-bottom:12px;
            box-shadow:0 8px 24px rgba(18,55,82,.06);
        }
        .brand-wrap{
            display:flex;
            align-items:center;
            gap:12px;
        }
        .brand-mark{
            width:44px;
            height:44px;
            border-radius:12px;
            display:grid;
            place-items:center;
            font-weight:800;
            font-size:17px;
            color:#fff;
            background:linear-gradient(135deg,var(--nav),var(--accent));
            box-shadow:0 6px 16px rgba(22,75,106,.22);
        }
        .brand-name{
            font-size:23px!important;
            font-weight:800!important;
            color:var(--ink)!important;
            line-height:1.1;
        }
        .brand-sub{
            font-size:13px!important;
            letter-spacing:.11em;
            text-transform:uppercase;
            color:var(--muted)!important;
            margin-top:3px;
        }
        .env-pill{
            display:inline-flex;
            align-items:center;
            gap:8px;
            border:1px solid var(--border);
            background:var(--surface-soft);
            color:var(--ink-soft);
            border-radius:999px;
            padding:8px 12px;
            font-size:15px!important;
            font-weight:650;
        }

        /* NAVEGAÇÃO SUPERIOR NATIVA DO STREAMLIT */
        [data-testid="stPageLink"]{
            width:100% !important;
        }

        [data-testid="stPageLink"] a{
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            min-height:50px !important;
            width:100% !important;
            padding:0 14px !important;

            text-decoration:none !important;

            border:1px solid #D9E5ED !important;
            border-radius:11px !important;

            background:rgba(255,255,255,.58) !important;

            color:var(--ink) !important;
            font-size:18px !important;
            font-weight:750 !important;

            box-shadow:0 1px 2px rgba(18,55,82,.025) !important;
            transition:all .18s ease !important;
        }

        [data-testid="stPageLink"] a:hover{
            background:#F4F9FC !important;
            border-color:#B9CFDE !important;
            color:var(--nav) !important;
            box-shadow:0 3px 10px rgba(31,110,165,.07) !important;
            transform:translateY(-1px);
        }

        /* Página atual: st.page_link disabled */
        [data-testid="stPageLink"] a[aria-disabled="true"],
        [data-testid="stPageLink"] button:disabled{
            background:linear-gradient(180deg,#2A77AA 0%,#1B5C88 100%) !important;
            color:#FFFFFF !important;
            border:1px solid #1B5C88 !important;
            box-shadow:0 5px 14px rgba(31,110,165,.18) !important;
            opacity:1 !important;
            transform:none !important;
        }

        /* Espaçamento da linha de navegação */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stPageLink"]){
            gap:8px !important;
            margin-bottom:18px !important;
        }

        /* HERO */
        .hero-container{
            border-radius:16px!important;
            overflow:hidden;
            background:
                radial-gradient(circle at 92% 10%, rgba(255,255,255,.08), transparent 28%),
                linear-gradient(110deg, #153F5C 0%, #174B67 55%, #1E6078 100%)!important;
            border:1px solid rgba(13,42,69,.15)!important;
            box-shadow:0 14px 34px rgba(22,55,80,.12)!important;
            margin-bottom:18px!important;
        }
        .hero-main{
            display:grid;
            grid-template-columns:1.2fr .9fr;
            gap:30px;
            padding:30px 34px 28px;
            color:white!important;
        }
        .hero-kicker{
            font-size:15px!important;
            font-weight:800!important;
            letter-spacing:.12em;
            text-transform:uppercase;
            color:#B9E5F6!important;
            margin-bottom:10px;
        }
        .hero-title{
            font-size:48px!important;
            line-height:1.12!important;
            font-weight:850!important;
            letter-spacing:-.04em;
            color:#fff!important;
            max-width:760px;
        }
        .hero-subtitle{
            margin-top:14px;
            max-width:760px;
            font-size:20px!important;
            line-height:1.55!important;
            color:#E8F3F8!important;
        }
        .hero-side{
            border-left:1px solid rgba(255,255,255,.26);
            padding-left:26px;
            display:grid;
            gap:16px;
            align-content:center;
        }
        .hero-side-item{
            display:grid;
            grid-template-columns:40px 1fr;
            gap:12px;
            align-items:start;
        }
        .hero-side-icon{
            width:40px;
            height:40px;
            border-radius:50%;
            display:grid;
            place-items:center;
            background:rgba(255,255,255,.12);
            font-size:20px!important;
        }
        .hero-side-title{
            color:#fff!important;
            font-size:19px!important;
            font-weight:800!important;
            margin-bottom:3px;
        }
        .hero-side-text{
            color:#DCEBF2!important;
            font-size:17px!important;
            line-height:1.4!important;
        }

        /* SECTION HEADERS */
        .section-heading{
            display:flex;
            align-items:center;
            gap:10px;
            font-size:30px!important;
            font-weight:850!important;
            color:var(--ink)!important;
            margin:20px 0 8px;
            letter-spacing:-.02em;
        }
        .section-subtitle{
            font-size:18px!important;
            color:var(--muted)!important;
            margin-bottom:14px;
        }

        /* KPI / METRICS */
        div[data-testid="stMetric"]{
            background:rgba(255,255,255,.98)!important;
            border:1px solid var(--border)!important;
            border-radius:14px!important;
            padding:18px 18px 16px!important;
            min-height:132px!important;
            box-shadow:0 8px 22px rgba(18,55,82,.06)!important;
        }
        div[data-testid="stMetricLabel"] p{
            font-size:18px!important;
            color:var(--ink-soft)!important;
            font-weight:750!important;
        }
        div[data-testid="stMetricValue"]{
            font-size:40px!important;
            line-height:1.1!important;
            font-weight:850!important;
            color:#071B2E!important;
            letter-spacing:-.03em!important;
        }
        div[data-testid="stMetricDelta"]{
            font-size:17px!important;
            font-weight:700!important;
        }

        .kpi-card,.dashboard-card,.clinical-card,.card{
            background:rgba(255,255,255,.98)!important;
            border:1px solid var(--border)!important;
            border-radius:14px!important;
            box-shadow:0 8px 22px rgba(18,55,82,.06)!important;
        }
        .kpi-card{
            min-height:132px;
            padding:18px;
        }
        .kpi-title{
            font-size:18px!important;
            font-weight:750!important;
            color:var(--ink-soft)!important;
        }
        .kpi-value{
            margin-top:8px;
            font-size:40px!important;
            line-height:1.1!important;
            font-weight:850!important;
            color:#071B2E!important;
        }

        /* PLOTLY AND TABLES */
        div[data-testid="stPlotlyChart"]{
            background:rgba(255,255,255,.98)!important;
            border:1px solid var(--border)!important;
            border-radius:14px!important;
            padding:8px!important;
            box-shadow:0 8px 22px rgba(18,55,82,.06)!important;
        }
        div[data-testid="stDataFrame"]{
            border:1px solid var(--border)!important;
            border-radius:14px!important;
            overflow:hidden!important;
            box-shadow:0 8px 22px rgba(18,55,82,.06)!important;
        }

        /* INPUTS */
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input{
            min-height:48px!important;
            background:#fff!important;
            border:1px solid #C8D8E4!important;
            border-radius:10px!important;
            box-shadow:none!important;
            font-size:18px!important;
        }
        div[data-baseweb="select"] *{
            font-size:18px!important;
            color:var(--ink)!important;
        }
        .stButton > button,
        .stDownloadButton > button{
            min-height:48px!important;
            border-radius:10px!important;
            background:linear-gradient(180deg,#2A77AA 0%, #1B5C88 100%)!important;
            border:0!important;
            color:#fff!important;
            font-size:18px!important;
            font-weight:800!important;
            padding:0 18px!important;
            box-shadow:0 5px 14px rgba(31,110,165,.18)!important;
        }

        details[data-testid="stExpander"]{
            background:#fff!important;
            border:1px solid var(--border)!important;
            border-radius:12px!important;
        }


        /* ESCALA TIPOGRÁFICA AMPLIADA */
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown td,
        .stMarkdown th {
            font-size:18px !important;
            line-height:1.55 !important;
        }

        div[data-testid="stDataFrame"] {
            font-size:17px !important;
        }

        div[data-testid="stDataFrame"] * {
            font-size:17px !important;
        }

        .stSelectbox label,
        .stMultiSelect label,
        .stTextInput label,
        .stNumberInput label,
        .stDateInput label,
        .stRadio label,
        .stCheckbox label {
            font-size:18px !important;
            font-weight:650 !important;
        }

        button[data-baseweb="tab"] p {
            font-size:18px !important;
            font-weight:700 !important;
        }

        details[data-testid="stExpander"] summary p {
            font-size:18px !important;
            font-weight:700 !important;
        }

        @media(max-width:1100px){
            .top-nav{grid-template-columns:repeat(4,1fr);}
            .hero-main{grid-template-columns:1fr;}
            .hero-side{border-left:0;border-top:1px solid rgba(255,255,255,.22);padding-left:0;padding-top:20px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def topo_produto():
    st.markdown(
        """
        <div class="product-bar">
            <div class="brand-wrap">
                <div class="brand-mark">UIC</div>
                <div>
                    <div class="brand-name">UTI Intelligent Care</div>
                    <div class="brand-sub">Clinical Intelligence Platform</div>
                </div>
            </div>
            <div class="env-pill">● Ambiente demonstrativo · Dados simulados</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def navegacao_topo(ativo="Início"):
    """
    Navegação superior usando o sistema nativo de páginas do Streamlit.
    Isso evita links quebrados e mantém a sidebar completamente oculta.
    """
    paginas = [
        ("Início", "app.py"),
        ("Visão geral", "pages/1_Dashboard_Geral.py"),
        ("Monitoramento", "pages/2_Monitoramento_Clinico.py"),
        ("LPP", "pages/3_Gestao_LPP.py"),
        ("Operacional", "pages/4_Gestao_Operacional.py"),
        ("Alertas", "pages/5_Central_de_Alertas.py"),
        ("Lean", "pages/7_Lean_Healthcare.py"),
    ]

    colunas = st.columns(len(paginas), gap="small")

    for coluna, (nome, caminho) in zip(colunas, paginas):
        with coluna:
            st.page_link(
                caminho,
                label=nome,
                use_container_width=True,
                disabled=(nome == ativo),
            )


def navegacao_superior(ativo="Início"):
    """Compatibilidade com páginas antigas; usa somente a navegação superior."""
    navegacao_topo(ativo)


def cabecalho_pagina(titulo, subtitulo, secao="UTI Intelligent Care", badge="Dados simulados"):
    st.markdown(
        f"""
        <div style="margin:8px 0 16px;">
            <div style="font-size:15px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:#1F6EA5;margin-bottom:5px;">{secao}</div>
            <div style="font-size:34px;font-weight:850;letter-spacing:-.03em;color:#0D2A45;line-height:1.15;">{titulo}</div>
            <div style="font-size:17px;line-height:1.5;color:#6F8798;margin-top:7px;max-width:980px;">{subtitulo}</div>
        </div>
        """, unsafe_allow_html=True
    )

def card(titulo, valor, icone=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{icone + " " if icone else ""}{titulo}</div>
            <div class="kpi-value">{valor}</div>
        </div>
        """, unsafe_allow_html=True
    )

def alerta(mensagem, nivel="normal"):
    cores = {
        "critico":("#FDECEC","#C9363E"),
        "alto":("#FFF2E7","#CC6D19"),
        "moderado":("#FFF7DA","#9E7410"),
        "normal":("#EAF8F3","#147D65"),
    }
    bg, fg = cores.get(nivel, cores["normal"])
    st.markdown(
        f'<div style="background:{bg};border:1px solid {fg}33;border-left:4px solid {fg};padding:14px 16px;border-radius:10px;color:#0D2A45;font-size:18px;">{mensagem}</div>',
        unsafe_allow_html=True
    )

def hero_home():
    st.markdown(
        """
        <div class="hero-container">
          <div class="hero-main">
            <div>
              <div class="hero-kicker">UTI Intelligent Care · Clinical Intelligence</div>
              <div class="hero-title">Visão integrada para decisões assistenciais mais rápidas e consistentes</div>
              <div class="hero-subtitle">
                Monitoramento de risco clínico, prevenção de lesão por pressão e priorização assistencial
                em uma interface única, construída sobre dados simulados para fins acadêmicos.
              </div>
            </div>
            <div class="hero-side">
              <div class="hero-side-item">
                <div class="hero-side-icon">◈</div>
                <div><div class="hero-side-title">Risco de LPP</div><div class="hero-side-text">Estratificação de risco para apoiar medidas preventivas.</div></div>
              </div>
              <div class="hero-side-item">
                <div class="hero-side-icon">▥</div>
                <div><div class="hero-side-title">Tendência clínica</div><div class="hero-side-text">Leitura temporal de sinais e escores.</div></div>
              </div>
              <div class="hero-side-item">
                <div class="hero-side-icon">●</div>
                <div><div class="hero-side-title">Gestão assistencial</div><div class="hero-side-text">Indicadores consolidados para organizar prioridades da equipe.</div></div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True
    )
