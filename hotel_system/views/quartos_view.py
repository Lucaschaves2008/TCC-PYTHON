import pandas as pd
import streamlit as st

import services.quarto_service as svc
from utils.formatters import (
    formatar_moeda,
    status_quarto_badge,
    tipo_quarto_label,
)

TIPOS = ["solteiro", "casal", "luxo", "suite"]
STATUS_LIST = ["disponivel", "ocupado", "manutencao"]


def render_quartos():
    st.title("🛏 Quartos")
    st.markdown("---")

    tab_lista, tab_novo, tab_editar = st.tabs(
        ["📋 Lista de Quartos", "➕ Novo Quarto", "✏️ Editar / Excluir"]
    )

    with tab_lista:
        _render_lista()

    with tab_novo:
        _render_form_novo()

    with tab_editar:
        _render_editar()


# ──────────────────────────────────────────────────────────────
# LISTA
# ──────────────────────────────────────────────────────────────

def _render_lista():
    st.subheader("Todos os quartos")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_status = st.selectbox(
            "Filtrar por status",
            options=["Todos"] + STATUS_LIST,
            format_func=lambda x: status_quarto_badge(x) if x != "Todos" else "🔎 Todos",
        )
    with col_f2:
        st.empty()

    try:
        quartos = svc.listar_quartos(
            filtro_status="" if filtro_status == "Todos" else filtro_status
        )
    except Exception as e:
        st.error(f"Erro ao carregar quartos: {e}")
        return

    if not quartos:
        st.info("Nenhum quarto encontrado.")
        return

    df = pd.DataFrame(quartos)[
        ["numero", "tipo", "status", "capacidade", "preco_diaria", "descricao"]
    ]
    df["tipo"] = df["tipo"].apply(tipo_quarto_label)
    df["status"] = df["status"].apply(status_quarto_badge)
    df["preco_diaria"] = df["preco_diaria"].apply(formatar_moeda)
    df.columns = ["Número", "Tipo", "Status", "Capacidade", "Diária", "Descrição"]

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(quartos)} quarto(s) listado(s).")


# ──────────────────────────────────────────────────────────────
# NOVO QUARTO
# ──────────────────────────────────────────────────────────────

def _render_form_novo():
    st.subheader("Cadastrar novo quarto")

    with st.form("form_novo_quarto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            numero = st.text_input("Número do quarto *", placeholder="Ex: 101")
            tipo = st.selectbox(
                "Tipo *",
                options=TIPOS,
                format_func=tipo_quarto_label,
            )
        with col2:
            preco = st.number_input(
                "Preço da diária (R$) *", min_value=0.0, step=10.0, format="%.2f"
            )
            capacidade = st.number_input(
                "Capacidade (pessoas) *", min_value=1, max_value=20, value=1
            )
        descricao = st.text_area("Descrição", placeholder="Opcional")

        st.markdown("*\\* campos obrigatórios*")
        submit = st.form_submit_button("💾 Cadastrar Quarto", use_container_width=True)

    if submit:
        try:
            svc.criar_quarto(
                numero=numero,
                tipo=tipo,
                preco_diaria=preco,
                capacidade=int(capacidade),
                descricao=descricao,
            )
            st.success(f"✅ Quarto **{numero.upper()}** cadastrado com sucesso!")
        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")


# ──────────────────────────────────────────────────────────────
# EDITAR / EXCLUIR
# ──────────────────────────────────────────────────────────────

def _render_editar():
    st.subheader("Editar, alterar status ou excluir quarto")

    try:
        quartos = svc.listar_quartos()
    except Exception as e:
        st.error(f"Erro ao carregar quartos: {e}")
        return

    if not quartos:
        st.info("Nenhum quarto cadastrado.")
        return

    opcoes = {
        q["id"]: f"Quarto {q['numero']}  —  {tipo_quarto_label(q['tipo'])}  —  {status_quarto_badge(q['status'])}"
        for q in quartos
    }
    quarto_id = st.selectbox(
        "Selecionar quarto",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    selecionado = next((q for q in quartos if q["id"] == quarto_id), None)
    if not selecionado:
        return

    # Alterar status rapidamente
    st.markdown("#### Alterar status")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        if st.button("🟢 Disponível", use_container_width=True):
            _mudar_status(quarto_id, "disponivel")
    with col_s2:
        if st.button("🔴 Ocupado", use_container_width=True):
            _mudar_status(quarto_id, "ocupado")
    with col_s3:
        if st.button("🟡 Manutenção", use_container_width=True):
            _mudar_status(quarto_id, "manutencao")

    st.markdown("#### Editar dados")

    idx_tipo = TIPOS.index(selecionado["tipo"]) if selecionado["tipo"] in TIPOS else 0

    with st.form("form_editar_quarto"):
        col1, col2 = st.columns(2)
        with col1:
            numero = st.text_input("Número", value=selecionado["numero"])
            tipo = st.selectbox(
                "Tipo",
                options=TIPOS,
                index=idx_tipo,
                format_func=tipo_quarto_label,
            )
        with col2:
            preco = st.number_input(
                "Diária (R$)",
                min_value=0.0,
                value=float(selecionado["preco_diaria"]),
                step=10.0,
                format="%.2f",
            )
            capacidade = st.number_input(
                "Capacidade",
                min_value=1,
                max_value=20,
                value=int(selecionado["capacidade"]),
            )
        descricao = st.text_area("Descrição", value=selecionado["descricao"])

        col_salvar, col_excluir = st.columns([3, 1])
        with col_salvar:
            salvar = st.form_submit_button("💾 Salvar", use_container_width=True)
        with col_excluir:
            excluir = st.form_submit_button("🗑️ Excluir", use_container_width=True, type="secondary")

    if salvar:
        try:
            svc.atualizar_quarto(
                quarto_id=quarto_id,
                numero=numero,
                tipo=tipo,
                preco_diaria=preco,
                capacidade=int(capacidade),
                descricao=descricao,
            )
            st.success("✅ Quarto atualizado!")
            st.rerun()
        except ValueError as e:
            st.error(f"❌ {e}")

    if excluir:
        try:
            svc.deletar_quarto(quarto_id)
            st.success("✅ Quarto excluído!")
            st.rerun()
        except ValueError as e:
            st.warning(f"⚠️ {e}")


def _mudar_status(quarto_id: int, novo_status: str):
    try:
        svc.alterar_status(quarto_id, novo_status)
        st.success(f"✅ Status alterado para: {status_quarto_badge(novo_status)}")
        st.rerun()
    except ValueError as e:
        st.error(f"❌ {e}")
