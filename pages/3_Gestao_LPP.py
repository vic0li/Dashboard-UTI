# ============================================================
# GESTÃO DO RISCO DE LPP
# UTI INTELLIGENT CARE
#
# Modelo integrado descrito no TCC até a Seção 5.4:
# 8 componentes normalizados -> Score LPP 0–10 -> Baixo/Médio/Alto
# + regra automática de classificação em Alto risco.
# ============================================================

import pandas as pd
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


st.set_page_config(
    page_title="Gestão LPP | UTI Intelligent Care",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("LPP")

st.markdown(
    """
    <style>
    .lpp-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:10px 0 4px 0;
    }
    .lpp-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:13px;
    }
    .lpp-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:15px;
        padding:18px 20px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
    }
    .lpp-card-title {
        color:#173E59;
        font-size:16px;
        font-weight:800;
        margin-bottom:6px;
    }
    .lpp-big {
        color:#0D2A45;
        font-size:31px;
        font-weight:850;
        letter-spacing:-0.03em;
    }
    .lpp-note {
        color:#6F8798;
        font-size:13px;
        line-height:1.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def tema_plotly(fig, altura=390):
    fig.update_layout(
        height=altura,
        margin=dict(l=20, r=20, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", size=14, color="#284A62"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=14),
    )
    return fig


def fmt(v, casas=1):
    v = pd.to_numeric(v, errors="coerce")
    return "N/D" if pd.isna(v) else f"{v:.{casas}f}"


# ============================================================
# DADOS
# ============================================================

try:
    df = load_data().copy()
    df = processar_dados(df)
    df = processar_riscos(df)
except Exception as e:
    st.error("Não foi possível processar a base de risco de LPP.")
    st.exception(e)
    st.stop()

if df.empty or "id_paciente" not in df.columns:
    st.error("A base não contém pacientes disponíveis.")
    st.stop()

df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
df = df.sort_values(["id_paciente", "timestamp_dt"])

pacientes = sorted(
    pd.to_numeric(df["id_paciente"], errors="coerce").dropna().astype(int).unique()
)

cabecalho_pagina(
    "Gestão do Risco de LPP",
    "Estratificação dinâmica do risco de lesão por pressão a partir do modelo integrado do protótipo.",
    secao="Prevenção e acompanhamento",
    badge="Modelo 0–10",
)

sel1, sel2 = st.columns([0.34, 0.66], gap="large")
with sel1:
    paciente = st.selectbox(
        "Paciente",
        pacientes,
        format_func=lambda x: f"Paciente P{int(x):02d}",
    )

df_p = df[df["id_paciente"] == paciente].copy().sort_values("timestamp_dt")
atual = df_p.iloc[-1]

with sel2:
    momento = atual.get("timestamp_dt")
    momento_txt = momento.strftime("%d/%m/%Y %H:%M") if pd.notna(momento) else "N/D"
    st.info(
        f"Registro atual: **{momento_txt}**  •  "
        f"Score LPP: **{fmt(atual.get('score_lpp'), 2)}/10**  •  "
        f"Classificação final: **{atual.get('classificacao_lpp', 'N/D')}**"
    )


# ============================================================
# RESUMO DO MODELO
# ============================================================

st.markdown('<div class="lpp-title">Avaliação atual</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lpp-subtitle">
        Resultado do modelo integrado composto por oito fatores clínicos e operacionais.
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Score LPP", f"{fmt(atual.get('score_lpp'), 2)} / 10")
with k2:
    st.metric("Risco LPP", atual.get("classificacao_lpp", "N/D"))
with k3:
    st.metric("Braden total", fmt(atual.get("braden_total"), 0))
with k4:
    st.metric("Classificação Braden", atual.get("braden_classificacao", "N/D"))

if bool(atual.get("regra_alto_risco_lpp", False)):
    st.warning(
        "Regra automática de Alto Risco ativa: Braden ≤ 12, permanência na posição atual "
        "> 120 minutos e uso de drogas vasoativas. A regra altera a classificação final "
        "para Alto, mas não modifica o valor numérico do Score LPP."
    )


# ============================================================
# OITO COMPONENTES
# ============================================================

st.write("")
st.markdown('<div class="lpp-title">Composição do Score LPP</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lpp-subtitle">
        Cada componente é normalizado em 0, 0,5 ou 1. Os oito fatores possuem
        contribuição igual no cálculo do score final.
    </div>
    """,
    unsafe_allow_html=True,
)

componentes = [
    ("Braden", "comp_lpp_braden"),
    ("Internação", "comp_lpp_internacao"),
    ("Vasoativo", "comp_lpp_vasoativo"),
    ("Mobilidade", "comp_lpp_mobilidade"),
    ("Tempo na posição", "comp_lpp_posicao"),
    ("Reposicionamentos", "comp_lpp_reposicionamento"),
    ("Pac./enfermeiro", "comp_lpp_equipe"),
    ("Ocupação", "comp_lpp_ocupacao"),
]

nomes = [x[0] for x in componentes]
valores = [
    pd.to_numeric(atual.get(col), errors="coerce")
    for _, col in componentes
]

fig = go.Figure(
    go.Bar(
        x=nomes,
        y=valores,
        text=["N/D" if pd.isna(v) else f"{v:.1f}" for v in valores],
        textposition="outside",
        marker_color="#4D8BC4",
        hovertemplate="<b>%{x}</b><br>Componente: %{y:.1f}<extra></extra>",
    )
)
fig.update_layout(
    xaxis_title="",
    yaxis_title="Componente normalizado",
    yaxis=dict(range=[0, 1.15], tickvals=[0, 0.5, 1]),
    showlegend=False,
)
fig.update_yaxes(gridcolor="#E7EEF3", zeroline=False)
fig.update_xaxes(showgrid=False)
tema_plotly(fig, 385)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# DETALHAMENTO DOS FATORES
# ============================================================

st.markdown('<div class="lpp-title">Detalhamento dos fatores</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lpp-subtitle">
        Valores simulados utilizados para determinar cada componente do modelo.
    </div>
    """,
    unsafe_allow_html=True,
)

detalhes = pd.DataFrame(
    [
        ["Braden total", fmt(atual.get("braden_total"), 0), fmt(atual.get("comp_lpp_braden"), 1)],
        ["Tempo de internação", f"{fmt(atual.get('dia_internacao'), 0)} dias", fmt(atual.get("comp_lpp_internacao"), 1)],
        ["Uso de drogas vasoativas", atual.get("uso_drogas_vasoativas", "N/D"), fmt(atual.get("comp_lpp_vasoativo"), 1)],
        ["Mobilidade (Braden)", fmt(atual.get("braden_mobilidade"), 0), fmt(atual.get("comp_lpp_mobilidade"), 1)],
        ["Tempo na posição atual", f"{fmt(atual.get('tempo_posicao_atual_min'), 0)} min", fmt(atual.get("comp_lpp_posicao"), 1)],
        ["Reposicionamentos/24h", fmt(atual.get("mudancas_posicao_24h"), 0), fmt(atual.get("comp_lpp_reposicionamento"), 1)],
        ["Pacientes por enfermeiro", fmt(atual.get("pacientes_por_enfermeiro"), 1), fmt(atual.get("comp_lpp_equipe"), 1)],
        ["Ocupação da UTI", f"{fmt(atual.get('taxa_ocupacao_pct'), 1)}%", fmt(atual.get("comp_lpp_ocupacao"), 1)],
    ],
    columns=["Fator", "Valor atual", "Componente"],
)

st.dataframe(detalhes, use_container_width=True, hide_index=True)


# ============================================================
# BRADEN
# ============================================================

st.write("")
st.markdown('<div class="lpp-title">Escala de Braden simulada</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lpp-subtitle">
        A pontuação total de Braden é apresentada para interpretação e também constitui
        um dos oito componentes do modelo integrado de risco de LPP.
    </div>
    """,
    unsafe_allow_html=True,
)

braden_cols = [
    ("Percepção sensorial", "braden_percepcao_sensorial"),
    ("Umidade", "braden_umidade"),
    ("Atividade", "braden_atividade"),
    ("Mobilidade", "braden_mobilidade"),
    ("Nutrição", "braden_nutricao"),
    ("Fricção/cisalhamento", "braden_friccao_cisalhamento"),
]

bc = st.columns(6)
for container, (nome, coluna) in zip(bc, braden_cols):
    with container:
        st.metric(nome, fmt(atual.get(coluna), 0))

st.caption(
    "Os valores das subescalas de Braden desta base são simulados e não resultam "
    "de avaliação clínica real."
)


# ============================================================
# EVOLUÇÃO DO SCORE
# ============================================================

st.write("")
st.markdown('<div class="lpp-title">Evolução do Score LPP</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lpp-subtitle">
        Comportamento do score integrado ao longo dos registros do paciente.
    </div>
    """,
    unsafe_allow_html=True,
)

fig_e = go.Figure()
fig_e.add_trace(
    go.Scatter(
        x=df_p["timestamp_dt"],
        y=pd.to_numeric(df_p["score_lpp"], errors="coerce"),
        mode="lines",
        name="Score LPP",
        line=dict(width=3),
        hovertemplate="%{x|%d/%m %H:%M}<br>Score: %{y:.2f}<extra></extra>",
    )
)
fig_e.add_hrect(y0=0, y1=4, fillcolor="rgba(109,159,134,.08)", line_width=0)
fig_e.add_hrect(y0=4, y1=7, fillcolor="rgba(199,162,82,.08)", line_width=0)
fig_e.add_hrect(y0=7, y1=10, fillcolor="rgba(184,92,92,.08)", line_width=0)
fig_e.add_hline(y=4, line_dash="dot", line_color="#C7A252")
fig_e.add_hline(y=7, line_dash="dot", line_color="#B85C5C")
fig_e.update_layout(
    xaxis_title="",
    yaxis_title="Score LPP",
    yaxis=dict(range=[0, 10]),
    showlegend=False,
    hovermode="x unified",
)
fig_e.update_yaxes(gridcolor="#E7EEF3", zeroline=False)
tema_plotly(fig_e, 390)
st.plotly_chart(fig_e, use_container_width=True, config={"displayModeBar": False})

st.caption(
    "Para operacionalização no dashboard, as faixas são tratadas de forma contínua: "
    "Baixo < 4; Médio ≥ 4 e < 7; Alto ≥ 7. A regra automática de Alto Risco pode "
    "alterar a classificação final sem alterar o score numérico."
)


# ============================================================
# REFERÊNCIA DAS REGRAS DO PROTÓTIPO
# ============================================================

with st.expander("Ver regras de normalização do modelo"):
    regras = pd.DataFrame(
        [
            ["Braden total", "≥ 19", "13–18", "≤ 12"],
            ["Tempo de internação", "< 3 dias", "3–6 dias", "≥ 7 dias"],
            ["Uso de vasoativo", "Não", "—", "Sim"],
            ["Mobilidade Braden", "4", "2–3", "1"],
            ["Tempo na posição", "< 60 min", "60–120 min", "> 120 min"],
            ["Reposicionamentos/24h", "≥ 12", "6–11", "< 6"],
            ["Pacientes/enfermeiro", "≤ 2", "3", "≥ 4"],
            ["Ocupação da UTI", "< 80%", "80–90%", "> 90%"],
        ],
        columns=["Fator", "Componente 0", "Componente 0,5", "Componente 1"],
    )
    st.dataframe(regras, use_container_width=True, hide_index=True)

    st.latex(
        r"Score_{LPP}=10 \times \frac{C_B+C_I+C_V+C_M+C_P+C_R+C_E+C_O}{8}"
    )

    st.caption(
        "Os limites utilizados exclusivamente para normalização dos dados simulados "
        "constituem decisões metodológicas do protótipo quando não correspondem a "
        "parâmetros clínicos validados."
    )


st.caption(
    "Protótipo acadêmico com dados simulados. O modelo de risco possui finalidade "
    "conceitual e demonstrativa e não substitui avaliação profissional, protocolos "
    "institucionais ou instrumentos clínicos validados."
)
