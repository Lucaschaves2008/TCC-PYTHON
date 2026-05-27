"""
Ponto de entrada do sistema.
Execute com: streamlit run app.py
(a partir da pasta hotel_system/)
"""
import sys
import os

# Garante que os imports internos funcionem independente de onde o arquivo é chamado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Hotel System — TCC",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

from views.dashboard import render_dashboard
from views.clientes_view import render_clientes
from views.quartos_view import render_quartos
from views.reservas_view import render_reservas


PAGINAS = {
    " Dashboard":   render_dashboard,
    " Clientes":    render_clientes,
    " Quartos":     render_quartos,
    " Reservas":    render_reservas,
}


def sidebar():
    with st.sidebar:
        st.markdown("# 🏨 Hotel System")
        st.markdown("*Sistema de Gestão Hoteleira*")
        st.markdown("---")

        pagina = st.radio(
            "Navegação",
            options=list(PAGINAS.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption("TCC — Sistema de Hospedagem")
        st.caption("Desenvolvido com Python + Streamlit")

    return pagina


def main():
    pagina = sidebar()
    PAGINAS[pagina]()


if __name__ == "__main__":
    main()
