# ============================================================
# MONITORAMENTO CLÍNICO
# UTI INTELLIGENT CARE
#
# Compatível com o motor analítico descrito no TCC até a Seção 5.5.
# FC, PAS e SpO2 compõem a camada clínica principal.
# Temperatura e lactato permanecem como informações complementares.
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
    page_title="Monitoramento Clínico | UTI Intelligent Care",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Monitoramento")


st.markdown(
    """
    <style>
    .monitor-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:10px 0 4px 0;
    }
    .monitor-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:13px;
    }
    .clinical-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:15px;
        padding:18px 20px;
        min-height:160px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
    }
    .clinical-name {
        color:#173E59;
        font-size:16px;
        font-weight:800;
        margin-bottom:7px;
    }
    .clinical-value {
        color:#0D2A45;
        font-size:31px;
        font-weight:850;
        letter-spacing:-0.03em;
        margin-bottom:5px;
    }
    .clinical-meta {
        color:#6F8798;
        font-size:13px;
        line-height:1.55;
    }
    .clinical-alert {
        color:#A24E4E;
        font-weight:800;
    }
    .clinical-ok {
        color:#587E6B;
        font-weight:750;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def tema_plotly(fig, altura=360):
    fig.update_layout(
        height=altura,
        margin=dict(l=20, r=20, t=25, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", size=14, color="#284A62"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(gridcolor="#EEF3F6")
    fig.update_yaxes(gridcolor="#EEF3F6", zeroline=False)
    return fig


def fmt(valor, casas=1):
    valor = pd.to_numeric(valor, errors="coerce")
    return "N/D" if pd.isna(valor) else f"{valor:.{casas}f}"


def tendencia_texto(valor):
    mapa = {
        "subindo": "↑ Subindo",
        "descendo": "↓ Descendo",
        "estavel": "→ Estável",
    }
    return mapa.get(str(valor).lower(), "N/D")


# ============================================================
# DADOS
# ============================================================

try:
    df = load_data().copy()
    df = processar_dados(df)
    df = processar_riscos(df)
except Exception as e:
    st.error("Não foi possível processar a base clínica.")
    st.exception(e)
    st.stop()

if df.empty or "id_paciente" not in df.columns:
    st.error("A base clínica não contém pacientes disponíveis.")
    st.stop()

df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
df = df.sort_values(["id_paciente", "timestamp_dt"])

pacientes = sorted(pd.to_numeric(df["id_paciente"], errors="coerce").dropna().astype(int).unique())

cabecalho_pagina(
    "Monitoramento Clínico",
    "Acompanhamento individual dos parâmetros fisiológicos simulados e de suas tendências recentes.",
    secao="Análise individual",
    badge="Dados simulados",
)

csel, cinfo = st.columns([0.34, 0.66], gap="large")

with csel:
    paciente = st.selectbox(
        "Paciente",
        pacientes,
        format_func=lambda x: f"Paciente P{int(x):02d}",
    )

df_p = df[df["id_paciente"] == paciente].copy().sort_values("timestamp_dt")
atual = df_p.iloc[-1]

with cinfo:
    momento = atual.get("timestamp_dt")
    momento_txt = momento.strftime("%d/%m/%Y %H:%M") if pd.notna(momento) else "N/D"
    dia = pd.to_numeric(atual.get("dia_internacao"), errors="coerce")
    dia_txt = str(int(dia)) if pd.notna(dia) else "N/D"
    st.info(
        f"Registro atual: **{momento_txt}**  •  "
        f"Dia de internação: **{dia_txt}**  •  "
        f"Risco LPP: **{atual.get('classificacao_lpp', 'N/D')}**"
    )


# ============================================================
# NÚCLEO CLÍNICO — FC, PAS E SpO2
# ============================================================

st.markdown('<div class="monitor-title">Parâmetros clínicos principais</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="monitor-subtitle">
        Valor atual, média móvel dos três registros mais recentes, direção da última variação
        e condição de alerta definida no motor analítico.
    </div>
    """,
    unsafe_allow_html=True,
)

parametros = [
    {
        "nome": "Frequência cardíaca",
        "col": "frequencia_cardiaca",
        "media": "frequencia_cardiaca_media_3",
        "trend": "frequencia_cardiaca_tendencia",
        "alerta": "alerta_fc_motor",
        "unidade": "bpm",
    },
    {
        "nome": "Pressão arterial sistólica",
        "col": "pressao_sistolica",
        "media": "pressao_sistolica_media_3",
        "trend": "pressao_sistolica_tendencia",
        "alerta": "alerta_pas_motor",
        "unidade": "mmHg",
    },
    {
        "nome": "SpO₂",
        "col": "saturacao_O2",
        "media": "saturacao_O2_media_3",
        "trend": "saturacao_O2_tendencia",
        "alerta": "alerta_spo2_motor",
        "unidade": "%",
    },
]

cols = st.columns(3, gap="large")
for container, p in zip(cols, parametros):
    valor = fmt(atual.get(p["col"]))
    media = fmt(atual.get(p["media"]))
    tendencia = tendencia_texto(atual.get(p["trend"]))
    alerta = bool(atual.get(p["alerta"], False))
    status = (
        '<span class="clinical-alert">Alerta ativo</span>'
        if alerta
        else '<span class="clinical-ok">Sem alerta</span>'
    )

    with container:
        st.markdown(
            f"""
            <div class="clinical-card">
                <div class="clinical-name">{p["nome"]}</div>
                <div class="clinical-value">{valor} <span style="font-size:15px;font-weight:700;color:#7890A0;">{p["unidade"]}</span></div>
                <div class="clinical-meta">
                    Média dos 3 registros: <b>{media} {p["unidade"]}</b><br>
                    Tendência: <b>{tendencia}</b><br>
                    Condição: {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SÉRIES TEMPORAIS
# ============================================================

st.write("")
st.markdown('<div class="monitor-title">Evolução temporal</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="monitor-subtitle">
        Valores observados e respectivas médias móveis de três registros.
        A tendência é descritiva e não constitui, isoladamente, classificação de deterioração clínica.
    </div>
    """,
    unsafe_allow_html=True,
)

graficos = st.tabs(["Frequência cardíaca", "PAS", "SpO₂"])

for tab, p in zip(graficos, parametros):
    with tab:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df_p["timestamp_dt"],
                y=pd.to_numeric(df_p[p["col"]], errors="coerce"),
                mode="lines",
                name="Valor observado",
                line=dict(width=2),
                hovertemplate="%{x|%d/%m %H:%M}<br>%{y:.1f} " + p["unidade"] + "<extra></extra>",
            )
        )

        if p["media"] in df_p.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_p["timestamp_dt"],
                    y=pd.to_numeric(df_p[p["media"]], errors="coerce"),
                    mode="lines",
                    name="Média móvel (3 registros)",
                    line=dict(width=3, dash="dot"),
                    hovertemplate="%{x|%d/%m %H:%M}<br>%{y:.1f} " + p["unidade"] + "<extra></extra>",
                )
            )

        fig.update_layout(
            xaxis_title="",
            yaxis_title=p["unidade"],
            hovermode="x unified",
        )
        tema_plotly(fig, 390)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# ALERTAS DO PACIENTE
# ============================================================

st.write("")
a1, a2 = st.columns([0.72, 0.28], gap="large")

with a1:
    st.markdown('<div class="monitor-title">Alertas atuais</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="monitor-subtitle">
            Regras explícitas do protótipo para FC, PAS, SpO₂ e classificação final de LPP.
        </div>
        """,
        unsafe_allow_html=True,
    )

    alertas = []
    if bool(atual.get("alerta_fc_motor", False)):
        alertas.append("Frequência cardíaca: FC ≤ 40 ou ≥ 131 bpm.")
    if bool(atual.get("alerta_pas_motor", False)):
        alertas.append("Pressão arterial sistólica: PAS ≤ 90 ou ≥ 220 mmHg.")
    if bool(atual.get("alerta_spo2_motor", False)):
        alertas.append("Saturação periférica de oxigênio: SpO₂ ≤ 91%.")
    if bool(atual.get("alerta_lpp_motor", False)):
        alertas.append("Lesão por pressão: classificação final de risco LPP = Alto.")

    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.markdown(
            """
            <div class="clinical-card" style="min-height:auto;padding:14px 18px;">
                <div class="clinical-ok">Sem alertas ativos no registro atual</div>
                <div class="clinical-meta" style="margin-top:4px;">
                    FC, PAS, SpO₂ e risco LPP permanecem dentro das condições sem alerta definidas no protótipo.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with a2:
    qtd = int(pd.to_numeric(atual.get("quantidade_alertas"), errors="coerce") or 0)
    st.metric("Alertas ativos", qtd)
    st.metric("Score LPP", fmt(atual.get("score_lpp"), 2))
    st.caption(f"Classificação: {atual.get('classificacao_lpp', 'N/D')}")


# ============================================================
# INFORMAÇÕES COMPLEMENTARES
# ============================================================

st.write("")
st.markdown('<div class="monitor-title">Informações clínicas complementares</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="monitor-subtitle">
        Variáveis presentes na base simulada, exibidas como apoio à caracterização do paciente.
        Elas não compõem as regras de alerta clínico definidas na Seção 5.3.
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Temperatura", f"{fmt(atual.get('temperatura'))} °C")
with c2:
    st.metric("Lactato", fmt(atual.get("lactato")))
with c3:
    st.metric("Creatinina", fmt(atual.get("creatinina"), 2))
with c4:
    st.metric("Leucócitos", fmt(atual.get("leucocitos"), 0))


# ============================================================
# CONTEXTO DO PACIENTE
# ============================================================

with st.expander("Contexto do registro simulado"):
    campos = {
        "Idade": atual.get("idade", "N/D"),
        "Motivo de internação": atual.get("motivo_internacao", "N/D"),
        "Comorbidades": atual.get("comorbidades", "N/D"),
        "Estado clínico simulado": atual.get("estado_clinico", "N/D"),
        "Uso de drogas vasoativas": atual.get("uso_drogas_vasoativas", "N/D"),
        "Braden total": atual.get("braden_total", "N/D"),
        "Classificação Braden": atual.get("braden_classificacao", "N/D"),
    }
    contexto = pd.DataFrame(
        {"Informação": list(campos.keys()), "Valor": list(campos.values())}
    )
    st.dataframe(contexto, use_container_width=True, hide_index=True)


st.caption(
    "Protótipo acadêmico com dados simulados. As tendências apresentadas são descritivas "
    "e as regras de alerta possuem finalidade conceitual. O sistema não substitui avaliação "
    "profissional, protocolos institucionais ou sistemas clínicos validados."
)
