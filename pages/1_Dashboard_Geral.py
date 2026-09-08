# ============================================================
# DASHBOARD GERAL
# UTI INTELLIGENT CARE
#
# Visão integrada dos indicadores clínicos, risco de LPP,
# alertas e priorização de pacientes.
#
# IMPORTANTE:
# A base possui registros temporais.
# Um mesmo paciente pode aparecer diversas vezes.
#
# Por isso:
#
# - KPIs de pacientes utilizam pacientes únicos
# - Gráficos utilizam o último registro de cada paciente
# - Tabela detalhada mantém os registros temporais
# ============================================================


import streamlit as st
import pandas as pd
import plotly.express as px


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
# FUNÇÕES AUXILIARES
# ============================================================

def obter_ultimo_registro_por_paciente(dataframe):
    """
    Retorna uma visão consolidada com apenas o último
    registro disponível de cada paciente.

    Isso evita que pacientes sejam contados diversas vezes
    nos KPIs e gráficos.
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
        df_temp["timestamp"] = pd.to_datetime(
            df_temp["timestamp"],
            errors="coerce"
        )

        # Ordena por paciente e tempo
        df_temp = df_temp.sort_values(
            by=["id_paciente", "timestamp"]
        )

        # Mantém apenas o último registro
        df_temp = df_temp.groupby(
            "id_paciente",
            as_index=False
        ).tail(1)
    else:
        # Caso não exista timestamp,
        # utiliza o último registro disponível
        df_temp = df_temp.groupby(
            "id_paciente",
            as_index=False
        ).tail(1)

    return df_temp


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
# GARANTIR TIMESTAMP
# ============================================================

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )


# ============================================================
# HEADER
# ============================================================

st.title("📊 Dashboard Geral")

st.caption(
    """
    Visão integrada e interativa dos indicadores clínicos,
    riscos e prioridades da UTI simulada.
    """
)

st.divider()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header(
    "🔍 Filtros Interativos"
)

st.sidebar.caption(
    """
    Os filtros aplicados nesta barra atualizam
    automaticamente todos os indicadores,
    gráficos e tabelas do dashboard.
    """
)


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
    opcoes_lpp = ["Todas"]

filtro_lpp = st.sidebar.selectbox(
    "🩹 Risco de LPP",
    options=opcoes_lpp
)


# ============================================================
# FILTRO DE PRIORIDADE
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
    opcoes_prioridade = ["Todas"]

filtro_prioridade = st.sidebar.selectbox(
    "🎯 Prioridade",
    options=opcoes_prioridade
)


# ============================================================
# INFORMAÇÃO SOBRE OS FILTROS
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
        st.sidebar.write(
            f"• {filtro}"
        )
else:
    st.sidebar.caption(
        "Nenhum filtro aplicado."
    )


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()

# ------------------------------------------------------------
# BUSCA POR PACIENTE
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# FILTRO CLÍNICO
# ------------------------------------------------------------
if filtro_clinico != "Todas":
    if "classificacao_clinica" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado[
                "classificacao_clinica"
            ].astype(str)
            == filtro_clinico
        ]

# ------------------------------------------------------------
# FILTRO LPP
# ------------------------------------------------------------
if filtro_lpp != "Todas":
    if "classificacao_lpp" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado[
                "classificacao_lpp"
            ].astype(str)
            == filtro_lpp
        ]

# ------------------------------------------------------------
# FILTRO PRIORIDADE
# ------------------------------------------------------------
if filtro_prioridade != "Todas":
    if "classificacao_prioridade" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado[
                "classificacao_prioridade"
            ].astype(str)
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

st.subheader(
    "📌 Situação Geral"
)

st.caption(
    """
    Os indicadores abaixo consideram pacientes únicos
    após a aplicação dos filtros.
    """
)

col1, col2, col3, col4 = st.columns(4)

# ============================================================
# PACIENTES
# ============================================================
with col1:
    if "id_paciente" in df_pacientes.columns:
        pacientes = (
            df_pacientes[
                "id_paciente"
            ].nunique()
        )
    else:
        pacientes = len(df_pacientes)

    st.metric(
        "👥 Pacientes",
        pacientes
    )

# ============================================================
# SCORE CLÍNICO
# ============================================================
with col2:
    if (
        "score_clinico"
        in df_pacientes.columns
    ):
        score_medio = (
            df_pacientes[
                "score_clinico"
            ].mean()
        )
        st.metric(
            "🩺 Score Clínico Médio",
            f"{score_medio:.1f}"
        )
    else:
        st.metric(
            "🩺 Score Clínico Médio",
            "N/D"
        )

# ============================================================
# SCORE LPP
# ============================================================
with col3:
    if (
        "score_lpp"
        in df_pacientes.columns
    ):
        lpp_medio = (
            df_pacientes[
                "score_lpp"
            ].mean()
        )
        st.metric(
            "🩹 Score LPP Médio",
            f"{lpp_medio:.1f}"
        )
    else:
        st.metric(
            "🩹 Score LPP Médio",
            "N/D"
        )

# ============================================================
# ALERTAS
# ============================================================
with col4:
    if (
        "quantidade_alertas"
        in df_pacientes.columns
    ):
        pacientes_com_alerta = (
            df_pacientes[
                df_pacientes[
                    "quantidade_alertas"
                ] > 0
            ]
            [
                "id_paciente"
            ]
            .nunique()
        )
        st.metric(
            "⚠️ Pacientes com Alertas",
            pacientes_com_alerta
        )
    else:
        st.metric(
            "⚠️ Pacientes com Alertas",
            "N/D"
        )


# ============================================================
# RESUMO TEMPORAL
# ============================================================

st.divider()

st.subheader(
    "🕒 Informações da Base"
)

col1, col2, col3, col4 = st.columns(4)

# ============================================================
# TOTAL DE REGISTROS
# ============================================================
with col1:
    st.metric(
        "📊 Registros Filtrados",
        f"{len(df_filtrado):,}"
        .replace(",", ".")
    )

# ============================================================
# TOTAL PACIENTES
# ============================================================
with col2:
    st.metric(
        "👥 Pacientes Únicos",
        len(df_pacientes)
    )

# ============================================================
# REGISTROS POR PACIENTE
# ============================================================
with col3:
    if len(df_pacientes) > 0:
        media_registros = (
            len(df_filtrado)
            /
            len(df_pacientes)
        )
        st.metric(
            "⏱️ Registros/Paciente",
            f"{media_registros:.1f}"
        )
    else:
        st.metric(
            "⏱️ Registros/Paciente",
            "N/D"
        )

# ============================================================
# PERÍODO
# ============================================================
with col4:
    if (
        "timestamp"
        in df_filtrado.columns
    ):
        timestamps_validos = (
            df_filtrado[
                "timestamp"
            ].dropna()
        )
        if not timestamps_validos.empty:
            inicio = (
                timestamps_validos.min()
            )
            fim = (
                timestamps_validos.max()
            )
            st.metric(
                "📅 Período",
                f"{inicio:%d/%m} - {fim:%d/%m}"
            )
        else:
            st.metric(
                "📅 Período",
                "N/D"
            )
    else:
        st.metric(
            "📅 Período",
            "N/D"
        )


# ============================================================
# DISTRIBUIÇÃO DE RISCOS
# ============================================================

st.divider()

st.subheader(
    "⚠️ Distribuição de Riscos"
)

st.caption(
    """
    Os gráficos apresentam a situação mais recente
    de cada paciente.
    """
)

col1, col2 = st.columns(2)

# ============================================================
# CLASSIFICAÇÃO CLÍNICA
# ============================================================
with col1:
    st.markdown(
        "### 🩺 Classificação Clínica"
    )
    if (
        "classificacao_clinica"
        in df_pacientes.columns
    ):
        df_clinica_counts = (
            df_pacientes[
                "classificacao_clinica"
            ]
            .value_counts()
            .reset_index()
        )
        df_clinica_counts.columns = [
            "Classificação",
            "Quantidade de Pacientes"
        ]
        fig_clinica = px.bar(
            df_clinica_counts,
            x="Classificação",
            y="Quantidade de Pacientes",
            text="Quantidade de Pacientes",
            color="Classificação"
        )
        fig_clinica.update_traces(
            textposition="outside"
        )
        fig_clinica.update_layout(
            showlegend=False,
            margin=dict(
                t=30,
                b=20,
                l=20,
                r=20
            ),
            height=350
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

# ============================================================
# CLASSIFICAÇÃO LPP
# ============================================================
with col2:
    st.markdown(
        "### 🩹 Risco de Lesão por Pressão"
    )
    if (
        "classificacao_lpp"
        in df_pacientes.columns
    ):
        df_lpp_counts = (
            df_pacientes[
                "classificacao_lpp"
            ]
            .value_counts()
            .reset_index()
        )
        df_lpp_counts.columns = [
            "Classificação",
            "Quantidade de Pacientes"
        ]
        fig_lpp = px.bar(
            df_lpp_counts,
            x="Classificação",
            y="Quantidade de Pacientes",
            text="Quantidade de Pacientes",
            color="Classificação"
        )
        fig_lpp.update_traces(
            textposition="outside"
        )
        fig_lpp.update_layout(
            showlegend=False,
            margin=dict(
                t=30,
                b=20,
                l=20,
                r=20
            ),
            height=350
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


# ============================================================
# PRIORIDADE
# ============================================================

st.divider()

st.subheader(
    "🎯 Distribuição da Prioridade"
)

st.caption(
    """
    Distribuição dos pacientes de acordo com
    o índice de prioridade calculado pelo motor analítico.
    """
)

if (
    "classificacao_prioridade"
    in df_pacientes.columns
):
    df_prioridade_counts = (
        df_pacientes[
            "classificacao_prioridade"
        ]
        .value_counts()
        .reset_index()
    )
    df_prioridade_counts.columns = [
        "Prioridade",
        "Quantidade de Pacientes"
    ]
    fig_prioridade = px.bar(
        df_prioridade_counts,
        x="Prioridade",
        y="Quantidade de Pacientes",
        text="Quantidade de Pacientes",
        color="Prioridade"
    )
    fig_prioridade.update_traces(
        textposition="outside"
    )
    fig_prioridade.update_layout(
        showlegend=False,
        height=350,
        margin=dict(
            t=30,
            b=20,
            l=20,
            r=20
        )
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
# TABELA DE PACIENTES
# ============================================================

st.divider()

st.subheader(
    "🚨 Situação Atual dos Pacientes"
)

st.caption(
    """
    Esta tabela apresenta o último registro disponível
    de cada paciente.
    """
)

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

if (
    not df_pacientes.empty
    and
    "indice_prioridade"
    in df_pacientes.columns
):
    df_exibicao = (
        df_pacientes
        .sort_values(
            by="indice_prioridade",
            ascending=False
        )
    )
else:
    df_exibicao = df_pacientes.copy()

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

st.divider()

st.subheader(
    "🕒 Histórico de Registros"
)

st.caption(
    """
    Diferentemente dos gráficos anteriores,
    esta tabela mantém os registros temporais.
    """
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

    if "timestamp" in df_historico.columns:
        df_historico = (
            df_historico
            .sort_values(
                by="timestamp",
                ascending=False
            )
        )

    st.dataframe(
        df_historico[
            colunas_historico_validas
        ],
        use_container_width=True,
        hide_index=True
    )
    st.caption(
        f"Total de registros históricos: {len(df_historico)}"
    )


# ============================================================
# DIAGNÓSTICO TÉCNICO
# ============================================================

st.divider()

with st.expander(
    "🔬 Status e Diagnóstico Técnico",
    expanded=False
):
    st.write(
        "### Estrutura dos dados"
    )
    st.write(
        f"**Registros totais da base:** {len(df):,}"
        .replace(",", ".")
    )
    st.write(
        f"**Registros após filtros:** {len(df_filtrado):,}"
        .replace(",", ".")
    )
    st.write(
        f"**Pacientes únicos após filtros:** {len(df_pacientes)}"
    )
    if len(df_pacientes) > 0:
        media = (
            len(df_filtrado)
            /
            len(df_pacientes)
        )
        st.write(
            f"**Média de registros por paciente:** {media:.2f}"
        )
    st.write(
        "### Colunas disponíveis"
    )
    st.write(
        list(df.columns)
    )


# ============================================================
# AVISO ACADÊMICO
# ============================================================

st.divider()

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