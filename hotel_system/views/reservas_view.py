from datetime import datetime, timedelta, date

import pandas as pd
import streamlit as st

import services.cliente_service as cliente_svc
import services.quarto_service as quarto_svc
import services.reserva_service as reserva_svc
from utils.formatters import (
    formatar_moeda,
    status_reserva_badge,
    tipo_quarto_label,
)

STATUS_OPCOES = ["todos", "pendente", "confirmada", "checkin", "checkout", "cancelada"]


def render_reservas():
    st.title("📋 Reservas")
    st.markdown("---")

    tab_lista, tab_nova, tab_gerenciar = st.tabs(
        ["📋 Lista", "➕ Nova Reserva", "⚙️ Gerenciar"]
    )

    with tab_lista:
        _render_lista()

    with tab_nova:
        _render_form_nova()

    with tab_gerenciar:
        _render_gerenciar()


# ──────────────────────────────────────────────────────────────
# LISTA
# ──────────────────────────────────────────────────────────────

def _render_lista():
    st.subheader("Todas as reservas")

    filtro = st.selectbox(
        "Filtrar por status",
        options=STATUS_OPCOES,
        format_func=lambda x: "🔎 Todos" if x == "todos" else status_reserva_badge(x),
    )

    try:
        reservas = reserva_svc.listar_reservas(
            filtro_status="" if filtro == "todos" else filtro
        )
    except Exception as e:
        st.error(f"Erro ao carregar reservas: {e}")
        return

    if not reservas:
        st.info("Nenhuma reserva encontrada.")
        return

    df = pd.DataFrame(reservas)[
        ["id", "cliente_nome", "quarto_numero", "check_in", "check_out",
         "numero_dias", "status", "total"]
    ]
    df["status"] = df["status"].apply(status_reserva_badge)
    df["total"] = df["total"].apply(formatar_moeda)
    df.columns = ["ID", "Cliente", "Quarto", "Check-in", "Check-out",
                  "Dias", "Status", "Total"]

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(reservas)} reserva(s) encontrada(s).")


# ──────────────────────────────────────────────────────────────
# NOVA RESERVA
# ──────────────────────────────────────────────────────────────

def _render_form_nova():
    st.subheader("Criar nova reserva")

    try:
        clientes = cliente_svc.listar_clientes()
        quartos = quarto_svc.listar_quartos(filtro_status="disponivel")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return

    if not clientes:
        st.warning("⚠️ Nenhum cliente cadastrado. Cadastre um cliente primeiro.")
        return
    if not quartos:
        st.warning("⚠️ Nenhum quarto disponível no momento.")
        return

    opcoes_clientes = {
        c["id"]: f"{c['nome']}  —  CPF: {c['cpf']}" for c in clientes
    }
    opcoes_quartos = {
        q["id"]: (
            f"Quarto {q['numero']}  —  {tipo_quarto_label(q['tipo'])}"
            f"  —  {formatar_moeda(q['preco_diaria'])}/noite"
        )
        for q in quartos
    }

    with st.form("form_nova_reserva", clear_on_submit=True):
        cliente_id = st.selectbox(
            "Cliente *",
            options=list(opcoes_clientes.keys()),
            format_func=lambda x: opcoes_clientes[x],
        )
        quarto_id = st.selectbox(
            "Quarto *",
            options=list(opcoes_quartos.keys()),
            format_func=lambda x: opcoes_quartos[x],
        )

        col1, col2 = st.columns(2)
        amanha = date.today() + timedelta(days=1)
        depois = date.today() + timedelta(days=3)
        with col1:
            check_in = st.date_input("Check-in *", value=amanha, min_value=date.today())
        with col2:
            check_out = st.date_input("Check-out *", value=depois, min_value=amanha)

        observacoes = st.text_area("Observações", placeholder="Opcional")

        # Preview do valor
        quarto_sel = next((q for q in quartos if q["id"] == quarto_id), None)
        if quarto_sel and check_in and check_out and check_out > check_in:
            dias = (check_out - check_in).days
            total_prev = dias * float(quarto_sel["preco_diaria"])
            st.info(
                f"💰 Estimativa: {dias} diária(s) × {formatar_moeda(quarto_sel['preco_diaria'])} "
                f"= **{formatar_moeda(total_prev)}**"
            )

        st.markdown("*\\* campos obrigatórios*")
        submit = st.form_submit_button("📋 Confirmar Reserva", use_container_width=True)

    if submit:
        try:
            check_in_dt = datetime.combine(check_in, datetime.min.time()).replace(hour=14)
            check_out_dt = datetime.combine(check_out, datetime.min.time()).replace(hour=12)
            reserva_svc.criar_reserva(
                cliente_id=int(cliente_id),
                quarto_id=int(quarto_id),
                check_in=check_in_dt,
                check_out=check_out_dt,
                observacoes=observacoes,
            )
            st.success("✅ Reserva criada e confirmada com sucesso!")
        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")


# ──────────────────────────────────────────────────────────────
# GERENCIAR (AÇÕES DE STATUS + EXCLUSÃO)
# ──────────────────────────────────────────────────────────────

def _render_gerenciar():
    st.subheader("Gerenciar reserva")

    try:
        reservas = reserva_svc.listar_reservas()
    except Exception as e:
        st.error(f"Erro ao carregar reservas: {e}")
        return

    ativas = [r for r in reservas if r["status"] not in ("checkout", "cancelada")]
    todas = reservas

    opcao_filtro = st.radio(
        "Mostrar reservas",
        options=["Ativas", "Todas"],
        horizontal=True,
    )
    lista = ativas if opcao_filtro == "Ativas" else todas

    if not lista:
        st.info("Nenhuma reserva para exibir.")
        return

    opcoes = {
        r["id"]: (
            f"#{r['id']}  —  {r['cliente_nome']}  —  "
            f"Quarto {r['quarto_numero']}  —  {status_reserva_badge(r['status'])}"
        )
        for r in lista
    }
    reserva_id = st.selectbox(
        "Selecionar reserva",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    selecionada = next((r for r in lista if r["id"] == reserva_id), None)
    if not selecionada:
        return

    # Detalhes
    st.markdown("#### Detalhes")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cliente", selecionada["cliente_nome"])
    col2.metric("Quarto", selecionada["quarto_numero"])
    col3.metric("Dias", selecionada["numero_dias"])
    col4.metric("Total", formatar_moeda(selecionada["total"]))

    st.markdown(f"**Status atual:** {status_reserva_badge(selecionada['status'])}")
    if selecionada["observacoes"]:
        st.markdown(f"**Observações:** {selecionada['observacoes']}")

    # Ações de status
    st.markdown("#### Ações")
    status_atual = selecionada["status"]

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        if status_atual == "pendente":
            if st.button("✅ Confirmar", use_container_width=True):
                _mudar_status(reserva_id, "confirmada")

    with col_b:
        if status_atual == "confirmada":
            if st.button("🔵 Check-in", use_container_width=True):
                _mudar_status(reserva_id, "checkin")

    with col_c:
        if status_atual == "checkin":
            if st.button("⚪ Check-out", use_container_width=True):
                _mudar_status(reserva_id, "checkout")

    with col_d:
        if status_atual not in ("checkout", "cancelada"):
            if st.button("❌ Cancelar", use_container_width=True, type="secondary"):
                _mudar_status(reserva_id, "cancelada")

    # Exclusão
    st.markdown("---")
    st.markdown("#### Excluir reserva")
    confirmar = st.checkbox("Confirmo que desejo excluir esta reserva permanentemente")
    if confirmar:
        if st.button("🗑️ Excluir Reserva", type="secondary"):
            try:
                reserva_svc.deletar_reserva(reserva_id)
                st.success("✅ Reserva excluída!")
                st.rerun()
            except ValueError as e:
                st.warning(f"⚠️ {e}")
            except Exception as e:
                st.error(f"❌ {e}")


def _mudar_status(reserva_id: int, novo_status: str):
    try:
        reserva_svc.alterar_status(reserva_id, novo_status)
        st.success(f"✅ Status alterado: {status_reserva_badge(novo_status)}")
        st.rerun()
    except ValueError as e:
        st.error(f"❌ {e}")
