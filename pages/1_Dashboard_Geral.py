# ============================================================
# DASHBOARD GERAL
# UTI INTELLIGENT CARE
#
# Visão integrada dos indicadores clínicos, risco de LPP,
# alertas e priorização de pacientes.
#
# IMPORTANTE:
# - A base possui registros temporais
# - Um mesmo paciente pode aparecer diversas vezes
#
# Por isso:
# - KPIs utilizam pacientes únicos
# - Gráficos utilizam o último registro de cada paciente
# - Histórico mantém os registros temporais
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.analytics import processar_dados
from utils.risk_engine import processar_riscos
from utils.styling import aplicar_estilo


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Geral | UTI Intelligent Care",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# ESTILO BASE
# ============================================================

aplicar_estilo()


# ============================================================
# AJUSTES VISUAIS COMPLEMENTARES
#
# Visual padronizado com a página:
# MONITORAMENTO CLÍNICO
#
# Fundo claro
# Sidebar azul
# KPIs profissionais
# Gráficos em tons de azul
# ============================================================

st.markdown(
    """
    <style>

    /* =======================================================
    FUNDO PRINCIPAL
    ======================================================= */

    .stApp {
        background-color: #F7F9FC !important;
        color: #1F2937 !important;
    }

    .main {
        background-color: #F7F9FC !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }


    /* =======================================================
    TEXTOS
    ======================================================= */

    h1,
    h2,
    h3 {
        color: #1E3A5F !important;
    }

    p,
    span,
    label,
    .stMarkdown,
    .stMarkdown p {
        color: #374151;
    }


    /* =======================================================
    SIDEBAR
    ======================================================= */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #1E3A5F 0%,
            #274C77 100%
        ) !important;

        border-right: 1px solid #D1D5DB;
    }


    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }


    /* =======================================================
    INPUT DE BUSCA
    ======================================================= */

    section[data-testid="stSidebar"] input {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;

        -webkit-text-fill-color: #1F2937 !important;

        border: 1px solid #93C5FD !important;

        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] input::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
    }


    /* =======================================================
    SELECTBOX
    ======================================================= */

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {

        background-color: #FFFFFF !important;

        border: 1px solid #93C5FD !important;

        border-radius: 8px !important;
    }


    section[data-testid="stSidebar"]
    div[data-baseweb="select"] * {

        color: #1F2937 !important;
    }


    section[data-testid="stSidebar"]
    div[data-baseweb="select"] svg {

        fill: #2563EB !important;
    }


    /* =======================================================
    MENU DO SELECTBOX
    ======================================================= */

    div[role="listbox"] {

        background-color: #FFFFFF !important;

        border: 1px solid #93C5FD !important;
    }


    div[role="option"] {

        background-color: #FFFFFF !important;

        color: #1F2937 !important;
    }


    div[role="option"] * {

        color: #1F2937 !important;
    }


    div[role="option"]:hover {

        background-color: #EFF6FF !important;

        color: #1E3A5F !important;
    }


    /* =======================================================
    KPIs / MÉTRICAS
    ======================================================= */

    div[data-testid="stMetric"] {

        background-color: #FFFFFF !important;

        border: 1px solid #D1D5DB !important;

        border-left: 4px solid #2563EB !important;

        border-radius: 10px !important;

        padding: 16px !important;

        box-shadow:
            0 2px 8px rgba(
                31,
                41,
                55,
                0.08
            );
    }


    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {

        color: #4B5563 !important;

        font-weight: 600 !important;
    }


    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] div {

        color: #1E3A5F !important;

        font-weight: 700 !important;
    }


    /* =======================================================
    EXPANDERS
    ======================================================= */

    details {

        background-color: #FFFFFF !important;

        border: 1px solid #D1D5DB !important;

        border-radius: 10px !important;
    }


    details summary {

        color: #1E3A5F !important;

        font-weight: 600 !important;
    }


    /* =======================================================
    ALERTAS
    ======================================================= */

    div[data-testid="stAlert"] {

        border-radius: 10px;
    }


    /* =======================================================
    DIVISORES
    ======================================================= */

    hr {

        border-color: #D1D5DB !important;
    }


    /* =======================================================
    DATAFRAME
    ======================================================= */

    div[data-testid="stDataFrame"] {

        border: 1px solid #D1D5DB;

        border-radius: 8px;

        overflow: hidden;

        background-color: #FFFFFF;
    }


    /* =======================================================
    GRÁFICOS
    ======================================================= */

    div[data-testid="stPlotlyChart"] {

        background-color: #FFFFFF;

        border-radius: 10px;
    }


    /* =======================================================
    BOTÕES
    ======================================================= */

    .stButton > button {

        background-color: #2563EB !important;

        color: #FFFFFF !important;

        border: 1px solid #1D4ED8 !important;

        border-radius: 8px !important;
    }


    .stButton > button:hover {

        background-color: #1D4ED8 !important;

        color: #FFFFFF !important;
    }


    /* =======================================================
    SIDEBAR DIVIDER
    ======================================================= */

    section[data-testid="stSidebar"] hr {

        border-color: rgba(
            255,
            255,
            255,
            0.25
        ) !important;
    }


    /* =======================================================
    CAPTION DA SIDEBAR
    ======================================================= */

    section[data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {

        color: #DCE6F2 !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] p {

        color: #DCE6F2 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PALETA DE CORES
#
# Tons padronizados de azul para manter consistência visual
# ============================================================

AZUL_ESCURO = "#12355B"

AZUL_PRINCIPAL = "#0B5CAD"

AZUL_MEDIO = "#1677C8"

AZUL_CLARO = "#4FA3E3"

AZUL_MUITO_CLARO = "#8CCAF0"

AZUL_SUAVE = "#E7F2FB"

CINZA_TEXTO = "#4B5563"

CINZA_GRID = "#E5E7EB"


PALETA_AZUL = [

    "#1E3A5F",

    "#2563EB",

    "#3B82F6",

    "#60A5FA",

    "#93C5FD"

]


# ============================================================
# FUNÇÃO DE CONVERSÃO DO TIMESTAMP
# ============================================================

def converter_timestamp(serie):

    """
    Converte timestamps priorizando o formato:

    DD/MM/AAAA HH:MM

    Também aceita:

    DD/MM/AAAA HH:MM:SS

    Caso existam formatos alternativos,
    realiza uma tentativa adicional
    utilizando dayfirst=True.
    """

    serie_original = (
        serie
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # PRIMEIRA TENTATIVA
    #
    # DD/MM/AAAA HH:MM
    # ========================================================

    serie_convertida = pd.to_datetime(

        serie_original,

        format="%d/%m/%Y %H:%M",

        errors="coerce"

    )


    # ========================================================
    # SEGUNDA TENTATIVA
    #
    # DD/MM/AAAA HH:MM:SS
    # ========================================================

    mascara_invalida = (
        serie_convertida
        .isna()
    )


    if mascara_invalida.any():

        tentativa = pd.to_datetime(

            serie_original.loc[
                mascara_invalida
            ],

            format="%d/%m/%Y %H:%M:%S",

            errors="coerce"

        )


        serie_convertida.loc[
            mascara_invalida
        ] = tentativa


    # ========================================================
    # TERCEIRA TENTATIVA
    #
    # CONVERSÃO FLEXÍVEL
    # ========================================================

    mascara_invalida = (
        serie_convertida
        .isna()
    )


    if mascara_invalida.any():

        tentativa = pd.to_datetime(

            serie_original.loc[
                mascara_invalida
            ],

            errors="coerce",

            dayfirst=True

        )


        serie_convertida.loc[
            mascara_invalida
        ] = tentativa


    return serie_convertida


# ============================================================
# FUNÇÃO PARA FORMATAR TIMESTAMP
# ============================================================

def formatar_timestamp(data):

    if pd.isna(data):

        return "N/D"


    return data.strftime(
        "%d/%m/%Y %H:%M"
    )


# ============================================================
# FUNÇÃO PARA OBTER O ÚLTIMO REGISTRO
# DE CADA PACIENTE
# ============================================================

def obter_ultimo_registro_por_paciente(dataframe):

    """
    Retorna apenas o último registro temporal
    disponível para cada paciente.
    """

    df_temp = dataframe.copy()


    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    if df_temp.empty:

        return df_temp


    if "id_paciente" not in df_temp.columns:

        return df_temp


    # ========================================================
    # TIMESTAMP
    # ========================================================

    if "timestamp" in df_temp.columns:


        df_temp["timestamp"] = converter_timestamp(

            df_temp["timestamp"]

        )


        # ====================================================
        # REMOVE TIMESTAMPS INVÁLIDOS
        # ====================================================

        df_temp = df_temp.dropna(

            subset=[
                "timestamp"
            ]

        )


        # ====================================================
        # ORDENAÇÃO
        # ====================================================

        df_temp = (

            df_temp

            .sort_values(

                [
                    "id_paciente",
                    "timestamp"
                ]

            )

            .copy()

        )


        # ====================================================
        # ÚLTIMO REGISTRO
        # ====================================================

        df_temp = (

            df_temp

            .groupby(

                "id_paciente",

                as_index=False

            )

            .tail(1)

        )


    else:


        # ====================================================
        # CASO NÃO EXISTA TIMESTAMP
        # ====================================================

        df_temp = (

            df_temp

            .groupby(

                "id_paciente",

                as_index=False

            )

            .tail(1)

        )


    return df_temp


# ============================================================
# FUNÇÃO PARA PADRONIZAR OS GRÁFICOS
# ============================================================

def estilizar_grafico(

    fig,

    altura=350,

    mostrar_grid_x=True,

    mostrar_grid_y=True

):


    # ========================================================
    # LAYOUT
    # ========================================================

    fig.update_layout(

        paper_bgcolor="#FFFFFF",

        plot_bgcolor="#FFFFFF",

        font=dict(

            family="Arial",

            color="#374151"

        ),

        height=altura,

        margin=dict(

            l=20,

            r=20,

            t=50,

            b=30

        ),

        hoverlabel=dict(

            bgcolor="#FFFFFF",

            font_color="#1F2937"

        ),

        showlegend=False

    )


    # ========================================================
    # EIXO X
    # ========================================================

    fig.update_xaxes(

        showgrid=mostrar_grid_x,

        gridcolor=CINZA_GRID,

        zeroline=False,

        title=None

    )


    # ========================================================
    # EIXO Y
    # ========================================================

    fig.update_yaxes(

        showgrid=mostrar_grid_y,

        gridcolor=CINZA_GRID,

        zeroline=False,

        title=None

    )


    return fig


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

try:

    df = load_data()


except Exception as e:

    st.error(
        "❌ Não foi possível carregar os dados."
    )

    st.exception(e)

    st.stop()


# ============================================================
# VALIDAÇÃO DA BASE
# ============================================================

if df.empty:

    st.error(
        "❌ A base de dados está vazia."
    )

    st.stop()


# ============================================================
# VALIDAÇÃO DO TIMESTAMP
# ============================================================

if "timestamp" not in df.columns:

    st.error(
        "❌ A coluna 'timestamp' não foi encontrada."
    )

    st.stop()


# ============================================================
# PRESERVAÇÃO DO TIMESTAMP ORIGINAL
# ============================================================

df["timestamp_original"] = (

    df["timestamp"]

    .astype(str)

    .str.strip()

)


# ============================================================
# CONVERSÃO CORRETA DO TIMESTAMP
#
# Formato principal da base:
#
# DD/MM/AAAA HH:MM
#
# Isso impede interpretações incorretas como:
#
# MM/DD/AAAA
# ============================================================

df["timestamp"] = converter_timestamp(

    df["timestamp_original"]

)


# ============================================================
# QUANTIDADE DE TIMESTAMPS INVÁLIDOS
# ============================================================

quantidade_timestamps_invalidos = (

    df["timestamp"]

    .isna()

    .sum()

)


# ============================================================
# REMOÇÃO DE TIMESTAMPS INVÁLIDOS
# ============================================================

df = df.dropna(

    subset=[
        "timestamp"
    ]

)


# ============================================================
# VALIDAÇÃO
# ============================================================

if df.empty:

    st.error(
        """
        ❌ Não existem timestamps válidos na base.

        O formato esperado é:

        DD/MM/AAAA HH:MM

        Exemplo:

        07/09/2026 20:00
        """
    )

    st.stop()


# ============================================================
# ORDENAÇÃO TEMPORAL INICIAL
# ============================================================

df = (

    df

    .sort_values(
        "timestamp"
    )

    .copy()

)


# ============================================================
# PROCESSAMENTO ANALÍTICO
# ============================================================

try:

    df = processar_dados(df)


except Exception as e:

    st.error(
        "❌ Erro no processamento analítico."
    )

    st.exception(e)

    st.stop()


# ============================================================
# MOTOR DE RISCO
# ============================================================

try:

    df = processar_riscos(df)


except Exception as e:

    st.error(
        "❌ Erro no motor de risco."
    )

    st.exception(e)

    st.stop()


# ============================================================
# ORDENAÇÃO FINAL
# ============================================================

df = (

    df

    .sort_values(
        "timestamp"
    )

    .copy()

)


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Dashboard Geral"
)


st.caption(
    """
    Visão integrada dos indicadores clínicos,
    riscos, alertas e prioridades dos pacientes
    da UTI.
    """
)


st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "🔍 Filtros"
)


st.sidebar.caption(
    """
    Utilize os filtros abaixo para atualizar
    automaticamente todos os indicadores,
    gráficos e tabelas.
    """
)


st.sidebar.divider()


# ============================================================
# BUSCA POR PACIENTE
# ============================================================

busca_paciente = st.sidebar.text_input(

    "🔎 Buscar paciente",

    placeholder="Ex: 1 ou PAC-001"

)


# ============================================================
# FILTRO CLÍNICO
# ============================================================

if "classificacao_clinica" in df.columns:


    opcoes_clinicas = (

        ["Todas"]

        +

        sorted(

            df[
                "classificacao_clinica"
            ]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

    )


else:

    opcoes_clinicas = [
        "Todas"
    ]


filtro_clinico = st.sidebar.selectbox(

    "🩺 Situação Clínica",

    options=opcoes_clinicas

)


# ============================================================
# FILTRO LPP
# ============================================================

if "classificacao_lpp" in df.columns:


    opcoes_lpp = (

        ["Todas"]

        +

        sorted(

            df[
                "classificacao_lpp"
            ]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

    )


else:

    opcoes_lpp = [
        "Todas"
    ]


filtro_lpp = st.sidebar.selectbox(

    "🩹 Risco de LPP",

    options=opcoes_lpp

)


# ============================================================
# FILTRO PRIORIDADE
# ============================================================

if "classificacao_prioridade" in df.columns:


    opcoes_prioridade = (

        ["Todas"]

        +

        sorted(

            df[
                "classificacao_prioridade"
            ]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

    )


else:

    opcoes_prioridade = [
        "Todas"
    ]


filtro_prioridade = st.sidebar.selectbox(

    "🎯 Prioridade",

    options=opcoes_prioridade

)


# ============================================================
# FILTROS ATIVOS
# ============================================================

st.sidebar.divider()


st.sidebar.subheader(
    "📌 Filtros Ativos"
)


filtros_ativos = []


if busca_paciente.strip():

    filtros_ativos.append(

        f"Paciente: {busca_paciente}"

    )


if filtro_clinico != "Todas":

    filtros_ativos.append(

        f"Clínico: {filtro_clinico}"

    )


if filtro_lpp != "Todas":

    filtros_ativos.append(

        f"LPP: {filtro_lpp}"

    )


if filtro_prioridade != "Todas":

    filtros_ativos.append(

        f"Prioridade: {filtro_prioridade}"

    )


if filtros_ativos:


    for filtro in filtros_ativos:

        st.sidebar.markdown(

            f"🔹 **{filtro}**"

        )


else:

    st.sidebar.caption(
        "Nenhum filtro aplicado."
    )


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()


# ============================================================
# BUSCA POR PACIENTE
# ============================================================

if busca_paciente.strip():

    if "id_paciente" in df_filtrado.columns:


        df_filtrado = df_filtrado[

            df_filtrado[
                "id_paciente"
            ]

            .astype(str)

            .str.contains(

                busca_paciente.strip(),

                case=False,

                na=False

            )

        ]


# ============================================================
# FILTRO CLÍNICO
# ============================================================

if filtro_clinico != "Todas":

    if "classificacao_clinica" in df_filtrado.columns:


        df_filtrado = df_filtrado[

            df_filtrado[
                "classificacao_clinica"
            ]

            .astype(str)

            == filtro_clinico

        ]


# ============================================================
# FILTRO LPP
# ============================================================

if filtro_lpp != "Todas":

    if "classificacao_lpp" in df_filtrado.columns:


        df_filtrado = df_filtrado[

            df_filtrado[
                "classificacao_lpp"
            ]

            .astype(str)

            == filtro_lpp

        ]


# ============================================================
# FILTRO PRIORIDADE
# ============================================================

if filtro_prioridade != "Todas":

    if "classificacao_prioridade" in df_filtrado.columns:


        df_filtrado = df_filtrado[

            df_filtrado[
                "classificacao_prioridade"
            ]

            .astype(str)

            == filtro_prioridade

        ]


# ============================================================
# VALIDAÇÃO DOS FILTROS
# ============================================================

if df_filtrado.empty:

    st.warning(
        """
        ⚠️ Nenhum registro foi encontrado
        para os filtros selecionados.
        """
    )


    st.info(
        "Altere ou remova algum filtro para visualizar os dados."
    )

    st.stop()


# ============================================================
# VISÃO CONSOLIDADA
#
# Último registro de cada paciente
# ============================================================

df_pacientes = (

    obter_ultimo_registro_por_paciente(
        df_filtrado
    )

)


# ============================================================
# SITUAÇÃO GERAL
# ============================================================

st.subheader(
    "📌 Situação Geral"
)


st.caption(
    """
    Indicadores baseados na situação mais recente
    disponível de cada paciente.
    """
)


# ============================================================
# PACIENTES ÚNICOS
# ============================================================

if "id_paciente" in df_pacientes.columns:

    pacientes = (

        df_pacientes[
            "id_paciente"
        ]

        .nunique()

    )


else:

    pacientes = len(
        df_pacientes
    )


# ============================================================
# SCORE CLÍNICO
# ============================================================

if "score_clinico" in df_pacientes.columns:

    score_medio = (

        df_pacientes[
            "score_clinico"
        ]

        .mean()

    )


    score_medio_formatado = (

        f"{score_medio:.1f}"

        if pd.notna(score_medio)

        else "N/D"

    )


else:

    score_medio_formatado = "N/D"


# ============================================================
# SCORE LPP
# ============================================================

if "score_lpp" in df_pacientes.columns:

    lpp_medio = (

        df_pacientes[
            "score_lpp"
        ]

        .mean()

    )


    lpp_medio_formatado = (

        f"{lpp_medio:.1f}"

        if pd.notna(lpp_medio)

        else "N/D"

    )


else:

    lpp_medio_formatado = "N/D"


# ============================================================
# PACIENTES COM ALERTAS
# ============================================================

if (

    "quantidade_alertas" in df_pacientes.columns

    and

    "id_paciente" in df_pacientes.columns

):


    pacientes_com_alerta = (

        df_pacientes[

            df_pacientes[
                "quantidade_alertas"
            ] > 0

        ][
            "id_paciente"
        ]

        .nunique()

    )


else:

    pacientes_com_alerta = "N/D"


# ============================================================
# KPIs
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(

        "👥 Pacientes",

        pacientes

    )


with col2:

    st.metric(

        "🩺 Score Clínico Médio",

        score_medio_formatado

    )


with col3:

    st.metric(

        "🩹 Score LPP Médio",

        lpp_medio_formatado

    )


with col4:

    st.metric(

        "⚠️ Pacientes com Alertas",

        pacientes_com_alerta

    )


# ============================================================
# INFORMAÇÕES DA BASE
# ============================================================

st.divider()


st.subheader(
    "🕒 Informações da Base"
)


st.caption(
    """
    Resumo dos registros temporais disponíveis
    após a aplicação dos filtros.
    """
)


# ============================================================
# CÁLCULOS
# ============================================================

total_registros = len(
    df_filtrado
)


total_pacientes = len(
    df_pacientes
)


if total_pacientes > 0:

    media_registros = (

        total_registros

        /

        total_pacientes

    )


else:

    media_registros = 0


# ============================================================
# PERÍODO
# ============================================================

periodo_formatado = "N/D"


if "timestamp" in df_filtrado.columns:


    timestamps_validos = (

        df_filtrado[
            "timestamp"
        ]

        .dropna()

    )


    if not timestamps_validos.empty:


        inicio = timestamps_validos.min()

        fim = timestamps_validos.max()


        periodo_formatado = (

            f"{inicio.strftime('%d/%m/%Y %H:%M')}"

            "\n"

            f"até {fim.strftime('%d/%m/%Y %H:%M')}"

        )


# ============================================================
# KPIs DA BASE
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(

        "📊 Registros Filtrados",

        f"{total_registros:,}".replace(
            ",",
            "."
        )

    )


with col2:

    st.metric(

        "👥 Pacientes Únicos",

        total_pacientes

    )


with col3:

    st.metric(

        "⏱️ Registros / Paciente",

        f"{media_registros:.1f}"

    )


with col4:

    st.metric(

        "📅 Período",

        periodo_formatado

    )


# ============================================================
# DISTRIBUIÇÃO DE RISCOS
# ============================================================

st.divider()


st.header(
    "⚠️ Distribuição de Riscos"
)


st.caption(
    """
    Distribuição baseada na situação mais recente
    disponível de cada paciente.
    """
)


col1, col2 = st.columns(2)


# ============================================================
# CLASSIFICAÇÃO CLÍNICA
# ============================================================

with col1:


    st.subheader(
        "🩺 Classificação Clínica"
    )


    if "classificacao_clinica" in df_pacientes.columns:


        df_clinica_counts = (

            df_pacientes[
                "classificacao_clinica"
            ]

            .value_counts()

            .reset_index()

        )


        df_clinica_counts.columns = [

            "Classificação",

            "Quantidade"

        ]


        fig_clinica = px.bar(

            df_clinica_counts,

            x="Classificação",

            y="Quantidade",

            text="Quantidade",

            color_discrete_sequence=[
                AZUL_PRINCIPAL
            ]

        )


        fig_clinica.update_traces(

            textposition="outside",

            cliponaxis=False,

            marker_line_width=0

        )


        fig_clinica = estilizar_grafico(

            fig_clinica,

            altura=350

        )


        st.plotly_chart(

            fig_clinica,

            use_container_width=True,

            key="grafico_clinica_geral"

        )


    else:

        st.warning(
            "⚠️ Classificação clínica não disponível."
        )


# ============================================================
# CLASSIFICAÇÃO LPP
# ============================================================

with col2:


    st.subheader(
        "🩹 Risco de Lesão por Pressão"
    )


    if "classificacao_lpp" in df_pacientes.columns:


        df_lpp_counts = (

            df_pacientes[
                "classificacao_lpp"
            ]

            .value_counts()

            .reset_index()

        )


        df_lpp_counts.columns = [

            "Classificação",

            "Quantidade"

        ]


        fig_lpp = px.bar(

            df_lpp_counts,

            x="Classificação",

            y="Quantidade",

            text="Quantidade",

            color_discrete_sequence=[
                AZUL_MEDIO
            ]

        )


        fig_lpp.update_traces(

            textposition="outside",

            cliponaxis=False,

            marker_line_width=0

        )


        fig_lpp = estilizar_grafico(

            fig_lpp,

            altura=350

        )


        st.plotly_chart(

            fig_lpp,

            use_container_width=True,

            key="grafico_lpp_geral"

        )


    else:

        st.warning(
            "⚠️ Classificação de LPP não disponível."
        )


# ============================================================
# DISTRIBUIÇÃO DA PRIORIDADE
# ============================================================

st.divider()


st.header(
    "🎯 Distribuição da Prioridade"
)


st.caption(
    """
    Classificação dos pacientes de acordo com
    o índice de prioridade calculado.
    """
)


if "classificacao_prioridade" in df_pacientes.columns:


    df_prioridade_counts = (

        df_pacientes[
            "classificacao_prioridade"
        ]

        .value_counts()

        .reset_index()

    )


    df_prioridade_counts.columns = [

        "Prioridade",

        "Quantidade"

    ]


    fig_prioridade = px.bar(

        df_prioridade_counts,

        x="Prioridade",

        y="Quantidade",

        text="Quantidade",

        color_discrete_sequence=[
            AZUL_PRINCIPAL
        ]

    )


    fig_prioridade.update_traces(

        textposition="outside",

        cliponaxis=False,

        marker_line_width=0

    )


    fig_prioridade = estilizar_grafico(

        fig_prioridade,

        altura=360

    )


    st.plotly_chart(

        fig_prioridade,

        use_container_width=True,

        key="grafico_prioridade_geral"

    )


else:

    st.warning(
        "⚠️ Classificação de prioridade não disponível."
    )


# ============================================================
# MOTIVOS DE INTERNAÇÃO / DIAGNÓSTICO INICIAL
# ============================================================
# Gráfico baseado na situação mais recente de cada paciente.
# A coluna principal utilizada é "diagnostico_inicial".
# ============================================================

COLUNA_DIAGNOSTICO_INICIAL = "diagnostico_principal"

st.divider()

st.header(
    "🏥 Motivos de Internação"
)

st.caption(
    "Distribuição dos diagnósticos iniciais dos pacientes, considerando o último registro disponível de cada paciente."
)

if COLUNA_DIAGNOSTICO_INICIAL in df_pacientes.columns:

    df_motivos = (
        df_pacientes[
            COLUNA_DIAGNOSTICO_INICIAL
        ]
        .dropna()
        .astype(str)
        .str.strip()
    )

    df_motivos = df_motivos[
        df_motivos != ""
    ]

    if not df_motivos.empty:

        df_motivos = (
            df_motivos
            .value_counts()
            .reset_index()
        )

        df_motivos.columns = [
            "Diagnóstico Inicial",
            "Quantidade"
        ]

        total_motivos = df_motivos["Quantidade"].sum()

        df_motivos["Porcentagem"] = (
            df_motivos["Quantidade"]
            / total_motivos
            * 100
        ).round(1)

        df_motivos["Rótulo"] = (
            df_motivos["Quantidade"].astype(str)
            + " ("
            + df_motivos["Porcentagem"].map(
                lambda valor: f"{valor:.1f}%".replace(".", ",")
            )
            + ")"
        )

        # Ordenação crescente para que o maior valor fique no topo
        df_motivos = (
            df_motivos
            .sort_values(
                "Quantidade",
                ascending=True
            )
        )

        # Paleta azul mais sofisticada e com melhor contraste visual
        cores_motivos = [
            "#0F3D5E",
            "#145DA0",
            "#1E81B0",
            "#2E8BC0",
            "#4DA8DA",
            "#7CC4E4",
            "#A9D6E5"
        ]

        cores_barras = [
            cores_motivos[i % len(cores_motivos)]
            for i in range(len(df_motivos))
        ]

        fig_motivos = px.bar(
            df_motivos,
            x="Quantidade",
            y="Diagnóstico Inicial",
            orientation="h",
            text="Rótulo",
            custom_data=["Porcentagem"]
        )

        fig_motivos.update_traces(
            textposition="outside",
            cliponaxis=False,
            marker_color=cores_barras,
            marker_line_color="#FFFFFF",
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Pacientes: %{x}<br>"
                "Percentual: %{customdata[0]:.1f}%"
                "<extra></extra>"
            )
        )

        fig_motivos.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            height=max(
                380,
                len(df_motivos) * 58
            ),
            margin=dict(
                l=20,
                r=100,
                t=20,
                b=40
            ),
            showlegend=False,
            font=dict(
                family="Arial",
                color="#374151"
            )
        )

        fig_motivos.update_xaxes(
            showgrid=True,
            gridcolor="#E8EEF5",
            zeroline=False,
            title="Quantidade de pacientes"
        )

        fig_motivos.update_yaxes(
            showgrid=False,
            title=None
        )

        st.plotly_chart(
            fig_motivos,
            use_container_width=True,
            key="grafico_motivos_internacao"
        )

        st.caption(
            "💡 Os rótulos mostram **quantidade de pacientes (percentual do total)**."
        )

    else:

        st.warning(
            "⚠️ Não há valores válidos em 'diagnostico_inicial'."
        )

else:

    st.warning(
        "⚠️ A coluna 'diagnostico_inicial' não foi encontrada na base de dados."
    )


# ============================================================
# SITUAÇÃO ATUAL DOS PACIENTES
# ============================================================

st.divider()


st.header(
    "🚨 Situação Atual dos Pacientes"
)


st.caption(
    """
    Último registro disponível de cada paciente,
    ordenado por índice de prioridade.
    """
)


# ============================================================
# COLUNAS
# ============================================================

colunas_pacientes = [

    "id_paciente",

    "timestamp",

    "score_clinico",

    "classificacao_clinica",

    "score_lpp",

    "classificacao_lpp",

    "quantidade_alertas",

    "indice_prioridade",

    "classificacao_prioridade"

]


colunas_validas = [

    coluna

    for coluna in colunas_pacientes

    if coluna in df_pacientes.columns

]


# ============================================================
# ORDENAÇÃO POR PRIORIDADE
# ============================================================

if (

    not df_pacientes.empty

    and

    "indice_prioridade" in df_pacientes.columns

):


    df_exibicao = (

        df_pacientes

        .sort_values(

            by="indice_prioridade",

            ascending=False

        )

        .copy()

    )


else:

    df_exibicao = (

        df_pacientes

        .copy()

    )


# ============================================================
# FORMATAÇÃO DO TIMESTAMP
# ============================================================

if "timestamp" in df_exibicao.columns:


    df_exibicao["timestamp"] = (

        df_exibicao[
            "timestamp"
        ]

        .apply(
            formatar_timestamp
        )

    )


# ============================================================
# EXIBIÇÃO
# ============================================================

if not df_exibicao.empty:


    st.dataframe(

        df_exibicao[
            colunas_validas
        ],

        use_container_width=True,

        hide_index=True

    )


else:

    st.warning(
        "⚠️ Nenhum paciente encontrado."
    )


# ============================================================
# HISTÓRICO TEMPORAL
# ============================================================

st.divider()


st.header(
    "🕒 Histórico de Registros"
)


st.caption(
    """
    Visualização completa dos registros temporais
    após a aplicação dos filtros.
    """
)


with st.expander(

    "📋 Visualizar histórico completo filtrado",

    expanded=False

):


    # ========================================================
    # COLUNAS
    # ========================================================

    colunas_historico = [

        "id_paciente",

        "timestamp",

        "score_clinico",

        "classificacao_clinica",

        "score_lpp",

        "classificacao_lpp",

        "quantidade_alertas",

        "indice_prioridade",

        "classificacao_prioridade"

    ]


    colunas_historico_validas = [

        coluna

        for coluna in colunas_historico

        if coluna in df_filtrado.columns

    ]


    # ========================================================
    # CÓPIA
    # ========================================================

    df_historico = (

        df_filtrado

        .copy()

    )


    # ========================================================
    # ORDENAÇÃO
    # ========================================================

    if "timestamp" in df_historico.columns:


        df_historico = (

            df_historico

            .sort_values(

                "timestamp",

                ascending=False

            )

        )


        # ====================================================
        # FORMATAÇÃO
        # ====================================================

        df_historico["timestamp"] = (

            df_historico[
                "timestamp"
            ]

            .apply(
                formatar_timestamp
            )

        )


    # ========================================================
    # TABELA
    # ========================================================

    st.dataframe(

        df_historico[
            colunas_historico_validas
        ],

        use_container_width=True,

        hide_index=True

    )


    st.caption(

        f"Total de registros históricos: "

        f"{len(df_historico):,}"

        .replace(
            ",",
            "."
        )

    )


# ============================================================
# DIAGNÓSTICO TÉCNICO
# ============================================================

st.divider()


with st.expander(

    "🛠️ Status e Diagnóstico Técnico",

    expanded=False

):


    # ========================================================
    # ESTRUTURA
    # ========================================================

    st.subheader(
        "📊 Estrutura dos dados"
    )


    st.write(

        f"**Registros totais da base:** "

        f"{len(df):,}"

        .replace(
            ",",
            "."
        )

    )


    st.write(

        f"**Registros após filtros:** "

        f"{len(df_filtrado):,}"

        .replace(
            ",",
            "."
        )

    )


    st.write(

        f"**Pacientes únicos após filtros:** "

        f"{len(df_pacientes):,}"

        .replace(
            ",",
            "."
        )

    )


    if len(df_pacientes) > 0:


        media = (

            len(df_filtrado)

            /

            len(df_pacientes)

        )


        st.write(

            f"**Média de registros por paciente:** "

            f"{media:.2f}"

        )


    # ========================================================
    # TIMESTAMP
    # ========================================================

    st.subheader(
        "🕒 Diagnóstico temporal"
    )


    st.success(
        "✓ Timestamp processado priorizando o formato DD/MM/AAAA HH:MM"
    )


    if quantidade_timestamps_invalidos == 0:


        st.success(
            "✓ Nenhum timestamp inválido encontrado"
        )


    else:


        st.warning(

            f"⚠️ Foram encontrados "

            f"{quantidade_timestamps_invalidos} "

            f"timestamps inválidos."

        )


    # ========================================================
    # PERÍODO
    # ========================================================

    if "timestamp" in df.columns:


        data_min = (

            df[
                "timestamp"
            ]

            .min()

        )


        data_max = (

            df[
                "timestamp"
            ]

            .max()

        )


        st.write(

            f"**Período total da base:** "

            f"{formatar_timestamp(data_min)} "

            f"até "

            f"{formatar_timestamp(data_max)}"

        )


    # ========================================================
    # TIPO DO TIMESTAMP
    # ========================================================

    st.subheader(
        "🔬 Tipo da coluna timestamp"
    )


    st.code(

        str(
            df[
                "timestamp"
            ].dtype
        )

    )


    # ========================================================
    # COLUNAS
    # ========================================================

    st.subheader(
        "📋 Colunas disponíveis"
    )


    st.write(
        list(df.columns)
    )


    # ========================================================
    # AMOSTRA TEMPORAL
    # ========================================================

    st.subheader(
        "🧪 Amostra dos registros temporais"
    )


    colunas_diagnostico = [

        "id_paciente",

        "timestamp_original",

        "timestamp"

    ]


    colunas_diagnostico = [

        coluna

        for coluna in colunas_diagnostico

        if coluna in df.columns

    ]


    st.dataframe(

        df[
            colunas_diagnostico
        ]

        .head(15),

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# AVISO ACADÊMICO
# ============================================================

st.divider()


st.info(

    """
    ⚠️ **Protótipo acadêmico**

    Os dados apresentados nesta página são totalmente simulados
    e possuem finalidade exclusivamente educacional e conceitual.

    Os indicadores, scores, alertas e classificações apresentados
    não constituem um sistema clínico validado e não devem ser
    utilizados para tomada de decisão clínica real.
    """

)
