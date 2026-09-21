# ============================================================
# GESTÃO OPERACIONAL
# UTI INTELLIGENT CARE
#
# Os indicadores taxa de ocupação e pacientes/enfermeiro desta página
# são os mesmos utilizados como componentes operacionais do Score LPP.
# ============================================================

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styling import (
    aplicar_estilo,
    topo_produto,
    navegacao_topo,
    cabecalho_pagina,
)


st.set_page_config(
    page_title="Gestão Operacional | UTI Intelligent Care",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Operacional")

st.markdown(
    """
    <style>
    .op-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:10px 0 4px 0;
    }
    .op-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def tema_plotly(fig, altura=350):
    fig.update_layout(
        height=altura,
        margin=dict(l=20, r=20, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", size=14, color="#284A62"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(gridcolor="#EEF3F6")
    fig.update_yaxes(gridcolor="#EEF3F6", zeroline=False)
    return fig


def fmt(v, casas=1):
    v = pd.to_numeric(v, errors="coerce")
    return "N/D" if pd.isna(v) else f"{v:.{casas}f}"


@st.cache_data
def carregar_operacional():
    raiz = Path(__file__).resolve().parent.parent
    caminho = raiz / "data" / "UTI_operacional.csv"

    if not caminho.exists():
        return pd.DataFrame()

    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
    df.columns = df.columns.astype(str).str.strip()

    if "timestamp" in df.columns:
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp_dt").reset_index(drop=True)

    numericas = [
        "capacidade_total_leitos",
        "leitos_bloqueados",
        "leitos_operacionais",
        "pacientes_monitorados_base",
        "pacientes_internados",
        "taxa_ocupacao_pct",
        "enfermeiros_turno",
        "pacientes_por_enfermeiro",
        "admissoes_turno",
        "altas_turno",
        "saldo_admissoes_altas",
    ]
    for c in numericas:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


df = carregar_operacional()

if df.empty:
    st.error("A base operacional não está disponível.")
    st.stop()

atual = df.iloc[-1]

cabecalho_pagina(
    "Gestão Operacional",
    "Acompanhamento da capacidade, ocupação, fluxo e relação entre pacientes e equipe de enfermagem.",
    secao="Capacidade e fluxo",
    badge="Dados simulados",
)


# ============================================================
# SITUAÇÃO ATUAL
# ============================================================

st.markdown('<div class="op-title">Situação operacional atual</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="op-subtitle">
        Indicadores correspondentes ao último período disponível na base operacional simulada.
    </div>
    """,
    unsafe_allow_html=True,
)

operacionais = pd.to_numeric(atual.get("leitos_operacionais"), errors="coerce")
internados = pd.to_numeric(atual.get("pacientes_internados"), errors="coerce")
disponiveis = (
    max(int(operacionais - internados), 0)
    if pd.notna(operacionais) and pd.notna(internados)
    else None
)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Leitos operacionais", fmt(atual.get("leitos_operacionais"), 0))
with k2:
    st.metric("Pacientes internados", fmt(atual.get("pacientes_internados"), 0))
with k3:
    st.metric("Ocupação", f"{fmt(atual.get('taxa_ocupacao_pct'), 1)}%")
with k4:
    st.metric("Pac./enfermeiro", fmt(atual.get("pacientes_por_enfermeiro"), 1))
with k5:
    st.metric("Leitos disponíveis", "N/D" if disponiveis is None else disponiveis)


# ============================================================
# OCUPAÇÃO E EQUIPE — MESMAS VARIÁVEIS DO MODELO LPP
# ============================================================

st.write("")
c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown('<div class="op-title">Evolução da ocupação</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="op-subtitle">
            A taxa de ocupação é também utilizada como um dos oito componentes do modelo integrado de LPP.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp_dt"],
            y=df["taxa_ocupacao_pct"],
            mode="lines",
            name="Ocupação",
            line=dict(width=3),
            hovertemplate="%{x|%d/%m %H:%M}<br>Ocupação: %{y:.1f}%<extra></extra>",
        )
    )
    fig.add_hline(y=80, line_dash="dot", line_color="#C7A252")
    fig.add_hline(y=90, line_dash="dot", line_color="#B85C5C")
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Ocupação (%)",
        showlegend=False,
        hovermode="x unified",
    )
    tema_plotly(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Normalização no Score LPP: < 80% = 0; 80–90% = 0,5; > 90% = 1.")

with c2:
    st.markdown('<div class="op-title">Relação pacientes/enfermeiro</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="op-subtitle">
            Indicador operacional incorporado ao modelo integrado de risco de LPP.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp_dt"],
            y=df["pacientes_por_enfermeiro"],
            mode="lines",
            name="Pacientes/enfermeiro",
            line=dict(width=3),
            hovertemplate="%{x|%d/%m %H:%M}<br>Pacientes/enfermeiro: %{y:.1f}<extra></extra>",
        )
    )
    fig.add_hline(y=2, line_dash="dot", line_color="#6D9F86")
    fig.add_hline(y=3, line_dash="dot", line_color="#C7A252")
    fig.add_hline(y=4, line_dash="dot", line_color="#B85C5C")
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Pacientes por enfermeiro",
        showlegend=False,
        hovermode="x unified",
    )
    tema_plotly(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Normalização no Score LPP: ≤ 2 = 0; 3 = 0,5; ≥ 4 = 1.")


# ============================================================
# CAPACIDADE
# ============================================================

st.write("")
st.markdown('<div class="op-title">Capacidade da unidade</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="op-subtitle">
        Relação entre capacidade total, leitos bloqueados, leitos operacionais e pacientes internados.
    </div>
    """,
    unsafe_allow_html=True,
)

fig_cap = go.Figure()
for coluna, nome in [
    ("capacidade_total_leitos", "Capacidade total"),
    ("leitos_operacionais", "Leitos operacionais"),
    ("pacientes_internados", "Pacientes internados"),
]:
    if coluna in df.columns:
        fig_cap.add_trace(
            go.Scatter(
                x=df["timestamp_dt"],
                y=df[coluna],
                mode="lines",
                name=nome,
                line=dict(width=2.5),
                hovertemplate="%{x|%d/%m %H:%M}<br>%{y:.0f}<extra></extra>",
            )
        )

fig_cap.update_layout(
    xaxis_title="",
    yaxis_title="Quantidade",
    hovermode="x unified",
)
tema_plotly(fig_cap, 365)
st.plotly_chart(fig_cap, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# FLUXO
# ============================================================

st.write("")
st.markdown('<div class="op-title">Fluxo de admissões e altas</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="op-subtitle">
        Movimentação simulada de pacientes por período operacional.
    </div>
    """,
    unsafe_allow_html=True,
)

fig_fluxo = go.Figure()
fig_fluxo.add_trace(
    go.Bar(
        x=df["timestamp_dt"],
        y=df["admissoes_turno"],
        name="Admissões",
        hovertemplate="%{x|%d/%m %H:%M}<br>Admissões: %{y:.0f}<extra></extra>",
    )
)
fig_fluxo.add_trace(
    go.Bar(
        x=df["timestamp_dt"],
        y=-df["altas_turno"],
        name="Altas",
        hovertemplate="%{x|%d/%m %H:%M}<br>Altas: %{customdata:.0f}<extra></extra>",
        customdata=df["altas_turno"],
    )
)
fig_fluxo.update_layout(
    barmode="relative",
    xaxis_title="",
    yaxis_title="Movimentação",
)
tema_plotly(fig_fluxo, 360)
st.plotly_chart(fig_fluxo, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# ÚLTIMO PERÍODO
# ============================================================

st.write("")
st.markdown('<div class="op-title">Último período registrado</div>', unsafe_allow_html=True)

momento = atual.get("timestamp_dt")
momento_txt = momento.strftime("%d/%m/%Y %H:%M") if pd.notna(momento) else "N/D"

resumo = pd.DataFrame(
    [
        ["Data/hora", momento_txt],
        ["Turno", atual.get("turno", "N/D")],
        ["Capacidade total", fmt(atual.get("capacidade_total_leitos"), 0)],
        ["Leitos bloqueados", fmt(atual.get("leitos_bloqueados"), 0)],
        ["Leitos operacionais", fmt(atual.get("leitos_operacionais"), 0)],
        ["Pacientes internados", fmt(atual.get("pacientes_internados"), 0)],
        ["Taxa de ocupação", f"{fmt(atual.get('taxa_ocupacao_pct'), 1)}%"],
        ["Enfermeiros no período", fmt(atual.get("enfermeiros_turno"), 0)],
        ["Pacientes por enfermeiro", fmt(atual.get("pacientes_por_enfermeiro"), 1)],
        ["Admissões", fmt(atual.get("admissoes_turno"), 0)],
        ["Altas", fmt(atual.get("altas_turno"), 0)],
    ],
    columns=["Indicador", "Valor"],
)
st.dataframe(resumo, use_container_width=True, hide_index=True)


st.caption(
    "Protótipo acadêmico com dados simulados. Os limites utilizados para normalização "
    "dos componentes operacionais do Score LPP constituem parâmetros metodológicos "
    "do protótipo e não devem ser interpretados como recomendações assistenciais."
)
