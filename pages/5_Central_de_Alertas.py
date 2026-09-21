# ============================================================
# CENTRAL DE ALERTAS
# UTI INTELLIGENT CARE
#
# Regras do protótipo descritas na Seção 5.3:
# FC <= 40 ou >= 131 bpm
# PAS <= 90 ou >= 220 mmHg
# SpO2 <= 91%
# Classificação final de LPP = Alto
#
# Não utiliza score clínico nem índice global de prioridade.
# ============================================================

import pandas as pd
import plotly.express as px
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
    page_title="Central de Alertas | UTI Intelligent Care",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Alertas")

st.markdown(
    """
    <style>
    .alert-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:10px 0 4px 0;
    }
    .alert-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:13px;
    }
    .alert-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:15px;
        padding:18px 20px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def tema_plotly(fig, altura=350):
    fig.update_layout(
        height=altura,
        margin=dict(l=20, r=20, t=20, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", size=14, color="#284A62"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=14),
    )
    fig.update_yaxes(gridcolor="#E7EEF3", zeroline=False)
    fig.update_xaxes(showgrid=False)
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
    st.error("Não foi possível processar os alertas.")
    st.exception(e)
    st.stop()

if df.empty or "id_paciente" not in df.columns:
    st.error("A base não contém pacientes disponíveis.")
    st.stop()

df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)

atual = (
    df.dropna(subset=["timestamp_dt"])
    .sort_values("timestamp_dt")
    .groupby("id_paciente", as_index=False)
    .tail(1)
    .copy()
)

cabecalho_pagina(
    "Central de Alertas",
    "Consolidação das ocorrências atuais identificadas pelas regras explícitas do motor analítico.",
    secao="Vigilância do protótipo",
    badge="Regras explícitas",
)


# ============================================================
# MÉTRICAS
# ============================================================

qtd = pd.to_numeric(
    atual.get("quantidade_alertas", pd.Series(0, index=atual.index)),
    errors="coerce",
).fillna(0)

pacientes_alerta = int((qtd > 0).sum())
total_alertas = int(qtd.sum())
alto_lpp = int(
    atual.get("classificacao_lpp", pd.Series("", index=atual.index))
    .astype(str).eq("Alto").sum()
)
sem_alerta = int((qtd == 0).sum())

st.markdown('<div class="alert-title">Situação atual</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="alert-subtitle">
        Os indicadores consideram somente o registro mais recente de cada paciente.
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Pacientes com alerta", pacientes_alerta)
with k2:
    st.metric("Alertas ativos", total_alertas)
with k3:
    st.metric("Alto risco LPP", alto_lpp)
with k4:
    st.metric("Sem alerta", sem_alerta)


# ============================================================
# TIPOS DE ALERTA
# ============================================================

st.write("")
c1, c2 = st.columns([1.05, 0.95], gap="large")

tipos = {
    "FC": "alerta_fc_motor",
    "PAS": "alerta_pas_motor",
    "SpO₂": "alerta_spo2_motor",
    "LPP": "alerta_lpp_motor",
}

resumo = pd.DataFrame(
    {
        "Tipo": list(tipos.keys()),
        "Ocorrências": [
            int(
                atual.get(col, pd.Series(False, index=atual.index))
                .fillna(False).astype(bool).sum()
            )
            for col in tipos.values()
        ],
    }
)

with c1:
    st.markdown('<div class="alert-title">Alertas por tipo</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="alert-subtitle">
            Frequência das quatro condições definidas no motor do protótipo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = px.bar(resumo, x="Tipo", y="Ocorrências")
    fig.update_traces(
        marker_color="#B85C5C",
        text=resumo["Ocorrências"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y} ocorrência(s)<extra></extra>",
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ocorrências")
    fig.update_yaxes(dtick=1)
    tema_plotly(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c2:
    st.markdown('<div class="alert-title">Regras implementadas</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="alert-subtitle">
            Limites utilizados para geração dos alertas atuais.
        </div>
        """,
        unsafe_allow_html=True,
    )

    regras = pd.DataFrame(
        [
            ["Frequência cardíaca", "FC ≤ 40 ou FC ≥ 131 bpm"],
            ["Pressão arterial sistólica", "PAS ≤ 90 ou PAS ≥ 220 mmHg"],
            ["SpO₂", "SpO₂ ≤ 91%"],
            ["Risco de LPP", "Classificação final = Alto"],
        ],
        columns=["Alerta", "Condição"],
    )
    st.dataframe(regras, use_container_width=True, hide_index=True, height=245)
    st.caption(
        "As faixas fisiológicas foram utilizadas como regras explícitas do protótipo. "
        "A implementação não corresponde ao NEWS2 completo."
    )


# ============================================================
# PACIENTES COM ALERTA
# ============================================================

st.write("")
st.markdown('<div class="alert-title">Pacientes com alertas ativos</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="alert-subtitle">
        A tabela não utiliza índice de prioridade. A ordenação considera somente a quantidade
        de alertas ativos e, em seguida, o Score LPP para facilitar a leitura da interface.
    </div>
    """,
    unsafe_allow_html=True,
)

alertados = atual[qtd > 0].copy()

if alertados.empty:
    st.success("Nenhum paciente apresenta condição de alerta no registro atual.")
else:
    alertados["_qtd"] = pd.to_numeric(alertados["quantidade_alertas"], errors="coerce").fillna(0)
    alertados["_score"] = pd.to_numeric(alertados["score_lpp"], errors="coerce").fillna(0)
    alertados = alertados.sort_values(["_qtd", "_score"], ascending=[False, False])

    tabela = pd.DataFrame()
    ids = pd.to_numeric(alertados["id_paciente"], errors="coerce").fillna(0).astype(int)
    tabela["Paciente"] = "P" + ids.astype(str).str.zfill(2)
    tabela["FC"] = pd.to_numeric(alertados["frequencia_cardiaca"], errors="coerce").round(1).values
    tabela["PAS"] = pd.to_numeric(alertados["pressao_sistolica"], errors="coerce").round(1).values
    tabela["SpO₂"] = pd.to_numeric(alertados["saturacao_O2"], errors="coerce").round(1).values
    tabela["Score LPP"] = pd.to_numeric(alertados["score_lpp"], errors="coerce").round(2).values
    tabela["Risco LPP"] = alertados["classificacao_lpp"].astype(str).values
    tabela["Nº alertas"] = alertados["_qtd"].astype(int).values
    tabela["Motivos"] = alertados["motivos_alerta"].astype(str).values

    st.dataframe(tabela, use_container_width=True, hide_index=True, height=330)


# ============================================================
# DETALHAMENTO POR PACIENTE
# ============================================================

st.write("")
st.markdown('<div class="alert-title">Detalhamento</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="alert-subtitle">
        Inspeção das condições atuais de um paciente monitorado.
    </div>
    """,
    unsafe_allow_html=True,
)

ids_disponiveis = sorted(
    pd.to_numeric(atual["id_paciente"], errors="coerce").dropna().astype(int).unique()
)

paciente = st.selectbox(
    "Paciente",
    ids_disponiveis,
    format_func=lambda x: f"Paciente P{int(x):02d}",
)

p = atual[atual["id_paciente"] == paciente].iloc[-1]

d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric("FC", f"{fmt(p.get('frequencia_cardiaca'))} bpm")
    st.caption("Alerta ativo" if bool(p.get("alerta_fc_motor", False)) else "Sem alerta")
with d2:
    st.metric("PAS", f"{fmt(p.get('pressao_sistolica'))} mmHg")
    st.caption("Alerta ativo" if bool(p.get("alerta_pas_motor", False)) else "Sem alerta")
with d3:
    st.metric("SpO₂", f"{fmt(p.get('saturacao_O2'))}%")
    st.caption("Alerta ativo" if bool(p.get("alerta_spo2_motor", False)) else "Sem alerta")
with d4:
    st.metric("Risco LPP", p.get("classificacao_lpp", "N/D"))
    st.caption(
        "Alerta ativo"
        if bool(p.get("alerta_lpp_motor", False))
        else f"Score {fmt(p.get('score_lpp'), 2)}/10"
    )

qtd_p = int(pd.to_numeric(p.get("quantidade_alertas"), errors="coerce") or 0)

if qtd_p > 0:
    st.warning(f"Alertas ativos: {p.get('motivos_alerta', 'N/D')}")
else:
    st.caption("✓ Nenhuma regra de alerta está ativa para este paciente no registro atual.")


# ============================================================
# CONTEXTO TEMPORAL DOS ALERTAS
# ============================================================

st.write("")
st.markdown('<div class="alert-title">Ocorrências ao longo dos registros</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="alert-subtitle">
        Quantidade de pacientes com cada tipo de alerta em cada momento da base simulada.
        O histórico é agregado para toda a UTI, evitando um gráfico vazio quando o paciente
        selecionado não apresenta alertas.
    </div>
    """,
    unsafe_allow_html=True,
)

historico = (
    df.dropna(subset=["timestamp_dt"])
    .groupby("timestamp_dt", as_index=False)
    .agg(
        FC=("alerta_fc_motor", "sum"),
        PAS=("alerta_pas_motor", "sum"),
        SpO2=("alerta_spo2_motor", "sum"),
        LPP=("alerta_lpp_motor", "sum"),
    )
    .sort_values("timestamp_dt")
)

for c in ["FC", "PAS", "SpO2", "LPP"]:
    historico[c] = pd.to_numeric(historico[c], errors="coerce").fillna(0).astype(int)

if historico[["FC", "PAS", "SpO2", "LPP"]].to_numpy().sum() == 0:
    st.info("Não há ocorrências de alerta em nenhum registro da base simulada.")
else:
    hist_long = historico.melt(
        id_vars="timestamp_dt",
        value_vars=["FC", "PAS", "SpO2", "LPP"],
        var_name="Tipo",
        value_name="Pacientes",
    )
    hist_long["Tipo"] = hist_long["Tipo"].replace({"SpO2": "SpO₂", "LPP": "LPP Alto"})

    fig_h = px.line(
        hist_long,
        x="timestamp_dt",
        y="Pacientes",
        color="Tipo",
    )
    fig_h.update_traces(
        line=dict(width=2.5),
        hovertemplate="%{x|%d/%m %H:%M}<br>Pacientes: %{y}<extra></extra>",
    )
    fig_h.update_layout(
        xaxis_title="",
        yaxis_title="Pacientes com alerta",
        legend_title_text="Tipo de alerta",
        hovermode="x unified",
    )
    fig_h.update_yaxes(dtick=1, rangemode="tozero")
    tema_plotly(fig_h, 350)
    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

st.caption(
    "Protótipo acadêmico com dados simulados. Os alertas apresentados possuem finalidade "
    "conceitual e demonstrativa, não constituem protocolo de resposta clínica nem sistema "
    "de alarme médico validado e não substituem avaliação profissional."
)
