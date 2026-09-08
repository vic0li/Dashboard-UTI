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
    page_title="UTI Intelligent Care",
    page_icon="🏥",
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

# O DataFrame df contém TODOS os registros temporais.
# Para representar a situação ATUAL de cada paciente,
# será utilizado apenas o último registro disponível.

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
# HEADER / HERO SECTION
# ============================================================

st.title("🏥 UTI Intelligent Care")
st.caption("🛡️ ICU Sentinel")
st.header("Monitoramento inteligente de risco em UTI")
st.write(
    """
    Protótipo de dashboard preditivo para gestão de risco
    clínico e operacional, integrando dados simulados
    e princípios de Lean Healthcare.
    """
)

# ============================================================
# PILARES DO SISTEMA
# ============================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧠 Risco de LPP")
    st.caption("Escore ponderado com base nos dados simulados.")

with col2:
    st.subheader("📈 Tendência clínica")
    st.caption("Deterioração precoce e score clínico.")

with col3:
    st.subheader("🏥 Gestão operacional")
    st.caption("Integração entre risco, dados e gestão Lean.")

st.caption("TCC · Engenharia Biomédica · PUC-Campinas · 2026")
st.divider()

# ============================================================
# VISÃO GERAL
# ============================================================

st.subheader("📊 Visão geral")
st.caption("Os indicadores abaixo representam a situação mais recente disponível de cada paciente.")

# ============================================================
# MÉTRICAS DE PACIENTES ATUAIS
# ============================================================

total_pacientes = (
    df_pacientes["id_paciente"].nunique()
    if "id_paciente" in df_pacientes.columns
    else len(df_pacientes)
)

if "quantidade_alertas" in df_pacientes.columns:
    total_alertas_val = int(df_pacientes["quantidade_alertas"].sum())
else:
    total_alertas_val = 0

if "saturacao_O2" in df_pacientes.columns:
    spo2_media = f"{df_pacientes['saturacao_O2'].mean():.1f}%"
else:
    spo2_media = "N/D"

if "frequencia_cardiaca" in df_pacientes.columns:
    fc_media = f"{df_pacientes['frequencia_cardiaca'].mean():.1f}"
else:
    fc_media = "N/D"

if "temperatura" in df_pacientes.columns:
    temp_media = f"{df_pacientes['temperatura'].mean():.1f}°C"
else:
    temp_media = "N/D"

# CARDS
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("👥 Pacientes", total_pacientes)
with m2:
    st.metric("⚠️ Alertas atuais", total_alertas_val)
with m3:
    st.metric("⭕ SpO₂ média", spo2_media)
with m4:
    st.metric("💓 FC média", fc_media)
with m5:
    st.metric("🌡️ Temperatura média", temp_media)

# ============================================================
# MOTOR ANALÍTICO
# ============================================================

st.divider()
st.header("🧠 Motor Analítico")
st.caption("Indicadores calculados utilizando o último registro disponível de cada paciente.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if "score_clinico" in df_pacientes.columns:
        score_clinico_medio = df_pacientes["score_clinico"].mean()
        st.metric(label="Score Clínico Médio", value=f"{score_clinico_medio:.1f}")
    else:
        st.metric(label="Score Clínico Médio", value="N/D")

with col2:
    if "score_lpp" in df_pacientes.columns:
        score_lpp_medio = df_pacientes["score_lpp"].mean()
        st.metric(label="Score LPP Médio", value=f"{score_lpp_medio:.1f}")
    else:
        st.metric(label="Score LPP Médio", value="N/D")

with col3:
    if "quantidade_alertas" in df_pacientes.columns:
        total_alertas = int(df_pacientes["quantidade_alertas"].sum())
        st.metric(label="Alertas Atuais", value=total_alertas)
    else:
        st.metric(label="Alertas Atuais", value="N/D")

with col4:
    if "indice_prioridade" in df_pacientes.columns:
        prioridade_media = df_pacientes["indice_prioridade"].mean()
        st.metric(label="Prioridade Média", value=f"{prioridade_media:.1f}")
    else:
        st.metric(label="Prioridade Média", value="N/D")

# ============================================================
# ETAPA 7.6 - VALIDAÇÃO DO MOTOR ANALÍTICO
# ============================================================

st.divider()
st.header("🔬 Validação do Motor Analítico")
st.write(
    """
    Esta seção verifica se as variáveis derivadas foram criadas
    corretamente e permite validar o comportamento dos scores,
    classificações, alertas e índices de prioridade.
    """
)

# 1. VERIFICAÇÃO DAS VARIÁVEIS
st.subheader("1️⃣ Verificação das Variáveis Geradas")

colunas_motor = [
    "score_clinico",
    "classificacao_clinica",
    "score_lpp",
    "classificacao_lpp",
    "quantidade_alertas",
    "indice_prioridade",
    "classificacao_prioridade"
]

colunas_encontradas = 0
for coluna in colunas_motor:
    if coluna in df.columns:
        st.success(f"✅ `{coluna}` criada com sucesso")
        colunas_encontradas += 1
    else:
        st.error(f"❌ `{coluna}` não encontrada")

if colunas_encontradas == len(colunas_motor):
    st.success("🎉 Todas as variáveis esperadas foram geradas pelo motor analítico.")
else:
    st.warning(f"⚠️ Foram encontradas {colunas_encontradas} de {len(colunas_motor)} variáveis esperadas.")

# 2. ESTATÍSTICAS DOS SCORES
st.divider()
st.subheader("2️⃣ Estatísticas dos Scores")
st.caption("Estatísticas calculadas sobre a situação atual de cada paciente.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🩺 Score Clínico")
    if "score_clinico" in df_pacientes.columns:
        st.metric("Mínimo", f"{df_pacientes['score_clinico'].min():.1f}")
        st.metric("Máximo", f"{df_pacientes['score_clinico'].max():.1f}")
        st.metric("Média", f"{df_pacientes['score_clinico'].mean():.1f}")
    else:
        st.warning("Score clínico não disponível.")

with col2:
    st.markdown("### 🩹 Score LPP")
    if "score_lpp" in df_pacientes.columns:
        st.metric("Mínimo", f"{df_pacientes['score_lpp'].min():.1f}")
        st.metric("Máximo", f"{df_pacientes['score_lpp'].max():.1f}")
        st.metric("Média", f"{df_pacientes['score_lpp'].mean():.1f}")
    else:
        st.warning("Score LPP não disponível.")

with col3:
    st.markdown("### 🔥 Índice de Prioridade")
    if "indice_prioridade" in df_pacientes.columns:
        st.metric("Mínimo", f"{df_pacientes['indice_prioridade'].min():.1f}")
        st.metric("Máximo", f"{df_pacientes['indice_prioridade'].max():.1f}")
        st.metric("Média", f"{df_pacientes['indice_prioridade'].mean():.1f}")
    else:
        st.warning("Índice de prioridade não disponível.")

# 3. DISTRIBUIÇÃO DAS CLASSIFICAÇÕES
st.divider()
st.subheader("3️⃣ Distribuição Atual dos Pacientes")
st.caption("Cada paciente é contabilizado apenas uma vez, utilizando seu registro mais recente.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🩺 Situação Clínica")
    if "classificacao_clinica" in df_pacientes.columns:
        distribuicao_clinica = df_pacientes["classificacao_clinica"].value_counts().reset_index()
        distribuicao_clinica.columns = ["Classificação", "Pacientes"]
        st.dataframe(distribuicao_clinica, use_container_width=True, hide_index=True)
    else:
        st.warning("Classificação clínica não disponível.")

with col2:
    st.markdown("### 🩹 Risco de LPP")
    if "classificacao_lpp" in df_pacientes.columns:
        distribuicao_lpp = df_pacientes["classificacao_lpp"].value_counts().reset_index()
        distribuicao_lpp.columns = ["Classificação", "Pacientes"]
        st.dataframe(distribuicao_lpp, use_container_width=True, hide_index=True)
    else:
        st.warning("Classificação LPP não disponível.")

with col3:
    st.markdown("### 🔥 Prioridade")
    if "classificacao_prioridade" in df_pacientes.columns:
        distribuicao_prioridade = df_pacientes["classificacao_prioridade"].value_counts().reset_index()
        distribuicao_prioridade.columns = ["Classificação", "Pacientes"]
        st.dataframe(distribuicao_prioridade, use_container_width=True, hide_index=True)
    else:
        st.warning("Classificação de prioridade não disponível.")

# 4. VERIFICAÇÃO DE DADOS NULOS
st.divider()
st.subheader("4️⃣ Verificação de Dados Nulos")

colunas_validacao = [
    "score_clinico",
    "score_lpp",
    "quantidade_alertas",
    "indice_prioridade"
]

for coluna in colunas_validacao:
    if coluna in df.columns:
        quantidade_nulos = df[coluna].isnull().sum()
        if quantidade_nulos == 0:
            st.success(f"✅ `{coluna}`: nenhum valor nulo")
        else:
            st.warning(f"⚠️ `{coluna}`: {quantidade_nulos} valores nulos")

# 5. AUDITORIA DOS RESULTADOS
st.divider()
st.subheader("5️⃣ Auditoria dos Resultados")
st.caption("Visualização dos dados de entrada e das variáveis geradas pelo motor analítico.")

colunas_auditoria = [
    "id_paciente", "timestamp",
    "frequencia_cardiaca", "saturacao_O2", "temperatura", "lactato",
    "tempo_posicao_atual_min", "pressao_media_colchao",
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
st.divider()
st.subheader("6️⃣ Pacientes com Maior Prioridade")
st.caption("Cada paciente aparece apenas uma vez. A classificação considera o último registro disponível.")

if "indice_prioridade" in df_pacientes.columns:
    pacientes_prioritarios = df_pacientes.sort_values("indice_prioridade", ascending=False).head(10)
    colunas_prioridade = [
        "id_paciente", "timestamp",
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
st.divider()
st.subheader("7️⃣ Relação entre Risco Clínico e Risco de LPP")
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
    if "quantidade_alertas" in df_pacientes.columns:
        hover_data.append("quantidade_alertas")
    if "timestamp" in df_pacientes.columns:
        hover_data.append("timestamp")

    fig = px.scatter(
        df_pacientes,
        x="score_clinico",
        y="score_lpp",
        size="indice_prioridade",
        hover_data=hover_data,
        title="Relação entre Score Clínico, Score LPP e Prioridade"
    )
    fig.update_layout(xaxis_title="Score Clínico", yaxis_title="Score LPP", height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Não foi possível gerar o gráfico porque uma ou mais variáveis necessárias não estão disponíveis.")

# 8. RESUMO DA BASE
st.divider()
st.header("📊 Resumo da Base de Dados")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Registros Temporais", f"{len(df):,}".replace(",", "."))

with col2:
    pacientes = df["id_paciente"].nunique() if "id_paciente" in df.columns else "N/D"
    st.metric("Pacientes Únicos", pacientes)

with col3:
    st.metric("Variáveis", len(df.columns))

with col4:
    st.metric("Modelo", "Série Temporal")

st.caption(
    """
    ℹ️ A base possui múltiplos registros por paciente ao longo
    do tempo. Por isso, o número de registros temporais pode ser
    significativamente maior que o número de pacientes únicos.
    """
)

# VISUALIZAR DADOS PROCESSADOS
st.divider()
st.header("📋 Dados Processados")

with st.expander("Visualizar registros processados pelo motor analítico", expanded=False):
    colunas_processadas = [
        "id_paciente", "timestamp",
        "score_clinico", "classificacao_clinica",
        "score_lpp", "classificacao_lpp",
        "quantidade_alertas",
        "indice_prioridade", "classificacao_prioridade"
    ]
    colunas_disponiveis = [coluna for coluna in colunas_processadas if coluna in df.columns]

    if colunas_disponiveis:
        st.dataframe(df[colunas_disponiveis].head(20), use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhuma coluna processada foi encontrada.")

# DIAGNÓSTICO TÉCNICO
st.divider()
with st.expander("🛠️ Diagnóstico técnico", expanded=False):
    st.subheader("Estrutura dos dados")
    registros_por_paciente = len(df) / len(df_pacientes) if len(df_pacientes) > 0 else 0

    st.write(
        f"""
        **Total de registros temporais:** {len(df)}

        **Total de pacientes únicos:** {len(df_pacientes)}

        **Registros médios por paciente:** {registros_por_paciente:.1f}
        """
    )

    st.subheader("Colunas disponíveis na base")
    st.write(list(df.columns))

    st.subheader("Tipos de dados")
    tipos_dados = df.dtypes.astype(str).reset_index()
    tipos_dados.columns = ["Coluna", "Tipo de dado"]
    st.dataframe(tipos_dados, use_container_width=True, hide_index=True)

# INFORMAÇÕES TÉCNICAS
st.divider()
with st.expander("⚙️ Informações técnicas do sistema", expanded=False):
    st.subheader("Arquitetura do protótipo")
    st.code(
        """
DADOS SIMULADOS
↓
DATA LOADER
↓
PROCESSAMENTO ANALÍTICO
↓
MOTOR DE RISCO
↓
SCORES E ALERTAS
↓
PRIORIZAÇÃO
↓
DASHBOARD
        """,
        language=None
    )

    st.subheader("Estrutura dos dados")
    st.code(
        """
PACIENTE PAC-001
│
├── 10:00 → Registro temporal
├── 11:00 → Registro temporal
├── 12:00 → Registro temporal
└── 13:00 → Estado atual do paciente

DASHBOARD GERENCIAL
↓
Utiliza o último registro de cada paciente

ANÁLISE TEMPORAL
↓
Utiliza todos os registros
        """,
        language=None
    )

    st.subheader("Status do sistema")
    st.success("✓ Dados carregados")
    st.success("✓ Dados processados")
    st.success("✓ Motor analítico executado")
    st.success("✓ Pacientes consolidados")
    st.success("✓ Sistema pronto para visualização")

# AVISO IMPORTANTE
st.divider()
st.info(
    """
    ⚠️ **Aviso importante**

    Este sistema é um **protótipo acadêmico** desenvolvido com dados totalmente simulados.

    Os scores, regras, classificações e alertas possuem finalidade exclusivamente **conceitual e educacional**.

    Este protótipo não substitui avaliação profissional, protocolos institucionais ou sistemas clínicos validados.
    """
)