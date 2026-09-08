
# ============================================================
# PÁGINA 2
# MONITORAMENTO CLÍNICO
# UTI INTELLIGENT CARE
#
# Monitoramento temporal e análise clínica
# dos pacientes simulados da UTI.
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

    layout="wide",

    initial_sidebar_state="expanded"

)


# ============================================================
# ESTILO
# ============================================================

aplicar_estilo()


# ============================================================
# TÍTULO
# ============================================================

st.title("🩺 Monitoramento Clínico")


st.caption(
    """
    Acompanhamento dos indicadores clínicos simulados,
    evolução temporal e situação atual dos pacientes.
    """
)


st.divider()


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
# PREPARAÇÃO TEMPORAL
# ============================================================

if "timestamp" in df.columns:

    df["timestamp"] = pd.to_datetime(

        df["timestamp"],

        errors="coerce"

    )


# ============================================================
# FILTROS INTERATIVOS
# ============================================================

st.sidebar.header(
    "🔍 Filtros"
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

        .astype(str)

        .unique()

        .tolist()

    )


    paciente_selecionado = st.sidebar.selectbox(

        "👤 Paciente",

        options=[

            "Todos"

        ] + lista_pacientes

    )


else:

    paciente_selecionado = "Todos"


# ============================================================
# FILTRO DE CLASSIFICAÇÃO CLÍNICA
# ============================================================

if "classificacao_clinica" in df.columns:


    classificacoes = sorted(

        df[
            "classificacao_clinica"
        ]

        .dropna()

        .unique()

        .tolist()

    )


    classificacao_selecionada = (

        st.sidebar.selectbox(

            "🩺 Situação Clínica",

            options=[

                "Todas"

            ] + classificacoes

        )

    )


else:

    classificacao_selecionada = "Todas"


# ============================================================
# FILTRO DE PERÍODO
# ============================================================

periodo_disponivel = (

    "timestamp" in df.columns

    and

    df["timestamp"].notna().any()

)


if periodo_disponivel:


    data_min = df["timestamp"].min().date()

    data_max = df["timestamp"].max().date()


    periodo_selecionado = (

        st.sidebar.date_input(

            "📅 Período",

            value=(

                data_min,

                data_max

            ),

            min_value=data_min,

            max_value=data_max

        )

    )


else:

    periodo_selecionado = None


# ============================================================
# BOTÃO PARA LIMPAR FILTROS
# ============================================================

if st.sidebar.button(

    "🔄 Limpar filtros"

):

    st.rerun()


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()


# ============================================================
# FILTRO DE PACIENTE
# ============================================================

if (

    paciente_selecionado != "Todos"

    and

    "id_paciente" in df_filtrado.columns

):


    df_filtrado = (

        df_filtrado[

            df_filtrado[
                "id_paciente"
            ].astype(str)

            == paciente_selecionado

        ]

        .copy()

    )


# ============================================================
# FILTRO DE CLASSIFICAÇÃO CLÍNICA
# ============================================================

if (

    classificacao_selecionada != "Todas"

    and

    "classificacao_clinica"

    in df_filtrado.columns

):


    df_filtrado = (

        df_filtrado[

            df_filtrado[
                "classificacao_clinica"
            ]

            == classificacao_selecionada

        ]

        .copy()

    )


# ============================================================
# FILTRO DE PERÍODO
# ============================================================

if (

    periodo_selecionado

    and

    "timestamp"

    in df_filtrado.columns

):


    if isinstance(

        periodo_selecionado,

        tuple

    ) and len(

        periodo_selecionado

    ) == 2:


        data_inicio = pd.to_datetime(

            periodo_selecionado[0]

        )


        data_fim = (

            pd.to_datetime(

                periodo_selecionado[1]

            )

            +

            pd.Timedelta(

                days=1

            )

        )


        df_filtrado = (

            df_filtrado[

                (

                    df_filtrado[
                        "timestamp"
                    ]

                    >= data_inicio

                )

                &

                (

                    df_filtrado[
                        "timestamp"
                    ]

                    < data_fim

                )

            ]

            .copy()

        )


# ============================================================
# VERIFICAÇÃO DO FILTRO
# ============================================================

if df_filtrado.empty:


    st.warning(
        """
        ⚠️ Nenhum registro encontrado para os filtros
        selecionados.
        """
    )


    st.stop()


# ============================================================
# DATAFRAME DE PACIENTES ATUAIS
# ============================================================

# Após aplicar os filtros temporais,
# identificamos o último registro disponível
# de cada paciente.


if (

    "id_paciente"

    in df_filtrado.columns

    and

    "timestamp"

    in df_filtrado.columns

):


    df_pacientes = (

        df_filtrado

        .sort_values(

            "timestamp"

        )

        .groupby(

            "id_paciente",

            as_index=False

        )

        .tail(1)

        .copy()

    )


elif "id_paciente" in df_filtrado.columns:


    df_pacientes = (

        df_filtrado

        .drop_duplicates(

            subset="id_paciente",

            keep="last"

        )

        .copy()

    )


else:


    df_pacientes = (

        df_filtrado.copy()

    )


# ============================================================
# CONTEXTO DO FILTRO
# ============================================================

st.info(
    f"""
    📊 **Contexto atual:** {len(df_pacientes)}
    pacientes únicos e {len(df_filtrado)}
    registros temporais estão sendo analisados.
    """
)


# ============================================================
# SITUAÇÃO CLÍNICA ATUAL
# ============================================================

st.header(
    "📊 Situação Clínica Atual"
)


st.caption(
    """
    Os indicadores abaixo utilizam apenas o último
    registro disponível de cada paciente após a
    aplicação dos filtros.
    """
)


# ============================================================
# TOTAL DE PACIENTES
# ============================================================

total_pacientes = (

    df_pacientes[
        "id_paciente"
    ].nunique()

    if "id_paciente"

    in df_pacientes.columns

    else len(df_pacientes)

)


# ============================================================
# SPO2 MÉDIA
# ============================================================

if (

    "saturacao_O2"

    in df_pacientes.columns

):


    spo2_media = (

        df_pacientes[
            "saturacao_O2"
        ]

        .mean()

    )


else:


    spo2_media = None


# ============================================================
# FC MÉDIA
# ============================================================

if (

    "frequencia_cardiaca"

    in df_pacientes.columns

):


    fc_media = (

        df_pacientes[
            "frequencia_cardiaca"
        ]

        .mean()

    )


else:


    fc_media = None


# ============================================================
# TEMPERATURA MÉDIA
# ============================================================

if (

    "temperatura"

    in df_pacientes.columns

):


    temperatura_media = (

        df_pacientes[
            "temperatura"
        ]

        .mean()

    )


else:


    temperatura_media = None


# ============================================================
# SCORE CLÍNICO MÉDIO
# ============================================================

if (

    "score_clinico"

    in df_pacientes.columns

):


    score_medio = (

        df_pacientes[
            "score_clinico"
        ]

        .mean()

    )


else:


    score_medio = None


# ============================================================
# CARDS
# ============================================================

col1, col2, col3, col4, col5 = (

    st.columns(5)

)


with col1:


    st.metric(

        "👥 Pacientes",

        total_pacientes

    )


with col2:


    if spo2_media is not None:


        st.metric(

            "⭕ SpO₂ Média",

            f"{spo2_media:.1f}%"

        )


    else:


        st.metric(

            "⭕ SpO₂ Média",

            "N/D"

        )


with col3:


    if fc_media is not None:


        st.metric(

            "💓 FC Média",

            f"{fc_media:.1f} bpm"

        )


    else:


        st.metric(

            "💓 FC Média",

            "N/D"

        )


with col4:


    if temperatura_media is not None:


        st.metric(

            "🌡️ Temperatura",

            f"{temperatura_media:.1f} °C"

        )


    else:


        st.metric(

            "🌡️ Temperatura",

            "N/D"

        )


with col5:


    if score_medio is not None:


        st.metric(

            "🧠 Score Clínico",

            f"{score_medio:.1f}"

        )


    else:


        st.metric(

            "🧠 Score Clínico",

            "N/D"

        )


# ============================================================
# DISTRIBUIÇÃO CLÍNICA
# ============================================================

st.divider()

st.header(
    "🩺 Distribuição da Situação Clínica"
)


st.caption(
    """
    Cada paciente é contabilizado apenas uma vez,
    utilizando seu registro mais recente.
    """
)


if (

    "classificacao_clinica"

    in df_pacientes.columns

):


    distribuicao_clinica = (

        df_pacientes

        .groupby(

            "classificacao_clinica"

        )

        .agg(

            Pacientes=(

                "id_paciente",

                "nunique"

            )

        )

        .reset_index()

    )


    fig_classificacao = px.bar(

        distribuicao_clinica,

        x="classificacao_clinica",

        y="Pacientes",

        text="Pacientes",

        color="classificacao_clinica",

        labels={

            "classificacao_clinica":

            "Situação Clínica"

        }

    )


    fig_classificacao.update_layout(

        showlegend=False,

        height=400,

        xaxis_title="Situação Clínica",

        yaxis_title="Número de Pacientes"

    )


    st.plotly_chart(

        fig_classificacao,

        use_container_width=True

    )


else:


    st.warning(
        """
        A coluna de classificação clínica
        não está disponível.
        """
    )


# ============================================================
# EVOLUÇÃO TEMPORAL
# ============================================================

st.divider()

st.header(
    "📈 Evolução Temporal dos Indicadores"
)


st.caption(
    """
    Esta seção utiliza todos os registros temporais
    disponíveis após a aplicação dos filtros.
    """
)


# ============================================================
# SELEÇÃO DO INDICADOR
# ============================================================

indicadores_disponiveis = []


mapa_indicadores = {

    "Frequência Cardíaca":

    "frequencia_cardiaca",


    "SpO₂":

    "saturacao_O2",


    "Temperatura":

    "temperatura",


    "Pressão Sistólica":

    "pressao_sistolica",


    "Pressão Diastólica":

    "pressao_diastolica",


    "Score Clínico":

    "score_clinico"

}


for nome, coluna in mapa_indicadores.items():


    if coluna in df_filtrado.columns:


        indicadores_disponiveis.append(

            nome

        )


if indicadores_disponiveis:


    indicador_selecionado = (

        st.selectbox(

            "Selecione o indicador clínico",

            indicadores_disponiveis

        )

    )


    coluna_indicador = (

        mapa_indicadores[
            indicador_selecionado
        ]

    )


    if (

        "timestamp"

        in df_filtrado.columns

    ):


        fig_temporal = px.line(

            df_filtrado,

            x="timestamp",

            y=coluna_indicador,

            color=(

                "id_paciente"

                if

                "id_paciente"

                in df_filtrado.columns

                else None

            ),

            markers=True,

            labels={

                coluna_indicador:

                indicador_selecionado,

                "timestamp":

                "Data / Hora"

            }

        )


        fig_temporal.update_layout(

            height=500,

            hovermode="x unified",

            xaxis_title="Data / Hora",

            yaxis_title=indicador_selecionado

        )


        st.plotly_chart(

            fig_temporal,

            use_container_width=True

        )


    else:


        st.warning(
            "Timestamp não disponível."
        )


else:


    st.warning(
        """
        Nenhum indicador clínico disponível
        para análise temporal.
        """
    )


# ============================================================
# INDICADORES CLÍNICOS EM PARALELO
# ============================================================

st.divider()

st.header(
    "📊 Indicadores Clínicos"
)


st.caption(
    """
    Visualização simultânea dos principais
    indicadores clínicos simulados.
    """
)


col1, col2 = st.columns(2)


# ============================================================
# FREQUÊNCIA CARDÍACA
# ============================================================

with col1:


    st.subheader(
        "💓 Frequência Cardíaca"
    )


    if (

        "frequencia_cardiaca"

        in df_filtrado.columns

        and

        "timestamp"

        in df_filtrado.columns

    ):


        fig_fc = px.line(

            df_filtrado,

            x="timestamp",

            y="frequencia_cardiaca",

            color=(

                "id_paciente"

                if

                "id_paciente"

                in df_filtrado.columns

                else None

            ),

            labels={

                "frequencia_cardiaca":

                "FC (bpm)",

                "timestamp":

                "Data / Hora"

            }

        )


        fig_fc.update_layout(

            height=350,

            hovermode="x unified"

        )


        st.plotly_chart(

            fig_fc,

            use_container_width=True

        )


    else:


        st.warning(
            "Dados de frequência cardíaca indisponíveis."
        )


# ============================================================
# SPO2
# ============================================================

with col2:


    st.subheader(
        "⭕ Saturação de Oxigênio"
    )


    if (

        "saturacao_O2"

        in df_filtrado.columns

        and

        "timestamp"

        in df_filtrado.columns

    ):


        fig_spo2 = px.line(

            df_filtrado,

            x="timestamp",

            y="saturacao_O2",

            color=(

                "id_paciente"

                if

                "id_paciente"

                in df_filtrado.columns

                else None

            ),

            labels={

                "saturacao_O2":

                "SpO₂ (%)",

                "timestamp":

                "Data / Hora"

            }

        )


        fig_spo2.update_layout(

            height=350,

            hovermode="x unified"

        )


        st.plotly_chart(

            fig_spo2,

            use_container_width=True

        )


    else:


        st.warning(
            "Dados de SpO₂ indisponíveis."
        )


# ============================================================
# PRESSÃO ARTERIAL
# ============================================================

st.divider()

st.header(
    "🩸 Pressão Arterial"
)


if (

    "pressao_sistolica"

    in df_filtrado.columns

    and

    "pressao_diastolica"

    in df_filtrado.columns

    and

    "timestamp"

    in df_filtrado.columns

):


    df_pressao = (

        df_filtrado[

            [

                "timestamp",

                "id_paciente",

                "pressao_sistolica",

                "pressao_diastolica"

            ]

        ]

        .copy()

    )


    df_pressao_long = (

        df_pressao

        .melt(

            id_vars=[

                "timestamp",

                "id_paciente"

            ],

            value_vars=[

                "pressao_sistolica",

                "pressao_diastolica"

            ],

            var_name="Tipo",

            value_name="Pressão"

        )

    )


    fig_pressao = px.line(

        df_pressao_long,

        x="timestamp",

        y="Pressão",

        color="Tipo",

        line_dash=(

            "id_paciente"

            if

            paciente_selecionado == "Todos"

            else None

        ),

        labels={

            "timestamp":

            "Data / Hora",

            "Pressão":

            "Pressão (mmHg)"

        }

    )


    fig_pressao.update_layout(

        height=450,

        hovermode="x unified"

    )


    st.plotly_chart(

        fig_pressao,

        use_container_width=True

    )


else:


    st.warning(
        """
        Dados de pressão arterial
        não estão disponíveis.
        """
    )


# ============================================================
# ANÁLISE INDIVIDUAL DO PACIENTE
# ============================================================

st.divider()

st.header(
    "👤 Análise Individual do Paciente"
)


st.caption(
    """
    Visualização detalhada da evolução temporal
    de um paciente específico.
    """
)


if "id_paciente" in df.columns:


    pacientes_analise = sorted(

        df[
            "id_paciente"
        ]

        .dropna()

        .astype(str)

        .unique()

        .tolist()

    )


    paciente_analise = (

        st.selectbox(

            "Selecione um paciente para análise detalhada",

            pacientes_analise

        )

    )


    df_paciente_individual = (

        df[

            df[
                "id_paciente"
            ].astype(str)

            == paciente_analise

        ]

        .copy()

    )


    if (

        "timestamp"

        in df_paciente_individual.columns

    ):


        df_paciente_individual = (

            df_paciente_individual

            .sort_values(

                "timestamp"

            )

        )


    # ========================================================
    # ÚLTIMO REGISTRO
    # ========================================================

    ultimo_registro = (

        df_paciente_individual

        .tail(1)

    )


    if not ultimo_registro.empty:


        st.subheader(
            "📌 Situação Atual"
        )


        c1, c2, c3, c4 = (

            st.columns(4)

        )


        with c1:


            if (

                "frequencia_cardiaca"

                in ultimo_registro.columns

            ):


                valor_fc = (

                    ultimo_registro[
                        "frequencia_cardiaca"
                    ].iloc[0]

                )


                st.metric(

                    "💓 FC",

                    f"{valor_fc:.1f} bpm"

                )


        with c2:


            if (

                "saturacao_O2"

                in ultimo_registro.columns

            ):


                valor_spo2 = (

                    ultimo_registro[
                        "saturacao_O2"
                    ].iloc[0]

                )


                st.metric(

                    "⭕ SpO₂",

                    f"{valor_spo2:.1f}%"

                )


        with c3:


            if (

                "temperatura"

                in ultimo_registro.columns

            ):


                valor_temp = (

                    ultimo_registro[
                        "temperatura"
                    ].iloc[0]

                )


                st.metric(

                    "🌡️ Temperatura",

                    f"{valor_temp:.1f} °C"

                )


        with c4:


            if (

                "score_clinico"

                in ultimo_registro.columns

            ):


                valor_score = (

                    ultimo_registro[
                        "score_clinico"
                    ].iloc[0]

                )


                st.metric(

                    "🧠 Score Clínico",

                    f"{valor_score:.1f}"

                )


    # ========================================================
    # EVOLUÇÃO DO PACIENTE
    # ========================================================

    st.subheader(
        "📈 Evolução do Paciente"
    )


    variaveis_individuais = [

        "frequencia_cardiaca",

        "saturacao_O2",

        "temperatura",

        "score_clinico"

    ]


    variaveis_existentes = [

        coluna

        for coluna

        in variaveis_individuais

        if coluna

        in df_paciente_individual.columns

    ]


    if (

        variaveis_existentes

        and

        "timestamp"

        in df_paciente_individual.columns

    ):


        df_individual_long = (

            df_paciente_individual

            .melt(

                id_vars=[

                    "timestamp"

                ],

                value_vars=(

                    variaveis_existentes

                ),

                var_name="Indicador",

                value_name="Valor"

            )

        )


        fig_individual = px.line(

            df_individual_long,

            x="timestamp",

            y="Valor",

            color="Indicador",

            markers=True

        )


        fig_individual.update_layout(

            height=500,

            hovermode="x unified",

            xaxis_title="Data / Hora",

            yaxis_title="Valor"

        )


        st.plotly_chart(

            fig_individual,

            use_container_width=True

        )


    else:


        st.warning(
            """
            Não existem dados suficientes para gerar
            a evolução individual.
            """
        )


# ============================================================
# TABELA CLÍNICA ATUAL
# ============================================================

st.divider()

st.header(
    "📋 Situação Atual dos Pacientes"
)


st.caption(
    """
    Cada paciente aparece apenas uma vez,
    utilizando seu último registro disponível.
    """
)


colunas_clinicas = [

    "id_paciente",

    "timestamp",

    "frequencia_cardiaca",

    "pressao_sistolica",

    "pressao_diastolica",

    "saturacao_O2",

    "temperatura",

    "lactato",

    "score_clinico",

    "classificacao_clinica"

]


colunas_existentes = [

    coluna

    for coluna

    in colunas_clinicas

    if coluna

    in df_pacientes.columns

]


if colunas_existentes:


    df_tabela = (

        df_pacientes[

            colunas_existentes

        ]

        .copy()

    )


    if (

        "score_clinico"

        in df_tabela.columns

    ):


        df_tabela = (

            df_tabela

            .sort_values(

                "score_clinico",

                ascending=False

            )

        )


    st.dataframe(

        df_tabela,

        use_container_width=True,

        hide_index=True

    )


else:


    st.warning(
        """
        Nenhuma variável clínica disponível
        para visualização.
        """
    )


# ============================================================
# RESUMO TÉCNICO
# ============================================================

st.divider()


with st.expander(

    "🔬 Informações sobre a análise",

    expanded=False

):


    st.write(
        f"""
        **Registros temporais analisados:** {len(df_filtrado)}

        **Pacientes únicos analisados:** {len(df_pacientes)}
        """
    )


    st.write(
        """
        ### Lógica da página

        **Visão atual**

        Utiliza apenas o último registro disponível
        de cada paciente.

        **Evolução temporal**

        Utiliza todos os registros disponíveis
        após a aplicação dos filtros.

        Isso permite separar corretamente:

        • Estado atual do paciente

        • Histórico clínico

        • Evolução temporal dos indicadores
        """
    )


# ============================================================
# AVISO ACADÊMICO
# ============================================================

st.divider()


st.info(
    """
    ⚠️ **Protótipo acadêmico**

    Esta página utiliza dados totalmente simulados
    para demonstrar conceitos de monitoramento clínico,
    análise temporal e suporte à decisão.

    Os indicadores e scores apresentados possuem
    finalidade exclusivamente educacional e conceitual.
    """
)

