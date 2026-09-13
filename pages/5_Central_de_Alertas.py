# ============================================================
# GESTÃO OPERACIONAL DA UTI
# UTI INTELLIGENT CARE
#
# Integra dados clínicos simulados e dados operacionais
# simulados para acompanhamento da capacidade e do fluxo da UTI.
# ============================================================

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_data
from utils.styling import aplicar_estilo, topo_produto, navegacao_topo


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Gestão Operacional | UTI Intelligent Care",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Operacional")


# ============================================================
# CSS EXCLUSIVO DA PÁGINA
# ============================================================

st.markdown(
    """
    <style>
    .op-header {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:24px;
        padding:12px 2px 20px 2px;
    }

    .op-header-left {
        display:flex;
        align-items:center;
        gap:16px;
    }

    .op-header-icon {
        width:58px;
        height:58px;
        border-radius:18px;
        display:grid;
        place-items:center;
        background:#EAF4FA;
        border:1px solid #D4E6F1;
        color:#1F6EA5;
        font-size:25px;
        font-weight:850;
    }

    .op-title {
        color:#0D2A45;
        font-size:34px;
        line-height:1.15;
        font-weight:850;
        letter-spacing:-0.03em;
        margin:0;
    }

    .op-subtitle {
        color:#667F92;
        font-size:17px;
        line-height:1.5;
        margin-top:6px;
    }

    .op-info {
        max-width:350px;
        background:#EEF7FC;
        border:1px solid #D3E7F2;
        border-radius:12px;
        padding:12px 15px;
        color:#45657C;
        font-size:14px;
        line-height:1.45;
    }

    .op-section-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:8px 0 4px 0;
    }

    .op-section-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:12px;
    }

    .op-note {
        background:#F7FAFC;
        border:1px solid #DCE8EF;
        border-radius:12px;
        padding:13px 15px;
        color:#587287;
        font-size:14px;
        line-height:1.5;
        margin-top:8px;
    }

    .op-alert {
        background:#FFF4E7;
        border:1px solid #F2D7B2;
        border-left:5px solid #F2A34A;
        border-radius:12px;
        padding:14px 16px;
        color:#6D563B;
        font-size:15px;
        line-height:1.5;
        margin-top:10px;
    }

    .op-good {
        background:#EFF9F4;
        border:1px solid #CFEADC;
        border-left:5px solid #159A7A;
        border-radius:12px;
        padding:14px 16px;
        color:#45685D;
        font-size:15px;
        line-height:1.5;
        margin-top:10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def localizar_base_operacional():
    """
    Procura a base operacional dentro da pasta data do projeto.
    Aceita variações simples de nome para facilitar a substituição.
    """
    raiz = Path(__file__).resolve().parent.parent

    candidatos = [
        raiz / "data" / "UTI_operacional.csv",
        raiz / "data" / "uti_operacional.csv",
        raiz / "UTI_operacional.csv",
    ]

    for caminho in candidatos:
        if caminho.exists():
            return caminho

    return None


@st.cache_data
def carregar_operacional(caminho_str):
    caminho = Path(caminho_str)
    return pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
    )


def converter_data_hora(serie):
    """
    Conversão robusta para datas em diferentes formatos.
    """
    convertido = pd.to_datetime(
        serie,
        errors="coerce",
        dayfirst=True,
    )
    return convertido


def tema_plotly(fig, altura=350):
    """
    Mantém os gráficos coerentes com a identidade visual do dashboard.
    O título interno fica explicitamente vazio para não aparecer 'undefined'.
    """
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


def formatar_diagnostico(texto):
    if pd.isna(texto):
        return "Não informado"

    return (
        str(texto)
        .replace("_", " ")
        .strip()
        .capitalize()
    )


# ============================================================
# CARREGAMENTO DAS BASES
# ============================================================

# Base clínica
try:
    df_clinico = load_data().copy()
except Exception as e:
    st.error("Não foi possível carregar a base clínica.")
    st.exception(e)
    st.stop()

if df_clinico.empty:
    st.error("A base clínica está vazia.")
    st.stop()


# Base operacional
caminho_operacional = localizar_base_operacional()

if caminho_operacional is None:
    st.error(
        """
        A base operacional não foi encontrada.

        Coloque o arquivo **UTI_operacional.csv** dentro da pasta:

        `data/UTI_operacional.csv`
        """
    )
    st.stop()

try:
    df_op = carregar_operacional(str(caminho_operacional)).copy()
except Exception as e:
    st.error("Não foi possível carregar a base operacional.")
    st.exception(e)
    st.stop()

if df_op.empty:
    st.error("A base operacional está vazia.")
    st.stop()


# ============================================================
# PREPARAÇÃO TEMPORAL
# ============================================================

df_op["timestamp_dt"] = converter_data_hora(df_op["timestamp"])

if "timestamp" in df_clinico.columns:
    df_clinico["timestamp_dt"] = converter_data_hora(
        df_clinico["timestamp"]
    )

df_op = df_op.dropna(subset=["timestamp_dt"]).sort_values("timestamp_dt")

if df_op.empty:
    st.error("Não foi possível interpretar as datas da base operacional.")
    st.stop()


# ============================================================
# REGISTRO OPERACIONAL ATUAL
# ============================================================

op_atual = df_op.iloc[-1]

capacidade_total = int(op_atual["capacidade_total_leitos"])
leitos_bloqueados = int(op_atual["leitos_bloqueados"])
leitos_operacionais = int(op_atual["leitos_operacionais"])
pacientes_internados = int(op_atual["pacientes_internados"])
taxa_ocupacao = float(op_atual["taxa_ocupacao_pct"])
enfermeiros_turno = int(op_atual["enfermeiros_turno"])
pacientes_enfermeiro = float(op_atual["pacientes_por_enfermeiro"])


# ============================================================
# ÚLTIMO REGISTRO CLÍNICO DE CADA PACIENTE
# ============================================================

if (
    "timestamp_dt" in df_clinico.columns
    and df_clinico["timestamp_dt"].notna().any()
):
    df_pacientes = (
        df_clinico
        .dropna(subset=["timestamp_dt"])
        .sort_values("timestamp_dt")
        .groupby("id_paciente", as_index=False)
        .tail(1)
        .copy()
    )
else:
    df_pacientes = (
        df_clinico
        .drop_duplicates(
            subset="id_paciente",
            keep="last",
        )
        .copy()
    )


# ============================================================
# MÉTRICAS DERIVADAS
# ============================================================

if "tempo_internacao_horas" in df_pacientes.columns:
    permanencia_media_dias = (
        pd.to_numeric(
            df_pacientes["tempo_internacao_horas"],
            errors="coerce",
        )
        .mean()
        / 24
    )
elif "dia_internacao" in df_pacientes.columns:
    permanencia_media_dias = (
        pd.to_numeric(
            df_pacientes["dia_internacao"],
            errors="coerce",
        )
        .mean()
    )
else:
    permanencia_media_dias = float("nan")


# Admissões nas últimas 48h da base operacional
data_limite_48h = df_op["timestamp_dt"].max() - pd.Timedelta(hours=48)

admissoes_48h = int(
    pd.to_numeric(
        df_op.loc[
            df_op["timestamp_dt"] >= data_limite_48h,
            "admissoes_turno",
        ],
        errors="coerce",
    )
    .fillna(0)
    .sum()
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="op-header">
        <div class="op-header-left">
            <div class="op-header-icon">▦</div>
            <div>
                <div class="op-title">Gestão Operacional da UTI</div>
                <div class="op-subtitle">
                    Visão integrada de capacidade, fluxo de pacientes,
                    permanência e carga assistencial.
                </div>
            </div>
        </div>
        <div class="op-info">
            <b>Dados operacionais simulados</b><br>
            Esta página combina a base clínica do protótipo com
            indicadores operacionais sintéticos da UTI.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPIs PRINCIPAIS
# ============================================================

st.markdown(
    '<div class="op-section-title">Situação operacional atual</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="op-section-subtitle">Indicadores referentes ao período mais recente disponível nas bases simuladas.</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Ocupação da UTI",
        f"{taxa_ocupacao:.1f}%",
        help=(
            f"{pacientes_internados} pacientes para "
            f"{leitos_operacionais} leitos operacionais."
        ),
    )

with k2:
    if pd.notna(permanencia_media_dias):
        st.metric(
            "Permanência média",
            f"{permanencia_media_dias:.1f} dias",
        )
    else:
        st.metric(
            "Permanência média",
            "N/D",
        )

with k3:
    st.metric(
        "Pacientes / enfermeiro",
        f"{pacientes_enfermeiro:.1f}",
        help=(
            f"{pacientes_internados} pacientes e "
            f"{enfermeiros_turno} enfermeiros no turno atual."
        ),
    )

with k4:
    st.metric(
        "Admissões nas últimas 48h",
        f"{admissoes_48h}",
    )


st.write("")


# ============================================================
# OCUPAÇÃO + CARGA POR TURNO
# ============================================================

col_ocupacao, col_turno = st.columns(
    [1.15, 0.85],
    gap="large",
)


# ------------------------------------------------------------
# EVOLUÇÃO DA OCUPAÇÃO
# ------------------------------------------------------------

with col_ocupacao:

    st.markdown(
        '<div class="op-section-title">Ocupação ao longo do tempo</div>',
        unsafe_allow_html=True,
    )

    ocupacao_diaria = (
        df_op
        .assign(
            dia=df_op["timestamp_dt"].dt.date
        )
        .groupby("dia", as_index=False)
        .agg(
            ocupacao_media=("taxa_ocupacao_pct", "mean"),
            ocupacao_maxima=("taxa_ocupacao_pct", "max"),
        )
    )

    ocupacao_diaria["dia_label"] = pd.to_datetime(
        ocupacao_diaria["dia"]
    ).dt.strftime("%d/%m")

    fig_ocupacao = go.Figure()

    fig_ocupacao.add_trace(
        go.Scatter(
            x=ocupacao_diaria["dia_label"],
            y=ocupacao_diaria["ocupacao_media"],
            mode="lines+markers",
            name="Ocupação média",
            line=dict(
                color="#2B84C5",
                width=3,
            ),
            marker=dict(
                size=7,
                color="#2B84C5",
                line=dict(
                    color="#FFFFFF",
                    width=1,
                ),
            ),
            fill="tozeroy",
            fillcolor="rgba(43,132,197,.10)",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Ocupação média: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig_ocupacao.add_hline(
        y=90,
        line_dash="dash",
        line_color="#E8A045",
        annotation_text="90%",
        annotation_position="top right",
    )

    fig_ocupacao.update_layout(
        xaxis_title="Data",
        yaxis_title="Ocupação (%)",
        showlegend=False,
    )

    fig_ocupacao.update_yaxes(
        range=[
            0,
            max(
                105,
                float(
                    ocupacao_diaria["ocupacao_maxima"].max()
                )
                + 5,
            ),
        ],
        gridcolor="#E7EEF3",
        zeroline=False,
    )

    fig_ocupacao.update_xaxes(
        showgrid=False,
    )

    tema_plotly(
        fig_ocupacao,
        altura=365,
    )

    st.plotly_chart(
        fig_ocupacao,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ------------------------------------------------------------
# CARGA POR TURNO
# ------------------------------------------------------------

with col_turno:

    st.markdown(
        '<div class="op-section-title">Carga assistencial por turno</div>',
        unsafe_allow_html=True,
    )

    carga_turno = (
        df_op
        .groupby("turno", as_index=False)
        .agg(
            pacientes_por_enfermeiro=("pacientes_por_enfermeiro", "mean")
        )
    )

    ordem_turnos = ["Manhã", "Tarde", "Noite"]

    carga_turno["turno"] = pd.Categorical(
        carga_turno["turno"],
        categories=ordem_turnos,
        ordered=True,
    )

    carga_turno = carga_turno.sort_values("turno")

    fig_turno = px.bar(
        carga_turno,
        x="turno",
        y="pacientes_por_enfermeiro",
        labels={
            "turno": "Turno",
            "pacientes_por_enfermeiro": "Pacientes / enfermeiro",
        },
    )

    fig_turno.update_traces(
        marker_color="#4B8ED1",
        marker_line_width=0,
        text=[
            f"{v:.1f}"
            for v in carga_turno["pacientes_por_enfermeiro"]
        ],
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>Pacientes/enfermeiro: %{y:.1f}"
            "<extra></extra>"
        ),
    )

    fig_turno.update_layout(
        showlegend=False,
        xaxis_title="Turno",
        yaxis_title="Pacientes / enfermeiro",
    )

    fig_turno.update_yaxes(
        gridcolor="#E7EEF3",
        zeroline=False,
    )

    fig_turno.update_xaxes(
        showgrid=False,
    )

    tema_plotly(
        fig_turno,
        altura=365,
    )

    st.plotly_chart(
        fig_turno,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# CAPACIDADE ATUAL + FLUXO
# ============================================================

st.write("")

col_leitos, col_fluxo = st.columns(
    [0.82, 1.18],
    gap="large",
)


# ------------------------------------------------------------
# DISTRIBUIÇÃO DOS LEITOS
# ------------------------------------------------------------

with col_leitos:

    st.markdown(
        '<div class="op-section-title">Capacidade atual dos leitos</div>',
        unsafe_allow_html=True,
    )

    leitos_disponiveis = max(
        leitos_operacionais - pacientes_internados,
        0,
    )

    ocupados_reais = min(
        pacientes_internados,
        leitos_operacionais,
    )

    df_leitos = pd.DataFrame(
        {
            "Status": [
                "Ocupados",
                "Disponíveis",
                "Bloqueados",
            ],
            "Leitos": [
                ocupados_reais,
                leitos_disponiveis,
                leitos_bloqueados,
            ],
        }
    )

    fig_leitos = go.Figure(
        data=[
            go.Pie(
                labels=df_leitos["Status"],
                values=df_leitos["Leitos"],
                hole=0.62,
                marker=dict(
                    colors=[
                        "#79AEE3",
                        "#BFE5D6",
                        "#E6D7F3",
                    ]
                ),
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b>"
                    "<br>%{value} leito(s)"
                    "<br>%{percent}"
                    "<extra></extra>"
                ),
            )
        ]
    )

    fig_leitos.add_annotation(
        x=0.5,
        y=0.54,
        text=f"<b>{capacidade_total}</b>",
        showarrow=False,
        font=dict(
            size=28,
            color="#0D2A45",
        ),
    )

    fig_leitos.add_annotation(
        x=0.5,
        y=0.42,
        text="leitos",
        showarrow=False,
        font=dict(
            size=14,
            color="#6C8597",
        ),
    )

    fig_leitos.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.03,
        ),
    )

    tema_plotly(
        fig_leitos,
        altura=350,
    )

    st.plotly_chart(
        fig_leitos,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ------------------------------------------------------------
# ADMISSÕES E ALTAS
# ------------------------------------------------------------

with col_fluxo:

    st.markdown(
        '<div class="op-section-title">Fluxo de pacientes</div>',
        unsafe_allow_html=True,
    )

    fluxo_diario = (
        df_op
        .assign(
            dia=df_op["timestamp_dt"].dt.date
        )
        .groupby("dia", as_index=False)
        .agg(
            Admissões=("admissoes_turno", "sum"),
            Altas=("altas_turno", "sum"),
        )
    )

    fluxo_diario["Data"] = pd.to_datetime(
        fluxo_diario["dia"]
    ).dt.strftime("%d/%m")

    fluxo_long = fluxo_diario.melt(
        id_vars="Data",
        value_vars=[
            "Admissões",
            "Altas",
        ],
        var_name="Movimento",
        value_name="Pacientes",
    )

    fig_fluxo = px.bar(
        fluxo_long,
        x="Data",
        y="Pacientes",
        color="Movimento",
        barmode="group",
        color_discrete_map={
            "Admissões": "#5B8FD5",
            "Altas": "#52B8A0",
        },
    )

    fig_fluxo.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>%{fullData.name}: %{y}"
            "<extra></extra>"
        ),
    )

    fig_fluxo.update_layout(
        xaxis_title="Data",
        yaxis_title="Número de pacientes",
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
        ),
    )

    fig_fluxo.update_yaxes(
        gridcolor="#E7EEF3",
        zeroline=False,
        dtick=1,
    )

    fig_fluxo.update_xaxes(
        showgrid=False,
    )

    tema_plotly(
        fig_fluxo,
        altura=350,
    )

    st.plotly_chart(
        fig_fluxo,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# PERMANÊNCIA + LEITOS BLOQUEADOS
# ============================================================

st.write("")

col_permanencia, col_diag = st.columns(
    2,
    gap="large",
)


# ------------------------------------------------------------
# TEMPO DE PERMANÊNCIA
# ------------------------------------------------------------

with col_permanencia:

    st.markdown(
        '<div class="op-section-title">Tempo de permanência dos pacientes</div>',
        unsafe_allow_html=True,
    )

    if "tempo_internacao_horas" in df_pacientes.columns:
        permanencia = (
            pd.to_numeric(
                df_pacientes["tempo_internacao_horas"],
                errors="coerce",
            )
            / 24
        )
    else:
        permanencia = pd.to_numeric(
            df_pacientes.get(
                "dia_internacao",
                pd.Series(dtype=float),
            ),
            errors="coerce",
        )

    permanencia = permanencia.dropna()

    if not permanencia.empty:

        faixas = pd.cut(
            permanencia,
            bins=[
                -float("inf"),
                3,
                7,
                14,
                float("inf"),
            ],
            labels=[
                "Até 3 dias",
                "4–7 dias",
                "8–14 dias",
                "> 14 dias",
            ],
        )

        dist_perm = (
            faixas
            .value_counts(sort=False)
            .reset_index()
        )

        dist_perm.columns = [
            "Faixa",
            "Pacientes",
        ]

        fig_perm = px.bar(
            dist_perm,
            x="Faixa",
            y="Pacientes",
        )

        fig_perm.update_traces(
            marker_color="#80A9D8",
            marker_line_width=0,
            text=dist_perm["Pacientes"],
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>%{y} paciente(s)"
                "<extra></extra>"
            ),
        )

        fig_perm.update_layout(
            xaxis_title="Tempo de permanência",
            yaxis_title="Pacientes",
            showlegend=False,
        )

        fig_perm.update_yaxes(
            gridcolor="#E7EEF3",
            zeroline=False,
            dtick=1,
        )

        fig_perm.update_xaxes(
            showgrid=False,
        )

        tema_plotly(
            fig_perm,
            altura=335,
        )

        st.plotly_chart(
            fig_perm,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    else:
        st.info(
            "Não há informação suficiente para calcular o tempo de permanência."
        )


# ------------------------------------------------------------
# LEITOS BLOQUEADOS AO LONGO DO PERÍODO
# ------------------------------------------------------------

with col_diag:

    st.markdown(
        '<div class="op-section-title">Leitos bloqueados ao longo do período</div>',
        unsafe_allow_html=True,
    )

    if (
        "leitos_bloqueados" in df_op.columns
        and "timestamp_dt" in df_op.columns
    ):

        bloqueios = (
            df_op
            .dropna(subset=["timestamp_dt"])
            .assign(
                dia=df_op["timestamp_dt"].dt.date
            )
            .groupby("dia", as_index=False)
            .agg(
                leitos_bloqueados=("leitos_bloqueados", "max")
            )
        )

        bloqueios["Data"] = pd.to_datetime(
            bloqueios["dia"]
        ).dt.strftime("%d/%m")

        fig_bloqueios = px.bar(
            bloqueios,
            x="Data",
            y="leitos_bloqueados",
        )

        fig_bloqueios.update_traces(
            marker_color="#9A88C8",
            marker_line_width=0,
            text=bloqueios["leitos_bloqueados"],
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Leitos bloqueados: %{y}"
                "<extra></extra>"
            ),
        )

        fig_bloqueios.update_layout(
            xaxis_title="Data",
            yaxis_title="Leitos bloqueados",
            showlegend=False,
        )

        fig_bloqueios.update_yaxes(
            gridcolor="#E7EEF3",
            zeroline=False,
            dtick=1,
        )

        fig_bloqueios.update_xaxes(
            showgrid=False,
        )

        tema_plotly(
            fig_bloqueios,
            altura=335,
        )

        st.plotly_chart(
            fig_bloqueios,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        media_bloqueados = pd.to_numeric(
            bloqueios["leitos_bloqueados"],
            errors="coerce",
        ).mean()

        pico_bloqueados = pd.to_numeric(
            bloqueios["leitos_bloqueados"],
            errors="coerce",
        ).max()

        st.caption(
            f"Média de {media_bloqueados:.1f} leito(s) bloqueado(s) por dia; "
            f"pico de {pico_bloqueados:.0f}."
        )

    else:
        st.info(
            "A base operacional não possui informação suficiente "
            "sobre leitos bloqueados."
        )


# ============================================================
# RESUMO OPERACIONAL
# ============================================================

st.write("")

st.markdown(
    '<div class="op-section-title">Resumo da capacidade assistencial</div>',
    unsafe_allow_html=True,
)

if taxa_ocupacao >= 90:
    st.markdown(
        f"""
        <div class="op-alert">
            <b>Atenção à capacidade operacional.</b><br>
            A ocupação atual é de <b>{taxa_ocupacao:.1f}%</b>,
            com {pacientes_internados} pacientes e
            {leitos_operacionais} leitos operacionais.
            O indicador deve ser acompanhado em conjunto com a carga
            assistencial e o fluxo de admissões e altas.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="op-good">
            <b>Capacidade operacional dentro do cenário simulado.</b><br>
            A ocupação atual é de <b>{taxa_ocupacao:.1f}%</b>,
            com {pacientes_internados} pacientes e
            {leitos_operacionais} leitos operacionais.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ACESSO A ANÁLISES COMPLEMENTARES
# ============================================================

st.write("")

a1, a2 = st.columns(2)

with a1:
    st.page_link(
        "pages/1_Dashboard_Geral.py",
        label="Voltar à Visão Geral",
        use_container_width=True,
    )

with a2:
    st.page_link(
        "pages/7_Lean_Healthcare.py",
        label="Ver Lean Healthcare",
        use_container_width=True,
    )


# ============================================================
# AVISO FINAL
# ============================================================

st.caption(
    "Protótipo acadêmico com dados simulados. "
    "Indicadores de capacidade, dimensionamento da equipe, admissões e altas "
    "foram construídos para fins de demonstração conceitual e não devem ser "
    "interpretados como parâmetros assistenciais reais."
)
