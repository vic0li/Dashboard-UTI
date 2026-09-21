# ============================================================
# VISÃO GERAL DA UTI
# UTI INTELLIGENT CARE
#
# Compatível com o motor analítico descrito no TCC até a Seção 5.5.
# ============================================================

from pathlib import Path

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
    page_title="Visão Geral | UTI Intelligent Care",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Visão geral")


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
    </style>
    """,
    unsafe_allow_html=True,
)


def tema_plotly(fig, altura=350):
    fig.update_layout(
        title_text="",
        height=altura,
        margin=dict(l=20, r=20, t=18, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", size=15, color="#284A62"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=14, font_family="Segoe UI"),
    )
    return fig


def carregar_operacional():
    raiz = Path(__file__).resolve().parent.parent
    caminho = raiz / "data" / "UTI_operacional.csv"

    if not caminho.exists():
        return pd.DataFrame()

    try:
        op = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
        if "timestamp" in op.columns:
            op["timestamp_dt"] = pd.to_datetime(op["timestamp"], errors="coerce")
            op = op.sort_values("timestamp_dt")
        return op
    except Exception:
        return pd.DataFrame()


# ============================================================
# DADOS E MOTOR ÚNICO
# ============================================================

try:
    df = load_data().copy()
    df = processar_dados(df)
    df = processar_riscos(df)
except Exception as e:
    st.error("Não foi possível processar a base do dashboard.")
    st.exception(e)
    st.stop()

if df.empty:
    st.error("A base clínica está vazia.")
    st.stop()

if "timestamp" in df.columns:
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
else:
    df["timestamp_dt"] = pd.NaT

if "id_paciente" in df.columns and df["timestamp_dt"].notna().any():
    df_atual = (
        df.dropna(subset=["timestamp_dt"])
        .sort_values("timestamp_dt")
        .groupby("id_paciente", as_index=False)
        .tail(1)
        .copy()
    )
elif "id_paciente" in df.columns:
    df_atual = df.drop_duplicates("id_paciente", keep="last").copy()
else:
    df_atual = df.copy()


# ============================================================
# MÉTRICAS
# ============================================================

total_pacientes = (
    int(df_atual["id_paciente"].nunique())
    if "id_paciente" in df_atual.columns
    else len(df_atual)
)

class_lpp = df_atual.get(
    "classificacao_lpp",
    pd.Series("Não disponível", index=df_atual.index),
).astype(str)

pacientes_alto_lpp = int(class_lpp.eq("Alto").sum())

qtd_alertas = pd.to_numeric(
    df_atual.get("quantidade_alertas", pd.Series(0, index=df_atual.index)),
    errors="coerce",
).fillna(0)

pacientes_com_alerta = int((qtd_alertas > 0).sum())
total_alertas = int(qtd_alertas.sum())

df_op = carregar_operacional()
ocupacao_atual = None
leitos_disponiveis = None
pacientes_enfermeiro = None

if not df_op.empty:
    op_atual = df_op.iloc[-1]

    valor = pd.to_numeric(op_atual.get("taxa_ocupacao_pct"), errors="coerce")
    if pd.notna(valor):
        ocupacao_atual = float(valor)

    operacionais = pd.to_numeric(op_atual.get("leitos_operacionais"), errors="coerce")
    internados = pd.to_numeric(op_atual.get("pacientes_internados"), errors="coerce")
    if pd.notna(operacionais) and pd.notna(internados):
        leitos_disponiveis = max(int(operacionais - internados), 0)

    valor = pd.to_numeric(op_atual.get("pacientes_por_enfermeiro"), errors="coerce")
    if pd.notna(valor):
        pacientes_enfermeiro = float(valor)


# ============================================================
# CABEÇALHO
# ============================================================

cabecalho_pagina(
    "Visão Geral da UTI",
    "Síntese executiva dos indicadores preventivos, clínicos e operacionais simulados.",
    secao="Panorama executivo",
    badge="Dados simulados",
)

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

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Pacientes monitorados", total_pacientes)
with k2:
    st.metric("Ocupação da UTI", f"{ocupacao_atual:.1f}%" if ocupacao_atual is not None else "N/D")
with k3:
    st.metric("Alto risco LPP", pacientes_alto_lpp)
with k4:
    st.metric("Pacientes com alerta", pacientes_com_alerta)


# ============================================================
# PANORAMA CLÍNICO
# ============================================================

st.write("")
st.markdown(
    '<div class="overview-section-title">Panorama clínico</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="overview-section-subtitle">
        Situação atual dos pacientes a partir das regras de alerta do protótipo.
        Esta visualização substitui a antiga classificação clínica, que não faz parte do motor atual.
    </div>
    """,
    unsafe_allow_html=True,
)

situacao = pd.DataFrame(
    {
        "Situação": ["Sem alertas", "Com alertas"],
        "Pacientes": [
            int((qtd_alertas == 0).sum()),
            int((qtd_alertas > 0).sum()),
        ],
    }
)

fig_pan = px.bar(
    situacao,
    x="Situação",
    y="Pacientes",
)
fig_pan.update_traces(
    marker_color=["#6D9F86", "#B85C5C"],
    text=situacao["Pacientes"],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>%{y} paciente(s)<extra></extra>",
)
fig_pan.update_layout(
    showlegend=False,
    xaxis_title="",
    yaxis_title="Pacientes",
)
fig_pan.update_yaxes(gridcolor="#E7EEF3", zeroline=False, dtick=1)
fig_pan.update_xaxes(showgrid=False)
tema_plotly(fig_pan, 300)
st.plotly_chart(fig_pan, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# RISCO LPP + RESUMO OPERACIONAL
# ============================================================

st.write("")
col_lpp, col_op = st.columns([1.25, 0.75], gap="large")

with col_lpp:
    st.markdown(
        '<div class="overview-section-title">Distribuição do risco de LPP</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="overview-section-subtitle">
            Classificação final do modelo integrado de risco no registro atual.
        </div>
        """,
        unsafe_allow_html=True,
    )

    ordem = ["Baixo", "Médio", "Alto"]
    dist = (
        class_lpp[class_lpp.isin(ordem)]
        .value_counts()
        .reindex(ordem, fill_value=0)
        .rename_axis("Classificação")
        .reset_index(name="Pacientes")
    )

    fig = px.bar(dist, x="Classificação", y="Pacientes")
    fig.update_traces(
        marker_color=["#6D9F86", "#C7A252", "#B85C5C"],
        text=dist["Pacientes"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y} paciente(s)<extra></extra>",
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Pacientes")
    fig.update_yaxes(gridcolor="#E7EEF3", zeroline=False, dtick=1)
    fig.update_xaxes(showgrid=False)
    tema_plotly(fig, 340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_op:
    st.markdown(
        '<div class="overview-section-title">Resumo operacional</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="overview-section-subtitle">
            Condição operacional associada ao período mais recente.
        </div>
        """,
        unsafe_allow_html=True,
    )

    ocup_texto = f"{ocupacao_atual:.1f}%" if ocupacao_atual is not None else "N/D"
    leitos_texto = str(leitos_disponiveis) if leitos_disponiveis is not None else "N/D"
    equipe_texto = f"{pacientes_enfermeiro:.1f}" if pacientes_enfermeiro is not None else "N/D"

    st.markdown(
        f"""
        <div class="overview-card">
            <div class="overview-small-title">Ocupação atual</div>
            <div class="overview-number">{ocup_texto}</div>
            <div class="overview-status">percentual de leitos operacionais ocupados</div>
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
                <div class="overview-status">relação operacional</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TENDÊNCIAS + ALERTAS
# ============================================================

st.write("")
trend_col, alert_col = st.columns([1.15, 0.85], gap="large")

with trend_col:
    st.markdown(
        '<div class="overview-section-title">Tendências clínicas atuais</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="overview-section-subtitle">
            Direção da última variação observada em FC, PAS e SpO₂.
        </div>
        """,
        unsafe_allow_html=True,
    )

    variaveis = {
        "FC": "frequencia_cardiaca_tendencia",
        "PAS": "pressao_sistolica_tendencia",
        "SpO₂": "saturacao_O2_tendencia",
    }
    linhas = []
    for nome, coluna in variaveis.items():
        if coluna in df_atual.columns:
            contagem = df_atual[coluna].astype(str).value_counts()
            for tendencia in ["subindo", "estavel", "descendo"]:
                linhas.append(
                    {
                        "Parâmetro": nome,
                        "Tendência": tendencia.capitalize(),
                        "Pacientes": int(contagem.get(tendencia, 0)),
                    }
                )

    if linhas:
        tend = pd.DataFrame(linhas)
        fig_t = px.bar(
            tend,
            x="Parâmetro",
            y="Pacientes",
            color="Tendência",
            barmode="group",
            category_orders={"Tendência": ["Subindo", "Estavel", "Descendo"]},
            color_discrete_map={
                "Subindo": "#4D8BC4",
                "Estavel": "#91A5B4",
                "Descendo": "#6D9F86",
            },
        )
        fig_t.update_layout(
            legend_title_text="Direção",
            xaxis_title="",
            yaxis_title="Pacientes",
        )
        fig_t.update_yaxes(gridcolor="#E7EEF3", zeroline=False, dtick=1)
        fig_t.update_xaxes(showgrid=False)
        tema_plotly(fig_t, 345)
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("As tendências de FC, PAS e SpO₂ não estão disponíveis.")

with alert_col:
    st.markdown(
        '<div class="overview-section-title">Alertas do motor</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="overview-section-subtitle">
            Ocorrências atuais segundo as regras definidas para FC, PAS, SpO₂ e LPP.
        </div>
        """,
        unsafe_allow_html=True,
    )

    alertas = {
        "FC": "alerta_fc_motor",
        "PAS": "alerta_pas_motor",
        "SpO₂": "alerta_spo2_motor",
        "LPP": "alerta_lpp_motor",
    }
    resumo_alertas = pd.DataFrame(
        {
            "Tipo": list(alertas.keys()),
            "Ocorrências": [
                int(df_atual.get(col, pd.Series(False, index=df_atual.index)).fillna(False).astype(bool).sum())
                for col in alertas.values()
            ],
        }
    )

    fig_a = px.bar(resumo_alertas, x="Tipo", y="Ocorrências")
    fig_a.update_traces(
        marker_color="#B85C5C",
        text=resumo_alertas["Ocorrências"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y} ocorrência(s)<extra></extra>",
    )
    fig_a.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ocorrências")
    fig_a.update_yaxes(gridcolor="#E7EEF3", zeroline=False, dtick=1)
    fig_a.update_xaxes(showgrid=False)
    tema_plotly(fig_a, 345)
    st.plotly_chart(fig_a, use_container_width=True, config={"displayModeBar": False})

    st.caption(f"{total_alertas} alerta(s) ativo(s) em {pacientes_com_alerta} paciente(s).")


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
        Ordenação de interface baseada em alto risco de LPP, quantidade de alertas
        e Score LPP. Não constitui um índice clínico de prioridade.
    </div>
    """,
    unsafe_allow_html=True,
)

rank = df_atual.copy()
rank["_alto_lpp"] = rank.get(
    "classificacao_lpp",
    pd.Series("", index=rank.index),
).astype(str).eq("Alto").astype(int)
rank["_alertas"] = pd.to_numeric(
    rank.get("quantidade_alertas", pd.Series(0, index=rank.index)),
    errors="coerce",
).fillna(0)
rank["_score_lpp"] = pd.to_numeric(
    rank.get("score_lpp", pd.Series(0, index=rank.index)),
    errors="coerce",
).fillna(0)

top5 = rank.sort_values(
    ["_alto_lpp", "_alertas", "_score_lpp"],
    ascending=[False, False, False],
).head(5)

tabela = pd.DataFrame()
if "id_paciente" in top5.columns:
    ids = pd.to_numeric(top5["id_paciente"], errors="coerce").fillna(0).astype(int)
    tabela["Paciente"] = "P" + ids.astype(str).str.zfill(2)

tabela["Score LPP"] = pd.to_numeric(top5["score_lpp"], errors="coerce").round(2).values
tabela["Risco LPP"] = top5["classificacao_lpp"].astype(str).values
tabela["Alertas"] = top5["_alertas"].astype(int).values
tabela["Motivos"] = top5.get(
    "motivos_alerta",
    pd.Series("Sem alerta", index=top5.index),
).astype(str).values

for rotulo, coluna in [
    ("FC", "frequencia_cardiaca"),
    ("PAS", "pressao_sistolica"),
    ("SpO₂", "saturacao_O2"),
]:
    if coluna in top5.columns:
        tabela[rotulo] = pd.to_numeric(top5[coluna], errors="coerce").round(1).values

st.dataframe(tabela, use_container_width=True, hide_index=True, height=235)


# ============================================================
# ATALHOS
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

st.caption(
    "Protótipo acadêmico com dados simulados. "
    "Os indicadores apresentados possuem finalidade conceitual "
    "e não substituem avaliação profissional, protocolos institucionais "
    "ou sistemas clínicos validados."
)
