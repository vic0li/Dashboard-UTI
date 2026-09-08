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
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.analytics import processar_dados
from utils.risk_engine import processar_riscos


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Geral | UTI Intelligent Care",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PALETA DE CORES
# ============================================================

CORES = {

    "azul_escuro": "#12355B",
    "azul_principal": "#1F5F99",
    "azul_medio": "#4A90C2",
    "azul_claro": "#78B5DD",
    "azul_muito_claro": "#DCECF7",

    "branco": "#FFFFFF",

    "cinza_fundo": "#F5F7FA",
    "cinza_card": "#F8FAFC",

    "cinza_texto": "#64748B",
    "cinza_escuro": "#334155",

    "cinza_borda": "#E2E8F0",

    "verde": "#2E8B57",
    "laranja": "#E6A23C",
    "vermelho": "#D9534F"
}


PALETA_AZUL = [

    "#12355B",
    "#1F5F99",
    "#4A90C2",
    "#78B5DD",
    "#A8D0E6"

]


# ============================================================
# CSS PERSONALIZADO
# ============================================================

st.markdown(
    f"""

<style>

/* ========================================================= */
/* FUNDO PRINCIPAL */
/* ========================================================= */

.stApp {{
    background-color: {CORES["cinza_fundo"]};
}}


/* ========================================================= */
/* CONTAINER PRINCIPAL */
/* ========================================================= */

.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}}


/* ========================================================= */
/* TÍTULOS */
/* ========================================================= */

h1 {{
    color: {CORES["azul_escuro"]};
    font-weight: 700;
}}

h2 {{
    color: {CORES["azul_escuro"]};
}}

h3 {{
    color: {CORES["azul_escuro"]};
}}


/* ========================================================= */
/* SIDEBAR */
/* ========================================================= */

[data-testid="stSidebar"] {{
    background-color: {CORES["branco"]};
    border-right: 1px solid {CORES["cinza_borda"]};
}}


/* ========================================================= */
/* LABELS DOS FILTROS */
/* ========================================================= */

[data-testid="stSidebar"] label {{
    color: {CORES["azul_escuro"]} !important;
    font-weight: 600 !important;
}}


/* ========================================================= */
/* SELECTBOX */
/* ========================================================= */

[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: white;
    border-color: {CORES["cinza_borda"]};
    color: {CORES["cinza_escuro"]};
}}


/* TEXTO SELECIONADO SEMPRE VISÍVEL */

[data-testid="stSidebar"] div[data-baseweb="select"] span {{
    color: {CORES["cinza_escuro"]} !important;
    opacity: 1 !important;
}}


/* ========================================================= */
/* INPUT */
/* ========================================================= */

[data-testid="stSidebar"] input {{
    color: {CORES["cinza_escuro"]} !important;
    background-color: white !important;
}}


/* ========================================================= */
/* MÉTRICAS NATIVAS */
/* ========================================================= */

[data-testid="stMetric"] {{
    background-color: white;
    border: 1px solid {CORES["cinza_borda"]};
    border-radius: 12px;
    padding: 18px;
}}

[data-testid="stMetricLabel"] {{
    color: {CORES["cinza_texto"]};
    font-weight: 600;
}}

[data-testid="stMetricValue"] {{
    color: {CORES["azul_escuro"]};
    font-weight: 700;
}}


/* ========================================================= */
/* DIVISORES */
/* ========================================================= */

hr {{
    border-color: {CORES["cinza_borda"]};
}}


/* ========================================================= */
/* TABELAS */
/* ========================================================= */

[data-testid="stDataFrame"] {{
    background-color: white;
    border-radius: 10px;
}}


/* ========================================================= */
/* EXPANDERS */
/* ========================================================= */

.streamlit-expanderHeader {{
    background-color: white;
    border-radius: 8px;
    color: {CORES["azul_escuro"]};
    font-weight: 600;
}}


/* ========================================================= */
/* CARD PERSONALIZADO */
/* ========================================================= */

.kpi-card {{
    background-color: white;
    border: 1px solid {CORES["cinza_borda"]};
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;

    box-shadow:
        0px 2px 6px rgba(15, 23, 42, 0.04);
}}


.kpi-title {{
    font-size: 14px;
    color: {CORES["cinza_texto"]};
    font-weight: 600;
    margin-bottom: 10px;
}}


.kpi-value {{
    font-size: 30px;
    color: {CORES["azul_escuro"]};
    font-weight: 700;
}}


.kpi-subtitle {{
    font-size: 12px;
    color: {CORES["cinza_texto"]};
    margin-top: 5px;
}}


/* ========================================================= */
/* SEÇÃO */
/* ========================================================= */

.section-title {{
    font-size: 22px;
    font-weight: 700;
    color: {CORES["azul_escuro"]};
    margin-bottom: 4px;
}}


.section-subtitle {{
    font-size: 14px;
    color: {CORES["cinza_texto"]};
    margin-bottom: 20px;
}}


/* ========================================================= */
/* CARD DOS GRÁFICOS */
/* ========================================================= */

.chart-card {{
    background-color: white;
    border: 1px solid {CORES["cinza_borda"]};
    border-radius: 14px;
    padding: 15px;
}}

</style>

""",

    unsafe_allow_html=True
)


# ============================================================
# FUNÇÃO DE CONVERSÃO DO TIMESTAMP
# ============================================================

def converter_timestamp(serie):

    """
    Converte timestamps priorizando o formato:

    DD/MM/AAAA HH:MM

    Caso existam formatos alternativos na base,
    tenta uma conversão secundária utilizando dayfirst=True.
    """

    serie_original = serie.copy()

    # --------------------------------------------------------
    # PRIMEIRA TENTATIVA
    # FORMATO BRASILEIRO EXPLÍCITO
    # --------------------------------------------------------

    serie_convertida = pd.to_datetime(

        serie_original,

        format="%d/%m/%Y %H:%M",

        errors="coerce"

    )


    # --------------------------------------------------------
    # SEGUNDA TENTATIVA
    # FORMATO COM SEGUNDOS
    # --------------------------------------------------------

    mascara_invalida = serie_convertida.isna()

    if mascara_invalida.any():

        tentativa = pd.to_datetime(

            serie_original.loc[mascara_invalida],

            format="%d/%m/%Y %H:%M:%S",

            errors="coerce"

        )

        serie_convertida.loc[mascara_invalida] = tentativa


    # --------------------------------------------------------
    # TERCEIRA TENTATIVA
    # CONVERSÃO FLEXÍVEL COM DAYFIRST
    # --------------------------------------------------------

    mascara_invalida = serie_convertida.isna()

    if mascara_invalida.any():

        tentativa = pd.to_datetime(

            serie_original.loc[mascara_invalida],

            errors="coerce",

            dayfirst=True

        )

        serie_convertida.loc[mascara_invalida] = tentativa


    return serie_convertida


# ============================================================
# FUNÇÃO PARA FORMATAR DATA
# ============================================================

def formatar_timestamp(data):

    if pd.isna(data):

        return "N/D"

    return data.strftime("%d/%m/%Y %H:%M")


# ============================================================
# FUNÇÃO PARA OBTER ÚLTIMO REGISTRO
# ============================================================

def obter_ultimo_registro_por_paciente(dataframe):

    """
    Retorna uma visão consolidada contendo
    apenas o último registro disponível
    de cada paciente.
    """

    df_temp = dataframe.copy()


    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    if df_temp.empty:

        return df_temp


    if "id_paciente" not in df_temp.columns:

        return df_temp


    # --------------------------------------------------------
    # TRATAMENTO DO TIMESTAMP
    # --------------------------------------------------------

    if "timestamp" in df_temp.columns:

        df_temp["timestamp"] = converter_timestamp(
            df_temp["timestamp"]
        )


        # ----------------------------------------------------
        # ORDENA POR PACIENTE E TEMPO
        # ----------------------------------------------------

        df_temp = df_temp.sort_values(

            by=[
                "id_paciente",
                "timestamp"
            ],

            ascending=[
                True,
                True
            ]

        )


        # ----------------------------------------------------
        # MANTÉM ÚLTIMO REGISTRO
        # ----------------------------------------------------

        df_temp = (

            df_temp

            .groupby(
                "id_paciente",
                as_index=False
            )

            .tail(1)

        )


    else:

        # ----------------------------------------------------
        # CASO NÃO EXISTA TIMESTAMP
        # ----------------------------------------------------

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
# FUNÇÃO DE ESTILIZAÇÃO DOS GRÁFICOS
# ============================================================

def estilizar_grafico(

    fig,

    altura=360,

    mostrar_grid_x=True,

    mostrar_grid_y=False

):

    fig.update_layout(

        paper_bgcolor="white",

        plot_bgcolor="white",

        font=dict(

            family="Arial",

            color=CORES["cinza_escuro"]

        ),

        height=altura,

        margin=dict(

            t=40,

            b=30,

            l=30,

            r=30

        ),

        showlegend=False,

        hoverlabel=dict(

            bgcolor="white",

            font_color=CORES["cinza_escuro"]

        )

    )


    fig.update_xaxes(

        showgrid=mostrar_grid_x,

        gridcolor="#EEF2F6",

        zeroline=False,

        title=None

    )


    fig.update_yaxes(

        showgrid=mostrar_grid_y,

        gridcolor="#EEF2F6",

        zeroline=False,

        title=None

    )


    return fig


# ============================================================
# FUNÇÃO PARA CRIAR CARD KPI
# ============================================================

def criar_kpi(

    titulo,

    valor,

    subtitulo=""

):

    st.markdown(

        f"""

        <div class="kpi-card">

            <div class="kpi-title">
                {titulo}
            </div>

            <div class="kpi-value">
                {valor}
            </div>

            <div class="kpi-subtitle">
                {subtitulo}
            </div>

        </div>

        """,

        unsafe_allow_html=True

    )


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

try:

    df = load_data()


except Exception as e:

    st.error(
        "❌ Erro ao carregar os dados."
    )

    st.exception(e)

    st.stop()


# ============================================================
# VALIDAÇÃO DA BASE
# ============================================================

if df.empty:

    st.error(

        """
        ❌ A base de dados está vazia.

        Verifique o arquivo:

        `data/uti_simulada.csv`
        """

    )

    st.stop()


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
# GARANTIR TIMESTAMP CORRETO
# ============================================================

if "timestamp" in df.columns:

    df["timestamp"] = converter_timestamp(
        df["timestamp"]
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(

    """
    <div>

        <div style="
            font-size: 32px;
            font-weight: 750;
            color: #12355B;
            margin-bottom: 5px;
        ">
            📊 Dashboard Geral
        </div>

        <div style="
            font-size: 15px;
            color: #64748B;
        ">
            Visão integrada dos indicadores clínicos, riscos,
            alertas e prioridades da UTI.
        </div>

    </div>
    """,

    unsafe_allow_html=True

)


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(

    """
    <div style="
        font-size: 22px;
        font-weight: 700;
        color: #12355B;
        margin-bottom: 8px;
    ">
        🔍 Filtros
    </div>
    """,

    unsafe_allow_html=True

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

    placeholder="Ex: PAC-001"

)


# ============================================================
# FILTRO CLÍNICO
# ============================================================

if "classificacao_clinica" in df.columns:

    opcoes_clinicas = (

        ["Todas"]

        +

        sorted(

            df["classificacao_clinica"]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

    )

else:

    opcoes_clinicas = ["Todas"]


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

            df["classificacao_lpp"]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

    )

else:

    opcoes_lpp = ["Todas"]


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

            df["classificacao_prioridade"]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

    )

else:

    opcoes_prioridade = ["Todas"]


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

            df_filtrado["id_paciente"]

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

            df_filtrado["classificacao_clinica"]

            .astype(str)

            == filtro_clinico

        ]


# ============================================================
# FILTRO LPP
# ============================================================

if filtro_lpp != "Todas":

    if "classificacao_lpp" in df_filtrado.columns:

        df_filtrado = df_filtrado[

            df_filtrado["classificacao_lpp"]

            .astype(str)

            == filtro_lpp

        ]


# ============================================================
# FILTRO PRIORIDADE
# ============================================================

if filtro_prioridade != "Todas":

    if "classificacao_prioridade" in df_filtrado.columns:

        df_filtrado = df_filtrado[

            df_filtrado["classificacao_prioridade"]

            .astype(str)

            == filtro_prioridade

        ]


# ============================================================
# VERIFICAÇÃO
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
# VISÃO CONSOLIDADA POR PACIENTE
# ============================================================

df_pacientes = obter_ultimo_registro_por_paciente(
    df_filtrado
)


# ============================================================
# SITUAÇÃO GERAL
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)


st.markdown(

    """
    <div class="section-title">
        📌 Situação Geral
    </div>

    <div class="section-subtitle">
        Indicadores baseados na situação mais recente
        de cada paciente.
    </div>
    """,

    unsafe_allow_html=True

)


# ============================================================
# CÁLCULOS DOS KPIs
# ============================================================

if "id_paciente" in df_pacientes.columns:

    pacientes = df_pacientes["id_paciente"].nunique()

else:

    pacientes = len(df_pacientes)


# SCORE CLÍNICO

if "score_clinico" in df_pacientes.columns:

    score_medio = df_pacientes["score_clinico"].mean()

    score_medio_formatado = f"{score_medio:.1f}"

else:

    score_medio_formatado = "N/D"


# SCORE LPP

if "score_lpp" in df_pacientes.columns:

    lpp_medio = df_pacientes["score_lpp"].mean()

    lpp_medio_formatado = f"{lpp_medio:.1f}"

else:

    lpp_medio_formatado = "N/D"


# ALERTAS

if (

    "quantidade_alertas" in df_pacientes.columns

    and

    "id_paciente" in df_pacientes.columns

):

    pacientes_com_alerta = (

        df_pacientes[
            df_pacientes["quantidade_alertas"] > 0
        ]

        ["id_paciente"]

        .nunique()

    )

else:

    pacientes_com_alerta = "N/D"


# ============================================================
# CARDS KPI
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    criar_kpi(

        "👥 Pacientes",

        pacientes,

        "Pacientes únicos"

    )


with col2:

    criar_kpi(

        "🩺 Score Clínico Médio",

        score_medio_formatado,

        "Situação clínica atual"

    )


with col3:

    criar_kpi(

        "🩹 Score LPP Médio",

        lpp_medio_formatado,

        "Risco médio identificado"

    )


with col4:

    criar_kpi(

        "⚠️ Pacientes com Alertas",

        pacientes_com_alerta,

        "Necessitam atenção"

    )


# ============================================================
# INFORMAÇÕES DA BASE
# ============================================================

st.markdown("<br><br>", unsafe_allow_html=True)


st.markdown(

    """
    <div class="section-title">
        🕒 Informações da Base
    </div>

    <div class="section-subtitle">
        Resumo dos registros temporais disponíveis
        após a aplicação dos filtros.
    </div>
    """,

    unsafe_allow_html=True

)


# ============================================================
# CÁLCULOS
# ============================================================

total_registros = len(df_filtrado)

total_pacientes = len(df_pacientes)


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

        df_filtrado["timestamp"]

        .dropna()

    )


    if not timestamps_validos.empty:

        inicio = timestamps_validos.min()

        fim = timestamps_validos.max()


        periodo_formatado = (

            f"{inicio.strftime('%d/%m/%Y %H:%M')}"

            "<br>"

            f"{fim.strftime('%d/%m/%Y %H:%M')}"

        )


# ============================================================
# CARDS DE INFORMAÇÃO
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    criar_kpi(

        "📊 Registros Filtrados",

        f"{total_registros:,}".replace(",", "."),

        "Registros temporais"

    )


with col2:

    criar_kpi(

        "👥 Pacientes Únicos",

        total_pacientes,

        "Última situação disponível"

    )


with col3:

    criar_kpi(

        "⏱️ Registros / Paciente",

        f"{media_registros:.1f}",

        "Média de acompanhamentos"

    )


with col4:

    criar_kpi(

        "📅 Período",

        periodo_formatado,

        "DD/MM/AAAA HH:MM"

    )


# ============================================================
# DISTRIBUIÇÃO DE RISCOS
# ============================================================

st.markdown("<br><br>", unsafe_allow_html=True)


st.markdown(

    """
    <div class="section-title">
        ⚠️ Distribuição de Riscos
    </div>

    <div class="section-subtitle">
        Distribuição baseada na situação mais recente
        de cada paciente.
    </div>
    """,

    unsafe_allow_html=True

)


col1, col2 = st.columns(2)


# ============================================================
# CLASSIFICAÇÃO CLÍNICA
# ============================================================

with col1:

    st.markdown(
        '<div class="chart-card">',
        unsafe_allow_html=True
    )


    st.markdown(
        "### 🩺 Classificação Clínica"
    )


    if "classificacao_clinica" in df_pacientes.columns:


        df_clinica_counts = (

            df_pacientes["classificacao_clinica"]

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

            color_discrete_sequence=PALETA_AZUL

        )


        fig_clinica.update_traces(

            textposition="outside",

            marker_line_width=0

        )


        fig_clinica = estilizar_grafico(
            fig_clinica
        )


        st.plotly_chart(

            fig_clinica,

            use_container_width=True,

            key="grafico_clinica_geral"

        )


    else:

        st.warning(
            "Classificação clínica não disponível."
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# CLASSIFICAÇÃO LPP
# ============================================================

with col2:

    st.markdown(
        '<div class="chart-card">',
        unsafe_allow_html=True
    )


    st.markdown(
        "### 🩹 Risco de Lesão por Pressão"
    )


    if "classificacao_lpp" in df_pacientes.columns:


        df_lpp_counts = (

            df_pacientes["classificacao_lpp"]

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

            color_discrete_sequence=PALETA_AZUL

        )


        fig_lpp.update_traces(

            textposition="outside",

            marker_line_width=0

        )


        fig_lpp = estilizar_grafico(
            fig_lpp
        )


        st.plotly_chart(

            fig_lpp,

            use_container_width=True,

            key="grafico_lpp_geral"

        )


    else:

        st.warning(
            "Classificação de LPP não disponível."
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# DISTRIBUIÇÃO DA PRIORIDADE
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)


st.markdown(

    """
    <div class="section-title">
        🎯 Distribuição da Prioridade
    </div>

    <div class="section-subtitle">
        Classificação dos pacientes de acordo com
        o índice de prioridade calculado.
    </div>
    """,

    unsafe_allow_html=True

)


if "classificacao_prioridade" in df_pacientes.columns:


    df_prioridade_counts = (

        df_pacientes["classificacao_prioridade"]

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
            CORES["azul_principal"]
        ]

    )


    fig_prioridade.update_traces(

        textposition="outside"

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
        "Classificação de prioridade não disponível."
    )


# ============================================================
# MOTIVOS DE INTERNAÇÃO
# ============================================================

# Procura automaticamente uma coluna correspondente

possiveis_colunas_motivo = [

    "motivo_internacao",

    "motivo_de_internacao",

    "Motivo de Internação",

    "motivo",

    "diagnostico",

    "diagnóstico"

]


coluna_motivo = None


for coluna in possiveis_colunas_motivo:

    if coluna in df_pacientes.columns:

        coluna_motivo = coluna

        break


# ============================================================
# GRÁFICO HORIZONTAL
# ============================================================

if coluna_motivo is not None:


    st.markdown("<br>", unsafe_allow_html=True)


    st.markdown(

        """
        <div class="section-title">
            🏥 Motivos de Internação
        </div>

        <div class="section-subtitle">
            Principais motivos registrados para internação.
        </div>
        """,

        unsafe_allow_html=True

    )


    df_motivos = (

        df_pacientes[coluna_motivo]

        .dropna()

        .astype(str)

        .value_counts()

        .reset_index()

    )


    df_motivos.columns = [

        "Motivo",

        "Quantidade"

    ]


    # Ordenação para barras horizontais

    df_motivos = df_motivos.sort_values(
        "Quantidade",
        ascending=True
    )


    fig_motivos = px.bar(

        df_motivos,

        x="Quantidade",

        y="Motivo",

        orientation="h",

        text="Quantidade",

        color_discrete_sequence=[
            CORES["azul_principal"]
        ]

    )


    fig_motivos.update_traces(

        textposition="outside",

        cliponaxis=False,

        marker=dict(

            line=dict(
                width=0
            )

        )

    )


    fig_motivos.update_layout(

        paper_bgcolor="white",

        plot_bgcolor="white",

        height=430,

        margin=dict(

            t=30,

            b=30,

            l=30,

            r=60

        ),

        showlegend=False

    )


    fig_motivos.update_xaxes(

        showgrid=True,

        gridcolor="#EEF2F6",

        zeroline=False,

        title=None

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


# ============================================================
# SITUAÇÃO ATUAL DOS PACIENTES
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)


st.markdown(

    """
    <div class="section-title">
        🚨 Situação Atual dos Pacientes
    </div>

    <div class="section-subtitle">
        Último registro disponível de cada paciente,
        ordenado por prioridade.
    </div>
    """,

    unsafe_allow_html=True

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
# ORDENAÇÃO
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

    df_exibicao = df_pacientes.copy()


# ============================================================
# FORMATAÇÃO DO TIMESTAMP PARA EXIBIÇÃO
# ============================================================

if "timestamp" in df_exibicao.columns:

    df_exibicao["timestamp"] = (

        df_exibicao["timestamp"]

        .apply(formatar_timestamp)

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
        "Nenhum paciente encontrado."
    )


# ============================================================
# HISTÓRICO TEMPORAL
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)


st.markdown(

    """
    <div class="section-title">
        🕒 Histórico de Registros
    </div>

    <div class="section-subtitle">
        Visualização completa dos registros temporais
        após a aplicação dos filtros.
    </div>
    """,

    unsafe_allow_html=True

)


with st.expander(

    "Visualizar histórico completo filtrado",

    expanded=False

):


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


    df_historico = df_filtrado.copy()


    # --------------------------------------------------------
    # ORDENAÇÃO
    # --------------------------------------------------------

    if "timestamp" in df_historico.columns:

        df_historico = (

            df_historico

            .sort_values(

                by="timestamp",

                ascending=False

            )

        )


        # ----------------------------------------------------
        # FORMATAÇÃO VISUAL
        # ----------------------------------------------------

        df_historico["timestamp"] = (

            df_historico["timestamp"]

            .apply(formatar_timestamp)

        )


    # --------------------------------------------------------
    # TABELA
    # --------------------------------------------------------

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

        .replace(",", ".")

    )


# ============================================================
# DIAGNÓSTICO TÉCNICO
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)


with st.expander(

    "🔬 Status e Diagnóstico Técnico",

    expanded=False

):


    st.markdown(
        "### Estrutura dos dados"
    )


    st.write(

        f"**Registros totais da base:** "

        f"{len(df):,}"

        .replace(",", ".")

    )


    st.write(

        f"**Registros após filtros:** "

        f"{len(df_filtrado):,}"

        .replace(",", ".")

    )


    st.write(

        f"**Pacientes únicos após filtros:** "

        f"{len(df_pacientes):,}"

        .replace(",", ".")

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


    st.markdown(
        "### Colunas disponíveis"
    )


    st.write(
        list(df.columns)
    )


# ============================================================
# AVISO ACADÊMICO
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)


st.info(

    """
    ⚠️ **Protótipo acadêmico**

    Este dashboard utiliza dados totalmente simulados
    para fins de demonstração, modelagem e desenvolvimento
    de uma arquitetura conceitual de apoio à decisão em UTI.

    Os scores, alertas e classificações possuem finalidade
    educacional e não devem ser utilizados para decisões
    clínicas reais.
    """

)
