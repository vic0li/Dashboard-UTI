# ============================================================
# MONITORAMENTO CLÍNICO
# UTI INTELLIGENT CARE
#
# Página dedicada à análise temporal dos indicadores
# clínicos simulados.
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

    page_title="Monitoramento Clínico | UTI Intelligent Care",

    page_icon="🩺",

    layout="wide"

)


# ============================================================
# ESTILO
# ============================================================

aplicar_estilo()


# ============================================================
# AJUSTES VISUAIS COMPLEMENTARES
# Visual limpo, branco, cinza e azul
# Compatível com modo claro e escuro
# ============================================================

st.markdown(
    """
    <style>

    /* =======================================================
       FUNDO PRINCIPAL
       Fundo branco e visual clínico/profissional
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
    }

    /* =======================================================
       TEXTOS
    ======================================================= */

    h1, h2, h3 {
        color: #1E3A5F !important;
    }

    p, span, label,
    .stMarkdown,
    .stMarkdown p {
        color: #374151;
    }

    /* =======================================================
       SIDEBAR
       Azul profissional com alto contraste
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
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* =======================================================
       SELECTBOX
       Campo branco + texto escuro sempre visível
    ======================================================= */

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #93C5FD !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] * {
        color: #1F2937 !important;
    }

    div[data-baseweb="select"] svg {
        fill: #2563EB !important;
    }

    /* Valor selecionado */
    div[data-baseweb="select"] input {
        color: #1F2937 !important;
        -webkit-text-fill-color: #1F2937 !important;
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
       DATE INPUT
    ======================================================= */

    div[data-testid="stDateInput"] input {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        -webkit-text-fill-color: #1F2937 !important;
        border: 1px solid #93C5FD !important;
        border-radius: 8px !important;
    }

    div[data-testid="stDateInput"] svg {
        fill: #2563EB !important;
    }

    /* =======================================================
       KPI / MÉTRICAS
       Mantém exatamente o layout original
    ======================================================= */

    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-left: 4px solid #2563EB !important;
        border-radius: 10px !important;
        padding: 16px !important;
        box-shadow: 0 2px 8px rgba(31, 41, 55, 0.08);
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

    </style>
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
# VALIDAÇÃO DA COLUNA TIMESTAMP
# ============================================================

if "timestamp" not in df.columns:

    st.error(
        "❌ A coluna 'timestamp' não foi encontrada."
    )

    st.stop()


# ============================================================
# PRESERVAÇÃO DO TIMESTAMP ORIGINAL
# ============================================================

# Mantém uma cópia do valor original.
#
# Isso facilita o diagnóstico caso exista algum problema
# com o formato da data.

df["timestamp_original"] = (

    df["timestamp"]

    .astype(str)

    .str.strip()

)


# ============================================================
# PROCESSAMENTO CORRETO DO TIMESTAMP
# ============================================================

# IMPORTANTE:
#
# A base simulada utiliza:
#
# DD/MM/AAAA HH:MM
#
# Exemplo:
#
# 07/09/2026 20:00
#
# O formato é definido explicitamente para impedir
# interpretações automáticas como:
#
# MM/DD/AAAA


df["timestamp"] = pd.to_datetime(

    df["timestamp_original"],

    format="%d/%m/%Y %H:%M",

    errors="coerce"

)


# ============================================================
# VERIFICAÇÃO DE DATAS INVÁLIDAS
# ============================================================

quantidade_timestamps_invalidos = (

    df["timestamp"]

    .isna()

    .sum()

)


# ============================================================
# REMOÇÃO DE DATAS INVÁLIDAS
# ============================================================

df = df.dropna(

    subset=[

        "timestamp"

    ]

)


# ============================================================
# VALIDAÇÃO APÓS CONVERSÃO
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
# ORDENAÇÃO TEMPORAL
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
# PERÍODO TOTAL DA BASE
# ============================================================

data_min = (

    df["timestamp"]

    .min()

)


data_max = (

    df["timestamp"]

    .max()

)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🩺 Monitoramento Clínico"
)


st.caption(

    """
    Acompanhamento temporal individual dos indicadores
    clínicos simulados dos pacientes da UTI.
    """

)


st.divider()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header(
    "🔍 Monitoramento"
)


# ============================================================
# FILTRO DE PACIENTE
# ============================================================

if "id_paciente" not in df.columns:

    st.error(
        "❌ A coluna 'id_paciente' não foi encontrada."
    )

    st.stop()


# Garante que os IDs sejam tratados como números
df["id_paciente"] = pd.to_numeric(
    df["id_paciente"],
    errors="coerce"
)

# Lista fixa e ordenada de pacientes: 1 até 26
lista_pacientes = list(range(1, 27))


if not lista_pacientes:

    st.error(
        "❌ Nenhum paciente encontrado na base."
    )

    st.stop()


paciente_selecionado = st.sidebar.selectbox(

    "Selecionar paciente",

    lista_pacientes

)


# ============================================================
# DADOS DO PACIENTE SELECIONADO
# ============================================================

df_paciente = (

    df[

        df[
            "id_paciente"
        ]

        == paciente_selecionado

    ]

    .copy()

)


# ============================================================
# VALIDAÇÃO DO PACIENTE
# ============================================================

if df_paciente.empty:

    st.error(
        "❌ Não foram encontrados registros para este paciente."
    )

    st.stop()


# ============================================================
# PERÍODO DISPONÍVEL DO PACIENTE
# ============================================================

data_min_paciente = (

    df_paciente[
        "timestamp"
    ]

    .min()

)


data_max_paciente = (

    df_paciente[
        "timestamp"
    ]

    .max()

)


# ============================================================
# FILTRO DE PERÍODO
# ============================================================

st.sidebar.divider()


st.sidebar.subheader(
    "📅 Período"
)


periodo = st.sidebar.date_input(

    "Período de análise",

    value=(

        data_min_paciente.date(),

        data_max_paciente.date()

    ),

    min_value=data_min_paciente.date(),

    max_value=data_max_paciente.date()

)


# ============================================================
# DATAFRAME DO MONITORAMENTO
# ============================================================

df_monitoramento = (

    df_paciente

    .copy()

)


# ============================================================
# FILTRO DE PERÍODO
# ============================================================

if isinstance(

    periodo,

    tuple

) and len(periodo) == 2:


    data_inicio = pd.Timestamp(

        periodo[0]

    )


    # ========================================================
    # DATA FINAL
    # ========================================================

    # Utiliza o final do dia selecionado.

    data_fim = (

        pd.Timestamp(

            periodo[1]

        )

        + pd.Timedelta(

            days=1

        )

        - pd.Timedelta(

            microseconds=1

        )

    )


    df_monitoramento = (

        df_monitoramento[

            (

                df_monitoramento[
                    "timestamp"
                ]

                >= data_inicio

            )

            &

            (

                df_monitoramento[
                    "timestamp"
                ]

                <= data_fim

            )

        ]

        .copy()

    )


# ============================================================
# ORDENAÇÃO
# ============================================================

df_monitoramento = (

    df_monitoramento

    .sort_values(

        "timestamp"

    )

    .copy()

)


# ============================================================
# VALIDAÇÃO DO FILTRO
# ============================================================

if df_monitoramento.empty:

    st.warning(

        """
        ⚠️ Nenhum dado foi encontrado para o paciente
        e período selecionados.
        """

    )

    st.stop()


# ============================================================
# INFORMAÇÕES DO PACIENTE
# ============================================================

st.subheader(
    "👤 Paciente Monitorado"
)


col1, col2, col3 = st.columns(3)


# ============================================================
# PACIENTE
# ============================================================

with col1:

    st.metric(

        "ID do Paciente",

        paciente_selecionado

    )


# ============================================================
# PRIMEIRO REGISTRO
# ============================================================

with col2:


    primeiro_registro = (

        df_monitoramento[
            "timestamp"
        ]

        .min()

    )


    st.metric(

        "Início do Período",

        primeiro_registro.strftime(

            "%d/%m/%Y %H:%M"

        )

    )


# ============================================================
# ÚLTIMO REGISTRO
# ============================================================

with col3:


    ultimo_registro = (

        df_monitoramento[
            "timestamp"
        ]

        .max()

    )


    st.metric(

        "Último Registro",

        ultimo_registro.strftime(

            "%d/%m/%Y %H:%M"

        )

    )


# ============================================================
# INFORMAÇÃO DO PERÍODO
# ============================================================

st.caption(

    f"""
    Período disponível para este paciente:
    {data_min_paciente.strftime('%d/%m/%Y %H:%M')}
    até
    {data_max_paciente.strftime('%d/%m/%Y %H:%M')}
    """

)


# ============================================================
# ÚLTIMO REGISTRO DO PACIENTE
# ============================================================

registro_atual = (

    df_monitoramento

    .sort_values(

        "timestamp"

    )

    .tail(1)

    .iloc[0]

)


# ============================================================
# RESUMO CLÍNICO ATUAL
# ============================================================

st.divider()


st.subheader(
    "📊 Situação Clínica Atual"
)


st.caption(

    """
    Os valores abaixo correspondem ao último
    registro disponível no período selecionado.
    """

)


col1, col2, col3, col4 = st.columns(4)


# ============================================================
# FUNÇÃO AUXILIAR PARA MÉTRICAS
# ============================================================

def mostrar_metrica(

    coluna,

    titulo,

    formato

):


    if coluna in registro_atual.index:


        valor = registro_atual[
            coluna
        ]


        if pd.notna(valor):


            return formato.format(

                valor

            )


    return "N/D"


# ============================================================
# FREQUÊNCIA CARDÍACA
# ============================================================

with col1:


    valor_fc = mostrar_metrica(

        "frequencia_cardiaca",

        "Frequência Cardíaca",

        "{:.1f} bpm"

    )


    st.metric(

        "❤️ Frequência Cardíaca",

        valor_fc

    )


# ============================================================
# SATURAÇÃO
# ============================================================

with col2:


    valor_spo2 = mostrar_metrica(

        "saturacao_O2",

        "Saturação",

        "{:.1f}%"

    )


    st.metric(

        "⭕ Saturação de O₂",

        valor_spo2

    )


# ============================================================
# TEMPERATURA
# ============================================================

with col3:


    valor_temperatura = mostrar_metrica(

        "temperatura",

        "Temperatura",

        "{:.1f} °C"

    )


    st.metric(

        "🌡️ Temperatura",

        valor_temperatura

    )


# ============================================================
# LACTATO
# ============================================================

with col4:


    valor_lactato = mostrar_metrica(

        "lactato",

        "Lactato",

        "{:.2f}"

    )


    st.metric(

        "🧪 Lactato",

        valor_lactato

    )


# ============================================================
# FUNÇÃO AUXILIAR PARA GRÁFICOS
# ============================================================

def grafico_temporal(

    dataframe,

    coluna,

    titulo,

    eixo_y

):


    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    if coluna not in dataframe.columns:


        st.warning(

            f"⚠️ {titulo}: dados não disponíveis."

        )

        return


    # ========================================================
    # PREPARAÇÃO
    # ========================================================

    dados_grafico = (

        dataframe[

            [

                "timestamp",

                coluna

            ]

        ]

        .copy()

    )


    dados_grafico = (

        dados_grafico

        .dropna()

        .sort_values(

            "timestamp"

        )

    )


    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    if dados_grafico.empty:


        st.warning(

            f"⚠️ {titulo}: não há dados disponíveis."

        )

        return


    # ========================================================
    # GRÁFICO
    # ========================================================

    fig = px.line(

        dados_grafico,

        x="timestamp",

        y=coluna

    )


    # ========================================================
    # ESTILO DA LINHA
    # ========================================================

    fig.update_traces(

        line=dict(

            width=3

        )

    )


    # ========================================================
    # LAYOUT
    # ========================================================

    fig.update_layout(

        title=titulo,

        xaxis_title="Data / Hora",

        yaxis_title=eixo_y,

        height=350,

        margin=dict(

            l=20,

            r=20,

            t=50,

            b=20

        ),

        hovermode="x unified"

    )


    # ========================================================
    # EIXO X
    # ========================================================

    fig.update_xaxes(

        tickformat="%d/%m\n%H:%M",

        showgrid=True

    )


    # ========================================================
    # EIXO Y
    # ========================================================

    fig.update_yaxes(

        showgrid=True

    )


    # ========================================================
    # EXIBIÇÃO
    # ========================================================

    st.plotly_chart(

        fig,

        use_container_width=True

    )


# ============================================================
# SINAIS VITAIS
# ============================================================

st.divider()


st.header(
    "❤️ Sinais Vitais"
)


st.caption(

    """
    Evolução temporal individual dos principais
    sinais vitais do paciente selecionado.
    """

)


# ============================================================
# FREQUÊNCIA CARDÍACA E SATURAÇÃO
# ============================================================

col1, col2 = st.columns(2)


with col1:


    grafico_temporal(

        df_monitoramento,

        "frequencia_cardiaca",

        "❤️ Frequência Cardíaca",

        "FC (bpm)"

    )


with col2:


    grafico_temporal(

        df_monitoramento,

        "saturacao_O2",

        "⭕ Saturação de Oxigênio",

        "SpO₂ (%)"

    )


# ============================================================
# PRESSÃO ARTERIAL
# ============================================================

st.divider()


st.subheader(
    "🩸 Pressão Arterial"
)


st.caption(

    """
    Visualização individual da pressão sistólica
    e diastólica ao longo do período.
    """

)


col1, col2 = st.columns(2)


# ============================================================
# PRESSÃO SISTÓLICA
# ============================================================

with col1:


    grafico_temporal(

        df_monitoramento,

        "pressao_sistolica",

        "Pressão Sistólica",

        "Pressão (mmHg)"

    )


# ============================================================
# PRESSÃO DIASTÓLICA
# ============================================================

with col2:


    grafico_temporal(

        df_monitoramento,

        "pressao_diastolica",

        "Pressão Diastólica",

        "Pressão (mmHg)"

    )


# ============================================================
# TEMPERATURA
# ============================================================

st.divider()


st.subheader(
    "🌡️ Temperatura"
)


grafico_temporal(

    df_monitoramento,

    "temperatura",

    "Evolução da Temperatura Corporal",

    "Temperatura (°C)"

)


# ============================================================
# EXAMES LABORATORIAIS
# ============================================================

st.divider()


st.header(
    "🧪 Indicadores Laboratoriais"
)


st.caption(

    """
    Evolução temporal dos indicadores laboratoriais
    disponíveis na base simulada.
    """

)


col1, col2, col3 = st.columns(3)


# ============================================================
# LACTATO
# ============================================================

with col1:


    grafico_temporal(

        df_monitoramento,

        "lactato",

        "Lactato",

        "Lactato"

    )


# ============================================================
# LEUCÓCITOS
# ============================================================

with col2:


    grafico_temporal(

        df_monitoramento,

        "leucocitos",

        "Leucócitos",

        "Leucócitos"

    )


# ============================================================
# CREATININA
# ============================================================

with col3:


    grafico_temporal(

        df_monitoramento,

        "creatinina",

        "Creatinina",

        "Creatinina"

    )


# ============================================================
# TENDÊNCIA CLÍNICA
# ============================================================

st.divider()


st.header(
    "📈 Tendência Clínica"
)


st.caption(

    """
    Evolução temporal do score clínico calculado
    pelo motor analítico.
    """

)


grafico_temporal(

    df_monitoramento,

    "score_clinico",

    "Evolução do Score Clínico",

    "Score Clínico"

)


# ============================================================
# CLASSIFICAÇÃO CLÍNICA ATUAL
# ============================================================

if "classificacao_clinica" in registro_atual.index:


    classificacao = registro_atual[

        "classificacao_clinica"

    ]


    if pd.notna(classificacao):


        st.subheader(
            "🚦 Classificação Atual"
        )


        st.info(

            f"""
            Situação clínica atual:

            **{classificacao}**
            """

        )


# ============================================================
# DADOS UTILIZADOS
# ============================================================

st.divider()


with st.expander(

    "📋 Visualizar dados utilizados no monitoramento",

    expanded=False

):


    colunas_monitoramento = [


        # IDENTIFICAÇÃO

        "id_paciente",

        "timestamp",


        # SINAIS VITAIS

        "frequencia_cardiaca",

        "pressao_sistolica",

        "pressao_diastolica",

        "saturacao_O2",

        "temperatura",


        # LABORATORIAIS

        "lactato",

        "leucocitos",

        "creatinina",


        # MOTOR ANALÍTICO

        "score_clinico",

        "classificacao_clinica"

    ]


    colunas_disponiveis = [


        coluna

        for coluna in colunas_monitoramento

        if coluna in df_monitoramento.columns

    ]


    st.dataframe(

        df_monitoramento[

            colunas_disponiveis

        ],

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# DIAGNÓSTICO TEMPORAL
# ============================================================

st.divider()


with st.expander(

    "🛠️ Diagnóstico temporal",

    expanded=False

):


    # ========================================================
    # STATUS DA CONVERSÃO
    # ========================================================

    st.subheader(
        "Status da conversão temporal"
    )


    st.success(
        "✓ Timestamp convertido utilizando formato DD/MM/AAAA HH:MM"
    )


    # ========================================================
    # DATAS INVÁLIDAS
    # ========================================================

    if quantidade_timestamps_invalidos == 0:


        st.success(
            "✓ Nenhum timestamp inválido encontrado"
        )


    else:


        st.warning(

            f"""
            ⚠️ Foram encontrados
            {quantidade_timestamps_invalidos}
            timestamps inválidos.
            """

        )


    # ========================================================
    # INFORMAÇÕES
    # ========================================================

    st.subheader(
        "Informações do monitoramento"
    )


    st.write(

        f"""
        **Paciente selecionado:** {paciente_selecionado}

        **Total de registros utilizados:** {len(df_monitoramento)}

        **Primeiro timestamp selecionado:**
        {df_monitoramento['timestamp'].min().strftime('%d/%m/%Y %H:%M')}

        **Último timestamp selecionado:**
        {df_monitoramento['timestamp'].max().strftime('%d/%m/%Y %H:%M')}

        **Período total da base:**
        {data_min.strftime('%d/%m/%Y %H:%M')}
        até
        {data_max.strftime('%d/%m/%Y %H:%M')}

        **Período disponível do paciente:**
        {data_min_paciente.strftime('%d/%m/%Y %H:%M')}
        até
        {data_max_paciente.strftime('%d/%m/%Y %H:%M')}
        """

    )


    # ========================================================
    # TIPO DO TIMESTAMP
    # ========================================================

    st.subheader(
        "Tipo da coluna timestamp"
    )


    st.code(

        str(

            df[
                "timestamp"
            ].dtype

        )

    )


    # ========================================================
    # AMOSTRA TEMPORAL
    # ========================================================

    st.subheader(
        "Amostra dos registros temporais"
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

    Os dados apresentados nesta página são totalmente
    simulados e possuem finalidade exclusivamente
    educacional e conceitual.

    Os indicadores e scores apresentados não constituem
    um sistema clínico validado e não devem ser utilizados
    para tomada de decisão clínica real.
    """

)
