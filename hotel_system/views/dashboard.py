import streamlit as st
import pandas as pd

import services.cliente_service as cliente_svc
import services.quarto_service as quarto_svc
import services.reserva_service as reserva_svc
from utils.formatters import status_reserva_badge, status_quarto_badge, formatar_moeda


def render_dashboard():
    st.title("Dashboard")
    st.markdown("Visão geral do hotel em tempo real.")
    st.markdown("---")

    # --- MÉTRICAS ---
    try:
        total_clientes = cliente_svc.contar_clientes()
        total_quartos = quarto_svc.contar_quartos()
        status_quartos = quarto_svc.contar_por_status()
        reservas_ativas = reserva_svc.contar_ativas()
        total_reservas = reserva_svc.contar_reservas()

        disponivel = status_quartos.get("disponivel", 0)
        ocupado = status_quartos.get("ocupado", 0)
        manutencao = status_quartos.get("manutencao", 0)

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("👥 Clientes", total_clientes)
    with col2:
        st.metric("🛏 Total Quartos", total_quartos)
    with col3:
        st.metric("🟢 Disponíveis", disponivel)
    with col4:
        st.metric("🔴 Ocupados", ocupado)
    with col5:
        st.metric("📋 Reservas Ativas", reservas_ativas)

    st.markdown("---")

    # --- OCUPAÇÃO VISUAL ---
    col_esq, col_dir = st.columns([1, 1])

    with col_esq:
        st.subheader("🏨 Ocupação dos Quartos")
        if total_quartos > 0:
            pct_ocupado = round((ocupado / total_quartos) * 100, 1)
            pct_disponivel = round((disponivel / total_quartos) * 100, 1)
            pct_manutencao = round((manutencao / total_quartos) * 100, 1)
            st.progress(ocupado / total_quartos)
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Ocupação", f"{pct_ocupado}%")
            col_b.metric("Disponível", f"{pct_disponivel}%")
            col_c.metric("Manutenção", f"{pct_manutencao}%")

            df_ocup = pd.DataFrame({
                "Status": ["Disponível", "Ocupado", "Manutenção"],
                "Quantidade": [disponivel, ocupado, manutencao],
            })
            st.bar_chart(df_ocup.set_index("Status"))
        else:
            st.info("Nenhum quarto cadastrado.")

    with col_dir:
        st.subheader("📋 Reservas Recentes")
        try:
            reservas = reserva_svc.listar_reservas()[:8]
            if reservas:
                df = pd.DataFrame(reservas)[
                    ["id", "cliente_nome", "quarto_numero", "check_in", "check_out", "status", "total"]
                ]
                df.columns = ["ID", "Cliente", "Quarto", "Check-in", "Check-out", "Status", "Total (R$)"]
                df["Status"] = df["Status"].apply(status_reserva_badge)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma reserva registrada ainda.")
        except Exception as e:
            st.warning(f"Não foi possível carregar reservas: {e}")

    st.markdown("---")
    st.caption(f"Total de reservas no sistema: {total_reservas}")
