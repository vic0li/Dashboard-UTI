# ============================================================
# APP PRINCIPAL
# UTI INTELLIGENT CARE
#
# Home / landing page do protótipo acadêmico.
# A análise detalhada fica distribuída nas páginas especializadas.
# ============================================================

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.data_loader import load_data
from utils.analytics import processar_dados
from utils.risk_engine import processar_riscos
from utils.styling import aplicar_estilo, topo_produto, navegacao_topo, hero_home


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="UTI Intelligent Care",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# ESTILO E NAVEGAÇÃO
# ============================================================

aplicar_estilo()
topo_produto()
navegacao_topo("Início")
hero_home()


# ============================================================
# CSS EXCLUSIVO DA HOME
# ============================================================

st.markdown(
    """
    <style>
    .home-section-title {
        color:#0D2A45;
        font-size:27px;
        font-weight:850;
        letter-spacing:-0.02em;
        margin:12px 0 4px 0;
    }

    .home-section-subtitle {
        color:#6F8798;
        font-size:16px;
        line-height:1.5;
        margin-bottom:15px;
    }

    .home-summary-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:16px;
        padding:20px 22px;
        min-height:150px;
        box-shadow:0 5px 18px rgba(21,61,89,.045);
    }

    .home-summary-kicker {
        color:#6F8798;
        font-size:14px;
        font-weight:750;
        text-transform:uppercase;
        letter-spacing:.05em;
        margin-bottom:8px;
    }

    .home-summary-title {
        color:#0D2A45;
        font-size:21px;
        font-weight:850;
        margin-bottom:8px;
    }

    .home-summary-text {
        color:#587287;
        font-size:15px;
        line-height:1.55;
    }

    .home-status-row {
        display:flex;
        align-items:center;
        gap:10px;
        margin-top:13px;
        color:#49677C;
        font-size:14px;
        font-weight:650;
    }

    .home-dot {
        width:10px;
        height:10px;
        border-radius:50%;
        display:inline-block;
        flex-shrink:0;
    }

    .home-dot-green { background:#159A7A; }
    .home-dot-orange { background:#F4A62A; }
    .home-dot-red { background:#E5484D; }
    .home-dot-blue { background:#1F6EA5; }

    .home-area-card {
        background:#FFFFFF;
        border:1px solid #D8E4EC;
        border-radius:16px;
        padding:19px 20px 17px 20px;
        min-height:142px;
        box-shadow:0 4px 14px rgba(21,61,89,.035);
        margin-bottom:8px;
    }

    .home-area-number {
        color:#1F6EA5;
        font-size:13px;
        font-weight:800;
        letter-spacing:.06em;
        text-transform:uppercase;
        margin-bottom:7px;
    }

    .home-area-title {
        color:#0D2A45;
        font-size:20px;
        font-weight:850;
        margin-bottom:7px;
    }

    .home-area-text {
        color:#667F92;
        font-size:14px;
        line-height:1.5;
    }

    .home-about {
        background:#F6FAFC;
        border:1px solid #DCE8EF;
        border-radius:15px;
        padding:17px 20px;
        color:#567186;
        font-size:15px;
        line-height:1.55;
        margin-top:8px;
    }

    .home-about strong {
        color:#173E59;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CARREGAMENTO DOS DADOS CLÍNICOS
# ============================================================

try:
    df = load_data().copy()
except Exception as e:
    st.error("Não foi possível carregar os dados clínicos.")
    st.exception(e)
    st.stop()

if df.empty:
    st.error(
        "A base clínica está vazia. Verifique o arquivo "
        "`data/uti_simulada.csv`."
    )
    st.stop()


# ============================================================
# PROCESSAMENTO ANALÍTICO
# ============================================================

try:
    df = processar_dados(df)
except Exception:
    # A Home continua funcional mesmo se parte das variáveis
    # derivadas não puder ser processada.
    pass

try:
    df = processar_riscos(df)
except Exception:
    pass


# ============================================================
# PREPARAÇÃO TEMPORAL
# ============================================================

if "timestamp" in df.columns:
    df["timestamp_dt"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        dayfirst=True,
    )
else:
    df["timestamp_dt"] = pd.NaT


if (
    "id_paciente" in df.columns
    and df["timestamp_dt"].notna().any()
):
    df_pacientes = (
        df
        .dropna(subset=["timestamp_dt"])
        .sort_values("timestamp_dt")
        .groupby("id_paciente", as_index=False)
        .tail(1)
        .copy()
    )
elif "id_paciente" in df.columns:
    df_pacientes = (
        df
        .drop_duplicates(
            subset="id_paciente",
            keep="last",
        )
        .copy()
    )
else:
    df_pacientes = df.copy()


# ============================================================
# BASE OPERACIONAL - OPCIONAL NA HOME
# ============================================================

def carregar_ocupacao_operacional():
    raiz = Path(__file__).resolve().parent

    candidatos = [
        raiz / "data" / "UTI_operacional.csv",
        raiz / "data" / "uti_operacional.csv",
    ]

    for caminho in candidatos:
        if caminho.exists():
            try:
                op = pd.read_csv(
                    caminho,
                    sep=";",
                    encoding="utf-8-sig",
                )

                if op.empty:
                    return None

                if "timestamp" in op.columns:
                    op["_timestamp"] = pd.to_datetime(
                        op["timestamp"],
                        errors="coerce",
                        dayfirst=True,
                    )
                    op = op.sort_values("_timestamp")

                if "taxa_ocupacao_pct" in op.columns:
                    valor = pd.to_numeric(
                        op.iloc[-1]["taxa_ocupacao_pct"],
                        errors="coerce",
                    )

                    if pd.notna(valor):
                        return float(valor)

            except Exception:
                return None

    return None


ocupacao_atual = carregar_ocupacao_operacional()


# ============================================================
# INDICADORES DA HOME
# ============================================================

total_pacientes = (
    int(df_pacientes["id_paciente"].nunique())
    if "id_paciente" in df_pacientes.columns
    else len(df_pacientes)
)


if "quantidade_alertas" in df_pacientes.columns:
    alertas_ativos = int(
        pd.to_numeric(
            df_pacientes["quantidade_alertas"],
            errors="coerce",
        )
        .fillna(0)
        .sum()
    )
else:
    colunas_alerta = [
        coluna
        for coluna in [
            "alerta_fc",
            "alerta_spo2",
            "alerta_temp",
            "alerta_lactato",
            "alerta_hemodinamico",
            "alerta_renal",
        ]
        if coluna in df_pacientes.columns
    ]

    alertas_ativos = 0

    for coluna in colunas_alerta:
        serie = (
            df_pacientes[coluna]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        alertas_ativos += int(
            serie.isin(
                [
                    "1",
                    "true",
                    "sim",
                    "yes",
                    "alerta",
                    "ativo",
                ]
            ).sum()
        )


# Prioridade elevada - fonte oficial: motor de risco
if "classificacao_prioridade" in df_pacientes.columns:
    serie_prioridade = (
        df_pacientes["classificacao_prioridade"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    prioritarios = int(
        serie_prioridade.isin(["alta", "crítica", "critica"]).sum()
    )
else:
    prioritarios = 0


# Risco de LPP elevado - fonte oficial: motor de risco
lpp_elevado = 0

if "classificacao_lpp" in df_pacientes.columns:
    serie_lpp = (
        df_pacientes["classificacao_lpp"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    lpp_elevado = int(
        serie_lpp.isin(["alto", "crítico", "critico"]).sum()
    )


# ============================================================
# VISÃO RÁPIDA
# ============================================================

st.markdown(
    '<div class="home-section-title">Visão rápida da UTI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-section-subtitle">
        Indicadores essenciais do registro mais recente. As análises
        completas estão disponíveis nas páginas especializadas.
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Pacientes monitorados",
        total_pacientes,
    )

with m2:
    st.metric(
        "Alertas ativos",
        alertas_ativos,
    )

with m3:
    st.metric(
        "Alta prioridade",
        prioritarios,
    )

with m4:
    st.metric(
        "Ocupação da UTI",
        (
            f"{ocupacao_atual:.1f}%"
            if ocupacao_atual is not None
            else "N/D"
        ),
        help=(
            "Indicador proveniente da base operacional simulada."
            if ocupacao_atual is not None
            else "A base operacional não foi encontrada."
        ),
    )


# ============================================================
# RESUMO DO ESTADO ATUAL
# ============================================================

st.write("")

st.markdown(
    '<div class="home-section-title">Estado atual</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-section-subtitle">
        Leitura resumida das três dimensões principais do protótipo.
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3, gap="large")


# ------------------------------------------------------------
# CLÍNICO
# ------------------------------------------------------------

with c1:

    if prioritarios > 0:
        classe_dot = "home-dot-orange"
        status_clinico = (
            f"{prioritarios} paciente(s) em prioridade elevada"
        )
    else:
        classe_dot = "home-dot-green"
        status_clinico = "Sem prioridade elevada identificada"

    st.markdown(
        f"""
        <div class="home-summary-card">
            <div class="home-summary-kicker">Clínico</div>
            <div class="home-summary-title">Monitoramento assistencial</div>
            <div class="home-summary-text">
                Acompanhe sinais vitais, exames laboratoriais,
                score clínico e tendências individuais dos pacientes.
            </div>
            <div class="home-status-row">
                <span class="home-dot {classe_dot}"></span>
                {status_clinico}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# LPP
# ------------------------------------------------------------

with c2:

    if lpp_elevado > 0:
        classe_dot = "home-dot-orange"
        status_lpp = (
            f"{lpp_elevado} paciente(s) com risco alto ou muito alto"
        )
    else:
        classe_dot = "home-dot-green"
        status_lpp = "Sem pacientes em risco elevado"

    st.markdown(
        f"""
        <div class="home-summary-card">
            <div class="home-summary-kicker">Prevenção</div>
            <div class="home-summary-title">Risco de LPP</div>
            <div class="home-summary-text">
                Priorize pacientes com maior risco, tempo prolongado
                na posição e fatores preventivos relevantes.
            </div>
            <div class="home-status-row">
                <span class="home-dot {classe_dot}"></span>
                {status_lpp}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# OPERACIONAL
# ------------------------------------------------------------

with c3:

    if ocupacao_atual is None:
        classe_dot = "home-dot-blue"
        status_op = "Indicador operacional indisponível"
    elif ocupacao_atual >= 90:
        classe_dot = "home-dot-red"
        status_op = f"Ocupação elevada: {ocupacao_atual:.1f}%"
    else:
        classe_dot = "home-dot-green"
        status_op = f"Ocupação atual: {ocupacao_atual:.1f}%"

    st.markdown(
        f"""
        <div class="home-summary-card">
            <div class="home-summary-kicker">Operacional</div>
            <div class="home-summary-title">Capacidade e fluxo</div>
            <div class="home-summary-text">
                Visualize ocupação, permanência, carga assistencial,
                disponibilidade de leitos e movimentação da UTI.
            </div>
            <div class="home-status-row">
                <span class="home-dot {classe_dot}"></span>
                {status_op}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ÁREAS DO SISTEMA
# ============================================================

st.write("")

st.markdown(
    '<div class="home-section-title">Áreas do sistema</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-section-subtitle">
        Cada página possui uma finalidade específica para evitar
        sobreposição de informações.
    </div>
    """,
    unsafe_allow_html=True,
)


a1, a2, a3 = st.columns(3, gap="large")

with a1:
    st.markdown(
        """
        <div class="home-area-card">
            <div class="home-area-number">01 · Visão geral</div>
            <div class="home-area-title">Panorama da UTI</div>
            <div class="home-area-text">
                Síntese executiva dos principais indicadores clínicos,
                preventivos e operacionais.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/1_Dashboard_Geral.py",
        label="Abrir Visão geral",
        use_container_width=True,
    )

with a2:
    st.markdown(
        """
        <div class="home-area-card">
            <div class="home-area-number">02 · Monitoramento</div>
            <div class="home-area-title">Paciente individual</div>
            <div class="home-area-text">
                Evolução de sinais vitais, exames e tendências clínicas
                do paciente selecionado.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/2_Monitoramento_Clinico.py",
        label="Abrir Monitoramento",
        use_container_width=True,
    )

with a3:
    st.markdown(
        """
        <div class="home-area-card">
            <div class="home-area-number">03 · LPP</div>
            <div class="home-area-title">Prevenção de lesão por pressão</div>
            <div class="home-area-text">
                Risco de LPP, fatores associados, posicionamento e
                priorização preventiva.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/3_Gestao_LPP.py",
        label="Abrir Gestão de LPP",
        use_container_width=True,
    )


st.write("")

a4, a5, a6 = st.columns(3, gap="large")

with a4:
    st.markdown(
        """
        <div class="home-area-card">
            <div class="home-area-number">04 · Operacional</div>
            <div class="home-area-title">Capacidade da UTI</div>
            <div class="home-area-text">
                Ocupação, leitos, fluxo, permanência e carga assistencial
                por turno.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/4_Gestao_Operacional.py",
        label="Abrir Operacional",
        use_container_width=True,
    )

with a5:
    st.markdown(
        """
        <div class="home-area-card">
            <div class="home-area-number">05 · Alertas</div>
            <div class="home-area-title">Central de priorização</div>
            <div class="home-area-text">
                Identifique rapidamente quais pacientes precisam de
                atenção e os motivos associados.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/5_Central_de_Alertas.py",
        label="Abrir Central de Alertas",
        use_container_width=True,
    )

with a6:
    st.markdown(
        """
        <div class="home-area-card">
            <div class="home-area-number">06 · Lean</div>
            <div class="home-area-title">Melhoria de processos</div>
            <div class="home-area-text">
                Conecte os indicadores do dashboard aos conceitos de
                Lean Healthcare e melhoria contínua.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/7_Lean_Healthcare.py",
        label="Abrir Lean Healthcare",
        use_container_width=True,
    )


# ============================================================
# SOBRE O PROTÓTIPO
# ============================================================

st.write("")

st.markdown(
    '<div class="home-section-title">Sobre o protótipo</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-about">
        <strong>UTI Intelligent Care</strong> é um protótipo acadêmico
        desenvolvido para demonstrar a integração entre dados clínicos,
        risco de Lesão por Pressão, alertas e indicadores operacionais
        em uma única solução de apoio à gestão da UTI.
        <br><br>
        Os dados utilizados são <strong>simulados</strong>. Os scores,
        regras e alertas possuem finalidade conceitual e educacional e
        não substituem avaliação profissional, protocolos institucionais
        ou sistemas clínicos validados.
    </div>
    """,
    unsafe_allow_html=True,
)
