# ============================================================
# GESTÃO DE LESÃO POR PRESSÃO (LPP)
# UTI INTELLIGENT CARE
#
# Página dedicada à prevenção, estratificação e monitoramento
# do risco de lesão por pressão em pacientes da UTI.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.analytics import processar_dados
from utils.risk_engine import processar_riscos
from utils.styling import aplicar_estilo, topo_produto, navegacao_topo


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Gestão de LPP | UTI Intelligent Care",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# ESTILO GLOBAL / NAVEGAÇÃO
# ============================================================

aplicar_estilo()
topo_produto()
navegacao_topo("LPP")


# ============================================================
# ESTILO EXCLUSIVO DA PÁGINA LPP
# ============================================================

st.markdown(
    """
    <style>

    /* Cabeçalho da página */
    .lpp-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 12px 2px 20px 2px;
    }

    .lpp-header-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .lpp-header-icon {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        display: grid;
        place-items: center;
        background: #EAF4FA;
        border: 1px solid #D4E6F1;
        color: #1F6EA5;
        font-size: 27px;
        font-weight: 800;
    }

    .lpp-title {
        color: #0D2A45;
        font-size: 34px;
        line-height: 1.15;
        font-weight: 850;
        letter-spacing: -0.03em;
        margin: 0;
    }

    .lpp-subtitle {
        color: #667F92;
        font-size: 17px;
        line-height: 1.5;
        margin-top: 6px;
    }

    .lpp-info {
        max-width: 340px;
        background: #EEF7FC;
        border: 1px solid #D3E7F2;
        border-radius: 12px;
        padding: 12px 15px;
        color: #45657C;
        font-size: 14px;
        line-height: 1.45;
    }

    /* Títulos de bloco */
    .lpp-section-title {
        color: #0D2A45;
        font-size: 25px;
        font-weight: 850;
        letter-spacing: -0.02em;
        margin: 8px 0 4px 0;
    }

    .lpp-section-subtitle {
        color: #738B9C;
        font-size: 15px;
        margin-bottom: 14px;
    }

    /* Cards customizados */
    .lpp-card {
        background: rgba(255,255,255,.98);
        border: 1px solid #D8E4EC;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 8px 22px rgba(18,55,82,.055);
    }

    .lpp-mini-label {
        color: #5E778A;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .lpp-mini-value {
        color: #0B2034;
        font-size: 31px;
        font-weight: 850;
        letter-spacing: -0.03em;
    }

    /* Status de risco */
    .pill-baixo,
    .pill-moderado,
    .pill-alto,
    .pill-muito-alto,
    .pill-critico {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 750;
    }

    .pill-baixo {
        color: #287A46;
        background: #E8F6EC;
    }

    .pill-moderado {
        color: #9B6B00;
        background: #FFF3D8;
    }

    .pill-alto {
        color: #B53D36;
        background: #FDE8E7;
    }

    .pill-muito-alto,
    .pill-critico {
        color: #8E2530;
        background: #F8DDE1;
    }

    /* Recomendação */
    .recommendation {
        background: #FFF1F0;
        border: 1px solid #F4CECB;
        border-left: 5px solid #E5484D;
        border-radius: 12px;
        padding: 15px 17px;
        margin-top: 12px;
    }

    .recommendation-title {
        color: #B62F35;
        font-size: 17px;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .recommendation-text {
        color: #5C4144;
        font-size: 15px;
        line-height: 1.5;
    }

    .recommendation-ok {
        background: #EFF9F4;
        border: 1px solid #CDEADB;
        border-left: 5px solid #159A7A;
        border-radius: 12px;
        padding: 15px 17px;
        margin-top: 12px;
    }

    .recommendation-ok .recommendation-title {
        color: #16765F;
    }

    .recommendation-ok .recommendation-text {
        color: #49665D;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def converter_timestamp(serie):
    """Converte a coluna timestamp para datetime."""
    return pd.to_datetime(
        serie.astype(str).str.strip(),
        dayfirst=True,
        errors="coerce",
    )


def normalizar_nivel(valor):
    """Padroniza nomes do nível de risco."""
    valor = str(valor).strip().lower()
    mapa = {
        "baixo": "Baixo",
        "moderado": "Moderado",
        "alto": "Alto",
        "muito_alto": "Muito alto",
        "muito alto": "Muito alto",
        "crítico": "Crítico",
        "critico": "Crítico",
    }
    return mapa.get(valor, valor.replace("_", " ").title())


def classe_risco(valor):
    valor = str(valor).strip().lower()
    if valor in ("crítico", "critico"):
        return "pill-critico"
    if valor in ("muito_alto", "muito alto"):
        return "pill-muito-alto"
    if valor == "alto":
        return "pill-alto"
    if valor == "moderado":
        return "pill-moderado"
    return "pill-baixo"


def tema_plotly(fig, altura=370):
    """Padroniza os gráficos da página."""
    fig.update_layout(
        height=altura,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Segoe UI, Arial, sans-serif",
            color="#284A62",
            size=15,
        ),
        title_font=dict(
            size=18,
            color="#0D2A45",
        ),
        legend=dict(
            font=dict(size=14),
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=14,
            font_family="Segoe UI",
        ),
    )
    return fig


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

df = load_data().copy()

if df.empty:
    st.warning("A base de dados está vazia.")
    st.stop()

# Fonte oficial dos indicadores: pipeline analítico + motor de risco.
df = processar_dados(df)
df = processar_riscos(df)

df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp_dt"])

if df.empty:
    st.warning("Não foi possível interpretar os timestamps da base.")
    st.stop()


# ============================================================
# ÚLTIMO REGISTRO DE CADA PACIENTE
# ============================================================

df_atual = (
    df.sort_values("timestamp_dt")
      .groupby("id_paciente", as_index=False)
      .tail(1)
      .copy()
)

df_atual["classificacao_lpp_fmt"] = (
    df_atual["classificacao_lpp"]
    .apply(normalizar_nivel)
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="lpp-header">
        <div class="lpp-header-left">
            <div class="lpp-header-icon">◇</div>
            <div>
                <div class="lpp-title">Gestão de Lesão por Pressão (LPP)</div>
                <div class="lpp-subtitle">
                    Estratificação do risco, posicionamento e priorização
                    preventiva dos pacientes da UTI.
                </div>
            </div>
        </div>
        <div class="lpp-info">
            <b>Modelo acadêmico de apoio à decisão</b><br>
            Os indicadores abaixo são calculados a partir dos dados simulados
            disponíveis no protótipo.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPIs
# ============================================================

total_pacientes = df_atual["id_paciente"].nunique()

alto_risco = df_atual[
    df_atual["classificacao_lpp"].astype(str).str.lower().isin(
        ["alto", "crítico", "critico"]
    )
]["id_paciente"].nunique()

risco_medio = df_atual["score_lpp"].mean()

tempo_medio = df_atual["tempo_posicao_atual_min"].mean()

reposicionamentos_media = df_atual["mudancas_posicao_24h"].mean()

reposicionamento_pendente = int(
    (
        pd.to_numeric(
            df_atual["tempo_posicao_atual_min"],
            errors="coerce",
        )
        >= 120
    ).sum()
)


st.markdown(
    '<div class="lpp-section-title">Situação atual da UTI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="lpp-section-subtitle">Indicadores calculados a partir do registro mais recente de cada paciente.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Alto / crítico",
        f"{alto_risco}",
    )

with c2:
    st.metric(
        "Reposicionamento ≥ 120 min",
        f"{reposicionamento_pendente}",
        help="Pacientes com 120 minutos ou mais na posição atual.",
    )

with c3:
    st.metric(
        "Score médio de LPP",
        f"{risco_medio:.1f}",
    )

with c4:
    st.metric(
        "Tempo médio na posição",
        f"{tempo_medio:.0f} min",
    )

with c5:
    st.metric(
        "Mudanças de posição / 24h",
        f"{reposicionamentos_media:.1f}",
    )


st.write("")


# ============================================================
# DISTRIBUIÇÃO DE RISCO + SCORE POR PACIENTE
# ============================================================

graf1, graf2 = st.columns([0.92, 1.28], gap="large")


# ------------------------------------------------------------
# DONUT
# ------------------------------------------------------------

with graf1:

    st.markdown(
        '<div class="lpp-section-title">Distribuição do risco de LPP</div>',
        unsafe_allow_html=True,
    )

    ordem = ["Baixo", "Moderado", "Alto", "Crítico"]

    distribuicao = (
        df_atual["classificacao_lpp_fmt"]
        .value_counts()
        .reindex(ordem, fill_value=0)
        .reset_index()
    )

    distribuicao.columns = ["Nível de risco", "Pacientes"]

    cores_risco = {
        "Baixo": "#7CB342",
        "Moderado": "#F9A825",
        "Alto": "#EF5350",
        "Crítico": "#C62828",
    }

    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=distribuicao["Nível de risco"],
                values=distribuicao["Pacientes"],
                hole=0.62,
                marker=dict(
                    colors=[
                        cores_risco[n]
                        for n in distribuicao["Nível de risco"]
                    ]
                ),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>%{value} paciente(s)<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig_donut.add_annotation(
        x=0.5,
        y=0.53,
        text=f"<b>{total_pacientes}</b>",
        showarrow=False,
        font=dict(
            size=28,
            color="#0D2A45",
        ),
    )

    fig_donut.add_annotation(
        x=0.5,
        y=0.42,
        text="pacientes",
        showarrow=False,
        font=dict(
            size=14,
            color="#6C8597",
        ),
    )

    fig_donut.update_layout(
        title_text="",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.03,
        ),
    )

    tema_plotly(fig_donut, altura=370)

    st.plotly_chart(
        fig_donut,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ------------------------------------------------------------
# BARRAS DE RISCO
# ------------------------------------------------------------

with graf2:

    st.markdown(
        '<div class="lpp-section-title">Score de risco por paciente</div>',
        unsafe_allow_html=True,
    )

    df_barras = (
        df_atual[
            [
                "id_paciente",
                "score_lpp",
                "classificacao_lpp_fmt",
            ]
        ]
        .sort_values(
            "score_lpp",
            ascending=False,
        )
        .head(12)
        .copy()
    )

    df_barras["Paciente"] = (
        "P"
        + df_barras["id_paciente"]
          .astype(int)
          .astype(str)
          .str.zfill(2)
    )

    fig_bar = px.bar(
        df_barras,
        x="Paciente",
        y="score_lpp",
        color="classificacao_lpp_fmt",
        color_discrete_map=cores_risco,
        labels={
            "score_lpp": "Score de risco",
            "classificacao_lpp_fmt": "Risco",
        },
    )

    fig_bar.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Score: %{y:.0f}<extra></extra>",
    )

    fig_bar.update_layout(
        title_text="",
        showlegend=False,
        xaxis_title="Paciente",
        yaxis_title="Score de risco LPP",
    )

    fig_bar.update_yaxes(
        range=[0, 105],
        gridcolor="#E7EEF3",
        zeroline=False,
    )

    fig_bar.update_xaxes(
        showgrid=False,
    )

    tema_plotly(fig_bar, altura=370)

    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# PRIORIDADE + COMPOSIÇÃO DO RISCO
# ============================================================

st.write("")

col_prioridade, col_componentes = st.columns(
    [1.25, 0.95],
    gap="large",
)


# ------------------------------------------------------------
# TABELA DOS PACIENTES PRIORITÁRIOS
# ------------------------------------------------------------

with col_prioridade:

    st.markdown(
        '<div class="lpp-section-title">Pacientes com maior necessidade preventiva</div>',
        unsafe_allow_html=True,
    )

    tabela = (
        df_atual[
            [
                "id_paciente",
                "classificacao_lpp_fmt",
                "score_lpp",
                "tempo_posicao_atual_min",
                "mudancas_posicao_24h",
                "fatores_score_lpp",
            ]
        ]
        .sort_values(
            ["score_lpp", "tempo_posicao_atual_min"],
            ascending=[False, False],
        )
        .head(8)
        .copy()
    )

    tabela["Paciente"] = (
        "P"
        + tabela["id_paciente"]
          .astype(int)
          .astype(str)
          .str.zfill(2)
    )

    tabela["Tempo na posição"] = (
        tabela["tempo_posicao_atual_min"]
        .round(0)
        .astype(int)
        .astype(str)
        + " min"
    )

    tabela["Score LPP"] = (
        tabela["score_lpp"]
        .round(0)
        .astype(int)
    )

    tabela["Mudanças / 24h"] = (
        tabela["mudancas_posicao_24h"]
        .round(0)
        .astype(int)
    )

    tabela["Risco"] = tabela["classificacao_lpp_fmt"]

    tabela_exibir = tabela[
        [
            "Paciente",
            "Risco",
            "Score LPP",
            "Tempo na posição",
            "Mudanças / 24h",
        ]
    ]

    st.dataframe(
        tabela_exibir,
        use_container_width=True,
        hide_index=True,
        height=330,
        column_config={
            "Paciente": st.column_config.TextColumn(
                "Paciente",
                width="small",
            ),
            "Risco": st.column_config.TextColumn(
                "Risco de LPP",
                width="medium",
            ),
            "Score LPP": st.column_config.ProgressColumn(
                "Score LPP",
                min_value=0,
                max_value=100,
                format="%d",
            ),
            "Tempo na posição": st.column_config.TextColumn(
                "Tempo na posição",
            ),
            "Mudanças / 24h": st.column_config.NumberColumn(
                "Mudanças / 24h",
            ),
        },
    )


# ------------------------------------------------------------
# COMPOSIÇÃO DO RISCO
# ------------------------------------------------------------

with col_componentes:

    st.markdown(
        '<div class="lpp-section-title">Composição média do risco</div>',
        unsafe_allow_html=True,
    )

    componentes = pd.DataFrame(
        {
            "Fator": [
                "Tempo",
                "Pressão",
                "Mudanças",
                "Movimento",
                "Imobilidade",
            ],
            "Contribuição": [
                df_atual["score_lpp_tempo"].mean(),
                df_atual["score_lpp_pressao"].mean(),
                df_atual["score_lpp_mudancas"].mean(),
                df_atual["score_lpp_movimento"].mean(),
                df_atual["score_lpp_imobilidade"].mean(),
            ],
        }
    )

    cores_componentes = [
        "#3D8BDB",
        "#8E5BD9",
        "#35B5AD",
        "#F39A38",
        "#5A7D8C",
    ]

    fig_componentes = go.Figure(
        go.Bar(
            x=componentes["Fator"],
            y=componentes["Contribuição"],
            marker_color=cores_componentes,
            text=[
                f"{v:.1f} pts"
                for v in componentes["Contribuição"]
            ],
            textposition="outside",
            cliponaxis=False,
        )
    )

    fig_componentes.update_layout(
        title_text="",
        xaxis_title="",
        yaxis_title="Pontos médios no score",
        showlegend=False,
    )

    fig_componentes.update_yaxes(
        range=[
            0,
            max(
                30,
                componentes["Contribuição"].max() * 1.22,
            ),
        ],
        gridcolor="#E7EEF3",
        zeroline=False,
    )

    fig_componentes.update_xaxes(
        showgrid=False,
    )

    tema_plotly(
        fig_componentes,
        altura=330,
    )

    st.plotly_chart(
        fig_componentes,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# MONITORAMENTO INDIVIDUAL
# ============================================================

st.write("")

st.markdown(
    '<div class="lpp-section-title">Análise preventiva individual</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="lpp-section-subtitle">Selecione um paciente para analisar exclusivamente os fatores associados ao risco de LPP e ao posicionamento.</div>',
    unsafe_allow_html=True,
)


# Opções ordenadas por maior risco atual
ordem_pacientes = (
    df_atual.sort_values(
        "score_lpp",
        ascending=False,
    )["id_paciente"]
    .astype(int)
    .tolist()
)

mapa_opcoes = {}

for pid in ordem_pacientes:

    linha = df_atual[
        df_atual["id_paciente"] == pid
    ].iloc[0]

    nivel = normalizar_nivel(
        linha["classificacao_lpp"]
    )

    mapa_opcoes[
        f"P{pid:02d} · {nivel} · score {linha['score_lpp']:.0f}"
    ] = pid


paciente_label = st.selectbox(
    "Paciente",
    options=list(mapa_opcoes.keys()),
    index=0,
)

paciente_id = mapa_opcoes[paciente_label]

atual = (
    df_atual[
        df_atual["id_paciente"] == paciente_id
    ]
    .iloc[0]
)


# ------------------------------------------------------------
# KPIs INDIVIDUAIS
# ------------------------------------------------------------

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.metric(
        "Tempo na posição atual",
        f"{atual['tempo_posicao_atual_min']:.0f} min",
    )

with p2:
    st.metric(
        "Mudanças de posição / 24h",
        f"{atual['mudancas_posicao_24h']:.0f}",
    )

with p3:
    st.metric(
        "Pressão média do colchão",
        f"{atual['pressao_media_colchao']:.1f}",
    )

with p4:
    st.metric(
        "Índice de movimento",
        f"{atual['indice_movimento'] * 100:.0f}%",
    )


# ============================================================
# HISTÓRICO + FATORES DO PACIENTE
# ============================================================

hist_col, risco_col = st.columns(
    [1.35, 0.85],
    gap="large",
)


# ------------------------------------------------------------
# EVOLUÇÃO DO SCORE
# ------------------------------------------------------------

with hist_col:

    st.markdown(
        '<div class="lpp-section-title">Evolução do score de risco de LPP</div>',
        unsafe_allow_html=True,
    )

    hist = (
        df[
            df["id_paciente"] == paciente_id
        ]
        .sort_values("timestamp_dt")
        .tail(48)
        .copy()
    )

    fig_hist = go.Figure()

    fig_hist.add_trace(
        go.Scatter(
            x=hist["timestamp_dt"],
            y=hist["score_lpp"],
            mode="lines+markers",
            line=dict(
                color="#2B84C5",
                width=3,
            ),
            marker=dict(
                size=6,
                color="#2B84C5",
                line=dict(
                    color="#FFFFFF",
                    width=1,
                ),
            ),
            fill="tozeroy",
            fillcolor="rgba(43,132,197,.10)",
            hovertemplate=(
                "<b>%{x|%d/%m %H:%M}</b>"
                "<br>Risco LPP: %{y:.0f}"
                "<extra></extra>"
            ),
        )
    )

    # Faixas visuais aproximadas para facilitar leitura
    fig_hist.add_hrect(
        y0=0,
        y1=29,
        fillcolor="rgba(124,179,66,.06)",
        line_width=0,
    )

    fig_hist.add_hrect(
        y0=30,
        y1=59,
        fillcolor="rgba(249,168,37,.06)",
        line_width=0,
    )

    fig_hist.add_hrect(
        y0=60,
        y1=79,
        fillcolor="rgba(239,83,80,.05)",
        line_width=0,
    )

    fig_hist.add_hrect(
        y0=80,
        y1=100,
        fillcolor="rgba(198,40,40,.06)",
        line_width=0,
    )

    fig_hist.update_layout(
        title_text="",
        xaxis_title="Horário",
        yaxis_title="Score de risco LPP",
        showlegend=False,
    )

    fig_hist.update_yaxes(
        range=[0, 105],
        gridcolor="#E7EEF3",
        zeroline=False,
    )

    fig_hist.update_xaxes(
        gridcolor="#F0F4F7",
    )

    tema_plotly(
        fig_hist,
        altura=350,
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ------------------------------------------------------------
# FATORES IDENTIFICADOS + RECOMENDAÇÃO
# ------------------------------------------------------------

with risco_col:

    st.markdown(
        '<div class="lpp-section-title">Fatores de risco identificados</div>',
        unsafe_allow_html=True,
    )

    fatores_motor = [
        ("Tempo na posição", atual.get("score_lpp_tempo", 0)),
        ("Pressão no colchão", atual.get("score_lpp_pressao", 0)),
        ("Mudanças de posição", atual.get("score_lpp_mudancas", 0)),
        ("Índice de movimento", atual.get("score_lpp_movimento", 0)),
        ("Imobilidade", atual.get("score_lpp_imobilidade", 0)),
    ]

    fatores_ativos = [
        (nome, float(valor))
        for nome, valor in fatores_motor
        if pd.notna(valor) and float(valor) > 0
    ]

    if fatores_ativos:
        for nome, pontos in sorted(
            fatores_ativos,
            key=lambda item: item[1],
            reverse=True,
        ):
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:12px;
                    padding:10px 2px;
                    border-bottom:1px solid #E7EEF3;
                ">
                    <span style="
                        color:#35576F;
                        font-size:15px;
                        font-weight:650;
                    ">{nome}</span>
                    <span style="
                        color:#B45F06;
                        font-size:14px;
                        font-weight:750;
                    ">+{pontos:.1f} pts</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info(
            "Nenhum componente do motor adicionou pontos ao score de LPP neste registro."
        )

    nivel_atual = str(
        atual["classificacao_lpp"]
    ).lower()

    tempo_atual = float(
        atual["tempo_posicao_atual_min"]
    )

    if (
        nivel_atual in [
            "alto",
            "crítico",
            "critico",
        ]
        or tempo_atual >= 120
    ):

        st.markdown(
            """
            <div class="recommendation">
                <div class="recommendation-title">
                    Recomendação preventiva prioritária
                </div>
                <div class="recommendation-text">
                    O protótipo identifica necessidade de atenção preventiva
                    para LPP. A equipe pode revisar reposicionamento, mobilidade,
                    condições de pressão e os fatores de risco apresentados
                    nesta página.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="recommendation-ok">
                <div class="recommendation-title">
                    Acompanhamento preventivo
                </div>
                <div class="recommendation-text">
                    O risco atual não indica prioridade máxima.
                    Manter o acompanhamento dos fatores de risco,
                    mobilidade e rotina de reposicionamento.
                </div>
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
        "pages/2_Monitoramento_Clinico.py",
        label="Ver monitoramento clínico do paciente",
        use_container_width=True,
    )

with a2:
    st.page_link(
        "pages/5_Central_de_Alertas.py",
        label="Ver Central de Alertas",
        use_container_width=True,
    )


# ============================================================
# AVISO
# ============================================================

st.caption(
    "Protótipo acadêmico com dados simulados. "
    "Os indicadores não substituem avaliação profissional, "
    "protocolos institucionais ou sistemas clínicos validados."
)
