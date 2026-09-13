# ============================================================
# MONITORAMENTO CLÍNICO
# UTI INTELLIGENT CARE
#
# Página dedicada ao acompanhamento individual do paciente.
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


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Monitoramento Clínico | UTI Intelligent Care",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Monitoramento")


# ============================================================
# CSS EXCLUSIVO DA PÁGINA
# ============================================================

st.markdown(
    """
    <style>
    .mon-section-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:8px 0 4px 0;
    }

    .mon-section-subtitle {
        color:#738B9C;
        font-size:15px;
        line-height:1.5;
        margin-bottom:14px;
    }

    .mon-context-card {
        background:#F6FAFC;
        border:1px solid #DCE8EF;
        border-radius:14px;
        padding:15px 18px;
        color:#567186;
        font-size:14px;
        line-height:1.5;
    }

    .mon-class-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:15px;
        padding:18px 20px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
        min-height:116px;
    }

    .mon-class-label {
        color:#71899A;
        font-size:13px;
        font-weight:750;
        text-transform:uppercase;
        letter-spacing:.04em;
        margin-bottom:7px;
    }

    .mon-class-value {
        color:#0D2A45;
        font-size:23px;
        font-weight:850;
    }

    .mon-class-note {
        color:#6F8798;
        font-size:13px;
        margin-top:5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def converter_timestamp(serie):
    serie_original = serie.astype(str).str.strip()

    convertido = pd.to_datetime(
        serie_original,
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    )

    mascara = convertido.isna()

    if mascara.any():
        convertido.loc[mascara] = pd.to_datetime(
            serie_original.loc[mascara],
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce",
        )

    mascara = convertido.isna()

    if mascara.any():
        convertido.loc[mascara] = pd.to_datetime(
            serie_original.loc[mascara],
            errors="coerce",
            dayfirst=True,
        )

    return convertido


def tema_plotly(fig, altura=330):
    fig.update_layout(
        title_text="",
        height=altura,
        margin=dict(l=18, r=18, t=18, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Segoe UI, Arial, sans-serif",
            size=14,
            color="#35576F",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=14,
        ),
        showlegend=False,
    )

    fig.update_xaxes(
        gridcolor="#F0F4F7",
        zeroline=False,
        tickformat="%d/%m\n%H:%M",
    )

    fig.update_yaxes(
        gridcolor="#E7EEF3",
        zeroline=False,
    )

    return fig


def valor_formatado(registro, coluna, formato):
    if coluna not in registro.index:
        return "N/D"

    valor = pd.to_numeric(
        registro[coluna],
        errors="coerce",
    )

    if pd.isna(valor):
        return "N/D"

    return formato.format(valor)


def formatar_texto(valor):
    if pd.isna(valor):
        return "N/D"

    return (
        str(valor)
        .replace("_", " ")
        .strip()
        .capitalize()
    )


def encontrar_coluna(dataframe, opcoes):
    for coluna in opcoes:
        if coluna in dataframe.columns:
            return coluna
    return None


def grafico_linha(
    dataframe,
    coluna,
    titulo,
    eixo_y,
    cor="#2B84C5",
    altura=315,
):
    if coluna not in dataframe.columns:
        st.info(f"{titulo}: dado não disponível.")
        return

    dados = (
        dataframe[
            [
                "timestamp",
                coluna,
            ]
        ]
        .copy()
    )

    dados[coluna] = pd.to_numeric(
        dados[coluna],
        errors="coerce",
    )

    dados = (
        dados
        .dropna()
        .sort_values("timestamp")
    )

    if dados.empty:
        st.info(f"{titulo}: não há dados no período selecionado.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dados["timestamp"],
            y=dados[coluna],
            mode="lines",
            line=dict(
                color=cor,
                width=3,
            ),
            hovertemplate=(
                "<b>%{x|%d/%m %H:%M}</b>"
                "<br>" + eixo_y + ": %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title=eixo_y,
    )

    tema_plotly(
        fig,
        altura=altura,
    )

    st.markdown(
        f'<div class="mon-section-title" style="font-size:19px;">{titulo}</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# CARREGAMENTO
# ============================================================

try:
    df = load_data().copy()
except Exception as e:
    st.error("Não foi possível carregar os dados.")
    st.exception(e)
    st.stop()

if df.empty:
    st.error("A base clínica está vazia.")
    st.stop()

if "timestamp" not in df.columns:
    st.error("A coluna `timestamp` não foi encontrada.")
    st.stop()

if "id_paciente" not in df.columns:
    st.error("A coluna `id_paciente` não foi encontrada.")
    st.stop()


# ============================================================
# PREPARAÇÃO TEMPORAL
# ============================================================

df["timestamp"] = converter_timestamp(
    df["timestamp"]
)

df = (
    df
    .dropna(subset=["timestamp"])
    .sort_values("timestamp")
    .copy()
)

if df.empty:
    st.error("Não existem timestamps válidos na base.")
    st.stop()


# ============================================================
# MOTOR ANALÍTICO
# ============================================================

try:
    df = processar_dados(df)
except Exception as e:
    st.error("Erro no processamento analítico.")
    st.exception(e)
    st.stop()

try:
    df = processar_riscos(df)
except Exception as e:
    st.error("Erro no motor de risco.")
    st.exception(e)
    st.stop()


# ============================================================
# CABEÇALHO
# ============================================================

cabecalho_pagina(
    "Monitoramento Clínico",
    (
        "Acompanhamento individual da evolução de sinais vitais, "
        "indicadores laboratoriais e tendência clínica."
    ),
    secao="Paciente individual",
    badge="Dados simulados",
)


# ============================================================
# SELEÇÃO DO PACIENTE
# ============================================================

df["id_paciente"] = pd.to_numeric(
    df["id_paciente"],
    errors="coerce",
)

ids = (
    df["id_paciente"]
    .dropna()
    .astype(int)
    .sort_values()
    .unique()
    .tolist()
)

if not ids:
    st.error("Nenhum paciente válido foi encontrado.")
    st.stop()


st.markdown(
    '<div class="mon-section-title">Selecionar acompanhamento</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mon-section-subtitle">
        Escolha o paciente e o intervalo que deseja analisar.
    </div>
    """,
    unsafe_allow_html=True,
)

f1, f2 = st.columns(
    [0.72, 1.28],
    gap="large",
)

with f1:
    paciente_selecionado = st.selectbox(
        "Paciente",
        options=ids,
        format_func=lambda x: f"Paciente {int(x):02d}",
    )


df_paciente = (
    df[
        df["id_paciente"]
        == paciente_selecionado
    ]
    .copy()
)

if df_paciente.empty:
    st.error("Não foram encontrados registros para esse paciente.")
    st.stop()


data_min_paciente = df_paciente["timestamp"].min()
data_max_paciente = df_paciente["timestamp"].max()


with f2:
    periodo = st.date_input(
        "Período de análise",
        value=(
            data_min_paciente.date(),
            data_max_paciente.date(),
        ),
        min_value=data_min_paciente.date(),
        max_value=data_max_paciente.date(),
    )


# ============================================================
# FILTRO DO PERÍODO
# ============================================================

df_monitoramento = df_paciente.copy()

if isinstance(periodo, tuple) and len(periodo) == 2:

    inicio = pd.Timestamp(periodo[0])

    fim = (
        pd.Timestamp(periodo[1])
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )

    df_monitoramento = (
        df_monitoramento[
            (df_monitoramento["timestamp"] >= inicio)
            & (df_monitoramento["timestamp"] <= fim)
        ]
        .sort_values("timestamp")
        .copy()
    )


if df_monitoramento.empty:
    st.warning(
        "Não há registros para o paciente no período selecionado."
    )
    st.stop()


registro_atual = (
    df_monitoramento
    .sort_values("timestamp")
    .iloc[-1]
)


# ============================================================
# IDENTIFICAÇÃO E CONTEXTO
# ============================================================

st.write("")

i1, i2, i3 = st.columns(3)

with i1:
    st.metric(
        "Paciente",
        f"P{int(paciente_selecionado):02d}",
    )

with i2:
    st.metric(
        "Registros no período",
        len(df_monitoramento),
    )

with i3:
    st.metric(
        "Última atualização",
        registro_atual["timestamp"].strftime("%d/%m/%Y %H:%M"),
    )


st.markdown(
    f"""
    <div class="mon-context-card">
        Período disponível para este paciente:
        <b>{data_min_paciente.strftime('%d/%m/%Y %H:%M')}</b>
        até
        <b>{data_max_paciente.strftime('%d/%m/%Y %H:%M')}</b>.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SITUAÇÃO ATUAL
# ============================================================

st.write("")

st.markdown(
    '<div class="mon-section-title">Situação clínica atual</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mon-section-subtitle">
        Último registro disponível dentro do período selecionado.
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric(
        "Frequência cardíaca",
        valor_formatado(
            registro_atual,
            "frequencia_cardiaca",
            "{:.0f} bpm",
        ),
    )

with m2:
    st.metric(
        "SpO₂",
        valor_formatado(
            registro_atual,
            "saturacao_O2",
            "{:.0f}%",
        ),
    )

with m3:
    st.metric(
        "PAM",
        valor_formatado(
            registro_atual,
            "pressao_media",
            "{:.0f} mmHg",
        ),
    )

with m4:
    st.metric(
        "Temperatura",
        valor_formatado(
            registro_atual,
            "temperatura",
            "{:.1f} °C",
        ),
    )

with m5:
    st.metric(
        "Lactato",
        valor_formatado(
            registro_atual,
            "lactato",
            "{:.2f}",
        ),
    )


# ============================================================
# CLASSIFICAÇÃO E SCORE
# ============================================================

col_classificacao = encontrar_coluna(
    df_monitoramento,
    [
        "classificacao_clinica",
    ],
)

col_score = encontrar_coluna(
    df_monitoramento,
    [
        "score_clinico",
    ],
)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    classificacao = (
        formatar_texto(registro_atual[col_classificacao])
        if col_classificacao
        else "N/D"
    )

    st.markdown(
        f"""
        <div class="mon-class-card">
            <div class="mon-class-label">Classificação atual</div>
            <div class="mon-class-value">{classificacao}</div>
            <div class="mon-class-note">
                Interpretação conceitual do motor analítico
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    if col_score:
        score = pd.to_numeric(
            registro_atual[col_score],
            errors="coerce",
        )
        score_texto = (
            f"{score:.1f}"
            if pd.notna(score)
            else "N/D"
        )
    else:
        score_texto = "N/D"

    st.markdown(
        f"""
        <div class="mon-class-card">
            <div class="mon-class-label">Score clínico</div>
            <div class="mon-class-value">{score_texto}</div>
            <div class="mon-class-note">
                Valor do registro mais recente
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    quantidade_alertas = pd.to_numeric(
        registro_atual.get(
            "quantidade_alertas",
            None,
        ),
        errors="coerce",
    )

    alertas_texto = (
        str(int(quantidade_alertas))
        if pd.notna(quantidade_alertas)
        else "N/D"
    )

    st.markdown(
        f"""
        <div class="mon-class-card">
            <div class="mon-class-label">Alertas ativos</div>
            <div class="mon-class-value">{alertas_texto}</div>
            <div class="mon-class-note">
                Alertas clínicos associados ao registro atual
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SINAIS VITAIS
# ============================================================

st.write("")

st.markdown(
    '<div class="mon-section-title">Evolução dos sinais vitais</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mon-section-subtitle">
        Comportamento temporal dos principais parâmetros fisiológicos.
    </div>
    """,
    unsafe_allow_html=True,
)

g1, g2 = st.columns(2, gap="large")

with g1:
    grafico_linha(
        df_monitoramento,
        "frequencia_cardiaca",
        "Frequência cardíaca",
        "FC (bpm)",
        "#2B84C5",
    )

with g2:
    grafico_linha(
        df_monitoramento,
        "saturacao_O2",
        "Saturação de oxigênio",
        "SpO₂ (%)",
        "#3AA690",
    )


# ============================================================
# PRESSÃO + TEMPERATURA
# ============================================================

g3, g4 = st.columns(2, gap="large")

with g3:

    if all(
        coluna in df_monitoramento.columns
        for coluna in [
            "pressao_sistolica",
            "pressao_diastolica",
        ]
    ):

        dados_pa = (
            df_monitoramento[
                [
                    "timestamp",
                    "pressao_sistolica",
                    "pressao_diastolica",
                ]
            ]
            .copy()
        )

        dados_pa["pressao_sistolica"] = pd.to_numeric(
            dados_pa["pressao_sistolica"],
            errors="coerce",
        )

        dados_pa["pressao_diastolica"] = pd.to_numeric(
            dados_pa["pressao_diastolica"],
            errors="coerce",
        )

        dados_pa = dados_pa.dropna(
            how="all",
            subset=[
                "pressao_sistolica",
                "pressao_diastolica",
            ],
        )

        st.markdown(
            '<div class="mon-section-title" style="font-size:19px;">Pressão arterial</div>',
            unsafe_allow_html=True,
        )

        if not dados_pa.empty:

            fig_pa = go.Figure()

            fig_pa.add_trace(
                go.Scatter(
                    x=dados_pa["timestamp"],
                    y=dados_pa["pressao_sistolica"],
                    mode="lines",
                    name="Sistólica",
                    line=dict(
                        color="#5B8FD5",
                        width=3,
                    ),
                )
            )

            fig_pa.add_trace(
                go.Scatter(
                    x=dados_pa["timestamp"],
                    y=dados_pa["pressao_diastolica"],
                    mode="lines",
                    name="Diastólica",
                    line=dict(
                        color="#A574C5",
                        width=3,
                    ),
                )
            )

            fig_pa.update_layout(
                xaxis_title="",
                yaxis_title="mmHg",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.01,
                    xanchor="left",
                    x=0,
                ),
            )

            tema_plotly(
                fig_pa,
                altura=315,
            )

            fig_pa.update_layout(
                showlegend=True,
            )

            st.plotly_chart(
                fig_pa,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        else:
            st.info("Pressão arterial: não há dados no período.")

    else:
        st.info("Pressão arterial não disponível.")

with g4:
    grafico_linha(
        df_monitoramento,
        "temperatura",
        "Temperatura corporal",
        "Temperatura (°C)",
        "#E38B54",
    )


# ============================================================
# INDICADORES LABORATORIAIS
# ============================================================

st.write("")

st.markdown(
    '<div class="mon-section-title">Indicadores laboratoriais</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mon-section-subtitle">
        Evolução dos marcadores laboratoriais disponíveis para o paciente.
    </div>
    """,
    unsafe_allow_html=True,
)

l1, l2, l3 = st.columns(3, gap="large")

with l1:
    grafico_linha(
        df_monitoramento,
        "lactato",
        "Lactato",
        "Lactato",
        "#D97863",
        altura=300,
    )

with l2:
    grafico_linha(
        df_monitoramento,
        "leucocitos",
        "Leucócitos",
        "Leucócitos",
        "#6C8FD8",
        altura=300,
    )

with l3:
    grafico_linha(
        df_monitoramento,
        "creatinina",
        "Creatinina",
        "Creatinina",
        "#8B7BC6",
        altura=300,
    )


# ============================================================
# TENDÊNCIA CLÍNICA
# ============================================================

st.write("")

st.markdown(
    '<div class="mon-section-title">Tendência clínica</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mon-section-subtitle">
        Evolução do score clínico do paciente ao longo do período.
    </div>
    """,
    unsafe_allow_html=True,
)

if col_score:
    grafico_linha(
        df_monitoramento,
        col_score,
        "Evolução do score clínico",
        "Score clínico",
        "#315F89",
        altura=340,
    )
else:
    st.info(
        "O score clínico não está disponível na base processada."
    )


# ============================================================
# ACESSO RÁPIDO
# ============================================================

st.write("")

a1, a2 = st.columns(2)

with a1:
    st.page_link(
        "pages/5_Central_de_Alertas.py",
        label="Ver alertas e priorização",
        use_container_width=True,
    )

with a2:
    st.page_link(
        "pages/3_Gestao_LPP.py",
        label="Ver risco de LPP",
        use_container_width=True,
    )


# ============================================================
# AVISO ACADÊMICO
# ============================================================

st.caption(
    "Protótipo acadêmico com dados simulados. "
    "Os indicadores, scores e classificações possuem finalidade "
    "conceitual e não substituem avaliação clínica ou protocolos institucionais."
)
