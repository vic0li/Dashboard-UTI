import streamlit as st


def aplicar_estilo():
    st.markdown(
        """
        <style>

        /* =====================================================
            CONFIGURAÇÕES GERAIS
        ===================================================== */
        .stApp {
            background-color: #F5F7FA;
        }

        /* =====================================================
            TÍTULOS
        ===================================================== */
        h1 {
            color: #16324F;
            font-weight: 700;
        }
        h2 {
            color: #16324F;
        }
        h3 {
            color: #1F4E79;
        }

        /* =====================================================
            HERO / BLOCO DE APRESENTAÇÃO (Topo do Layout)
        ===================================================== */
        .hero-container {
            background-color: #1a3b70;
            color: white;
            padding: 35px 40px;
            border-radius: 14px 14px 0 0;
        }
        .hero-features {
            background-color: #ffffff;
            padding: 20px 40px;
            border-radius: 0 0 14px 14px;
            border: 1px solid #E1E5EA;
            border-top: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            margin-bottom: 25px;
        }
        .hero-title {
            font-size: 26px;
            font-weight: bold;
            margin: 8px 0;
            color: white;
        }
        .hero-subtitle {
            font-size: 14px;
            color: #c5d3ea;
            line-height: 1.5;
        }

        /* =====================================================
            CARDS E KPIS
        ===================================================== */
        .dashboard-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #E1E5EA;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 15px;
        }

        .kpi-card {
            background-color: white;
            padding: 18px;
            border-radius: 12px;
            border: 1px solid #E1E5EA;
            text-align: center;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.02);
        }
        .kpi-title {
            font-size: 13px;
            color: #6B7280;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #16324F;
        }

        /* =====================================================
            ALERTAS
        ===================================================== */
        .alerta-critico {
            background-color: #FFF1F1;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #D62828;
            color: #9b1c1c;
        }
        .alerta-alto {
            background-color: #FFF4E5;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #F77F00;
        }
        .alerta-moderado {
            background-color: #FFF9DB;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #F4C430;
        }
        .alerta-normal {
            background-color: #EDF7ED;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #2E7D32;
        }

        /* =====================================================
            SIDEBAR
        ===================================================== */
        section[data-testid="stSidebar"] {
            background-color: #16324F;
        }
        section[data-testid="stSidebar"] * {
            color: white;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def card(titulo, valor, icone="📊"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                {icone} {titulo}
            </div>
            <div class="kpi-value">
                {valor}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alerta(mensagem, nivel="normal"):
    classe = f"alerta-{nivel}"
    st.markdown(
        f"""
        <div class="{classe}">
            {mensagem}
        </div>
        """,
        unsafe_allow_html=True,
    )