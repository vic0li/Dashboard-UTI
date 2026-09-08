# ============================================================
# APP PRINCIPAL
# UTI INTELLIGENT CARE
#
# Protótipo acadêmico para monitoramento inteligente
# de risco clínico e operacional em UTI
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.analytics import processar_dados
from utils.risk_engine import processar_riscos
from utils.styling import aplicar_estilo

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Gestão da UTI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILO
# ============================================================

aplicar_estilo()

# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

try:
    df = load_data()
except Exception as e:
    st.error("❌ Não foi possível carregar os dados.")
    st.exception(e)
    st.stop()

# ============================================================
# VALIDAÇÃO DA BASE
# ============================================================

if df.empty:
    st.error(
        """
        ❌ Não foi possível carregar os dados da UTI.

        Verifique se o arquivo:
        `data/uti_simulada.csv`
        está corretamente localizado.
        """
    )
    st.stop()

# ============================================================
# PROCESSAMENTO ANALÍTICO
# ============================================================

try:
    df = processar_dados(df)
except Exception as e:
    st.error("❌ Erro no processamento dos dados.")
    st.exception(e)
    st.stop()

# ============================================================
# MOTOR DE RISCO
# ============================================================

try:
    df = processar_riscos(df)
except Exception as e:
    st.error("❌ Erro no motor de risco.")
    st.exception(e)
    st.stop()

# ============================================================
# PREPARAÇÃO TEMPORAL DOS DADOS
# ============================================================

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ============================================================
# DATAFRAME DE PACIENTES ATUAIS
# ============================================================

if "id_paciente" in df.columns and "timestamp" in df.columns:
    df_pacientes = (
        df.sort_values("timestamp")
        .groupby("id_paciente", as_index=False)
        .tail(1)
        .copy()
    )
elif "id_paciente" in df.columns:
    df_pacientes = df.drop_duplicates(subset="id_paciente", keep="last").copy()
else:
    df_pacientes = df.copy()

# ============================================================
# HEADER / HERO SECTION (Layout refinado)
# ============================================================

st.title("🏥 UTI Intelligent Care")
st.caption("🛡️ ICU Sentinel · Monitoramento Preditivo e Inteligência Operacional")

st.markdown(
    """
    <div style="background-color: #f0f2f6; padding: 16px; border-radius: 8px; border-left: 5px solid #1f77b4; margin-bottom: 20px;">
        <p style="margin: 0; font-size: 15px; color: #31333F;">
            <b>Visão Geral do Sistema:</b> Protótipo de dashboard preditivo para gestão de risco clínico e operacional em Unidade de Terapia Intensiva, integrando dados simulados e princípios de <i>Lean Healthcare</i>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# PILARES DO SISTEMA
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.info("🧠 **Risco de LPP**\n\nEscore ponderado para prevenção de lesão por pressão.")

with col2:
    st.info("📈 **Tendência Clínica**\n\nMonitoramento de deterioração precoce e escores.")

with col3:
    st.info("🏥 **Gestão Operacional**\n\nIntegração entre risco, pacientes e eficiência.")

st.markdown("---")

# ============================================================
# VISÃO GERAL & MÉTRICAS
# ============================================================

st.subheader("📊 Indicadores Atuais da UTI")
st.caption("Os indicadores abaixo representam a situação mais recente disponível de cada paciente monitorado.")

total_pacientes = (
    df_pacientes["id_paciente"].nunique()
    if "id_paciente" in df_pacientes.columns
    else len(df_pacientes)
)

total_alertas_val = int(df_pacientes["quantidade_alertas"].sum()) if "quantidade_alertas" in df_pacientes.columns else 0
spo2_media = f"{df_pacientes['saturacao_O2'].mean():.1f}%" if "saturacao_O2" in df_pacientes.columns else "N/D"
fc_media = f"{df_pacientes['frequencia_cardiaca'].mean():.1f}" if "frequencia_cardiaca" in df_pacientes.columns else "N/D"
temp_media = f"{df_pacientes['temperatura'].mean():.1f}°C" if "temperatura" in df_pacientes.columns else "N/D"

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("👥 Pacientes", total_pacientes)
with m2:
    st.metric("⚠️ Alertas Atuais", total_alertas_val)
with m3:
    st.metric("⭕ SpO₂ Média", spo2_media)
with m4:
    st.metric("💓 FC Média", fc_media)
with m5:
    st.metric("🌡️ Temp. Média", temp_media)

# ============================================================
# MOTOR ANALÍTICO
# ============================================================

st.markdown("---")
st.header("🧠 Motor Analítico")
st.caption("Scores médios calculados utilizando o último registro disponível de cada paciente.")

c1, c2, c3, c4 = st.columns(4)

with c1:
    score_clinico_medio = df_pacientes["score_clinico"].mean() if "score_clinico" in df_pacientes.columns else 0
    st.metric("Score Clínico Médio", f"{score_clinico_medio:.1f}")

with c2:
    score_lpp_medio = df_pacientes["score_lpp"].mean() if "score_lpp" in df_pacientes.columns else 0
    st.metric("Score LPP Médio", f"{score_lpp_medio:.1f}")

with c3:
    st.metric("Alertas Atuais", total_alertas_val)

with c4:
    prioridade_media = df_pacientes["indice_prioridade"].mean() if "indice_prioridade" in df_pacientes.columns else 0
    st.metric("Prioridade Média", f"{prioridade_media:.1f}")

# ============================================================
# SEÇÃO DE MOTIVO DE INTERNAÇÃO (DIAGNÓSTICO PRINCIPAL)
# ============================================================

st.markdown("---")
st.header(" Motivo de Internação")
st.caption("Distribuição dos principais motivos e diagnósticos que motivaram a admissão dos pacientes na UTI.")

col_diag1, col_diag2 = st.columns([1.2, 1])

with col_diag1:
    if "diagnostico_principal" in df_pacientes.columns:
        df_diag = df_pacientes["diagnostico_principal"].value_counts().reset_index()
        df_diag.columns = ["Diagnóstico / Motivo", "Total de Pacientes"]
        st.dataframe(df_diag, use_container_width=True, hide_index=True)
    elif "diagnostico_principal" in df.columns:
        df_diag = df.drop_duplicates(subset="id_paciente", keep="last")["diagnostico_principal"].value_counts().reset_index()
        df_diag.columns = ["Diagnóstico / Motivo", "Total de Pacientes"]
        st.dataframe(df_diag, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Coluna `diagnostico_principal` não encontrada na base de dados.")

with col_diag2:
    if "diagnostico_principal" in df_pacientes.columns:
        fig_diag = px.pie(
            df_pacientes, 
            names="diagnostico_principal", 
            title="Proporção por Motivo de Internação",
            hole=0.4
        )
        fig_diag.update_layout(height=350, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_diag, use_container_width=True)
    else:
        st.info("Gráfico indisponível sem a coluna de diagnóstico.")

# ============================================================
# ETAPA 7.6 - VALIDAÇÃO DO MOTOR ANALÍTICO
# ============================================================

st.markdown("---")
st.header(" Validação do Motor Analítico")
st.write(
    """
    Esta seção verifica se as variáveis derivadas foram criadas
    corretamente e permite validar o comportamento dos scores,
    classificações, alertas e índices de prioridade.
    """
)

# 1. VERIFICAÇÃO DAS VARIÁVEIS
st.subheader(" Verificação das Variáveis Geradas")

colunas_motor = [
    "score_clinico",
    "classificacao_clinica",
    "score_lpp",
    "classificacao_lpp",
    "quantidade_alertas",
    "indice_prioridade",
    "classificacao_prioridade",
    "diagnostico_principal"
]

colunas_encontradas = 0
for coluna in colunas_motor:
    if coluna in df.columns:
        st.success(f"✅ `{coluna}` criada/presente com sucesso")
        colunas_encontradas += 1
    else:
        st.warning(f"⚠️ `{coluna}` não encontrada")

# 2. ESTATÍSTICAS DOS SCORES
st.markdown("---")
st.subheader(" Estatísticas dos Scores")
st.caption("Estatísticas calculadas sobre a situação atual de cada paciente.")

s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("#####  Score Clínico")
    if "score_clinico" in df_pacientes.columns:
        st.metric("Mínimo", f"{df_pacientes['score_clinico'].min():.1f}")
        st.metric("Máximo", f"{df_pacientes['score_clinico'].max():.1f}")
        st.metric("Média", f"{df_pacientes['score_clinico'].mean():.1f}")
    else:
        st.warning("N/D")

with s2:
    st.markdown("#####  Score LPP")
    if "score_lpp" in df_pacientes.columns:
        st.metric("Mínimo", f"{df_pacientes['score_lpp'].min():.1f}")
        st.metric("Máximo", f"{df_pacientes['score_lpp'].max():.1f}")
        st.metric("Média", f"{df_pacientes['score_lpp'].mean():.1f}")
    else:
        st.warning("N/D")

with s3:
    st.markdown("##### 🔥 Índice de Prioridade")
    if "indice_prioridade" in df_pacientes.columns:
        st.metric("Mínimo", f"{df_pacientes['indice_prioridade'].min():.1f}")
        st.metric("Máximo", f"{df_pacientes['indice_prioridade'].max():.1f}")
        st.metric("Média", f"{df_pacientes['indice_prioridade'].mean():.1f}")
    else:
        st.warning("N/D")

# 3. DISTRIBUIÇÃO DAS CLASSIFICAÇÕES
st.markdown("---")
st.subheader(" Distribuição Atual dos Pacientes")
st.caption("Cada paciente é contabilizado apenas uma vez, utilizando seu registro mais recente.")

d1, d2, d3 = st.columns(3)

with d1:
    st.markdown("##### 🩺 Situação Clínica")
    if "classificacao_clinica" in df_pacientes.columns:
        dist_clinica = df_pacientes["classificacao_clinica"].value_counts().reset_index()
        dist_clinica.columns = ["Classificação", "Pacientes"]
        st.dataframe(dist_clinica, use_container_width=True, hide_index=True)
    else:
        st.warning("N/D")

with d2:
    st.markdown("##### 🩹 Risco de LPP")
    if "classificacao_lpp" in df_pacientes.columns:
        dist_lpp = df_pacientes["classificacao_lpp"].value_counts().reset_index()
        dist_lpp.columns = ["Classificação", "Pacientes"]
        st.dataframe(dist_lpp, use_container_width=True, hide_index=True)
    else:
        st.warning("N/D")

with d3:
    st.markdown("##### 🔥 Prioridade")
    if "classificacao_prioridade" in df_pacientes.columns:
        dist_prio = df_pacientes["classificacao_prioridade"].value_counts().reset_index()
        dist_prio.columns = ["Classificação", "Pacientes"]
        st.dataframe(dist_prio, use_container_width=True, hide_index=True)
    else:
        st.warning("N/D")

# 4. VERIFICAÇÃO DE DADOS NULOS
st.markdown("---")
st.subheader(" Verificação de Dados Nulos")

colunas_validacao = [
    "score_clinico",
    "score_lpp",
    "quantidade_alertas",
    "indice_prioridade",
    "diagnostico_principal"
]

for coluna in colunas_validacao:
    if coluna in df.columns:
        qtd_nulos = df[coluna].isnull().sum()
        if qtd_nulos == 0:
            st.success(f"✅ `{coluna}`: nenhum valor nulo")
        else:
            st.warning(f"⚠️ `{coluna}`: {qtd_nulos} valores nulos")

# 5. AUDITORIA DOS RESULTADOS
st.markdown("---")
st.subheader(" Auditoria dos Resultados")
st.caption("Visualização dos dados de entrada e das variáveis geradas pelo motor analítico.")

colunas_auditoria = [
    "id_paciente", "timestamp", "diagnostico_principal",
    "frequencia_cardiaca", "saturacao_O2", "temperatura", "lactato",
    "score_clinico", "classificacao_clinica",
    "score_lpp", "classificacao_lpp",
    "quantidade_alertas",
    "indice_prioridade", "classificacao_prioridade"
]

colunas_existentes = [coluna for coluna in colunas_auditoria if coluna in df_pacientes.columns]

if colunas_existentes:
    df_auditoria = df_pacientes[colunas_existentes].copy()
    if "indice_prioridade" in df_auditoria.columns:
        df_auditoria = df_auditoria.sort_values("indice_prioridade", ascending=False)
    st.dataframe(df_auditoria.head(20), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhuma coluna disponível para auditoria.")

# 6. PACIENTES COM MAIOR PRIORIDADE
st.markdown("---")
st.subheader(" Pacientes com Maior Prioridade")
st.caption("Cada paciente aparece apenas uma vez. A classificação considera o último registro disponível.")

if "indice_prioridade" in df_pacientes.columns:
    pacientes_prioritarios = df_pacientes.sort_values("indice_prioridade", ascending=False).head(10)
    colunas_prioridade = [
        "id_paciente", "timestamp", "diagnostico_principal",
        "score_clinico", "classificacao_clinica",
        "score_lpp", "classificacao_lpp",
        "quantidade_alertas",
        "indice_prioridade", "classificacao_prioridade"
    ]
    colunas_prioridade_existentes = [coluna for coluna in colunas_prioridade if coluna in pacientes_prioritarios.columns]
    st.dataframe(pacientes_prioritarios[colunas_prioridade_existentes], use_container_width=True, hide_index=True)
else:
    st.warning("Índice de prioridade não disponível.")

# 7. RELAÇÃO ENTRE SCORE CLÍNICO E SCORE LPP
st.markdown("---")
st.subheader(" Relação entre Risco Clínico e Risco de LPP")
st.caption(
    """
    Cada ponto representa um paciente.
    O registro utilizado corresponde ao estado mais recente.
    O tamanho do marcador representa o índice de prioridade.
    """
)

colunas_grafico = ["score_clinico", "score_lpp", "indice_prioridade"]
grafico_disponivel = all(coluna in df_pacientes.columns for coluna in colunas_grafico)

if grafico_disponivel:
    hover_data = []
    if "id_paciente" in df_pacientes.columns:
        hover_data.append("id_paciente")
    if "diagnostico_principal" in df_pacientes.columns:
        hover_data.append("diagnostico_principal")
    if "quantidade_alertas" in df_pacientes.columns:
        hover_data.append("quantidade_alertas")

    fig = px.scatter(
        df_pacientes,
        x="score_clinico",
        y="score_lpp",
        size="indice_prioridade",
        color="diagnostico_principal" if "diagnostico_principal" in df_pacientes.columns else None,
        hover_data=hover_data,
        title="Relação entre Score Clínico, Score LPP e Prioridade"
    )
    fig.update_layout(xaxis_title="Score Clínico", yaxis_title="Score LPP", height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Gráfico indisponível.")

# 8. RESUMO DA BASE & DADOS TÉCNICOS
st.markdown("---")
st.header("📊 Resumo da Base de Dados")

r1, r2, r3, r4 = st.columns(4)
with r1:
    st.metric("Registros Temporais", f"{len(df):,}".replace(",", "."))
with r2:
    pacientes = df["id_paciente"].nunique() if "id_paciente" in df.columns else "N/D"
    st.metric("Pacientes Únicos", pacientes)
with r3:
    st.metric("Variáveis", len(df.columns))
with r4:
    st.metric("Modelo", "Série Temporal")

# AVISO IMPORTANTE
st.markdown("---")
st.info(
    """
    ⚠️ **Aviso importante**

    Este sistema é um **protótipo acadêmico** desenvolvido com dados totalmente simulados.

    Os scores, regras, classificações e alertas possuem finalidade exclusivamente **conceitual e educacional**.

    Este protótipo não substitui avaliação profissional, protocolos institucionais ou sistemas clínicos validados.
    """
)

st.caption("TCC · Engenharia Biomédica · PUC-Campinas · 2026")
