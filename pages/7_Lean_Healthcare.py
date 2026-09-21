# ============================================================
# ANÁLISE LEAN
# UTI INTELLIGENT CARE
#
# Página orientada ao processo, conectando os dados simulados
# aos gargalos do AS-IS descritos no TCC.
#
# Não cria score Lean, não replica a Central de Alertas e não
# afirma impacto assistencial não mensurado.
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


st.set_page_config(
    page_title="Análise Lean | UTI Intelligent Care",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Lean")

st.markdown(
    """
    <style>
    .lean-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:10px 0 4px 0;
    }
    .lean-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:13px;
    }
    .lean-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:15px;
        padding:18px 20px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
        min-height:148px;
    }
    .lean-card-title {
        color:#173E59;
        font-size:16px;
        font-weight:800;
        margin-bottom:7px;
    }
    .lean-card-text {
        color:#647F91;
        font-size:14px;
        line-height:1.55;
    }
    .lean-step {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:14px;
        padding:16px 18px;
        min-height:135px;
    }
    .lean-step-label {
        color:#2F6F9F;
        font-size:13px;
        font-weight:850;
        text-transform:uppercase;
        letter-spacing:.04em;
        margin-bottom:5px;
    }
    .lean-step-title {
        color:#173E59;
        font-size:16px;
        font-weight:800;
        margin-bottom:5px;
    }
    .lean-step-text {
        color:#6F8798;
        font-size:13px;
        line-height:1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def tema_plotly(fig, altura=360):
    fig.update_layout(
        height=altura,
        margin=dict(l=25, r=25, t=30, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", size=14, color="#284A62"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=14),
    )
    return fig


def carregar_operacional():
    raiz = Path(__file__).resolve().parent.parent
    caminho = raiz / "data" / "UTI_operacional.csv"
    if not caminho.exists():
        return pd.DataFrame()

    op = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
    op["timestamp_dt"] = pd.to_datetime(op["timestamp"], errors="coerce")
    op = op.sort_values("timestamp_dt")

    for c in [
        "taxa_ocupacao_pct",
        "pacientes_por_enfermeiro",
        "pacientes_internados",
        "leitos_operacionais",
        "admissoes_turno",
        "altas_turno",
    ]:
        if c in op.columns:
            op[c] = pd.to_numeric(op[c], errors="coerce")
    return op


# ============================================================
# DADOS
# ============================================================

try:
    df = load_data().copy()
    df = processar_dados(df)
    df = processar_riscos(df)
    op = carregar_operacional()
except Exception as e:
    st.error("Não foi possível processar os dados para a análise Lean.")
    st.exception(e)
    st.stop()

if df.empty:
    st.error("A base clínica está vazia.")
    st.stop()

df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)

cabecalho_pagina(
    "Análise Lean",
    "Leitura do processo assistencial a partir dos gargalos do estado atual e dos dados simulados do protótipo.",
    secao="Processo e melhoria contínua",
    badge="Lean Healthcare",
)


# ============================================================
# 1. INDICADORES DE PROCESSO
# ============================================================

st.markdown('<div class="lean-title">Indicadores de processo</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lean-subtitle">
        Indicadores selecionados para representar condições associadas ao fluxo,
        à carga operacional e à prevenção de LPP. Não constituem um score Lean.
    </div>
    """,
    unsafe_allow_html=True,
)

# Ocupação
ocup_media = (
    pd.to_numeric(op["taxa_ocupacao_pct"], errors="coerce").mean()
    if not op.empty and "taxa_ocupacao_pct" in op.columns else None
)
ocup_alta = (
    (pd.to_numeric(op["taxa_ocupacao_pct"], errors="coerce") > 90).mean() * 100
    if not op.empty and "taxa_ocupacao_pct" in op.columns else None
)

# Relação pacientes/enfermeiro
carga_media = (
    pd.to_numeric(op["pacientes_por_enfermeiro"], errors="coerce").mean()
    if not op.empty and "pacientes_por_enfermeiro" in op.columns else None
)
carga_alta = (
    (pd.to_numeric(op["pacientes_por_enfermeiro"], errors="coerce") >= 4).mean() * 100
    if not op.empty and "pacientes_por_enfermeiro" in op.columns else None
)

# Posição >120 min
pos = pd.to_numeric(df.get("tempo_posicao_atual_min"), errors="coerce")
pct_posicao = (pos > 120).mean() * 100 if pos.notna().any() else None

# Permanência >=7 dias
dias = pd.to_numeric(df.get("dia_internacao"), errors="coerce")
pct_permanencia = (dias >= 7).mean() * 100 if dias.notna().any() else None

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Ocupação média", "N/D" if ocup_media is None else f"{ocup_media:.1f}%")
    if ocup_alta is not None:
        st.caption(f"{ocup_alta:.1f}% dos períodos acima de 90%.")
with k2:
    st.metric("Pac./enfermeiro médio", "N/D" if carga_media is None else f"{carga_media:.1f}")
    if carga_alta is not None:
        st.caption(f"{carga_alta:.1f}% dos períodos com relação ≥ 4.")
with k3:
    st.metric("Registros > 120 min", "N/D" if pct_posicao is None else f"{pct_posicao:.1f}%")
    st.caption("Tempo na posição atual.")
with k4:
    st.metric("Registros com ≥ 7 dias", "N/D" if pct_permanencia is None else f"{pct_permanencia:.1f}%")
    st.caption("Tempo de internação no registro.")


# ============================================================
# 2. GARGALOS DO AS-IS
# ============================================================

st.write("")
st.markdown('<div class="lean-title">Gargalos do estado atual (AS-IS)</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lean-subtitle">
        Relação entre os gargalos identificados na análise do processo e a contribuição
        do protótipo para ampliar a visibilidade das informações.
    </div>
    """,
    unsafe_allow_html=True,
)

gargalos = [
    (
        "Avaliação e monitoramento do risco de LPP",
        "Informações de risco podem exigir consulta a diferentes registros e avaliações.",
        "Score LPP integrado, Braden e fatores de risco reunidos em uma mesma interface.",
    ),
    (
        "Coleta e registro das informações assistenciais",
        "Dados distribuídos ao longo das etapas de acompanhamento dificultam uma leitura consolidada.",
        "Estruturação de uma base única simulada para processamento analítico.",
    ),
    (
        "Integração das informações clínicas",
        "Parâmetros clínicos e fatores de risco podem ser analisados de forma fragmentada.",
        "FC, PAS, SpO₂, tendências e risco de LPP processados por um motor centralizado.",
    ),
    (
        "Comunicação e compartilhamento de informações",
        "A dispersão das informações dificulta a construção de uma visão comum da situação.",
        "Páginas padronizadas e Central de Alertas para visualização das condições identificadas.",
    ),
    (
        "Utilização dos dados para apoio à decisão",
        "Registros isolados possuem menor capacidade de evidenciar padrões e condições recorrentes.",
        "Indicadores, tendências e regras explícitas transformam os dados simulados em informação estruturada.",
    ),
]

for i in range(0, len(gargalos), 2):
    cols = st.columns(2, gap="large")
    for j, container in enumerate(cols):
        idx = i + j
        if idx >= len(gargalos):
            break
        titulo, problema, contribuicao = gargalos[idx]
        with container:
            st.markdown(
                f"""
                <div class="lean-card">
                    <div class="lean-card-title">{titulo}</div>
                    <div class="lean-card-text">
                        <b>AS-IS:</b> {problema}<br><br>
                        <b>Contribuição do protótipo:</b> {contribuicao}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.write("")


# ============================================================
# 3. MATRIZ IMPACTO × FREQUÊNCIA
# ============================================================

st.markdown('<div class="lean-title">Matriz de observação dos problemas</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lean-subtitle">
        Frequência calculada a partir das bases simuladas e impacto atribuído apenas
        para organização visual do protótipo. A matriz não constitui método clínico validado
        nem comprovação de causalidade.
    </div>
    """,
    unsafe_allow_html=True,
)

freq_pos = float(pct_posicao or 0)
freq_ocup = float(ocup_alta or 0)
freq_carga = float(carga_alta or 0)
freq_perm = float(pct_permanencia or 0)

# Impacto = parâmetro visual/conceitual, não inferido clinicamente.
matriz = pd.DataFrame(
    {
        "Condição observada": [
            "Posição > 120 min",
            "Ocupação > 90%",
            "Pac./enfermeiro ≥ 4",
            "Internação ≥ 7 dias",
        ],
        "Frequência (%)": [freq_pos, freq_ocup, freq_carga, freq_perm],
        "Impacto conceitual": [3, 3, 3, 2],
    }
)

fig_m = px.scatter(
    matriz,
    x="Frequência (%)",
    y="Impacto conceitual",
    text="Condição observada",
    size=[18, 18, 18, 18],
)
fig_m.update_traces(
    textposition="top center",
    marker=dict(opacity=.78),
    hovertemplate="<b>%{text}</b><br>Frequência: %{x:.1f}%<br>Impacto conceitual: %{y}<extra></extra>",
)
fig_m.update_layout(
    xaxis_title="Frequência nos dados simulados (%)",
    yaxis_title="Impacto conceitual",
    yaxis=dict(range=[0.7, 3.35], tickvals=[1, 2, 3], ticktext=["Baixo", "Médio", "Alto"]),
    showlegend=False,
)
fig_m.update_xaxes(gridcolor="#E7EEF3", zeroline=False)
fig_m.update_yaxes(gridcolor="#E7EEF3", zeroline=False)
tema_plotly(fig_m, 390)
st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})

st.caption(
    "O eixo de frequência é calculado diretamente a partir das bases simuladas. "
    "O eixo de impacto é uma categorização conceitual para demonstração da ferramenta "
    "e não representa resultado de validação clínica ou estudo de impacto."
)


# ============================================================
# 4. AS-IS -> TO-BE
# ============================================================

st.write("")
st.markdown('<div class="lean-title">Evolução proposta do fluxo de informação</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lean-subtitle">
        Síntese conceitual da transição entre o estado atual analisado e o fluxo proposto com o protótipo.
    </div>
    """,
    unsafe_allow_html=True,
)

fluxo = [
    ("AS-IS", "Dados dispersos", "Informações clínicas e operacionais consultadas separadamente."),
    ("Integração", "Base estruturada", "Dados simulados clínicos e operacionais organizados temporalmente."),
    ("Análise", "Motor centralizado", "Regras de LPP, alertas e tendências calculadas por uma lógica única."),
    ("Visualização", "Dashboard integrado", "Informações consolidadas em páginas com objetivos distintos."),
    ("TO-BE", "Apoio à análise preventiva", "Maior visibilidade das condições identificadas pelo protótipo."),
]

cols = st.columns(5, gap="small")
for container, (etapa, titulo, texto) in zip(cols, fluxo):
    with container:
        st.markdown(
            f"""
            <div class="lean-step">
                <div class="lean-step-label">{etapa}</div>
                <div class="lean-step-title">{titulo}</div>
                <div class="lean-step-text">{texto}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 5. PDCA
# ============================================================

st.write("")
st.markdown('<div class="lean-title">Ciclo de melhoria contínua</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lean-subtitle">
        Aplicação conceitual do PDCA para orientar futuras avaliações e melhorias do processo.
    </div>
    """,
    unsafe_allow_html=True,
)

pdca = [
    (
        "P — Plan",
        "Selecionar um problema de processo evidenciado pelos indicadores e definir objetivo, medida e período de acompanhamento.",
    ),
    (
        "D — Do",
        "Implementar a ação de melhoria em ambiente controlado, mantendo registro das alterações realizadas.",
    ),
    (
        "C — Check",
        "Comparar os indicadores antes e depois da intervenção e verificar se houve mudança mensurável no processo.",
    ),
    (
        "A — Act",
        "Padronizar a melhoria quando sustentada pelos resultados ou revisar a hipótese e iniciar um novo ciclo.",
    ),
]

cols = st.columns(4, gap="large")
for container, (titulo, texto) in zip(cols, pdca):
    with container:
        st.markdown(
            f"""
            <div class="lean-card" style="min-height:180px;">
                <div class="lean-card-title">{titulo}</div>
                <div class="lean-card-text">{texto}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 6. OPORTUNIDADES DE MELHORIA
# ============================================================

st.write("")
st.markdown('<div class="lean-title">Oportunidades para avaliação futura</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lean-subtitle">
        Possíveis frentes de análise derivadas do processo. Os efeitos abaixo são hipóteses
        de melhoria e devem ser medidos antes de qualquer conclusão sobre impacto.
    </div>
    """,
    unsafe_allow_html=True,
)

oportunidades = pd.DataFrame(
    [
        [
            "Consolidação das informações",
            "Tempo necessário para localizar e reunir dados relevantes",
            "Avaliar possível redução do tempo de busca por informações",
        ],
        [
            "Acompanhamento do posicionamento",
            "Frequência de registros acima de 120 min na posição atual",
            "Avaliar mudanças após ações de prevenção e organização do processo",
        ],
        [
            "Gestão da capacidade",
            "Taxa de ocupação e períodos acima do parâmetro metodológico",
            "Investigar associação com sobrecarga e fluxo da unidade",
        ],
        [
            "Dimensionamento observado",
            "Relação pacientes/enfermeiro ao longo dos períodos",
            "Avaliar variações operacionais e sua relação com o processo",
        ],
        [
            "Uso dos alertas",
            "Quantidade e tipos de alertas identificados",
            "Avaliar utilidade, recorrência e necessidade de ajuste das regras",
        ],
    ],
    columns=["Frente", "Indicador para acompanhamento", "Objetivo de avaliação"],
)
st.dataframe(oportunidades, use_container_width=True, hide_index=True)


st.caption(
    "Protótipo acadêmico com dados simulados. A página Lean organiza indicadores e "
    "oportunidades de melhoria a partir da análise conceitual do processo. Não demonstra "
    "redução real de lead time, eventos adversos, risco clínico ou carga de trabalho, "
    "uma vez que essas hipóteses exigem validação futura em ambiente real."
)
