# ============================================================
# VISÃO GERAL DA UTI
# UTI INTELLIGENT CARE
#
# Painel executivo com síntese clínica, preventiva e operacional.
# As análises detalhadas permanecem nas páginas especializadas.
# ============================================================

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_data
from utils.analytics import processar_dados
from utils.risk_engine import processar_riscos
from utils.styling import (
    aplicar_estilo,
    topo_produto,
    navegacao_topo,
    cabecalho_pagina,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Visão Geral | UTI Intelligent Care",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Visão geral")


# ============================================================
# CSS DA PÁGINA
# ============================================================

st.markdown(
    """
    <style>
    .overview-section-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:8px 0 4px 0;
    }

    .overview-section-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:12px;
    }

    .overview-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:15px;
        padding:18px 20px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
    }

    .overview-small-title {
        color:#173E59;
        font-size:17px;
        font-weight:800;
        margin-bottom:6px;
    }

    .overview-small-text {
        color:#647F91;
        font-size:14px;
        line-height:1.5;
    }

    .overview-number {
        color:#0D2A45;
        font-size:31px;
        font-weight:850;
        letter-spacing:-0.03em;
        margin-top:7px;
        margin-bottom:2px;
    }

    .overview-status {
        color:#6F8798;
        font-size:13px;
        font-weight:650;
    }

    .overview-insight {
        background:#F6FAFC;
        border:1px solid #DCE8EF;
        border-radius:12px;
        padding:14px 16px;
        color:#526F83;
        font-size:14px;
        line-height:1.55;
        margin-top:10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def tema_plotly(fig, altura=350):
    fig.update_layout(
        title_text="",
        height=altura,
        margin=dict(l=20, r=20, t=18, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Segoe UI, Arial, sans-serif",
            size=15,
            color="#284A62",
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=14,
            font_family="Segoe UI",
        ),
    )
    return fig


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    return (
        str(valor)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def formatar_categoria(valor):
    if pd.isna(valor):
        return "Não informado"
    return (
        str(valor)
        .replace("_", " ")
        .strip()
        .capitalize()
    )


def detectar_coluna(dataframe, opcoes):
    for coluna in opcoes:
        if coluna in dataframe.columns:
            return coluna
    return None


def carregar_operacional():
    raiz = Path(__file__).resolve().parent.parent

    candidatos = [
        raiz / "data" / "UTI_operacional.csv",
        raiz / "data" / "uti_operacional.csv",
    ]

    for caminho in candidatos:
        if caminho.exists():
            try:
                op = pd.read_csv(
                    caminho,
                    sep=";",
                    encoding="utf-8-sig",
                )

                if op.empty:
                    continue

                if "timestamp" in op.columns:
                    op["timestamp_dt"] = pd.to_datetime(
                        op["timestamp"],
                        errors="coerce",
                        dayfirst=True,
                    )
                    op = op.sort_values("timestamp_dt")

                return op

            except Exception:
                continue

    return pd.DataFrame()


# ============================================================
# DADOS CLÍNICOS
# ============================================================

try:
    df = load_data().copy()
except Exception as e:
    st.error("Não foi possível carregar os dados clínicos.")
    st.exception(e)
    st.stop()

if df.empty:
    st.error("A base clínica está vazia.")
    st.stop()


# ============================================================
# PROCESSAMENTO ANALÍTICO
# ============================================================

try:
    df = processar_dados(df)
except Exception:
    pass

try:
    df = processar_riscos(df)
except Exception:
    pass


# ============================================================
# TIMESTAMP
# ============================================================

if "timestamp" in df.columns:
    df["timestamp_dt"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        dayfirst=True,
    )
else:
    df["timestamp_dt"] = pd.NaT


# ============================================================
# ÚLTIMO REGISTRO POR PACIENTE
# ============================================================

if (
    "id_paciente" in df.columns
    and df["timestamp_dt"].notna().any()
):
    df_atual = (
        df
        .dropna(subset=["timestamp_dt"])
        .sort_values("timestamp_dt")
        .groupby("id_paciente", as_index=False)
        .tail(1)
        .copy()
    )
elif "id_paciente" in df.columns:
    df_atual = (
        df
        .drop_duplicates(
            subset="id_paciente",
            keep="last",
        )
        .copy()
    )
else:
    df_atual = df.copy()


# ============================================================
# COLUNAS ANALÍTICAS
# ============================================================

col_clinico = detectar_coluna(
    df_atual,
    [
        "classificacao_clinica",
        "nivel_risco_clinico",
    ],
)

col_lpp = detectar_coluna(
    df_atual,
    [
        "classificacao_lpp",
        "nivel_risco_LPP",
    ],
)

col_prioridade = detectar_coluna(
    df_atual,
    [
        "classificacao_prioridade",
    ],
)

col_score_clinico = detectar_coluna(
    df_atual,
    [
        "score_clinico",
        "score_risco_clinico",
    ],
)

col_score_lpp = detectar_coluna(
    df_atual,
    [
        "score_lpp",
        "risco_LPP",
    ],
)


# ============================================================
# MÉTRICAS CLÍNICAS
# ============================================================

total_pacientes = (
    int(df_atual["id_paciente"].nunique())
    if "id_paciente" in df_atual.columns
    else len(df_atual)
)


# Alertas ativos
if "quantidade_alertas" in df_atual.columns:
    alertas_ativos = int(
        pd.to_numeric(
            df_atual["quantidade_alertas"],
            errors="coerce",
        )
        .fillna(0)
        .sum()
    )
else:
    alertas_ativos = 0


# Pacientes prioritários
if col_prioridade:
    serie_prioridade = df_atual[col_prioridade].apply(normalizar_texto)

    mascara_prioridade = serie_prioridade.isin(
        [
            "alta",
            "alto",
            "muito_alta",
            "muito_alto",
            "critica",
            "crítica",
            "critico",
            "crítico",
        ]
    )

    pacientes_prioritarios = int(
        df_atual.loc[mascara_prioridade, "id_paciente"].nunique()
        if "id_paciente" in df_atual.columns
        else mascara_prioridade.sum()
    )
elif "indice_prioridade" in df_atual.columns:
    indice = pd.to_numeric(
        df_atual["indice_prioridade"],
        errors="coerce",
    )
    pacientes_prioritarios = int((indice >= 60).sum())
else:
    pacientes_prioritarios = 0


# LPP elevado
if col_lpp:
    serie_lpp = df_atual[col_lpp].apply(normalizar_texto)

    mascara_lpp = serie_lpp.isin(
        [
            "alto",
            "alta",
            "muito_alto",
            "muito_alta",
        ]
    )

    pacientes_lpp_elevado = int(
        df_atual.loc[mascara_lpp, "id_paciente"].nunique()
        if "id_paciente" in df_atual.columns
        else mascara_lpp.sum()
    )
else:
    pacientes_lpp_elevado = 0


# ============================================================
# MÉTRICAS OPERACIONAIS
# ============================================================

df_op = carregar_operacional()

ocupacao_atual = None
leitos_disponiveis = None
pacientes_enfermeiro = None

if not df_op.empty:

    op_atual = df_op.iloc[-1]

    if "taxa_ocupacao_pct" in op_atual.index:
        valor = pd.to_numeric(
            op_atual["taxa_ocupacao_pct"],
            errors="coerce",
        )
        if pd.notna(valor):
            ocupacao_atual = float(valor)

    if (
        "leitos_operacionais" in op_atual.index
        and "pacientes_internados" in op_atual.index
    ):
        operacionais = pd.to_numeric(
            op_atual["leitos_operacionais"],
            errors="coerce",
        )
        internados = pd.to_numeric(
            op_atual["pacientes_internados"],
            errors="coerce",
        )

        if pd.notna(operacionais) and pd.notna(internados):
            leitos_disponiveis = max(
                int(operacionais - internados),
                0,
            )

    if "pacientes_por_enfermeiro" in op_atual.index:
        valor = pd.to_numeric(
            op_atual["pacientes_por_enfermeiro"],
            errors="coerce",
        )
        if pd.notna(valor):
            pacientes_enfermeiro = float(valor)


# ============================================================
# CABEÇALHO
# ============================================================

cabecalho_pagina(
    "Visão Geral da UTI",
    (
        "Síntese executiva dos principais indicadores clínicos, "
        "preventivos e operacionais da unidade."
    ),
    secao="Panorama executivo",
    badge="Dados simulados",
)


# ============================================================
# KPIs EXECUTIVOS
# ============================================================

st.markdown(
    '<div class="overview-section-title">Situação atual da UTI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="overview-section-subtitle">
        Indicadores consolidados do registro mais recente de cada paciente
        e do último período operacional disponível.
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "Pacientes",
        total_pacientes,
    )

with k2:
    st.metric(
        "Ocupação",
        (
            f"{ocupacao_atual:.1f}%"
            if ocupacao_atual is not None
            else "N/D"
        ),
    )

with k3:
    st.metric(
        "Alta prioridade",
        pacientes_prioritarios,
    )

with k4:
    st.metric(
        "Risco LPP elevado",
        pacientes_lpp_elevado,
    )

with k5:
    st.metric(
        "Alertas ativos",
        alertas_ativos,
    )


# ============================================================
# PANORAMA CLÍNICO + RESUMO OPERACIONAL
# ============================================================

st.write("")

col_clin, col_op = st.columns(
    [1.25, 0.75],
    gap="large",
)


# ------------------------------------------------------------
# DISTRIBUIÇÃO CLÍNICA
# ------------------------------------------------------------

with col_clin:

    st.markdown(
        '<div class="overview-section-title">Panorama clínico</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="overview-section-subtitle">
            Distribuição da situação clínica atual dos pacientes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if col_clinico:

        clinica = (
            df_atual[col_clinico]
            .apply(formatar_categoria)
            .value_counts()
            .reset_index()
        )

        clinica.columns = [
            "Classificação",
            "Pacientes",
        ]

        fig_clinica = px.bar(
            clinica,
            x="Classificação",
            y="Pacientes",
        )

        fig_clinica.update_traces(
            marker_color="#4D8BC4",
            marker_line_width=0,
            text=clinica["Pacientes"],
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>%{y} paciente(s)"
                "<extra></extra>"
            ),
        )

        fig_clinica.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Pacientes",
        )

        fig_clinica.update_yaxes(
            gridcolor="#E7EEF3",
            zeroline=False,
            dtick=1,
        )

        fig_clinica.update_xaxes(
            showgrid=False,
        )

        tema_plotly(
            fig_clinica,
            altura=340,
        )

        st.plotly_chart(
            fig_clinica,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    else:
        st.info(
            "A classificação clínica não está disponível na base processada."
        )


# ------------------------------------------------------------
# RESUMO OPERACIONAL
# ------------------------------------------------------------

with col_op:

    st.markdown(
        '<div class="overview-section-title">Resumo operacional</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="overview-section-subtitle">
            Indicadores essenciais de capacidade assistencial.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not df_op.empty:

        ocup_texto = (
            f"{ocupacao_atual:.1f}%"
            if ocupacao_atual is not None
            else "N/D"
        )

        leitos_texto = (
            str(leitos_disponiveis)
            if leitos_disponiveis is not None
            else "N/D"
        )

        equipe_texto = (
            f"{pacientes_enfermeiro:.1f}"
            if pacientes_enfermeiro is not None
            else "N/D"
        )

        st.markdown(
            f"""
            <div class="overview-card">
                <div class="overview-small-title">Ocupação atual</div>
                <div class="overview-number">{ocup_texto}</div>
                <div class="overview-status">
                    Percentual de leitos operacionais ocupados
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        o1, o2 = st.columns(2)

        with o1:
            st.markdown(
                f"""
                <div class="overview-card">
                    <div class="overview-small-title">Leitos disponíveis</div>
                    <div class="overview-number">{leitos_texto}</div>
                    <div class="overview-status">no último período</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with o2:
            st.markdown(
                f"""
                <div class="overview-card">
                    <div class="overview-small-title">Pac./enfermeiro</div>
                    <div class="overview-number">{equipe_texto}</div>
                    <div class="overview-status">carga assistencial</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info(
            "Base operacional não encontrada. "
            "Os indicadores detalhados permanecem disponíveis "
            "quando `data/UTI_operacional.csv` estiver presente."
        )


# ============================================================
# TENDÊNCIA AGREGADA + MOTIVOS DE INTERNAÇÃO
# ============================================================

st.write("")

trend_col, diag_col = st.columns(
    [1.18, 0.82],
    gap="large",
)


# ------------------------------------------------------------
# TENDÊNCIA CLÍNICA AGREGADA
# ------------------------------------------------------------

with trend_col:

    st.markdown(
        '<div class="overview-section-title">Tendência clínica da UTI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="overview-section-subtitle">
            Evolução agregada do score clínico ao longo do período.
        </div>
        """,
        unsafe_allow_html=True,
    )

    coluna_score_hist = detectar_coluna(
        df,
        [
            "score_clinico",
            "score_risco_clinico",
        ],
    )

    if (
        coluna_score_hist
        and df["timestamp_dt"].notna().any()
    ):

        serie_hist = (
            df[
                [
                    "timestamp_dt",
                    coluna_score_hist,
                ]
            ]
            .copy()
        )

        serie_hist[coluna_score_hist] = pd.to_numeric(
            serie_hist[coluna_score_hist],
            errors="coerce",
        )

        serie_hist = (
            serie_hist
            .dropna()
            .groupby("timestamp_dt", as_index=False)
            .agg(
                score_medio=(coluna_score_hist, "mean")
            )
            .sort_values("timestamp_dt")
            .tail(72)
        )

        if not serie_hist.empty:

            fig_trend = go.Figure()

            fig_trend.add_trace(
                go.Scatter(
                    x=serie_hist["timestamp_dt"],
                    y=serie_hist["score_medio"],
                    mode="lines",
                    line=dict(
                        color="#2B84C5",
                        width=3,
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(43,132,197,.08)",
                    hovertemplate=(
                        "<b>%{x|%d/%m %H:%M}</b>"
                        "<br>Score clínico médio: %{y:.1f}"
                        "<extra></extra>"
                    ),
                )
            )

            fig_trend.update_layout(
                showlegend=False,
                xaxis_title="Período",
                yaxis_title="Score clínico médio",
            )

            fig_trend.update_yaxes(
                gridcolor="#E7EEF3",
                zeroline=False,
            )

            fig_trend.update_xaxes(
                gridcolor="#F0F4F7",
            )

            tema_plotly(
                fig_trend,
                altura=345,
            )

            st.plotly_chart(
                fig_trend,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        else:
            st.info(
                "Não há registros suficientes para gerar a tendência clínica."
            )

    else:
        st.info(
            "Score clínico temporal não disponível."
        )


# ------------------------------------------------------------
# MOTIVOS DE INTERNAÇÃO
# ------------------------------------------------------------

with diag_col:

    st.markdown(
        '<div class="overview-section-title">Motivos de internação</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="overview-section-subtitle">
            Principais diagnósticos dos pacientes atualmente monitorados.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "diagnostico_principal" in df_atual.columns:

        diagnosticos = (
            df_atual["diagnostico_principal"]
            .apply(formatar_categoria)
            .value_counts()
            .head(6)
            .sort_values(ascending=True)
            .reset_index()
        )

        diagnosticos.columns = [
            "Diagnóstico",
            "Pacientes",
        ]

        fig_diag = px.bar(
            diagnosticos,
            x="Pacientes",
            y="Diagnóstico",
            orientation="h",
        )

        fig_diag.update_traces(
            marker_color="#7C91C9",
            marker_line_width=0,
            text=diagnosticos["Pacientes"],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>%{x} paciente(s)"
                "<extra></extra>"
            ),
        )

        fig_diag.update_layout(
            showlegend=False,
            xaxis_title="Pacientes",
            yaxis_title="",
        )

        fig_diag.update_xaxes(
            gridcolor="#E7EEF3",
            zeroline=False,
            dtick=1,
        )

        fig_diag.update_yaxes(
            showgrid=False,
        )

        tema_plotly(
            fig_diag,
            altura=345,
        )

        st.plotly_chart(
            fig_diag,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    else:
        st.info(
            "Diagnóstico principal não disponível."
        )


# ============================================================
# PACIENTES QUE EXIGEM ATENÇÃO
# ============================================================

st.write("")

st.markdown(
    '<div class="overview-section-title">Pacientes que exigem atenção</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="overview-section-subtitle">
        Os cinco pacientes com maior prioridade global no registro atual.
        O detalhamento completo permanece na Central de Alertas.
    </div>
    """,
    unsafe_allow_html=True,
)


df_rank = df_atual.copy()

if "indice_prioridade" in df_rank.columns:
    df_rank["_ordem"] = pd.to_numeric(
        df_rank["indice_prioridade"],
        errors="coerce",
    ).fillna(0)

elif col_score_clinico:
    df_rank["_ordem"] = pd.to_numeric(
        df_rank[col_score_clinico],
        errors="coerce",
    ).fillna(0)

else:
    df_rank["_ordem"] = 0


top5 = (
    df_rank
    .sort_values(
        "_ordem",
        ascending=False,
    )
    .head(5)
    .copy()
)


tabela = pd.DataFrame()

if "id_paciente" in top5.columns:
    tabela["Paciente"] = (
        "P"
        + pd.to_numeric(
            top5["id_paciente"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
        .astype(str)
        .str.zfill(2)
    )

if col_clinico:
    tabela["Situação clínica"] = (
        top5[col_clinico]
        .apply(formatar_categoria)
        .values
    )

if col_lpp:
    tabela["Risco LPP"] = (
        top5[col_lpp]
        .apply(formatar_categoria)
        .values
    )

if "quantidade_alertas" in top5.columns:
    tabela["Alertas"] = (
        pd.to_numeric(
            top5["quantidade_alertas"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
        .values
    )

if col_prioridade:
    tabela["Prioridade"] = (
        top5[col_prioridade]
        .apply(formatar_categoria)
        .values
    )
elif "indice_prioridade" in top5.columns:
    tabela["Índice de prioridade"] = (
        pd.to_numeric(
            top5["indice_prioridade"],
            errors="coerce",
        )
        .round(1)
        .values
    )

if not tabela.empty:
    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        height=235,
    )
else:
    st.info(
        "Não há informações suficientes para montar a priorização."
    )


# ============================================================
# ATALHOS ANALÍTICOS
# ============================================================

st.write("")

a1, a2, a3 = st.columns(3)

with a1:
    st.page_link(
        "pages/2_Monitoramento_Clinico.py",
        label="Analisar paciente individual",
        use_container_width=True,
    )

with a2:
    st.page_link(
        "pages/5_Central_de_Alertas.py",
        label="Abrir Central de Alertas",
        use_container_width=True,
    )

with a3:
    st.page_link(
        "pages/4_Gestao_Operacional.py",
        label="Ver Gestão Operacional",
        use_container_width=True,
    )


# ============================================================
# CONTEXTO
# ============================================================

st.markdown(
    """
    <div class="overview-insight">
        <b>Leitura da página:</b> esta visão foi intencionalmente
        simplificada para apresentar apenas o panorama da UTI.
        Risco de LPP, alertas, monitoramento individual e desempenho
        operacional possuem páginas próprias para análise detalhada.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Protótipo acadêmico com dados simulados. "
    "Os indicadores apresentados possuem finalidade conceitual "
    "e não substituem avaliação clínica ou protocolos institucionais."
)
