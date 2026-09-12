import streamlit as st
from utils.styling import aplicar_estilo, navegacao_superior, cabecalho_pagina, navegacao_topo

st.set_page_config(page_title="Lean Healthcare | UTI Intelligent Care", page_icon="", layout="wide", initial_sidebar_state="collapsed")
aplicar_estilo()
navegacao_topo("Lean")
cabecalho_pagina("Lean Healthcare", "Indicadores e oportunidades de melhoria contínua no fluxo assistencial.", secao="Módulo assistencial", badge="Em desenvolvimento")
st.markdown("""<div class="coming-soon"><div class="coming-soon-icon">+</div><div class="coming-soon-title">Módulo em desenvolvimento</div><div class="coming-soon-copy">Estrutura visual preparada para futura implementação das análises de melhoria contínua.</div></div>""", unsafe_allow_html=True)
