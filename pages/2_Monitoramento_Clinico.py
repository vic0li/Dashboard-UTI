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
# PROCESSAMENTO DO TIMESTAMP
# ============================================================

if "timestamp" in df.columns:

    df["timestamp"] = pd.to_datetime(

        df["timestamp"],

        dayfirst=True,

        errors="coerce"

    )


else:

    st.error(
        "❌ A coluna 'timestamp' não foi encontrada."
    )

    st.stop()


# ============================================================
# REMOVER TIMESTAMPS INVÁLIDOS
# ============================================================

df = df.dropna(
    subset=["timestamp"]
)


# ============================================================
# VALIDAÇÃO APÓS PROCESSAMENTO
# ============================================================

if df.empty:

    st.error(
        "❌ Não existem timestamps válidos na base."
    )

    st.stop()


# ============================================================
# ORDENAÇÃO TEMPORAL
# ============================================================

df = df.sort_values(
    "timestamp"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🩺 Monitoramento Clínico"
)


st.caption(
    """
    Acompanhamento temporal dos indicadores clínicos
    simulados dos pacientes da UTI.
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

if "id_paciente" in df.columns:


    lista_pacientes = sorted(

        df[
            "id_paciente"
        ]

        .dropna()

        .unique()

        .tolist()

    )


    if not lista_pacientes:

        st.error(
            "❌ Nenhum paciente encontrado na base."
        )

        st.stop()


    paciente_selecionado = st.sidebar.selectbox(

        "Selecionar paciente",

        lista_pacientes

    )


else:

    st.error(
        "❌ A coluna 'id_paciente' não foi encontrada."
    )

    st.stop()


# ============================================================
# FILTRO DE PERÍODO
# ============================================================

data_min = df[
    "timestamp"
].min()


data_max = df[
    "timestamp"
].max()


periodo = st.sidebar.date_input(

    "Período de análise",

    value=(

        data_min.date(),

        data_max.date()

    ),

    min_value=data_min.date(),

    max_value=data_max.date()

)


# ============================================================
# DATAFRAME DO MONITORAMENTO
# ============================================================

df_monitoramento = df.copy()


# ============================================================
# FILTRO DE PACIENTE
# ============================================================

df_monitoramento = (

    df_monitoramento[

        df_monitoramento[
            "id_paciente"
        ]

        == paciente_selecionado

    ]

    .copy()

)


# ============================================================
# FILTRO DE PERÍODO
# ============================================================

if periodo is not None and len(periodo) == 2:


    data_inicio = pd.to_datetime(

        periodo[0]

    )


    data_fim = (

        pd.to_datetime(
            periodo[1]
        )

        + pd.Timedelta(
            days=1
        )

        - pd.Timedelta(
            seconds=1
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
# FREQUÊNCIA CARDÍACA
# ============================================================

with col1:


    if "frequencia_cardiaca" in df_monitoramento.columns:


        valor = registro_atual[
            "frequencia_cardiaca"
        ]


        if pd.notna(valor):

            st.metric(

                "❤️ Frequência Cardíaca",

                f"{valor:.1f} bpm"

            )


        else:

            st.metric(

                "❤️ Frequência Cardíaca",

                "N/D"

            )


    else:

        st.metric(

            "❤️ Frequência Cardíaca",

            "N/D"

        )


# ============================================================
# SATURAÇÃO
# ============================================================

with col2:


    if "saturacao_O2" in df_monitoramento.columns:


        valor = registro_atual[
            "saturacao_O2"
        ]


        if pd.notna(valor):

            st.metric(

                "⭕ Saturação de O₂",

                f"{valor:.1f}%"

            )


        else:

            st.metric(

                "⭕ Saturação de O₂",

                "N/D"

            )


    else:

        st.metric(

            "⭕ Saturação de O₂",

            "N/D"

        )


# ============================================================
# TEMPERATURA
# ============================================================

with col3:


    if "temperatura" in df_monitoramento.columns:


        valor = registro_atual[
            "temperatura"
        ]


        if pd.notna(valor):

            st.metric(

                "🌡️ Temperatura",

                f"{valor:.1f} °C"

            )


        else:

            st.metric(

                "🌡️ Temperatura",

                "N/D"

            )


    else:

        st.metric(

            "🌡️ Temperatura",

            "N/D"

        )


# ============================================================
# LACTATO
# ============================================================

with col4:


    if "lactato" in df_monitoramento.columns:


        valor = registro_atual[
            "lactato"
        ]


        if pd.notna(valor):

            st.metric(

                "🧪 Lactato",

                f"{valor:.2f}"

            )


        else:

            st.metric(

                "🧪 Lactato",

                "N/D"

            )


    else:

        st.metric(

            "🧪 Lactato",

            "N/D"

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
    # VALIDAÇÃO DA COLUNA
    # ========================================================

    if coluna not in dataframe.columns:

        st.warning(

            f"{titulo}: dados não disponíveis."

        )

        return


    # ========================================================
    # PREPARAÇÃO DOS DADOS
    # ========================================================

    dados_grafico = (

        dataframe[

            [

                "timestamp",

                coluna

            ]

        ]

        .dropna()

        .copy()

    )


    # ========================================================
    # VALIDAÇÃO DOS DADOS
    # ========================================================

    if dados_grafico.empty:

        st.warning(

            f"{titulo}: não há dados disponíveis."

        )

        return


    # ========================================================
    # ORDENAÇÃO TEMPORAL
    # ========================================================

    dados_grafico = dados_grafico.sort_values(

        "timestamp"

    )


    # ========================================================
    # CRIAÇÃO DO GRÁFICO
    # ========================================================

    fig = px.line(

        dados_grafico,

        x="timestamp",

        y=coluna,

        title=titulo

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

        xaxis_title="Data / Hora",

        yaxis_title=eixo_y,

        height=350,

        margin=dict(

            l=20,

            r=20,

            t=50,

            b=20

        ),

        hovermode="x unified",

        xaxis=dict(

            tickformat="%d/%m\n%H:%M"

        )

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
    sinais vitais do paciente.
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
    Evolução temporal dos exames laboratoriais
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
    Evolução do score clínico calculado pelo
    motor analítico.
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


    st.subheader(
        "🚦 Classificação Atual"
    )


    classificacao = registro_atual[
        "classificacao_clinica"
    ]


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


        "id_paciente",

        "timestamp",


        "frequencia_cardiaca",

        "pressao_sistolica",

        "pressao_diastolica",

        "saturacao_O2",

        "temperatura",


        "lactato",

        "leucocitos",

        "creatinina",


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


    st.write(

        f"""
        **Paciente selecionado:** {paciente_selecionado}

        **Total de registros utilizados:**
        {len(df_monitoramento)}

        **Primeiro timestamp:**
        {df_monitoramento['timestamp'].min()}

        **Último timestamp:**
        {df_monitoramento['timestamp'].max()}

        **Período total disponível:**
        {data_min.strftime('%d/%m/%Y')}
        até
        {data_max.strftime('%d/%m/%Y')}
        """

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

    Este sistema não deve ser utilizado para tomada
    de decisão clínica real.
    """

)
