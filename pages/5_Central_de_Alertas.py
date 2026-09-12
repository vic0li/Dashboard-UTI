# ============================================================
# CENTRAL DE ALERTAS
# UTI INTELLIGENT CARE
#
# Integra alertas clínicos e preventivos de LPP para apoiar
# a priorização visual no protótipo acadêmico.
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_data
from utils.styling import aplicar_estilo, topo_produto, navegacao_topo


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Central de Alertas | UTI Intelligent Care",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo()
topo_produto()
navegacao_topo("Alertas")


# ============================================================
# CSS EXCLUSIVO DA PÁGINA
# ============================================================

st.markdown(
    """
    <style>
    .alert-header {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:24px;
        padding:12px 2px 20px 2px;
    }

    .alert-header-left {
        display:flex;
        align-items:center;
        gap:16px;
    }

    .alert-header-icon {
        width:58px;
        height:58px;
        border-radius:18px;
        display:grid;
        place-items:center;
        background:#FFF2EA;
        border:1px solid #F0D7C6;
        color:#D86A32;
        font-size:24px;
        font-weight:850;
    }

    .alert-title {
        color:#0D2A45;
        font-size:34px;
        line-height:1.15;
        font-weight:850;
        letter-spacing:-0.03em;
        margin:0;
    }

    .alert-subtitle {
        color:#667F92;
        font-size:17px;
        line-height:1.5;
        margin-top:6px;
    }

    .alert-info {
        max-width:360px;
        background:#F7FAFC;
        border:1px solid #DCE7EE;
        border-radius:12px;
        padding:12px 15px;
        color:#506C80;
        font-size:14px;
        line-height:1.45;
    }

    .section-title {
        color:#0D2A45;
        font-size:25px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:8px 0 4px 0;
    }

    .section-subtitle {
        color:#738B9C;
        font-size:15px;
        margin-bottom:12px;
    }

    .priority-card {
        border-radius:14px;
        padding:15px 17px;
        border:1px solid #DCE7EE;
        background:#FFFFFF;
        box-shadow:0 3px 12px rgba(23,59,83,.04);
        margin-bottom:10px;
    }

    .priority-critical {
        border-left:5px solid #E5484D;
        background:#FFF8F8;
    }

    .priority-high {
        border-left:5px solid #F09A3E;
        background:#FFF9F2;
    }

    .priority-moderate {
        border-left:5px solid #E6C24A;
        background:#FFFDF4;
    }

    .priority-low {
        border-left:5px solid #159A7A;
        background:#F7FCFA;
    }

    .priority-title {
        color:#16364E;
        font-size:17px;
        font-weight:800;
        margin-bottom:4px;
    }

    .priority-text {
        color:#637D8F;
        font-size:14px;
        line-height:1.45;
    }

    .legend-pill {
        display:inline-block;
        border-radius:999px;
        padding:5px 10px;
        margin-right:6px;
        font-size:13px;
        font-weight:750;
    }

    .pill-critical { background:#FDEAEA; color:#B8383D; }
    .pill-high { background:#FFF0DD; color:#B46A20; }
    .pill-moderate { background:#FFF7D8; color:#8E741C; }
    .pill-low { background:#EAF8F2; color:#24765F; }

    .recommendation {
        background:#F7FAFC;
        border:1px solid #DCE8EF;
        border-radius:12px;
        padding:14px 16px;
        color:#526F83;
        line-height:1.55;
        font-size:15px;
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


def normalizar_bool(valor):
    if pd.isna(valor):
        return False

    if isinstance(valor, bool):
        return valor

    if isinstance(valor, (int, float)):
        return valor != 0

    txt = str(valor).strip().lower()

    return txt in {
        "1", "true", "sim", "yes", "y", "s",
        "alerta", "ativo", "alto", "critico", "crítico"
    }


def nivel_prioridade(row):
    """
    Regra visual acadêmica para ordenar a central.
    Não representa protocolo clínico validado.
    """

    qtd_alertas = int(row.get("quantidade_alertas_calc", 0))
    risco_lpp = str(row.get("nivel_risco_LPP", "")).strip().lower()
    risco_clinico = str(row.get("nivel_risco_clinico", "")).strip().lower()
    tempo_posicao = pd.to_numeric(
        row.get("tempo_posicao_atual_min", 0),
        errors="coerce",
    )

    if pd.isna(tempo_posicao):
        tempo_posicao = 0

    if (
        qtd_alertas >= 3
        or risco_lpp == "muito_alto"
        or risco_clinico in {"muito_alto", "critico", "crítico"}
    ):
        return "Crítica"

    if (
        qtd_alertas == 2
        or risco_lpp == "alto"
        or risco_clinico == "alto"
        or tempo_posicao >= 180
    ):
        return "Alta"

    if (
        qtd_alertas == 1
        or risco_lpp == "moderado"
        or risco_clinico == "moderado"
        or tempo_posicao >= 120
    ):
        return "Moderada"

    return "Baixa"


def prioridade_score(nivel):
    return {
        "Crítica": 4,
        "Alta": 3,
        "Moderada": 2,
        "Baixa": 1,
    }.get(nivel, 0)


def listar_motivos(row):
    motivos = []

    mapa_alertas = [
        ("alerta_fc", "Frequência cardíaca"),
        ("alerta_spo2", "Saturação de O₂"),
        ("alerta_temp", "Temperatura"),
        ("alerta_lactato", "Lactato"),
        ("alerta_hemodinamico", "Instabilidade hemodinâmica"),
        ("alerta_renal", "Função renal"),
    ]

    for coluna, nome in mapa_alertas:
        if coluna in row.index and normalizar_bool(row[coluna]):
            motivos.append(nome)

    risco_lpp = str(row.get("nivel_risco_LPP", "")).strip().lower()

    if risco_lpp in {"alto", "muito_alto"}:
        motivos.append(
            "Risco de LPP " +
            ("muito alto" if risco_lpp == "muito_alto" else "alto")
        )

    tempo = pd.to_numeric(
        row.get("tempo_posicao_atual_min", None),
        errors="coerce",
    )

    if pd.notna(tempo) and tempo >= 120:
        motivos.append("Tempo prolongado na mesma posição")

    if not motivos:
        motivos.append("Sem alerta ativo relevante")

    return motivos


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

try:
    df = load_data().copy()
except Exception as e:
    st.error("Não foi possível carregar os dados.")
    st.exception(e)
    st.stop()

if df.empty:
    st.error("A base de dados está vazia.")
    st.stop()


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

df["timestamp_dt"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
    dayfirst=True,
)

df_atual = (
    df
    .dropna(subset=["timestamp_dt"])
    .sort_values("timestamp_dt")
    .groupby("id_paciente", as_index=False)
    .tail(1)
    .copy()
)

if df_atual.empty:
    st.error("Não foi possível obter o estado atual dos pacientes.")
    st.stop()


# ============================================================
# ALERTAS CLÍNICOS
# ============================================================

colunas_alerta = [
    c for c in [
        "alerta_fc",
        "alerta_spo2",
        "alerta_temp",
        "alerta_lactato",
        "alerta_hemodinamico",
        "alerta_renal",
    ]
    if c in df_atual.columns
]

for coluna in colunas_alerta:
    df_atual[coluna + "_bool"] = df_atual[coluna].apply(normalizar_bool)

bool_cols = [c + "_bool" for c in colunas_alerta]

if bool_cols:
    df_atual["quantidade_alertas_calc"] = (
        df_atual[bool_cols]
        .sum(axis=1)
        .astype(int)
    )
else:
    df_atual["quantidade_alertas_calc"] = 0


# Alerta preventivo de reposicionamento
if "tempo_posicao_atual_min" in df_atual.columns:
    df_atual["alerta_reposicionamento"] = (
        pd.to_numeric(
            df_atual["tempo_posicao_atual_min"],
            errors="coerce",
        )
        >= 120
    )
else:
    df_atual["alerta_reposicionamento"] = False


# Prioridade integrada
df_atual["prioridade"] = df_atual.apply(
    nivel_prioridade,
    axis=1,
)

df_atual["prioridade_score"] = (
    df_atual["prioridade"]
    .map(prioridade_score)
)


# ============================================================
# KPIs
# ============================================================

total_pacientes = df_atual["id_paciente"].nunique()

pacientes_com_alerta = int(
    (
        (df_atual["quantidade_alertas_calc"] > 0)
        | df_atual["alerta_reposicionamento"]
        | df_atual["prioridade"].isin(["Crítica", "Alta"])
    ).sum()
)

alertas_clinicos_ativos = int(
    df_atual["quantidade_alertas_calc"].sum()
)

prioridade_critica = int(
    (df_atual["prioridade"] == "Crítica").sum()
)

reposicionamentos = int(
    df_atual["alerta_reposicionamento"].sum()
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="alert-header">
        <div class="alert-header-left">
            <div class="alert-header-icon">!</div>
            <div>
                <div class="alert-title">Central de Alertas</div>
                <div class="alert-subtitle">
                    Priorização integrada de alertas clínicos,
                    risco de LPP e necessidade de reposicionamento.
                </div>
            </div>
        </div>
        <div class="alert-info">
            <b>Priorização acadêmica</b><br>
            A classificação apresentada combina variáveis simuladas
            e regras conceituais do protótipo, não substituindo
            protocolos assistenciais validados.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPIs PRINCIPAIS
# ============================================================

st.markdown(
    '<div class="section-title">Situação atual</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Visão consolidada do último registro disponível de cada paciente.</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Pacientes com atenção",
        f"{pacientes_com_alerta}",
        help=f"De {total_pacientes} pacientes monitorados.",
    )

with k2:
    st.metric(
        "Alertas clínicos ativos",
        f"{alertas_clinicos_ativos}",
    )

with k3:
    st.metric(
        "Prioridade crítica",
        f"{prioridade_critica}",
    )

with k4:
    st.metric(
        "Reposicionamento",
        f"{reposicionamentos}",
        help="Pacientes com 120 minutos ou mais na posição atual.",
    )


# ============================================================
# DISTRIBUIÇÃO + TIPOS DE ALERTA
# ============================================================

st.write("")

c1, c2 = st.columns(
    [0.78, 1.22],
    gap="large",
)


# ------------------------------------------------------------
# DISTRIBUIÇÃO DE PRIORIDADE
# ------------------------------------------------------------

with c1:

    st.markdown(
        '<div class="section-title">Distribuição por prioridade</div>',
        unsafe_allow_html=True,
    )

    ordem = [
        "Crítica",
        "Alta",
        "Moderada",
        "Baixa",
    ]

    cores_prioridade = {
        "Crítica": "#E5484D",
        "Alta": "#F09A3E",
        "Moderada": "#E1C24F",
        "Baixa": "#159A7A",
    }

    dist = (
        df_atual["prioridade"]
        .value_counts()
        .reindex(ordem, fill_value=0)
        .reset_index()
    )

    dist.columns = [
        "Prioridade",
        "Pacientes",
    ]

    fig_dist = go.Figure(
        data=[
            go.Pie(
                labels=dist["Prioridade"],
                values=dist["Pacientes"],
                hole=0.64,
                marker=dict(
                    colors=[
                        cores_prioridade[p]
                        for p in dist["Prioridade"]
                    ]
                ),
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b>"
                    "<br>%{value} paciente(s)"
                    "<br>%{percent}"
                    "<extra></extra>"
                ),
            )
        ]
    )

    fig_dist.add_annotation(
        x=0.5,
        y=0.55,
        text=f"<b>{total_pacientes}</b>",
        showarrow=False,
        font=dict(
            size=28,
            color="#0D2A45",
        ),
    )

    fig_dist.add_annotation(
        x=0.5,
        y=0.42,
        text="pacientes",
        showarrow=False,
        font=dict(
            size=14,
            color="#718A9B",
        ),
    )

    fig_dist.update_layout(
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
        ),
    )

    tema_plotly(
        fig_dist,
        altura=350,
    )

    st.plotly_chart(
        fig_dist,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ------------------------------------------------------------
# TIPOS DE ALERTA
# ------------------------------------------------------------

with c2:

    st.markdown(
        '<div class="section-title">Alertas mais frequentes</div>',
        unsafe_allow_html=True,
    )

    mapa_nomes = {
        "alerta_fc": "Frequência cardíaca",
        "alerta_spo2": "Saturação de O₂",
        "alerta_temp": "Temperatura",
        "alerta_lactato": "Lactato",
        "alerta_hemodinamico": "Hemodinâmico",
        "alerta_renal": "Renal",
    }

    dados_alerta = []

    for coluna in colunas_alerta:
        dados_alerta.append(
            {
                "Tipo": mapa_nomes[coluna],
                "Quantidade": int(
                    df_atual[coluna + "_bool"].sum()
                ),
            }
        )

    dados_alerta.append(
        {
            "Tipo": "Reposicionamento",
            "Quantidade": reposicionamentos,
        }
    )

    df_tipos = (
        pd.DataFrame(dados_alerta)
        .sort_values(
            "Quantidade",
            ascending=True,
        )
    )

    fig_tipos = px.bar(
        df_tipos,
        x="Quantidade",
        y="Tipo",
        orientation="h",
    )

    fig_tipos.update_traces(
        marker_color="#D97863",
        marker_line_width=0,
        text=df_tipos["Quantidade"],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>%{x} ocorrência(s)"
            "<extra></extra>"
        ),
    )

    fig_tipos.update_layout(
        showlegend=False,
        xaxis_title="Ocorrências",
        yaxis_title="",
    )

    fig_tipos.update_xaxes(
        gridcolor="#E7EEF3",
        zeroline=False,
        dtick=1,
    )

    fig_tipos.update_yaxes(
        showgrid=False,
    )

    tema_plotly(
        fig_tipos,
        altura=350,
    )

    st.plotly_chart(
        fig_tipos,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# FILTROS
# ============================================================

st.write("")

st.markdown(
    '<div class="section-title">Fila de priorização</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Pacientes ordenados pela prioridade conceitual calculada no protótipo.</div>',
    unsafe_allow_html=True,
)

f1, f2 = st.columns(
    [0.7, 1.3],
)

with f1:
    filtro_prioridade = st.multiselect(
        "Prioridade",
        options=[
            "Crítica",
            "Alta",
            "Moderada",
            "Baixa",
        ],
        default=[
            "Crítica",
            "Alta",
            "Moderada",
        ],
    )

with f2:
    somente_alertas = st.toggle(
        "Mostrar somente pacientes com algum alerta ativo",
        value=True,
    )


df_fila = df_atual.copy()

if filtro_prioridade:
    df_fila = df_fila[
        df_fila["prioridade"].isin(
            filtro_prioridade
        )
    ]

if somente_alertas:
    df_fila = df_fila[
        (df_fila["quantidade_alertas_calc"] > 0)
        | df_fila["alerta_reposicionamento"]
        | df_fila["prioridade"].isin(["Crítica", "Alta"])
    ]

df_fila = df_fila.sort_values(
    [
        "prioridade_score",
        "quantidade_alertas_calc",
        "risco_LPP"
        if "risco_LPP" in df_fila.columns
        else "id_paciente",
    ],
    ascending=[
        False,
        False,
        False,
    ],
)


# ============================================================
# TABELA DE PRIORIZAÇÃO
# ============================================================

tabela = pd.DataFrame()

tabela["Paciente"] = (
    "Paciente " +
    df_fila["id_paciente"].astype(str)
)

tabela["Prioridade"] = df_fila["prioridade"]

tabela["Alertas clínicos"] = (
    df_fila["quantidade_alertas_calc"]
)

if "nivel_risco_clinico" in df_fila.columns:
    tabela["Risco clínico"] = (
        df_fila["nivel_risco_clinico"]
        .astype(str)
        .str.replace("_", " ")
        .str.title()
    )

if "nivel_risco_LPP" in df_fila.columns:
    tabela["Risco LPP"] = (
        df_fila["nivel_risco_LPP"]
        .astype(str)
        .str.replace("_", " ")
        .str.title()
    )

if "tempo_posicao_atual_min" in df_fila.columns:
    tabela["Tempo na posição"] = (
        pd.to_numeric(
            df_fila["tempo_posicao_atual_min"],
            errors="coerce",
        )
        .round(0)
        .astype("Int64")
        .astype(str)
        + " min"
    )

st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True,
    height=min(
        480,
        45 + len(tabela) * 38,
    ),
)


# ============================================================
# DETALHE DO PACIENTE
# ============================================================

st.write("")

st.markdown(
    '<div class="section-title">Detalhamento da prioridade</div>',
    unsafe_allow_html=True,
)

ids_disponiveis = (
    df_atual
    .sort_values(
        [
            "prioridade_score",
            "quantidade_alertas_calc",
        ],
        ascending=False,
    )["id_paciente"]
    .tolist()
)

paciente_escolhido = st.selectbox(
    "Selecione o paciente",
    options=ids_disponiveis,
    format_func=lambda x: f"Paciente {x}",
)

registro = (
    df_atual[
        df_atual["id_paciente"] == paciente_escolhido
    ]
    .iloc[0]
)

motivos = listar_motivos(registro)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Prioridade",
        registro["prioridade"],
    )

with m2:
    st.metric(
        "Alertas clínicos",
        int(registro["quantidade_alertas_calc"]),
    )

with m3:
    if "score_risco_clinico" in registro.index:
        valor = pd.to_numeric(
            registro["score_risco_clinico"],
            errors="coerce",
        )

        st.metric(
            "Score clínico",
            f"{valor:.0f}" if pd.notna(valor) else "N/D",
        )
    else:
        st.metric(
            "Score clínico",
            "N/D",
        )

with m4:
    if "risco_LPP" in registro.index:
        valor = pd.to_numeric(
            registro["risco_LPP"],
            errors="coerce",
        )

        st.metric(
            "Score LPP",
            f"{valor:.0f}" if pd.notna(valor) else "N/D",
        )
    else:
        st.metric(
            "Score LPP",
            "N/D",
        )


# ============================================================
# MOTIVOS DO ALERTA
# ============================================================

st.markdown(
    '<div class="section-subtitle" style="margin-top:16px;"><b>Motivos identificados</b></div>',
    unsafe_allow_html=True,
)

for motivo in motivos:
    st.markdown(
        f"""
        <div class="priority-card">
            <div class="priority-title">{motivo}</div>
            <div class="priority-text">
                Evento identificado a partir do registro mais recente
                disponível na base simulada.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RESUMO DOS FATORES DE ATENÇÃO
# ============================================================

st.write("")

st.markdown(
    '<div class="section-title">Resumo dos fatores de atenção</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-subtitle">
        Síntese dos elementos que sustentam a prioridade atual do paciente.
        O acompanhamento temporal detalhado permanece na página de Monitoramento.
    </div>
    """,
    unsafe_allow_html=True,
)

resumo_fatores = []

if int(registro["quantidade_alertas_calc"]) > 0:
    resumo_fatores.append(
        f"{int(registro['quantidade_alertas_calc'])} alerta(s) clínico(s) ativo(s)"
    )

if "nivel_risco_clinico" in registro.index:
    valor = str(registro["nivel_risco_clinico"]).replace("_", " ").strip().title()
    if valor and valor.lower() != "nan":
        resumo_fatores.append(f"Risco clínico: {valor}")

if "nivel_risco_LPP" in registro.index:
    valor = str(registro["nivel_risco_LPP"]).replace("_", " ").strip().title()
    if valor and valor.lower() != "nan":
        resumo_fatores.append(f"Risco de LPP: {valor}")

if "tempo_posicao_atual_min" in registro.index:
    valor = pd.to_numeric(
        registro["tempo_posicao_atual_min"],
        errors="coerce",
    )
    if pd.notna(valor) and valor >= 120:
        resumo_fatores.append(
            f"Tempo na posição atual: {valor:.0f} min"
        )

if resumo_fatores:
    for fator in resumo_fatores:
        st.markdown(
            f"""
            <div class="priority-card">
                <div class="priority-title">{fator}</div>
                <div class="priority-text">
                    Fator considerado na priorização conceitual do protótipo.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info(
        "Não foram identificados fatores adicionais de atenção "
        "no registro atual."
    )


# ============================================================
# ORIENTAÇÃO CONCEITUAL
# ============================================================

st.write("")

st.markdown(
    '<div class="section-title">Orientação de priorização</div>',
    unsafe_allow_html=True,
)

prioridade = registro["prioridade"]

if prioridade == "Crítica":
    texto = (
        "O paciente apresenta combinação de fatores classificada como "
        "prioridade crítica pelo protótipo. Recomenda-se destacar o caso "
        "na fila de avaliação e verificar os fatores responsáveis pelos "
        "alertas ativos."
    )
elif prioridade == "Alta":
    texto = (
        "O paciente apresenta fatores que justificam atenção prioritária. "
        "A equipe pode revisar os alertas ativos, a tendência clínica e "
        "as medidas preventivas de LPP."
    )
elif prioridade == "Moderada":
    texto = (
        "O paciente apresenta sinais que merecem acompanhamento. "
        "A central mantém o caso visível para favorecer intervenção "
        "preventiva antes de uma possível piora."
    )
else:
    texto = (
        "No registro atual, o paciente apresenta baixa prioridade "
        "na regra conceitual utilizada pelo protótipo, permanecendo "
        "em monitoramento."
    )

st.markdown(
    f"""
    <div class="recommendation">
        {texto}
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
        label="Abrir Monitoramento Clínico",
        use_container_width=True,
    )

with a2:
    st.page_link(
        "pages/3_Gestao_LPP.py",
        label="Abrir Gestão de LPP",
        use_container_width=True,
    )


# ============================================================
# LEGENDA E AVISO
# ============================================================

st.write("")

st.markdown(
    """
    <div>
        <span class="legend-pill pill-critical">Crítica</span>
        <span class="legend-pill pill-high">Alta</span>
        <span class="legend-pill pill-moderate">Moderada</span>
        <span class="legend-pill pill-low">Baixa</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Protótipo acadêmico com dados simulados. A classificação de prioridade "
    "é uma regra conceitual desenvolvida para demonstrar a integração de alertas "
    "e não substitui julgamento clínico, protocolos institucionais ou sistemas "
    "de apoio à decisão validados."
)
